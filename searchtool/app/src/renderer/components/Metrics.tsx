import { useEffect, useState } from 'react'
import type { MetricsSummary } from '../../shared/contracts'

const Metrics = () => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMetrics = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await window.app.metrics.get(10)
      setMetrics(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'メトリクスの読み込みに失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    if (!confirm('すべてのメトリクスをクリアしますか？')) {
      return
    }
    try {
      await window.app.metrics.clear()
      await loadMetrics()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'メトリクスのクリアに失敗しました')
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [])

  if (loading) {
    return (
      <div className="metrics-panel">
        <p>メトリクスを読み込み中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="metrics-panel">
        <p className="error">{error}</p>
        <button onClick={loadMetrics}>再読み込み</button>
      </div>
    )
  }

  if (!metrics) {
    return null
  }

  return (
    <div className="metrics-panel">
      <div className="metrics-header">
        <h2>検索統計</h2>
        <div className="metrics-actions">
          <button onClick={loadMetrics}>更新</button>
          {metrics.totalSearches > 0 ? <button onClick={handleClear}>クリア</button> : null}
        </div>
      </div>

      <div className="metrics-summary">
        <div className="metric-card">
          <span className="metric-label">総検索回数</span>
          <strong className="metric-value">{metrics.totalSearches}</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">平均処理時間</span>
          <strong className="metric-value">{metrics.averageDurationMs} ms</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">総Local件数</span>
          <strong className="metric-value">{metrics.totalLocalHits}</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">総Redmine件数</span>
          <strong className="metric-value">{metrics.totalRedmineHits}</strong>
        </div>
      </div>

      {metrics.recentSearches.length > 0 ? (
        <div className="recent-searches">
          <h3>直近の検索</h3>
          <table>
            <thead>
              <tr>
                <th>検索日時</th>
                <th>キーワード</th>
                <th>処理時間</th>
                <th>Local</th>
                <th>Redmine</th>
              </tr>
            </thead>
            <tbody>
              {metrics.recentSearches.map((record, index) => (
                <tr key={index}>
                  <td>{new Date(record.timestamp).toLocaleString('ja-JP')}</td>
                  <td className="keyword-cell">{record.keyword}</td>
                  <td>{record.metrics.durationMs} ms</td>
                  <td>{record.metrics.localHits}</td>
                  <td>{record.metrics.redmineHits}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="placeholder">まだ検索履歴がありません。</p>
      )}
    </div>
  )
}

export default Metrics
