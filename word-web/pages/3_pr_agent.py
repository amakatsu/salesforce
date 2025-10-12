#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import sys
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

# バックエンドモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from word.pr_agent_backend import PRAgentRunner, ConfigManager, Logger

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
    - Azure OpenAI API キーとユーザID（レビュー生成用）

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

    st.subheader("🔑 API認証情報")

    # GitLab Token
    default_token = os.getenv("GITLAB_TOKEN", "")
    gitlab_token = st.text_input(
        "GitLab Token",
        value=default_token,
        type="password",
        help="GitLabリポジトリにアクセスするためのパーソナルアクセストークン（api scope必須）"
    )

    # OpenAI API設定
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input(
        "APIキー",
        value=default_api_key,
        type="password",
        help="Azure OpenAI APIのキーを入力してください"
    )

    default_user_id = os.getenv("APIM_USER_ID", "")
    user_id = st.text_input(
        "ユーザID",
        value=default_user_id,
        help="API Management のユーザIDを入力してください"
    )

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
        # LLMモデル選択
        model_options = [
            "gemini/gemini-2.0-flash",
            "gemini/gemini-1.5-pro",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]
        selected_model = st.selectbox(
            "LLMモデル",
            model_options,
            help="使用するLLMモデルを選択"
        )

        # カスタムプロンプト
        custom_prompt = st.text_area(
            "カスタムプロンプト",
            placeholder="例: XSS脆弱性を重点的にチェック\nメモリ使用量を最適化",
            height=100,
            help="レビューに適用する追加の指示やコンテキスト情報"
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
            import urllib.parse

            # GitLab MR一覧を取得
            match = re.match(r'https://gitlab\.com/(.+)', project_url.rstrip('/'))
            if match:
                project_path = match.group(1)
                # URLエンコード
                encoded_project = urllib.parse.quote(project_path, safe='')

                # GitLab API でMR一覧を取得
                headers = {
                    "PRIVATE-TOKEN": gitlab_token
                }
                api_url = f"https://gitlab.com/api/v4/projects/{encoded_project}/merge_requests"

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
                st.warning("有効なGitLabプロジェクトURLを入力してください")

        except Exception as e:
            st.error(f"エラー: {str(e)}")
    elif project_url and not gitlab_token:
        st.warning("⚠️ GitLab Tokenを入力してください")

st.markdown("---")

# 実行ボタン
button_disabled = not (gitlab_token and api_key and user_id and pr_url)
if pr_command == "ask":
    button_disabled = button_disabled or not question

if st.button("🚀 PR-Agent実行", type="primary", use_container_width=True, disabled=button_disabled):
    if not gitlab_token or not api_key or not user_id:
        st.error("❌ GitLab Token、APIキー、ユーザIDを入力してください")
    elif not pr_url:
        st.error("❌ MR URLを入力してください")
    elif pr_command == "ask" and not question:
        st.error("❌ askコマンドには質問内容が必要です")
    else:
        try:
            # API認証情報を環境変数に設定
            os.environ['GITLAB_TOKEN'] = gitlab_token
            os.environ['OPENAI_API_KEY'] = api_key
            os.environ['APIM_USER_ID'] = user_id

            progress_bar = st.progress(0)
            status_text = st.empty()

            # 設定ファイルを適用
            status_text.text("⚙️ 設定ファイルを適用中...")
            progress_bar.progress(10)

            if config_path:
                # 選択された設定ファイルを適用
                config_manager.apply_config(config_path, custom_prompt)
            else:
                # デフォルト設定を作成
                config_manager.create_default_config(custom_prompt)

            status_text.text(f"🔄 PR-Agent {pr_command} コマンドを実行中...")
            progress_bar.progress(30)

            # PR-Agentを実行
            extra_args = []
            if pr_command == "ask" and question:
                extra_args.append(question)

            async def run_agent():
                runner = PRAgentRunner()
                return await runner.run(pr_url, pr_command, extra_args)

            result = asyncio.run(run_agent())

            progress_bar.progress(100)

            if result:
                status_text.text("✅ 実行完了！")
                st.success("✅ PR-Agentコマンドが正常に完了しました！")

                st.markdown("### 📋 実行内容")
                st.write(f"- **コマンド**: {pr_command}")
                st.write(f"- **MR URL**: {pr_url}")
                st.write(f"- **モデル**: {selected_model}")
                st.write(f"- **設定**: {selected_config}")
                if pr_command == "ask" and question:
                    st.write(f"- **質問**: {question}")
                if custom_prompt:
                    st.write(f"- **カスタムプロンプト**: {custom_prompt}")

                st.info("💡 結果はGitLabのMRページに投稿されました")
            else:
                status_text.text("❌ レビュー失敗")
                st.error("❌ レビュー中にエラーが発生しました")

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
        PR-Agent v2.0 | Powered by Streamlit & tool-branch backend
    </div>
    """,
    unsafe_allow_html=True
)
