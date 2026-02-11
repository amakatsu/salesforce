# ポータブル配布 ディレクトリレイアウト設計書

## 概要

SearchTool をインストーラなしで配布する。
USB メモリやファイルサーバーからコピーするだけで動作する状態を目指す。

electron-builder の `portable` ターゲットを使い、
exe と同じディレクトリにデータを配置する。

---

## 1. ビルド設定の変更

### 現状（NSIS インストーラ）

```json5
// electron-builder.json5（現在）
"win": {
  "target": [{ "target": "nsis", "arch": ["x64"] }]
}
```

### 変更後（portable 追加）

```json5
"win": {
  "target": [
    { "target": "nsis", "arch": ["x64"] },
    { "target": "portable", "arch": ["x64"] }
  ]
},
"portable": {
  "artifactName": "${productName}-Portable-${version}.${ext}"
}
```

`npm run build:win` で NSIS と portable の両方が生成される。

---

## 2. ディレクトリレイアウト

```
SearchTool-Portable-1.0.0.exe    ← ポータブル実行ファイル
./data/
  recipes/       # 検索レシピ（保存済み検索パターン）
  cache/         # 検索結果キャッシュ
  logs/          # 実行ログ
  settings.json  # アプリ設定（SettingsStore の出力先）
./profiles/      # Playwright ブラウザプロファイル
```

### 各ディレクトリの役割

| ディレクトリ | 格納データ | 書き込み頻度 |
|-------------|-----------|-------------|
| `data/recipes/` | 検索条件のプリセット（JSON） | ユーザー操作時 |
| `data/cache/` | 直近の検索結果 | 毎回の検索時 |
| `data/logs/` | `app-YYYYMMDD.log`（JSON Lines） | 常時 |
| `data/settings.json` | AppSettings のシリアライズ | 設定変更時 |
| `profiles/` | Chromium / Edge のユーザーデータ | ブラウザ操作時 |

---

## 3. データディレクトリの解決

### ポータブルモードの判定

Electron は `PORTABLE_EXECUTABLE_DIR` 環境変数を自動的にセットする。
この変数が存在すれば portable モードと判定する。

```typescript
// main.ts でのデータディレクトリ解決
const resolveDataDir = (): string => {
  const portableDir = process.env.PORTABLE_EXECUTABLE_DIR
  if (portableDir) {
    // ポータブルモード: exe と同階層の data/
    return path.join(portableDir, 'data')
  }
  // インストーラモード: 従来通り userData
  return app.getPath('userData')
}
```

### SettingsStore への影響

現在 `SettingsStore` は `app.getPath('userData')` を受け取っている。
ポータブルモードでは `resolveDataDir()` を渡すだけで対応できる。

```typescript
// 変更箇所: main.ts の bootstrap()
const dataDir = resolveDataDir()
logger = new Logger(dataDir)            // logs/ を dataDir 配下に
settingsStore = new SettingsStore(dataDir)  // settings.json を dataDir 配下に
```

---

## 4. ブラウザプロファイル管理

### 優先順位

```
1. 既存ブラウザ（channel 指定）  ← 推奨
   - channel: msedge  （社内 PC に入っている可能性が最も高い）
   - channel: chrome
2. Playwright 同梱 Chromium      ← フォールバック
   - profiles/ 配下にダウンロード・配置
```

### 理由

- 社内 PC には Edge がプリインストールされている前提
- 認証済みセッション（SSO / NTLM）を再利用するため、既存ブラウザを優先する
- Playwright 同梱 Chromium は認証が必要なサイトで不便だが、Edge / Chrome がない環境のフォールバックとして必要

### プロファイルディレクトリの解決

```typescript
const resolveProfileDir = (): string => {
  const portableDir = process.env.PORTABLE_EXECUTABLE_DIR
  if (portableDir) {
    return path.join(portableDir, 'profiles')
  }
  // インストーラモード: デフォルトの Playwright キャッシュを使う
  return ''  // 空文字 = playwright-mcp のデフォルト位置
}
```

settings.ts の `browser.userDataDir` にこの値をデフォルト設定する。
ユーザーが設定画面で明示的に変更した場合はそちらを優先。

### playwright-mcp への渡し方

現在のコードで既に `PLAYWRIGHT_MCP_PROFILE_DIR` 環境変数を渡している。

