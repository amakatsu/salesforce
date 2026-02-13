import { createTool } from '@mastra/core/tools'
import { z } from 'zod'
import { createRequire } from 'node:module'
import path from 'node:path'
import process from 'node:process'
import { Client } from '@modelcontextprotocol/sdk/client'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { CallToolResultSchema, type CallToolResult } from '@modelcontextprotocol/sdk/types.js'

// ---------------------------------------------------------------------------
// playwright-mcp 接続
// ---------------------------------------------------------------------------

const require = createRequire(import.meta.url)
const PLAYWRIGHT_MCP_ENTRY = path.resolve(
  require.resolve('playwright-mcp/package.json'),
  '..',
  'dist',
  'server.js',
)

const DEFAULT_BROWSER = 'msedge'
const WAIT_SECONDS = 3
const TIMEOUT_MS = 30_000

const connectPlaywright = async (userDataDir?: string): Promise<Client> => {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [PLAYWRIGHT_MCP_ENTRY, '--browser', DEFAULT_BROWSER],
    env: {
      ...process.env,
      PLAYWRIGHT_MCP_PROFILE_DIR: userDataDir ?? '',
    },
    stderr: 'pipe',
  })

  const client = new Client({ name: 'SharePointSearchTool', version: '0.0.0' })
  await client.connect(transport)
  return client
}

const callMcpTool = async (
  client: Client,
  name: string,
  args: Record<string, unknown>,
  timeoutMs: number,
): Promise<CallToolResult> => {
  const result = await client.request(
    { method: 'tools/call', params: { name, arguments: args } },
    CallToolResultSchema,
    { timeout: timeoutMs },
  )

  if (result.isError) {
    const message = extractText(result)
    throw new Error(message || `${name} failed`)
  }

  return result
}

const extractText = (result: CallToolResult): string =>
  result.content.find((c): c is { type: 'text'; text: string } => c.type === 'text')?.text ?? ''

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
// Tool 定義
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
    .describe('検索対象を絞るSharePointサイトURL'),
})

const outputSchema = z.object({
  pageSnapshot: z
    .string()
    .describe('検索結果ページのアクセシビリティスナップショット（Markdown形式）'),
  searchUrl: z.string().describe('実際に検索したURL'),
  currentUrl: z.string().describe('スナップショット取得時のURL'),
})

export const sharePointSearchTool = createTool({
  id: 'sharepoint_search',
  description:
    'SharePoint検索ページへ遷移し、結果ページのアクセシビリティスナップショットを返す。' +
    '結果の解釈はAgentがExtractToolで行う。固定セレクタは使わない。',
  inputSchema,
  outputSchema,
  execute: async ({ context }) => {
    const { keyword, siteScope } = inputSchema.parse(context)

    if (!siteScope) {
      throw new Error('siteScope（SharePointサイトURL）が必要です')
    }

    const searchUrl = buildSearchUrl(siteScope, keyword)
    const client = await connectPlaywright()

    try {
      // 1. 検索URLへ遷移（キーワードはURLパラメータで渡す）
      await callMcpTool(client, 'browser_navigate', { url: searchUrl }, TIMEOUT_MS)

      // 2. ページ読み込みを待機
      await callMcpTool(client, 'browser_wait_for', { time: WAIT_SECONDS }, TIMEOUT_MS)

      // 3. アクセシビリティスナップショットを取得
      const snapshotResult = await callMcpTool(client, 'browser_snapshot', {}, TIMEOUT_MS)
      const pageSnapshot = extractText(snapshotResult)

      if (!pageSnapshot) {
        throw new Error('スナップショットの取得に失敗しました')
      }

      return { pageSnapshot, searchUrl, currentUrl: searchUrl }
    } finally {
      await client.close().catch(() => undefined)
    }
  },
})
