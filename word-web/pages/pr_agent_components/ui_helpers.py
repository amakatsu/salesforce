# -*- coding: utf-8 -*-
"""
PR-Agent UI ヘルパー関数
"""
import streamlit as st
from .constants import MODAL_STATE_KEY


def close_modal():
    """モーダル状態をクリアするコールバック関数"""
    st.session_state.pop(MODAL_STATE_KEY, None)


def render_result_summary(placeholder, result_state):
    """実行結果サマリーを表示"""
    with placeholder.container():
        if not result_state:
            st.info("実行結果はここに表示されます")
            return

        params = result_state.get('params', {})
        warnings = result_state.get('warnings') or []
        errors = result_state.get('errors') or []
        status = result_state.get('status')

        # ステータス表示
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

        # 実行内容表示
        st.markdown("### 📋 実行内容")
        _render_execution_params(params)

        # フッター
        if status == 'success':
            if params.get('is_preview_mode'):
                st.info("💡 プレビューモードで実行されました。結果はGitLabに投稿されていません。")
            else:
                st.info("💡 結果はGitLabのMRページに投稿されました")
        else:
            st.warning("💡 上記のエラーログを確認して、問題を修正してください")


def _render_execution_params(params: dict):
    """実行パラメータを表示"""
    if params.get('is_preview_mode'):
        st.write("- **実行モード**: 📋 プレビューのみ（投稿なし）")
    else:
        st.write("- **実行モード**: ✅ 実行して投稿")

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
            st.write("- **モデル**: PBkBKGPT0SpkSub001OAI001MDL015")

    if params.get('selected_config'):
        st.write(f"- **設定**: {params['selected_config']}")

    if params.get('pr_command') == "ask" and params.get('question'):
        st.write(f"- **質問**: {params['question']}")

    if params.get('custom_prompt'):
        st.write(f"- **カスタムプロンプト**: {params['custom_prompt']}")


def render_page_header():
    """ページヘッダーを表示"""
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


def render_usage_guide():
    """使い方ガイドを表示"""
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


def apply_sidebar_styles():
    """サイドバーのスタイルを適用"""
    st.markdown("""
    <style>
    /* サイドバーの要素間のマージンを削減 */
    .stSidebar [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    .stSidebar [data-testid="stBlock"]:not(:last-child) {
        margin-bottom: 0.25rem;
    }
    /* セレクトボックス、テキスト入力の下マージンを削減 */
    .stSidebar .stSelectbox, .stSidebar .stTextInput, .stSidebar .stNumberInput {
        margin-bottom: 0.5rem;
    }
    /* マークダウンの上下マージンを削減 */
    .stSidebar .stMarkdown {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    /* 区切り線の上下マージンを削減 */
    .stSidebar hr {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_page_footer():
    """ページフッターを表示"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
            PR-Agent v2.0 | Powered by Streamlit & tool-branch backend
        </div>
        """,
        unsafe_allow_html=True
    )
