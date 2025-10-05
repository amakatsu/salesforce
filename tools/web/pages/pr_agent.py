#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import sys
import os
import asyncio
from pathlib import Path

# 共通設定をインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from web_common.config import (
    render_api_credentials_section,
    get_custom_prompt,
    CUSTOM_PROMPT_TEMPLATES
)

# pr-agentモジュールのパスを追加
tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tools_dir / "pr-agent"))

# ページ設定
st.set_page_config(
    page_title="PR-Agent",
    page_icon="🤖",
    layout="wide"
)

# タイトル
st.title("🤖 PR-Agent")
st.markdown("""
<div style='background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 プルリクエストの自動レビュー</h3>
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

    ### ステップ1️⃣: レビュー方法を選択

    **方法A: GitHubリポジトリから**
    - リポジトリURL、ブランチ、PRナンバーを入力

    **方法B: ローカルファイルから**
    - 変更されたファイルをアップロード

    ### ステップ2️⃣: API設定

    - GitHub Token（リポジトリアクセス用）
    - LLM API Key（レビュー生成用）

    ### ステップ3️⃣: レビュー実行

    「🚀 レビュー実行」ボタンをクリック

    ### ステップ4️⃣: 結果を確認

    - コードレビューコメント
    - 改善提案
    - テストケース提案
    - セキュリティチェック結果
    """)

st.markdown("---")

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    st.subheader("🔑 GitLab Token")

    # GitLab Token
    default_gitlab_token = os.getenv("GITLAB_TOKEN", "")
    gitlab_token = st.text_input(
        "GitLab Token",
        value=default_gitlab_token,
        type="password",
        help="GitLabリポジトリにアクセスするためのパーソナルアクセストークン（api scope必須）"
    )

    st.markdown("---")

    # Azure OpenAI認証情報（共通設定を使用）
    api_key, user_id = render_api_credentials_section()

    st.markdown("---")

    st.subheader("🎯 PR-Agentコマンド")

    # コマンドの説明
    command_descriptions = {
        "review": "📝 コードレビュー - コードの問題点、改善提案、ベストプラクティスを分析",
        "improve": "✨ コード改善 - 具体的なコード改善案を提示（リファクタリング、最適化など）",
        "describe": "📋 PR説明生成 - PRの内容を分析して説明文を自動生成",
        "ask": "❓ 質問応答 - PRに関する質問に回答（例: セキュリティリスクは？）",
        "update_changelog": "📰 変更履歴更新 - CHANGELOGファイルを自動更新",
        "generate_labels": "🏷️ ラベル生成 - PRの内容に基づいて適切なラベルを提案"
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
            placeholder="例: 後方互換性リスクは？",
            help="PRに関する質問を入力してください"
        )

    st.markdown("---")

    st.subheader("⚙️ コンテキスト設定")

    # 利用可能な設定ファイルを取得
    configs_dir = tools_dir / "pr-agent" / "configs"

    config_options = {"デフォルト": None}
    config_descriptions = {"デフォルト": "標準設定を使用"}

    # プリセット
    presets_dir = configs_dir / "presets"
    if presets_dir.exists():
        for config_file in sorted(presets_dir.glob("*.toml")):
            key = f"🎯 {config_file.stem}"
            config_options[key] = str(config_file)
            # ファイルから説明を抽出
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        config_descriptions[key] = first_line.lstrip('# ').strip()
                    else:
                        config_descriptions[key] = f"プリセット: {config_file.stem}"
            except:
                config_descriptions[key] = f"プリセット: {config_file.stem}"

    # 言語固有
    lang_dir = configs_dir / "language-specific"
    if lang_dir.exists():
        for config_file in sorted(lang_dir.glob("*.toml")):
            key = f"🔧 {config_file.stem}"
            config_options[key] = str(config_file)
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        config_descriptions[key] = first_line.lstrip('# ').strip()
                    else:
                        config_descriptions[key] = f"言語固有設定: {config_file.stem}"
            except:
                config_descriptions[key] = f"言語固有設定: {config_file.stem}"

    # テンプレート
    templates_dir = configs_dir / "templates"
    if templates_dir.exists():
        for config_file in sorted(templates_dir.glob("*.toml")):
            key = f"📄 {config_file.stem}"
            config_options[key] = str(config_file)
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        config_descriptions[key] = first_line.lstrip('# ').strip()
                    else:
                        config_descriptions[key] = f"テンプレート: {config_file.stem}"
            except:
                config_descriptions[key] = f"テンプレート: {config_file.stem}"

    selected_config = st.selectbox(
        "設定ファイル",
        options=list(config_options.keys()),
        help="PR-Agentの動作を制御する設定ファイルを選択"
    )

    config_path = config_options[selected_config]

    # 設定ファイルの説明を下に表示
    st.info(config_descriptions.get(selected_config, "標準設定を使用"))

    # 選択された設定の内容を確認可能に
    if selected_config != "デフォルト":
        with st.expander("📖 設定ファイルの内容を確認", expanded=False):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    st.code(f.read(), language="toml")
            except Exception as e:
                st.error(f"設定ファイルの読み込みに失敗: {e}")

    st.markdown("---")

    with st.expander("🔧 詳細設定", expanded=False):
        model = st.selectbox(
            "LLMモデル",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            help="使用するAzure OpenAIモデル"
        )

        custom_prompt = get_custom_prompt(
            CUSTOM_PROMPT_TEMPLATES["pr_agent"],
            "このレビューに適用する追加の指示やコンテキスト情報"
        )

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


