# 自己修復メカニズム設計書

## 概要

SearchTool v2 の Web 検索（Redmine / SharePoint / Teams / 社内 Docs）は、
固定セレクタで DOM を走査して検索結果を抽出している。
サイト側の HTML 変更で抽出が壊れた場合、**playwright-mcp のアクセシビリティスナップショットを使って再抽出する**仕組みを設ける。

```
通常フロー:  execute-code（固定セレクタ） → 結果
修復フロー:  固定セレクタ失敗 → browser_snapshot → LLM で再抽出 → 結果
```

---

## 1. 壊れたと判断する基準

| 条件 | 閾値 | 備考 |
|------|------|------|
| 検索結果が 0 件 | `results.length === 0` | ページ自体は HTTP 200 で返っている |
| `error: true` が返った | execute-code 内の catch | セレクタ不在やタイムアウト |
| タイトル・URL がすべて空 | filter 後に全滅 | セレクタ名だけ一致するが中身が変わったケース |

**判断しないケース**: 検索キーワードにヒットしないだけ（検索結果ページ自体は正常表示）は修復対象外。
→ 通常フローで `{ results: [], searchUrl }` が返るのは正常動作。

区別の方法: execute-code 内で「検索結果コンテナ自体が存在するか」を先に確認する。
コンテナが存在するのに中身が取れない場合のみ修復対象とする。

```typescript
// execute-code 内の判定ロジック（擬似コード）
const containerExists = await page.$('#search-results') !== null
const results = /* 通常の抽出処理 */
return {
  results,
  containerExists,  // 修復判断に使う
  searchUrl,
}
```

---

## 2. 修復フロー

### シーケンス

```
1. 通常の execute-code を実行
2. 結果を検証（上記基準）
3. 修復対象と判断した場合:
   a. playwright-mcp の browser_snapshot ツールを呼ぶ
   b. スナップショット（テキスト）を取得
   c. LLM に修復プロンプト + スナップショットを渡す
   d. LLM が構造化 JSON を返す
   e. 通常の SearchHit[] 形式に変換して返す
4. 修復でも取れなければ error を返す
```

### リトライ上限

| 段階 | 回数 | 理由 |
|------|------|------|
| 通常抽出 | 1 回 | 固定セレクタは冪等 |
| 修復抽出 | 1 回 | LLM 呼び出しはコストが高い |
| 合計 | 最大 2 回 | これ以上はサイト障害とみなす |

### エスカレーション条件

修復抽出も失敗した場合:
- `errors.redmine`（または該当ソース）にメッセージをセット
- ログに `level: 'error'` で記録
- UI のエラー表示に「セレクタ修復に失敗しました。サイトの HTML 構造が変更された可能性があります」と表示

---

## 3. playwright-mcp アクセシビリティスナップショットの取得

### 仕組み

playwright-mcp は `browser_snapshot` ツールを提供する。
これはページの **アクセシビリティツリー** をマークダウン形式で返す。
ピクセルベースではなく構造化テキストなので、LLM が解析しやすい。

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

## 4. 修復プロンプト

### 設計方針

- LLM にはスナップショットと出力形式だけを渡す
- サイト固有の知識は含めない（汎用性を保つ）
- JSON 以外を出力させない

### 修復プロンプト雛形

以下のプロンプトは、スナップショットから検索結果を抽出する際に LLM に渡す。

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
- JSON 以外のテキストを出力しないこと

# スナップショット
{snapshot}
```

### プロンプトの変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `{maxItems}` | 取得上限件数 | `50` |
| `{baseUrl}` | 検索対象サイトの base URL | `https://redmine.example.com` |
| `{snapshot}` | `browser_snapshot` の出力テキスト | （上記例参照） |

---

## 5. 修復の実装箇所

### 変更対象ファイルと変更内容

各 MCP サーバー（`redmine-ui.server.ts`, `sharepoint-search.server.ts` など）の
`run*Search` 関数に修復ロジックを追加する。

```typescript
// 擬似コード: redmine-ui.server.ts の修復追加
export const runRedmineSearch = async (input: RedmineSearchInput): Promise<RedmineSearchHit[]> => {
  // ... 既存の client.connect / init-browser ...

  // 1. 通常抽出
  const execResult = await callTool(client, 'execute-code', { code: buildExecuteScript(...) }, timeoutMs)
  const hits = extractHits(execResult, input.baseUrl)

  // 2. 修復判定
  const payload = JSON.parse(getTextContent(execResult) ?? '{}')
  const needsRepair = payload.containerExists && hits.length === 0

  if (!needsRepair) {
    return hits.slice(0, maxItems)
  }

  // 3. 修復抽出
  const snapshotResult = await callTool(client, 'browser_snapshot', {}, timeoutMs)
  const snapshotText = getTextContent(snapshotResult)
  if (!snapshotText) {
    return []
  }

  return repairExtract(snapshotText, input.baseUrl, maxItems)
}
```

### repairExtract の配置

修復ロジックは全サーバーで共通化する。

```
src/main/mcp-servers/
  repair.ts              ← 新規: 共通の修復抽出ロジック
  redmine-ui.server.ts   ← 修復呼び出しを追加
  sharepoint-search.server.ts
  teams-search.server.ts
  internal-docs-search.server.ts
```

`repair.ts` は以下を提供する:
- `buildRepairPrompt(snapshot, baseUrl, maxItems)`: プロンプト組み立て
- `repairExtract(snapshot, baseUrl, maxItems)`: LLM 呼び出し + JSON パース

---

## 6. LLM 呼び出し方法

修復用の LLM 呼び出しは Mastra Agent とは別に、軽量な単発呼び出しで行う。

理由:
- 修復はツール呼び出し不要（スナップショットは手元にある）
- Agent のオーバーヘッドが不要
- 高速に結果が欲しい

```typescript
// repair.ts での LLM 呼び出し（擬似コード）
import { generateText } from '@mastra/core'

const repairExtract = async (
  snapshot: string,
  baseUrl: string,
  maxItems: number,
): Promise<Array<{ title: string; url: string; snippet: string }>> => {
  const prompt = buildRepairPrompt(snapshot, baseUrl, maxItems)

  const response = await generateText({
    model: /* settings から取得 */,
    prompt,
  })

  const parsed = JSON.parse(response.text)
  return parsed.results ?? []
}
```

---

## 7. まとめ

| 項目 | 内容 |
|------|------|
| トリガー | 検索結果コンテナが存在するのに抽出結果が 0 件 |
| 修復手段 | playwright-mcp `browser_snapshot` → LLM で再抽出 |
| リトライ | 通常 1 回 + 修復 1 回 = 最大 2 回 |
| エスカレーション | 修復失敗時はエラーメッセージ + ログ記録 |
| 新規ファイル | `src/main/mcp-servers/repair.ts` |
| 変更ファイル | 各 `*.server.ts` の run*Search 関数 |
