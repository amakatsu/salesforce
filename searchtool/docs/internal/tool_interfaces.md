# SearchTool v2 — Tool インターフェース定義

> **Version**: 2.0.0-draft
> **対象**: `app/src/main/mastra/tools/` 配下の Tool 群

## 1. 設計方針

### v1 の課題

v1 では各ソース（SharePoint, Redmine 等）ごとにモノリシックな Tool が存在し、
「ブラウザ操作 → ページ解析 → 結果抽出」を 1 つの execute 内で一気通貫していた。
この構造は以下の問題を抱える:

- 抽出ロジックの変更がブラウザ操作コードに波及する
- 抽出失敗時のリトライが Tool 全体の再実行になる
- playwright-mcp のスナップショットを活用できない

### v2 の方針

**責務を分離する。**

| レイヤー | 責務 | 状態 |
|----------|------|------|
| NavigationTool | ブラウザ操作（遷移・入力・クリック） | ステートフル（ブラウザ） |
| SearchTool | 検索実行のオーケストレーション | ステートレス |
| ExtractTool | ページスナップショットからの構造化データ抽出 | 純粋関数 |
| RepairTool | 抽出失敗時の再取得・再抽出 | ステートフル（ブラウザ） |

### 制約

- Mastra `createTool` API に準拠
- スキーマは Zod で定義（実装にそのまま使える精度）
- 最小プロダクト: SharePoint 検索結果トップ N（タイトル / URL / スニペット）

---

## 2. Tool 一覧と責務

```
Agent
  │
  ├─ SharePointSearchTool   検索を実行し結果を返す（メイン導線）
  │    ├─ NavigationTool     SharePoint検索ページへ遷移・キーワード入力
  │    ├─ SharePointExtractTool  スナップショットから検索結果を抽出
  │    └─ RepairTool         抽出失敗時にplaywright-mcpで再抽出
  │
  └─ NavigationTool          単独でも使用可（ページ遷移・操作）
```

| Tool | いつ呼ばれるか |
|------|----------------|
| `SharePointSearchTool` | Agent がSharePoint検索を実行するとき |
| `SharePointExtractTool` | 検索結果ページのスナップショットから結果を取り出すとき |
| `NavigationTool` | ブラウザでページ遷移・クリック・テキスト入力が必要なとき |
| `RepairTool` | ExtractTool が失敗し、再取得が必要なとき |

---

## 3. 各 Tool のインターフェース定義

### 3a. SharePointSearchTool

SharePoint の検索を実行し、構造化された結果を返す。
内部で NavigationTool → SharePointExtractTool を順に呼ぶオーケストレーター。

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

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
  keyword: z.string().min(1).describe('検索キーワード'),
  maxResults: z.number().int().min(1).max(100).default(20)
    .describe('最大取得件数'),
  siteScope: z.string().url().optional()
    .describe('検索対象を絞るSharePointサイトURL（省略時は全サイト）'),
})

// ── 出力 ──
const outputSchema = z.object({
  results: z.array(searchHitSchema),
  searchUrl: z.string().url().describe('実際に検索したURL'),
  totalFound: z.number().int().optional()
    .describe('SharePointが報告した総件数（取得できた場合）'),
})

// ── エラー時 ──
// execute が throw した場合、Mastra が自動的に isError: true を返す。
// エラーメッセージは Error.message に記載。
```

**呼び出しタイミング**: Agent が `sharepoint` ソースを有効にして検索を実行するとき。

---

### 3b. SharePointExtractTool

ページのアクセシビリティスナップショットを受け取り、
検索結果を構造化データとして抽出する。**ブラウザ操作は一切行わない。**

```typescript
// ── 入力 ──
const inputSchema = z.object({
  pageSnapshot: z.string().min(1)
    .describe('playwright-mcp browser_snapshot で取得したMarkdown形式のアクセシビリティスナップショット'),
})

// ── 出力 ──
const outputSchema = z.object({
  results: z.array(searchHitSchema),
  confidence: z.enum(['high', 'medium', 'low'])
    .describe('抽出結果の信頼度。low の場合 RepairTool の使用を推奨'),
  rawItemCount: z.number().int()
    .describe('スナップショット内で検出した候補要素数'),
})
```

**呼び出しタイミング**: NavigationTool で検索ページに遷移し、スナップショットを取得した後。

**confidence の判定基準**:
- `high`: 全候補から title + url が正常に抽出できた
- `medium`: 一部の候補で url または snippet が欠損
- `low`: 候補が 0 件、またはスナップショットのパースに失敗

---

### 3c. NavigationTool

playwright-mcp を通じてブラウザを操作する。
1 つの action を実行し、結果を返す。

```typescript
// ── 入力 ──
const actionSchema = z.enum([
  'navigate',   // URLへ遷移
  'click',      // 要素をクリック
  'type',       // テキストを入力
  'snapshot',   // 現在のページのアクセシビリティスナップショットを取得
  'wait',       // 指定秒数またはテキスト出現を待機
])

