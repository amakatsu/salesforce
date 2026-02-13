import { Agent } from '@mastra/core/agent'
import type { AppSettings } from '../../shared/settings'
import type { SearchHit, SearchSource, PrimarySearchSource } from '../../shared/contracts'
import { createPlaywrightMcpClient } from './mcp-config'
import { createNavigationTool, type PlaywrightCaller } from './tools/navigation'
import { createRetryTool } from './tools/retry'
import { sharePointSearchTool } from './tools/sharepoint-search'
import { extractTool } from './tools/extract'
import { internalDocsSearchTool } from './tools/internal-docs-search'
import { teamsMessageSearchTool } from './tools/teams-message-search'

/**
 * Search Agent — スナップショットベース適応型設計
 *
 * 固定セレクタ禁止。
 * playwright-mcp の browser_snapshot でページ構造を取得し、
 * Agent が自律的に検索UIの要素を特定・操作・結果抽出を行う。
 *
 * 【拡張ポイント】
 * - instructions を検索ソースごとにカスタマイズ可能
 */

const SEARCH_AGENT_INSTRUCTIONS = `あなたは社内ナレッジ検索エージェントです。
Webブラウザを操作して、指定された検索ソースからキーワードに関連する情報を取得します。

## 利用可能なツール
- navigation: ブラウザ操作（navigate/click/type/snapshot/wait）
- retry: 判断失敗時に新しいスナップショットを取得
- sharepointSearch: SharePoint検索ページへ遷移しスナップショットを返す
- internalDocsSearch: 社内ドキュメントサイトへ遷移しスナップショットを返す
- teamsMessageSearch: Teams のメッセージ本文を検索。scope で chat/channel/all を選択可能
- extract: スナップショットから検索結果を構造化データに変換

## 動作原則
- navigation({ action: "snapshot" }) でページのアクセシビリティツリーを取得し、UIの構造を理解する
- スナップショットから検索入力欄やボタンの ref を特定し、navigation({ action: "type" / "click" }) で操作する
- 固定のCSSセレクタには依存しない。常にスナップショットから要素を判断する
- 検索結果はスナップショットから構造化データとして抽出する
- スナップショットの解釈に失敗した場合は retry で新しいスナップショットを取得し再判断する（最大3回）

## 出力形式
検索結果は以下のJSON形式で返すこと:
{
  "results": [
    { "title": "結果タイトル", "url": "結果のURL", "snippet": "説明文（300文字以内）" }
  ]
}

## 制約
- ナビゲーション・ヘッダー・フッター・広告は除外すること
- JSON以外のテキストを出力しないこと
- 1回の検索で最大20件まで取得すること
` as const

// ---------------------------------------------------------------------------
// 型定義
// ---------------------------------------------------------------------------

type SourceHits = Record<PrimarySearchSource, SearchHit[]>

export interface SearchAgentResult {
  summary: string
  reasoning: string[]
  hits: SourceHits
  errors: Partial<Record<PrimarySearchSource, string>>
}

interface SearchAgentRequest {
  keyword: string
  settings: AppSettings
  enabledSources: SearchSource[]
}

// ---------------------------------------------------------------------------
// Playwright 呼び出しプロキシ
// ---------------------------------------------------------------------------
// リクエストごとに実体を差し替える。Agent のツールはキャッシュされるが、
// 実際の playwright-mcp 接続はリクエスト単位で作られるため、
// プロキシで間接参照する。

let activePlaywrightCaller: PlaywrightCaller | null = null

const callPlaywrightProxy: PlaywrightCaller = async (toolName, args) => {
  if (!activePlaywrightCaller) {
    throw new Error('PlaywrightClient が接続されていません')
  }
  return activePlaywrightCaller(toolName, args)
}

/**
 * MCPClient のツールセットから PlaywrightCaller を構築する。
 * toolsets['playwright'] 内の各ツールの execute を呼び出す薄いラッパー。
 */
