# SearchTool — Tool インターフェース定義

> **Version**: 2.0.0-draft
> **対象**: `app/src/main/mastra/tools/` 配下の Tool 群

## 1. 設計方針

### v1 の課題

v1 では各ソース（SharePoint, Redmine 等）ごとにモノリシックな Tool が存在し、
「ブラウザ操作 → 固定セレクタでDOM解析 → 結果抽出」を 1 つの execute 内で一気通貫していた。
この構造は以下の問題を抱える:

- **固定セレクタ依存**: サイトのDOM構造が変わると即座に壊れる
- 抽出ロジックの変更がブラウザ操作コードに波及する
- 抽出失敗時のリトライが Tool 全体の再実行になる
- playwright-mcp のアクセシビリティスナップショットを活用できない

### 現行の方針

**固定セレクタを排除し、スナップショットベースの適応的設計にする。**

核心: **「壊れたら修復する」のではなく「毎回その場で判断する」。**
Agent（LLM）がアクセシビリティスナップショットを読み取り、
ページ構造に適応的にデータを抽出する。固定パーサーは使わない。

| レイヤー | 責務 | 状態 |
|----------|------|------|
| NavigationTool | アクセシビリティベースのブラウザ操作 | ステートフル（ブラウザ） |
| SearchTool | 検索オーケストレーション（遷移→スナップショット取得） | ステートレス |
| ExtractTool | スナップショットからの構造化データ抽出（Agent判断ベース） | 純粋関数 |
| RetryTool | 判断失敗時の再スナップショット取得・リトライ | ステートフル（ブラウザ） |

### 設計原則

1. **固定セレクタ禁止** — CSS セレクタや XPath をハードコードしない
2. **スナップショット駆動** — `browser_snapshot` で取得したアクセシビリティツリーが全ての判断根拠
3. **アクセシビリティベースLocator** — `getByRole()`, `getByLabel()`, `getByText()` 相当の ref を使用
4. **Agent が解釈者** — ページ構造の理解はコードではなく Agent（LLM）が担う

### 制約

- Mastra `createTool` API に準拠
- スキーマは Zod で定義（実装にそのまま使える精度）
- 最小プロダクト: SharePoint 検索結果トップ N（タイトル / URL / スニペット）

---

## 2. Tool 一覧と責務

```
Agent（スナップショットを読み取り、適応的に判断する主体）
  │
  ├─ NavigationTool              ブラウザ操作（アクセシビリティベース）
  │
  ├─ SharePointSearchTool        SharePoint検索ページへ遷移→スナップショット返却
  │    └─ NavigationTool          遷移・入力操作
  │
  ├─ SharePointExtractTool       スナップショットからAgent判断で結果を構造化
  │
  ├─ TeamsMessageSearchTool      Teams検索→スナップショット返却
  │    └─ NavigationTool          遷移・検索操作
  │
  ├─ RedmineSearchTool           Redmine検索→スナップショット返却
  │    └─ NavigationTool          遷移・検索操作
  │
  ├─ LocalSearchTool             ローカルファイル検索（ripgrep、ブラウザ不要）
  │
  └─ RetryTool                   判断失敗時の再スナップショット取得
       └─ NavigationTool          再読み込み・スクロール・再スナップショット
```

**データフローの基本パターン（Webソース）**:
```
SearchTool（遷移→スナップショット取得）
  → Agent がスナップショットを読み取り
  → ExtractTool or Agent 自身が構造化データに変換
  → 失敗時: RetryTool で再スナップショット → 再判断
```

| Tool | いつ呼ばれるか |
|------|----------------|
| `NavigationTool` | ブラウザ操作が必要なとき（アクセシビリティref指定） |
| `SharePointSearchTool` | SharePoint検索ページへの遷移とスナップショット取得 |
| `SharePointExtractTool` | Agent がスナップショットから検索結果を構造化するとき |
| `TeamsMessageSearchTool` | Teams メッセージ検索とスナップショット取得 |
| `RedmineSearchTool` | Redmine チケット検索とスナップショット取得 |
| `LocalSearchTool` | ローカルファイル全文検索（ripgrep） |
| `RetryTool` | Agent の判断が失敗し、再スナップショットが必要なとき |

