# 適応的判断プロンプト設計書

## 概要

SearchTool の Web 検索（Redmine / SharePoint / Teams / 社内 Docs）は、
**毎回 playwright-mcp のアクセシビリティスナップショットを取得し、Agent が判断して検索結果を抽出する**。

固定セレクタによる DOM 走査は行わない。
サイトの HTML 構造に依存しないため、サイト側の変更で壊れることがない。

```
ページ遷移 → browser_snapshot → Agent が抽出判断 → 構造化 JSON
```

---

## 1. 設計思想

### なぜ固定セレクタを使わないか

| 固定セレクタ方式 | 適応的判断方式 |
|-----------------|--------------|
| サイト HTML に依存する | アクセシビリティツリーに依存する |
| HTML 変更で壊れる | 意味構造が変わらない限り動く |
| 壊れたら修復ロジックが必要 | 毎回同じフローで動く |
| セレクタのメンテナンスコスト | プロンプトのメンテナンスのみ |

### 基本フロー（全ソース共通）

```
1. playwright-mcp で対象ページに遷移（browser_navigate）
2. ページの読み込み完了を待機
3. browser_snapshot でアクセシビリティスナップショットを取得
4. ソース別の抽出プロンプト + スナップショットを Agent に渡す
5. Agent が構造化 JSON を返す
6. JSON を SearchHit[] 形式に変換して返す
```

---

## 2. playwright-mcp アクセシビリティスナップショット

### 仕組み

playwright-mcp は `browser_snapshot` ツールを提供する。
これはページの **アクセシビリティツリー** をマークダウン形式で返す。
ピクセルベースではなく構造化テキストなので、Agent が解析しやすい。

### 取得方法

現在のコードでは `StdioClientTransport` で playwright-mcp プロセスと通信している。
スナップショット取得は既存の `callTool` 関数で呼び出せる。

```typescript
// 既存の callTool を流用
const snapshotResult = await callTool(
  client,
  'browser_snapshot',
  {},  // 引数なし（現在のページのスナップショット）
  timeoutMs,
)
const snapshotText = getTextContent(snapshotResult)
```

### スナップショットの形式（例）

```
- navigation "Main Navigation"
  - link "Home" [ref=e1]
  - link "Search" [ref=e2]
- main
  - heading "Search Results for: keyword" [level=1]
  - list
    - listitem
      - link "Result Title 1" [ref=e3]
        - text "https://example.com/page1"
      - paragraph "This is the snippet for result 1..."
    - listitem
      - link "Result Title 2" [ref=e4]
        - text "https://example.com/page2"
      - paragraph "This is the snippet for result 2..."
```

---

## 3. 抽出プロンプト

### 設計方針

- Agent にはスナップショットと出力形式だけを渡す
- サイト固有の CSS セレクタ知識は含めない
- JSON 以外を出力させない
- 毎回の検索で使う基本動作のプロンプトである（「修復」ではない）

### 3.1 汎用抽出プロンプト（SharePoint / 社内 Docs）

以下のプロンプトは、スナップショットから検索結果を抽出する際に Agent に渡す。

```
あなたは検索結果抽出エンジンです。以下のルールを厳守してください。

# 入力
Webページのアクセシビリティスナップショットが提供されます。
このページは検索結果ページです。

# タスク
スナップショットから検索結果を抽出し、JSON配列として出力してください。

# 出力形式
```json
{
  "results": [
    {
      "title": "検索結果のタイトル",
      "url": "結果のURL（絶対URL）",
      "snippet": "結果の説明文やスニペット（300文字以内）"
    }
  ]
}
```

# 制約
- results 配列の上限は {maxItems} 件
- ナビゲーション、ヘッダー、フッター、広告は除外すること
- URL が相対パスの場合は "{baseUrl}" を基準に絶対URLへ変換すること
- title が取れない場合は URL をそのまま title にすること
- snippet が取れない場合は空文字 "" にすること
- 検索結果が見つからない場合は空の results 配列を返すこと
- JSON 以外のテキストを出力しないこと

# スナップショット
{snapshot}
```

