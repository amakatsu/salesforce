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

  const client = new Client({ name: 'TeamsMessageSearchTool', version: '0.0.0' })
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
// Teams 検索 URL 構築
// ---------------------------------------------------------------------------

const TEAMS_BASE_URL = 'https://teams.microsoft.com'

const buildSearchUrl = (keyword: string): string => {
  const encoded = encodeURIComponent(keyword)
  return `${TEAMS_BASE_URL}/_#/search/messages/${encoded}`
}

// ---------------------------------------------------------------------------
// Tool 定義（tool_interfaces.md §3e 準拠）
// ---------------------------------------------------------------------------

const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード'),
  scope: z.enum(['chat', 'channel', 'all']).default('all')
    .describe('検索スコープ。chat: 1対1/グループチャット, channel: チャンネル, all: 両方'),
  maxResults: z
    .number()
    .int()
    .min(1)
    .max(50)
    .default(20)
    .describe('最大取得件数（Agent が抽出時に参照する上限）'),
})

const outputSchema = z.object({
  pageSnapshot: z
    .string()
    .describe('検索結果ページのアクセシビリティスナップショット（Markdown形式）'),
  searchUrl: z.string().describe('検索に使用したTeams URL'),
  currentUrl: z.string().describe('スナップショット取得時のURL'),
  scope: z.enum(['chat', 'channel', 'all']).describe('実際に検索したスコープ'),
})

export const teamsMessageSearchTool = createTool({
  id: 'teams_message_search',
  description:
    'Teams検索ページへ遷移し、メッセージ検索結果のアクセシビリティスナップショットを返す。' +
    '結果の解釈はAgentがExtractToolで行う。固定セレクタは使わない。',
  inputSchema,
  outputSchema,
  execute: async ({ context }) => {
    const { keyword, scope } = inputSchema.parse(context)

    const searchUrl = buildSearchUrl(keyword)
    const client = await connectPlaywright()

    try {
      // 1. Teams 検索ページへ遷移
      await callMcpTool(client, 'browser_navigate', { url: searchUrl }, TIMEOUT_MS)

      // 2. ページ読み込みを待機
      await callMcpTool(client, 'browser_wait_for', { time: WAIT_SECONDS }, TIMEOUT_MS)

      // 3. スコープフィルタの適用（all 以外の場合）
      if (scope !== 'all') {
        // スナップショットからフィルタタブの ref を特定して切り替え
        const filterSnapshot = await callMcpTool(client, 'browser_snapshot', {}, TIMEOUT_MS)
        const snapshotText = extractText(filterSnapshot)

        // フィルタタブ名を特定（Agent がスナップショットから判断する前提だが、
        // ここでは基本的なテキストマッチでタブ候補を探す）
        const tabLabel = scope === 'chat' ? 'Chat' : 'Channel'
        if (snapshotText.includes(tabLabel)) {
          await callMcpTool(client, 'browser_click', {
            element: `${tabLabel} filter tab`,
            ref: '',
          }, TIMEOUT_MS)
          await callMcpTool(client, 'browser_wait_for', { time: WAIT_SECONDS }, TIMEOUT_MS)
        }
      }

      // 4. アクセシビリティスナップショットを取得
      const snapshotResult = await callMcpTool(client, 'browser_snapshot', {}, TIMEOUT_MS)
      const pageSnapshot = extractText(snapshotResult)

      if (!pageSnapshot) {
        throw new Error('スナップショットの取得に失敗しました')
      }

      return { pageSnapshot, searchUrl, currentUrl: searchUrl, scope }
    } finally {
      await client.close().catch(() => undefined)
    }
  },
})
