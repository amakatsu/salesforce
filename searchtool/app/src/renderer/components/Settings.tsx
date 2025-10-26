import { AppSettings } from '../../shared/settings'

type Props = {
  value: AppSettings
  saving: boolean
  onChange: (next: AppSettings) => void
  onSave: () => void
}

const normaliseList = (input: string) =>
  input
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean)

const Settings = ({ value, saving, onChange, onSave }: Props) => {
  const update = (partial: Partial<AppSettings>) => {
    onChange({
      ...value,
      ...partial,
    })
  }

  return (
    <div className="settings-panel">
      <div className="field-group">
        <label>デフォルトキーワード</label>
        <input
          value={value.keyword}
          placeholder="例: 監査"
          onChange={(event) => update({ keyword: event.target.value })}
        />
      </div>

      <div className="field-group">
        <label>ローカル検索ルート (複数行で指定)</label>
        <textarea
          rows={3}
          value={value.local.root.join('\n')}
          onChange={(event) => update({ local: { ...value.local, root: normaliseList(event.target.value) } })}
          placeholder={'C:\\docs\nD:\\knowledge'}
        />
      </div>

      <div className="field-group">
        <label>除外グロブ</label>
        <textarea
          rows={2}
          value={value.excludeGlobs.join('\n')}
          onChange={(event) => update({ excludeGlobs: normaliseList(event.target.value) })}
          placeholder={'.git\nnode_modules'}
        />
      </div>

      <div className="field-group">
        <label>ブラウザ userDataDir</label>
        <input
          value={value.browser.userDataDir}
          onChange={(event) => update({ browser: { ...value.browser, userDataDir: event.target.value } })}
          placeholder="C:\\Users\\me\\AppData\\Local\\Microsoft\\Edge\\User Data"
        />
      </div>

      <h3 style={{ margin: '24px 0 12px 0', fontSize: '1.2rem' }}>Web検索ソース（複数指定可能）</h3>

      <div className="field-group">
        <label>Redmine URLs (複数行で指定)</label>
        <textarea
          rows={3}
          value={value.redmine.urls.join('\n')}
          onChange={(event) => update({ redmine: { urls: normaliseList(event.target.value) } })}
          placeholder={'https://redmine1.example.com\nhttps://redmine2.example.com'}
        />
      </div>

      <div className="field-group">
        <label>SharePoint URLs (複数行で指定)</label>
        <textarea
          rows={3}
          value={value.sharepoint.urls.join('\n')}
          onChange={(event) => update({ sharepoint: { urls: normaliseList(event.target.value) } })}
          placeholder={'https://company1.sharepoint.com\nhttps://company2.sharepoint.com'}
        />
      </div>

      <div className="field-group">
        <label>Teams URLs (複数行で指定)</label>
        <textarea
          rows={3}
          value={value.teams.urls.join('\n')}
          onChange={(event) => update({ teams: { urls: normaliseList(event.target.value) } })}
          placeholder={'https://teams.microsoft.com/_#/discover\nhttps://teams.microsoft.com'}
        />
      </div>

      <div className="field-group">
        <label>社内ドキュメントサイト URL</label>
        <input
          value={value.internalDocs.baseUrl}
          onChange={(event) => update({ internalDocs: { ...value.internalDocs, baseUrl: event.target.value } })}
          placeholder="https://docs.company.com"
        />
      </div>

      <div className="limits-grid">
        <div className="field-group">
          <label>Local max results</label>
          <input
            type="number"
            min={1}
            max={2000}
            value={value.limits.localMaxResults}
            onChange={(event) => update({ limits: { ...value.limits, localMaxResults: Number(event.target.value) } })}
          />
        </div>
        <div className="field-group">
          <label>Redmine max results</label>
          <input
            type="number"
            min={1}
            max={200}
            value={value.limits.redmineMaxResults}
            onChange={(event) => update({ limits: { ...value.limits, redmineMaxResults: Number(event.target.value) } })}
          />
        </div>
        <div className="field-group">
          <label>Timeout (sec)</label>
          <input
            type="number"
            min={5}
            max={300}
            value={value.limits.timeoutSeconds}
            onChange={(event) => update({ limits: { ...value.limits, timeoutSeconds: Number(event.target.value) } })}
          />
        </div>
        <div className="field-group">
          <label>Scroll steps</label>
          <input
            type="number"
            min={1}
            max={50}
            value={value.limits.scrollSteps}
            onChange={(event) => update({ limits: { ...value.limits, scrollSteps: Number(event.target.value) } })}
          />
        </div>
      </div>

      <div className="actions">
        <button onClick={onSave} disabled={saving}>
          {saving ? '保存中...' : '設定を保存'}
        </button>
      </div>
    </div>
  )
}

export default Settings
