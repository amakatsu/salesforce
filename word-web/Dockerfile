# word-web/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# curl: HEALTHCHECK用 / ca-certificates: HTTPS用 / git: PR-Agent用
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

# ← ここがポイント：ビルドコンテキストは「リポジトリ直下」なのでパスは word-web/...
COPY word-web/requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY word-web/app.py /app/app.py
COPY word-web/usage_tracker.py /app/usage_tracker.py
COPY word-web/.streamlit /app/.streamlit
COPY word-web/pages /app/pages
COPY word /app/word

# .envファイルをコピー（本番では環境変数で設定するため、ローカル開発用）
COPY .env /app/.env

ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
