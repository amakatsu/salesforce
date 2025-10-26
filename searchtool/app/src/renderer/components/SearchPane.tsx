import { useMemo, useState } from 'react'
import type { SearchResponse } from '../../shared/contracts'

type Props = {
  keyword: string
  onKeywordChange: (value: string) => void
  onSearch: () => void
  searching: boolean
  result: SearchResponse | null
  error?: string | null
}

type Tab = 'summary' | 'combined' | 'local' | 'redmine'

const tabConfig: Record<Tab, string> = {
  summary: 'Mastra要約',
  combined: 'すべて',
  local: 'Local',
  redmine: 'Web',
}

const SearchPane = ({ keyword, onKeywordChange, onSearch, searching, result, error }: Props) => {
  const [activeTab, setActiveTab] = useState<Tab>('summary')

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
      { label: '社内ドキュメント', value: result.metrics.internalDocsHits },
      { label: '合計', value: result.hits.combined.length },
    ]
  }, [result])

  const renderHits = (tab: Tab) => {
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
      default:
        hits = result.hits.combined
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

  const activeContent = () => {
    switch (activeTab) {
      case 'summary':
        return renderSummary()
      case 'local':
        return renderHits('local')
      case 'redmine':
        return renderHits('redmine')
      case 'combined':
      default:
        return renderHits('combined')
    }
  }

  return (
    <section className="search-pane">
      <div className="search-bar">
        <input
          value={keyword}
          onChange={(event) => onKeywordChange(event.target.value)}
          placeholder="検索キーワード"
          disabled={searching}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && keyword.trim() && !searching) {
              onSearch()
            }
          }}
        />
        <button onClick={onSearch} disabled={searching || !keyword.trim()}>
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

      {error ? <p className="error">{error}</p> : null}

      {searching && !result ? (
        <div className="loading-state">
          <span className="spinner large"></span>
          <p>検索を実行中です...</p>
        </div>
      ) : null}

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

      <div className="tabs">
        {(Object.keys(tabConfig) as Tab[]).map((tab) => (
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

      <div className="tab-panel">{activeContent()}</div>
    </section>
  )
}

export default SearchPane
