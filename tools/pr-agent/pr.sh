#!/usr/bin/env bash
set -euo pipefail

# ==== 必須環境変数 ====
: "${GITLAB_TOKEN:?set GITLAB_TOKEN (GitLab PAT with api scope)}"
: "${GEMINI_API_KEY:?set GEMINI_API_KEY (Gemini API key)}"
: "${OPENAI_API_KEY:=}"  # 空でOK（OpenAIフォールバック抑止）

IMAGE="codiumai/pr-agent@sha256:526a22352c71d04e315ff739fde130d40e4da3bef7191cd02bd2eee3ef29d386"
MODEL_DEFAULT="gemini/gemini-2.0-flash"
LANG_DEFAULT="ja-JP"

usage() {
  cat <<'USAGE' >&2
Usage:
  pr.sh <command> <URL> [options]

<command>（OSSでCLI実行OKなものだけ）
  review               : 差分に日本語インライン指摘
  improve              : Apply suggestion付きの修正提案（YAML厳格）
  describe             : PRタイトル/本文を生成（コメント投稿）
  ask                  : PRに関する自由質問（-q 必須）
  ask_line             : 指定ファイル/行に関する質問（--file --line 必須）
  update_changelog     : CHANGELOG追記案
  generate_labels      : ラベル提案
  settings             : 有効設定ダンプ（-C で設定ファイル指定可）
  auto_review          : 自動レビュー実行
  similar_issue        : 類似Issue/PRを探す（<URL>は Issue URL ）
  add_docs             : ドキュメント追加案
  help_docs            : リポのドキュメントに基づくQ&A
  config               : 設定キーのプレビュー
  answer               : 汎用一言回答

<URL>
  review/improve/describe/ask/ask_line/update_changelog/generate_labels/settings/auto_review/help_docs/add_docs/config/answer:
    → MR URL（例）https://gitlab.com/<group>/<project>/-/merge_requests/<IID>
  similar_issue:
    → Issue URL（例）https://gitlab.com/<group>/<project>/-/issues/<IID>

[options]
  -q "TEXT"            : ask/answer/help_docs の質問文
  --file PATH          : ask_line 用の相対パス
  --line N             : ask_line 用の行番号
  -n NUM               : improve の提案数（既定 10）
  -L NUM               : review のインライン上限（既定 30）
  -C PATH              : 設定ファイル（例 ./.pr-agent/configuration.toml）
  --model NAME         : 例 gemini/gemini-2.5-pro（既定 gemini/gemini-2.0-flash）
  --exclude JSON       : 除外globs JSON（例 '["**/*.png","**/yarn.lock"]')
  -h|--help            : ヘルプ

例:
  ./pr.sh review  https://gitlab.com/jenkins245/one/-/merge_requests/1
  ./pr.sh improve https://gitlab.com/jenkins245/one/-/merge_requests/1 -n 8
  ./pr.sh ask     https://gitlab.com/jenkins245/one/-/merge_requests/1 -q "後方互換リスクは？"
  ./pr.sh ask_line https://gitlab.com/jenkins245/one/-/merge_requests/1 --file app/remix-app/one/server.ts --line 120 -q "改善案は？"
  ./pr.sh similar_issue https://gitlab.com/<g>/<p>/-/issues/1
USAGE
}

CMD="${1:-}"; shift || true
URL="${1:-}"; [[ -n "${URL:-}" ]] && shift || true

MODEL="$MODEL_DEFAULT"
LANG="$LANG_DEFAULT"
NUM_SUGG=10
INLINE_LIMIT=30
CONFIG_PATH=""
QUESTION=""
EXCLUDE_GLOBS=""
ASK_FILE=""
ASK_LINE=""

INSTR=$'YAMLのみ。トップレベルは suggestions。各要素は file,start_line,end_line,replacement,note 必須。\nreplacement は複数行リテラル(|)でコードのみ（```、//、/* */ 禁止）。先頭が単なるハイフン(-)の行は作らない。説明は note に日本語で簡潔に。'

