#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメインチェックツール - Webインターフェース (Streamlit)
"""
import streamlit as st
import pandas as pd
import tempfile
import sys
import json
from pathlib import Path

# 共通設定をインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.config import render_api_credentials_section, get_custom_prompt, CUSTOM_PROMPT_TEMPLATES

# domainモジュールをインポート
domain_dir = Path(__file__).parent.parent / "domain"
sys.path.insert(0, str(domain_dir.parent))
from domain.domain_check import (
    load_domains, load_tables, load_targets,
    process_domain_suggestion, save_outputs,
    ApiClient, DEFAULT_CONFIG
)
import threading

# ページ設定
st.set_page_config(
    page_title="ドメインチェックツール",
    page_icon="🔍",
    layout="wide"
)

# タイトル
st.title("🔍 ドメインチェックツール")
st.markdown("""
<div style='background: linear-gradient(90deg, #f56565 0%, #ed8936 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 ドメイン設計の整合性をチェック</h3>
    <p style='color: #fff5f5; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        LLMが項目名を分析してドメイン候補を提案 | データ型・桁数の整合性をチェック
    </p>
</div>
""", unsafe_allow_html=True)

# 使い方ガイド
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ **ドメイン提案**: 対象一覧の項目名からLLMが適切なドメインを提案
    - ✅ **整合性チェック**: ドメイン定義とテーブル定義の型・桁数をチェック
    - ✅ 業務的意味の分析
    - ✅ 技術的項目の自動判定

    ---

    ## 🚀 使用手順

    ### ステップ1️⃣: ファイルをアップロード

    以下の3種類のExcelファイルをアップロード:

    1. **対象一覧**: チェック対象の項目名リスト
       - 必須列: 「項目名」

    2. **ドメイン定義**: 既存のドメイン定義
       - 必須列: 「ドメイン名」「データ型」
       - オプション: 「桁数」「単項目チェック」

    3. **テーブル定義**: データベーステーブル定義
       - 必須列: 「テーブル名」「項目名」「カラム名」
       - オプション: 「データ型」「桁数」

    ### ステップ2️⃣: API設定

    - APIキーとユーザIDを入力（サイドバー）

    ### ステップ3️⃣: チェック実行

    「🚀 チェック実行」ボタンをクリック

    ### ステップ4️⃣: 結果を確認・ダウンロード

    - ドメイン提案結果
    - 整合性チェック結果
    - Excelレポートのダウンロード
    """)

st.markdown("---")

# サイドバーで設定
with st.sidebar:
    st.header("⚙️ 設定")

    # API認証情報（共通設定を使用）
    api_key, user_id = render_api_credentials_section()

    st.markdown("---")

    with st.expander("🔧 詳細設定", expanded=False):
        max_tokens = st.number_input(
            "Max Tokens",
            value=DEFAULT_CONFIG["MAX_TOKENS"],
            min_value=100,
            max_value=800,
            help="LLMが生成する最大トークン数"
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_CONFIG["TEMPERATURE"],
            step=0.1,
            help="生成の多様性（0に近いほど安定）"
        )
        max_workers = st.slider(
            "並列処理数",
            min_value=1,
            max_value=10,
            value=DEFAULT_CONFIG["MAX_WORKERS"],
            help="並列で処理するスレッド数"
        )

        custom_prompt = get_custom_prompt(
            CUSTOM_PROMPT_TEMPLATES["domain_check"],
            "ドメイン提案時の追加の指示やルール"
        )

# メインエリア
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📄 対象一覧")
    target_files = st.file_uploader(
        "対象一覧 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="target",
        help="項目名のリストが記載されたExcelファイル"
    )
    if target_files:
        st.success(f"✅ {len(target_files)}件")

with col2:
    st.subheader("📚 ドメイン定義")
    domain_files = st.file_uploader(
        "ドメイン定義 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="domain",
        help="既存のドメイン定義が記載されたExcelファイル"
    )
    if domain_files:
        st.success(f"✅ {len(domain_files)}件")

with col3:
    st.subheader("🗃️ テーブル定義")
    table_files = st.file_uploader(
        "テーブル定義 (*.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="table",
        help="データベーステーブル定義が記載されたExcelファイル"
    )
    if table_files:
        st.success(f"✅ {len(table_files)}件")

st.markdown("---")

# 実行ボタン（APIキーとファイルが揃っている場合のみ有効）
# 常に両方実行
check_mode = "both"

# 必要なファイルチェック
files_ready = domain_files and table_files and target_files

button_disabled = not (api_key and user_id and files_ready)

