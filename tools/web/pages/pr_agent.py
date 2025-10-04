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

# tools/pr-agentモジュールのパスを追加
tools_dir = Path(__file__).parent.parent.parent
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

    st.subheader("🔑 API認証情報")

    # デフォルト値を環境変数から取得
    default_gitlab_token = os.getenv("GITLAB_TOKEN", "")
    default_gemini_key = os.getenv("GEMINI_API_KEY", "")

    gitlab_token = st.text_input(
        "GitLab Token",
        value=default_gitlab_token,
        type="password",
        help="GitLabリポジトリにアクセスするためのパーソナルアクセストークン（api scope必須）"
    )
    gemini_api_key = st.text_input(
        "Gemini API Key",
        value=default_gemini_key,
        type="password",
        help="Gemini APIキー（コードレビュー生成用）"
    )

    st.markdown("---")

    st.subheader("🎯 PR-Agentコマンド")
    pr_command = st.selectbox(
        "実行コマンド",
        ["review", "improve", "describe", "ask", "update_changelog", "generate_labels"],
        help="実行するPR-Agentコマンドを選択"
    )

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

    # プリセット
    presets_dir = configs_dir / "presets"
    if presets_dir.exists():
        for config_file in sorted(presets_dir.glob("*.toml")):
            config_options[f"🎯 {config_file.stem}"] = str(config_file)

    # 言語固有
    lang_dir = configs_dir / "language-specific"
    if lang_dir.exists():
        for config_file in sorted(lang_dir.glob("*.toml")):
            config_options[f"🔧 {config_file.stem}"] = str(config_file)

    # テンプレート
    templates_dir = configs_dir / "templates"
    if templates_dir.exists():
        for config_file in sorted(templates_dir.glob("*.toml")):
            config_options[f"📄 {config_file.stem}"] = str(config_file)

    selected_config = st.selectbox(
        "設定ファイル",
        options=list(config_options.keys()),
        help="PR-Agentの動作を制御する設定ファイルを選択"
    )

    config_path = config_options[selected_config]

    # 選択された設定の説明
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
            ["gemini/gemini-2.0-flash", "gemini/gemini-2.5-pro"],
            help="使用するGeminiモデル"
        )

        custom_prompt = st.text_area(
            "カスタムプロンプト（オプション）",
            placeholder="例: XSS脆弱性を重点的にチェック",
            help="設定ファイルに追加の指示を付与"
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

mr_url = st.text_input(
    "マージリクエストURL",
    placeholder="https://gitlab.com/group/project/-/merge_requests/1",
    help="レビュー対象のGitLab MR URL"
)

st.markdown("---")

# 実行ボタン（APIキーとMR URLが入力されている場合のみ有効）
button_disabled = not (gitlab_token and gemini_api_key and mr_url)
if pr_command == "ask":
    button_disabled = button_disabled or not question

if st.button("🚀 PR-Agent実行", type="primary", use_container_width=True, disabled=button_disabled):
    if not gitlab_token or not gemini_api_key:
        st.error("❌ GitLab TokenとGemini API Keyを入力してください")
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
            env["GEMINI_API_KEY"] = gemini_api_key
            env["GOOGLE_AI_STUDIO__GEMINI_API_KEY"] = gemini_api_key
            env["OPENAI_API_KEY"] = ""
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
