import { useEffect, useMemo, useState, type KeyboardEvent } from 'react'
import type { SearchResponse, SearchSource } from '../../shared/contracts'

const SOURCE_OPTIONS: Array<{ id: SearchSource; label: string; hint: string }> = [
  { id: 'local', label: 'ローカル', hint: 'プロジェクト内のファイル検索' },
  { id: 'redmine', label: 'Redmine', hint: 'チケット/課題' },
  { id: 'sharepoint', label: 'SharePoint', hint: '社内ポータル' },
  { id: 'teams', label: 'Teams', hint: 'チャット履歴' },
  { id: 'internalDocs', label: '社内Docs', hint: 'Wiki/ガイドライン' },
]

const DEFAULT_MAX_HITS = 50
const MIN_MAX_HITS = 5
const MAX_MAX_HITS = 200

export type ResultTab = 'combined' | 'local' | 'redmine' | 'sharepoint' | 'teams' | 'internalDocs'

const tabConfig: Record<ResultTab, string> = {
  combined: '統合結果',
  local: 'Local',
  redmine: 'Redmine',
  sharepoint: 'SharePoint',
  teams: 'Teams',
  internalDocs: '社内Docs',
}

type SearchOptions = {
  sources: SearchSource[]
  maxCombinedHits: number
}

type Props = {
  keyword: string
  onKeywordChange: (value: string) => void
  onSearch: (options: SearchOptions) => void
  searching: boolean
  result: SearchResponse | null
  error?: string | null
  initialTab?: ResultTab
}

