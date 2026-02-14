import { createTool } from '@mastra/core/tools'
import { z } from 'zod'
import type { PlaywrightCaller } from './navigation'

// ---------------------------------------------------------------------------
// Schema（tool_interfaces.md §3a 準拠）
// ---------------------------------------------------------------------------

const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード'),
  maxResults: z
    .number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe('最大取得件数（Agent が抽出時に参照する上限）'),
  siteScope: z
    .string()
    .url()
    .optional()
    .describe('検索対象を絞るSharePointサイトURL（省略時はエラー）'),
})

const outputSchema = z.object({
  pageSnapshot: z
    .string()
    .describe('検索結果ページのアクセシビリティスナップショット（Markdown形式）'),
  searchUrl: z.string().describe('実際に検索したURL'),
  currentUrl: z.string().describe('スナップショット取得時のURL'),
})

// ---------------------------------------------------------------------------
// SharePoint 検索 URL 構築
// ---------------------------------------------------------------------------

const buildSearchUrl = (siteScope: string, keyword: string): string => {
  const url = new URL(siteScope)
  const basePath = url.pathname.endsWith('/') ? url.pathname : `${url.pathname}/`
  url.pathname = `${basePath}_layouts/15/osssearchresults.aspx`
  url.search = ''
  url.searchParams.set('k', keyword)
  return url.toString()
}

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
// SharePointSearchTool
// ---------------------------------------------------------------------------

const WAIT_SECONDS = 3

/**
 * SharePoint 検索ページへ遷移し、結果ページのスナップショットを返す。
 * 結果の解釈は Agent が ExtractTool で行う。固定セレクタは使わない。
 *
 * @param callPlaywright - 共有の playwright-mcp 呼び出し関数
 */
export const createSharePointSearchTool = (callPlaywright: PlaywrightCaller) =>
  createTool({
    id: 'sharepoint_search',
    description:
      'SharePoint検索ページへ遷移し、結果ページのアクセシビリティスナップショットを返す。' +
      '結果の解釈はAgentがExtractToolで行う。固定セレクタは使わない。',
    inputSchema,
    outputSchema,
    execute: async ({ context }) => {
      if (!context.siteScope) {
        throw new Error('siteScope（SharePointサイトURL）が必要です')
      }

      const searchUrl = buildSearchUrl(context.siteScope, context.keyword)

      // 1. 検索URLへ遷移（キーワードはURLパラメータで渡す）
      await callPlaywright('browser_navigate', { url: searchUrl })

      // 2. ページ読み込みを待機
      await callPlaywright('browser_wait_for', { time: WAIT_SECONDS })

      // 3. アクセシビリティスナップショットを取得
      const snapshotResult = await callPlaywright('browser_snapshot', {})
      const pageSnapshot = extractText(snapshotResult)

      if (!pageSnapshot) {
        throw new Error('スナップショットの取得に失敗しました')
      }

      return { pageSnapshot, searchUrl, currentUrl: searchUrl }
    },
  })
