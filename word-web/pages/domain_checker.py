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
import io
import contextlib
import sys
import time

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
    """ファイルアップローダーを配置し、選択種別とファイルリストを返す。"""
    st.subheader("📄 入力ファイル")

    match_target = st.radio(
        "マッチング対象を選択",
        options=["画面項目定義", "テーブル定義"],
        horizontal=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.caption(f"{match_target}ファイル（必須）")
        target_key = "screen" if match_target == "画面項目定義" else "table"
        target_help = (
            "項目名称、型、テキストタイプ、桁数、外部コード"
            if match_target == "画面項目定義"
            else "論理項目名、データ型、Length、全体数値、少数桁"
        )
        target_files = st.file_uploader(
            f"{match_target} (*.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True,
            key=target_key,
            help=target_help,
        )
        if target_files:
            st.success(f"✅ {len(target_files)}件")
            for f in target_files:
                st.text(f"  • {f.name}")

    with col2:
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

    screen_files = target_files if match_target == "画面項目定義" else []
    table_files = target_files if match_target == "テーブル定義" else []

    return match_target, screen_files, table_files, domain_files


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def _save_files_to_tmpdir(files, tmpdir, label, detail_text):
    """アップロードファイルを一時ディレクトリに保存する。"""
    for i, f in enumerate(files):
        (tmpdir / f.name).write_bytes(f.read())
        detail_text.text(f"{label}保存中: {i + 1}/{len(files)} - {f.name}")


def _run_domain_check(match_target, screen_files, table_files, domain_files, fuzzy_threshold):
    """ドメインチェック全工程を実行し、結果を session_state に保存する。"""
    track_usage(action="実行ボタン押下", tool_name="マッチング")
    _clear_results()

    progress = st.progress(0)
    status = st.empty()
    detail = st.empty()

    class _Tee(io.TextIOBase):
        def __init__(self, *streams):
            self._streams = streams
        def write(self, s):
            for st in self._streams:
                st.write(s)
                st.flush()
            return len(s)
        def flush(self):
            for st in self._streams:
                st.flush()

    log_buf = io.StringIO()
    log_placeholder = st.empty()
    log_lines: list[str] = []
    last_log_time = {"ts": 0.0}

    def _log(msg: str) -> None:
        log_lines.append(msg)
        # keep last 200 lines for UI
        view = "\n".join(log_lines[-200:])
        log_placeholder.code(view)
        print(msg)
    tee_out = _Tee(sys.stdout, log_buf)
    tee_err = _Tee(sys.stderr, log_buf)
    try:
        with contextlib.redirect_stdout(tee_out), contextlib.redirect_stderr(tee_err):
            with tempfile.TemporaryDirectory() as tmpdir_str:
                tmpdir = Path(tmpdir_str)
                config = DOMAIN_CONFIG.copy()
                config["FUZZY_THRESHOLD"] = float(fuzzy_threshold)
                config["OUT_DIR"] = str(tmpdir / "out")

                _log("[WEB] Step1: save files start")
                # Step 1: ファイル保存
                status.text("📁 ステップ 1/5: ファイルを保存中...")
                file_summary = (
                    f"{match_target}: {len(screen_files) + len(table_files)}件、"
                    f"ドメイン定義: {len(domain_files)}件"
                )
                detail.text(file_summary)
                progress.progress(5)

                if screen_files:
                    _save_files_to_tmpdir(screen_files, tmpdir, "画面項目定義", detail)
                if table_files:
                    _save_files_to_tmpdir(table_files, tmpdir, "テーブル定義", detail)
                _save_files_to_tmpdir(domain_files, tmpdir, "ドメイン定義", detail)
                progress.progress(15)
                _log("[WEB] Step1: save files done")

                # Step 2: データ読み込み
                _log("[WEB] Step2: load data start")
                screen_items, table_items, domains, domain_raw_df = _load_all_data(
                    tmpdir, config, progress, status, detail, match_target,
                )
                _log(f"[WEB] Step2: load data done (screen={len(screen_items)}, table={len(table_items)}, domains={len(domains)})")

                # Step 3: 照合処理（全件対象 → 抽出シート用の生データ兼用）
                _log("[WEB] Step3: matching start")
                screen_df, table_df = _run_matching(
                    screen_items, table_items, domains, config, progress, status, detail, match_target, log_cb=_log,
                )
                _log("[WEB] Step3: matching done")

                # Step 4: 重複排除（照合済みDFに対して数字除去+桁数で集約）
                _log("[WEB] Step4: dedup start")
                screen_dedup_df, table_dedup_df = _dedup_results(
                    screen_df, table_df, progress, status, detail, match_target,
                )
                _log("[WEB] Step4: dedup done")

                # Step 5: 結果保存（4シート: 抽出×2 + 重複排除×2）
                _log("[WEB] Step5: save results start")
                _save_and_store_results(
                    screen_df, table_df, screen_dedup_df, table_dedup_df,
                    config, progress, status, detail, match_target, domain_raw_df,
                )
                _log("[WEB] Step5: save results done")

    except FileNotFoundError as e:
        st.error(f"❌ ファイルが見つかりません: {e}")
    except ValueError as e:
        st.error(f"❌ データ形式エラー: {e}")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")
        st.exception(e)
    finally:
        log_text = log_buf.getvalue().strip()
        if log_text:
            with st.expander("実行ログ", expanded=False):
                st.text(log_text)


def _load_all_data(tmpdir, config, progress, status, detail, match_target):
    """3種類のExcelファイルを読み込む。"""
    status.text("📂 ステップ 2/5: データを読み込み中...")

    screen_items = []
    table_items = []
    if match_target == "画面項目定義":
        detail.text("画面項目定義を解析中...")
        screen_items = load_screen_items(tmpdir, config)
        detail.text(f"✓ 画面項目定義: {len(screen_items)}件")
        progress.progress(30)
    else:
        detail.text("テーブル定義を解析中...")
        table_items = load_table_definitions(tmpdir, config)
        detail.text(f"✓ テーブル定義: {len(table_items)}件")
        progress.progress(30)

    detail.text("ドメイン定義を解析中...")
    domains, domain_raw_df = load_domains(tmpdir, config, return_raw=True)
    detail.text(f"✓ ドメイン定義: {len(domains)}件")
    progress.progress(45)

    return screen_items, table_items, domains, domain_raw_df


def _run_matching(screen_items, table_items, domains, config, progress, status, detail, match_target, log_cb=None):
    """画面項目×ドメイン、テーブル定義×ドメインの照合を実行する。"""
    status.text("🔄 ステップ 3/5: 照合処理中...")
    if match_target == "画面項目定義":
        detail.text(f"画面項目 {len(screen_items)}件")
    else:
        detail.text(f"テーブル定義 {len(table_items)}件")

    screen_df = pd.DataFrame()
    table_df = pd.DataFrame()

    if match_target == "画面項目定義":
        def on_screen_progress(processed, total):
            pct = 30 + int(35 * processed / total) if total > 0 else 30
            progress.progress(pct)
            status.text(f"🔄 ステップ 3/5: 照合処理中... {pct}%")
            detail.text(f"画面項目照合中: {processed}/{total}件（最新）")
            now = time.time()
            if now - on_screen_progress.last_log_ts >= 10:
                on_screen_progress.last_log_ts = now
                print(f"[WEB] progress screen {processed}/{total} ({pct}%)")
            if log_cb and (processed % 10 == 0 or processed == total):
                pct_text = f"{(processed * 100 / total):.1f}%" if total else "0.0%"
                log_cb(f"[INFO] {processed}/{total} 件処理済み ({pct_text})")
        on_screen_progress.last_log_ts = 0.0

        screen_df = process_screen_domain_matching(
            screen_items, domains, config, progress_callback=on_screen_progress,
        )
        progress.progress(70)
    else:
        def on_table_progress(processed, total):
            pct = 30 + int(35 * processed / total) if total > 0 else 30
            progress.progress(pct)
            status.text(f"🔄 ステップ 3/5: 照合処理中... {pct}%")
            detail.text(f"テーブル定義照合中: {processed}/{total}件（最新）")
            now = time.time()
            if now - on_table_progress.last_log_ts >= 10:
                on_table_progress.last_log_ts = now
                print(f"[WEB] progress table {processed}/{total} ({pct}%)")
            if log_cb and (processed % 10 == 0 or processed == total):
                pct_text = f"{(processed * 100 / total):.1f}%" if total else "0.0%"
                log_cb(f"[INFO] {processed}/{total} 件処理済み ({pct_text})")
        on_table_progress.last_log_ts = 0.0

        table_df = process_table_domain_matching(
            table_items, domains, config, progress_callback=on_table_progress,
        )
        progress.progress(70)

    return screen_df, table_df


def _dedup_results(screen_df, table_df, progress, status, detail, match_target):
    """照合済みDataFrameを項目名（数字除去後）＋桁数で重複排除する。"""
    status.text("🔧 ステップ 4/5: 重複排除中...")

    screen_dedup = pd.DataFrame()
    table_dedup = pd.DataFrame()
    if match_target == "画面項目定義":
        before_screen = len(screen_df)
        screen_dedup = dedup_by_name_and_digits(screen_df, "項目名称", "最大桁")
        detail.text(f"✓ 画面項目: {before_screen}件 → {len(screen_dedup)}件")
    else:
        before_table = len(table_df)
        table_dedup = dedup_by_name_and_digits(table_df, "論理項目名", "Length")
        detail.text(f"✓ テーブル定義: {before_table}件 → {len(table_dedup)}件")
    progress.progress(80)

    return screen_dedup, table_dedup


def _save_and_store_results(
    screen_df, table_df, screen_dedup_df, table_dedup_df,
    config, progress, status, detail, match_target, domain_raw_df,
):
    """結果をExcel（4シート）に保存し、session_state に格納する。"""
    status.text("💾 ステップ 5/5: 結果を保存中...")
    detail.text("Excelファイルを作成しています...")

    save_domain_check_results(
        screen_df,
        table_df,
        screen_dedup_df,
        table_dedup_df,
        config,
        include_screen=(match_target == "画面項目定義"),
        include_table=(match_target == "テーブル定義"),
        domains_df=domain_raw_df,
    )

    # tempdir 消失に備え、Excelバイトを session_state に退避
    out_dir = Path(config["OUT_DIR"])
    for result_file in out_dir.glob("*.xlsx"):
        st.session_state.result_excel_bytes = result_file.read_bytes()
        st.session_state.result_filename = result_file.name
        break

    st.session_state.processing_done = True
    st.session_state.screen_result_df = screen_dedup_df if match_target == "画面項目定義" else None
    st.session_state.table_result_df = table_dedup_df if match_target == "テーブル定義" else None

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

    confirmed = len(df[df["判定結果"] == "完全一致"])
    candidate = len(df[df["判定結果"].str.startswith("提案")])
    select_needed = len(df[df["判定結果"] == "選択必須"])
    excluded = len(df[df["判定結果"] == "対象外"])

    pct = lambda n: f"{n * 100 / total:.1f}%" if total > 0 else "0%"
    col1.metric("総項目数", f"{total}件")
    col2.metric("完全一致", f"{confirmed}件", pct(confirmed))
    col3.metric("提案", f"{candidate}件", pct(candidate))
    col4.metric("選択必須", f"{select_needed}件", pct(select_needed))
    col5.metric("対象外", f"{excluded}件", pct(excluded))


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
    page_title="マッチングツール",
    page_icon="🔍",
    layout="wide",
)

