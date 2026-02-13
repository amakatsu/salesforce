import { MCPConfiguration } from '@mastra/mcp'
import type { AppSettings } from '../../shared/settings'

/**
 * playwright-mcp への接続設定。
 *
 * Mastra MCPConfiguration を使い、playwright-mcp を stdio 経由で起動する。
 * Agent に browser_snapshot / browser_click / browser_type 等を提供する。
 *
 * 【拡張ポイント】
 * - DEFAULT_BROWSER を AppSettings.browser.channel に切り替え（Phase 1 P1-7）
 * - servers に他の MCP サーバーを追加可能
 */

const DEFAULT_BROWSER = 'msedge'

export const createPlaywrightMcpClient = (settings: AppSettings): MCPConfiguration => {
  const userDataDir = settings.browser.userDataDir || undefined

  const args = ['@playwright/mcp@latest', '--browser', DEFAULT_BROWSER]
  if (userDataDir) {
    args.push('--user-data-dir', userDataDir)
  }

  return new MCPConfiguration({
    id: 'searchtool-playwright',
    servers: {
      playwright: {
        command: 'npx',
        args,
      },
    },
  })
}
