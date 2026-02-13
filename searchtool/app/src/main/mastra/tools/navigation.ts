import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ---------------------------------------------------------------------------
// 型定義
// ---------------------------------------------------------------------------

/**
 * playwright-mcp ツール呼び出し関数の型。
 * NavigationTool / RetryTool が browser_* ツールを呼ぶ際に使う。
 */
export type PlaywrightCaller = (
  toolName: string,
  args: Record<string, unknown>,
) => Promise<unknown>

// ---------------------------------------------------------------------------
// Schema（tool_interfaces.md §3c 準拠）
// ---------------------------------------------------------------------------

const inputSchema = z.object({
  action: z.enum(['navigate', 'click', 'type', 'snapshot', 'wait']),
  ref: z.string().default('').describe(
    'browser_snapshot のアクセシビリティref値。click/type で使用',
  ),
  target: z.string().default('').describe(
    'navigate: URL, click/type: アクセシブルな説明, wait: 待機テキスト',
  ),
  value: z.string().optional().describe(
    'type: 入力テキスト, wait: タイムアウト秒数',
  ),
})

const outputSchema = z.object({
  success: z.boolean(),
  currentUrl: z.string().describe('操作後のURL（不明の場合は空文字）'),
  pageSnapshot: z.string().optional().describe(
    'snapshot アクションの場合のみ返却',
  ),
  error: z.string().optional(),
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
// NavigationTool
// ---------------------------------------------------------------------------

/**
 * アクセシビリティベースのブラウザ操作ツール。
 *
 * CSSセレクタは使わない。要素特定は browser_snapshot の ref 値、
 * または getByRole/getByLabel/getByText 相当のアクセシブルな説明で行う。
 *
 * @param callPlaywright - playwright-mcp ツール呼び出し関数
 */
export const createNavigationTool = (callPlaywright: PlaywrightCaller) =>
  createTool({
    id: 'navigation',
    description:
      'アクセシビリティベースのブラウザ操作。' +
      'CSSセレクタは使わない。ref はスナップショットの要素参照値。',
    inputSchema,
    outputSchema,
    execute: async ({ context }) => {
      try {
        switch (context.action) {
          case 'navigate': {
            await callPlaywright('browser_navigate', { url: context.target })
            return { success: true, currentUrl: context.target }
          }
          case 'click': {
            await callPlaywright('browser_click', {
              ref: context.ref,
              element: context.target,
            })
            return { success: true, currentUrl: '' }
          }
          case 'type': {
            await callPlaywright('browser_type', {
              ref: context.ref,
              text: context.value ?? '',
              element: context.target,
            })
            return { success: true, currentUrl: '' }
          }
          case 'snapshot': {
            const result = await callPlaywright('browser_snapshot', {})
            return {
              success: true,
              currentUrl: '',
              pageSnapshot: extractText(result),
            }
          }
          case 'wait': {
            const args: Record<string, unknown> = {}
            if (context.target) args.text = context.target
            if (context.value) args.time = Number(context.value)
            await callPlaywright('browser_wait_for', args)
            return { success: true, currentUrl: '' }
          }
        }
      } catch (err) {
        return {
          success: false,
          currentUrl: '',
          error: err instanceof Error ? err.message : String(err),
        }
      }
    },
  })