---

## 3. 各 Tool のインターフェース定義

### 3a. SharePointSearchTool

SharePoint 検索ページへ遷移し、キーワードを入力し、
結果ページのアクセシビリティスナップショットを返すオーケストレーター。
**結果の解釈は Agent が行う**（固定パーサーを持たない）。

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ── 入力 ──
const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード'),
  maxResults: z.number().int().min(1).max(100).default(20)
    .describe('最大取得件数（Agent が抽出時に参照する上限）'),
  siteScope: z.string().url().optional()
    .describe('検索対象を絞るSharePointサイトURL（省略時は全サイト）'),
})

// ── 出力 ──
const outputSchema = z.object({
  pageSnapshot: z.string().describe(
    '検索結果ページのアクセシビリティスナップショット（Markdown形式）。' +
    'Agent がこのスナップショットを読み取り、検索結果を抽出する'
  ),
  searchUrl: z.string().url().describe('実際に検索したURL'),
  currentUrl: z.string().url().describe('スナップショット取得時のURL'),
})

// ── エラー時 ──
// execute が throw した場合、Mastra が自動的に isError: true を返す。
// エラーメッセージは Error.message に記載。
```

**呼び出しタイミング**: Agent が `sharepoint` ソースを有効にして検索を実行するとき。

**execute 内部フロー**（固定セレクタ不使用）:
1. `NavigationTool({ action: "navigate", target: searchUrl })` で遷移
2. `NavigationTool({ action: "snapshot" })` でスナップショット取得
3. スナップショットに検索ボックスがあれば、Agent が ref を特定して入力
4. 結果読み込み待ち後、最終スナップショットを返却

---

### 3b. SharePointExtractTool

アクセシビリティスナップショットを受け取り、Agent の判断で
検索結果を構造化データに変換する。**ブラウザ操作は一切行わない（純粋関数を維持）。**

固定パーサーではなく、Agent（LLM）がスナップショットのテキスト構造を読み取り、
検索結果に該当する要素を適応的に特定する。

```typescript
// ── 共通の検索結果スキーマ ──
const searchHitSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  snippet: z.string(),
  lastModified: z.string().datetime().optional(),
})

export type SearchHit = z.infer<typeof searchHitSchema>

// ── 入力 ──
const inputSchema = z.object({
  pageSnapshot: z.string().min(1)
    .describe('browser_snapshot で取得したMarkdown形式のアクセシビリティスナップショット'),
  sourceType: z.enum(['sharepoint', 'teams', 'redmine', 'generic']).default('sharepoint')
    .describe('スナップショットの出典。Agent の抽出ヒントとして使用'),
  maxResults: z.number().int().min(1).max(100).default(20)
    .describe('抽出する最大件数'),
})

// ── 出力 ──
const outputSchema = z.object({
  results: z.array(searchHitSchema),
  confidence: z.enum(['high', 'medium', 'low'])
    .describe('Agent による抽出の確信度'),
  itemsFound: z.number().int()
    .describe('スナップショット内で検出した候補要素数'),
  interpretation: z.string().optional()
    .describe('Agent がスナップショットをどう解釈したかの説明（デバッグ用）'),
})
```

**呼び出しタイミング**: SearchTool がスナップショットを返した後、Agent が構造化データを得たいとき。

**Agent 判断のフロー**:
1. スナップショットのテキストからリンク付きの繰り返し要素を検出
2. 各要素から title（見出し or リンクテキスト）、url（href）、snippet（本文抜粋）を抽出
3. ページ構造が未知でも、アクセシビリティツリーの階層構造から適応的に判断

**confidence の判定基準**:
- `high`: 候補要素から title + url を正常に抽出でき、パターンが明確
- `medium`: 一部の候補で url または snippet が欠損、または構造が曖昧
- `low`: 候補が 0 件、またはスナップショットが検索結果ページに見えない

---

### 3c. NavigationTool

playwright-mcp を通じてブラウザを操作する。
1 つの action を実行し、結果を返す。

**アクセシビリティベースLocator を使用する。CSS セレクタは使わない。**
要素の特定は `browser_snapshot` が返す ref 値、
または `getByRole()` / `getByLabel()` / `getByText()` 相当のアクセシブルな説明で行う。

```typescript
// ── 入力 ──
const actionSchema = z.enum([
  'navigate',   // URLへ遷移
  'click',      // 要素をクリック（アクセシビリティref指定）
  'type',       // テキストを入力（アクセシビリティref指定）
  'snapshot',   // 現在のページのアクセシビリティスナップショットを取得
  'wait',       // 指定秒数またはテキスト出現を待機
])