while (( "$#" )); do
  case "$1" in
    -q) QUESTION="${2:-}"; shift 2 ;;
    -n) NUM_SUGG="${2:-}"; shift 2 ;;
    -L) INLINE_LIMIT="${2:-}"; shift 2 ;;
    -C) CONFIG_PATH="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --exclude) EXCLUDE_GLOBS="${2:-}"; shift 2 ;;
    --file) ASK_FILE="${2:-}"; shift 2 ;;
    --line) ASK_LINE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1;;
  esac
done

[[ -z "$CMD" || -z "$URL" ]] && { usage; exit 1; }

common_env=(
  -e CONFIG__GIT_PROVIDER=gitlab
  -e GITLAB__URL="https://gitlab.com"
  -e GITLAB__PERSONAL_ACCESS_TOKEN="$GITLAB_TOKEN"
  -e GITLAB__AUTH_TYPE="oauth_token"
  -e GEMINI_API_KEY="$GEMINI_API_KEY"
  -e GOOGLE_AI_STUDIO__GEMINI_API_KEY="$GEMINI_API_KEY"
  -e OPENAI_API_KEY="$OPENAI_API_KEY"
)

flags=(
  --config.model="$MODEL"
  --config.fallback_models='["'"$MODEL"'"]'
  --config.response_language="$LANG"
  --ask.allow_repo_context=true
)

[[ -n "$EXCLUDE_GLOBS" ]] && flags+=( --filters.exclude_globs="$EXCLUDE_GLOBS" )
config_flag=()
[[ -n "$CONFIG_PATH" ]] && config_flag=(-config_path="$CONFIG_PATH")

run_mr_cmd() {
  docker run --rm "${common_env[@]}" "$IMAGE" --pr_url "$URL" "$@"
}
run_issue_cmd() {
  docker run --rm "${common_env[@]}" "$IMAGE" --issue_url "$URL" "$@"
}

case "$CMD" in
  review)
    run_mr_cmd review \
      "${flags[@]}" \
      --pr_reviewer.inline_code_comments=true \
      --pr_reviewer.inline_comments_limit="$INLINE_LIMIT" \
      --pr_reviewer.file_size_limit_kb=200 \
      "${config_flag[@]}"
    ;;
  improve)
    run_mr_cmd improve \
      "${flags[@]}" \
      --pr_code_suggestions.commitable_code_suggestions=true \
      --pr_code_suggestions.num_code_suggestions="$NUM_SUGG" \
      --pr_code_suggestions.extra_instructions="$INSTR"
    ;;
  describe)
    run_mr_cmd describe \
      "${flags[@]}" \
      --pr_description.publish_description_as_comment=true \
      "${config_flag[@]}"
    ;;
  ask)
    [[ -z "$QUESTION" ]] && { echo "ask requires -q \"TEXT\"" >&2; exit 1; }
    docker run --rm "${common_env[@]}" "$IMAGE" \
      --pr_url "$URL" ask "$QUESTION" \
      "${flags[@]}"
    ;;
  ask_line)
    [[ -z "$QUESTION" || -z "$ASK_FILE" || -z "$ASK_LINE" ]] && {
      echo "ask_line requires --file PATH --line N and -q \"TEXT\"" >&2; exit 1; }
    docker run --rm "${common_env[@]}" "$IMAGE" \
      --pr_url "$URL" ask_line --file "$ASK_FILE" --line "$ASK_LINE" "$QUESTION" \
      "${flags[@]}"
    ;;
  update_changelog|generate_labels|auto_review|help_docs|add_docs|config|answer|settings)
    # similar_issue 以外は MR URL 前提（settings は configファイル指定あれば付与）
    extra=()
    [[ "$CMD" == "settings" && -n "$CONFIG_PATH" ]] && extra+=("${config_flag[@]}")
    if [[ "$CMD" == "answer" || "$CMD" == "help_docs" ]]; then
      [[ -z "$QUESTION" ]] && { echo "$CMD requires -q \"TEXT\"" >&2; exit 1; }
      run_mr_cmd "$CMD" "$QUESTION" "${flags[@]}" "${extra[@]}"
    else
      run_mr_cmd "$CMD" "${flags[@]}" "${extra[@]}"
    fi
    ;;
  similar_issue)
    run_issue_cmd similar_issue "${flags[@]}"
    ;;
  *)
    echo "Unsupported command: $CMD" >&2; usage; exit 1 ;;
esac
