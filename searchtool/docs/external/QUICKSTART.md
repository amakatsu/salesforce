# SearchTool - クイックスタートガイド

最速で SearchTool を試すための手順です。

---

## ⚡ 5 分でスタート

### ステップ 1: 依存関係の確認

```bash
# Node.js のバージョン確認（18 以上が必要）
node --version

# ripgrep の確認
which rg
# なければインストール:
# sudo apt install ripgrep  # Ubuntu/Debian
# brew install ripgrep      # macOS
```

### ステップ 2: プロジェクトのセットアップ

```bash
cd /home/ec2-user/salesforce/searchtool/app

# npm パッケージのインストール（初回のみ）
npm install

# Playwright ブラウザのインストール（Web 検索を使う場合）
npx playwright install chromium
```

### ステップ 3: 環境変数の設定

```bash
# .env ファイルを作成（プロジェクトルートに）
cd /home/ec2-user/salesforce/searchtool
cat > .env <<'EOF'
# OpenAI API キー（AI 要約機能に必要）
OPENAI_API_KEY=sk-your-actual-api-key-here

# 使用するモデル（オプション、デフォルト: gpt-4o-mini）
MASTRA_MODEL_ID=openai/gpt-4o-mini
EOF
```

### ステップ 4: アプリの起動

```bash
cd app

# 開発モードで起動
npm run dev
```

---

## 🎯 初回設定（アプリ起動後）

### 1. 設定タブを開く

アプリが起動したら、上部のナビゲーションから「設定」タブをクリック。

### 2. ローカル検索の設定

**ルートディレクトリ**（1 行 1 パス）:

```
/home/ec2-user/projects
/home/ec2-user/documents
```

**除外パターン**（カンマ区切り）:

```
.git, node_modules, .venv, target, dist, build
```

### 3. Web 検索の設定（オプション）

使いたいサービスの URL を設定：

**Redmine URL**（1 行 1 URL、複数サイト対応）:

```
https://redmine.example.com
https://redmine2.example.com
```

**SharePoint URL**（1 行 1 URL、複数サイト対応）:

```
https://yourcompany.sharepoint.com/sites/docs
```

**Teams URL**（1 行 1 URL、複数チーム対応）:

```
https://teams.microsoft.com/...
```

**社内ドキュメント URL**:

```
https://docs.internal.example.com
```

### 4. ブラウザ設定（オプション）

ログイン状態を保持したい場合：

**User Data Dir**:

```
/home/ec2-user/.config/chromium
```

または

```
/home/ec2-user/.config/google-chrome
```

### 5. 制限設定（オプション）

デフォルトのままでも OK ですが、調整可能：

- **ローカル最大件数**: 200
- **Web 最大件数**: 50
- **タイムアウト（秒）**: 30
- **スクロール回数**: 5

### 6. 保存

「保存」ボタンをクリック。

---

## 🔍 検索を試す

### 1. 検索タブに戻る

上部のナビゲーションから「検索」タブをクリック。

### 2. キーワードを入力

例:

```
API 認証 エラー
```

または

```
React hooks
```

### 3. 検索実行

Enter キーを押すか、検索ボタンをクリック。

### 4. 結果を確認

タブで切り替え：

- **Mastra 要約** - AI による検索結果の要約
- **すべて** - 全ソースの統合結果
- **Local** - ローカルファイルの検索結果
- **Web** - Redmine/SharePoint/Teams/社内ドキュメントの結果

---

## 📊 統計を見る

「統計」タブをクリックすると、以下が表示されます：

- 総検索回数
- 平均処理時間
- ソース別総ヒット数
- 直近 10 件の検索履歴

---

## 🐛 トラブルシューティング

### "ripgrep (rg/rga) が見つかりません"

```bash
# ripgrep のインストール
sudo apt install ripgrep  # Ubuntu/Debian
brew install ripgrep      # macOS
```

### "検索キーワードを入力してください"

設定タブで「ルートディレクトリ」が空の場合に表示されます。
最低 1 つのパスを設定してください。

### "検索に失敗しました"

1. **ローカル検索の場合**:
   - ルートディレクトリのパスが正しいか確認
   - ripgrep がインストールされているか確認（`which rg`）

2. **Web 検索の場合**:
   - Playwright がインストールされているか確認
   - URL が正しいか確認
   - タイムアウト時間を増やす（60 秒など）

3. **AI 要約の場合**:
   - `.env` ファイルに `OPENAI_API_KEY` が設定されているか確認
   - API キーが有効か確認

### Playwright ブラウザが起動しない

```bash
# Chromium の再インストール
npx playwright install chromium
```

### ログインが必要な Web サイト

「User Data Dir」を設定すると、ブラウザのログイン状態が保持されます：

1. 通常のブラウザで対象サイトにログイン
2. ブラウザのプロファイルディレクトリを確認
3. そのパスを「User Data Dir」に設定

**Chrome/Chromium の場合**:

- Linux: `~/.config/chromium` または `~/.config/google-chrome`
- macOS: `~/Library/Application Support/Google/Chrome`
- Windows: `%LOCALAPPDATA%\Google\Chrome\User Data`

---

## 🚀 本番ビルド

開発が完了したら、配布用にビルド：

```bash
# Linux 用
npm run build:linux
# → release/1.0.0/SearchTool-Linux-1.0.0.AppImage

# Windows 用（Windows 環境で実行）
npm run build:win
# → release/1.0.0/SearchTool-Setup-1.0.0.exe
```

---

## 📝 便利なコマンド

```bash
# 型チェック
npm run typecheck

# リント
npm run lint

# 開発モード（ホットリロード）
npm run dev

# ビルド（すべてのプラットフォーム）
npm run build:all
```

---

## 🔗 関連ドキュメント

- **詳細な使い方**: [README.md](./README.md)
- **開発状況**: [STATUS.md](./STATUS.md)
- **プレゼン資料**: [PRESENTATION.md](./PRESENTATION.md)
- **実装バックログ**: [issues.md](./issues.md)

---

## ❓ よくある質問

### Q: AI 要約機能を使わずにローカル検索だけできますか？

A: はい、可能です。OpenAI API キーを設定しない場合、AI 要約は実行されず、Fallback 検索が動作します。検索結果は通常通り表示されます。

### Q: オフラインでも使えますか？

A: ローカル検索のみであれば、OpenAI API キー不要でオフライン使用可能です。Web 検索や AI 要約にはインターネット接続が必要です。

### Q: 検索結果はどこに保存されますか？

A: 検索結果自体は保存されませんが、以下が記録されます：

- ログ: `logs/app-YYYYMMDD.log`
- 設定: `~/.config/searchtool/settings.json`（Linux）
- メトリクス: メモリ内（アプリ終了で消去）

### Q: カスタムの検索ソースを追加できますか？

A: はい、MCP サーバーとして実装すれば追加可能です。詳細は開発者向けドキュメントを参照してください。

---