const inputSchema = z.object({
  action: actionSchema,
  target: z.string().describe(
    'navigate: URL, click/type: 要素のref値またはアクセシブルな説明, ' +
    'snapshot: 不要（空文字可）, wait: 待機対象テキストまたは空文字'
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
    .describe('action が snapshot の場合のみ。Markdown形式のスナップショット'),
  error: z.string().optional()
    .describe('失敗時のエラーメッセージ'),
})
```

**呼び出しタイミング**: ブラウザ操作が必要なあらゆる場面。

**action ごとの振る舞い**:

| action | target | value | 動作 |
|--------|--------|-------|------|
| `navigate` | URL | — | そのURLへ遷移 |
| `click` | 要素ref | — | 要素をクリック |
| `type` | 要素ref | 入力文字列 | 要素にテキスト入力 |
| `snapshot` | （空文字可） | — | 現在ページのスナップショットを返す |
| `wait` | 待機テキスト | タイムアウト秒 | テキスト出現を待機 |

---

### 3d. RepairTool

ExtractTool の抽出が失敗（confidence: low）または例外時に、
playwright-mcp を使って再度スナップショットを取得し、別戦略で再抽出を試みる。

```typescript
// ── 入力 ──
const inputSchema = z.object({
  failedToolName: z.string().describe('失敗した Tool の id（例: "sharepoint.extract"）'),
  errorMessage: z.string().describe('失敗時のエラーメッセージまたは状況説明'),
  pageSnapshot: z.string().describe(
    '失敗時点のスナップショット（再利用可能な場合）。' +
    '空文字の場合は現在のページから再取得する'
  ),
})

// ── 出力 ──
const outputSchema = z.object({
  repaired: z.boolean().describe('修復に成功したか'),
  results: z.array(searchHitSchema).optional()
    .describe('修復成功時の抽出結果'),
  escalation: z.string().optional()
    .describe('修復失敗時の理由。Agent はこれをユーザーに報告する'),
  strategy: z.string().optional()
    .describe('使用した修復戦略（デバッグ用）'),
})
```

**呼び出しタイミング**: SharePointExtractTool が `confidence: low` を返した場合、
または execute 内で例外が発生した場合。

**修復戦略の優先順**:
1. 現在のスナップショットで DOM セレクターを変えて再抽出
2. ページを再読み込みし、新しいスナップショットで再抽出
3. 修復不能と判断し `escalation` メッセージを返す

---

## 4. Agent ↔ Tool やりとりフロー

### 正常系: SharePoint 検索

```
Agent
  │
  │  ① SharePointSearchTool.execute({ keyword, maxResults, siteScope })
  │     │
  │     │  内部で以下を順に実行:
  │     │
  │     ├─ ② NavigationTool.execute({ action: "navigate", target: searchUrl })
  │     │     → { success: true, currentUrl }
  │     │
  │     ├─ ③ NavigationTool.execute({ action: "wait", target: "検索結果" })
  │     │     → { success: true }
  │     │
  │     ├─ ④ NavigationTool.execute({ action: "snapshot" })
  │     │     → { success: true, pageSnapshot: "..." }
  │     │
  │     ├─ ⑤ SharePointExtractTool.execute({ pageSnapshot })
  │     │     → { results: [...], confidence: "high", rawItemCount: 15 }
  │     │
  │     └─ return { results, searchUrl, totalFound }
  │
  └─ Agent は results を SearchHit[] にマッピング
```

### 異常系: 抽出失敗 → 修復

```
Agent
  │
  │  ① SharePointSearchTool.execute({ keyword, maxResults })
  │     │
  │     ├─ ②③④ NavigationTool（正常系と同じ）
  │     │
  │     ├─ ⑤ SharePointExtractTool.execute({ pageSnapshot })
  │     │     → { results: [], confidence: "low", rawItemCount: 0 }
  │     │
  │     ├─ ⑥ RepairTool.execute({
  │     │       failedToolName: "sharepoint.extract",
  │     │       errorMessage: "confidence: low, rawItemCount: 0",
  │     │       pageSnapshot: "..."
  │     │     })
  │     │     → { repaired: true, results: [...], strategy: "alt-selectors" }
  │     │       or
  │     │     → { repaired: false, escalation: "ページ構造が想定外" }
  │     │
  │     └─ repaired ? return results : return empty + log escalation
  │
  └─ Agent は結果に応じて reasoning を記載
```

### Agent の判断フロー（疑似コード）

```
1. ユーザーのキーワードを受け取る
2. 有効なソースを確認
3. SharePoint が有効なら:
   a. SharePointSearchTool を呼ぶ
   b. results が空でも confidence が high なら「該当なし」として扱う
   c. RepairTool でも失敗したら escalation を reasoning に含める
4. 全ソースの結果を統合して構造化出力を返す
```

---

## 5. MCP 対応の拡張ポイント

### 現在のアーキテクチャ

v1 では `mcpClient.ts` が全 Tool の MCP 呼び出しを `switch` 文でルーティングしていた。
v2 では各 Tool が直接 playwright-mcp クライアントを使用する。

### playwright-mcp との統合

NavigationTool は内部で playwright-mcp の以下のツールを使用する:

| playwright-mcp ツール | NavigationTool action との対応 |
|----------------------|-------------------------------|
| `browser_navigate` | `navigate` |
| `browser_click` | `click` |
| `browser_type` | `type` |
| `browser_snapshot` | `snapshot` |
| `browser_wait_for` | `wait` |

### 新しいソースの追加手順

新しい検索ソース（例: Confluence）を追加する場合:

1. **`ConfluenceExtractTool`** を作成 — そのソース固有の抽出ロジック
2. **`ConfluenceSearchTool`** を作成 — NavigationTool + ExtractTool をオーケストレーション
3. **Agent の tools に登録** — `agent.ts` の tools オブジェクトに追加
4. **RepairTool は共通** — 新ソースでもそのまま使える

NavigationTool と RepairTool は全ソース共通のため、変更不要。

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

/** 検索結果1件の共通スキーマ */
export const searchHitSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  snippet: z.string(),
  lastModified: z.string().datetime().optional(),
})

export type SearchHit = z.infer<typeof searchHitSchema>

/** Tool のエラー応答（Mastra 標準に準拠） */
// Mastra は execute が throw した場合 isError: true を返す。
// アプリケーション固有のエラー情報は Error.message に含める。
```
