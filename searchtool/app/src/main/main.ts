import { app, BrowserWindow, ipcMain, IpcMainInvokeEvent } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { promises as fs } from 'node:fs'
import { SettingsStore } from './settings/store'
import { createSearchService } from './services/searchService'
import { Logger } from './services/logger'
import { MetricsService, type SearchRecord } from './services/metricsService'
import type { SearchPayload, SearchResponse } from '../shared/contracts'
import type { AppSettings } from '../shared/settings'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

process.env.APP_ROOT = path.join(__dirname, '..')
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

const screenshotPath = process.env.SCREENSHOT_PATH
const screenshotSampleFile = process.env.SCREENSHOT_SAMPLE_FILE
const screenshotMetricsFile = process.env.SCREENSHOT_METRICS_FILE
const screenshotView = process.env.SCREENSHOT_VIEW
const screenshotKeyword = process.env.SCREENSHOT_KEYWORD
const screenshotSearchTab = process.env.SCREENSHOT_SEARCH_TAB
const screenshotDelayMs = Number(process.env.SCREENSHOT_DELAY_MS ?? '400')

let screenshotSample: SearchResponse | undefined

let mainWindow: BrowserWindow | null = null
let settingsStore: SettingsStore
let logger: Logger
let metricsService: MetricsService
let searchService: ReturnType<typeof createSearchService>

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const dispatchScreenshotConfig = async (window: BrowserWindow) => {
  if (!screenshotView && !screenshotKeyword && !screenshotSearchTab && !screenshotSample) {
    return
  }

  const detail: Record<string, unknown> = {}
  if (screenshotView) {
    detail.view = screenshotView
  }
  if (screenshotKeyword) {
    detail.keyword = screenshotKeyword
  }
  if (screenshotSearchTab) {
    detail.searchTab = screenshotSearchTab
  }
  if (screenshotSample) {
    detail.searchResult = screenshotSample
  }

  if (Object.keys(detail).length === 0) {
    return
  }

  const serialized = JSON.stringify(detail)
  await window.webContents.executeJavaScript(
    `window.dispatchEvent(new CustomEvent('screenshot-config', { detail: ${serialized} }))`,
    true
  )

  const waitMs = Number.isFinite(screenshotDelayMs) ? Math.max(0, screenshotDelayMs) : 400
  if (waitMs > 0) {
    await delay(waitMs)
  }
}

const loadScreenshotArtifacts = async () => {
  if (screenshotSampleFile) {
    try {
      const data = await fs.readFile(screenshotSampleFile, 'utf-8')
      screenshotSample = JSON.parse(data) as SearchResponse
      logger?.info('Loaded screenshot search sample', 'main', { screenshotSampleFile })
    } catch (error) {
      logger?.error('Failed to load screenshot search sample', 'main', {
        error: error instanceof Error ? error.message : error,
        screenshotSampleFile,
      })
    }
  }

  if (screenshotMetricsFile) {
    try {
      const data = await fs.readFile(screenshotMetricsFile, 'utf-8')
      const records = JSON.parse(data) as SearchRecord[]
      if (Array.isArray(records) && records.length > 0) {
        metricsService?.seed(records)
        logger?.info('Seeded metrics sample data', 'main', { count: records.length })
      }
    } catch (error) {
      logger?.error('Failed to load screenshot metrics sample', 'main', {
        error: error instanceof Error ? error.message : error,
        screenshotMetricsFile,
      })
    }
  }
}

const setupScreenshotCapture = (window: BrowserWindow) => {
  if (!screenshotPath) {
    return
  }
  window.webContents.once('did-finish-load', async () => {
    try {
      await dispatchScreenshotConfig(window)
      const image = await window.webContents.capturePage()
      await fs.mkdir(path.dirname(screenshotPath), { recursive: true })
      await fs.writeFile(screenshotPath, image.toPNG())
      logger?.info('Screenshot saved', 'main', { screenshotPath })
    } catch (error) {
      logger?.error('Screenshot capture failed', 'main', {
        error: error instanceof Error ? error.message : error,
      })
    } finally {
      app.quit()
    }
  })
}

const ensureWindow = async () => {
  if (mainWindow) return mainWindow

  mainWindow = new BrowserWindow({
    title: 'Search Agent',
    width: 1280,
    height: 820,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
    },
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  if (VITE_DEV_SERVER_URL) {
    await mainWindow.loadURL(VITE_DEV_SERVER_URL)
  } else {
    mainWindow.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
  setupScreenshotCapture(mainWindow)

  return mainWindow
}

const registerIpc = () => {
  ipcMain.handle('settings:get', async () => settingsStore.get())
  ipcMain.handle('settings:set', async (_event, payload: AppSettings) => settingsStore.save(payload))
  ipcMain.handle('search:run', async (_event: IpcMainInvokeEvent, payload: SearchPayload) => {
    const keyword = payload?.keyword?.trim() ?? ''
    const settings = settingsStore.get()
    if (!keyword && !settings.keyword) {
      throw new Error('検索キーワードを入力してください。')
    }
    const resolvedPayload: SearchPayload = {
      keyword: keyword || settings.keyword,
      sources: payload.sources,
      maxCombinedHits: payload.maxCombinedHits,
    }
    return searchService.runSearch(resolvedPayload, keyword ? { ...settings, keyword } : settings)
  })
  ipcMain.handle('metrics:get', async (_event, limit?: number) => {
    return metricsService.getSummary(limit ?? 10)
  })
  ipcMain.handle('metrics:clear', async () => {
    metricsService.clear()
    logger.info('Metrics cleared', 'main')
  })
}

const bootstrap = async () => {
  const userDataPath = app.getPath('userData')

  logger = new Logger(userDataPath)
  metricsService = new MetricsService()
  settingsStore = new SettingsStore(userDataPath)

  await settingsStore.load()

  searchService = createSearchService(logger, metricsService)

  await loadScreenshotArtifacts()

  logger.info('Application started', 'main', { version: app.getVersion() })

  registerIpc()
  await ensureWindow()
}

app.whenReady().then(bootstrap)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    mainWindow = null
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    ensureWindow()
  }
})
