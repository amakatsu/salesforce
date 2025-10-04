# 開発支援ツール統合ポータル

開発効率を向上させる3つのツールを統合したWebポータルです。

## 🛠️ 統合ツール

### 📝 単語照合ツール
Excel単語帳との照合により、lowerCamelCase形式の物理名を自動提案します。

- ✅ 完全一致判定
- ✅ 未登録語検出
- ✅ LLM自動提案

### 🔍 ドメインチェックツール
ドメイン設計の整合性をチェックし、問題点を検出します。

- ✅ ドメイン提案: LLMが項目名を分析してドメイン候補を提案
- ✅ 整合性チェック: データ型・桁数の整合性をチェック
- ✅ 業務的意味の分析

### 🤖 PR-Agent
GitLab マージリクエストの自動レビューとコード品質チェックを実施します。

- ✅ コードレビュー
- ✅ 改善提案
- ✅ テスト提案
- ✅ コンテキスト切り替え（セキュリティ重視、パフォーマンス重視など）

## 📁 ディレクトリ構造

```
tools/
├── web/                    # Streamlit Webポータル
│   ├── app.py             # ホーム画面
│   ├── pages/             # 各ツールのUI
│   │   ├── word_matching.py
│   │   ├── domain_check.py
│   │   └── pr_agent.py
│   ├── Dockerfile
│   └── requirements.txt
├── word/                   # 単語照合ロジック
│   └── word.py
├── domain/                 # ドメインチェックロジック
│   └── domain_check.py
├── pr-agent/              # PR-Agentロジック
│   ├── pr.sh
│   └── prg/
└── docker-compose.yml     # Docker構成
```

## 🚀 起動方法

### 方法1: ローカル実行（Streamlit）

```bash
cd tools/web
streamlit run app.py
```

ブラウザで http://localhost:8501 にアクセス

### 方法2: Docker

```bash
cd tools

# イメージをビルド
docker build -t dev-tools-web -f web/Dockerfile .

# コンテナを起動
docker run -d \
  -p 8501:8501 \
  --name dev-tools-web \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e GITLAB_TOKEN=$GITLAB_TOKEN \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  dev-tools-web

# ログ確認
docker logs -f dev-tools-web

# 停止
docker stop dev-tools-web
docker rm dev-tools-web
```

## 🔑 環境変数

以下の環境変数を設定するか、各ツールの画面で入力してください：

### 単語照合ツール
- `OPENAI_API_KEY` - Azure OpenAI APIキー（オプション）
- ユーザID（画面で入力）

### ドメインチェックツール
- `OPENAI_API_KEY` - Azure OpenAI APIキー（オプション）
- ユーザID（画面で入力）

### PR-Agent
- `GITLAB_TOKEN` - GitLabパーソナルアクセストークン（オプション）
- `GEMINI_API_KEY` - Gemini APIキー（オプション）

### 環境変数ファイル

環境変数を`.env`ファイルに保存しておくと便利です：

```bash
# tools/.env
OPENAI_API_KEY=your_openai_key
GITLAB_TOKEN=your_gitlab_token
GEMINI_API_KEY=your_gemini_key
```

Dockerコンテナ起動時に `--env-file .env` オプションで読み込めます。

## 📝 必要な依存関係

### Python パッケージ

```bash
pip install -r web/requirements.txt
```

主要パッケージ：
- streamlit
- pandas
- openpyxl
- requests
- rapidfuzz

## 🎯 各ツールの使い方

### 単語照合ツール

1. サイドバーでAPIキーとユーザIDを入力
2. 画面項目定義ファイル（Excel）をアップロード
3. 単語名一覧ファイル（Excel）をアップロード
4. 「照合実行」ボタンをクリック
5. 結果をExcelでダウンロード

### ドメインチェックツール

1. サイドバーでAPIキーとユーザIDを入力
2. 対象一覧ファイル（Excel）をアップロード
3. ドメイン定義ファイル（Excel）をアップロード
4. テーブル定義ファイル（Excel）をアップロード
5. 実行モードを選択（ドメイン提案のみ/整合性チェックのみ/両方）
6. 「チェック実行」ボタンをクリック
7. 結果をExcelでダウンロード

### PR-Agent

1. サイドバーでGitLab TokenとGemini API Keyを入力
2. コマンドを選択（review/improve/describe/ask など）
3. コンテキスト設定を選択（セキュリティ重視/パフォーマンス重視など）
4. マージリクエストURLを入力
5. 「PR-Agent実行」ボタンをクリック
6. 結果がGitLabのMRページに投稿されます

## 🔧 トラブルシューティング

### Dockerビルドエラー

```bash
# キャッシュをクリアしてビルド
docker build --no-cache -t dev-tools-web -f web/Dockerfile .
```

### ポート競合

```bash
# ポート8501が使用中の場合、別のポートを使用
docker run -d -p 8502:8501 --name dev-tools-web dev-tools-web
# ブラウザで http://localhost:8502 にアクセス
```

### Pythonパスエラー

```bash
# PYTHONPATH を確認
echo $PYTHONPATH

# 必要に応じて設定
export PYTHONPATH=/path/to/tools:$PYTHONPATH
```

## 📚 ドキュメント

各ツールの詳細な使い方は、アプリケーション内の「使い方を見る」セクションを参照してください。

## 🐛 バグ報告・機能要望

問題が発生した場合や機能追加の要望がある場合は、イシューを作成してください。

## 📄 ライセンス

このプロジェクトは社内ツールとして開発されています。