const inputSchema = z.object({
  action: actionSchema,
  ref: z.string().describe(
    'browser_snapshot が返すアクセシビリティツリーの要素ref値。' +
    'navigate: 不要（空文字可）, snapshot: 不要（空文字可）, ' +
    'click/type: スナップショットで確認した要素のref, ' +
    'wait: 不要（空文字可）'
  ),
  target: z.string().describe(
    'navigate: 遷移先URL, ' +
    'click/type: 要素のアクセシブルな説明（例: "検索ボックス", "送信ボタン"）, ' +
    'wait: 待機対象テキスト, snapshot: 不要（空文字可）'
  ),
  value: z.string().optional().describe(
    'type: 入力テキスト, wait: タイムアウト秒数（文字列）, 他: 不要'
  ),
})

// ── 出力 ──
const outputSchema = z.object({
  success: z.boolean(),
  currentUrl: z.string().url().describe('操作後の現在のURL'),
  pageSnapshot: z.string().optional()
    .describe('action が snapshot の場合のみ。Markdown形式のアクセシビリティスナップショット'),
  error: z.string().optional()
    .describe('失敗時のエラーメッセージ'),
})
```

**呼び出しタイミング**: ブラウザ操作が必要なあらゆる場面。

**action ごとの振る舞い**:

| action | ref | target | value | 動作 |
|--------|-----|--------|-------|------|
| `navigate` | （空文字） | URL | — | そのURLへ遷移 |
| `click` | スナップショットのref値 | アクセシブルな説明 | — | 要素をクリック |
| `type` | スナップショットのref値 | アクセシブルな説明 | 入力文字列 | 要素にテキスト入力 |
| `snapshot` | （空文字） | （空文字） | — | 現在ページのスナップショットを返す |
| `wait` | （空文字） | 待機テキスト | タイムアウト秒 | テキスト出現を待機 |

**要素特定の優先順位**（CSSセレクタ禁止）:
1. `ref` — スナップショットで取得した一意の参照値（最優先）
2. `target` — role/label/text によるアクセシブルな説明（refが不明な場合のフォールバック）

---

### 3d. RetryTool

> **旧名: RepairTool** — 設計思想を変更。
> 「壊れたセレクタを修復する」のではなく、
> 「Agent の判断が失敗した場合に新しいスナップショットを取得してリトライする」ツール。

Agent がスナップショットを解釈できなかった場合に、
ページ状態を変更（リロード・スクロール・待機）してから
新しいスナップショットを返す。Agent はこの新スナップショットで再判断する。

```typescript
// ── 入力 ──
const inputSchema = z.object({
  reason: z.string().describe('リトライの理由（例: "検索結果が読み込まれていない"）'),
  strategy: z.enum(['reload', 'wait', 'scroll', 'snapshot_only']).default('wait')
    .describe(
      'reload: ページを再読み込み, ' +
      'wait: 追加の読み込み待機, ' +
      'scroll: ページをスクロールして追加コンテンツを表示, ' +
      'snapshot_only: 何もせず現在のスナップショットを再取得'
    ),
  waitSeconds: z.number().int().min(1).max(30).default(3)
    .describe('wait/reload 後のスナップショット取得までの待機秒数'),
})

