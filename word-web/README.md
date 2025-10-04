# Excel単語照合ツール - Webインターフェース

ブラウザから簡単に利用できるExcel単語照合ツールです。既存の`word.py`を修正せずに、Webアプリケーションとして動作します。

## 特徴

- 🌐 **ブラウザから利用可能** - インストール不要、URLにアクセスするだけ
- 📁 **ドラッグ&ドロップ対応** - ファイルを簡単にアップロード
- 📊 **リアルタイムプレビュー** - 処理結果を即座に確認
- 💾 **デスクトップにダウンロード** - 結果をExcelファイルとして保存
- 🐳 **Docker対応** - 1コマンドで起動可能
- 🔒 **既存コード保護** - `word.py`は一切修正なし

## クイックスタート

### 前提条件

- Docker と Docker Compose がインストールされていること
- （オプション）`.env`ファイルでAPI設定を行うこと

### 起動方法

1. **リポジトリのルートディレクトリに移動**

```bash
cd /path/to/salesforce
```

2. **環境変数の設定（必要に応じて）**

`word-web/.env`ファイルを作成するか、既存の`.env`を利用:

```bash
# API設定（例）
OPENAI_BASE_URL=https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu
OPENAI_API_KEY=your-api-key-here
OPENAI_HEADERS_JSON={"api-key":"your-key","apim-user-id":"YOUR_ID"}

# プロキシ設定（必要な場合）
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080
```

3. **Docker Composeで起動**

```bash
cd word-web
docker-compose up -d
```

4. **ブラウザでアクセス**

```
http://localhost:8501
```

### 停止方法

```bash
docker-compose down
```

## 使い方

### 1. ファイルのアップロード

- **左側**: 画面項目定義ファイル（`*画面項目定義*.xlsx`）をアップロード
- **右側**: 単語名一覧ファイル（`*単語名一覧*.xlsx`）をアップロード

複数ファイルをまとめてアップロード可能です。

### 2. 設定の調整（オプション）

サイドバーから以下を設定できます：

- **画面項目定義の列名**: デフォルト「項目名称」
- **単語帳の列名**: デフォルト「論理名」
- **LLM設定**: Max Tokens、Temperature、類似度しきい値など

### 3. 照合実行

「🚀 照合実行」ボタンをクリック

### 4. 結果の確認とダウンロード

- **処理サマリ**: 完全一致/一部一致/一致なしの件数を表示
- **結果プレビュー**: 先頭10件をブラウザで確認
- **ダウンロード**: 「📥 結果をダウンロード」ボタンで`match_result.xlsx`を取得

## ディレクトリ構成

```
salesforce/
├── word/
│   └── word.py          # 既存のCLIツール（修正なし）
│
└── word-web/            # 新規作成
    ├── app.py           # Streamlitアプリ
    ├── Dockerfile       # Dockerイメージ定義
    ├── docker-compose.yml
    ├── requirements.txt
    └── README.md        # このファイル
```

## トラブルシューティング

### ポート8501が既に使用されている

`docker-compose.yml`のポート設定を変更:

```yaml
ports:
  - "8502:8501"  # 左側を変更
```

その後、`http://localhost:8502`でアクセス

### API接続エラー

1. `.env`ファイルの設定を確認
2. プロキシ設定が必要か確認
3. コンテナログを確認:

```bash
docker-compose logs -f word-web
```

### ファイルアップロードが失敗する

- ファイルサイズが大きすぎる場合、Streamlitのデフォルト制限（200MB）に引っかかる可能性があります
- `app.py`に以下を追加して制限を緩和:

```python
st.set_page_config(
    page_title="...",
    max_upload_size=500  # 500MBまで
)
```

## ローカル開発

Dockerを使わずに直接実行する場合:

```bash
cd word-web

# 依存パッケージのインストール
pip install -r requirements.txt

# Streamlitアプリの起動
streamlit run app.py
```

## ライセンス

既存の`word.py`と同じライセンスに従います。

## サポート

問題が発生した場合は、GitHubのIssueを作成してください。