#### プロンプトの変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{maxItems}` | 取得上限件数 | `50` |
| `{baseUrl}` | 検索対象サイトの base URL | `https://sharepoint.example.com` |
| `{snapshot}` | `browser_snapshot` の出力テキスト | （上記例参照） |

### 3.2 Redmine 抽出プロンプト

Redmine はチケット管理システムであり、検索結果にはチケット ID・ステータス・担当者が含まれる。
汎用プロンプトでは `title / url / snippet` しか取れないため、Redmine 専用プロンプトを用意する。

```
あなたはRedmineチケット抽出エンジンです。以下のルールを厳守してください。

# 入力
Redmine検索結果ページのアクセシビリティスナップショットが提供されます。

# タスク
スナップショットからRedmineの検索結果（チケット・Wikiページ等）を抽出し、JSON配列として出力してください。

# 出力形式
```json
{
  "results": [
    {
      "ticketId": "12345",
      "title": "チケットまたはページのタイトル",
      "status": "進行中",
      "assignee": "担当者名",
      "url": "https://redmine.example.com/issues/12345"
    }
  ]
}
```

# 制約
- results 配列の上限は {maxItems} 件
- ticketId はURLパスの `/issues/` 以降の数字。Wikiページ等でIDがない場合は空文字 ""
- status が取れない場合は空文字 ""（チケット以外の検索結果もあり得る）
- assignee が取れない場合は null
- URL が相対パスの場合は "{baseUrl}" を基準に絶対URLへ変換すること
- ナビゲーション、サイドバー、フッターは除外すること
- 検索結果が見つからない場合は空の results 配列を返すこと
- JSON 以外のテキストを出力しないこと

# スナップショット
{snapshot}
```

#### プロンプトの変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{maxItems}` | 取得上限件数 | `50` |
| `{baseUrl}` | Redmine の base URL | `https://redmine.example.com` |
| `{snapshot}` | `browser_snapshot` の出力テキスト | — |

#### スナップショット例（Redmine）

```
- main
  - heading "Search results" [level=2]
  - list "search-results"
    - listitem
      - link "Bug #12345: ログイン画面でエラーが発生する" [ref=e10]
      - text "プロジェクト: MyProject"
      - text "ステータス: 進行中  担当: 田中太郎"
      - paragraph "ログイン画面で特定の条件下でエラーが..."
    - listitem
      - link "Feature #12346: ダッシュボード改善" [ref=e11]
      - text "プロジェクト: MyProject"
      - text "ステータス: 新規  担当: 佐藤花子"
      - paragraph "ダッシュボードにグラフ表示を追加..."
```

### 3.3 Teams メッセージ抽出プロンプト

Teams のメッセージ検索結果は一般的な Web 検索と構造が異なる。
送信者・チャンネル名・タイムスタンプがメッセージに紐づくため、専用プロンプトを用意する。

```
あなたはMicrosoft Teamsメッセージ抽出エンジンです。以下のルールを厳守してください。

# 入力
Microsoft Teams検索結果ページのアクセシビリティスナップショットが提供されます。
検索対象はチャットメッセージおよびチャンネルメッセージです。

# タスク
スナップショットからTeamsの検索結果メッセージを抽出し、JSON配列として出力してください。

# 出力形式
```json
{
  "results": [
    {
      "sender": "送信者の表示名",
      "message": "メッセージ本文（500文字以内）",
      "channel": "チャンネル名またはチャット相手名",
      "timestamp": "2026-01-15T10:30:00",
      "url": "メッセージへのパーマリンク"
    }
  ]
}
```

# 制約
- results 配列の上限は {maxItems} 件
- sender が取れない場合は "不明" とすること
- message はメッセージ本文のみ。UIラベルや装飾テキストは含めないこと
- channel が取れない場合は null（1対1チャットの場合も null でよい）
- timestamp は ISO 8601 形式。取れない場合は null
- url が取れない場合は null
- 検索フィルター、ナビゲーション、サイドバーのUI要素は除外すること
- 同一メッセージの重複は除外すること
- 検索結果が見つからない場合は空の results 配列を返すこと
- JSON 以外のテキストを出力しないこと

# スナップショット
{snapshot}
```

