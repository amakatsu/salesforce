import { AppSettings } from '../../shared/settings'
import { SearchPayload, SearchResponse, SearchService } from '../../shared/contracts'
import { generateAgentSummary } from '../mastra/agent'
import type { Logger } from './logger'
import type { MetricsService } from './metricsService'

export const createSearchService = (logger: Logger, metricsService: MetricsService): SearchService => {
  return {
    async runSearch(payload: SearchPayload, settings: AppSettings): Promise<SearchResponse> {
      const startedAt = Date.now()
      const resolvedKeyword = payload.keyword

      logger.info('Search request received', 'searchService', { keyword: resolvedKeyword })

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
        const agentResult = await generateAgentSummary({ keyword: resolvedKeyword, settings })
        const durationMs = Date.now() - startedAt

        const metrics = {
          startedAt: new Date(startedAt).toISOString(),
          durationMs,
          localHits: agentResult.hits.local.length,
          redmineHits: agentResult.hits.redmine.length,
          sharepointHits: agentResult.hits.sharepoint.length,
          teamsHits: agentResult.hits.teams.length,
          internalDocsHits: agentResult.hits.internalDocs.length,
        }

        metricsService.recordSearch(resolvedKeyword, metrics)

        logger.info('Search completed successfully', 'searchService', {
          keyword: resolvedKeyword,
          durationMs,
          localHits: metrics.localHits,
          redmineHits: metrics.redmineHits,
          sharepointHits: metrics.sharepointHits,
          teamsHits: metrics.teamsHits,
          internalDocsHits: metrics.internalDocsHits,
          usedAgent: agentResult.usedAgent,
        })

        // すべての結果を統合して combined に格納（重要度順にソート）
        const combinedHits = [
          ...agentResult.hits.local,
          ...agentResult.hits.redmine,
          ...agentResult.hits.sharepoint,
          ...agentResult.hits.teams,
          ...agentResult.hits.internalDocs,
        ].slice(0, 50) // 最大50件まで

        return {
          keyword: resolvedKeyword,
          summary: agentResult.summary,
          reasoning: agentResult.reasoning,
          metrics,
          hits: {
            ...agentResult.hits,
            combined: combinedHits,
          },
        }
      } catch (error) {
        const durationMs = Date.now() - startedAt
        logger.error('Search failed', 'searchService', {
          keyword: resolvedKeyword,
          durationMs,
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
