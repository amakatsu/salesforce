import { contextBridge, ipcRenderer } from 'electron'
import type { AppSettings } from '../shared/settings'
import type { SearchPayload, SearchResponse, MetricsSummary } from '../shared/contracts'

type SettingsBridge = {
  get: () => Promise<AppSettings>
  set: (payload: AppSettings) => Promise<AppSettings>
}

type MetricsBridge = {
  get: (limit?: number) => Promise<MetricsSummary>
  clear: () => Promise<void>
}

const api = {
  settings: {
    get: (): Promise<AppSettings> => ipcRenderer.invoke('settings:get'),
    set: (payload: AppSettings): Promise<AppSettings> => ipcRenderer.invoke('settings:set', payload),
  } satisfies SettingsBridge,
  search: (payload: SearchPayload): Promise<SearchResponse> => ipcRenderer.invoke('search:run', payload),
  metrics: {
    get: (limit?: number): Promise<MetricsSummary> => ipcRenderer.invoke('metrics:get', limit),
    clear: (): Promise<void> => ipcRenderer.invoke('metrics:clear'),
  } satisfies MetricsBridge,
}

contextBridge.exposeInMainWorld('app', api)
