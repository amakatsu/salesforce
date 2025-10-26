import { useEffect, useState } from 'react'
import Settings from './components/Settings'
import SearchPane from './components/SearchPane'
import Metrics from './components/Metrics'
import type { AppSettings } from '../shared/settings'
import type { SearchResponse } from '../shared/contracts'
import './App.css'

type View = 'search' | 'settings' | 'metrics'

const App = () => {
  const [view, setView] = useState<View>('search')
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [saving, setSaving] = useState(false)
  const [searching, setSearching] = useState(false)
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [searchError, setSearchError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    window.app.settings
      .get()
      .then((loaded) => {
        if (!mounted) return
        setSettings(loaded)
      })
      .catch((err) => {
        if (!mounted) return
        setError(err instanceof Error ? err.message : '設定の読み込みに失敗しました')
      })
    return () => {
      mounted = false
    }
  }, [])

  const updateSettings = (next: AppSettings) => {
    setSettings(next)
  }

  const handleSave = async () => {
    if (!settings) return
    setSaving(true)
    setError(null)
    try {
      const saved = await window.app.settings.set(settings)
      setSettings(saved)
    } catch (err) {
      setError(err instanceof Error ? err.message : '設定の保存に失敗しました')
    } finally {
      setSaving(false)
    }
  }

  const handleSearch = async () => {
    if (!settings?.keyword.trim()) {
      setSearchError('検索キーワードを入力してください')
      return
    }
    setSearching(true)
    setSearchError(null)
    try {
      const response = await window.app.search({ keyword: settings.keyword })
      setSearchResult(response)
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : '検索に失敗しました')
    } finally {
      setSearching(false)
    }
  }

  if (!settings) {
    return (
      <div className="app-shell">
        <p>設定を読み込み中...</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header>
        <div>
          <h1>Search Agent</h1>
          <p>ローカルとRedmineを一括サーチ</p>
        </div>
        <nav>
          <button className={view === 'search' ? 'active' : ''} onClick={() => setView('search')}>
            検索
          </button>
          <button className={view === 'metrics' ? 'active' : ''} onClick={() => setView('metrics')}>
            統計
          </button>
          <button className={view === 'settings' ? 'active' : ''} onClick={() => setView('settings')}>
            設定
          </button>
        </nav>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <main>
        {view === 'search' ? (
          <SearchPane
            keyword={settings.keyword}
            onKeywordChange={(keyword) => updateSettings({ ...settings, keyword })}
            onSearch={handleSearch}
            searching={searching}
            result={searchResult}
            error={searchError}
          />
        ) : view === 'metrics' ? (
          <Metrics />
        ) : (
          <Settings value={settings} onChange={updateSettings} saving={saving} onSave={handleSave} />
        )}
      </main>
    </div>
  )
}

export default App
