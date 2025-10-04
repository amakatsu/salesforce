# tools/web/Dockerfile
# 開発支援ツール統合Webポータル
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# システムパッケージのインストール
# curl: HEALTHCHECK用 / ca-certificates: HTTPS用
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ビルドコンテキストは tools/ ディレクトリ
COPY web/requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Webアプリケーションファイルをコピー
COPY web/app.py /app/app.py
COPY web/pages /app/pages

# バックエンドロジックをコピー
COPY word /app/word
COPY domain /app/domain
COPY pr-agent /app/pr-agent

# Pythonパスを設定（tools/配下からインポートできるように）
ENV PYTHONPATH=/app:$PYTHONPATH

# Streamlit設定
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
