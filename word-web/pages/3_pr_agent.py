#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import tempfile
from pathlib import Path

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
    github_token = st.text_input(
        "GitHub Token",
        type="password",
        help="GitHubリポジトリにアクセスするためのパーソナルアクセストークン"
    )
    llm_api_key = st.text_input(
        "LLM API Key",
        type="password",
        help="コードレビュー生成用のLLM APIキー"
    )

    st.markdown("---")

    st.subheader("🎯 レビュー項目")
    review_code_quality = st.checkbox("コード品質", value=True)
    review_security = st.checkbox("セキュリティ", value=True)
    review_performance = st.checkbox("パフォーマンス", value=True)
    review_tests = st.checkbox("テストカバレッジ", value=True)
    review_docs = st.checkbox("ドキュメント", value=False)

    st.markdown("---")

    with st.expander("🔧 詳細設定", expanded=False):
        review_depth = st.selectbox(
            "レビューの詳細度",
            ["簡易", "標準", "詳細"],
            index=1
        )
        max_comments = st.slider(
            "最大コメント数",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )

# メインエリア - タブで切り替え
tab1, tab2 = st.tabs(["🔗 GitHubリポジトリから", "📁 ローカルファイルから"])

with tab1:
    st.subheader("GitHub プルリクエスト情報")

    repo_url = st.text_input(
        "リポジトリURL",
        placeholder="https://github.com/owner/repo",
        help="レビュー対象のGitHubリポジトリURL"
    )

    col1, col2 = st.columns(2)
    with col1:
        branch_name = st.text_input(
            "ブランチ名",
            placeholder="feature/new-feature",
            help="レビュー対象のブランチ名"
        )
    with col2:
        pr_number = st.number_input(
            "PR番号",
            min_value=1,
            value=1,
            help="プルリクエスト番号"
        )

    if st.button("🚀 GitHubからレビュー実行", type="primary", use_container_width=True, disabled=not (github_token and llm_api_key and repo_url)):
        if not github_token or not llm_api_key:
            st.error("❌ GitHub TokenとLLM API Keyを入力してください")
        elif not repo_url:
            st.error("❌ リポジトリURLを入力してください")
        else:
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔄 GitHubからプルリクエスト情報を取得中...")
                progress_bar.progress(25)

                # TODO: GitHub API連携を実装
                import time
                time.sleep(1)

                status_text.text("🔄 コードを分析中...")
                progress_bar.progress(50)

                time.sleep(1)

                status_text.text("🔄 LLMでレビューを生成中...")
                progress_bar.progress(75)

                time.sleep(1)

                progress_bar.progress(100)
                status_text.text("✅ レビュー完了！")

                st.success("✅ レビューが完了しました！")
                show_review_results()

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)

with tab2:
    st.subheader("📄 変更ファイル")

    uploaded_files = st.file_uploader(
        "変更されたファイル",
        accept_multiple_files=True,
        help="レビュー対象のコードファイルをアップロード"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)}件のファイルが選択されました")
        for f in uploaded_files:
            st.text(f"  • {f.name}")

    if st.button("🚀 ローカルファイルをレビュー実行", type="primary", use_container_width=True, disabled=not (llm_api_key and uploaded_files)):
        if not llm_api_key:
            st.error("❌ LLM API Keyを入力してください")
        elif not uploaded_files:
            st.error("❌ レビュー対象のファイルをアップロードしてください")
        else:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir = Path(tmpdir)

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("📁 ファイルをアップロード中...")
                    progress_bar.progress(20)

                    for f in uploaded_files:
                        file_path = tmpdir / f.name
                        file_path.write_bytes(f.read())

                    status_text.text("🔄 コードを分析中...")
                    progress_bar.progress(50)

                    # TODO: 実際のコード分析ロジックを実装
                    import time
                    time.sleep(1)

                    status_text.text("🔄 LLMでレビューを生成中...")
                    progress_bar.progress(75)

                    time.sleep(1)

                    progress_bar.progress(100)
                    status_text.text("✅ レビュー完了！")

                    st.success("✅ レビューが完了しました！")
                    show_review_results()

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)


def show_review_results():
    """レビュー結果を表示する関数（ダミーデータ）"""

    st.markdown("---")
    st.subheader("📊 レビュー結果サマリ")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("総合スコア", "85/100", delta="5")
    col2.metric("重大な問題", "2件", delta="-1", delta_color="inverse")
    col3.metric("改善提案", "8件")
    col4.metric("コードカバレッジ", "78%", delta="3%")

    # レビューコメント
    st.subheader("💬 レビューコメント")

    with st.expander("🔴 重大な問題 (2件)", expanded=True):
        st.markdown("""
        **1. セキュリティ: SQLインジェクションの脆弱性**
        - ファイル: `src/database/query.py:45`
        - 問題: ユーザー入力が直接SQLクエリに連結されています
        - 提案: プレースホルダーを使用してパラメータ化クエリに変更してください

        ```python
        # 修正前
        query = f"SELECT * FROM users WHERE id = {user_id}"

        # 修正後
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        ```

        **2. パフォーマンス: N+1クエリ問題**
        - ファイル: `src/api/handlers.py:120`
        - 問題: ループ内でデータベースクエリを実行しています
        - 提案: 一括取得またはJOINを使用してください
        """)

    with st.expander("🟡 改善提案 (8件)", expanded=False):
        st.markdown("""
        1. **コードの重複** - `utils.py:30-50` と `helpers.py:15-35` で類似コードが検出されました
        2. **命名規則** - 変数名 `tmp` は意味が不明確です。より説明的な名前に変更してください
        3. **エラーハンドリング** - 例外をキャッチしていますが、ログ出力がありません
        4. **型ヒント** - 関数の戻り値に型ヒントがありません
        5. **コメント不足** - 複雑なロジックにコメントを追加してください
        6. **マジックナンバー** - 定数 `100` を使用していますが、意味を明確にしてください
        7. **未使用インポート** - `datetime` がインポートされていますが使用されていません
        8. **長すぎる関数** - `process_data()` は80行あります。分割を検討してください
        """)

    with st.expander("✅ 良い点", expanded=False):
        st.markdown("""
        - テストカバレッジが高い (78%)
        - エラーハンドリングが適切に実装されています
        - ドキュメント文字列が充実しています
        - 一貫したコーディングスタイル
        """)

    # テスト提案
    st.subheader("🧪 テストケース提案")

    st.code("""
def test_user_authentication_with_invalid_credentials():
    \"\"\"無効な認証情報でログインを試みた場合のテスト\"\"\"
    response = client.post('/login', json={
        'username': 'test_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 401
    assert 'error' in response.json()

def test_sql_injection_prevention():
    \"\"\"SQLインジェクション対策のテスト\"\"\"
    malicious_input = "1; DROP TABLE users--"
    response = client.get(f'/users/{malicious_input}')
    # エラーが返され、テーブルが削除されないことを確認
    assert response.status_code in [400, 404]
    """, language="python")

    st.info("💡 実際のPR-Agent機能を実装する必要があります")


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
