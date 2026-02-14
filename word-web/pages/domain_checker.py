#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメインチェックツール - Webインターフェース (Streamlit)

画面項目定義 + テーブル定義 + ドメイン定義の3ファイルを読み込み、
ドメインの存在チェックと新規ドメイン提案を行う。
"""
import sys
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path

# 親ディレクトリのwordモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from word.domain import (
    load_screen_items,
    load_domains,
    load_table_definitions,
    dedup_by_name_and_digits,
    process_screen_domain_matching,
    process_table_domain_matching,
    save_domain_check_results,
)
from word.config import get_domain_config
from pages.util.usage_tracker import track_usage


# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------

DOMAIN_CONFIG = get_domain_config()

RESULT_DISPLAY_COLUMNS = [
    "項目名称", "判定結果", "一致ドメイン名", "備考",
    "型", "D_データ型", "D_参照外部コード",
]


# ---------------------------------------------------------------------------
# セッション状態
# ---------------------------------------------------------------------------

def _init_session_state():
    """結果保持用の session_state を初期化する。"""
    defaults = {
        "processing_done": False,
        "screen_result_df": None,
        "table_result_df": None,
        "result_excel_bytes": None,
        "result_filename": "domain_check_results.xlsx",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_results():
    """前回の結果をクリアする。"""
    st.session_state.processing_done = False
    st.session_state.screen_result_df = None
    st.session_state.table_result_df = None
    st.session_state.result_excel_bytes = None


# ---------------------------------------------------------------------------
# ファイルアップロード UI
# ---------------------------------------------------------------------------

def _render_file_uploaders():
    """3つのファイルアップローダーを配置し、ファイルリストを返す。"""
    st.subheader("📄 入力ファイル")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("画面項目定義ファイル（必須）")
        screen_files = st.file_uploader(
            "画面項目定義 (*.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True,
            key="screen",
            help="項目名称、型、テキストタイプ、桁数、外部コード",
        )
        if screen_files:
            st.success(f"✅ {len(screen_files)}件")
            for f in screen_files:
                st.text(f"  • {f.name}")

    with col2:
        st.caption("テーブル定義ファイル（必須）")
        table_files = st.file_uploader(
            "テーブル定義 (*.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True,
            key="table",
            help="論理項目名、データ型、Length、全体数値、少数桁",
        )
        if table_files:
            st.success(f"✅ {len(table_files)}件")
            for f in table_files:
                st.text(f"  • {f.name}")

    with col3:
        st.caption("ドメイン定義ファイル（必須）")
        domain_files = st.file_uploader(
            "ドメイン定義 (*.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True,
            key="domain",
            help="ドメイン名、データ型、文字数、バイト長、桁数、書式、参照外部コード",
        )
        if domain_files:
            st.success(f"✅ {len(domain_files)}件")
            for f in domain_files:
                st.text(f"  • {f.name}")

    return screen_files, table_files, domain_files


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def _save_files_to_tmpdir(files, tmpdir, label, detail_text):
    """アップロードファイルを一時ディレクトリに保存する。"""
    for i, f in enumerate(files):
        (tmpdir / f.name).write_bytes(f.read())
        detail_text.text(f"{label}保存中: {i + 1}/{len(files)} - {f.name}")


def _run_domain_check(screen_files, table_files, domain_files, fuzzy_threshold):
    """ドメインチェック全工程を実行し、結果を session_state に保存する。"""
    track_usage(action="実行ボタン押下", tool_name="ドメイン照合")
    _clear_results()

    progress = st.progress(0)
    status = st.empty()
    detail = st.empty()

    try:
        with tempfile.TemporaryDirectory() as tmpdir_str:
            tmpdir = Path(tmpdir_str)
            config = DOMAIN_CONFIG.copy()
            config["FUZZY_THRESHOLD"] = float(fuzzy_threshold)
            config["OUT_DIR"] = str(tmpdir / "out")

            # Step 1: ファイル保存
            status.text("📁 ステップ 1/5: ファイルを保存中...")
            file_summary = (
                f"画面項目定義: {len(screen_files)}件、"
                f"テーブル定義: {len(table_files)}件、"
                f"ドメイン定義: {len(domain_files)}件"
            )
            detail.text(file_summary)
            progress.progress(5)

            _save_files_to_tmpdir(screen_files, tmpdir, "画面項目定義", detail)
            _save_files_to_tmpdir(table_files, tmpdir, "テーブル定義", detail)
            _save_files_to_tmpdir(domain_files, tmpdir, "ドメイン定義", detail)
            progress.progress(15)

            # Step 2: データ読み込み
            screen_items, table_items, domains = _load_all_data(
                tmpdir, config, progress, status, detail,
            )

            # Step 3: 照合処理（全件対象 → 抽出シート用の生データ兼用）
            screen_df, table_df = _run_matching(
                screen_items, table_items, domains, config, progress, status, detail,
            )

            # Step 4: 重複排除（照合済みDFに対して数字除去+桁数で集約）
            screen_dedup_df, table_dedup_df = _dedup_results(
                screen_df, table_df, progress, status, detail,
            )

            # Step 5: 結果保存（4シート: 抽出×2 + 重複排除×2）
            _save_and_store_results(
                screen_df, table_df, screen_dedup_df, table_dedup_df,
                config, progress, status, detail,
            )

    except FileNotFoundError as e:
        st.error(f"❌ ファイルが見つかりません: {e}")
    except ValueError as e:
        st.error(f"❌ データ形式エラー: {e}")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")
        st.exception(e)


def _load_all_data(tmpdir, config, progress, status, detail):
    """3種類のExcelファイルを読み込む。"""
    status.text("📂 ステップ 2/5: データを読み込み中...")

    detail.text("画面項目定義を解析中...")
    screen_items = load_screen_items(tmpdir, config)
    detail.text(f"✓ 画面項目定義: {len(screen_items)}件")
    progress.progress(25)

    detail.text("テーブル定義を解析中...")
    table_items = load_table_definitions(tmpdir, config)
    detail.text(f"✓ テーブル定義: {len(table_items)}件")
    progress.progress(35)

    detail.text("ドメイン定義を解析中...")
    domains = load_domains(tmpdir, config)
    detail.text(f"✓ ドメイン定義: {len(domains)}件")
    progress.progress(45)

    return screen_items, table_items, domains


def _run_matching(screen_items, table_items, domains, config, progress, status, detail):
    """画面項目×ドメイン、テーブル定義×ドメインの照合を実行する（全件対象）。"""
    status.text("🔄 ステップ 3/5: 照合処理中...")
    detail.text(
        f"画面項目 {len(screen_items)}件 + テーブル定義 {len(table_items)}件 "
        f"× ドメイン {len(domains)}件"
    )

    def on_screen_progress(processed, total):
        pct = 30 + int(25 * processed / total) if total > 0 else 30
        progress.progress(pct)
        detail.text(f"画面項目照合中: {processed}/{total}件")

    screen_df = process_screen_domain_matching(
        screen_items, domains, config, progress_callback=on_screen_progress,
    )
    progress.progress(55)

    def on_table_progress(processed, total):
        pct = 55 + int(20 * processed / total) if total > 0 else 55
        progress.progress(pct)
        detail.text(f"テーブル定義照合中: {processed}/{total}件")

    table_df = process_table_domain_matching(
        table_items, domains, config, progress_callback=on_table_progress,
    )
    progress.progress(75)

    return screen_df, table_df


def _dedup_results(screen_df, table_df, progress, status, detail):
    """照合済みDataFrameを項目名（数字除去後）＋桁数で重複排除する。"""
    status.text("🔧 ステップ 4/5: 重複排除中...")

    before_screen = len(screen_df)
    screen_dedup = dedup_by_name_and_digits(screen_df, "項目名称", "最大桁")
    detail.text(f"✓ 画面項目: {before_screen}件 → {len(screen_dedup)}件")

    before_table = len(table_df)
    table_dedup = dedup_by_name_and_digits(table_df, "論理項目名", "Length")
    detail.text(f"✓ テーブル定義: {before_table}件 → {len(table_dedup)}件")
    progress.progress(80)

    return screen_dedup, table_dedup


def _save_and_store_results(
    screen_df, table_df, screen_dedup_df, table_dedup_df,
    config, progress, status, detail,
):
    """結果をExcel（4シート）に保存し、session_state に格納する。"""
    status.text("💾 ステップ 5/5: 結果を保存中...")
    detail.text("Excelファイルを作成しています...")

    save_domain_check_results(
        screen_df, table_df, screen_dedup_df, table_dedup_df, config,
    )

    # tempdir 消失に備え、Excelバイトを session_state に退避
    out_dir = Path(config["OUT_DIR"])
    for result_file in out_dir.glob("*.xlsx"):
        st.session_state.result_excel_bytes = result_file.read_bytes()
        st.session_state.result_filename = result_file.name
        break

    st.session_state.processing_done = True
    st.session_state.screen_result_df = screen_dedup_df
    st.session_state.table_result_df = table_dedup_df

    total = len(screen_dedup_df) + len(table_dedup_df)
    progress.progress(100)
    status.text("✅ 処理完了！")
    detail.text(f"全 {total} 件の照合が完了しました（重複排除後）")


# ---------------------------------------------------------------------------
# 結果表示（session_state ベース — rerun 後も消えない）
# ---------------------------------------------------------------------------

def _show_results():
    """session_state に保存された結果を表示する。"""
    if not st.session_state.processing_done:
        return

    st.success("✅ チェック処理が完了しました！")

    screen_df = st.session_state.screen_result_df
    table_df = st.session_state.table_result_df

    # サマリ
    _show_summary("画面項目", screen_df)
    _show_summary("テーブル定義", table_df)

    # プレビュー（タブ切替）
    tab_screen, tab_table = st.tabs(["📋 画面項目の結果", "📋 テーブル定義の結果"])
    with tab_screen:
        _show_preview(screen_df, "画面項目")
    with tab_table:
        _show_preview(table_df, "テーブル定義")

    # ダウンロード
    _show_download()


def _show_summary(label, df):
    """照合結果のサマリをメトリクスカードで表示する。"""
    if df is None or len(df) == 0:
        return

    st.subheader(f"📊 {label}サマリ")
    total = len(df)
    col1, col2, col3, col4, col5 = st.columns(5)

    confirmed = len(df[df["判定結果"] == "確定"])
    candidate = len(df[df["判定結果"] == "候補"])
    select_needed = len(df[df["判定結果"] == "選択必要"])
    excluded = len(df[df["判定結果"] == "対象外"])
    no_match = len(df[df["判定結果"] == "一致なし"])

    pct = lambda n: f"{n * 100 / total:.1f}%" if total > 0 else "0%"
    col1.metric("総項目数", f"{total}件")
    col2.metric("確定", f"{confirmed}件", pct(confirmed))
    col3.metric("候補", f"{candidate}件", pct(candidate))
    col4.metric("選択必要", f"{select_needed}件", pct(select_needed))
    col5.metric("一致なし", f"{no_match}件", pct(no_match))


def _show_preview(df, label):
    """結果テーブルのプレビュー（先頭20件）を表示する。"""
    if df is None or len(df) == 0:
        st.info(f"{label}の結果はありません")
        return

    st.caption(f"{label}の結果プレビュー（先頭20件）")
    # 存在する列のみ選択（画面/テーブルで列名が異なる）
    priority_cols = [
        "項目名称", "論理項目名",
        "判定結果", "一致ドメイン名", "備考",
        "型", "データ型", "テキストタイプ",
    ]
    cols = [c for c in priority_cols if c in df.columns]
    preview = df[cols].head(20) if cols else df.head(20)
    st.dataframe(preview, use_container_width=True)


def _show_download():
    """結果Excelのダウンロードボタンを表示する。"""
    excel_bytes = st.session_state.result_excel_bytes
    if excel_bytes is None:
        return

    st.markdown("---")
    st.download_button(
        label="📥 結果をダウンロード (Excel)",
        data=excel_bytes,
        file_name=st.session_state.result_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )


# ===========================================================================
# ページ構成
# ===========================================================================

st.set_page_config(
    page_title="ドメイン照合ツール",
    page_icon="🔍",
    layout="wide",
)

if "visited_domain_check" not in st.session_state:
    track_usage(action="ページ訪問", tool_name="ドメイン照合")
    st.session_state.visited_domain_check = True

_init_session_state()

# ── ヘッダー ──
st.title("🔍 ドメイン照合ツール")
st.markdown("""
<div style='background: linear-gradient(90deg, #f56565 0%, #ed8936 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 画面項目・テーブル定義のドメイン存在チェックと提案</h3>
    <p style='color: #fff5f5; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        画面項目定義・テーブル定義に対応するドメインの存在をチェックし、
        存在しない場合は新規ドメインを提案します
    </p>