#### プロンプトの変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{maxItems}` | 取得上限件数 | `50` |
| `{snapshot}` | `browser_snapshot` の出力テキスト | — |

注意: Teams の抽出プロンプトには `{baseUrl}` がない。
Teams メッセージの URL はスナップショット内のリンクからそのまま取得するため。

#### スナップショット例（Teams）

```
- main
  - heading "Search" [level=1]
  - tablist
    - tab "Messages" [selected]
    - tab "People"
    - tab "Files"
  - list
    - listitem
      - text "田中太郎"
      - text "開発チーム > general"
      - text "1月15日 10:30"
      - paragraph "デプロイ手順を更新しました。確認お願いします。"
      - link "Go to message" [ref=e20]
    - listitem
      - text "佐藤花子"
      - text "1月14日 15:00"
      - paragraph "レビューコメントを反映しました。"
      - link "Go to message" [ref=e21]
```

### 3.4 ローカル検索（適応的判断の対象外）

ローカル検索（`local-fs.server.ts`）は **適応的判断の対象外** である。

**理由**:
- ripgrep（`rg` / `rga`）による CLI ベースの全文検索であり、ブラウザ操作を伴わない
- スナップショットという概念が存在しない
- 入出力が JSON Lines 形式で決定的に動作する

ローカル検索で失敗するケース（ripgrep 未インストール、パス不在等）は、
現在の `runLocalSearch` のエラーハンドリングで十分対応できている。

---

## 4. 抽出フロー詳細

### 4.1 基本シーケンス（Redmine / SharePoint / 社内 Docs）

```
1. playwright-mcp で検索URLに遷移（browser_navigate）
2. ページ読み込み完了を待機（waitForTimeout）
3. browser_snapshot でスナップショットを取得
4. ソース別プロンプト + スナップショットを Agent に渡す
5. Agent が構造化 JSON を返す
6. JSON を SearchHit[] 形式に変換して返す
```

### 4.2 Teams シーケンス（SPA 対応）

Teams Web は SPA であり、DOM が遅延レンダリングされる。
スナップショット取得前に十分な待機が必要。

```
1. playwright-mcp で Teams 検索URLに遷移（browser_navigate）
2. 初回待機（3秒）
3. browser_snapshot でスナップショットを取得
4. スナップショットに検索結果が含まれるか簡易チェック
   - 含まれない場合: 追加待機（2秒）→ スナップショット再取得
5. Teams 抽出プロンプト + スナップショットを Agent に渡す
6. Agent が構造化 JSON を返す
7. JSON を SearchHit[] 形式に変換して返す
```

---

## 5. リトライ設計

### 抽出失敗の定義

| 条件 | 判断 |
|------|------|
| Agent が空の results を返した | 検索結果なし（正常） |
| Agent が JSON パースエラーを起こした | 抽出失敗（リトライ対象） |
| スナップショットが空だった | ページ読み込み失敗（リトライ対象） |
| タイムアウト | ネットワークまたはサイト障害 |

### リトライ上限

| ソース | スナップショット取得 | Agent 判断 | 合計 |
|--------|-------------------|-----------|------|
| Redmine / SharePoint / 社内 Docs | 1 回 | リトライ 1 回 | 最大 2 回 |
| Teams | 1 回 + 追加待機 1 回 | リトライ 1 回 | 最大 3 回 |

### エスカレーション条件

リトライ上限に達しても結果が取れない場合:
- `errors.<source>` にメッセージをセット
- ログに `level: 'error'` で記録
- UI のエラー表示に「検索結果の抽出に失敗しました。サイトに接続できないか、ページ構造が想定外です」と表示

---

## 6. 実装箇所

### 変更対象ファイルと変更内容

各 MCP サーバーから固定セレクタの `execute-code` を廃止し、
`browser_snapshot` + Agent 判断に置き換える。

