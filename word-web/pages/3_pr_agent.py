#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
# Dockerコンテナ内: /app/pages/3_pr_agent.py → /app/.env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    # デバッグ: 環境変数の読み込み確認
    import logging
    logging.info(f"✅ .env loaded from: {env_path}")
else:
    import logging
    logging.warning(f"⚠️ .env not found at: {env_path}")

# バックエンドモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from word.pr_agent import PRAgentRunner, ConfigManager, Logger, UrlValidator

# トラッキングをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from usage_tracker import track_usage

# Geminiモデルのデフォルト値
gemini_model = ""


def render_result_summary(placeholder, result_state):
    """Render run result details that persist across reruns."""
    with placeholder.container():
        if not result_state:
            st.info("実行結果はここに表示されます")
            return

        params = result_state.get('params', {})
        warnings = result_state.get('warnings') or []
        errors = result_state.get('errors') or []
        status = result_state.get('status')

        if status == 'success':
            if warnings:
                st.warning(f"⚠️ PR-Agentコマンドが完了しましたが、{len(warnings)}件の警告がありました")
                with st.expander(f"⚠️ 警告詳細 ({len(warnings)}件)", expanded=False):
                    for warn in warnings[:10]:
                        st.code(warn, language='log')
            else:
                st.success("✅ PR-Agentコマンドが正常に完了しました！")
        else:
            st.error("❌ レビュー中にエラーが発生しました")
            if errors:
                with st.expander(f"🔍 エラー詳細 ({len(errors)}件)", expanded=True):
                    for err in errors[:20]:
                        st.code(err, language='log')

        st.markdown("### 📋 実行内容")
        if params.get('pr_command'):
            st.write(f"- **コマンド**: {params['pr_command']}")
        if params.get('pr_url'):
            st.write(f"- **MR URL**: {params['pr_url']}")
        if params.get('gitlab_url'):
            st.write(f"- **GitLab URL**: {params['gitlab_url']} ✅ ユーザー指定")
        ai_provider = params.get('ai_provider')
        if ai_provider:
            if ai_provider == "Gemini":
                st.write("- **AIプロバイダー**: Google Gemini")
                if params.get('gemini_model'):
                    st.write(f"- **モデル**: {params['gemini_model']}")
            else:
                st.write("- **AIプロバイダー**: OpenAI (Azure)")
                st.write("- **モデル**: gpt-4o")
        if params.get('selected_config'):
            st.write(f"- **設定**: {params['selected_config']}")
        if params.get('pr_command') == "ask" and params.get('question'):
            st.write(f"- **質問**: {params['question']}")
        if params.get('custom_prompt'):
            st.write(f"- **カスタムプロンプト**: {params['custom_prompt']}")

        if status == 'success':
            st.info("💡 結果はGitLabのMRページに投稿されました")
        else:
            st.warning("💡 上記のエラーログを確認して、問題を修正してください")

# ページ設定
st.set_page_config(
    page_title="PR-Agent",
    page_icon="🤖",
    layout="wide"
)

# ページ訪問記録（初回のみ）
if 'visited_pr_agent' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="PR-Agent")
    st.session_state.visited_pr_agent = True

# タイトル
st.title("🤖 PR-Agent")
st.markdown("""
<div style='background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 マージリクエストの自動レビュー</h3>
    <p style='color: #f0fff4; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        AIがコードをレビューして改善提案・テストケース・ドキュメントを自動生成
    </p>
</div>
""", unsafe_allow_html=True)