# メインエリア
st.subheader("GitLab マージリクエスト情報")

# MR選択方法
input_method = st.radio(
    "入力方法",
    ["URLを直接入力", "プロジェクトから選択"],
    horizontal=True
)

mr_url = ""
selected_mr = None

if input_method == "URLを直接入力":
    mr_url = st.text_input(
        "マージリクエストURL",
        placeholder="https://gitlab.com/group/project/-/merge_requests/1",
        help="レビュー対象のGitLab MR URL"
    )
else:
    # プロジェクトから選択
    project_url = st.text_input(
        "プロジェクトURL",
        placeholder="https://gitlab.com/group/project",
        help="GitLabプロジェクトのURL"
    )

    if project_url and gitlab_token:
        try:
            import requests
            import re

            # プロジェクトIDを抽出
            match = re.match(r'https://gitlab\.com/(.+)', project_url.rstrip('/'))
            if match:
                project_path = match.group(1)

                # GitLab APIでMR一覧を取得
                headers = {"PRIVATE-TOKEN": gitlab_token}
                api_url = f"https://gitlab.com/api/v4/projects/{project_path.replace('/', '%2F')}/merge_requests"

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

                        mr_url = mr_options[selected_label]

                        # 選択されたMRの詳細を表示
                        selected_mr = next(mr for mr in mrs if mr['web_url'] == mr_url)

                        with st.expander("📋 MR詳細", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**タイトル**: {selected_mr['title']}")
                                st.write(f"**作成者**: {selected_mr['author']['name']}")
                                st.write(f"**ソースブランチ**: {selected_mr['source_branch']}")
                            with col2:
                                st.write(f"**ターゲットブランチ**: {selected_mr['target_branch']}")
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
                st.warning("有効なGitLabプロジェクトURLを入力してください")
        except Exception as e:
            st.error(f"エラー: {str(e)}")
    elif project_url and not gitlab_token:
        st.warning("⚠️ GitLab Tokenを入力してください")

st.markdown("---")

# 実行ボタン（APIキーとMR URLが入力されている場合のみ有効）
button_disabled = not (gitlab_token and api_key and user_id and mr_url)
if pr_command == "ask":
    button_disabled = button_disabled or not question

if st.button("🚀 PR-Agent実行", type="primary", use_container_width=True, disabled=button_disabled):
    if not gitlab_token or not api_key or not user_id:
        st.error("❌ GitLab Token、Azure OpenAI API Key、User IDを入力してください")
    elif not mr_url:
        st.error("❌ マージリクエストURLを入力してください")
    elif pr_command == "ask" and not question:
        st.error("❌ askコマンドには質問内容が必要です")
    else:
        try:
            import subprocess
            import toml

            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text(f"🔄 設定ファイルを読み込み中...")
            progress_bar.progress(10)

            # 設定を読み込んでコマンドライン引数に変換
            config_args = []

            if config_path:
                # 選択された設定ファイルを読み込み
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = toml.load(f)

                # config セクション
                if 'config' in config_data:
                    for key, value in config_data['config'].items():
                        if key != 'model':  # modelは別で指定
                            config_args.extend([f"--config.{key}", str(value)])

                # pr_reviewer セクション
                if 'pr_reviewer' in config_data:
                    for key, value in config_data['pr_reviewer'].items():
                        if isinstance(value, bool):
                            config_args.extend([f"--pr_reviewer.{key}", "true" if value else "false"])
                        else:
                            config_args.extend([f"--pr_reviewer.{key}", str(value)])

                # pr_code_suggestions セクション
                if 'pr_code_suggestions' in config_data:
                    for key, value in config_data['pr_code_suggestions'].items():
                        if isinstance(value, bool):
                            config_args.extend([f"--pr_code_suggestions.{key}", "true" if value else "false"])
                        else:
                            config_args.extend([f"--pr_code_suggestions.{key}", str(value)])

                # pr_description セクション
                if 'pr_description' in config_data:
                    for key, value in config_data['pr_description'].items():
                        if isinstance(value, bool):
                            config_args.extend([f"--pr_description.{key}", "true" if value else "false"])
                        else:
                            config_args.extend([f"--pr_description.{key}", str(value)])

            # カスタムプロンプトを追加
            if custom_prompt:
                config_args.extend(["--pr_reviewer.extra_instructions", custom_prompt])

            # コマンド別の設定
            if pr_command == "improve" and 'num_suggestions' in locals():
                config_args.extend(["--pr_code_suggestions.num_code_suggestions", str(num_suggestions)])

            if pr_command == "review" and 'inline_limit' in locals():
                config_args.extend(["--pr_reviewer.inline_comments_limit", str(inline_limit)])

            status_text.text(f"🔄 PR-Agent {pr_command} コマンドを実行中...")
            progress_bar.progress(25)

            # 環境変数を設定
            env = os.environ.copy()
            env["GITLAB_TOKEN"] = gitlab_token
            env["OPENAI_API_KEY"] = api_key
            env["APIM_USER_ID"] = user_id
            env["CONFIG__GIT_PROVIDER"] = "gitlab"
            env["CONFIG__MODEL"] = model
            env["CONFIG__RESPONSE_LANGUAGE"] = "ja-JP"
            env["GITLAB__URL"] = "https://gitlab.com"
            env["GITLAB__PERSONAL_ACCESS_TOKEN"] = gitlab_token
            env["GITLAB__AUTH_TYPE"] = "oauth_token"

            # PR-Agent実行スクリプト
            pr_agent_dir = tools_dir / "pr-agent"
            runner_script = pr_agent_dir / "tools" / "pr_agent_runner.py"

            cmd = [
                sys.executable,
                str(runner_script),
                "-u", mr_url,
                "--command", pr_command,
                "--config.model", model,
                "--config.git_provider", "gitlab",
                "--config.response_language", "ja-JP"
            ]

            # 設定ファイルから読み込んだ引数を追加
            cmd.extend(config_args)

            if pr_command == "ask" and question:
                cmd.extend(["--question", question])

            progress_bar.progress(50)

            # 実行
            with st.spinner(f"{pr_command} 実行中..."):
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10分タイムアウト
                    cwd=str(pr_agent_dir)
                )

            progress_bar.progress(100)
            status_text.text("✅ 実行完了！")

            if result.returncode == 0:
                st.success("✅ PR-Agentコマンドが正常に完了しました！")

                st.markdown("### 📋 実行内容")
                st.write(f"- **コマンド**: {pr_command}")
                st.write(f"- **MR URL**: {mr_url}")
                st.write(f"- **モデル**: {model}")
                st.write(f"- **設定**: {selected_config}")
                if pr_command == "ask" and question:
                    st.write(f"- **質問**: {question}")
                if custom_prompt:
                    st.write(f"- **カスタムプロンプト**: {custom_prompt}")

                # 出力を表示
                if result.stdout:
                    with st.expander("📄 実行ログ", expanded=False):
                        st.code(result.stdout, language="text")

                st.info("💡 結果はGitLabのマージリクエストページに投稿されました")
            else:
                st.error(f"❌ コマンドがエラーで終了しました (exit code: {result.returncode})")
                if result.stdout:
                    st.code(result.stdout, language="text")
                if result.stderr:
                    with st.expander("⚠️ エラー詳細", expanded=True):
                        st.code(result.stderr, language="text")

        except subprocess.TimeoutExpired:
            st.error("❌ タイムアウトしました。処理に10分以上かかりました。")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")
            st.exception(e)
        finally:
            progress_bar.progress(0)
            status_text.text("")
# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        PR-Agent v1.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