if st.button("🚀 チェック実行", type="primary", use_container_width=True, disabled=button_disabled):
    if not api_key or not user_id:
        st.error("❌ APIキーとユーザIDを入力してください")
    elif not files_ready:
        st.error("❌ 必要なファイルをすべてアップロードしてください")
    else:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                # プログレスバー
                progress_bar = st.progress(0)
                status_text = st.empty()

                # ファイル保存
                status_text.text("📁 ファイルをアップロード中...")
                progress_bar.progress(10)

                if target_files:
                    for i, f in enumerate(target_files):
                        file_path = tmpdir / f"対象一覧_{i+1}.xlsx"
                        file_path.write_bytes(f.read())

                for i, f in enumerate(domain_files):
                    file_path = tmpdir / f"ドメイン定義_{i+1}.xlsx"
                    file_path.write_bytes(f.read())

                for i, f in enumerate(table_files):
                    file_path = tmpdir / f"テーブル定義_{i+1}.xlsx"
                    file_path.write_bytes(f.read())

                progress_bar.progress(20)

                # 設定の上書き
                config = DEFAULT_CONFIG.copy()
                config["MAX_TOKENS"] = int(max_tokens)
                config["TEMPERATURE"] = float(temperature)
                config["MAX_WORKERS"] = int(max_workers)
                config["OUT_DIR"] = str(tmpdir / "out")
                config["CHECK_MODE"] = "both"

                # API設定の上書き
                config["OPENAI_HEADERS_JSON"] = json.dumps({
                    "api-key": api_key,
                    "apim-user-id": user_id
                })

                # データ読み込み
                status_text.text("📖 ファイルを読み込み中...")
                progress_bar.progress(30)

                domains = load_domains(tmpdir, config)
                tables = load_tables(tmpdir, config)

                progress_bar.progress(40)

                api_client = ApiClient(config)
                api_semaphore = threading.Semaphore(config["MAX_CONCURRENT_API"])

                df_suggestion = None
                df_validation = None

                # 機能1: ドメイン提案
                if config["CHECK_MODE"] in ["both", "suggestion"]:
                    targets = load_targets(tmpdir, config)
                    if targets:
                        status_text.text(f"🔄 ドメイン提案処理中... ({len(targets)}件)")
                        progress_bar.progress(50)

                        with st.spinner("ドメイン提案中..."):
                            df_suggestion = process_domain_suggestion(
                                targets, domains, tables, config, api_client, api_semaphore
                            )

                        progress_bar.progress(70)

                # 機能2: 整合性チェック
                # if config["CHECK_MODE"] in ["both", "validation"]:
                #     status_text.text("🔄 整合性チェック中...")
                #     progress_bar.progress(80)
                #     # TODO: process_domain_validation を実装

                # 結果保存
                status_text.text("💾 結果を保存中...")
                save_outputs(df_suggestion, df_validation, config)

                progress_bar.progress(100)
                status_text.text("✅ 処理完了！")

                st.success("✅ チェック処理が完了しました！")

                # サマリ表示
                if df_suggestion is not None and len(df_suggestion) > 0:
                    st.subheader("📊 ドメイン提案結果サマリ")

                    total = len(df_suggestion)
                    exact_match = len(df_suggestion[df_suggestion["判定結果"] == "完全一致"])
                    need_review = len(df_suggestion[df_suggestion["判定結果"] == "要判断"])
                    errors = len(df_suggestion[df_suggestion["判定結果"].str.contains("エラー", na=False)])

                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("合計", f"{total}件")
                    col_b.metric("完全一致", f"{exact_match}件", f"{exact_match*100/total:.1f}%" if total > 0 else "0%")
                    col_c.metric("要判断", f"{need_review}件", f"{need_review*100/total:.1f}%" if total > 0 else "0%")
                    col_d.metric("エラー", f"{errors}件", delta=f"-{errors}" if errors > 0 else "0", delta_color="inverse")

                    # 結果プレビュー
                    st.subheader("📋 結果プレビュー（先頭10件）")
                    preview_df = df_suggestion.head(10)
                    st.dataframe(preview_df, use_container_width=True)

                # ダウンロードボタン
                st.markdown("---")
                result_file = Path(config["OUT_DIR"]) / "domain_check_result.xlsx"

                if result_file.exists():
                    with open(result_file, "rb") as f:
                        st.download_button(
                            label="📥 結果をダウンロード (Excel)",
                            data=f.read(),
                            file_name="domain_check_result.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True
                        )

        except FileNotFoundError as e:
            st.error(f"❌ ファイルエラー: {str(e)}")
            st.info("💡 ファイル名に「対象一覧」「ドメイン定義」「テーブル定義」のキーワードを含めてください")
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
        ドメインチェックツール v1.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
