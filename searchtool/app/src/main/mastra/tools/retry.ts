import { createTool } from '@mastra/core/tools'
import { z } from 'zod'
import type { PlaywrightCaller } from './navigation'

// ---------------------------------------------------------------------------
// Schema（tool_interfaces.md §3d 準拠）
// ---------------------------------------------------------------------------

const inputSchema = z.object({
  reason: z.string().describe('リトライの理由（例: "検索結果が読み込まれていない"）'),
  strategy: z.enum(['reload', 'wait', 'scroll', 'snapshot_only']).default('wait')
    .describe(
      'reload: ページ再読み込み, wait: 追加待機, ' +
      'scroll: 下スクロール, snapshot_only: 即座にスナップショット再取得',
    ),
  waitSeconds: z.number().int().min(1).max(30).default(3)
    .describe('wait/reload 後のスナップショット取得までの待機秒数'),
})

const outputSchema = z.object({
  pageSnapshot: z.string().describe('新しいアクセシビリティスナップショット'),
  currentUrl: z.string().describe('現在のURL'),
  strategyUsed: z.string().describe('実行した戦略'),
})

// ---------------------------------------------------------------------------
// MCP 結果からテキストを抽出
// ---------------------------------------------------------------------------

const extractText = (result: unknown): string => {
  if (typeof result === 'string') return result
  if (result && typeof result === 'object') {
    const obj = result as Record<string, unknown>
    if (typeof obj.text === 'string') return obj.text
    if (Array.isArray(obj.content)) {
      return (obj.content as Array<{ type?: string; text?: string }>)
        .filter((c) => c.type === 'text' && c.text)
        .map((c) => c.text!)
        .join('\n')
    }
  }
  return JSON.stringify(result)
}

// ---------------------------------------------------------------------------
// RetryTool
// ---------------------------------------------------------------------------

/**
 * Agent の判断失敗時にページ状態を変更し、新しいスナップショットを返す。
 * 解釈は常に Agent が行う（「毎回その場で判断する」の原則）。
 *
 * @param callPlaywright - playwright-mcp ツール呼び出し関数
 */
export const createRetryTool = (callPlaywright: PlaywrightCaller) =>
  createTool({
    id: 'retry',
    description:
      'Agent の判断失敗時にページ状態を変更し、新しいスナップショットを返す。' +
      '解釈は常に Agent が行う。',
    inputSchema,
    outputSchema,
    execute: async ({ context }) => {
      switch (context.strategy) {
        case 'reload':
          await callPlaywright('browser_evaluate', {
            function: '() => { window.location.reload() }',
          })
          await callPlaywright('browser_wait_for', { time: context.waitSeconds })
          break
        case 'wait':
          await callPlaywright('browser_wait_for', { time: context.waitSeconds })
          break
        case 'scroll':
          await callPlaywright('browser_press_key', { key: 'End' })
          await callPlaywright('browser_wait_for', { time: 1 })
          break
        case 'snapshot_only':
          break
      }

      const result = await callPlaywright('browser_snapshot', {})
      return {
        pageSnapshot: extractText(result),
        currentUrl: '',
        strategyUsed: context.strategy,
      }
    },
  })
