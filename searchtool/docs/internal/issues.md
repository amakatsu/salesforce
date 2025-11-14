# SearchTool: implementation backlog

- [x] **T0 - プロジェクト初期化**: electron-viteベースのReact/TS足場にMastra/Playwright依存を追加、`npm run typecheck`で静的検証済み。
- [x] **T1 - 設定保存（Zod+JSON）**: `src/shared/settings.ts`でスキーマ化し、`SettingsStore`+IPC+UIで永続化。preload経由でrendererからget/set可能。
- [x] **T2 - MCPサーバ(local.search)**: `src/main/mcp-servers/local-fs.server.ts`でrg/rgaを叩く `runLocalSearch` を実装し、MCPクライアントと検索サービスから利用可能。
- [x] **T3 - MCPサーバ(redmine.search)**: `playwright-mcp`経由でRedmine検索を走らせる`runRedmineSearch`を実装（MCP stdioクライアント + execute-codeでDOM抽出）。
- [x] **T4 - MCPブリッジ**: `mastra/tools/*` にMastraツールラッパーを実装し、`mcpClient`経由でlocal/redmine両方を呼び出せるようにした。
- [x] **T5 - Mastraエージェント**: `mastra/agent.ts`でMastra Agent + MCPツールを実行し、`searchService`が要約とヒット表を取得する実装に切り替え。
- [x] **T6 - IPC & UI仕上げ**: rendererでローカル/RedmineタブとMastra要約を実データで描画し、エラーハンドリング/進捗表示を追加。TypeScript型定義、スピナーアニメーション、Enter key対応、詳細エラーメッセージ実装済み。ビルド成功確認(156MB AppImage)。
- [x] **T7 - ログ＆メトリクス**: JSONLログ(`logs/app-YYYYMMDD.log`)出力とUIでの直近処理時間/件数表示。Logger/MetricsServiceクラス実装、IPC経由で統計画面に総検索回数/平均処理時間/総件数/直近10件の検索履歴を表示。ビルド成功確認。
- [x] **T9 - SharePoint/Teams/社内ドキュメント検索追加**: playwright-mcpを使用してSharePoint、Teams、社内ドキュメントサイトの検索を追加。自動検索欄検出機能実装。UIは「すべて」タブで統合表示、ソースバッジで区別。設定画面に各URLフィールド追加。**Redmine/SharePoint/Teamsは複数URL登録可能（複数行入力）、Promise.allSettledで並列検索実行。**
- [ ] **T8 - ビルド/配布**: `electron-builder`経由でWindows向けNSISセットアップ作成、E2E確認。
