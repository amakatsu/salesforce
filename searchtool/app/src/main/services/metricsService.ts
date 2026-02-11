import { SearchMetrics } from '../../shared/contracts'

export interface SearchRecord {
  keyword: string
  metrics: SearchMetrics
  timestamp: string
}

export interface MetricsSummary {
  totalSearches: number
  recentSearches: SearchRecord[]
  averageDurationMs: number
  totalLocalHits: number
  totalRedmineHits: number
}

export class MetricsService {
  private searchHistory: SearchRecord[] = []
  private readonly maxHistorySize = 100

  recordSearch(keyword: string, metrics: SearchMetrics): void {
    const record: SearchRecord = {
      keyword,
      metrics,
      timestamp: new Date().toISOString(),
    }

    this.searchHistory.unshift(record)

    if (this.searchHistory.length > this.maxHistorySize) {
      this.searchHistory = this.searchHistory.slice(0, this.maxHistorySize)
    }
  }

  getSummary(limit: number = 10): MetricsSummary {
    const recentSearches = this.searchHistory.slice(0, limit)
    const totalSearches = this.searchHistory.length

    const averageDurationMs =
      totalSearches > 0
        ? this.searchHistory.reduce((sum, record) => sum + record.metrics.durationMs, 0) / totalSearches
        : 0

    const totalLocalHits = this.searchHistory.reduce((sum, record) => sum + record.metrics.localHits, 0)
    const totalRedmineHits = this.searchHistory.reduce((sum, record) => sum + record.metrics.redmineHits, 0)

    return {
      totalSearches,
      recentSearches,
      averageDurationMs: Math.round(averageDurationMs),
      totalLocalHits,
      totalRedmineHits,
    }
  }

  getRecentSearches(limit: number = 10): SearchRecord[] {
    return this.searchHistory.slice(0, limit)
  }

  seed(records: SearchRecord[]): void {
    if (!Array.isArray(records) || records.length === 0) {
      return
    }
    this.searchHistory = records.slice(0, this.maxHistorySize)
  }

  clear(): void {
    this.searchHistory = []
  }
}
