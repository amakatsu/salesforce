import { Agent } from '@mastra/core/agent'
import { z } from 'zod'
import { AppSettings } from '../../shared/settings'
import { SEARCH_SOURCES, type SearchHit, type SearchSource } from '../../shared/contracts'
import { invokeMcp } from './tools/mcpClient'
import { localSearchTool } from './tools/localTool'
import { redmineSearchTool } from './tools/redmineTool'
import { sharepointSearchTool } from './tools/sharepointTool'
import { teamsMessageSearchTool } from './tools/teams-message-search'
import { internalDocsSearchTool } from './tools/internal-docs-search'
import type { LocalSearchHit } from '../mcp-servers/local-fs.server'
import type { RedmineSearchHit } from '../mcp-servers/redmine-ui.server'
import type { SharePointSearchHit } from '../mcp-servers/sharepoint-search.server'
import type { TeamsSearchHit } from '../mcp-servers/teams-search.server'
import type { InternalDocsSearchHit } from '../mcp-servers/internal-docs-search.server'

const structuredOutputSchema = z.object({
  summary: z.string().min(1),
  reasons: z.array(z.string().min(1)).min(1).max(8),
  local: z
    .array(
      z.object({
        title: z.string().optional(),
        reference: z.string().min(1),
        snippet: z.string().min(1),
      }),
    )
    .max(20)
    .default([]),
  redmine: z
    .array(
      z.object({
        title: z.string().optional(),
        reference: z.string().min(1),
        snippet: z.string().min(1),
      }),
    )
    .max(20)
    .default([]),
})

type StructuredOutput = z.infer<typeof structuredOutputSchema>

export interface AgentSummaryResult {
  summary: string
  reasoning: string[]
  hits: {
    local: SearchHit[]
    redmine: SearchHit[]
    sharepoint: SearchHit[]
    teams: SearchHit[]
    internalDocs: SearchHit[]
  }
  errors: {
    redmine?: string | null
    sharepoint?: string | null
    teams?: string | null
    internalDocs?: string | null
  }
  usedAgent: boolean
}

interface AgentRequest {
  keyword: string
  settings: AppSettings
  enabledSources: SearchSource[]
}

let cachedAgent: Agent | null = null
let cachedApiKey: string | null = null

const SEARCH_AGENT_PROMPT = `あなたは社内ナレッジ検索エージェントです。以下を厳密に守ってください。
- ユーザーが有効化した検索ソース（local/redmine/sharepoint/teams/internalDocs）のみを対象とすること
- mcp_local_search を最優先で実行し、必要に応じて他ソースを1回ずつ実行する
- 重複URL/パスを統合し、ソースごとに上位20件以内に収める
- 最終出力は JSON (summary, reasons, local[], redmine[] で構成) のみを返す` as const

const summarySchema = structuredOutputSchema
const SOURCE_LABELS: Record<typeof SEARCH_SOURCES[number], string> = {
  local: 'Local',
  redmine: 'Redmine',
  sharepoint: 'SharePoint',
  teams: 'Teams',
  internalDocs: '社内Docs',
}

const buildSummaryFromCounts = (counts: Record<typeof SEARCH_SOURCES[number], number>, enabledSet: Set<SearchSource>) => {
  const parts = SEARCH_SOURCES.filter((source) => enabledSet.has(source)).map((source) => `${SOURCE_LABELS[source]} ${counts[source] ?? 0}件`)
  return parts.length ? `検索結果: ${parts.join(', ')}` : '検索対象が選択されていません'
}

