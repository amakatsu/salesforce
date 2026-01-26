#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import sys
import os
import json
import importlib
import uuid
from pathlib import Path
from dotenv import load_dotenv
from streamlit.runtime.scriptrunner import get_script_run_ctx

# .envファイルを読み込み
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# pr_agent パッケージを確実に読み込む（同名ページとの衝突回避）
page_dir = Path(__file__).parent
page_dir_str = str(page_dir)
if page_dir_str in sys.path:
    sys.path.remove(page_dir_str)

try:
    real_pr_agent_pkg = importlib.import_module("pr_agent")
    sys.modules["pr_agent"] = real_pr_agent_pkg
except ImportError:
    real_pr_agent_pkg = None

# ローカルコンポーネントのインポート用にページディレクトリを再度末尾に追加
sys.path.append(page_dir_str)

# バックエンドモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from word.pr_agent import (
    PRAgentRunner,
    ConfigManager,
    Logger,
    UrlValidator,
    ConfigRepository,
)
from word.pr_agent.excel_validator import ExcelSpecValidator

# トラッキングをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from pages.util.usage_tracker import track_usage

# PR-Agentモジュールをインポート
from pr_agent_components.constants import (
    MODAL_STATE_KEY, INPUT_METHOD_KEY,
    COMMAND_DESCRIPTIONS, COMMAND_SECTION_MAP,
    GEMINI_MODELS, AI_PROVIDERS
)
from pr_agent_components.config_editor import config_editor_modal
from pr_agent_components.ui_helpers import (
    render_result_summary, close_modal, render_page_header,
    render_usage_guide, apply_sidebar_styles, render_page_footer
)


# =============================================================================
# ヘルパー関数
# =============================================================================

def _render_openai_config():
    """OpenAI設定を表示"""
    headers_json = os.getenv("OPENAI_HEADERS_JSON", "{}")
    try:
        headers_dict = json.loads(headers_json)
        default_api_key = headers_dict.get("api-key", "")
        default_user_id = headers_dict.get("apim-user-id", "")
    except:
        default_api_key = ""
        default_user_id = ""

    api_key = st.text_input(
        "OpenAI APIキー",
        value=default_api_key,
        type="password",
        help="OpenAI APIのキーを入力してください"
    )

    user_id = st.text_input(
        "ユーザID",
        value=default_user_id,
        help="APIユーザIDを入力してください"
    )

    return api_key, user_id


def _render_gemini_config():
    """Gemini設定を表示"""
    api_key = st.text_input(
        "Gemini APIキー",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Google Gemini APIのキーを入力してください"
    )

    gemini_model = st.selectbox(
        "Geminiモデル",
        GEMINI_MODELS,
        help="使用するGeminiモデルを選択"
    )

    return api_key, gemini_model


def _build_config_options(config_repo):
    """設定オプションを構築"""
    config_options = {"デフォルト": None}
    config_descriptions = {"デフォルト": "標準的なコードレビュー設定（common.tomlのみ使用）"}

    for info in config_repo.list_configs():
        config_options[info.name] = str(info.path)
        config_descriptions[info.name] = _extract_description(info.path)

    return config_options, config_descriptions


