/**
 * スクリーンショット撮影スクリプト
 * UIモックのスクリーンショットをPlaywrightで撮影
 */

import { chromium } from 'playwright'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

async function captureScreenshots() {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  スクリーンショット撮影開始')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log()

  const browser = await chromium.launch({
    headless: true,
  })

  const context = await browser.newContext({
    viewport: { width: 1280, height: 1400 },
    deviceScaleFactor: 2, // Retina対応
  })

  const page = await context.newPage()

  try {
    // UIモックを開く
    const htmlPath = join(__dirname, 'ui-mock.html')
    const fileUrl = `file://${htmlPath}`

    console.log('【1】設定画面の全体表示')
    console.log('────────────────────────────────────────')
    await page.goto(fileUrl)
    await page.waitForLoadState('networkidle')

    const screenshotDir = join(__dirname, '../screenshots')
    const { mkdirSync } = await import('fs')
    try {
      mkdirSync(screenshotDir, { recursive: true })
    } catch (e) {
      // ディレクトリが既に存在する場合は無視
    }

    // 1. 全体のスクリーンショット
    await page.screenshot({
      path: join(screenshotDir, '01-settings-full.png'),
      fullPage: true,
    })
    console.log('✅ 保存: screenshots/01-settings-full.png')
    console.log()

    // 2. AI設定セクションのみ
    console.log('【2】AI設定セクション（新機能）')
    console.log('────────────────────────────────────────')
    await page.evaluate(() => {
      const h3Elements = Array.from(document.querySelectorAll('h3'))
      const aiSection = h3Elements.find(el => el.textContent?.includes('AI設定'))
      if (aiSection) {
        aiSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
    await page.waitForTimeout(500)

    const aiSection = await page.locator('h3:has-text("AI設定")').first()
    const aiSectionBox = await aiSection.boundingBox()
    if (aiSectionBox) {
      await page.screenshot({
        path: join(screenshotDir, '02-ai-settings.png'),
        clip: {
          x: 0,
          y: aiSectionBox.y - 20,
          width: 1280,
          height: 400,
        },
      })
      console.log('✅ 保存: screenshots/02-ai-settings.png')
    }
    console.log()

    // 3. APIキー入力欄にフォーカス
    console.log('【3】APIキー入力欄（フォーカス状態）')
    console.log('────────────────────────────────────────')
    await page.locator('#apiKey').click()
    await page.waitForTimeout(300)

    const apiKeyBox = await page.locator('#apiKey').boundingBox()
    if (apiKeyBox) {
      await page.screenshot({
        path: join(screenshotDir, '03-api-key-focus.png'),
        clip: {
          x: Math.max(0, apiKeyBox.x - 40),
          y: Math.max(0, apiKeyBox.y - 80),
          width: Math.min(1280, apiKeyBox.width + 80),
          height: 180,
        },
      })
      console.log('✅ 保存: screenshots/03-api-key-focus.png')
    }
    console.log()

    // 4. サンプル値を入力した状態
    console.log('【4】サンプル値入力後の画面')
    console.log('────────────────────────────────────────')
    await page.locator('#apiKey').fill('sk-proj-xxxxxxxxxxxxxxxxxxxxx')
    await page.locator('#modelId').fill('openai/gpt-4o-mini')
    await page.locator('#localRoot').fill('/home/user/projects\n/home/user/documents')
    await page.locator('#redmineUrls').fill('https://redmine.example.com')
    await page.locator('#sharepointUrls').fill('https://company.sharepoint.com/sites/docs')

    await page.screenshot({
      path: join(screenshotDir, '04-settings-filled.png'),
      fullPage: true,
    })
    console.log('✅ 保存: screenshots/04-settings-filled.png')
    console.log()

    // 5. 保存ボタン
    console.log('【5】保存ボタン')
    console.log('────────────────────────────────────────')
    await page.evaluate(() => {
      const button = document.querySelector('button')
      if (button) {
        button.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
    await page.waitForTimeout(500)

    const saveButton = await page.locator('button').boundingBox()
    if (saveButton) {
      await page.screenshot({
        path: join(screenshotDir, '05-save-button.png'),
        clip: {
          x: Math.max(0, saveButton.x - 100),
          y: Math.max(0, saveButton.y - 50),
          width: Math.min(1280, saveButton.width + 200),
          height: 120,
        },
      })
      console.log('✅ 保存: screenshots/05-save-button.png')
    }
    console.log()

    // 6. インフォボックス
    console.log('【6】新機能インフォボックス')
    console.log('────────────────────────────────────────')
    await page.evaluate(() => {
      window.scrollTo(0, 0)
    })
    await page.waitForTimeout(500)

    const infoBox = await page.locator('.info-box').boundingBox()
    if (infoBox) {
      await page.screenshot({
        path: join(screenshotDir, '06-info-box.png'),
        clip: {
          x: Math.max(0, infoBox.x - 20),
          y: Math.max(0, infoBox.y - 20),
          width: Math.min(1280, infoBox.width + 40),
          height: infoBox.height + 40,
        },
      })
      console.log('✅ 保存: screenshots/06-info-box.png')
    }
    console.log()

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log('  スクリーンショット撮影完了！')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log()
    console.log('保存先: app/screenshots/')
    console.log()
    console.log('生成されたファイル:')
    console.log('  01-settings-full.png        - 設定画面全体')
    console.log('  02-ai-settings.png          - AI設定セクション')
    console.log('  03-api-key-focus.png        - APIキー入力欄')
    console.log('  04-settings-filled.png      - サンプル値入力後')
    console.log('  05-save-button.png          - 保存ボタン')
    console.log('  06-info-box.png             - 新機能お知らせ')
    console.log()

  } catch (error) {
    console.error('❌ エラーが発生しました:', error)
    throw error
  } finally {
    await browser.close()
  }
}

captureScreenshots().catch(console.error)