export const generateAgentSummary = async ({ keyword, settings, enabledSources }: AgentRequest): Promise<AgentSummaryResult> => {
  const enabledSet = new Set<SearchSource>(enabledSources)
  const agent = ensureAgent(settings)
  if (agent) {
    try {
      const prompt = buildAgentPrompt(keyword, settings, enabledSources)
      const full = await agent.generate(
        [
          {
            role: 'user',
            content: prompt,
          },
        ],
        {
          output: summarySchema,
        },
      )
      const structured = (full.object ?? null) as StructuredOutput | null
      const toolHits = collectToolHits(full.toolResults ?? [])

      const localHits = dedupeHits(toolHits.local.length ? toolHits.local : mapStructuredHits(structured?.local ?? [], 'local'))
      const redmineHits = dedupeHits(toolHits.redmine)
      const sharepointHits = dedupeHits(toolHits.sharepoint)
      const teamsHits = dedupeHits(toolHits.teams)
      const internalDocsHits = dedupeHits(toolHits.internalDocs)

      const filteredHits = {
        local: enabledSet.has('local') ? localHits : [],
        redmine: enabledSet.has('redmine') ? redmineHits : [],
        sharepoint: enabledSet.has('sharepoint') ? sharepointHits : [],
        teams: enabledSet.has('teams') ? teamsHits : [],
        internalDocs: enabledSet.has('internalDocs') ? internalDocsHits : [],
      }

      const filteredErrors = {
        redmine: enabledSet.has('redmine') ? toolHits.errors.redmine : null,
        sharepoint: enabledSet.has('sharepoint') ? toolHits.errors.sharepoint : null,
        teams: enabledSet.has('teams') ? toolHits.errors.teams : null,
        internalDocs: enabledSet.has('internalDocs') ? toolHits.errors.internalDocs : null,
      }

      if (structured) {
        return {
          summary: structured.summary || 'No summary available',
          reasoning: structured.reasons.length ? structured.reasons : ['No reasoning available'],
          hits: filteredHits,
          errors: filteredErrors,
          usedAgent: true,
        }
      }
    } catch (error) {
      console.error('Mastra agent execution failed', error)
    }
  }

  const fallback = await runDirectSearch(keyword, settings, enabledSources)
  const summaryText = buildSummaryFromCounts(
    {
      local: fallback.localHits.length,
      redmine: fallback.redmineHits.length,
      sharepoint: fallback.sharepointHits.length,
      teams: fallback.teamsHits.length,
      internalDocs: fallback.internalDocsHits.length,
    },
    enabledSet,
  )
  return {
    summary: summaryText,
    reasoning: ['Fallback search completed'],
    hits: {
      local: fallback.localHits,
      redmine: fallback.redmineHits,
      sharepoint: fallback.sharepointHits,
      teams: fallback.teamsHits,
      internalDocs: fallback.internalDocsHits,
    },
    errors: fallback.errors,
    usedAgent: false,
  }
}

const ensureAgent = (settings: AppSettings) => {
  // APIキーが変更されたらキャッシュをクリア
  const currentApiKey = settings.ai.apiKey || process.env.OPENAI_API_KEY || process.env.MASTRA_OPENAI_API_KEY || ''
  if (cachedAgent && cachedApiKey !== currentApiKey) {
    cachedAgent = null
  }

  if (cachedAgent) {
    return cachedAgent
  }

  const model = resolveModelConfig(settings)
  if (!model) {
    return null
  }

  cachedApiKey = currentApiKey
  cachedAgent = new Agent({
    name: 'search-agent',
    instructions: SEARCH_AGENT_PROMPT,
    model,
    maxRetries: 1,
    tools: {
      mcp_local_search: localSearchTool,
      mcp_redmine_search: redmineSearchTool,
      mcp_sharepoint_search: sharepointSearchTool,
      mcp_teams_search: teamsMessageSearchTool,
      mcp_internalDocs_search: internalDocsSearchTool,
    },
  })
  return cachedAgent
}

const resolveModelConfig = (settings: AppSettings) => {
  // 設定画面のAPIキーを優先、なければ環境変数
  const openAiKey = settings.ai.apiKey || process.env.OPENAI_API_KEY || process.env.MASTRA_OPENAI_API_KEY
  if (!openAiKey) {
    return null
  }

  // 設定画面のモデルIDを優先、なければ環境変数、デフォルトはgpt-4o-mini
  let modelId = settings.ai.modelId || process.env.MASTRA_MODEL_ID || 'openai/gpt-4o-mini'

  // モデルIDに'/'が含まれていない場合は'openai/'を付ける
  if (!modelId.includes('/')) {
    modelId = `openai/${modelId}`
  }

  return {
    id: modelId as `${string}/${string}`,
    apiKey: openAiKey,
  }
}