// ── 出力 ──
const outputSchema = z.object({
  pageSnapshot: z.string().describe('新しいアクセシビリティスナップショット'),
  currentUrl: z.string().url().describe('現在のURL'),
  strategyUsed: z.string().describe('実行した戦略'),
})
```

**呼び出しタイミング**: Agent が ExtractTool で `confidence: low` を得た場合、
またはスナップショットが検索結果を含んでいないと判断した場合。

**リトライ戦略**:

| strategy | 動作 | 想定ケース |
|----------|------|-----------|
| `reload` | ページ再読み込み → 待機 → スナップショット | 認証リダイレクト後 |
| `wait` | 追加待機 → スナップショット | JS の遅延レンダリング |
| `scroll` | ページ末尾までスクロール → スナップショット | 遅延読み込みコンテンツ |
| `snapshot_only` | 即座にスナップショット再取得 | 前回のスナップショットが不完全 |

**設計上の注意**:
- RetryTool は結果の解釈を行わない。新しいスナップショットを返すのみ
- 解釈は常に Agent が行う（「毎回その場で判断」の原則）
- Agent は最大 2〜3 回のリトライ後、諦めてユーザーに報告すべき

---

### 3e. TeamsMessageSearchTool

Teams Web UI に遷移し、キーワードで検索を実行し、
結果ページのアクセシビリティスナップショットを返す。
**結果の解釈は Agent が行う**（固定パーサーを持たない）。

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ── Teams メッセージ結果スキーマ（Agent が ExtractTool で使用） ──
const teamsMessageHitSchema = z.object({
  sender: z.string().describe('送信者の表示名'),
  message: z.string().describe('メッセージ本文（抜粋）'),
  channel: z.string().optional().describe('チャンネル名（チャンネルメッセージの場合）'),
  timestamp: z.string().describe('送信日時（ISO 8601 または表示テキスト）'),
  url: z.string().url().optional().describe('メッセージへの直リンク（取得できた場合）'),
})

export type TeamsMessageHit = z.infer<typeof teamsMessageHitSchema>

// ── 入力 ──
const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード'),
  scope: z.enum(['chat', 'channel', 'all']).default('all')
    .describe('検索スコープ。chat: 1対1/グループチャット, channel: チャンネル, all: 両方'),
  maxResults: z.number().int().min(1).max(50).default(20)
    .describe('最大取得件数（Agent が抽出時に参照する上限）'),
})

// ── 出力 ──
const outputSchema = z.object({
  pageSnapshot: z.string().describe(
    '検索結果ページのアクセシビリティスナップショット。' +
    'Agent がこのスナップショットを読み取り、メッセージを抽出する'
  ),
  searchUrl: z.string().url().describe('検索に使用したTeams URL'),
  currentUrl: z.string().url().describe('スナップショット取得時のURL'),
  scope: z.enum(['chat', 'channel', 'all']).describe('実際に検索したスコープ'),
})

// ── エラー時 ──
// execute が throw した場合、Mastra が自動的に isError: true を返す。
// 認証エラー（ログインが必要な場合）は Error.message に明記。
```

**呼び出しタイミング**: Agent が `teams` ソースを有効にして検索を実行するとき。

**scope ごとの振る舞い**:

| scope | 対象 | Teams UI 操作（アクセシビリティベース） |
|-------|------|----------------------------------------|
| `chat` | 1対1チャット・グループチャット | スナップショットから Messages タブのフィルタref を特定して操作 |
| `channel` | チーム内チャンネルの投稿 | スナップショットからフィルタref を特定して操作 |
| `all` | 両方 | フィルタなし（デフォルト） |

---

### 3f. RedmineSearchTool

Redmine の検索ページに遷移し、キーワードで検索を実行し、
結果ページのアクセシビリティスナップショットを返す。
**結果の解釈は Agent が行う**（固定パーサーを持たない）。

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ── Redmine チケット結果スキーマ（Agent が ExtractTool で使用） ──
const redmineTicketHitSchema = z.object({
  ticketId: z.string().describe('チケット番号（例: "12345"）'),
  title: z.string().describe('チケットのタイトル'),
  status: z.string().describe('ステータス（例: "進行中", "新規", "終了"）'),
  assignee: z.string().optional().describe('担当者名（未割当の場合は省略）'),
  url: z.string().url().describe('チケットへのURL'),
})

