/// <reference types="vite-plugin-electron/electron-env" />

import type { AppSettings } from '../shared/settings'
import type { SearchPayload, SearchResponse } from '../shared/contracts'

declare namespace NodeJS {
  interface ProcessEnv {
    APP_ROOT: string
    VITE_PUBLIC: string
  }
}

declare global {
  interface Window {
    app: {
      settings: {
        get: () => Promise<AppSettings>
        set: (payload: AppSettings) => Promise<AppSettings>
      }
      search: (payload: SearchPayload) => Promise<SearchResponse>
    }
  }
}