const SearchPane = ({ keyword, onKeywordChange, onSearch, searching, result, error, initialTab }: Props) => {
  const [selectedSources, setSelectedSources] = useState<SearchSource[]>(() => SOURCE_OPTIONS.map((option) => option.id))
  const [maxHits, setMaxHits] = useState<number>(DEFAULT_MAX_HITS)
  const [activeTab, setActiveTab] = useState<ResultTab>(initialTab ?? 'combined')

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab)
    }
  }, [initialTab])

  const availableTabs = useMemo<ResultTab[]>(() => {
    const tabs: ResultTab[] = ['combined']
    SOURCE_OPTIONS.forEach(({ id }) => {
      if (selectedSources.includes(id)) {
        tabs.push(id as ResultTab)
      }
    })
    return tabs
  }, [selectedSources])

  useEffect(() => {
    if (!availableTabs.includes(activeTab)) {
      setActiveTab('combined')
    }
  }, [availableTabs, activeTab])

  const summaryMetrics = useMemo(() => {
    if (!result) {
      return null
    }
    return [
      { label: '処理時間', value: `${result.metrics.durationMs} ms` },
      { label: 'Local', value: result.metrics.localHits },
      { label: 'Redmine', value: result.metrics.redmineHits },
      { label: 'SharePoint', value: result.metrics.sharepointHits },
      { label: 'Teams', value: result.metrics.teamsHits },
      { label: '社内Docs', value: result.metrics.internalDocsHits },
      { label: '統合', value: result.hits.combined.length },
    ]
  }, [result])

  const toggleSource = (source: SearchSource) => {
    setSelectedSources((prev) => {
      if (prev.includes(source)) {
        if (prev.length === 1) {
          return prev
        }
        return prev.filter((item) => item !== source)
      }
      return [...prev, source]
    })
  }

  const handleMaxHitsChange = (value: string) => {
    const parsed = Number(value)
    if (!Number.isFinite(parsed)) {
      setMaxHits(DEFAULT_MAX_HITS)
      return
    }
    const clamped = Math.min(MAX_MAX_HITS, Math.max(MIN_MAX_HITS, Math.floor(parsed)))
    setMaxHits(clamped)
  }

  const handleSearch = () => {
    if (!keyword.trim() || selectedSources.length === 0) {
      return
    }
    onSearch({ sources: selectedSources, maxCombinedHits: maxHits })
  }

  const renderHits = (tab: ResultTab) => {
    if (!result) {
      return <p className="placeholder">まだ結果がありません。</p>
    }

    let hits
    switch (tab) {
      case 'local':
        hits = result.hits.local
        break
      case 'redmine':
        hits = result.hits.redmine
        break
      case 'sharepoint':
        hits = result.hits.sharepoint
        break
      case 'teams':
        hits = result.hits.teams
        break
      case 'internalDocs':
        hits = result.hits.internalDocs
        break
      case 'combined':
      default:
        hits = result.hits.combined
        break
    }

    if (!hits.length) {
      return <p className="placeholder">ヒットはありませんでした。</p>
    }

    return (
      <div className="hits-table">
        {hits.map((hit) => (
          <article key={hit.id} className="hit-row">
            <header>
              <strong>{hit.title || hit.reference}</strong>
              <div className="hit-meta">
                <span className={`source-badge ${hit.source}`}>{hit.source}</span>
                <span className="hit-reference">{hit.reference}</span>
              </div>
            </header>
            <p>{hit.snippet}</p>
          </article>
        ))}
      </div>
    )
  }

  const renderSummary = () => {
    if (!result) {
      return <p className="placeholder">検索を実行するとMastraの要約が表示されます。</p>
    }
    return (
      <div className="summary-card">
        <p className="summary-text">{result.summary}</p>
        {result.reasoning.length > 0 ? (
          <ul>
            {result.reasoning.map((line, index) => (
              <li key={`${index}-${line}`}>{line}</li>
            ))}
          </ul>
        ) : null}
      </div>
    )
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && keyword.trim() && !searching) {
      handleSearch()
    }
  }

  return (
    <section className="search-pane">
      <div className="search-controls">
        <div className="search-bar">
          <input
            value={keyword}
            onChange={(event) => onKeywordChange(event.target.value)}
            placeholder="検索キーワード"
            disabled={searching}
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleSearch} disabled={searching || !keyword.trim() || selectedSources.length === 0}>
            {searching ? (
              <>
                <span className="spinner"></span>
                検索中...
              </>
            ) : (
              '検索'
            )}
          </button>
        </div>

        <div className="search-options">
          <div className="source-picker">
            <span className="picker-label">検索対象</span>
            <div className="source-pills">
              {SOURCE_OPTIONS.map((option) => {
                const active = selectedSources.includes(option.id)
                return (
                  <button
                    key={option.id}
                    type="button"
                    className={`source-pill ${active ? 'active' : ''}`}
                    onClick={() => toggleSource(option.id)}
                    disabled={searching}
                  >
                    <span>{option.label}</span>
                    <small>{option.hint}</small>
                  </button>
                )
              })}
            </div>
          </div>
          <div className="hit-limit">
            <label htmlFor="maxHits">取り込む最大件数</label>
            <input
              id="maxHits"
              type="number"
              min={MIN_MAX_HITS}
              max={MAX_MAX_HITS}
              value={maxHits}
              onChange={(event) => handleMaxHitsChange(event.target.value)}
              disabled={searching}
            />
          </div>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}

      {summaryMetrics ? (
        <div className="metrics">
          {summaryMetrics.map((metric) => (
            <div key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </div>
          ))}
        </div>
      ) : null}

      <div className="search-output-grid">
        <div className="summary-column">
          <div className="summary-header">
            <h3>Mastra要約</h3>
            <p>検索完了後にAI要約を表示します</p>
          </div>
          {renderSummary()}
        </div>
        <div className="results-column">
          <div className="results-header">
            <div>
              <h3>検索結果</h3>
              <p>
                有効な検索対象: {selectedSources.map((source) => tabConfig[source as ResultTab] ?? source).join(', ')} ／ 上限 {maxHits} 件
              </p>
            </div>
          </div>
          <div className="tabs">
            {availableTabs.map((tab) => (
              <button
                key={tab}
                className={tab === activeTab ? 'active' : ''}
                onClick={() => setActiveTab(tab)}
                disabled={searching}
              >
                {tabConfig[tab]}
              </button>
            ))}
          </div>
          <div className="tab-panel">
            {searching && !result ? (
              <div className="loading-state">
                <span className="spinner large"></span>
                <p>検索を実行中です...</p>
              </div>
            ) : (
              renderHits(activeTab)
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default SearchPane
