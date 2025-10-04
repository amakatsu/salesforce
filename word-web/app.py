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

# 親ディレクトリのwordモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from word.word import process, save_outputs, DEFAULT_CONFIG

# ページ設定
st.set_page_config(
    page_title="Excel単語照合ツール",
    page_icon="📝",
    layout="wide"
)

# タイトル
st.title("📝 Excel単語照合ツール")
st.markdown("---")

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    # 基本設定
    screen_col = st.text_input("画面項目定義の列名", value=DEFAULT_CONFIG["SCREEN_COL"])
    vocab_col = st.text_input("単語帳の列名（論理名）", value=DEFAULT_CONFIG["VOCAB_TERM_COL"])

    st.markdown("---")

    # LLM設定（上級者向け）
    with st.expander("🔧 LLM設定（上級者向け）", expanded=False):
        max_tokens = st.number_input("Max Tokens", value=DEFAULT_CONFIG["MAX_TOKENS"], min_value=100, max_value=4000)
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=DEFAULT_CONFIG["TEMPERATURE"], step=0.1)
        fuzzy_threshold = st.slider("類似度しきい値", min_value=0.0, max_value=1.0, value=DEFAULT_CONFIG["FUZZY_THRESHOLD"], step=0.05)
        max_workers = st.number_input("並列処理数", value=DEFAULT_CONFIG["MAX_WORKERS"], min_value=1, max_value=20)

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

# 実行ボタン
if st.button("🚀 照合実行", type="primary", use_container_width=True):
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

                for f in screen_files:
                    file_path = tmpdir / f.name
                    file_path.write_bytes(f.read())

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
                config["MAX_WORKERS"] = int(max_workers)
                config["OUT_DIR"] = str(tmpdir / "out")

                # 処理実行
                status_text.text("🔄 照合処理を実行中...")
                progress_bar.progress(30)

                with st.spinner("照合処理中... (数分かかる場合があります)"):
                    df = process(tmpdir, screen_col, vocab_col, config)

                progress_bar.progress(70)

                # 結果保存
                status_text.text("💾 結果を保存中...")
                save_outputs(df, config)

                progress_bar.progress(90)

                # 結果表示
                status_text.text("✅ 処理完了！")
                progress_bar.progress(100)

                st.success("✅ 照合処理が完了しました！")

                # サマリ表示
                st.subheader("📊 処理サマリ")
                col_a, col_b, col_c, col_d = st.columns(4)

                total = len(df)
                exact = len(df[df["match_type"] == "完全一致"])
                partial = len(df[df["match_type"] == "一部一致"])
                no_match = len(df[df["match_type"] == "一致なし"])

                col_a.metric("合計", f"{total}件")
                col_b.metric("完全一致", f"{exact}件", f"{exact*100/total:.1f}%" if total > 0 else "0%")
                col_c.metric("一部一致", f"{partial}件", f"{partial*100/total:.1f}%" if total > 0 else "0%")
                col_d.metric("一致なし", f"{no_match}件", f"{no_match*100/total:.1f}%" if total > 0 else "0%")

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
