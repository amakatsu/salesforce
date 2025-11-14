import { AppSettings } from './settings'

export type SearchSource = 'local' | 'redmine' | 'sharepoint' | 'teams' | 'internalDocs' | 'combined'
export const SEARCH_SOURCES = ['local', 'redmine', 'sharepoint', 'teams', 'internalDocs'] as const
export type PrimarySearchSource = (typeof SEARCH_SOURCES)[number]

export interface SearchPayload {
  keyword: string
  sources?: SearchSource[]
  maxCombinedHits?: number
}

export interface SearchHit {
  id: string
  source: SearchSource
  title: string
  reference: string
  snippet: string
  score?: number
}

export interface SearchMetrics {
  startedAt: string
  durationMs: number
  localHits: number
  redmineHits: number
  sharepointHits: number
  teamsHits: number
  internalDocsHits: number
}

export interface SearchResponse {
  keyword: string
  summary: string
  reasoning: string[]
  metrics: SearchMetrics
  hits: {
    local: SearchHit[]
    redmine: SearchHit[]
    sharepoint: SearchHit[]
    teams: SearchHit[]
    internalDocs: SearchHit[]
    combined: SearchHit[]
  }
}

export interface SearchService {
  runSearch(payload: SearchPayload, settings: AppSettings): Promise<SearchResponse>
}

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