if "visited_domain_check" not in st.session_state:
    track_usage(action="ページ訪問", tool_name="マッチング")
    st.session_state.visited_domain_check = True

_init_session_state()

# ── ヘッダー ──
st.title("🔍 マッチングツール")
st.markdown("""
<div style='background: linear-gradient(90deg, #f56565 0%, #ed8936 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 画面項目・テーブル定義のマッチング</h3>
    <p style='color: #fff5f5; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        画面項目定義・テーブル定義とドメイン一覧を照合し、
        最適なドメイン候補を提案します
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

    - **完全一致**: 型＋桁数＋名前が一致するドメインあり
    - **提案**: 候補からの提案、もしくは新規ドメイン提案
    - **選択必須**: フラグ・コメント等の特殊パターン（人間が選択）
    - **対象外**: 属性列が全て空のためマッチング対象外
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
match_target, screen_files, table_files, domain_files = _render_file_uploaders()

st.markdown("---")

# ── 実行ボタン ──
if match_target == "画面項目定義":
    all_files_ready = bool(screen_files and domain_files)
else:
    all_files_ready = bool(table_files and domain_files)
if st.button(
    "🚀 チェック実行",
    type="primary",
    use_container_width=True,
    disabled=not all_files_ready,
):
    _run_domain_check(match_target, screen_files, table_files, domain_files, fuzzy_threshold)

# ── 結果表示（session_state ベース — rerun 後も維持される） ──
_show_results()

# ── フッター ──
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        マッチングツール v2.0 | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
