/// <reference types="vite/client" />

import type { AppSettings } from './shared/settings'
import type { SearchPayload, SearchResponse, MetricsSummary } from './shared/contracts'

declare global {
  interface WindowEventMap {
    'screenshot-config': CustomEvent<{
      view?: 'search' | 'settings' | 'metrics'
      keyword?: string
      searchResult?: SearchResponse
      searchTab?: 'summary' | 'combined' | 'local' | 'redmine' | 'sharepoint' | 'teams' | 'internalDocs'
    }>
  }
  interface Window {
    app: {
      settings: {
        get: () => Promise<AppSettings>
        set: (payload: AppSettings) => Promise<AppSettings>
      }
      search: (payload: SearchPayload) => Promise<SearchResponse>
      metrics: {
        get: (limit?: number) => Promise<MetricsSummary>
        clear: () => Promise<void>
      }
    }
  }
}
