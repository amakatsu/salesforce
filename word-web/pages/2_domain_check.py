#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメインチェックツール - Webインターフェース (Streamlit)
"""
import sys
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path

# 親ディレクトリのwordモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from word.domain_check import (
    load_screen_items, load_domains,
    process_screen_domain_matching,
    save_outputs, DEFAULT_CONFIG
)
import json

# ページ設定
st.set_page_config(
    page_title="ドメイン照合ツール",
    page_icon="🔍",
    layout="wide"
)

# タイトル
st.title("🔍 ドメイン照合ツール")
st.markdown("""
<div style='background: linear-gradient(90deg, #f56565 0%, #ed8936 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 画面項目のドメイン存在チェックと提案</h3>
    <p style='color: #fff5f5; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        画面項目定義に対応するドメインの存在をチェックし、存在しない場合は新規ドメインを提案します
    </p>
</div>
""", unsafe_allow_html=True)

# 使い方ガイド
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ 画面項目に対応するドメインの存在チェック（完全一致・類似一致）
    - ✅ 存在するドメインの情報を自動取得
    - ✅ ドメインが存在しない項目への新規ドメイン提案
    - ✅ 画面項目定義の長さ・編集形式から新規ドメイン定義を自動生成

    ---

    ## 🚀 使用手順

    ### ステップ1️⃣: ファイルをアップロード

    - **画面項目定義**: 項目名称、フィールドタイプ、長さ、編集形式、必須チェック
    - **ドメイン定義一覧**: ドメイン名、データ型、最小/最大文字数、最小/最大値、書式正規表現、参照外部コードIDなど

    ### ステップ2️⃣: 存在チェック実行

    「🚀 チェック実行」ボタンをクリック

    ### ステップ3️⃣: 結果を確認

    - **完全一致**: 対応するドメインが存在。ドメイン定義の全情報を自動取得
    - **類似一致**: 類似するドメインが存在。そのドメイン情報を表示（類似度も表示）
    - **不一致（提案必要）**: ドメインが存在せず、画面項目に長さ制約や編集形式があるため、新規ドメイン提案を自動生成
    - **不一致（チェック不要）**: ドメインが存在しないが、長さ・編集形式の定義もないため、ドメイン設定不要と判断
    """)

st.markdown("---")

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    with st.expander("🔧 類似度設定", expanded=False):
        fuzzy_threshold = st.slider(
            "類似一致の閾値",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_CONFIG["FUZZY_THRESHOLD"],
            step=0.05,
            help="類似度判定の最低スコア（高いほど厳密）"
        )

# メインエリア
st.subheader("📄 入力ファイル")

col1, col2 = st.columns(2)

with col1:
    st.caption("画面項目定義ファイル（必須）")
    screen_files = st.file_uploader(
        "画面項目定義 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="screen",
        help="項目名称、フィールドタイプ、長さ、編集形式、必須チェック"
    )
    if screen_files:
        st.success(f"✅ {len(screen_files)}件")
        for f in screen_files:
            st.text(f"  • {f.name}")

with col2:
    st.caption("ドメイン定義ファイル（必須）")
    domain_files = st.file_uploader(
        "ドメイン定義 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="domain",
        help="ドメイン名、データ型、最大文字数、コード値など"
    )
    if domain_files:
        st.success(f"✅ {len(domain_files)}件")
        for f in domain_files:
            st.text(f"  • {f.name}")

st.markdown("---")

# セッション状態の初期化
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
    st.session_state.result_df = None

# 実行ボタン
button_disabled = not (screen_files and domain_files)
if st.button("🚀 チェック実行", type="primary", use_container_width=True, disabled=button_disabled):
    # 前回の結果をクリア
    st.session_state.processing_done = False
    st.session_state.result_df = None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # プログレスバー
            progress_bar = st.progress(0)
            status_text = st.empty()

            # ファイル保存
            status_text.text("📁 ファイルをアップロード中...")
            progress_bar.progress(10)

            # 画面項目定義ファイル
            for i, f in enumerate(screen_files):
                file_path = tmpdir / f.name
                file_path.write_bytes(f.read())

            # ドメイン定義ファイル
            for i, f in enumerate(domain_files):
                file_path = tmpdir / f.name
                file_path.write_bytes(f.read())

            progress_bar.progress(20)

            # 設定の上書き
            config = DEFAULT_CONFIG.copy()
            config["FUZZY_THRESHOLD"] = float(fuzzy_threshold)
            config["OUT_DIR"] = str(tmpdir / "out")

            # データ読み込み
            status_text.text("📂 データを読み込み中...")
            progress_bar.progress(30)

            screen_items = load_screen_items(tmpdir, config)
            domains = load_domains(tmpdir, config)

            progress_bar.progress(50)

            # 突合処理
            status_text.text("🔄 画面項目とドメインを突合中...")

            with st.spinner("突合処理中..."):
                df_result = process_screen_domain_matching(screen_items, domains, config)

            progress_bar.progress(80)

            # 結果保存
            status_text.text("💾 結果を保存中...")
            save_outputs(df_result, config)

            progress_bar.progress(100)
            status_text.text("✅ 処理完了！")

            st.success("✅ チェック処理が完了しました！")

            # セッションステートに結果を保存
            st.session_state.processing_done = True
            st.session_state.result_df = df_result

            # サマリ表示
            st.subheader("📊 処理サマリ")
            col1, col2, col3, col4 = st.columns(4)

            total = len(df_result)
            exact = len(df_result[df_result['判定結果'] == '完全一致'])
            similar = len(df_result[df_result['判定結果'] == '類似一致'])
            need_suggest = len(df_result[df_result['判定結果'] == '不一致（提案必要）'])
            no_check = len(df_result[df_result['判定結果'] == '不一致（チェック不要）'])

            col1.metric("総項目数", f"{total}件")
            col2.metric("完全一致", f"{exact}件", f"{exact*100/total:.1f}%" if total > 0 else "0%")
            col3.metric("類似一致", f"{similar}件", f"{similar*100/total:.1f}%" if total > 0 else "0%")
            col4.metric("提案必要", f"{need_suggest}件", f"{need_suggest*100/total:.1f}%" if total > 0 else "0%")

            # プレビュー
            st.subheader("📋 結果プレビュー（先頭10件）")
            display_cols = ["項目名称", "判定結果", "一致ドメイン名", "類似度", "データ型", "最大文字数", "参照外部コードID"]
            preview_df = df_result[display_cols].head(10) if all(col in df_result.columns for col in display_cols) else df_result.head(10)
            st.dataframe(preview_df, use_container_width=True)

            # ダウンロードボタン
            st.markdown("---")
            out_dir = Path(config["OUT_DIR"])
            result_file = out_dir / "screen_domain_check.xlsx"

            if result_file.exists():
                with open(result_file, "rb") as f:
                    st.download_button(
                        label="📥 結果をダウンロード (Excel)",
                        data=f.read(),
                        file_name="screen_domain_check.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )

    except Exception as e:
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.exception(e)

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        ドメイン照合ツール v1.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