export type RedmineTicketHit = z.infer<typeof redmineTicketHitSchema>

// ── 入力 ──
const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード'),
  project: z.string().optional()
    .describe('プロジェクト識別子（例: "my-project"）。省略時は全プロジェクト横断'),
  status: z.enum(['open', 'closed', 'all']).default('open')
    .describe('チケットのステータスフィルタ'),
  maxResults: z.number().int().min(1).max(100).default(20)
    .describe('最大取得件数（Agent が抽出時に参照する上限）'),
})

// ── 出力 ──
const outputSchema = z.object({
  pageSnapshot: z.string().describe(
    '検索結果ページのアクセシビリティスナップショット。' +
    'Agent がこのスナップショットを読み取り、チケット情報を抽出する'
  ),
  searchUrl: z.string().url().describe('実際に検索したRedmine URL'),
  currentUrl: z.string().url().describe('スナップショット取得時のURL'),
})

// ── エラー時 ──
// execute が throw した場合、Mastra が自動的に isError: true を返す。
```

**呼び出しタイミング**: Agent が `redmine` ソースを有効にして検索を実行するとき。

**status フィルタの対応**（スナップショットからフィルタUIのrefを特定して操作）:

| status | Redmine UI での操作 |
|--------|---------------------|
| `open` | ステータスが「終了」以外のチケット |
| `closed` | ステータスが「終了」のチケットのみ |
| `all` | 全ステータス |

---

### 3g. LocalSearchTool

ripgrep（`rg` / `rga`）を使ったローカルファイル全文検索。
**ブラウザ・Playwright は一切使用しない。** CLIベースの高速検索。

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ── ローカル検索結果スキーマ ──
const localFileHitSchema = z.object({
  filePath: z.string().describe('マッチしたファイルの絶対パス'),
  lineNumber: z.number().int().describe('マッチした行番号'),
  matchedLine: z.string().describe('マッチした行の内容'),
  context: z.string().optional()
    .describe('前後の行を含むコンテキスト（取得できた場合）'),
})

export type LocalFileHit = z.infer<typeof localFileHitSchema>

// ── 入力 ──
const inputSchema = z.object({
  keyword: z.string().min(1).describe('検索キーワード（正規表現対応）'),
  searchPath: z.array(z.string().min(1)).nonempty()
    .describe('検索対象のディレクトリパス（複数指定可）'),
  filePattern: z.string().optional()
    .describe('ファイルパターン（glob形式、例: "*.ts"）。省略時は全ファイル'),
  maxResults: z.number().int().min(1).max(2000).default(200)
    .describe('最大取得件数'),
})

// ── 出力 ──
const outputSchema = z.object({
  results: z.array(localFileHitSchema),
  command: z.string().describe('実行した ripgrep コマンド（デバッグ用）'),
  totalMatches: z.number().int()
    .describe('マッチ総数（maxResults で切り捨て前）'),
})

// ── エラー時 ──
// execute が throw した場合、Mastra が自動的に isError: true を返す。
// searchPath が存在しない場合は即座にエラー。
```

**呼び出しタイミング**: Agent が `local` ソースを有効にして検索を実行するとき。

**実行方式**:
- 子プロセスとして `rg --json` を実行し、JSON 出力をパース
- `rga`（ripgrep-all）が利用可能な場合は PDF/Office ファイルも検索対象
- NavigationTool / RepairTool は不要（CLI 直接実行のため）

---

## 4. Agent ↔ Tool やりとりフロー

### 正常系: SharePoint 検索（スナップショット駆動）