```typescript
// redmine-ui.server.ts（既存コード）
const createTransport = (userDataDir?: string) =>
  new StdioClientTransport({
    command: process.execPath,
    args: [PLAYWRIGHT_MCP_ENTRY],
    env: {
      ...process.env,
      PLAYWRIGHT_MCP_PROFILE_DIR: userDataDir ?? '',
    },
    stderr: 'pipe',
  })
```

変更不要。`userDataDir` に `resolveProfileDir()` の値が流れるだけ。

---

## 5. データのライフサイクル

| データ | 作成 | 更新 | 削除 |
|--------|------|------|------|
| `data/settings.json` | 初回起動時 | 設定変更時 | しない |
| `data/recipes/*.json` | ユーザーが保存時 | ユーザーが編集時 | ユーザーが明示的に削除 |
| `data/cache/` | 検索実行時 | 同一キーワード再検索時に上書き | 容量上限到達時に LRU 削除 |
| `data/logs/app-*.log` | 毎日初回ログ時 | 追記 | 7 日超のファイルを起動時に削除 |
| `profiles/` | 初回ブラウザ起動時 | ブラウザ操作のたび | しない（手動削除のみ） |

### キャッシュの容量管理

```typescript
const CACHE_MAX_ENTRIES = 100   // 直近 100 検索分を保持
const CACHE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000  // 7 日
```

### ログのローテーション

現在の Logger は日付ごとにファイルを分けている（`app-YYYYMMDD.log`）。
ポータブルモードでは起動時に 7 日超のログファイルを削除する。

```typescript
// Logger に追加するメソッド
async pruneOldLogs(maxAgeDays: number = 7): Promise<void> {
  const cutoff = Date.now() - maxAgeDays * 24 * 60 * 60 * 1000
  const files = await fs.readdir(this.logDir)
  for (const file of files) {
    if (!file.startsWith('app-') || !file.endsWith('.log')) continue
    const stat = await fs.stat(path.join(this.logDir, file))
    if (stat.mtimeMs < cutoff) {
      await fs.unlink(path.join(this.logDir, file))
    }
  }
}
```

---

## 6. Node.js 要件と Electron バージョンの整合性

### 制約

| コンポーネント | 要件 |
|---------------|------|
| Mastra v1 (`@mastra/core ^0.23`) | Node.js 22.13+ |
| Electron 30 (`electron ^30.0.1`) | 内蔵 Node.js 20.x |

### 問題

Electron 30 は Node.js 20.x を内蔵しており、Mastra v1 の要件（22.13+）を満たさない。

### 対応方針

| 選択肢 | メリット | デメリット |
|--------|---------|-----------|
| **A. Electron 33+ に上げる** | Node 22.x 内蔵。Mastra 要件を満たす | 破壊的変更の確認が必要 |
| **B. Mastra を別プロセスで動かす** | Electron バージョンに依存しない | プロセス間通信の設計が必要 |
| **C. Mastra のバージョンを固定** | 現状維持 | 将来の機能追加が制限される |

**推奨: A（Electron 33+ に更新）**

Electron 33 は Node.js 22.x を内蔵しており、Mastra の要件をネイティブに満たす。
`electron ^30.0.1` → `electron ^33.0.0` への更新を計画すること。

更新時の確認事項:
- Electron 33 の Breaking Changes を確認
- `vite-plugin-electron` の互換性を確認
- `electron-builder` のバージョンが Electron 33 に対応しているか確認

---

## 7. まとめ

| 項目 | 内容 |
|------|------|
| ビルドターゲット | `portable` を `electron-builder.json5` に追加 |
| データ配置 | `PORTABLE_EXECUTABLE_DIR/data/` |
| プロファイル配置 | `PORTABLE_EXECUTABLE_DIR/profiles/` |
| ブラウザ優先順位 | msedge → chrome → 同梱 Chromium |
| ログローテーション | 7 日超を起動時に削除 |
| Electron 更新 | 33+ 推奨（Node 22.x 内蔵） |

### 変更対象ファイル

| ファイル | 変更内容 |
|----------|---------|
| `electron-builder.json5` | `portable` ターゲット追加 |
| `main.ts` | `resolveDataDir()` / `resolveProfileDir()` 追加 |
| `services/logger.ts` | `pruneOldLogs()` 追加 |
| `package.json` | Electron バージョン更新（計画） |
