#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel単語照合ツール - Webインターフェース (Streamlit)
既存のword.pyを修正せずに利用する
"""
import sys
import shutil
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
# Dockerコンテナ内: /app/pages/1_word_matching.py → /app/.env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 親ディレクトリのwordモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from word.word import process, save_outputs, DEFAULT_CONFIG

# トラッキングをインポート
from usage_tracker import track_usage

# ページ設定
st.set_page_config(
    page_title="Excel単語照合ツール",
    page_icon="📝",
    layout="wide"
)

# ページ訪問記録（初回のみ）
if 'visited_word_matching' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="単語照合")
    st.session_state.visited_word_matching = True

# タイトル
st.title("📝 単語照合ツール")
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 単語 ⇄ 単語帳を照合して物理名を自動提案</h3>
    <p style='color: #e0e7ff; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        LLMが lowerCamelCase の命名を提案 | 未登録語を自動検出
    </p>
</div>
""", unsafe_allow_html=True)

# 使い方ガイド（必要な時だけ開く）
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ 単語帳との照合で一致状況を判定
    - ✅ lowerCamelCase の物理名を提案（例: `customerPersonInChargeName`）
    - ✅ 未登録語を自動検出してリスト化
    - ✅ 結果をExcelで色分け表示

    ---

    ## 🚀 使用手順（4ステップ）

    ### ステップ1️⃣: サイドバーでAPI情報を入力

    **必須項目:**
    - 🔑 **APIキー**: Azure OpenAI APIのキー
    - 👤 **ユーザID**: API ManagementのユーザID

    **オプション:**
    - 📋 Excel列名（通常はデフォルトのままでOK）

    ### ステップ2️⃣: ファイルをアップロード

    | 場所 | 内容 | ファイル名 |
    |------|------|------------|
    | **左側** 📄 | 画面項目定義 | 自由に設定OK |
    | **右側** 📚 | 単語名一覧 | 自由に設定OK |

    **ポイント:**
    - ファイル名は何でもOK（左右の区別で自動判定）
    - 複数ファイルをまとめてアップロード可能
    - ドラッグ&ドロップにも対応

    ### ステップ3️⃣: 照合を実行

    「🚀 照合実行」ボタンをクリック

    - 処理中は進捗バーで状況をリアルタイム確認
    - 例: 「🔄 照合処理を実行中... (45/100件 処理済み)」
    - 大量データは数時間かかることがあります（2000件の場合、30分程度・・）

    ### ステップ4️⃣: 結果を確認・ダウンロード

    **📊 処理サマリ**
    - 完全一致 / 完全一致（部品ごと） / 一部一致 / 一致なし の件数と割合を表示

    **📋 結果プレビュー**
    - 先頭10件をブラウザで即座に確認

    **📥 ダウンロード**
    - 「📥 結果をダウンロード (Excel)」ボタンで取得
    - 未登録語のリスト付き

    ---

    ### 🔍 判定ロジックの詳細

    各画面項目名は以下のステップで判定されます：

    **ステップ1️⃣ 正規化と完全一致チェック**
    - 全角/半角、大文字/小文字を統一して正規化
    - 単語帳と完全一致する場合 → **即座に「完全一致」と判定**（LLM未使用）

    **ステップ2️⃣ 候補語の抽出（類似度計算）**
    - 類似度スコアが閾値（デフォルト0.72）以上の単語を抽出
    - 複合語対策として、単語分解も実施
    - 上位候補を選定

    **ステップ3️⃣ LLMによる詳細判定**
    - 候補語リストをLLMに送信
    - LLMが以下を判定：
      - **完全一致（部品ごと）**: 画面項目名を分解した全ての語が単語帳に存在
        - 例: 「回収稟議番号」→「回収」+「稟議番号」が両方とも単語帳にある
      - **一部一致**: 分解した語の一部が単語帳にあり、一部は未登録
        - 例: 「顧客担当者名」→「顧客」と「名」はあるが「担当者」は未登録
      - **一致なし**: どの語も単語帳に存在しない

    **ステップ4️⃣ 物理名の提案**
    - 候補語の物理名を組み合わせて lowerCamelCase で提案
    - 未登録語は命名規則に従って自動生成
    - 文字数制約（8文字推奨、最大15文字）を考慮

    ### 📊 出力結果の見方
    - **完全一致**: 単語帳に単一語として登録済み。そのまま使用可能
    - **完全一致（部品ごと）**: 分解した全ての語が単語帳に存在。内容確認が必要。未登録語の追加を検討
    - **一部一致**: 内容確認が必要。未登録語の追加を検討
    - **一致なし**: 単語帳への追加が必要

    """)

st.markdown("---")

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    # API設定
    import json
    default_headers = json.loads(DEFAULT_CONFIG["OPENAI_HEADERS_JSON"])
    default_api_key = default_headers.get("api-key", "")
    default_user_id = default_headers.get("apim-user-id", "")

    st.subheader("🔑 API認証情報")
    st.caption("LLM APIに接続するための認証情報を入力してください")
    api_key = st.text_input(
        "APIキー",
        value=default_api_key,
        type="password",
        help="Azure OpenAI APIのキーを入力してください"
    )
    user_id = st.text_input(
        "ユーザID (apim-user-id)",
        value=default_user_id,
        help="API Management のユーザIDを入力してください"
    )

    st.markdown("---")

    # 基本設定
    st.subheader("📋 Excel列名設定")
    st.caption("各Excelファイルで参照する列名を指定してください")
    screen_col = st.text_input(
        "画面項目定義の列名",
        value=DEFAULT_CONFIG["SCREEN_COL"],
        help="画面項目定義ファイルで照合対象となる項目名が記載されている列名"
    )
    vocab_col = st.text_input(
        "単語帳の列名（論理名）",
        value=DEFAULT_CONFIG["VOCAB_TERM_COL"],
        help="単語帳ファイルで論理名が記載されている列名"
    )

    st.markdown("---")

    # LLM設定（上級者向け）
    with st.expander("🔧 LLM設定（上級者向け）", expanded=False):
        st.caption("LLMの動作パラメータを調整できます（通常は変更不要）")
        max_tokens = st.number_input(
            "Max Tokens",
            value=DEFAULT_CONFIG["MAX_TOKENS"],
            min_value=100,
            max_value=800,
            help="LLMが生成する最大トークン数（大きいほど詳細な出力が可能）"
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_CONFIG["TEMPERATURE"],
            step=0.1,
            help="生成の多様性（0に近いほど安定、高いほど創造的）"
        )
        fuzzy_threshold = st.slider(
            "類似度しきい値",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_CONFIG["FUZZY_THRESHOLD"],
            step=0.05,
            help="単語の類似度判定の最低スコア（高いほど厳密に一致）"
        )

# メインエリア
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 画面項目定義ファイル")
    screen_files = st.file_uploader(
        "画面項目定義 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="screen"
    )
    if screen_files:
        st.success(f"✅ {len(screen_files)}件のファイルが選択されました")
        for f in screen_files:
            st.text(f"  • {f.name}")

with col2:
    st.subheader("📚 単語名一覧ファイル")
    vocab_files = st.file_uploader(
        "単語名一覧 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="vocab"
    )
    if vocab_files:
        st.success(f"✅ {len(vocab_files)}件のファイルが選択されました")
        for f in vocab_files:
            st.text(f"  • {f.name}")

st.markdown("---")

# セッション状態の初期化
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
    st.session_state.result_df = None

# 実行ボタン（APIキーとユーザIDが入力されている場合のみ有効）
button_disabled = not (api_key and user_id)
if st.button("🚀 照合実行", type="primary", use_container_width=True, disabled=button_disabled):
    # 実行ボタン押下を記録
    track_usage(action="実行ボタン押下", tool_name="単語照合")

    # 前回の結果をクリア
    st.session_state.processing_done = False
    st.session_state.result_df = None

    if not screen_files or not vocab_files:
        st.error("❌ 画面項目定義ファイルと単語名一覧ファイルの両方を選択してください")
    else:
        # 一時ディレクトリで処理
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # プログレスバー
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # ファイル保存
                status_text.text("📁 ファイルをアップロード中...")
                progress_bar.progress(10)

                # 画面項目定義ファイルを元のファイル名で保存
                for f in screen_files:
                    file_path = tmpdir / f.name
                    file_path.write_bytes(f.read())

                # 単語帳ファイルを元のファイル名で保存
                for f in vocab_files:
                    file_path = tmpdir / f.name
                    file_path.write_bytes(f.read())

                progress_bar.progress(20)

                # 設定の上書き
                config = DEFAULT_CONFIG.copy()
                config["SCREEN_COL"] = screen_col
                config["VOCAB_TERM_COL"] = vocab_col
                config["MAX_TOKENS"] = int(max_tokens)
                config["TEMPERATURE"] = float(temperature)
                config["FUZZY_THRESHOLD"] = float(fuzzy_threshold)
                config["OUT_DIR"] = str(tmpdir / "out")

                # API設定の上書き
                config["OPENAI_HEADERS_JSON"] = json.dumps({"api-key": api_key, "apim-user-id": user_id})

                # 処理実行
                status_text.text("🔄 照合処理を実行中...")
                progress_bar.progress(30)

                # 進捗コールバック関数
                def update_progress(current, total):
                    # 30%から70%の範囲でプログレスバーを更新
                    progress = 30 + int((current / total) * 40)
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 照合処理を実行中... ({current}/{total}件 処理済み)")

                with st.spinner("照合処理中... (数分かかる場合があります)"):
                    try:
                        df = process(tmpdir, screen_col, vocab_col, config, progress_callback=update_progress)
                    except Exception as api_error:
                        # API認証エラーなどをキャッチ
                        error_msg = str(api_error)
                        if "401" in error_msg or "Unauthorized" in error_msg or "api-key" in error_msg.lower():
                            st.error("❌ API認証に失敗しました。APIキーまたはユーザIDを確認してください。")
                        else:
                            st.error(f"❌ 処理中にエラーが発生しました: {error_msg}")
                        raise

                progress_bar.progress(70)

                # 結果保存
                status_text.text("💾 結果を保存中...")
                save_outputs(df, config)

                progress_bar.progress(90)

                # 結果表示
                status_text.text("✅ 処理完了！")
                progress_bar.progress(100)

                st.success("✅ 照合処理が完了しました！")

                # セッションステートに結果を保存
                st.session_state.processing_done = True
                st.session_state.result_df = df

                # サマリ表示
                st.subheader("📊 処理サマリ")
                col_a, col_b, col_c, col_d, col_e = st.columns(5)

                total = len(df)
                exact = len(df[df["match_type"] == "完全一致"])
                exact_parts = len(df[df["match_type"] == "完全一致（部品ごと）"])
                partial = len(df[df["match_type"] == "一部一致"])
                no_match = len(df[df["match_type"] == "一致なし"])

                col_a.metric("合計", f"{total}件")
                col_b.metric("完全一致", f"{exact}件", f"{exact*100/total:.1f}%" if total > 0 else "0%")
                col_c.metric("完全一致(部品)", f"{exact_parts}件", f"{exact_parts*100/total:.1f}%" if total > 0 else "0%")
                col_d.metric("一部一致", f"{partial}件", f"{partial*100/total:.1f}%" if total > 0 else "0%")
                col_e.metric("一致なし", f"{no_match}件", f"{no_match*100/total:.1f}%" if total > 0 else "0%")

                # 結果プレビュー
                st.subheader("📋 結果プレビュー（先頭10件）")
                display_cols = ["screen_item", "match_type", "matched_term", "proposed_name", "reason"]
                preview_df = df[display_cols].head(10)
                st.dataframe(preview_df, use_container_width=True)

                # ダウンロードボタン
                st.markdown("---")
                result_file = Path(config["OUT_DIR"]) / "match_result.xlsx"

                if result_file.exists():
                    with open(result_file, "rb") as f:
                        st.download_button(
                            label="📥 結果をダウンロード (Excel)",
                            data=f.read(),
                            file_name="match_result.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True
                        )

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)
                progress_bar.progress(0)
                status_text.text("")

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        Excel単語照合ツール v1.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