const buildAgentPrompt = (keyword: string, settings: AppSettings, enabledSources: SearchSource[]) => {
  const enabledSet = new Set<SearchSource>(enabledSources)
  const localParams = {
    root: enabledSet.has('local') ? settings.local.root : [],
    query: keyword,
    max: settings.limits.localMaxResults,
    excludeGlobs: settings.excludeGlobs,
  }

  const webSearchInfo = {
    redmineUrls: enabledSet.has('redmine') ? settings.redmine.urls.filter((u) => u.trim()) : [],
    sharepointUrls: enabledSet.has('sharepoint') ? settings.sharepoint.urls.filter((u) => u.trim()) : [],
    teamsUrls: enabledSet.has('teams') ? settings.teams.urls.filter((u) => u.trim()) : [],
    internalDocsUrl: enabledSet.has('internalDocs') ? settings.internalDocs.baseUrl || '' : '',
    userDataDir: settings.browser.userDataDir,
    max: settings.limits.redmineMaxResults,
    timeoutSeconds: settings.limits.timeoutSeconds,
  }

  return `# ユーザー入力
${keyword}

# 有効な検索対象
${JSON.stringify(enabledSources)}

# ローカル検索パラメータ
${JSON.stringify(localParams, null, 2)}

# Web検索設定
${JSON.stringify(webSearchInfo, null, 2)}

- enabledSources に含まれないソースは絶対に検索しないこと
- local.searchは必ず上記JSONを参考に入力を作成すること
- Web検索は設定されたURLが空でない場合のみ実行すること
- すべての回答は日本語で書き、JSON以外のテキストを含めないこと`
}
const collectToolHits = (toolResults: any[]) => {
  const local: SearchHit[] = []
  const redmine: SearchHit[] = []
  const sharepoint: SearchHit[] = []
  const teams: SearchHit[] = []
  const internalDocs: SearchHit[] = []
  const errors = {
    redmine: null as string | null,
    sharepoint: null as string | null,
    teams: null as string | null,
    internalDocs: null as string | null,
  }

  for (const chunk of toolResults ?? []) {
    const toolName = chunk?.payload?.toolName
    const { result, isError } = chunk?.payload ?? {}

    if (toolName === 'mcp_local_search' && Array.isArray(result?.results) && !isError) {
      local.push(...mapLocalHits(result.results as LocalSearchHit[]))
    }

    if (toolName === 'mcp_redmine_search') {
      if (isError) {
        errors.redmine = typeof result?.message === 'string' ? result.message : 'Redmine検索でエラーが発生しました'
      } else if (Array.isArray(result?.results)) {
        redmine.push(...mapRedmineHits(result.results as RedmineSearchHit[]))
      }
    }

    if (toolName === 'mcp_sharepoint_search') {
      if (isError) {
        errors.sharepoint = typeof result?.message === 'string' ? result.message : 'SharePoint検索でエラーが発生しました'
      } else if (Array.isArray(result?.results)) {
        sharepoint.push(...mapSharePointHits(result.results as SharePointSearchHit[]))
      }
    }

    if (toolName === 'mcp_teams_search') {
      if (isError) {
        errors.teams = typeof result?.message === 'string' ? result.message : 'Teams検索でエラーが発生しました'
      } else if (Array.isArray(result?.results)) {
        teams.push(...mapTeamsHits(result.results as TeamsSearchHit[]))
      }
    }

    if (toolName === 'mcp_internalDocs_search') {
      if (isError) {
        errors.internalDocs = typeof result?.message === 'string' ? result.message : '社内ドキュメント検索でエラーが発生しました'
      } else if (Array.isArray(result?.results)) {
        internalDocs.push(...mapInternalDocsHits(result.results as InternalDocsSearchHit[]))
      }
    }
  }

  return {
    local,
    redmine,
    sharepoint,
    teams,
    internalDocs,
    errors,
  }
}

const mapStructuredHits = (rows: StructuredOutput['local'], source: 'local' | 'redmine'): SearchHit[] => {
  return rows.map((row, index) => ({
    id: `${source}-structured-${index}-${row.reference}`,
    source,
    title: row.title || row.reference,
    reference: row.reference,
    snippet: row.snippet,
  }))
}

const mapLocalHits = (hits: LocalSearchHit[]): SearchHit[] =>
  hits.map((hit, index) => ({
    id: `local-${index}-${hit.path}-${hit.line}`,
    source: 'local',
    title: hit.path,
    reference: `${hit.path}:${hit.line}`,
    snippet: hit.snippet,
  }))

const mapRedmineHits = (hits: RedmineSearchHit[]): SearchHit[] =>
  hits.map((hit, index) => ({
    id: `redmine-${index}-${hit.url}-${index}`,
    source: 'redmine',
    title: hit.title || hit.url,
    reference: hit.url,
    snippet: hit.snippet,
  }))

const mapSharePointHits = (hits: SharePointSearchHit[]): SearchHit[] =>
  hits.map((hit, index) => ({
    id: `sharepoint-${index}-${hit.url}`,
    source: 'sharepoint',
    title: hit.title || hit.url,
    reference: hit.url,
    snippet: hit.snippet,
  }))