def _extract_description(path):
    """設定ファイルから説明を抽出"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') and line not in ['#', '# =============================================================================']:
                    desc = line.lstrip('# ').strip()
                    if desc and not desc.startswith('='):
                        return desc
            return Path(path).stem
    except:
        return Path(path).stem


def _render_advanced_settings():
    """詳細設定を表示"""
    debug_level = 1
    verbosity_level = 2
    gitlab_url = None
    custom_prompt = ""
    with st.expander("🔧 詳細設定", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔍 ログレベル")
            debug_level = st.selectbox(
                "ログ出力レベル",
                options=[0, 1, 2],
                index=1,
                format_func=lambda x: {0: "エラーのみ", 1: "標準（推奨）", 2: "詳細"}[x],
                help="0:エラーのみ / 1:進捗情報 / 2:デバッグ詳細"
            )
            verbosity_level = min(debug_level, 2)
            st.caption("※ Verbosityは常にHigh (2) で固定されます。")

        with col2:
            st.markdown("#### 🌐 GitLab URL")
            default_gitlab_url = os.getenv("GITLAB_URL", "")
            gitlab_url = st.text_input(
                "GitLab URL（任意）",
                value=default_gitlab_url,
                placeholder="例: https://gitlab.example.com",
                help="通常はMR URLから自動抽出されます"
            )

        if gitlab_url:
            normalized_url = UrlValidator.normalize_gitlab_url(gitlab_url)
            if UrlValidator.validate_gitlab_url(normalized_url):
                gitlab_url = normalized_url
            else:
                st.error("❌ 無効なGitLab URL")
                gitlab_url = None

        custom_prompt = st.text_area(
            "📝 カスタムプロンプト（任意）",
            placeholder="例: セキュリティ脆弱性を重点的にチェック",
            height=80,
            help="レビューに適用する追加の指示"
        )

    if st.session_state.get("spec_include_in_prompt") and st.session_state.get("spec_prompt_text"):
        spec_prompt = st.session_state["spec_prompt_text"]
        if spec_prompt not in custom_prompt:
            custom_prompt = f"{custom_prompt}\n\n{spec_prompt}" if custom_prompt else spec_prompt
    verbosity_level = 2
    return debug_level, verbosity_level, gitlab_url, custom_prompt


def _render_excel_spec_validator():
    """Excel仕様チェックUI"""
    st.markdown("### 📄 仕様チェック (Excel)")
    st.caption(
        "仕様Excelをアップロードすると、指定した列に書かれている内容を読み取り、"
        "その情報をPR-Agentのレビュー指示（観点）に取り込みます。"
    )

    required_cols = st.text_input(
        "必須列（カンマ区切り）",
        value=st.session_state.get("excel_required_cols", "仕様ID,タイトル,対象ファイル"),
        key="excel_required_cols",
        help=(
            "仕様Excelに必ず含めたい列名を指定します（例: 仕様ID, タイトル, 対象ファイル）。"
            "ここで指定した列名はPR-Agentのカスタムプロンプトにも観点として組み込まれ、"
            "レビュー時に仕様との整合性を確認する指示として扱われます。"
        ),
    )

    uploaded_specs = st.file_uploader(
        "仕様Excelファイル (複数可)",
        type=["xls", "xlsx"],
        accept_multiple_files=True,
        key="excel_spec_files",
    )

    include_specs = st.checkbox(
        "PR-Agentレビューに仕様チェック結果を取り込む",
        value=st.session_state.get("spec_include_in_prompt", True),
        key="spec_include_in_prompt",
    )

    cols = [c.strip() for c in required_cols.split(",") if c.strip()]
    validator = ExcelSpecValidator(required_columns=cols)

    check_button = st.button(
        "仕様チェックを実行",
        type="primary",
        disabled=not uploaded_specs,
        use_container_width=True,
    )

    if check_button and uploaded_specs:
        with st.spinner("仕様ファイルを解析しています..."):
            results = validator.validate_files(uploaded_specs)
        st.session_state["excel_validator_results"] = results
        st.session_state["spec_prompt_text"] = _build_spec_prompt(results, cols)
        st.success("仕様チェックが完了しました")

    results = st.session_state.get("excel_validator_results")
    if results:
        for result in results:
            st.markdown(f"**{result.filename}**")
            for summary in result.sheet_summaries:
                issues = []
                if summary.empty:
                    issues.append("シートが空です")
                if summary.missing_required_columns:
                    missing = ", ".join(summary.missing_required_columns)
                    issues.append(f"不足列: {missing}")
                issue_text = "\n".join(issues) if issues else "OK"
                with st.expander(f"📑 {summary.name} — {summary.rows}行 / {summary.columns}列", expanded=bool(issues)):
                    if issues:
                        st.warning(issue_text)
                    else:
                        st.success("問題は検出されませんでした")

        if st.session_state.get("spec_prompt_text") and include_specs:
            st.info(
                "PR-Agentのカスタムプロンプトへ、アップロードした仕様内容を要約した指示を自動追加します。"
                "レビュー結果に仕様との整合性コメントが含まれやすくなります。"
            )


def _build_spec_prompt(results, required_cols):
    lines = ["# Excel Specification Checks"]
    for result in results:
        lines.append(f"- File: {result.filename}")
        for summary in result.sheet_summaries:
            if summary.empty and summary.rows == 0:
                continue
            desc = f"  - Sheet {summary.name}: {summary.rows} rows / {summary.columns} cols"
            if summary.missing_required_columns:
                desc += f" (missing: {', '.join(summary.missing_required_columns)})"
            lines.append(desc)
    if required_cols:
        lines.append("Required columns considered: " + ", ".join(required_cols))
    return "\n".join(lines)



def _render_mr_input(input_method, gitlab_token, gitlab_url):
    """MR入力UIを表示"""
    pr_url = ""

    if input_method == "URLを直接入力":
        pr_url = st.text_input(
            "MR URL",
            placeholder="https://gitlab.com/group/project/-/merge_requests/1",
            help="レビュー対象のマージリクエストURL"
        )

        if pr_url:
            if UrlValidator.validate_pr_url(pr_url):
                st.success("✅ 有効なMR/PR URL")
            else:
                st.error("❌ 無効なMR/PR URLです")
    else:
        pr_url = _render_project_selector(gitlab_token)

    return pr_url


def _render_project_selector(gitlab_token):
    """プロジェクト選択UIを表示"""
    import requests
    import re
    import urllib.parse

    project_url = st.text_input(
        "プロジェクトURL",
        placeholder="https://gitlab.example.com/group/project",
        help="GitLabプロジェクトのURL"
    )

    pr_url = ""

    if project_url and gitlab_token:
        try:
            match = re.match(r'(https?://[^/]+)/(.+)', project_url.rstrip('/'))
            if match:
                gitlab_base_url = match.group(1)
                project_path = match.group(2)
                encoded_project = urllib.parse.quote(project_path, safe='')

                headers = {"PRIVATE-TOKEN": gitlab_token}
                api_url = f"{gitlab_base_url}/api/v4/projects/{encoded_project}/merge_requests"

                with st.spinner("MR一覧を取得中..."):
                    response = requests.get(
                        api_url, headers=headers,
                        params={"state": "opened", "order_by": "updated_at", "sort": "desc"}
                    )

                if response.status_code == 200:
                    mrs = response.json()
                    if mrs:
                        mr_options = {
                            f"!{mr['iid']} - {mr['title']} (by {mr['author']['name']})": mr['web_url']
                            for mr in mrs
                        }
                        selected_label = st.selectbox(
                            "マージリクエストを選択",
                            options=list(mr_options.keys()),
                            help="レビューしたいMRを選択してください"
                        )
                        pr_url = mr_options[selected_label]

                        # MR詳細表示
                        selected_mr = next(mr for mr in mrs if mr['web_url'] == pr_url)
                        with st.expander("📋 MR詳細", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**タイトル**: {selected_mr['title']}")
                                st.write(f"**作成者**: {selected_mr['author']['name']}")
                                st.write(f"**ターゲット**: {selected_mr['target_branch']}")
                            with col2:
                                st.write(f"**ソース**: {selected_mr['source_branch']}")
                                st.write(f"**作成日**: {selected_mr['created_at'][:10]}")
                                st.write(f"**更新日**: {selected_mr['updated_at'][:10]}")
                    else:
                        st.info("このプロジェクトにはオープンなMRがありません")
                else:
                    st.error(f"❌ MR一覧の取得に失敗しました: {response.status_code}")
            else:
                st.warning("⚠️ プロジェクトURLにはプロジェクトパスが必要です")
        except Exception as e:
            st.error(f"エラー: {str(e)}")
    elif project_url and not gitlab_token:
        st.warning("⚠️ GitLab Tokenを入力してください")

    return pr_url


def _render_execute_buttons(gitlab_token, api_key, user_id, pr_url, ai_provider,
                            pr_command, question, gemini_model, config_path, custom_prompt,
                            selected_config, debug_level, verbosity_level, gitlab_url, runtime_config_manager):
    """実行ボタンを表示"""
    # 実行状態の初期化
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'execute_params' not in st.session_state:
        st.session_state.execute_params = None
    if 'log_text' not in st.session_state:
        st.session_state.log_text = ""
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

    # ボタン有効/無効判定
    if ai_provider == "Gemini":
        button_disabled = not (gitlab_token and api_key and pr_url)
    else:
        button_disabled = not (gitlab_token and api_key and user_id and pr_url)

    if pr_command == "ask":
        button_disabled = button_disabled or not question

    button_disabled = button_disabled or st.session_state.is_running

    if st.session_state.is_running and not st.session_state.execute_params:
        st.session_state.is_running = False

    # ボタン表示
    col_execute1, col_execute2 = st.columns(2)

    with col_execute1:
        preview_button = st.button("📋 プレビュー実行（投稿しない）", use_container_width=True, disabled=button_disabled)

    with col_execute2:
        execute_button = st.button("🚀 実行して投稿", type="primary", use_container_width=True, disabled=button_disabled)

    # ボタン押下時の処理
    if preview_button or execute_button:
        is_preview_mode = preview_button
        st.session_state.pop(MODAL_STATE_KEY, None)

        # バリデーション
        if not gitlab_token or not api_key:
            st.error("❌ GitLab TokenとAPIキーを入力してください")
        elif ai_provider == "OpenAI (Azure)" and not user_id:
            st.error("❌ OpenAI (Azure)にはユーザIDが必要です")
        elif not pr_url:
            st.error("❌ MR URLを入力してください")
        elif pr_command == "ask" and not question:
            st.error("❌ askコマンドには質問内容が必要です")
        else:
            mode_label = "プレビュー実行" if is_preview_mode else "実行して投稿"
            track_usage(action=f"{mode_label}ボタン押下", tool_name="PR-Agent", username=f"{pr_command}コマンド")

            st.session_state.log_text = ""
            st.session_state.last_result = None
            st.session_state.execute_params = {
                'gitlab_token': gitlab_token,
                'gitlab_url': gitlab_url if gitlab_url else None,
                'ai_provider': ai_provider,
                'api_key': api_key,
                'user_id': user_id,
                'pr_url': pr_url,
                'pr_command': pr_command,
                'question': question,
                'gemini_model': gemini_model,
                'config_path': config_path,
                'custom_prompt': custom_prompt,
                'selected_config': selected_config,
                'debug_level': debug_level,
                'verbosity_level': verbosity_level,
                'is_preview_mode': is_preview_mode
            }
            st.session_state.is_running = True
            st.rerun()

    # 前回の実行結果表示
    if st.session_state.get('last_result') and not st.session_state.is_running:
        st.markdown("---")
        st.subheader("📊 前回の実行結果")

        log_tab_prev, result_tab_prev = st.tabs(["📋 実行ログ", "✅ 実行結果"])

        with log_tab_prev:
            if st.session_state.get('last_log'):
                st.text(st.session_state.last_log)
            else:
                st.info("実行ログはありません")

        with result_tab_prev:
            result_placeholder_prev = st.empty()
            render_result_summary(result_placeholder_prev, st.session_state.last_result)

    # 実行処理
    if st.session_state.is_running and st.session_state.execute_params:
        _execute_pr_agent(runtime_config_manager)


def _execute_pr_agent(runtime_config_manager):
    """PR-Agentを実行"""
    import io
    import time
    import toml
    import concurrent.futures

    params = st.session_state.execute_params
    st.session_state.execute_params = None

    try:
        # 環境変数設定
        os.environ['GITLAB_TOKEN'] = params['gitlab_token']
        os.environ['GIT_PROVIDER'] = 'gitlab'

        # API設定
        api_config = _build_api_config(params)

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 設定ファイル適用
        status_text.text("⚙️ 設定ファイルを適用中...")
        progress_bar.progress(10)

        config_applied = _apply_config(params, api_config, runtime_config_manager)

        if not config_applied:
            st.error("❌ 設定ファイルの適用に失敗しました")
            st.session_state.is_running = False
            return

        config_file_path = runtime_config_manager.config_file
        params['resolved_config_file'] = str(config_file_path)
        status_text.text(f"✅ 設定ファイルを適用しました")

        # 設定表示
        _display_applied_config(params, config_file_path)

        status_text.text(f"🔄 PR-Agent {params['pr_command']} コマンドを実行中...")
        progress_bar.progress(30)

        st.info("💡 **実行中の操作:** 途中で中断したい場合は、ブラウザをリロード（F5キー）してください。")

        log_tab, result_tab = st.tabs(["📋 実行ログ", "✅ 実行結果"])

        with log_tab:
            log_placeholder = st.empty()

        with result_tab:
            result_placeholder = st.empty()

        # PR-Agent実行
        result, log_lines = _run_pr_agent(params, log_placeholder)

        progress_bar.progress(100)

        # 結果処理
        errors = [line for line in log_lines if 'ERROR' in line or 'Exception' in line or 'Traceback' in line]
        warnings = [line for line in log_lines if 'WARNING' in line or 'warning' in line]

        result_state = {
            'status': 'success' if result else 'error',
            'warnings': warnings,
            'errors': [] if result else errors,
            'params': {
                'pr_command': params['pr_command'],
                'pr_url': params['pr_url'],
                'gitlab_url': params.get('gitlab_url'),
                'ai_provider': params['ai_provider'],
                'gemini_model': params.get('gemini_model'),
                'selected_config': params.get('selected_config', 'デフォルト'),
                'question': params.get('question'),
                'custom_prompt': params.get('custom_prompt'),
                'is_preview_mode': params.get('is_preview_mode')
            }
        }

        status_text.text("✅ 実行完了！" if result else "❌ レビュー失敗")
        st.session_state.last_result = result_state
        st.session_state.last_log = '\n'.join(log_lines) if log_lines else ""
        render_result_summary(result_placeholder, result_state)

        st.session_state.is_running = False
        st.rerun()

    except Exception as e:
        st.session_state.is_running = False
        st.session_state.execute_params = None
        st.session_state.last_result = None
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.exception(e)


def _build_api_config(params):
    """API設定を構築"""
    if params['ai_provider'] == "Gemini":
        os.environ['AI_PROVIDER'] = 'google'
        os.environ['GEMINI_API_KEY'] = params['api_key']
        os.environ['GEMINI_MODEL'] = params['gemini_model']
        return {
            'provider': 'gemini',
            'api_key': params['api_key'],
            'model': params['gemini_model']
        }
    else:
        base_url = os.getenv("OPENAI_BASE_URL", "")
        api_path = os.getenv("OPENAI_PATH", "/chat/completions")
        os.environ.pop('GEMINI_API_KEY', None)
        os.environ.pop('GEMINI_MODEL', None)
        os.environ['AI_PROVIDER'] = 'openai'
        return {
            'provider': 'openai',
            'api_key': params['api_key'],
            'base_url': base_url,
            'api_path': api_path,
            'user_id': params['user_id'],
            'custom_headers': {
                'api-key': params['api_key'],
                'apim-user-id': params['user_id']
            }
        }


def _apply_config(params, api_config, runtime_config_manager):
    """設定を適用"""
    gitlab_url_param = params.get('gitlab_url')

    if params['config_path']:
        return runtime_config_manager.apply_config(
            params['config_path'],
            params['custom_prompt'],
            api_config,
            gitlab_url=gitlab_url_param,
            verbosity=params.get('verbosity_level', 1),
            preview_mode=params.get('is_preview_mode', False),
            pr_command=params['pr_command']
        )
    else:
        runtime_config_manager.create_default_config(
            params['custom_prompt'],
            api_config,
            gitlab_url=gitlab_url_param,
            verbosity=params.get('verbosity_level', 1),
            preview_mode=params.get('is_preview_mode', False),
            pr_command=params['pr_command']
        )
        return True


def _display_applied_config(params, config_file_path):
    """適用された設定を表示"""
    import toml

    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            applied_config = toml.load(f)

        relevant_sections = COMMAND_SECTION_MAP.get(params['pr_command'], [])
        filtered_config = {s: applied_config[s] for s in relevant_sections if s in applied_config}

        if params.get('is_preview_mode'):
            st.info("💡 プレビューモードで実行されます（GitLabに投稿されません）")

        with st.expander(f"📄 適用された設定 ({params['pr_command']}コマンド用)", expanded=False):
            if relevant_sections:
                st.info(f"💡 {params['pr_command']}コマンドに関連する設定のみ表示")
                st.code(toml.dumps(filtered_config), language="toml")
    except Exception as e:
        st.warning(f"設定の読み込みに失敗しました: {e}")


def _run_pr_agent(params, log_placeholder):
    """PR-Agentを実行してログを取得"""
    import sys
    import io
    import time
    import concurrent.futures

    log_lines = []

    class OutputCapture:
        def __init__(self, original_stream):
            self.original_stream = original_stream

        def write(self, text):
            self.original_stream.write(text)
            self.original_stream.flush()
            if text.strip():
                log_lines.append(text.rstrip())
                if len(log_lines) > 100:
                    log_lines.pop(0)

        def flush(self):
            self.original_stream.flush()

    def update_log_display(text):
        st.session_state.log_text = text
        if text:
            log_placeholder.text(text)
        else:
            log_placeholder.info("実行ログはここに表示されます")

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = OutputCapture(old_stdout)
    sys.stderr = OutputCapture(old_stderr)

    try:
        ctx = get_script_run_ctx()
        session_id = ctx.session_id if ctx else None

        if session_id:
            Logger.clear_session_logs(session_id)

        extra_args = []
        if params['pr_command'] == "ask" and params['question']:
            extra_args.append(params['question'])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                PRAgentRunner.run_sync,
                params['pr_url'],
                params['pr_command'],
                extra_args,
                params.get('resolved_config_file'),
                params.get('gitlab_url'),
                params.get('debug_level', 1),
                session_id,
            )

            while not future.done():
                if session_id:
                    session_logs = Logger.get_session_logs(session_id)
                    if session_logs:
                        log_text = '\n'.join([log['message'] for log in session_logs])
                        update_log_display(log_text)
                elif log_lines:
                    update_log_display('\n'.join(log_lines))
                time.sleep(0.5)

            result = future.result()

        # 最終ログ
        if session_id:
            session_logs = Logger.get_session_logs(session_id)
            if session_logs:
                log_lines = [log['message'] for log in session_logs]
                update_log_display('\n'.join(log_lines))

        return result, log_lines

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


# =============================================================================
# ページ設定
# =============================================================================

st.set_page_config(page_title="PR-Agent", page_icon="🤖", layout="wide")

# ページ訪問記録（初回のみ）
if 'visited_pr_agent' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="PR-Agent")
    st.session_state.visited_pr_agent = True

# ヘッダー
render_page_header()
render_usage_guide()
st.markdown("---")
with st.expander("📄 仕様Excelチェック（試行）", expanded=False):
    _render_excel_spec_validator()


# =============================================================================
# サイドバー設定
# =============================================================================

if 'config_session_id' not in st.session_state:
    try:
        ctx = get_script_run_ctx()
        current_session_id = ctx.session_id if ctx else None
    except RuntimeError:
        current_session_id = None
    st.session_state.config_session_id = current_session_id or uuid.uuid4().hex

runtime_config_manager = ConfigManager(session_id=st.session_state.config_session_id)
config_repo = ConfigRepository()

with st.sidebar:
    apply_sidebar_styles()

    # --- 1. 基本設定 ---
    st.header("⚙️ 1.設定")

    ai_provider = st.selectbox(
        "🤖 AIプロバイダー",
        AI_PROVIDERS,
        help="使用するAIモデルのプロバイダーを選択",
        on_change=close_modal
    )

    st.markdown("---")

    # GitLab Token
    gitlab_token = st.text_input(
        "🔑 GitLab Token",
        value=os.getenv("GITLAB_TOKEN", ""),
        type="password",
        help="GitLabアクセストークン（api scope必須）"
    )

    # プロバイダー別の認証情報
    gemini_model = ''
    user_id = None

    if ai_provider == "OpenAI (Azure)":
        api_key, user_id = _render_openai_config()
    else:
        api_key, gemini_model = _render_gemini_config()

    st.markdown("---")

    # --- 2. コマンド選択 ---
    st.subheader("🎯 2.PR-Agentコマンド")

    cmd_col, cmd_desc_col = st.columns([2, 1])
    with cmd_col:
        pr_command = st.selectbox(
            "実行コマンド",
            options=list(COMMAND_DESCRIPTIONS.keys()),
            help="実行するPR-Agentコマンドを選択",
            on_change=close_modal
        )
    with cmd_desc_col:
        st.caption("説明")
        st.caption(COMMAND_DESCRIPTIONS[pr_command])

    question = ""
    if pr_command == "ask":
        question = st.text_area(
            "質問内容",
            placeholder="例: このMRのセキュリティリスクは？",
            help="MRに関する質問を入力してください"
        )

    st.markdown("---")

    # --- 3. コンテキスト設定 ---
    st.subheader("⚙️ 3.コンテキスト設定")

    config_options, config_descriptions = _build_config_options(config_repo)

    config_col, config_desc_col = st.columns([2, 1])
    with config_col:
        selected_config = st.selectbox(
            "設定ファイル",
            options=list(config_options.keys()),
            help="PR-Agentの動作を制御する設定ファイルを選択",
            on_change=close_modal
        )

    config_path = config_options[selected_config]

    with config_desc_col:
        st.caption("説明")
        st.caption(config_descriptions.get(selected_config, "標準設定を使用"))

    # 設定ファイル編集モーダル
    if selected_config != "デフォルト":
        if st.button("⚙️ 設定を確認・編集", use_container_width=True, key="open_config_modal"):
            st.session_state[MODAL_STATE_KEY] = selected_config
        if st.session_state.get(MODAL_STATE_KEY) == selected_config:
            config_editor_modal(selected_config, config_path, config_repo)
    else:
        st.session_state.pop(MODAL_STATE_KEY, None)

    st.markdown("---")

    # 詳細設定
    debug_level, verbosity_level, gitlab_url, custom_prompt = _render_advanced_settings()


# =============================================================================
# メインエリア
# =============================================================================

st.subheader("📍 マージリクエスト情報")

input_method = st.radio(
    "入力方法",
    ["URLを直接入力", "プロジェクトから選択"],
    horizontal=True,
    key=INPUT_METHOD_KEY,
    on_change=close_modal
)

pr_url = _render_mr_input(input_method, gitlab_token, gitlab_url)

st.markdown("---")

# 実行ボタン
_render_execute_buttons(
    gitlab_token, api_key, user_id, pr_url, ai_provider,
    pr_command, question, gemini_model, config_path, custom_prompt,
    selected_config, debug_level, verbosity_level, gitlab_url, runtime_config_manager
)

# フッター
render_page_footer()
