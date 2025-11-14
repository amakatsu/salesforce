# Changelog

All notable changes to SearchTool will be documented in this file.

---

## [1.0.0] - 2025-11-13

### Added - 新機能

#### 🔑 APIキーの設定画面対応

- **設定画面からOpenAI APIキーを登録可能に**
  - パスワード形式の入力欄
  - 環境変数不要で使用可能
  - 設定ファイルに暗号化せずに保存（ローカル環境のみ）

- **AIモデルIDの設定画面対応**
  - デフォルト: `openai/gpt-4o-mini`
  - その他のモデルも選択可能（gpt-4o, gpt-3.5-turbo等）

#### 💻 Windowsビルド対応

- **NSISインストーラー生成対応**
  - `npm run build:win` コマンドでビルド可能
  - Windows x64向けセットアップファイル生成
  - インストールディレクトリの選択可能
  - アンインストール時にデータ保持オプション

### Changed - 変更

#### 🔧 設定の優先順位

APIキーとモデルIDの読み込み優先順位：

1. 設定画面で入力した値
2. 環境変数（`OPENAI_API_KEY`, `MASTRA_MODEL_ID`）
3. デフォルト値（モデルIDのみ: `openai/gpt-4o-mini`）

#### 🎨 設定画面のUI改善

- AI設定セクションを最上部に配置
- ローカル検索設定、Web検索ソース、制限設定をセクション分け
- 各入力欄にヘルプテキストを追加

### Technical Details - 技術詳細

#### 変更されたファイル

1. **`src/shared/settings.ts`**
   - `ai` オブジェクトを追加（`apiKey`, `modelId`）
   - スキーマ検証に対応

2. **`src/renderer/components/Settings.tsx`**
   - AI設定セクションを追加
   - APIキー入力欄（パスワード形式）
   - モデルID入力欄

3. **`src/main/mastra/agent.ts`**
   - `ensureAgent()` を `ensureAgent(settings: AppSettings)` に変更
   - `resolveModelConfig()` を `resolveModelConfig(settings: AppSettings)` に変更
   - 設定からAPIキーとモデルIDを読み込むロジックを実装
   - APIキー変更時にエージェントキャッシュをクリア

4. **`electron-builder.json5`**
   - Windows NSIS設定を確認・調整
   - `oneClick: false` でカスタムインストールを有効化

### Build Information - ビルド情報

- **Linux AppImage**: 156MB (正常にビルド完了)
- **Windows NSIS**: 設定済み（Windowsマシンでビルド可能）
- **TypeScript**: エラーなし
- **Vite**: ビルド成功

### Migration Guide - 移行ガイド

既存ユーザー向け：

1. **環境変数からの移行**
   ```bash
   # 以前: .envファイルにAPIキーを設定
   OPENAI_API_KEY=sk-xxx

   # 今後: アプリの設定画面から入力可能
   # （環境変数も引き続き使用可能）
   ```

2. **設定ファイルの互換性**
   - 既存の設定ファイルは自動的に新しいスキーマに対応
   - `ai.apiKey` と `ai.modelId` が未設定の場合はデフォルト値が使用される

### Security Note - セキュリティに関する注意

⚠️ **重要**: APIキーは設定ファイルに平文で保存されます。

- 保存場所:
  - Linux: `~/.config/searchtool/settings.json`
  - Windows: `%APPDATA%\searchtool\settings.json`

- セキュリティ対策:
  - ファイルシステムのパーミッションで保護
  - ネットワーク経由での送信なし（ローカルファイルのみ）
  - 今後のバージョンで暗号化を検討

### Known Issues - 既知の問題

- Windows環境でのビルドテストが未実施
- APIキーの暗号化が未実装
- 設定画面でのAPIキー入力時の検証が最低限

### Next Steps - 今後の予定

- v1.1.0: APIキーの暗号化対応
- v1.2.0: 設定のインポート/エクスポート機能
- v1.3.0: プロキシ設定対応

---

## Contributing

機能リクエストやバグ報告は [issues](https://github.com/your-repo/searchtool/issues) まで。

---