```
Agent
  │
  │  ① SharePointSearchTool.execute({ keyword, maxResults, siteScope })
  │     │  内部:
  │     ├─ NavigationTool.navigate(searchUrl)
  │     ├─ NavigationTool.snapshot()  ← 検索ページのスナップショット取得
  │     ├─ Agent がスナップショットから検索ボックスの ref を特定
  │     ├─ NavigationTool.type(ref, keyword)
  │     ├─ NavigationTool.wait("検索結果")
  │     ├─ NavigationTool.snapshot()  ← 結果ページのスナップショット取得
  │     └─ return { pageSnapshot, searchUrl, currentUrl }
  │
  │  ② Agent がスナップショットを読み取り、検索結果を認識
  │
  │  ③ SharePointExtractTool.execute({ pageSnapshot, sourceType: "sharepoint" })
  │     → { results: [...], confidence: "high", itemsFound: 15 }
  │
  └─ Agent は results を SearchHit[] にマッピング
```

### 異常系: Agent 判断失敗 → リトライ

```
Agent
  │
  │  ①② SearchTool + ExtractTool（正常系と同じ）
  │     → { results: [], confidence: "low", itemsFound: 0 }
  │
  │  ③ Agent: 「検索結果が見つからない。ページが読み込み途中かもしれない」
  │
  │  ④ RetryTool.execute({ reason: "検索結果未読み込み", strategy: "wait" })
  │     → { pageSnapshot: "（新しいスナップショット）", currentUrl }
  │
  │  ⑤ Agent が新しいスナップショットを再度読み取り
  │
  │  ⑥ SharePointExtractTool.execute({ pageSnapshot: newSnapshot })
  │     → { results: [...], confidence: "high" }  ← 成功
  │       or
  │     → { results: [], confidence: "low" }  ← 再度失敗 → Agent が諦めて報告
  │
  └─ Agent は結果に応じて reasoning を記載
```

### 正常系: Redmine / Teams 検索（共通パターン）

Webソースは全て同じスナップショット駆動パターンに従う:

```
Agent
  │
  │  ① XxxSearchTool.execute({ keyword, ... })
  │     → { pageSnapshot, searchUrl, currentUrl }
  │
  │  ② Agent がスナップショットを読み取り
  │
  │  ③ SharePointExtractTool.execute({
  │       pageSnapshot,
  │       sourceType: "redmine" | "teams" | "generic"
  │     })
  │     → { results, confidence, itemsFound }
  │
  │  ④ confidence が low なら → RetryTool でリトライ（上記異常系と同じ）
  │
  └─ Agent は results をマッピング
```

### 正常系: ローカル検索

```
Agent
  │
  │  ① LocalSearchTool.execute({ keyword, searchPath, filePattern, maxResults })
  │     │
  │     ├─ ripgrep 子プロセス実行（rg --json ...）
  │     ├─ JSON 出力をパースし localFileHitSchema にマッピング
  │     └─ return { results, command, totalMatches }
  │
  └─ Agent は results を SearchHit[] にマッピング
```

**Note**: LocalSearchTool はブラウザ不要。スナップショットも RetryTool も使わない。

### Agent の判断フロー（疑似コード）

```
1. ユーザーのキーワードを受け取る
2. 有効なソースを確認
3. local が有効なら（最優先）:
   a. LocalSearchTool を呼ぶ → 結果を直接取得（スナップショット不要）
4. Web ソースごとに（sharepoint / teams / redmine）:
   a. XxxSearchTool を呼ぶ → スナップショットを取得
   b. Agent がスナップショットを読み取り、ページ構造を理解
   c. ExtractTool でスナップショットから構造化データを抽出
   d. confidence が low なら:
      i.  RetryTool で新しいスナップショットを取得
      ii. 再度 ExtractTool で抽出を試みる（最大2〜3回）
      iii. それでも失敗なら reasoning に理由を記載して次へ
5. 全ソースの結果を統合して構造化出力を返す
```

---

## 5. MCP 対応の拡張ポイント

### 現在のアーキテクチャ

v1 では `mcpClient.ts` が全 Tool の MCP 呼び出しを `switch` 文でルーティングしていた。
現行では各 Tool が直接 playwright-mcp クライアントを使用する。

### playwright-mcp との統合

NavigationTool は内部で playwright-mcp の以下のツールを使用する:

| playwright-mcp ツール | NavigationTool action との対応 |
|----------------------|-------------------------------|
| `browser_navigate` | `navigate` |
| `browser_click` | `click` |
| `browser_type` | `type` |
| `browser_snapshot` | `snapshot` |
| `browser_wait_for` | `wait` |

### 各ソースと playwright-mcp の関係

| SearchTool | playwright-mcp 使用 | NavigationTool | RetryTool | ExtractTool |
|------------|---------------------|----------------|-----------|-------------|
| SharePointSearchTool | Yes | Yes | Yes | Yes |
| TeamsMessageSearchTool | Yes | Yes | Yes | Yes（sourceType: teams） |
| RedmineSearchTool | Yes | Yes | Yes | Yes（sourceType: redmine） |
| LocalSearchTool | **No**（ripgrep CLI） | No | No | No |

**スナップショット駆動の利点**: 新しいWebソースを追加しても、
ExtractTool と RetryTool は共通で使える。Agent がスナップショットから
適応的に判断するため、ソース固有のパーサーを書く必要がない。

### 新しいソースの追加手順

新しい検索ソース（例: Confluence）を追加する場合:

**Web ベースのソース（スナップショット駆動）:**
1. **`ConfluenceSearchTool`** を作成 — NavigationTool で遷移、スナップショットを返却
2. **Agent の tools に登録** — `agent.ts` の tools オブジェクトに追加
3. **ExtractTool で `sourceType: "confluence"` を指定** — Agent がスナップショットを解釈
4. **RetryTool / NavigationTool は共通** — 変更不要

**CLI ベースのソース（ローカル検索のような場合）:**
1. **`XxxSearchTool`** を作成 — 子プロセスで CLI を実行し結果をパース
2. **Agent の tools に登録**
3. スナップショット / NavigationTool / RetryTool は不要

**重要**: Webベースのソースでは固定セレクタを書かない。
SearchTool は「遷移してスナップショットを返す」だけに徹し、
解釈は Agent + ExtractTool に委ねる。

### MCP サーバーとしての公開（将来）

各 Tool に `mcp` プロパティを追加することで、外部から MCP 経由で呼び出せる:

```typescript
createTool({
  id: 'sharepoint.search',
  // ...既存定義...
  mcp: {
    annotations: {
      title: 'SharePoint Search',
      readOnlyHint: true,
      openWorldHint: true,
    },
  },
})
```

これにより、SearchTool 自体が MCP サーバーとして振る舞い、
他のエージェントや外部システムから検索機能を利用できるようになる。

---

## Appendix: 共通型定義

```typescript
// shared/tool-contracts.ts に配置想定

import { z } from 'zod'

/** 検索結果1件の共通スキーマ（SharePoint等Web検索用） */
export const searchHitSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  snippet: z.string(),
  lastModified: z.string().datetime().optional(),
})

export type SearchHit = z.infer<typeof searchHitSchema>

/** Teamsメッセージ結果スキーマ */
export const teamsMessageHitSchema = z.object({
  sender: z.string(),
  message: z.string(),
  channel: z.string().optional(),
  timestamp: z.string(),
  url: z.string().url().optional(),
})

export type TeamsMessageHit = z.infer<typeof teamsMessageHitSchema>

/** Redmineチケット結果スキーマ */
export const redmineTicketHitSchema = z.object({
  ticketId: z.string(),
  title: z.string(),
  status: z.string(),
  assignee: z.string().optional(),
  url: z.string().url(),
})

export type RedmineTicketHit = z.infer<typeof redmineTicketHitSchema>

/** ローカルファイル検索結果スキーマ */
export const localFileHitSchema = z.object({
  filePath: z.string(),
  lineNumber: z.number().int(),
  matchedLine: z.string(),
  context: z.string().optional(),
})

export type LocalFileHit = z.infer<typeof localFileHitSchema>

/** Tool のエラー応答（Mastra 標準に準拠） */
// Mastra は execute が throw した場合 isError: true を返す。
// アプリケーション固有のエラー情報は Error.message に含める。
```
