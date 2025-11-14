import { AppSettings } from '../../shared/settings'
import { SearchPayload, SearchResponse, SearchService, type SearchSource } from '../../shared/contracts'
import { generateAgentSummary } from '../mastra/agent'
import type { Logger } from './logger'
import type { MetricsService } from './metricsService'

const ALL_SOURCES: SearchSource[] = ['local', 'redmine', 'sharepoint', 'teams', 'internalDocs']

const sanitizeSources = (sources?: SearchSource[]): SearchSource[] => {
  const desired = (sources ?? ALL_SOURCES).filter((source): source is SearchSource => ALL_SOURCES.includes(source))
  if (desired.length === 0) {
    return [...ALL_SOURCES]
  }
  const unique = new Set<SearchSource>(desired)
  return ALL_SOURCES.filter((source) => unique.has(source))
}

const resolveMaxCombinedHits = (value?: number): number => {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    return 50
  }
  return Math.min(200, Math.max(5, Math.floor(parsed)))
}

export const createSearchService = (logger: Logger, metricsService: MetricsService): SearchService => {
  return {
    async runSearch(payload: SearchPayload, settings: AppSettings): Promise<SearchResponse> {
      const startedAt = Date.now()
      const resolvedKeyword = payload.keyword
      const enabledSources = sanitizeSources(payload.sources)
      const maxCombinedHits = resolveMaxCombinedHits(payload.maxCombinedHits)

      logger.info('Search request received', 'searchService', {
        keyword: resolvedKeyword,
        enabledSources,
        maxCombinedHits,
      })

      if (!resolvedKeyword?.trim()) {
        const error = '検索キーワードを入力してください'
        logger.warn(error, 'searchService')
        throw new Error(error)
      }

      if (!settings.local.root || settings.local.root.length === 0) {
        const error = 'ローカル検索のルートディレクトリが設定されていません。設定画面で入力してください。'
        logger.warn(error, 'searchService')
        throw new Error(error)
      }

      try {
        const agentResult = await generateAgentSummary({ keyword: resolvedKeyword, settings, enabledSources })
        const durationMs = Date.now() - startedAt

        const filteredHits = {
          local: enabledSources.includes('local') ? agentResult.hits.local : [],
          redmine: enabledSources.includes('redmine') ? agentResult.hits.redmine : [],
          sharepoint: enabledSources.includes('sharepoint') ? agentResult.hits.sharepoint : [],
          teams: enabledSources.includes('teams') ? agentResult.hits.teams : [],
          internalDocs: enabledSources.includes('internalDocs') ? agentResult.hits.internalDocs : [],
        }

        const metrics = {
          startedAt: new Date(startedAt).toISOString(),
          durationMs,
          localHits: filteredHits.local.length,
          redmineHits: filteredHits.redmine.length,
          sharepointHits: filteredHits.sharepoint.length,
          teamsHits: filteredHits.teams.length,
          internalDocsHits: filteredHits.internalDocs.length,
        }

        metricsService.recordSearch(resolvedKeyword, metrics)

        logger.info('Search completed successfully', 'searchService', {
          keyword: resolvedKeyword,
          durationMs,
          enabledSources,
          maxCombinedHits,
          localHits: metrics.localHits,
          redmineHits: metrics.redmineHits,
          sharepointHits: metrics.sharepointHits,
          teamsHits: metrics.teamsHits,
          internalDocsHits: metrics.internalDocsHits,
          usedAgent: agentResult.usedAgent,
        })

        const combinedHits = [
          ...filteredHits.local,
          ...filteredHits.redmine,
          ...filteredHits.sharepoint,
          ...filteredHits.teams,
          ...filteredHits.internalDocs,
        ].slice(0, maxCombinedHits)

        return {
          keyword: resolvedKeyword,
          summary: agentResult.summary,
          reasoning: agentResult.reasoning,
          metrics,
          hits: {
            ...filteredHits,
            combined: combinedHits,
          },
        }
      } catch (error) {
        const durationMs = Date.now() - startedAt
        logger.error('Search failed', 'searchService', {
          keyword: resolvedKeyword,
          durationMs,
          enabledSources,
          maxCombinedHits,
          error: error instanceof Error ? error.message : String(error),
        })
        throw new Error(
          error instanceof Error
            ? `検索に失敗しました: ${error.message}`
            : '検索中に予期しないエラーが発生しました',
        )
      }
    },
  }
}
