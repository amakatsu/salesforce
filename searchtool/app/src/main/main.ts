import { app, BrowserWindow, ipcMain, IpcMainInvokeEvent } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { SettingsStore } from './settings/store'
import { createSearchService } from './services/searchService'
import { Logger } from './services/logger'
import { MetricsService } from './services/metricsService'
import { SearchPayload } from '../shared/contracts'
import type { AppSettings } from '../shared/settings'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

process.env.APP_ROOT = path.join(__dirname, '..')
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let mainWindow: BrowserWindow | null = null
let settingsStore: SettingsStore
let logger: Logger
let metricsService: MetricsService
let searchService: ReturnType<typeof createSearchService>

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
    const resolvedPayload: SearchPayload = { keyword: keyword || settings.keyword }
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
