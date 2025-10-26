import { Agent } from '@mastra/core/agent'
import { z } from 'zod'
import { AppSettings } from '../../shared/settings'
import type { SearchHit } from '../../shared/contracts'
import { invokeMcp } from './tools/mcpClient'
import { localSearchTool } from './tools/localTool'
import { redmineSearchTool } from './tools/redmineTool'
import { sharepointSearchTool } from './tools/sharepointTool'
import { teamsSearchTool } from './tools/teamsTool'
import { internalDocsSearchTool } from './tools/internalDocsTool'
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
}

let cachedAgent: Agent | null = null

const SEARCH_AGENT_PROMPT = `あなたは社内ナレッジ検索エージェントです。以下を厳密に守ってください。
- まず mcp_local_search を1回だけ呼び、ローカル資料を取得して要点を整理する
- 次に (Redmineが設定されている場合) mcp_redmine_search を1回だけ呼ぶ
- local -> redmine の順序を守り、重複URL/パスを統合し上位20件以内に収める
- 最終出力は JSON (summary, reasons, local[], redmine[] で構成) のみを返す` as const

const summarySchema = structuredOutputSchema

export const generateAgentSummary = async ({ keyword, settings }: AgentRequest): Promise<AgentSummaryResult> => {
  const agent = ensureAgent()
  if (agent) {
    try {
      const prompt = buildAgentPrompt(keyword, settings)
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

      if (structured) {
        return {
          summary: structured.summary || 'No summary available',
          reasoning: structured.reasons.length ? structured.reasons : ['No reasoning available'],
          hits: {
            local: localHits,
            redmine: redmineHits,
            sharepoint: sharepointHits,
            teams: teamsHits,
            internalDocs: internalDocsHits,
          },
          errors: toolHits.errors,
          usedAgent: true,
        }
      }
    } catch (error) {
      console.error('Mastra agent execution failed', error)
    }
  }

  const fallback = await runDirectSearch(keyword, settings)
  return {
    summary: `検索結果: Local ${fallback.localHits.length}件, Redmine ${fallback.redmineHits.length}件, SharePoint ${fallback.sharepointHits.length}件, Teams ${fallback.teamsHits.length}件, 社内ドキュメント ${fallback.internalDocsHits.length}件`,
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

const ensureAgent = () => {
  if (cachedAgent) {
    return cachedAgent
  }
  const model = resolveModelConfig()
  if (!model) {
    return null
  }
  cachedAgent = new Agent({
    name: 'search-agent',
    instructions: SEARCH_AGENT_PROMPT,
    model,
    maxRetries: 1,
    tools: {
      mcp_local_search: localSearchTool,
      mcp_redmine_search: redmineSearchTool,
      mcp_sharepoint_search: sharepointSearchTool,
      mcp_teams_search: teamsSearchTool,
      mcp_internalDocs_search: internalDocsSearchTool,
    },
  })
  return cachedAgent
}

const resolveModelConfig = () => {
  const openAiKey = process.env.OPENAI_API_KEY ?? process.env.MASTRA_OPENAI_API_KEY
  if (!openAiKey) {
    return null
  }
  const envModel = process.env.MASTRA_MODEL_ID
  const modelId = (envModel && envModel.includes('/') ? envModel : 'openai/gpt-4o-mini') as `${string}/${string}`
  return {
    id: modelId,
    apiKey: openAiKey,
  }
}

const buildAgentPrompt = (keyword: string, settings: AppSettings) => {
  const localParams = {
    root: settings.local.root,
    query: keyword,
    max: settings.limits.localMaxResults,
    excludeGlobs: settings.excludeGlobs,
  }

  const webSearchInfo = {
    redmineUrls: settings.redmine.urls.filter((u) => u.trim()),
    sharepointUrls: settings.sharepoint.urls.filter((u) => u.trim()),
    teamsUrls: settings.teams.urls.filter((u) => u.trim()),
    internalDocsUrl: settings.internalDocs.baseUrl || '',
    userDataDir: settings.browser.userDataDir,
    max: settings.limits.redmineMaxResults,
    timeoutSeconds: settings.limits.timeoutSeconds,
  }

  return `# ユーザー入力\n${keyword}\n\n# ローカル検索パラメータ\n${JSON.stringify(localParams, null, 2)}\n\n# Web検索設定\n${JSON.stringify(webSearchInfo, null, 2)}\n\n- local.searchは必ず上記JSONを参考に入力を作成すること\n- Web検索は設定されたURLが空でない場合のみ実行すること\n- すべての回答は日本語で書き、JSON以外のテキストを含めないこと`
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

const runDirectSearch = async (keyword: string, settings: AppSettings) => {
  const localResponse = (await invokeMcp('local.search', {
    root: settings.local.root,
    query: keyword,
    max: settings.limits.localMaxResults,
    excludeGlobs: settings.excludeGlobs,
  })) as { results: LocalSearchHit[] }

  const localHits = dedupeHits(mapLocalHits(localResponse.results ?? []))
  const errors = {
    redmine: null as string | null,
    sharepoint: null as string | null,
    teams: null as string | null,
    internalDocs: null as string | null,
  }

  let redmineHits: SearchHit[] = []
  let sharepointHits: SearchHit[] = []
  let teamsHits: SearchHit[] = []
  let internalDocsHits: SearchHit[] = []

  // Redmine検索（複数URL対応）
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

  // SharePoint検索（複数URL対応）
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

  // Teams検索（複数URL対応）
  const teamsUrls = settings.teams.urls.filter((url) => url.trim())
  if (teamsUrls.length > 0) {
    const teamsResults = await Promise.allSettled(
      teamsUrls.map(async (baseUrl) => {
        const response = (await invokeMcp('teams.search' as const, {
          baseUrl,
          keyword,
          max: settings.limits.redmineMaxResults,
          timeoutSeconds: settings.limits.timeoutSeconds,
          userDataDir: settings.browser.userDataDir || undefined,
        })) as { results: TeamsSearchHit[] }
        return response.results ?? []
      }),
    )

    const allTeamsHits: TeamsSearchHit[] = []
    const teamsErrors: string[] = []

    teamsResults.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        allTeamsHits.push(...result.value)
      } else {
        teamsErrors.push(`${teamsUrls[index]}: ${result.reason}`)
      }
    })

    teamsHits = dedupeHits(mapTeamsHits(allTeamsHits))
    if (teamsErrors.length > 0) {
      errors.teams = teamsErrors.join('; ')
    }
  }

  // 社内ドキュメント検索
  if (settings.internalDocs.baseUrl?.trim()) {
    try {
      const internalDocsResponse = (await invokeMcp('internalDocs.search' as const, {
        baseUrl: settings.internalDocs.baseUrl,
        keyword,
        max: settings.limits.redmineMaxResults,
        timeoutSeconds: settings.limits.timeoutSeconds,
        userDataDir: settings.browser.userDataDir || undefined,
      })) as { results: InternalDocsSearchHit[] }
      internalDocsHits = dedupeHits(mapInternalDocsHits(internalDocsResponse.results ?? []))
    } catch (error) {
      errors.internalDocs = error instanceof Error ? error.message : '社内ドキュメント検索に失敗しました'
    }
  }

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
