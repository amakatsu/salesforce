FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# システムパッケージのインストール（openpyxl等で必要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY app.py .

# 親ディレクトリのwordモジュールをコピー
COPY ../word /app/word

# 環境変数のデフォルト設定（docker-compose.ymlで上書き可能）
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ポート公開
EXPOSE 8501

# ヘルスチェック
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Streamlitアプリの起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