const buildPlaywrightCaller = (
  toolsets: Record<string, Record<string, { execute: (args: unknown) => Promise<unknown> }>>,
): PlaywrightCaller => {
  const playwrightTools = toolsets['playwright']
  if (!playwrightTools) {
    throw new Error('playwright ツールセットが見つかりません')
  }
  return async (toolName, args) => {
    const tool = playwrightTools[toolName]
    if (!tool) {
      throw new Error(`Unknown playwright tool: ${toolName}`)
    }
    return tool.execute(args)
  }
}

// ---------------------------------------------------------------------------
// Agent キャッシュ
// ---------------------------------------------------------------------------

let cachedAgent: Agent | null = null
let cachedApiKey = ''

const ensureAgent = (settings: AppSettings): Agent | null => {
  const apiKey =
    settings.ai.apiKey ||
    process.env.OPENAI_API_KEY ||
    process.env.MASTRA_OPENAI_API_KEY ||
    ''
  if (!apiKey) return null

  if (cachedAgent && cachedApiKey === apiKey) return cachedAgent

  let modelId = settings.ai.modelId || process.env.MASTRA_MODEL_ID || 'openai/gpt-4o-mini'
  if (!modelId.includes('/')) {
    modelId = `openai/${modelId}`
  }

  cachedApiKey = apiKey
  cachedAgent = new Agent({
    name: 'search-agent',
    instructions: SEARCH_AGENT_INSTRUCTIONS,
    model: {
      id: modelId as `${string}/${string}`,
      apiKey,
    },
    tools: {
      navigation: createNavigationTool(callPlaywrightProxy),
      retry: createRetryTool(callPlaywrightProxy),
      sharepointSearch: sharePointSearchTool,
      extract: extractTool,
      internalDocsSearch: internalDocsSearchTool,
      teamsMessageSearch: teamsMessageSearchTool,
    },
  })

  return cachedAgent
}

// ---------------------------------------------------------------------------
// 空の SourceHits を生成
// ---------------------------------------------------------------------------

const emptyHits = (): SourceHits => ({
  local: [],
  redmine: [],
  sharepoint: [],
  teams: [],
  internalDocs: [],
})

// ---------------------------------------------------------------------------
// メイン実行
// ---------------------------------------------------------------------------

/**
 * Search Agent を実行する。
 *
 * playwright-mcp への接続を確立し、NavigationTool / RetryTool が
 * プロキシ経由でブラウザ操作を行えるようにしてから Agent を実行する。
 *
 * Agent は NavigationTool / RetryTool を通じてブラウザを操作する。
 * playwright-mcp の生ツール（browser_*）は Agent に直接公開しない。
 */
export const runSearchAgent = async ({
  keyword,
  settings,
  enabledSources,
}: SearchAgentRequest): Promise<SearchAgentResult> => {
  const agent = ensureAgent(settings)
  if (!agent) {
    return {
      summary: 'APIキーが設定されていません',
      reasoning: ['OpenAI APIキーを設定画面で入力してください'],
      hits: emptyHits(),
      errors: {},
    }
  }

  const mcpClient = createPlaywrightMcpClient(settings)

  try {
    const toolsets = await mcpClient.getToolsets()

    // NavigationTool / RetryTool が playwright-mcp を呼べるようにプロキシを設定
    activePlaywrightCaller = buildPlaywrightCaller(toolsets)

    const prompt = buildPrompt(keyword, enabledSources)

    const response = await agent.generate(
      [{ role: 'user' as const, content: prompt }],
    )

    // 【拡張ポイント】
    // 後続タスクで toolResults からソースごとの SearchHit[] を抽出するロジックを追加
    return {
      summary: response.text || '検索完了',
      reasoning: ['search agent executed'],
      hits: emptyHits(),
      errors: {},
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    return {
      summary: `検索エージェントでエラーが発生しました: ${message}`,
      reasoning: [message],
      hits: emptyHits(),
      errors: {},
    }
  } finally {
    activePlaywrightCaller = null
    await mcpClient.disconnect()
  }
}

// ---------------------------------------------------------------------------
// プロンプト構築
// ---------------------------------------------------------------------------

const buildPrompt = (keyword: string, enabledSources: SearchSource[]): string => {
  return `# 検索リクエスト
キーワード: ${keyword}
有効なソース: ${enabledSources.join(', ')}

上記のキーワードで検索を実行し、結果をJSON形式で返してください。`
}