const mapTeamsHits = (hits: TeamsSearchHit[]): SearchHit[] =>
  hits.map((hit, index) => ({
    id: `teams-${index}-${hit.url}`,
    source: 'teams',
    title: hit.title || hit.url,
    reference: hit.url,
    snippet: hit.snippet,
  }))

const mapInternalDocsHits = (hits: InternalDocsSearchHit[]): SearchHit[] =>
  hits.map((hit, index) => ({
    id: `internalDocs-${index}-${hit.url}`,
    source: 'internalDocs',
    title: hit.title || hit.url,
    reference: hit.url,
    snippet: hit.snippet,
  }))

const dedupeHits = (hits: SearchHit[]) => {
  const seen = new Set<string>()
  const result: SearchHit[] = []
  for (const hit of hits) {
    const key = `${hit.source}-${hit.reference}`
    if (seen.has(key)) continue
    seen.add(key)
    result.push(hit)
    if (result.length >= 20) break
  }
  return result
}

const runDirectSearch = async (keyword: string, settings: AppSettings, enabledSources: SearchSource[]) => {
  const enabledSet = new Set<SearchSource>(enabledSources)
  const shouldRun = (source: SearchSource) => enabledSet.has(source)

  const errors = {
    redmine: null as string | null,
    sharepoint: null as string | null,
    teams: null as string | null,
    internalDocs: null as string | null,
  }

  let localHits: SearchHit[] = []
  if (shouldRun('local')) {
    const localResponse = (await invokeMcp('local.search', {
      root: settings.local.root,
      query: keyword,
      max: settings.limits.localMaxResults,
      excludeGlobs: settings.excludeGlobs,
    })) as { results: LocalSearchHit[] }
    localHits = dedupeHits(mapLocalHits(localResponse.results ?? []))
  }

  let redmineHits: SearchHit[] = []
  if (shouldRun('redmine')) {
    const redmineUrls = settings.redmine.urls.filter((url) => url.trim())
    if (redmineUrls.length > 0) {
      const redmineResults = await Promise.allSettled(
        redmineUrls.map(async (baseUrl) => {
          const response = (await invokeMcp('redmine.search', {
            baseUrl,
            keyword,
            max: settings.limits.redmineMaxResults,
            timeoutSeconds: settings.limits.timeoutSeconds,
            userDataDir: settings.browser.userDataDir || undefined,
          })) as { results: RedmineSearchHit[] }
          return response.results ?? []
        }),
      )

      const allRedmineHits: RedmineSearchHit[] = []
      const redmineErrors: string[] = []

      redmineResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          allRedmineHits.push(...result.value)
        } else {
          redmineErrors.push(`${redmineUrls[index]}: ${result.reason}`)
        }
      })

      redmineHits = dedupeHits(mapRedmineHits(allRedmineHits))
      if (redmineErrors.length > 0) {
        errors.redmine = redmineErrors.join('; ')
      }
    }
  }

  let sharepointHits: SearchHit[] = []
  if (shouldRun('sharepoint')) {
    const sharepointUrls = settings.sharepoint.urls.filter((url) => url.trim())
    if (sharepointUrls.length > 0) {
      const sharepointResults = await Promise.allSettled(
        sharepointUrls.map(async (baseUrl) => {
          const response = (await invokeMcp('sharepoint.search' as const, {
            baseUrl,
            keyword,
            max: settings.limits.redmineMaxResults,
            timeoutSeconds: settings.limits.timeoutSeconds,
            userDataDir: settings.browser.userDataDir || undefined,
          })) as { results: SharePointSearchHit[] }
          return response.results ?? []
        }),
      )

      const allSharePointHits: SharePointSearchHit[] = []
      const sharepointErrors: string[] = []

      sharepointResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          allSharePointHits.push(...result.value)
        } else {
          sharepointErrors.push(`${sharepointUrls[index]}: ${result.reason}`)
        }
      })

      sharepointHits = dedupeHits(mapSharePointHits(allSharePointHits))
      if (sharepointErrors.length > 0) {
        errors.sharepoint = sharepointErrors.join('; ')
      }
    }
  }

  const teamsHits: SearchHit[] = []

  const internalDocsHits: SearchHit[] = []

  return {
    localHits,
    redmineHits,
    sharepointHits,
    teamsHits,
    internalDocsHits,
    errors,
  }
}

// Removed unused buildFallbackSummary and buildFallbackReasoning functions
