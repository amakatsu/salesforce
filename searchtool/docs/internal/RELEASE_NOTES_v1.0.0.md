# SearchTool v1.0.0 リリースノート

**リリース日**: 2025-11-14

---

## 🎉 主な新機能

### 1. 設定画面からのAPIキー登録 🔑

**環境変数不要でOpenAI APIキーを設定可能になりました！**

- **設定画面で直接入力**: 「AI設定」セクションからAPIキーを登録
- **パスワード形式**: 入力内容が表示されないセキュアな入力欄
- **即座に有効化**: 保存すると即座にAI要約機能が使用可能

**使い方**:
1. アプリを起動
2. 「設定」タブを開く
3. 「OpenAI API キー」欄に `sk-...` を入力
4. 「設定を保存」ボタンをクリック

**メリット**:
- 環境変数の設定が不要
- 非技術者でも簡単に設定可能
- 複数ユーザーで異なるAPIキーを使用可能

### 2. AIモデルIDの選択 🤖

**使用するAIモデルを設定画面から選択可能になりました！**

- **デフォルト**: `openai/gpt-4o-mini`（コスト効率重視）
- **高精度**: `openai/gpt-4o`（品質重視）
- **低コスト**: `openai/gpt-3.5-turbo`（速度重視）

**使い方**:
1. 「設定」タブの「AI モデル ID」欄に入力
2. 例: `openai/gpt-4o`, `gpt-4o-mini` など
3. 「設定を保存」ボタンをクリック

**優先順位**:
1. 設定画面で入力した値
2. 環境変数 `MASTRA_MODEL_ID`
3. デフォルト値（`openai/gpt-4o-mini`）

### 3. Windows ビルド対応 💻

**Windowsマシンで実行可能なインストーラーをビルドできるようになりました！**

- **NSIS インストーラー**: Windowsの標準的なセットアップウィザード
- **カスタムインストール**: インストール先を選択可能
- **アンインストール対応**: データ保持オプション付き

**ビルド方法**:
```bash
# Windowsマシンで実行
npm run build:win
```

**生成ファイル**:
```
release/1.0.0/SearchTool-Windows-1.0.0-Setup.exe
```

詳細は [WINDOWS_BUILD.md](./WINDOWS_BUILD.md) を参照してください。

---

## 📊 技術詳細

### 変更されたファイル

| ファイル | 変更内容 |
|---------|---------|
| `src/shared/settings.ts` | `ai` オブジェクト追加（`apiKey`, `modelId`） |
| `src/renderer/components/Settings.tsx` | AI設定セクション追加、UI改善 |
| `src/main/mastra/agent.ts` | 設定からAPIキーとモデルIDを読み込むロジック実装 |
| `electron-builder.json5` | Windows NSIS設定確認・調整 |

### 設定ファイルスキーマ

**新しいフィールド**:

```json
{
  "ai": {
    "apiKey": "",
    "modelId": "openai/gpt-4o-mini"
  }
}
```

**保存場所**:
- Linux: `~/.config/searchtool/settings.json`
- Windows: `%APPDATA%\searchtool\settings.json`

### 互換性

- **後方互換**: 既存の設定ファイルは自動的に新しいスキーマに対応
- **環境変数**: 引き続き使用可能（設定画面の値が優先）

---

## 🔒 セキュリティに関する注意

⚠️ **重要**: APIキーは設定ファイルに**平文**で保存されます。

### 保存場所

- **Linux**: `~/.config/searchtool/settings.json`
- **Windows**: `%APPDATA%\searchtool\settings.json`

### セキュリティ対策

✅ **実施済み**:
- ファイルシステムのパーミッションで保護
- ネットワーク経由での送信なし（ローカルファイルのみ）
- パスワード形式の入力欄（表示されない）

⚠️ **今後の対応予定**:
- v1.1.0: APIキーの暗号化対応
- v1.2.0: マスターパスワードによる保護

### 推奨事項

1. **個人使用**: 問題なし（自分のマシンのみ）
2. **共有PC**: 注意が必要（他のユーザーがファイルを読める可能性）
3. **企業利用**: 管理者と相談してください

---

## 📦 ダウンロード

### Linux

```bash
# ビルド
npm run build:linux

# 実行
./release/1.0.0/SearchTool-Linux-1.0.0.AppImage
```

**サイズ**: 156 MB

### Windows

**要件**: Windowsマシンが必要

```bash
# ビルド
npm run build:win

# インストーラーを実行
./release/1.0.0/SearchTool-Windows-1.0.0-Setup.exe
```

**サイズ**: 約 160 MB

---

## 🐛 既知の問題

1. **Windows環境でのビルドテストが未実施**
   - Linux環境でビルド設定を確認済み
   - Windowsマシンでのテストが必要

2. **APIキーの暗号化が未実装**
   - v1.1.0で対応予定
   - 現時点では平文で保存

3. **設定画面でのAPIキー検証が最低限**
   - 形式チェックのみ
   - 実際の有効性は検索実行時に確認

---

## 🔜 今後の予定

### v1.1.0 (次期バージョン)

- APIキーの暗号化対応
- 設定のインポート/エクスポート
- APIキー有効性の即座チェック

### v1.2.0

- マスターパスワード機能
- 複数APIキーの管理
- プロキシ設定対応

### v1.3.0

- 検索履歴の永続化
- ブックマーク機能
- 全文プレビュー機能

---

## 📚 ドキュメント

### 新規追加

- [CHANGELOG.md](./CHANGELOG.md) - 変更履歴
- [WINDOWS_BUILD.md](./WINDOWS_BUILD.md) - Windowsビルドガイド
- [RELEASE_NOTES_v1.0.0.md](./RELEASE_NOTES_v1.0.0.md) - このファイル

### 更新

- [README.md](./README.md) - APIキー設定手順を更新
- [QUICKSTART.md](./QUICKSTART.md) - 初回セットアップ手順を更新
- [STATUS.md](./STATUS.md) - 開発状況を更新

---

## 🙏 謝辞

SearchTool v1.0.0 をご利用いただきありがとうございます！

フィードバックやバグ報告は [Issues](https://github.com/your-repo/searchtool/issues) までお願いします。

---

## 📞 サポート

問題が発生した場合は、以下のドキュメントを参照してください：

- [README.md](./README.md) - 詳細な使い方
- [QUICKSTART.md](./QUICKSTART.md) - クイックスタート
- [STATUS.md](./STATUS.md) - 開発状況
- [WINDOWS_BUILD.md](./WINDOWS_BUILD.md) - Windowsビルド

---

**Happy Searching! 🔍**

---
