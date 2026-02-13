# SearchTool 実装計画書

> **Version**: 2.0.0-draft
> **Created**: 2026-02-11
> **Parent**: cmd_020

## 目次

1. [概要](#1-概要)
2. [v1 からの移行戦略](#2-v1-からの移行戦略)
3. [Phase 1: SharePoint検索MVP](#3-phase-1-sharepoint検索mvp)
4. [Phase 2: 社内ドキュメント検索](#4-phase-2-社内ドキュメント検索)
5. [Phase 3: Teamsメッセージ検索 + Redmine検索 + ローカル検索](#5-phase-3-teamsメッセージ検索--redmine検索--ローカル検索)
6. [Phase 4: ポータブル配布](#6-phase-4-ポータブル配布)
7. [Phase 5: 拡張（将来）](#7-phase-5-拡張将来)
8. [技術的リスクと対策](#8-技術的リスクと対策)
9. [関連設計書](#9-関連設計書)

---

## 1. 概要

### 何が変わるか

v1 は「5ソース統合検索の Electron アプリ」として完成した（95%）。
現行は **SharePoint/Teams 検索の実用化** にフォーカスする。

| 観点 | v1 | 現行 |
|------|----|----|
| SharePoint検索 | モノリシック Tool（固定セレクタ） | 責務分離（Navigation / Extract / Repair） |
| 社内ドキュメント検索 | 汎用 auto-detect（不安定） | 専用 ExtractTool で抽出精度向上 |
| Teams検索 | メッセージ検索（不安定） | Playwright UI操作でメッセージ本文を検索 |
| Redmine / ローカル | v1 実装 | v1 から維持（Phase 3 で統合確認） |
| 配布形態 | NSIS インストーラのみ | ポータブル exe 追加 |
| Node.js | 20.x（Electron 30 内蔵） | 22.x（Electron 33+ に更新） |

### 設計方針（殿の決定事項）

- **最小プロダクトの切り方**: SharePoint検索 → 社内ドキュメント検索 → Teams/Redmine/ローカル
- **リーダブルコード（t-wada流）**: 過剰設計禁止、必要最小限
- **実装者が迷わず着手できる精度** のタスク分解

---

## 2. v1 からの移行戦略

### 現状のv1アーキテクチャ

```
Renderer (React)
  ↓ IPC
Main Process (Electron 30)
  ├─ SettingsStore (Zod + JSON)
  ├─ Logger (JSONL)
  ├─ MetricsService
  └─ SearchService
       └─ Mastra Agent (OpenAI)
            ├─ localTool      → local-fs.server.ts       (ripgrep)
            ├─ redmineTool     → redmine-ui.server.ts     (playwright-mcp)
            ├─ sharepointTool  → sharepoint-search.server.ts (playwright-mcp)
            ├─ teamsTool       → teams-search.server.ts   (playwright-mcp)
            └─ internalDocsTool → internal-docs-search.server.ts (playwright-mcp)
```

### 何を残し、何を捨てるか

| コンポーネント | 判定 | 理由 |
|---------------|------|------|
| Electron シェル（main.ts, preload.ts） | **残す** | IPC 構造は堅実。Electron 33 へ更新のみ |
| React UI（App, SearchPane, Settings, Metrics） | **残す** | 変更不要。検索結果の表示形式はそのまま |
| shared/contracts.ts | **残す** | SearchHit / SearchResponse の型は現行でも有効 |
| shared/settings.ts | **残す + 拡張** | ブラウザ channel 設定を追加 |
| SettingsStore, Logger, MetricsService | **残す** | ポータブル対応で dataDir の解決ロジックのみ追加 |
| searchService.ts | **残す + 改修** | 新 Tool 群を呼ぶように Agent 生成部を差し替え |
| mastra/agent.ts | **大幅改修** | 新 Tool 構成（Navigation/Extract/Repair）に対応 |
| mastra/tools/*.ts（全5ファイル） | **捨てる** | 責務分離 Tool に置き換え |
| mastra/tools/mcpClient.ts | **捨てる** | 各 Tool が直接 playwright-mcp を使用 |
| mcp-servers/*.server.ts（全5ファイル） | **段階的に捨てる** | Phase 1 で sharepoint、Phase 2 で internalDocs、Phase 3 で teams を置き換え |
| localTool + local-fs.server.ts | **残す** | ripgrep 検索は変更なし |

### 移行の順序

```
Phase 0: Electron 33 更新（Node 22.13+ 対応）
Phase 1: SharePoint 検索を新 Tool に置き換え（他はv1のまま動く）
Phase 2: 社内ドキュメント検索を新 Tool で実装
Phase 3: Teamsメッセージ検索 + Redmine検索 + ローカル検索（まとめて統合確認）
Phase 4: ポータブル配布対応
Phase 5: 自己修復メカニズム、MCP公開、検索レシピ等の拡張
```

**重要**: 各 Phase 完了時点で、未着手ソースは v1 のまま動作し続ける。
段階的移行により、常にアプリ全体が動作する状態を保つ。

---

## 3. Phase 1: SharePoint検索MVP

> **ゴール**: Mastra Agent が SharePoint 検索を実行し、トップN件（タイトル/URL/スニペット）を返す

### 前提タスク: Electron 33 更新

Phase 1 の実装着手前に、Electron を 33+ に更新する。
Mastra `@mastra/core ^0.23` が Node.js 22.13+ を要求するため。

- [ ] **P0-1**: Electron 30 → 33 へ `package.json` を更新
- [ ] **P0-2**: `vite-plugin-electron` の互換性を確認・更新
- [ ] **P0-3**: `electron-builder` が Electron 33 に対応しているか確認・更新
- [ ] **P0-4**: `npm run dev` で起動確認（既存機能が壊れていないこと）
- [ ] **P0-5**: `npm run build:linux` でビルド確認

**完了条件**: Electron 33+ で既存v1機能が全て動作すること

**リスク**: Electron 33 の Breaking Changes が既存コードに影響する可能性
**対策**: Electron 33 リリースノートを事前確認。影響がある場合は個別対応

---

### 実装タスク一覧

#### Step 1: 共通型定義の作成

- [ ] **P1-1**: `shared/tool-contracts.ts` を新規作成
  - `searchHitSchema`（Zod）: title, url, snippet, lastModified?
  - `SearchHit` 型の export
  - 既存の `shared/contracts.ts` の `SearchHit` との整合性を確認

**完了条件**: 型定義が存在し、`npm run typecheck` が通ること

#### Step 2: NavigationTool の実装

- [ ] **P1-2**: `mastra/tools/navigationTool.ts` を新規作成
  - actions: navigate, click, type, snapshot, wait
  - 内部で playwright-mcp の対応ツールを呼ぶ
  - インターフェースは `tool_interfaces.md` §3c に準拠

**実装の要点**:
- playwright-mcp との通信は `StdioClientTransport` を使用（v1と同じ方式）
- `--browser msedge` をデフォルトとし、設定で変更可能にする
- `--user-data-dir` は Settings の `browser.userDataDir` を渡す

**完了条件**:
- NavigationTool 単体で SharePoint のページに遷移できること
- snapshot action でアクセシビリティスナップショットが取得できること

#### Step 3: SharePointExtractTool の実装

- [ ] **P1-3**: `mastra/tools/sharepointExtractTool.ts` を新規作成
  - 入力: pageSnapshot（Markdown形式のスナップショット）
  - 出力: results[], confidence, rawItemCount
  - インターフェースは `tool_interfaces.md` §3b に準拠
  - **ブラウザ操作は一切行わない**（純粋なテキスト解析）

**実装の要点**:
- スナップショットからリンク要素（`[ref=eN]` 付き）を正規表現で抽出
- ナビゲーション・ヘッダー・フッターを除外するヒューリスティクス
- confidence の判定: high（全件 title+url あり）/ medium（一部欠損）/ low（0件 or パース失敗）

**完了条件**:
- SharePoint 検索結果ページのスナップショットから正しく結果を抽出できること
- confidence が適切に判定されること

#### Step 4: SharePointSearchTool の実装

- [ ] **P1-4**: `mastra/tools/sharepointSearchTool.ts` を新規作成
  - NavigationTool → ExtractTool をオーケストレーション
  - インターフェースは `tool_interfaces.md` §3a に準拠
  - 検索URL構築: `{siteScope}/_layouts/15/osssearchresults.aspx?k={keyword}`

**実装の要点**:
- NavigationTool で検索ページへ遷移
- 結果読み込みを待機（wait action）
- snapshot を取得し ExtractTool に渡す
- confidence が low の場合は空結果を返す（将来 Phase 5 で自己修復メカニズムを導入予定）

**完了条件**:
- SharePoint サイトでキーワード検索を実行し、結果がトップN件返ること
- 検索結果なしの場合に空配列が返ること（エラーではない）

#### Step 5: Agent の差し替え

- [ ] **P1-5**: `mastra/agent.ts` を改修
  - SharePointSearchTool を Agent の tools に登録
  - 旧 sharepointTool を削除
  - buildAgentPrompt() に SharePoint の新しい使い方を記述
  - localTool, redmineTool 等は v1 のまま維持

- [ ] **P1-6**: `mastra/tools/mcpClient.ts` から sharepoint のルーティングを削除

**完了条件**:
- Agent が SharePointSearchTool を使って検索を実行できること
- Local / Redmine 等の既存検索が引き続き動作すること
- `npm run typecheck` が通ること

#### Step 6: Settings の拡張

- [ ] **P1-7**: `shared/settings.ts` に browser.channel 設定を追加
  - `browser.channel`: `'msedge' | 'chrome' | 'chromium'`（デフォルト: `'msedge'`）
  - UI には Phase 1 では追加しない（デフォルト値で動作）

**完了条件**: 設定スキーマが更新され、typecheck が通ること

#### Step 7: 結合テスト

- [ ] **P1-8**: SharePoint 検索の E2E 動作確認
  - `npm run dev` で起動
  - SharePoint を有効にして検索を実行
  - 結果がトップN件表示されること
  - 他のソース（Local, Redmine）も引き続き動作すること

**完了条件**: 全ソースが動作する状態でビルドが通ること

### Phase 1 の依存関係

```
P0-1〜P0-5 (Electron更新)
  └→ P1-1 (型定義)
       └→ P1-2 (NavigationTool)
            └→ P1-3 (ExtractTool)
                 └→ P1-4 (SearchTool)
                      └→ P1-5, P1-6 (Agent差し替え)
                           └→ P1-7 (Settings)
                                └→ P1-8 (結合テスト)
```

### Phase 1 の Definition of Done

- [ ] SharePoint 検索でトップN件（タイトル/URL/スニペット）が返る
- [ ] 既存の Local / Redmine / Teams / InternalDocs 検索が壊れていない
- [ ] `npm run typecheck` がエラーゼロ
- [ ] `npm run build:linux` が成功
- [ ] 旧 sharepoint-search.server.ts が使われていないこと

---

## 4. Phase 2: 社内ドキュメント検索

> **ゴール**: 社内ドキュメントサイト（Wiki、ナレッジベース等）の検索を新 Tool パターンで実装する

### 背景

v1 の `internal-docs-search.server.ts` は汎用的な auto-detect 方式（検索入力欄を複数セレクタで探索）を採用している。
これは対象サイトによって安定性が大きく異なり、実用的ではなかった。

Phase 1 で確立した責務分離パターン（NavigationTool + ExtractTool）を適用し、
社内ドキュメントサイト向けの専用 ExtractTool を実装することで抽出精度を向上させる。

### 実装タスク一覧

#### Step 1: InternalDocsExtractTool の実装

- [ ] **P2-1**: `mastra/tools/internalDocsExtractTool.ts` を新規作成
  - 入力: pageSnapshot（Markdown形式のスナップショット）
  - 出力: results[], confidence, rawItemCount
  - SharePointExtractTool と同じインターフェース（`tool_interfaces.md` §3b 準拠）
  - **ブラウザ操作は一切行わない**（純粋なテキスト解析）

**実装の要点**:
- 社内ドキュメントサイトは構造が多様なため、複数の抽出パターンを試行
- 抽出パターン: `.search-result`, `.result`, `article`, `[class*="result"]` 等
- 3件以上マッチした最初のパターンを採用（v1 の auto-detect ロジックを ExtractTool 内に移植）
- confidence 判定は SharePointExtractTool と同基準

**完了条件**:
- 社内ドキュメントサイトのスナップショットから検索結果を抽出できること
- 対象サイトの構造が異なっても複数パターンで対応できること

#### Step 2: InternalDocsSearchTool の実装

- [ ] **P2-2**: `mastra/tools/internalDocsSearchTool.ts` を新規作成
  - NavigationTool + InternalDocsExtractTool のオーケストレーション
  - 検索 URL の構築: baseUrl にアクセス → 検索入力欄を探索 → キーワード入力 → 結果待機
  - NavigationTool の navigate → snapshot → type → snapshot のフローで実現

**実装の要点**:
- 社内サイトは検索 URL パターンが統一されていないため、UI 操作で検索を実行
- NavigationTool で baseUrl に遷移
- snapshot で検索入力欄の ref を取得
- type action でキーワードを入力し、submit
- 結果ページの snapshot を取得し ExtractTool に渡す

**完了条件**:
- 社内ドキュメントサイトでキーワード検索を実行し、結果が返ること
- 検索結果なしの場合に空配列が返ること

#### Step 3: Agent への登録

- [ ] **P2-3**: `mastra/agent.ts` を改修
  - InternalDocsSearchTool を Agent の tools に登録
  - 旧 internalDocsTool を削除
  - buildAgentPrompt() を更新

- [ ] **P2-4**: `mastra/tools/mcpClient.ts` から internalDocs のルーティングを削除

**完了条件**:
- Agent が InternalDocsSearchTool を使って検索を実行できること
- 既存の SharePoint / Local / Redmine / Teams 検索が引き続き動作すること
- `npm run typecheck` が通ること

#### Step 4: 結合テスト

- [ ] **P2-5**: 社内ドキュメント検索の E2E 動作確認
  - `npm run dev` で起動
  - 社内ドキュメントソースを有効にして検索を実行
  - 結果が返ること
  - 他の全ソースも引き続き動作すること

**完了条件**: 全ソースが動作する状態でビルドが通ること

### Phase 2 の依存関係

```
Phase 1 完了（NavigationTool が存在、Tool パターンが確立）
  └→ P2-1 (InternalDocsExtractTool)
       └→ P2-2 (InternalDocsSearchTool)
            └→ P2-3, P2-4 (Agent登録)
                 └→ P2-5 (結合テスト)
```

### Phase 2 の Definition of Done

- [ ] 社内ドキュメントサイトの検索でトップN件が返る
- [ ] 複数パターンの抽出ロジックで多様なサイト構造に対応できる
- [ ] 既存の全ソース（SharePoint / Local / Redmine / Teams）が壊れていない
- [ ] `npm run typecheck` がエラーゼロ
- [ ] `npm run build:linux` が成功
- [ ] 旧 internal-docs-search.server.ts が使われていないこと

### リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| サイト構造が多様で抽出パターンが網羅できない | 特定サイトで結果が取れない | confidence: low を返し、ユーザーに通知。将来 Phase 5 の自己修復で対応 |
| 検索入力欄の auto-detect が失敗する | 検索自体が実行できない | 設定で検索 URL パターンを直接指定する代替手段を用意 |
| ログイン必須の社内サイト | 未認証で検索ページにアクセスできない | 既存ブラウザ（Edge）接続で SSO セッションを再利用 |

---

## 5. Phase 3: Teamsメッセージ検索 + Redmine検索 + ローカル検索

> **ゴール**: 残りの3ソースをまとめて統合確認し、全ソース検索を完成させる

### 背景

Phase 1（SharePoint）、Phase 2（社内ドキュメント）で Tool パターンが確立されている。
Phase 3 では残りの 3 ソースを対応する:

| ソース | 対応方針 |
|--------|---------|
| **Teamsメッセージ検索** | 新規 Tool（Playwright UI操作でチャット/チャンネルのメッセージ本文を検索） |
| **Redmine検索** | v1 から維持（playwright-mcp でチケット検索。動作確認のみ） |
| **ローカル検索** | v1 から維持（ripgrep。動作確認のみ） |

### 3a. Teamsメッセージ検索（新規実装）

Teams のチャット/チャンネルメッセージ本文を Playwright UI 操作で検索する。
SharePoint ベースのファイル検索ではなく、Teams 独自 UI の自動操作で実現する。

#### 実装タスク一覧

- [ ] **P3-1**: TeamsMessageExtractTool の実装（`mastra/tools/teamsMessageExtractTool.ts`）
  - 入力: pageSnapshot（Markdown形式のスナップショット）
  - 出力: results[], confidence, rawItemCount
  - 抽出フィールド: title（送信者 + 日時）, url（メッセージへのリンク）, snippet（メッセージ本文抜粋）
  - Teams 検索結果ページ固有のセレクタパターン:
    - `[data-tid="search-result-item"]`
    - `.search-result-item`
    - メッセージ本文、送信者名、タイムスタンプの抽出

**実装の要点**:
- Teams の検索結果は「メッセージ」「ファイル」「人」などのタブに分かれる
- メッセージタブのみを対象とするフィルタリングが必要
- スナップショットから送信者名・日時・本文を構造化して抽出

**完了条件**:
- Teams メッセージ検索結果のスナップショットから正しく結果を抽出できること
- メッセージタブの結果のみが抽出されること（ファイル・人は除外）

- [ ] **P3-2**: TeamsMessageSearchTool の実装（`mastra/tools/teamsMessageSearchTool.ts`）
  - NavigationTool + TeamsMessageExtractTool のオーケストレーション
  - Teams 検索 URL の構築:
    - teams.microsoft.com: `/_#/search/messages/{keyword}`
    - カスタム: `?search={keyword}`
  - NavigationTool で検索ページへ遷移 → メッセージタブ選択 → 結果待機 → snapshot → ExtractTool

**実装の要点**:
- Teams Web UI は SPA のため、ページ遷移後に結果が非同期で読み込まれる
- wait action で結果表示を待つ（最大タイムアウト: settings.limits.timeoutSeconds）
- メッセージタブへの切り替えが必要な場合は click action を使用

**完了条件**:
- Teams でキーワード検索を実行し、メッセージ結果がトップN件返ること
- 検索結果なしの場合に空配列が返ること

- [ ] **P3-3**: Agent への Teamsメッセージ検索の登録
  - TeamsMessageSearchTool を Agent の tools に追加
  - 旧 teamsTool を削除
  - `mastra/tools/mcpClient.ts` から teams のルーティングを削除
  - buildAgentPrompt() を更新

**完了条件**:
- Agent が TeamsMessageSearchTool を使って検索を実行できること
- `npm run typecheck` が通ること

### 3b. Redmine検索（v1 維持）

v1 の Redmine 検索（`redmineTool.ts` + `redmine-ui.server.ts`）はそのまま維持する。
Playwright UI オートメーションでチケット検索を行う既存実装は十分に機能している。

- [ ] **P3-4**: Redmine 検索の動作確認
  - Phase 2 完了時点の状態で Redmine 検索が正常に動作することを確認
  - 新 Tool（SharePoint, InternalDocs, Teams）との共存に問題がないこと

### 3c. ローカル検索（v1 維持）

v1 のローカル検索（`localTool.ts` + `local-fs.server.ts`）はそのまま維持する。
ripgrep（rg/rga）によるファイル検索は安定しており変更不要。

- [ ] **P3-5**: ローカル検索の動作確認
  - Phase 2 完了時点の状態でローカル検索が正常に動作することを確認
  - 他の新 Tool との共存に問題がないこと

### 3d. 全ソース結合テスト

- [ ] **P3-6**: 全5ソースの結合テスト
  - `npm run dev` で起動
  - 全ソース（SharePoint, InternalDocs, Teams, Redmine, Local）を有効にして検索を実行
  - 各ソースから結果が返ること
  - Promise.allSettled による並列検索が正常に動作すること
  - 一部ソースが失敗しても他のソースの結果が返ること（部分障害耐性）
  - `npm run build:linux` が成功すること

### Phase 3 の依存関係

```
Phase 2 完了（NavigationTool, ExtractTool パターンが確立）
  ├→ P3-1 (TeamsMessageExtractTool)
  │    └→ P3-2 (TeamsMessageSearchTool)
  │         └→ P3-3 (Agent登録)
  ├→ P3-4 (Redmine動作確認)     ← 独立して実行可能
  ├→ P3-5 (ローカル動作確認)     ← 独立して実行可能
  └→ 全て完了後 → P3-6 (全ソース結合テスト)
```

P3-1〜P3-3（Teams）と P3-4（Redmine）と P3-5（ローカル）は互いに独立しており、並行実施可能。

### Phase 3 の Definition of Done

- [ ] Teams のメッセージ検索でトップN件（送信者/本文/リンク）が返る
- [ ] Redmine 検索が v1 と同等に動作する
- [ ] ローカル検索が v1 と同等に動作する
- [ ] 全5ソース同時検索が正常に動作する
- [ ] 部分障害時に他ソースの結果が返る（部分障害耐性）
- [ ] `npm run typecheck` がエラーゼロ
- [ ] `npm run build:linux` が成功
- [ ] 旧 teamsTool.ts, teams-search.server.ts が使われていないこと

### リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| Teams Web UI が SPA で結果読み込みが遅い | タイムアウト頻発 | wait の待機時間を十分に確保（デフォルト30秒）。段階的待機 |
| Teams のメッセージタブの UI 構造が頻繁に変更される | ExtractTool の抽出が壊れる | confidence 判定で検出。将来 Phase 5 の自己修復で対応 |
| Teams の認証が SharePoint と異なる | 未認証で検索ページにアクセスできない | 既存ブラウザ（Edge）接続で SSO セッションを再利用 |
| Redmine / ローカル検索が新 Tool との共存で壊れる | 既存機能の回帰 | 結合テスト（P3-6）で全ソース同時動作を確認 |

---

## 6. Phase 4: ポータブル配布

> **ゴール**: インストーラなしで USB / ファイルサーバーからコピーして動作する

**詳細設計**: [portable_data_layout.md](./portable_data_layout.md) を参照

### 実装タスク一覧

- [ ] **P4-1**: データディレクトリ解決ロジックの実装
  - `main.ts` に `resolveDataDir()` を追加
  - `PORTABLE_EXECUTABLE_DIR` 環境変数で判定
  - SettingsStore, Logger, MetricsService に dataDir を渡す

- [ ] **P4-2**: ブラウザプロファイル解決ロジックの実装
  - `main.ts` に `resolveProfileDir()` を追加
  - ポータブル時: exe 同階層の `profiles/`
  - インストーラ時: デフォルト（変更なし）

- [ ] **P4-3**: electron-builder 設定の更新
  - `electron-builder.json5` に `portable` ターゲットを追加
  - `artifactName`: `SearchTool-Portable-${version}.${ext}`

- [ ] **P4-4**: ログローテーションの実装
  - Logger に `pruneOldLogs(maxAgeDays)` を追加
  - 起動時に 7 日超のログファイルを削除

- [ ] **P4-5**: ビルド・動作確認
  - `npm run build:win` で NSIS + portable の両方が生成されること
  - ポータブル exe を別ディレクトリにコピーして動作すること
  - `data/settings.json` が exe 同階層に生成されること

### Phase 4 の依存関係

```
Phase 1 完了（Electron 33 更新済み）
  └→ P4-1 (データディレクトリ)
  └→ P4-2 (プロファイルディレクトリ)
  └→ P4-3 (electron-builder設定)
  └→ P4-4 (ログローテーション)
       └→ P4-5 (ビルド・動作確認)
```

P4-1〜P4-4 は互いに独立しており、並行実装可能。

### Phase 4 の Definition of Done

- [ ] ポータブル exe がインストーラなしで動作する
- [ ] 設定・ログ・プロファイルが exe 同階層に保存される
- [ ] NSIS インストーラ版も引き続き動作する（回帰なし）
- [ ] 7 日超のログが起動時に自動削除される

### リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| USB メモリの書き込み速度 | ログ書き込みで遅延 | 非同期書き込み（既に Logger は async） |
| Windows のパス長制限（260文字） | 深いパスで動作不能 | データは exe 直下の浅い階層に配置 |
| 管理者権限なしで Edge が使えない | ブラウザ接続失敗 | 同梱 Chromium へのフォールバック |

---

## 7. Phase 5: 拡張（将来）

> **ゴール**: 追加機能で SearchTool の利便性を向上させる

### 5a. 自己修復メカニズム

全ソース共通の自己修復機能。サイト側の HTML 構造変更で固定セレクタが壊れた場合に、
playwright-mcp のアクセシビリティスナップショットを使って自動的に再抽出する。

**詳細設計**: [repair_prompts.md](./repair_prompts.md) を参照

- RepairTool の実装（`mastra/tools/repairTool.ts`）
  - `tool_interfaces.md` §3d に準拠
  - 修復戦略: セレクター変更 → ページ再読み込み → エスカレーション
  - リトライ上限: 通常1回 + 修復1回 = 最大2回
- 修復プロンプトの実装（`mastra/tools/repairPrompt.ts`）
  - スナップショット → LLM → 構造化 JSON の変換
  - Mastra Agent とは別の軽量 LLM 呼び出し（generateText）
- 全 SearchTool（SharePoint, InternalDocs, Teams）に修復フローを組み込み
  - ExtractTool の confidence が `low` → RepairTool を呼ぶ
  - RepairTool も失敗 → escalation メッセージを reasoning に含める

### 5b. MCP 対応による外部ツール連携

- SearchTool 自体を MCP サーバーとして公開
- 外部の Agent や Claude Code から検索機能を利用可能にする
- 各 Tool に `mcp.annotations` を追加（`tool_interfaces.md` §5 参照）

### 5c. 検索レシピのカスタマイズUI

- よく使う検索条件をプリセットとして保存
- `data/recipes/*.json` に保存（ポータブル対応済み）
- Settings 画面にレシピ管理タブを追加

### 5d. Redmine の責務分離化

- Phase 1-2 で確立した責務分離パターン（Navigation / Extract / Repair）を Redmine に適用
- RedmineExtractTool を作成し、v1 の固定セレクタ方式を置き換え
- NavigationTool, RepairTool は共通で再利用

---

## 8. 技術的リスクと対策

### 8a. Mastra v1 の Node.js 22.13+ 要件 vs Electron のバンドル Node バージョン

| 項目 | 詳細 |
|------|------|
| **問題** | `@mastra/core ^0.23` は Node.js 22.13+ を要求。Electron 30 は Node 20.x を内蔵 |
| **影響** | Mastra が Electron のメインプロセスで動作しない |
| **対策** | **Electron 33+ に更新**（Node 22.x 内蔵）。Phase 1 の前提タスクとして実施 |
| **代替案** | Mastra を別プロセス（sidecar）で動かす。ただし IPC 設計が複雑になるため非推奨 |
| **検証方法** | `process.versions.node` をログに出力し、22.13+ であることを確認 |

### 8b. SharePoint UI の変更頻度と自己修復の信頼性

| 項目 | 詳細 |
|------|------|
| **問題** | Microsoft が SharePoint の HTML 構造を変更すると固定セレクタが壊れる |
| **影響** | 検索結果が取得できなくなる |
| **対策** | Phase 2 の自己修復メカニズム。playwright-mcp のスナップショットは HTML 構造に依存しない |
| **限界** | ログインフローの変更には対応できない（手動対応が必要） |
| **監視** | 修復発動率をメトリクスに記録。閾値を超えたらアラート |

### 8c. ブラウザ接続の安定性（既存ブラウザ vs 同梱 Chromium）

| 項目 | 詳細 |
|------|------|
| **問題** | 既存ブラウザ（Edge/Chrome）への接続が不安定な場合がある |
| **影響** | 検索が実行できない、またはタイムアウト |
| **対策** | フォールバック順序: msedge → chrome → 同梱 chromium |
| **認証の課題** | 同梱 Chromium は SSO セッションを持たない。認証が必要なサイトではログインが必要 |
| **推奨** | 社内環境では Edge の利用を推奨（SSO / NTLM 認証を再利用できる） |

### 8d. playwright-mcp プロセスのライフサイクル

| 項目 | 詳細 |
|------|------|
| **問題** | v1 では検索ごとに playwright-mcp を spawn/kill している。オーバーヘッドが大きい |
| **影響** | 検索のレスポンスタイム悪化 |
| **対策案** | 長寿命の playwright-mcp プロセスを1つ起動し、複数検索で再利用する |
| **Phase 1 では** | v1 と同じ方式（毎回 spawn）で実装し、パフォーマンスが問題になったら改善 |
| **根拠** | YAGNI。まず動くものを作り、ボトルネックが確認されてから最適化 |

### 8e. Electron 33 への更新リスク

| 項目 | 詳細 |
|------|------|
| **問題** | Electron 30 → 33 で Breaking Changes がある可能性 |
| **影響** | 既存コードのコンパイルエラーまたはランタイムエラー |
| **対策** | Phase 1 の前提タスク（P0-1〜P0-5）で段階的に確認 |
| **確認事項** | Electron 31/32/33 の Breaking Changes リスト、vite-plugin-electron 互換性、electron-builder 互換性 |

---

## 9. 関連設計書

| ドキュメント | 内容 | Phase |
|-------------|------|-------|
| [tool_interfaces.md](./tool_interfaces.md) | Tool のインターフェース定義（Zod スキーマ、呼び出しフロー） | Phase 1-3 |
| [repair_prompts.md](./repair_prompts.md) | 自己修復メカニズム設計（修復判定基準、プロンプト雛形、実装箇所） | Phase 2 |
| [portable_data_layout.md](./portable_data_layout.md) | ポータブル配布のディレクトリレイアウト設計 | Phase 4 |
| [STATUS.md](./STATUS.md) | v1 の実装ステータス（95%完了） | 参考 |
| [issues.md](./issues.md) | v1 のタスクバックログ（T0-T9） | 参考 |

---

## Appendix: Phase ごとの変更ファイルマップ

### Phase 0（Electron 更新）

| ファイル | 変更内容 |
|----------|---------|
| `package.json` | electron, electron-builder, vite-plugin-electron バージョン更新 |

### Phase 1（SharePoint検索MVP）

| ファイル | 変更内容 |
|----------|---------|
| `shared/tool-contracts.ts` | **新規**: 共通型定義 |
| `mastra/tools/navigationTool.ts` | **新規**: ブラウザ操作 Tool |
| `mastra/tools/sharepointExtractTool.ts` | **新規**: スナップショット解析 Tool |
| `mastra/tools/sharepointSearchTool.ts` | **新規**: オーケストレーター Tool |
| `mastra/agent.ts` | **改修**: 新 Tool 構成に変更 |
| `mastra/tools/sharepointTool.ts` | **削除** |
| `mastra/tools/mcpClient.ts` | **改修**: sharepoint ルーティング削除 |
| `mcp-servers/sharepoint-search.server.ts` | **削除**（Phase 1 完了後） |
| `shared/settings.ts` | **改修**: browser.channel 追加 |

### Phase 2（社内ドキュメント検索）

| ファイル | 変更内容 |
|----------|---------|
| `mastra/tools/internalDocsExtractTool.ts` | **新規**: 社内ドキュメント抽出 Tool |
| `mastra/tools/internalDocsSearchTool.ts` | **新規**: 社内ドキュメント検索 Tool |
| `mastra/agent.ts` | **改修**: InternalDocsSearchTool 登録 |
| `mastra/tools/internalDocsTool.ts` | **削除** |
| `mastra/tools/mcpClient.ts` | **改修**: internalDocs ルーティング削除 |
| `mcp-servers/internal-docs-search.server.ts` | **削除**（Phase 2 完了後） |

### Phase 3（Teamsメッセージ検索 + Redmine + ローカル）

| ファイル | 変更内容 |
|----------|---------|
| `mastra/tools/teamsMessageExtractTool.ts` | **新規**: Teams メッセージ抽出 Tool |
| `mastra/tools/teamsMessageSearchTool.ts` | **新規**: Teams メッセージ検索 Tool |
| `mastra/agent.ts` | **改修**: TeamsMessageSearchTool 登録 |
| `mastra/tools/teamsTool.ts` | **削除** |
| `mastra/tools/mcpClient.ts` | **改修**: teams ルーティング削除 |
| `mcp-servers/teams-search.server.ts` | **削除**（Phase 3 完了後） |
| `mastra/tools/redmineTool.ts` | **維持**: v1 のまま動作確認 |
| `mcp-servers/redmine-ui.server.ts` | **維持**: v1 のまま動作確認 |
| `mastra/tools/localTool.ts` | **維持**: v1 のまま動作確認 |
| `mcp-servers/local-fs.server.ts` | **維持**: v1 のまま動作確認 |

### Phase 4（ポータブル配布）

| ファイル | 変更内容 |
|----------|---------|
| `main.ts` | **改修**: resolveDataDir(), resolveProfileDir() 追加 |
| `services/logger.ts` | **改修**: pruneOldLogs() 追加 |
| `electron-builder.json5` | **改修**: portable ターゲット追加 |