```typescript
// 擬似コード: 適応的判断の実装
export const runRedmineSearch = async (input: RedmineSearchInput): Promise<RedmineSearchHit[]> => {
  // ... 既存の client.connect ...

  // 1. ページ遷移
  const searchUrl = buildSearchUrl(input.baseUrl, input.keyword)
  await callTool(client, 'browser_navigate', { url: searchUrl }, timeoutMs)

  // 2. 待機
  await callTool(client, 'browser_wait_for', { time: 2 }, timeoutMs)

  // 3. スナップショット取得
  const snapshotResult = await callTool(client, 'browser_snapshot', {}, timeoutMs)
  const snapshotText = getTextContent(snapshotResult)
  if (!snapshotText) {
    return []
  }

  // 4. Agent による抽出判断
  return adaptiveExtract('redmine', snapshotText, input.baseUrl, maxItems)
}
```

### adaptiveExtract の配置

抽出ロジックは全サーバーで共通化する。

```
src/main/mcp-servers/
  adaptive-extract.ts         ← 新規: 共通の適応的抽出ロジック
  redmine-ui.server.ts        ← execute-code を廃止、適応的判断に置換
  sharepoint-search.server.ts ← 同上
  teams-search.server.ts      ← 同上（SPA 対応の追加待機あり）
  internal-docs-search.server.ts ← 同上
  local-fs.server.ts          ← 変更なし（ripgrep ベース）
```

`adaptive-extract.ts` は以下を提供する:
- `buildExtractPrompt(source, snapshot, baseUrl, maxItems)`: ソース別プロンプト組み立て
- `adaptiveExtract(source, snapshot, baseUrl, maxItems)`: Agent 呼び出し + JSON パース

ソース別のプロンプト選択:

| source | 使用するプロンプト | 出力形式 |
|--------|-------------------|---------|
| `redmine` | Redmine 抽出プロンプト | `{ticketId, title, status, assignee?, url}` |
| `sharepoint` | 汎用抽出プロンプト | `{title, url, snippet}` |
| `teams` | Teams メッセージ抽出プロンプト | `{sender, message, channel?, timestamp, url?}` |
| `internalDocs` | 汎用抽出プロンプト | `{title, url, snippet}` |
| `local` | 対象外（呼ばれない） | — |

---

## 7. Agent 呼び出し方法

抽出用の Agent 呼び出しは Mastra Agent（検索全体の統括）とは別に、軽量な単発呼び出しで行う。

理由:
- 抽出はツール呼び出し不要（スナップショットは手元にある）
- 検索統括 Agent のオーバーヘッドが不要
- 高速に結果が欲しい

```typescript
// adaptive-extract.ts（擬似コード）
import { generateText } from '@mastra/core'

const adaptiveExtract = async (
  source: 'redmine' | 'sharepoint' | 'teams' | 'internalDocs',
  snapshot: string,
  baseUrl: string,
  maxItems: number,
): Promise<Array<Record<string, unknown>>> => {
  const prompt = buildExtractPrompt(source, snapshot, baseUrl, maxItems)

  const response = await generateText({
    model: /* settings から取得 */,
    prompt,
  })

  const parsed = JSON.parse(response.text)
  return parsed.results ?? []
}
```

---

## 8. まとめ

| 項目 | 内容 |
|------|------|
| 設計思想 | 毎回スナップショットから Agent が判断（固定セレクタ不使用） |
| 基本動作 | browser_navigate → browser_snapshot → Agent 抽出 |
| リトライ | スナップショット再取得 → Agent 再判断（最大 2 回、Teams は 3 回） |
| エスカレーション | 抽出失敗時はエラーメッセージ + ログ記録 |
| 新規ファイル | `src/main/mcp-servers/adaptive-extract.ts` |
| 変更ファイル | 各 `*.server.ts` から execute-code を廃止 |
| 対象外 | ローカル検索（ripgrep ベース、ブラウザ非使用） |

### ソース別対応表

| ソース | 対象 | プロンプト | 出力形式 |
|--------|------|-----------|---------|
| Redmine | Yes | Redmine 専用 | `{ticketId, title, status, assignee?, url}` |
| SharePoint | Yes | 汎用 | `{title, url, snippet}` |
| Teams | Yes | Teams 専用 | `{sender, message, channel?, timestamp, url?}` |
| 社内 Docs | Yes | 汎用 | `{title, url, snippet}` |
| Local | **No** | — | — |