</div>
""", unsafe_allow_html=True)

# ── 使い方ガイド ──
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ 画面項目定義・テーブル定義とドメイン一覧の自動照合
    - ✅ 型＋桁数の大前提チェック → 項目名の類似度判定
    - ✅ 特殊パターン自動検出（フラグ・コメント・日付）
    - ✅ 4シート構成のExcel出力（抽出＋重複排除）

    ---

    ## 🚀 使用手順

    ### ステップ1️⃣: 3ファイルをアップロード

    - **画面項目定義**: 項目名称、型、テキストタイプ、桁数、外部コード等
    - **テーブル定義**: 論理項目名、データ型、Length、全体数値、少数桁
    - **ドメイン一覧**: ドメイン名、データ型、文字数、バイト長、桁数、書式等

    ### ステップ2️⃣: チェック実行

    「🚀 チェック実行」ボタンをクリック

    ### ステップ3️⃣: 結果を確認

    - **確定**: 型＋桁数＋名前が一致するドメインあり
    - **候補**: 類似するドメインの候補を提案
    - **選択必要**: フラグ・コメント等の特殊パターン（人間が選択）
    - **対象外**: 属性列が全て空のためドメイン不要
    - **一致なし**: 該当ドメインなし → 新規ドメイン定義が必要
    """)

st.markdown("---")

# ── サイドバー ──
with st.sidebar:
    st.header("⚙️ 設定")
    with st.expander("🔧 類似度設定", expanded=False):
        fuzzy_threshold = st.slider(
            "類似一致の閾値",
            min_value=0.0,
            max_value=1.0,
            value=DOMAIN_CONFIG["FUZZY_THRESHOLD"],
            step=0.05,
            help="類似度判定の最低スコア（高いほど厳密）",
        )

# ── ファイルアップロード ──
screen_files, table_files, domain_files = _render_file_uploaders()

st.markdown("---")

# ── 実行ボタン ──
all_files_ready = bool(screen_files and table_files and domain_files)
if st.button(
    "🚀 チェック実行",
    type="primary",
    use_container_width=True,
    disabled=not all_files_ready,
):
    _run_domain_check(screen_files, table_files, domain_files, fuzzy_threshold)

# ── 結果表示（session_state ベース — rerun 後も維持される） ──
_show_results()

# ── フッター ──
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        ドメイン照合ツール v2.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