# 使い方ガイド
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ コードレビューの自動化
    - ✅ コード品質の分析
    - ✅ 改善提案の生成
    - ✅ テストケースの提案
    - ✅ ドキュメントの自動生成

    ---

    ## 🚀 使用手順

    ### ステップ1️⃣: MR URLを入力

    GitLabのマージリクエストURLを入力

    ### ステップ2️⃣: API設定

    - GitLab Token（リポジトリアクセス用）
    - OpenAI API キーとユーザID（レビュー生成用）

    ### ステップ3️⃣: 設定を選択

    - プリセット設定（セキュリティ特化、パフォーマンス特化など）
    - コマンド選択（review, improve, describe等）

    ### ステップ4️⃣: レビュー実行

    「🚀 レビュー実行」ボタンをクリック
    """)

st.markdown("---")

# ConfigManagerを初期化
config_manager = ConfigManager()
available_configs = config_manager.get_available_configs()

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    # AIプロバイダー選択
    ai_provider = st.selectbox(
        "🤖 AIプロバイダー",
        ["OpenAI (Azure)", "Gemini"],
        help="使用するAIモデルのプロバイダーを選択"
    )

    # API認証情報
    st.markdown("---")

    # GitLab Token
    default_token = os.getenv("GITLAB_TOKEN", "")
    gitlab_token = st.text_input(
        "🔑 GitLab Token",
        value=default_token,
        type="password",
        help="GitLabアクセストークン（api scope必須）"
    )

    # プロバイダーに応じた認証情報入力
    import json

    gemini_model = ''

    if ai_provider == "OpenAI (Azure)":
        # OPENAI_HEADERS_JSONから値を抽出
        headers_json = os.getenv("OPENAI_HEADERS_JSON", "{}")
        try:
            headers_dict = json.loads(headers_json)
            default_api_key = headers_dict.get("api-key", "")
            default_user_id = headers_dict.get("apim-user-id", "")
        except:
            default_api_key = ""
            default_user_id = ""

        # OpenAI API設定
        api_key = st.text_input(
            "OpenAI APIキー",
            value=default_api_key,
            type="password",
            help="OpenAI APIのキーを入力してください（.envのOPENAI_HEADERS_JSONから自動取得）"
        )

        user_id = st.text_input(
            "ユーザID",
            value=default_user_id,
            help="APIユーザIDを入力してください（.envのOPENAI_HEADERS_JSONから自動取得）"
        )

    else:  # Gemini
        # Gemini API設定
        default_gemini_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini APIキー",
            value=default_gemini_key,
            help="Google Gemini APIのキーを入力してください（.envのGEMINI_API_KEYから自動取得）"
        )

        # Geminiモデル選択
        gemini_model = st.selectbox(
            "Geminiモデル",
            [
                "gemini/gemini-2.0-flash-exp",
                "gemini/gemini-1.5-pro-latest",
                "gemini/gemini-1.5-flash-latest",
                "gemini/gemini-1.5-flash-002"
            ],
            help="使用するGeminiモデルを選択"
        )

        user_id = None  # GeminiではユーザーID不要

    st.markdown("---")

    st.subheader("🎯 PR-Agentコマンド")

    # コマンドの説明
    command_descriptions = {
        "review": "📝 コードレビュー - コードの問題点、改善提案、ベストプラクティスを分析",
        "improve": "✨ コード改善 - 具体的なコード改善案を提示（リファクタリング、最適化など）",
        "describe": "📋 MR説明生成 - MRの内容を分析して説明文を自動生成",
        "ask": "❓ 質問応答 - MRに関する質問に回答（例: セキュリティリスクは？）",
        "generate_labels": "🏷️ ラベル生成 - MRの内容に基づいて適切なラベルを提案",
        "add_docs": "📚 ドキュメント追加 - コードのドキュメントを自動生成"
    }

    pr_command = st.selectbox(
        "実行コマンド",
        options=list(command_descriptions.keys()),
        help="実行するPR-Agentコマンドを選択"
    )

    # コマンド説明を下に表示
    st.info(command_descriptions[pr_command])

    # askコマンドの場合は質問入力欄を表示
    question = ""
    if pr_command == "ask":
        question = st.text_area(
            "質問内容",
            placeholder="例: このMRのセキュリティリスクは？",
            help="MRに関する質問を入力してください"
        )

    st.markdown("---")

    st.subheader("⚙️ コンテキスト設定")

    # 設定選択
    config_options = {"デフォルト": None}
    config_descriptions = {"デフォルト": "標準的なコードレビュー設定（common.tomlのみ使用）"}

    def extract_description(path):
        """設定ファイルから説明を抽出"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # コメント行で、=や空行でないものを探す
                    if line.startswith('#') and line not in ['#', '# =============================================================================']:
                        desc = line.lstrip('# ').strip()
                        if desc and not desc.startswith('='):
                            return desc
                return Path(path).stem
        except:
            return Path(path).stem

    # カスタム設定（すべての設定はcustomディレクトリに統合）
    for name, path in available_configs["custom"].items():
        config_options[name] = path
        config_descriptions[name] = extract_description(path)


    selected_config = st.selectbox(
        "設定ファイル",
        options=list(config_options.keys()),
        help="PR-Agentの動作を制御する設定ファイルを選択"
    )

    config_path = config_options[selected_config]

    # 設定ファイルの説明を下に表示
    st.info(config_descriptions.get(selected_config, "標準設定を使用"))

    # 選択された設定の内容を確認・編集可能に
    if selected_config != "デフォルト":
        # タブで表示と編集を切り替え
        view_tab, edit_tab = st.tabs(["📖 設定を確認", "✏️ 設定を編集"])

        with view_tab:
            try:
                import toml
                with open(config_path, "r", encoding="utf-8") as f:
                    full_config = toml.load(f)

                # コマンドに応じてセクションをフィルタリング
                command_section_map = {
                    "review": ["pr_reviewer"],
                    "improve": ["pr_improve", "pr_code_suggestions"],
                    "describe": ["pr_description"],
                    "ask": ["pr_questions"],
                    "generate_labels": ["pr_generate_labels"],
                    "add_docs": ["pr_add_docs"]
                }

                # 選択されたコマンドに対応するセクションを取得
                relevant_sections = command_section_map.get(pr_command, [])

                # 常に表示する共通セクション
                common_sections = []  # configやgitlabは表示しない

                # フィルタリングされた設定を作成
                filtered_config = {}
                for section in common_sections + relevant_sections:
                    if section in full_config:
                        filtered_config[section] = full_config[section]

                # フィルタリング情報を表示
                if relevant_sections:
                    st.info(f"💡 {pr_command}コマンドに関連する設定のみ表示しています: {', '.join(relevant_sections)}")

                # フィルタリングされた設定をTOML形式で表示
                filtered_toml = toml.dumps(filtered_config)
                st.code(filtered_toml, language="toml")

                # 全設定を見るオプション
                with st.expander("🔍 全設定を表示", expanded=False):
                    with open(config_path, "r", encoding="utf-8") as f:
                        st.code(f.read(), language="toml")

            except Exception as e:
                st.error(f"設定ファイルの読み込みに失敗: {e}")

        with edit_tab:
            try:
                import toml

                # 現在の設定を読み込み
                with open(config_path, "r", encoding="utf-8") as f:
                    current_config_text = f.read()

                st.info("💡 設定ファイルを直接編集できます。保存後、PR-Agent実行時に反映されます。")

                # 編集用テキストエリア
                edited_config_text = st.text_area(
                    f"{selected_config} の内容を編集",
                    value=current_config_text,
                    height=400,
                    help="TOML形式で設定を編集してください"
                )

                col1, col2 = st.columns([1, 3])
                with col1:
                    save_button = st.button("💾 保存", type="primary", use_container_width=True)
                with col2:
                    if st.button("🔄 元に戻す", use_container_width=True):
                        st.rerun()

                if save_button:
                    try:
                        # TOML構文チェック
                        import io
                        toml.load(io.StringIO(edited_config_text))

                        # バックアップを作成
                        import shutil
                        from datetime import datetime
                        backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy(config_path, backup_path)

                        # 設定ファイルを更新
                        with open(config_path, "w", encoding="utf-8") as f:
                            f.write(edited_config_text)

                        st.success(f"✅ 設定ファイルを保存しました！")
                        st.info(f"📋 バックアップ: {backup_path}")

                        # 実行記録
                        track_usage(action="設定ファイル編集", tool_name="PR-Agent", username=selected_config)

                    except toml.TomlDecodeError as e:
                        st.error(f"❌ TOML構文エラー: {str(e)}")
                        st.warning("修正してから再度保存してください")
                    except Exception as e:
                        st.error(f"❌ 保存エラー: {str(e)}")

            except Exception as e:
                st.error(f"設定ファイルの読み込みに失敗: {e}")

    st.markdown("---")

    with st.expander("🔧 詳細設定", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # デバッグレベル設定
            st.markdown("#### 🔍 ログレベル")
            debug_level = st.selectbox(
                "ログ出力レベル",
                options=[0, 1, 2],
                index=1,
                format_func=lambda x: {
                    0: "エラーのみ",
                    1: "標準（推奨）",
                    2: "詳細"
                }[x],
                help="0:エラーのみ / 1:進捗情報 / 2:デバッグ詳細"
            )
            # verbosity_levelを自動計算
            verbosity_level = min(debug_level, 2)

        with col2:
            # GitLab URL設定
            st.markdown("#### 🌐 GitLab URL")
            default_gitlab_url = os.getenv("GITLAB_URL", "")
            gitlab_url = st.text_input(
                "GitLab URL（任意）",
                value=default_gitlab_url,
                placeholder="例: https://gitlab.example.com",
                help="通常はMR URLから自動抽出されます"
            )

        # GitLab URLのバリデーション
        if gitlab_url:
            normalized_url = UrlValidator.normalize_gitlab_url(gitlab_url)
            if UrlValidator.validate_gitlab_url(normalized_url):
                gitlab_url = normalized_url
            else:
                st.error("❌ 無効なGitLab URL")
                gitlab_url = None

        st.markdown("---")

        # カスタムプロンプト
        custom_prompt = st.text_area(
            "📝 カスタムプロンプト（任意）",
            placeholder="例: セキュリティ脆弱性を重点的にチェック",
            height=80,
            help="レビューに適用する追加の指示"
        )

        # コマンド別の設定
        if pr_command == "improve":
            num_suggestions = st.slider(
                "提案数",
                min_value=1,
                max_value=20,
                value=10,
                help="コード改善提案の数"
            )
        elif pr_command == "review":
            inline_limit = st.slider(
                "インラインコメント上限",
                min_value=10,
                max_value=100,
                value=30,
                help="レビューコメントの最大数"
            )

    st.markdown("---")

# メインエリア
st.subheader("📍 マージリクエスト情報")

# 入力方法選択
input_method = st.radio(
    "入力方法",
    ["URLを直接入力", "プロジェクトから選択"],
    horizontal=True
)

pr_url = ""

if input_method == "URLを直接入力":
    pr_url = st.text_input(
        "MR URL",
        placeholder="https://gitlab.com/group/project/-/merge_requests/1",
        help="レビュー対象のマージリクエストURL"
    )

    # MR URLのバリデーション
    if pr_url:
        if UrlValidator.validate_pr_url(pr_url):
            st.success("✅ 有効なMR/PR URL")
        else:
            st.error("❌ 無効なMR/PR URLです。/merge_requests/ または /pull/ を含むURLを入力してください")
else:
    # プロジェクトから選択
    project_url = st.text_input(
        "プロジェクトURL",
        placeholder="https://gitlab.rp.dss.itmufg/PIT03077/word",
        help="GitLabプロジェクトのURL（例: https://gitlab.rp.dss.itmufg/グループ名/プロジェクト名）"
    )

    if project_url and gitlab_token:
        try:
            import requests
            import re
            import urllib.parse

            # GitLab MR一覧を取得
            # 独自ホスティングにも対応
            match = re.match(r'(https?://[^/]+)/(.+)', project_url.rstrip('/'))
            if match:
                gitlab_base_url = match.group(1)
                project_path = match.group(2)
                # URLエンコード
                encoded_project = urllib.parse.quote(project_path, safe='')

                # GitLab API でMR一覧を取得
                headers = {
                    "PRIVATE-TOKEN": gitlab_token
                }
                api_url = f"{gitlab_base_url}/api/v4/projects/{encoded_project}/merge_requests"

                with st.spinner("MR一覧を取得中..."):
                    response = requests.get(
                        api_url,
                        headers=headers,
                        params={"state": "opened", "order_by": "updated_at", "sort": "desc"}
                    )

                if response.status_code == 200:
                    mrs = response.json()

                    if mrs:
                        # MR選択ボックス
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

                        # 選択されたMRの詳細を表示
                        selected_mr = next(mr for mr in mrs if mr['web_url'] == pr_url)

                        with st.expander("📋 MR詳細", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**タイトル**: {selected_mr['title']}")
                                st.write(f"**作成者**: {selected_mr['author']['name']}")
                                st.write(f"**ターゲットブランチ**: {selected_mr['target_branch']}")
                            with col2:
                                st.write(f"**ソースブランチ**: {selected_mr['source_branch']}")
                                st.write(f"**作成日**: {selected_mr['created_at'][:10]}")
                                st.write(f"**更新日**: {selected_mr['updated_at'][:10]}")
                    else:
                        st.info("このプロジェクトにはオープンなMRがありません")
                else:
                    st.error(f"❌ MR一覧の取得に失敗しました: {response.status_code}")
                    if response.status_code == 401:
                        st.error("GitLab Tokenが無効です")
                    elif response.status_code == 404:
                        st.error("プロジェクトが見つかりません")
            else:
                st.warning("⚠️ プロジェクトURLにはプロジェクトパスが必要です")
                st.info("""
**正しい形式:**
- ✅ `https://gitlab.rp.dss.itmufg/グループ名/プロジェクト名`
- ✅ `https://gitlab.rp.dss.itmufg/PIT03077/word`

**間違った形式:**
- ❌ `https://gitlab.rp.dss.itmufg` （プロジェクトパスが無い）
                """)

        except Exception as e:
            st.error(f"エラー: {str(e)}")
    elif project_url and not gitlab_token:
        st.warning("⚠️ GitLab Tokenを入力してください")

st.markdown("---")

# 実行状態の管理
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'execute_params' not in st.session_state:
    st.session_state.execute_params = None
if 'log_text' not in st.session_state:
    st.session_state.log_text = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# 実行ボタン
# Geminiの場合はuser_id不要
if ai_provider == "Gemini":
    button_disabled = not (gitlab_token and api_key and pr_url)
else:
    button_disabled = not (gitlab_token and api_key and user_id and pr_url)

if pr_command == "ask":
    button_disabled = button_disabled or not question

# 実行中は無効化
button_disabled = button_disabled or st.session_state.is_running

# 実行中の状態を表示
if st.session_state.is_running:
    st.info("⏳ PR-Agent実行中です...しばらくお待ちください")

if st.button("🚀 PR-Agent実行", type="primary", use_container_width=True, disabled=button_disabled):
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
        # 実行ボタン押下を記録
        track_usage(action="実行ボタン押下", tool_name="PR-Agent", username=f"{pr_command}コマンド")

        st.session_state.log_text = ""
        st.session_state.last_result = None

        # 実行パラメータを保存
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
            'verbosity_level': verbosity_level
        }
        # 実行状態を設定して再レンダリング（二重クリック防止）
        st.session_state.is_running = True
        st.rerun()


# 実行パラメータがある場合は実行
if st.session_state.is_running and st.session_state.execute_params:
    params = st.session_state.execute_params
    st.session_state.execute_params = None  # パラメータをクリア

    try:
        # API認証情報を環境変数に設定（GitLab用）
        os.environ['GITLAB_TOKEN'] = params['gitlab_token']
        # GitプロバイダーをGitLabに固定（PR-AgentのURL自動判定をオーバーライド）
        os.environ['GIT_PROVIDER'] = 'gitlab'

        # API設定を準備（PR-Agent設定ファイルに注入）
        import json

        if params['ai_provider'] == "Gemini":
            # Gemini用の設定
            api_config = {
                'provider': 'gemini',
                'api_key': params['api_key'],
                'model': params['gemini_model']
            }
            # Geminiの場合は環境変数でプロバイダーとモデルを明示
            os.environ['AI_PROVIDER'] = 'google'
            os.environ['GEMINI_API_KEY'] = params['api_key']
            os.environ['GEMINI_MODEL'] = params['gemini_model']
        else:
            # OpenAI (Azure)用の設定
            base_url = os.getenv("OPENAI_BASE_URL", "")
            api_path = os.getenv("OPENAI_PATH", "/chat/completions")
            api_config = {
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
            # OpenAI利用時はGemini用の環境変数をリセット
            os.environ.pop('AI_PROVIDER', None)
            os.environ.pop('GEMINI_API_KEY', None)
            os.environ.pop('GEMINI_MODEL', None)
            os.environ['AI_PROVIDER'] = 'openai'

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 設定ファイルを適用
        status_text.text("⚙️ 設定ファイルを適用中...")
        progress_bar.progress(10)

        config_applied = False
        gitlab_url_param = params.get('gitlab_url')

        if params['config_path']:
            # 選択された設定ファイルを適用
            config_applied = config_manager.apply_config(
                params['config_path'],
                params['custom_prompt'],
                api_config,
                gitlab_url=gitlab_url_param,
                verbosity=params.get('verbosity_level', 1)
            )
        else:
            # デフォルト設定を作成
            config_manager.create_default_config(
                params['custom_prompt'],
                api_config,
                gitlab_url=gitlab_url_param,
                verbosity=params.get('verbosity_level', 1)
            )
            config_applied = True

        if config_applied:
            config_file_path = config_manager.config_file
            params['resolved_config_file'] = str(config_file_path)
            status_text.text(f"✅ 設定ファイルを適用しました ({config_file_path})")
            try:
                import toml
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    applied_config = toml.load(f)

                # コマンドに応じてフィルタリング
                command_section_map = {
                    "review": ["pr_reviewer"],
                    "improve": ["pr_improve", "pr_code_suggestions"],
                    "describe": ["pr_description"],
                    "ask": ["pr_questions"],
                    "generate_labels": ["pr_generate_labels"],
                    "add_docs": ["pr_add_docs"]
                }

                relevant_sections = command_section_map.get(params['pr_command'], [])
                filtered_config = {}
                for section in relevant_sections:
                    if section in applied_config:
                        filtered_config[section] = applied_config[section]

                # フィルタリングされた設定を表示
                filtered_toml = toml.dumps(filtered_config)

                with st.expander(f"📄 適用された設定 ({params['pr_command']}コマンド用)", expanded=False):
                    if relevant_sections:
                        st.info(f"💡 {params['pr_command']}コマンドに関連する設定のみ表示: {', '.join(relevant_sections)}")
                        st.code(filtered_toml, language="toml")

                    # 全設定を見るオプション
                    with st.expander("🔍 全設定を表示", expanded=False):
                        config_text = Path(config_file_path).read_text(encoding="utf-8")
                        preview = config_text if len(config_text) <= 4000 else config_text[:4000] + "\n... (truncated)"
                        st.code(preview, language="toml")

            except Exception as config_error:
                st.warning(f".pr_agent.toml の読み込みに失敗しました: {config_error}")
        else:
            st.error("❌ 設定ファイルの適用に失敗しました")
            st.session_state.is_running = False
            raise RuntimeError("Failed to apply PR-Agent configuration")

        status_text.text(f"🔄 PR-Agent {params['pr_command']} コマンドを実行中...（2～3分程度かかります）")
        progress_bar.progress(30)

        # 実行中の操作ガイド
        st.info("💡 **実行中の操作:** 途中で中断したい場合は、ブラウザをリロード（F5キー）してください。失敗した場合は、実行結果タブでエラーログを確認できます。")

        # タブで実行ログと結果を分ける
        log_tab, result_tab = st.tabs(["📋 実行ログ", "✅ 実行結果"])

        with log_tab:
            log_placeholder = st.empty()

        with result_tab:
            result_placeholder = st.empty()

        # PR-Agentを実行
        extra_args = []
        if params['pr_command'] == "ask" and params['question']:
            extra_args.append(params['question'])

        # ログ収集用（標準出力/エラー出力をキャプチャ）
        import sys
        import io
        import time
        import concurrent.futures

        log_lines = []
        capture_running = True

        def update_log_display(text):
            st.session_state.log_text = text
            if text:
                log_placeholder.text(text)
            else:
                log_placeholder.info("実行ログはここに表示されます")

        # 標準出力/エラー出力をキャプチャするクラス
        class OutputCapture:
            def __init__(self, original_stream):
                self.original_stream = original_stream
                self.buffer = io.StringIO()

            def write(self, text):
                self.original_stream.write(text)
                self.original_stream.flush()
                if text.strip():
                    log_lines.append(text.rstrip())
                    # 最新100行のみ保持
                    if len(log_lines) > 100:
                        log_lines.pop(0)

            def flush(self):
                self.original_stream.flush()

        # 標準出力/エラー出力をキャプチャ
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = OutputCapture(old_stdout)
        sys.stderr = OutputCapture(old_stderr)

        try:
            # Streamlitセッションステートからセッション IDを取得
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            session_id = ctx.session_id if ctx else None

            # セッションログをクリア（前回実行のログが残らないように）
            if session_id:
                Logger.clear_session_logs(session_id)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # PR-Agentを非同期で実行
                future = executor.submit(
                    PRAgentRunner.run_sync,
                    params['pr_url'],
                    params['pr_command'],
                    extra_args,
                    params.get('resolved_config_file'),
                    params.get('gitlab_url'),
                    params.get('debug_level', 1),
                    session_id  # セッションIDを渡す
                )

                # 完了するまでログを更新
                while not future.done():
                    # セッションログを取得して表示
                    if session_id:
                        session_logs = Logger.get_session_logs(session_id)
                        if session_logs:
                            log_text = '\n'.join([log['message'] for log in session_logs])
                            update_log_display(log_text)
                    elif log_lines:
                        # フォールバック: 標準出力キャプチャ
                        log_text = '\n'.join(log_lines)
                        update_log_display(log_text)
                    time.sleep(0.5)  # 0.5秒ごとに更新

                # 最終結果を取得
                result = future.result()

            # 最終ログを表示
            if session_id:
                session_logs = Logger.get_session_logs(session_id)
                if session_logs:
                    log_text = '\n'.join([log['message'] for log in session_logs])
                    update_log_display(log_text)
            elif log_lines:
                # フォールバック: 標準出力キャプチャ
                log_text = '\n'.join(log_lines)
                update_log_display(log_text)
        finally:
            # 標準出力/エラー出力を元に戻す
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            # 実行状態を解除
            st.session_state.is_running = False

        progress_bar.progress(100)

        # ログからエラー/警告を検出
        errors = [line for line in log_lines if 'ERROR' in line or 'Exception' in line or 'Traceback' in line]
        warnings = [line for line in log_lines if 'WARNING' in line or 'warning' in line or 'Failed to generate prediction' in line]

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
                'custom_prompt': params.get('custom_prompt')
            }
        }

        status_text.text("✅ 実行完了！" if result else "❌ レビュー失敗")
        st.session_state.last_result = result_state
        render_result_summary(result_placeholder, result_state)
        st.session_state.execute_params = None

    except Exception as e:
        st.session_state.is_running = False
        st.session_state.execute_params = None  # エラー時もクリア
        st.session_state.last_result = None
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.exception(e)

        # ページを再読み込みしてボタンを有効化
        st.info("🔄 ページを更新してください（F5キーを押すか、ブラウザの更新ボタンをクリック）")

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        PR-Agent v2.0 | Powered by Streamlit & tool-branch backend
    </div>
    """,
    unsafe_allow_html=True
)
