
# ---- Dockerfile ----
FROM python:3.11-slim

# 1) OSパッケージ（証明書・curlなど）を最低限
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# 2) PR-Agent をインストール
RUN pip install --no-cache-dir "pr-agent"

# 3) 実行ユーザ（root回避）
RUN useradd -m -u 10001 pragent
USER pragent

# 4) 作業ディレクトリ
WORKDIR /app

# 5) Webhook待受ポート
EXPOSE 8080

# 6) ヘルスチェック（軽いGET）
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8080/health || exit 1

# 7) 環境変数（必要なものは run 時に注入）
# - CONFIG.GIT_PROVIDER: gitlab / github など
# - GITLAB_TOKEN: GitLab PAT (scope: api)
# - GOOGLE_AI_STUDIO__GEMINI_API_KEY: Gemini APIキー
ENV CONFIG.GIT_PROVIDER=gitlab

# 8) サーバ起動（HTTP）
ENTRYPOINT ["pr-agent", "server", "--host", "0.0.0.0", "--port", "8080"]
