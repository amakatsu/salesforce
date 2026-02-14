#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメイン定義チェックツール

画面項目定義・テーブル定義とドメイン定義一覧を照合し、
一致状況を判定する。
"""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

try:
    from ..config import get_domain_config
except ImportError:
    from config import get_domain_config


# ====== 正規化 ================================================================

def normalize_text(text: str) -> str:
    """NFKC正規化 + 小文字化 + 同義語統一"""
    if text is None or text == "":
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = re.sub(r"[\u3000\s]+", " ", s)

    # 日付・時刻
    s = re.sub(r"取引日$", "日付", s)
    s = re.sub(r"年月日$", "日付", s)
    s = re.sub(r"(\w+)日$", r"\1日付", s)
    s = re.sub(r"日時$", "日時", s)
    s = re.sub(r"時刻$", "時刻", s)
    s = re.sub(r"タイムスタンプ$", "日時", s)

    # 金額・数量
    s = re.sub(r"金額$", "金額", s)
    s = re.sub(r"価格$", "金額", s)
    s = re.sub(r"料金$", "金額", s)
    s = re.sub(r"単価$", "単価", s)
    s = re.sub(r"数量$", "数量", s)
    s = re.sub(r"件数$", "数量", s)
    s = re.sub(r"個数$", "数量", s)

    # コード・ID
    s = re.sub(r"コード$", "コード", s)
    s = re.sub(r"cd$", "コード", s)
    s = re.sub(r"識別子$", "id", s)
    s = re.sub(r"番号$", "番号", s)
    s = re.sub(r"no$", "番号", s)

    # 名称
    s = re.sub(r"名称$", "名称", s)
    s = re.sub(r"名前$", "名称", s)
    s = re.sub(r"氏名$", "名称", s)
    s = re.sub(r"name$", "名称", s)

    # 区分・種別
    s = re.sub(r"区分$", "区分", s)
    s = re.sub(r"種別$", "区分", s)
    s = re.sub(r"タイプ$", "区分", s)
    s = re.sub(r"type$", "区分", s)

    # フラグ・状態
    s = re.sub(r"フラグ$", "フラグ", s)
    s = re.sub(r"flag$", "フラグ", s)
    s = re.sub(r"状態$", "状態", s)
    s = re.sub(r"ステータス$", "状態", s)
    s = re.sub(r"status$", "状態", s)

    # 備考・メモ
    s = re.sub(r"備考$", "備考", s)
    s = re.sub(r"メモ$", "備考", s)
    s = re.sub(r"コメント$", "備考", s)
    s = re.sub(r"摘要$", "備考", s)

    return s


def normalize_data_type(dtype: str) -> str:
    """データ型の正規化"""
    if not dtype:
        return ""
    dt = normalize_text(dtype)
    type_map = {
        "varchar": "varchar", "varchar2": "varchar", "char": "char",
        "int": "integer", "integer": "integer", "bigint": "bigint",
        "decimal": "decimal", "numeric": "decimal", "number": "decimal",
        "date": "date", "datetime": "datetime", "timestamp": "timestamp",
        "boolean": "boolean", "bool": "boolean",
    }
    for key, value in type_map.items():
        if key in dt:
            return value
    return dt


# ====== データクラス ==========================================================

@dataclass
class ScreenItem:
    """画面項目定義（確定仕様: 10列）"""
    item_name: str             # 項目名
    data_type: str             # データ型
    text_type: str             # テキストタイプ
    min_digits: Optional[str]  # 最小桁
    max_digits: Optional[str]  # 最大桁
    max_bytes: Optional[str]   # 最大バイト数
    min_value: Optional[str]   # 最小値
    max_value: Optional[str]   # 最大値
    code_id: str               # 外部コード
    row_number: int
    source_file: str
    source_sheet: str


@dataclass
class TableItem:
    """テーブル定義（確定仕様: 6列）"""
    item_name: str             # 項目名
    data_type: str             # データ型
    length: Optional[str]      # length
    integer_part: Optional[str]  # 数値の整数
    decimal_part: Optional[str]  # 小数点
    row_number: int
    source_file: str
    source_sheet: str


@dataclass
class DomainDef:
    """ドメイン定義（殿の確定仕様: 12列）"""
    name: str                      # ドメイン名
    data_type: str                 # データ型
    min_char: Optional[str]        # 最小文字数
    max_char: Optional[str]        # 最大文字数
    min_byte: Optional[str]        # 最小バイト長
    max_byte: Optional[str]        # 最大バイト長
    integer_digits: Optional[str]  # 整数部桁数
    decimal_digits: Optional[str]  # 小数部桁数
    min_value: Optional[str]       # 最小値
    max_value: Optional[str]       # 最大値
    regex: Optional[str]           # 書式（正規表現）
    code_id: str                   # 参照外部コード
    row_number: int
    source_file: str
    source_sheet: str


# ====== Excel I/O =============================================================

HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", "10"))


def _pick_matching_sheets(xls: pd.ExcelFile, preferred: Optional[str]) -> List[str]:
    if not preferred:
        return [xls.sheet_names[0]]
    norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]
    all_matches = []
    for pattern in patterns:
        want = norm(pattern)
        regex_pattern = want.replace("*", ".*")
        for name in xls.sheet_names:
            if re.match(regex_pattern, norm(name)):
                all_matches.append(name)
    seen: set[str] = set()
    result = []
    for sheet in all_matches:
        if sheet not in seen:
            result.append(sheet)
            seen.add(sheet)
    return result if result else [xls.sheet_names[0]]


def _detect_header_row(
    path: Path, sheet_name: str, required_cols: List[str], scan_rows: int,
) -> int:
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    req = {normalize_text(c) for c in required_cols if c}
    for i in range(len(head_df)):
        row_vals = {
            normalize_text(x) for x in head_df.iloc[i].values if str(x) not in {"", "nan"}
        }
        if req.issubset(row_vals):
            return i
    raise KeyError(
        f"必須列{sorted(required_cols)}を含むヘッダ行が見つかりません: {path.name}/{sheet_name}"
    )


def read_excel_with_header_detection(
    path: Path,
    sheet_name: Optional[str],
    required_cols: List[str],
    explicit_header_row_1based: Optional[int] = None,
    scan_rows: int = 30,
) -> Tuple[pd.DataFrame, int]:
    """ヘッダ行が1行目とは限らないExcelに対応。"""
    if explicit_header_row_1based is not None:
        hdr0 = max(0, explicit_header_row_1based - 1)
        return pd.read_excel(path, sheet_name=sheet_name, header=hdr0), hdr0
    if not HEADER_DETECT:
        return pd.read_excel(path, sheet_name=sheet_name), 0
    header_row = _detect_header_row(path, sheet_name, required_cols, scan_rows)
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row), header_row


# ====== セル値取得ユーティリティ ==============================================

_EMPTY_VALUES = {"", "nan", "None", " ", "\u3000"}


def _get_cell_value(
    row: pd.Series, df: pd.DataFrame, col_name: str, col_idx: int = -1,
) -> str:
    """列名で値を取得し、見つからなければ列位置でフォールバック。

    空値・NaN・"nan"等は空文字列として返す。
    """
    val = None
    if col_name in df.columns:
        val = row.get(col_name, "")
    elif 0 <= col_idx < len(row):
        try:
            val = row.iloc[col_idx]
        except Exception:
            val = ""

    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    val_str = str(val).strip()
    if val_str in _EMPTY_VALUES or val_str.isspace():
        return ""
    return val_str


def _find_columns(df: pd.DataFrame, column_names: Dict[str, str]) -> Dict[str, int]:
    """ヘッダー行から列名→列インデックスの対応を動的に取得する（部分一致）。

    列名が「項目名称（和名）」のように装飾されていても、
    検索キー「項目名称」でヒットする。完全一致を優先し、
    なければ部分一致にフォールバックする。

    Args:
        df: ヘッダー検出済みのDataFrame（df.columnsがヘッダー行）
        column_names: {内部キー: Excel列名} の辞書

    Returns:
        {内部キー: 列インデックス} の辞書（見つかった列のみ）
    """
    headers = [str(h).strip() for h in df.columns]
    col_map: Dict[str, int] = {}
    for key, col_name in column_names.items():
        target = col_name.strip()
        # 完全一致を優先
        exact = [i for i, h in enumerate(headers) if h == target]
        if exact:
            col_map[key] = exact[0]
            continue
        # 部分一致にフォールバック
        partial = [i for i, h in enumerate(headers) if target in h]
        if partial:
            col_map[key] = partial[0]
    return col_map


def _is_domain_unnecessary(row: pd.Series, col_map: Dict[str, int]) -> bool:
    """項目名称だけあって他が全て空 → ドメイン不要項目として除外対象。

    テキストタイプ〜外部コードの7列が全て空の場合にTrueを返す。
    """
    check_keys = [
        "text_type", "min_digits", "max_digits",
        "max_bytes", "min_value", "max_value", "external_code",
    ]
    for key in check_keys:
        if key not in col_map:
            continue
        val = row.iloc[col_map[key]]
        if not (pd.isna(val) or str(val).strip() in _EMPTY_VALUES):
            return False
    return True


# ====== データ読み込み ========================================================

def load_screen_items(dir_path: Path, cfg: Dict[str, Any]) -> List[ScreenItem]:
    """画面項目定義を読み込み（ヘッダー文字列検索方式・行番号付き）。

    殿の確定仕様:
    - 列はヘッダー行から文字列で動的検索（列番号固定禁止）
    - 正式列名: 項目名称, 型, テキストタイプ, 最小桁, 最大桁,
                最大バイト数, 最小値, 最大値, 外部コード
    - 項目名称だけあって他7列が全空の行は「ドメイン不要」（対象外）
      → 読み込みは行うが、process関数でマッチングスキップ＋「対象外」出力
    """
    # 列名マッピング: 内部キー → Excelヘッダーの正式列名
    screen_col_names: Dict[str, str] = {
        "item_name":     cfg.get("SCREEN_ITEM_COL", "項目名称"),
        "data_type":     cfg.get("SCREEN_TYPE_COL", "型"),
        "text_type":     cfg.get("SCREEN_TEXT_TYPE_COL", "テキストタイプ"),
        "min_digits":    cfg.get("SCREEN_MIN_DIGITS_COL", "最小桁"),
        "max_digits":    cfg.get("SCREEN_MAX_DIGITS_COL", "最大桁"),
        "max_bytes":     cfg.get("SCREEN_MAX_BYTES_COL", "最大バイト数"),
        "min_value":     cfg.get("SCREEN_MIN_VALUE_COL", "最小値"),
        "max_value":     cfg.get("SCREEN_MAX_VALUE_COL", "最大値"),
        "external_code": cfg.get("SCREEN_EXT_CODE_COL", "外部コード"),
    }

    files = sorted(dir_path.glob(cfg["SCREEN_GLOB"]))
    if not files:
        raise FileNotFoundError("画面項目定義ファイルが見つかりません")
    items: List[ScreenItem] = []
    for path in files:
        xls = pd.ExcelFile(path)
        for sheet in _pick_matching_sheets(xls, cfg["SCREEN_SHEET"]):
            try:
                df, header_row = read_excel_with_header_detection(
                    path, sheet, [screen_col_names["item_name"]], None, 30,
                )
                col_map = _find_columns(df, screen_col_names)
                if "item_name" not in col_map:
                    print(f"[警告] {path.name}({sheet}): 「{screen_col_names['item_name']}」列が見つかりません")
                    continue

                def _val(key: str) -> str:
                    if key not in col_map:
                        return ""
                    v = row.iloc[col_map[key]]
                    if pd.isna(v):
                        return ""
                    s = str(v).strip()
                    return "" if s in _EMPTY_VALUES else s

                for idx, row in df.iterrows():
                    if row.isna().all():
                        continue
                    item_name = _val("item_name")
                    if not item_name:
                        continue

                    items.append(ScreenItem(
                        item_name=item_name,
                        data_type=_val("data_type"),
                        text_type=_val("text_type"),
                        min_digits=_val("min_digits") or None,
                        max_digits=_val("max_digits") or None,
                        max_bytes=_val("max_bytes") or None,
                        min_value=_val("min_value") or None,
                        max_value=_val("max_value") or None,
                        code_id=_val("external_code"),
                        row_number=header_row + idx + 2,
                        source_file=path.name,
                        source_sheet=sheet,
                    ))
                print(f"[INFO] 画面項目定義読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計画面項目: {len(items)}件")
    return items


def load_domains(dir_path: Path, cfg: Dict[str, Any]) -> Dict[str, DomainDef]:
    """ドメイン定義を読み込み（ヘッダー文字列検索方式・正規化名でキー・行番号付き）。

    殿の確定仕様（12列）:
    - ドメイン名, データ型, 最小文字数, 最大文字数, 最小バイト長, 最大バイト長,
      整数部桁数, 小数部桁数, 最小値, 最大値, 書式（正規表現）, 参照外部コード
    """
    # 列名マッピング: 内部キー → Excelヘッダーの正式列名
    domain_col_names: Dict[str, str] = {
        "name":           cfg.get("DOMAIN_NAME_COL", "ドメイン名"),
        "data_type":      cfg.get("DOMAIN_TYPE_COL", "データ型"),
        "min_char":       cfg.get("DOMAIN_STR_MIN_CHARS_COL", "最小文字数"),
        "max_char":       cfg.get("DOMAIN_STR_MAX_CHARS_COL", "最大文字数"),
        "min_byte":       cfg.get("DOMAIN_BYTES_MIN_COL", "最小バイト長"),
        "max_byte":       cfg.get("DOMAIN_BYTES_MAX_COL", "最大バイト長"),
        "integer_digits": cfg.get("DOMAIN_INT_DIGITS_COL", "整数部桁数"),
        "decimal_digits": cfg.get("DOMAIN_DEC_DIGITS_COL", "小数部桁数"),
        "min_value":      cfg.get("DOMAIN_NUM_MIN_COL", "最小値"),
        "max_value":      cfg.get("DOMAIN_NUM_MAX_COL", "最大値"),
        "regex":          cfg.get("DOMAIN_REGEX_COL", "書式（正規表現）"),
        "code_id":        cfg.get("DOMAIN_EXT_CODE_COL", "参照外部コード"),
    }

    files = sorted(dir_path.glob(cfg["DOMAIN_GLOB"]))
    if not files:
        raise FileNotFoundError("ドメイン定義ファイルが見つかりません")
    domains: Dict[str, DomainDef] = {}
    for path in files:
        xls = pd.ExcelFile(path)
        for sheet in _pick_matching_sheets(xls, cfg["DOMAIN_SHEET"]):
            try:
                df, header_row = read_excel_with_header_detection(
                    path, sheet, [domain_col_names["name"]], None, 30,
                )
                col_map = _find_columns(df, domain_col_names)
                if "name" not in col_map:
                    print(f"[警告] {path.name}({sheet}): 「{domain_col_names['name']}」列が見つかりません")
                    continue

                def _val(key: str) -> str:
                    if key not in col_map:
                        return ""
                    v = row.iloc[col_map[key]]
                    if pd.isna(v):
                        return ""
                    s = str(v).strip()
                    return "" if s in _EMPTY_VALUES else s

                for idx, row in df.iterrows():
                    if row.isna().all():
                        continue
                    name = _val("name")
                    if not name:
                        continue

                    domains[normalize_text(name)] = DomainDef(
                        name=name,
                        data_type=_val("data_type"),
                        min_char=_val("min_char") or None,
                        max_char=_val("max_char") or None,
                        min_byte=_val("min_byte") or None,
                        max_byte=_val("max_byte") or None,
                        integer_digits=_val("integer_digits") or None,
                        decimal_digits=_val("decimal_digits") or None,
                        min_value=_val("min_value") or None,
                        max_value=_val("max_value") or None,
                        regex=_val("regex") or None,
                        code_id=_val("code_id"),
                        row_number=header_row + idx + 2,
                        source_file=path.name,
                        source_sheet=sheet,
                    )
                print(f"[INFO] ドメイン定義読み込み: {path.name}/{sheet} ({len(domains)}件)")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計ドメイン定義: {len(domains)}件")
    return domains


def load_table_definitions(dir_path: Path, cfg: Dict[str, Any]) -> List[TableItem]:
    """テーブル定義を読み込み（ヘッダー文字列検索方式・行番号付き）。

    殿の確定仕様:
    - 列はヘッダー行から文字列で動的検索（列番号固定禁止）
    - 正式列名: 論理項目名, データ型, Length, 全体数値, 少数桁
    - 論理項目名だけあって他4列が全空の行は「対象外」
      → 読み込みは行うが、process関数でマッチングスキップ＋「対象外」出力
    """
    # 列名マッピング: 内部キー → Excelヘッダーの正式列名
    table_col_names: Dict[str, str] = {
        "item_name":     cfg.get("TABLE_ITEM_COL", "論理項目名"),
        "data_type":     cfg.get("TABLE_TYPE_COL", "データ型"),
        "length":        cfg.get("TABLE_LENGTH_COL", "Length"),
        "integer_part":  cfg.get("TABLE_INT_COL", "全体数値"),
        "decimal_part":  cfg.get("TABLE_DEC_COL", "少数桁"),
    }

    files = sorted(dir_path.glob(cfg["TABLE_GLOB"]))
    if not files:
        raise FileNotFoundError("テーブル定義ファイルが見つかりません")
    items: List[TableItem] = []
    for path in files:
        xls = pd.ExcelFile(path)
        for sheet in _pick_matching_sheets(xls, cfg["TABLE_SHEET"]):
            try:
                df, header_row = read_excel_with_header_detection(
                    path, sheet, [table_col_names["item_name"]], None, 30,
                )
                col_map = _find_columns(df, table_col_names)
                if "item_name" not in col_map:
                    print(f"[警告] {path.name}({sheet}): 「{table_col_names['item_name']}」列が見つかりません")
                    continue

                def _val(key: str) -> str:
                    if key not in col_map:
                        return ""
                    v = row.iloc[col_map[key]]
                    if pd.isna(v):
                        return ""
                    s = str(v).strip()
                    return "" if s in _EMPTY_VALUES else s

                for idx, row in df.iterrows():
                    if row.isna().all():
                        continue
                    item_name = _val("item_name")
                    if not item_name:
                        continue

                    items.append(TableItem(
                        item_name=item_name,
                        data_type=_val("data_type"),
                        length=_val("length") or None,
                        integer_part=_val("integer_part") or None,
                        decimal_part=_val("decimal_part") or None,
                        row_number=header_row + idx + 2,
                        source_file=path.name,
                        source_sheet=sheet,
                    ))
                print(f"[INFO] テーブル定義読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計テーブル定義: {len(items)}件")
    return items


# ====== 類似度計算 ============================================================

try:
    from rapidfuzz import fuzz
    _FUZZ_AVAILABLE = True
except ImportError:
    from difflib import SequenceMatcher
    _FUZZ_AVAILABLE = False


def calc_similarity(s1: str, s2: str) -> float:
    """2つの文字列の類似度を計算（0.0〜1.0）"""
    if _FUZZ_AVAILABLE:
        return fuzz.ratio(s1, s2) / 100.0
    return SequenceMatcher(None, s1, s2).ratio()


# ====== マッチング結果型 ======================================================

@dataclass
class MatchResult:
    """ドメインマッチング結果。

    domain_matcher.py (C方式) / llm_matcher.py (B方式) と共通の型。

    match_type の値:
        レガシー: "exact", "similar", "unmatched"
        C方式:    "exact", "special_flag", "special_date",
                  "special_date_individual", "special_comment",
                  "similar", "needs_llm", "unmatched"

    特殊パターン（special_flag, special_comment）は自動割当ではなく
    人間選択方式。reason に選択肢テキストが格納される。
      フラグ: 「以下から選択: 0/1, 0/9, null/1, スペース/1」
      コメント/補記: 「改行あり/なしを確認して選択してください」
    """
    match_type: str
    domain: Optional[DomainDef]
    confidence: float
    reason: str


# match_type → 表示用「判定結果」の変換マップ（確定仕様）
_MATCH_TYPE_DISPLAY = {
    "exact": "確定",
    "special_date": "確定",
    "special_date_individual": "確定",
    "special_flag": "選択必要",
    "special_comment": "選択必要",
    "similar": "候補",
    "needs_llm": "候補",
    "unmatched": "一致なし",
    "unnecessary": "対象外",
}


def _match_result_to_display(result: MatchResult) -> str:
    """MatchResult.match_type を表示用「判定結果」文字列に変換する。"""
    return _MATCH_TYPE_DISPLAY.get(result.match_type, result.match_type)


# マッチャー関数の型: (item_dict, domains, cfg) -> MatchResult
# item_dict は collect_evidence() に渡す辞書形式:
#   必須: item_name (str), data_type (str)
#   任意: max_chars, max_bytes, min_value, max_value, external_code,
#         integer_digits, decimal_digits, length, source ("screen"|"table")
MatcherFn = Callable[[Dict[str, Any], Dict[str, DomainDef], Dict[str, Any]], MatchResult]


# ====== レガシーマッチャー（現行ロジック） ====================================

def _legacy_matcher(
    item: Dict[str, Any], domains: Dict[str, DomainDef], cfg: Dict[str, Any],
) -> MatchResult:
    """現行のマッチングロジック（名前ベースの完全一致 + fuzzy一致）。

    Args:
        item: 項目情報の辞書。必須キー: item_name, data_type。

    TODO(cmd_062): domain_matcher.collect_evidence() → resolve_without_llm() に
    差し替え予定。新ロジックでは:
      1. 項目名から数字を除去して正規化
      2. 型・桁の一致を大前提としてフィルタ
      3. 名前比較（完全一致 → 同義語一致 → LLM判定）
    """
    item_name = item["item_name"]
    item_name_norm = normalize_text(item_name)
    threshold = cfg["FUZZY_THRESHOLD"]

    # 完全一致
    if item_name_norm in domains:
        d = domains[item_name_norm]
        return MatchResult("exact", d, 1.0, f"ドメイン「{d.name}」と完全一致")

    # 類似一致（fuzzy）
    best_score = 0.0
    best_domain: Optional[DomainDef] = None
    for key, d in domains.items():
        score = calc_similarity(item_name_norm, key)
        if score > best_score:
            best_score = score
            best_domain = d

    if best_score >= threshold and best_domain is not None:
        reason = f"ドメイン「{best_domain.name}」と類似（{best_score:.1%}）"
        return MatchResult("similar", best_domain, best_score, reason)

    return MatchResult("unmatched", None, 0.0, "一致するドメインなし")


def _domain_detail_dict(domain: Optional[DomainDef]) -> Dict[str, str]:
    """DomainDef からドメイン詳細列の辞書を生成する（殿の確定仕様: 12列）。"""
    if domain is None:
        return {
            "D_データ型": "",
            "D_最小文字数": "", "D_最大文字数": "",
            "D_最小バイト長": "", "D_最大バイト長": "",
            "D_最小値": "", "D_最大値": "",
            "D_整数部桁数": "", "D_小数部桁数": "",
            "D_書式（正規表現）": "", "D_参照外部コード": "",
        }

    def _s(val: Optional[str]) -> str:
        if val is None:
            return ""
        v = str(val).strip()
        return "" if v in _EMPTY_VALUES else v

    return {
        "D_データ型": _s(domain.data_type),
        "D_最小文字数": _s(domain.min_char),
        "D_最大文字数": _s(domain.max_char),
        "D_最小バイト長": _s(domain.min_byte),
        "D_最大バイト長": _s(domain.max_byte),
        "D_最小値": _s(domain.min_value),
        "D_最大値": _s(domain.max_value),
        "D_整数部桁数": _s(domain.integer_digits),
        "D_小数部桁数": _s(domain.decimal_digits),
        "D_書式（正規表現）": _s(domain.regex),
        "D_参照外部コード": _s(domain.code_id),
    }


def _make_lookup_key(name: str, digits: Optional[str]) -> str:
    """VLOOKUP用の検索キーを生成する。"""
    d = str(digits).strip() if digits else ""
    return f"{name}_{d}" if d else name


def suggest_domain_from_screen_item(item: ScreenItem) -> Dict[str, str]:
    """画面項目定義からドメイン提案を生成（確定仕様対応）"""
    suggestions: Dict[str, str] = {}

    if item.data_type:
        dt = str(item.data_type).lower().strip()
        if any(k in dt for k in ("text", "string", "varchar")):
            suggestions["データ型"] = "VARCHAR"
        elif any(k in dt for k in ("number", "integer", "int")):
            suggestions["データ型"] = "INTEGER"
        elif "date" in dt:
            suggestions["データ型"] = "DATE"
        elif any(k in dt for k in ("decimal", "float", "numeric")):
            suggestions["データ型"] = "DECIMAL"
        elif any(k in dt for k in ("boolean", "bool")):
            suggestions["データ型"] = "BOOLEAN"
        else:
            suggestions["データ型"] = item.data_type

    if item.max_digits is not None:
        mv = str(item.max_digits).strip()
        if mv and mv not in _EMPTY_VALUES:
            suggestions["最大文字数"] = mv

    if item.max_bytes is not None:
        bv = str(item.max_bytes).strip()
        if bv and bv not in _EMPTY_VALUES:
            suggestions["最大バイト数"] = bv

    return suggestions


# ====== 重複排除 ==============================================================

_RE_DIGITS = re.compile(r"\d+")


def _strip_digits(name: str) -> str:
    """項目名から数字を全て除去する。仕様書 Section 3-5 準拠。

    例: 「ああ1」→「ああ」、「金額01」→「金額」
    """
    return _RE_DIGITS.sub("", name).strip()


def dedup_by_name_and_digits(
    df: pd.DataFrame, name_col: str, digits_col: str,
) -> pd.DataFrame:
    """「項目名（数字除去後）＋桁数」が完全一致する行を1つに集約する。

    仕様書 Section 2「重複排除の基準」準拠。
    項目名列は数字除去後の値に置換される（重複排除シート用）。
    """
    df = df.copy()
    df[name_col] = df[name_col].apply(_strip_digits)
    digits = df[digits_col].fillna("").astype(str).str.strip() if digits_col in df.columns else pd.Series([""] * len(df))
    df["検索キー"] = df[name_col] + "_" + digits
    return df.drop_duplicates(subset=["検索キー"], keep="first").reset_index(drop=True)


# ====== 画面項目 突合処理 ====================================================

def process_screen_domain_matching(
    screen_items: List[ScreenItem],
    domains: Dict[str, DomainDef],
    cfg: Dict[str, Any],
    progress_callback: Optional[Callable[[int, int], None]] = None,
    matcher: Optional[MatcherFn] = None,
) -> pd.DataFrame:
    """画面項目とドメインの突合処理。

    Args:
        matcher: マッチング関数。省略時はレガシーロジック (_legacy_matcher)。
                 TODO(cmd_062): domain_matcher.collect_evidence() ベースの
                 関数を渡すことで新ロジックに切り替え可能。

    Returns:
        全項目の照合結果DataFrame（検索キー付き）
    """
    match_fn = matcher or _legacy_matcher
    results: List[Dict[str, Any]] = []
    total = len(screen_items)

    for i, item in enumerate(screen_items):
        # ドメイン不要判定: 項目名称だけあって他7列が全空
        is_unnecessary = all(
            v is None or str(v).strip() in _EMPTY_VALUES
            for v in (item.text_type, item.min_digits, item.max_digits,
                      item.max_bytes, item.min_value, item.max_value, item.code_id)
        )

        if is_unnecessary:
            mr = MatchResult("unnecessary", None, 0.0, "ドメイン不要項目")
        else:
            item_dict: Dict[str, Any] = {
                "item_name": item.item_name,
                "data_type": item.data_type,
                "max_chars": item.max_digits,
                "max_bytes": item.max_bytes,
                "min_value": item.min_value,
                "max_value": item.max_value,
                "external_code": item.code_id,
                "source": "screen",
            }
            mr = match_fn(item_dict, domains, cfg)
        display_type = _match_result_to_display(mr)
        remark = mr.reason

        # 一致なしの備考補足
        if display_type == "一致なし":
            has_digits = bool(item.max_digits and str(item.max_digits).strip() not in _EMPTY_VALUES)
            has_bytes = bool(item.max_bytes and str(item.max_bytes).strip() not in _EMPTY_VALUES)
            if has_digits or has_bytes:
                remark = "桁数/バイト数の定義あり → 新規ドメイン提案が必要"
            else:
                remark = "桁数/バイト数なし → ドメイン設定不要の可能性"

        row: Dict[str, Any] = {
            "ファイル名": item.source_file,
            "項目名称": item.item_name,
            "型": item.data_type if item.data_type else "",
            "テキストタイプ": item.text_type if item.text_type else "",
            "最小桁": item.min_digits if item.min_digits else "",
            "最大桁": item.max_digits if item.max_digits else "",
            "最大バイト数": item.max_bytes if item.max_bytes else "",
            "最小値": item.min_value if item.min_value else "",
            "最大値": item.max_value if item.max_value else "",
            "外部コード": item.code_id if item.code_id else "",
            "一致ドメイン名": mr.domain.name if mr.domain else "",
            "判定結果": display_type,
            "備考": remark,
        }
        row.update(_domain_detail_dict(mr.domain))

        # 一致なし＋桁数ありの場合、提案情報で上書き
        if display_type == "一致なし":
            suggestions = suggest_domain_from_screen_item(item)
            if "データ型" in suggestions:
                row["D_データ型"] = suggestions["データ型"]
            if "最大文字数" in suggestions:
                row["D_最大文字数"] = suggestions["最大文字数"]
            if "最大バイト数" in suggestions:
                row["D_最大バイト長"] = suggestions["最大バイト数"]

        results.append(row)

        processed = i + 1
        if processed % 10 == 0 or processed == total:
            print(f"[INFO] 画面項目照合: {processed}/{total} 件処理済み")
        if progress_callback:
            progress_callback(processed, total)

    return _clean_dataframe(results)


# ====== テーブル定義 突合処理 ================================================

def process_table_domain_matching(
    table_items: List[TableItem],
    domains: Dict[str, DomainDef],
    cfg: Dict[str, Any],
    progress_callback: Optional[Callable[[int, int], None]] = None,
    matcher: Optional[MatcherFn] = None,
) -> pd.DataFrame:
    """テーブル定義とドメインの突合処理。

    Args:
        matcher: マッチング関数。省略時はレガシーロジック (_legacy_matcher)。
                 TODO(cmd_062): domain_matcher.collect_evidence() ベースの
                 関数を渡すことで新ロジックに切り替え可能。

    Returns:
        全項目の照合結果DataFrame（検索キー付き）
    """
    match_fn = matcher or _legacy_matcher
    results: List[Dict[str, Any]] = []
    total = len(table_items)

    for i, item in enumerate(table_items):
        # ドメイン不要判定: 論理項目名だけあって他4列が全空
        is_unnecessary = all(
            v is None or str(v).strip() in _EMPTY_VALUES
            for v in (item.data_type, item.length, item.integer_part, item.decimal_part)
        )

        if is_unnecessary:
            mr = MatchResult("unnecessary", None, 0.0, "ドメイン不要項目")
        else:
            item_dict: Dict[str, Any] = {
                "item_name": item.item_name,
                "data_type": item.data_type,
                "length": item.length,
                "integer_digits": item.integer_part,
                "decimal_digits": item.decimal_part,
                "source": "table",
            }
            mr = match_fn(item_dict, domains, cfg)
        display_type = _match_result_to_display(mr)
        remark = mr.reason

        # 一致なしの備考補足
        if display_type == "一致なし":
            has_type = bool(item.data_type and item.data_type.strip())
            has_length = bool(item.length and str(item.length).strip() not in _EMPTY_VALUES)
            if has_type or has_length:
                remark = "データ型/桁数の定義あり → 新規ドメイン提案が必要"
            else:
                remark = "データ型/桁数なし → ドメイン設定不要の可能性"

        # 一致時のデータ型整合性チェック
        if mr.domain and item.data_type:
            item_type_norm = normalize_data_type(item.data_type)
            domain_type_norm = normalize_data_type(mr.domain.data_type)
            if item_type_norm and domain_type_norm and item_type_norm != domain_type_norm:
                remark += f" / 型不一致: テーブル={item.data_type}, ドメイン={mr.domain.data_type}"

        row: Dict[str, Any] = {
            "ファイル名": item.source_file,
            "論理項目名": item.item_name,
            "データ型": item.data_type if item.data_type else "",
            "Length": item.length if item.length else "",
            "全体数値": item.integer_part if item.integer_part else "",
            "少数桁": item.decimal_part if item.decimal_part else "",
            "一致ドメイン名": mr.domain.name if mr.domain else "",
            "判定結果": display_type,
            "備考": remark,
        }
        row.update(_domain_detail_dict(mr.domain))
        results.append(row)

        processed = i + 1
        if processed % 10 == 0 or processed == total:
            print(f"[INFO] テーブル定義照合: {processed}/{total} 件処理済み")
        if progress_callback:
            progress_callback(processed, total)

    return _clean_dataframe(results)


def _clean_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """結果辞書リストをDataFrameに変換し、NaN/nan文字列を除去する。"""
    df = pd.DataFrame(results)
    df = df.fillna("")
    df = df.replace("nan", "")
    df = df.replace("None", "")
    return df


# ====== 出力 ==================================================================

# ドメイン詳細列の定義（殿の確定仕様: 11列）
_DOMAIN_DETAIL_COLS = [
    "D_データ型",
    "D_最小文字数", "D_最大文字数",
    "D_最小バイト長", "D_最大バイト長",
    "D_最小値", "D_最大値",
    "D_整数部桁数", "D_小数部桁数",
    "D_書式（正規表現）", "D_参照外部コード",
]

# 抽出シートに含める列（画面項目 — 殿の確定仕様シート1: A〜J）
_SCREEN_RAW_COLS = [
    "ファイル名", "項目名称", "型", "テキストタイプ",
    "最小桁", "最大桁", "最大バイト数", "最小値", "最大値", "外部コード",
]

# 抽出シートに含める列（テーブル定義 — 殿の確定仕様シート2: A〜F）
_TABLE_RAW_COLS = [
    "ファイル名", "論理項目名", "データ型", "Length", "全体数値", "少数桁",
]

# 重複排除シートの列（画面項目 — 殿の確定仕様シート3: A〜L）
_SCREEN_DEDUP_COLS = [
    "項目名称", "型", "テキストタイプ",
    "最小桁", "最大桁", "最大バイト数", "最小値", "最大値", "外部コード",
    "一致ドメイン名", "判定結果", "備考",
]

# 重複排除シートの列（テーブル定義 — 殿の確定仕様シート4: A〜H）
_TABLE_DEDUP_COLS = [
    "論理項目名", "データ型", "Length", "全体数値", "少数桁",
    "一致ドメイン名", "判定結果", "備考",
]


def save_domain_check_results(
    screen_df: pd.DataFrame,
    table_df: pd.DataFrame,
    screen_dedup_df: pd.DataFrame,
    table_dedup_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Path:
    """4シート構成のExcelファイルを保存する（確定仕様）。

    シート1: 画面項目_抽出（生データ + VLOOKUP列）
    シート2: テーブル定義_抽出（生データ + VLOOKUP列）
    シート3: 画面項目_重複排除（A〜L + ドメイン詳細M〜）
    シート4: テーブル定義_重複排除（A〜H + ドメイン詳細I〜）

    Returns:
        出力ファイルのPath
    """
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill
    from openpyxl.utils import get_column_letter

    out_dir = Path(cfg["OUT_DIR"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / "domain_check_result.xlsx"

    # 抽出シート用に列を絞る（A〜J / A〜F）
    screen_raw = _select_columns(screen_df, _SCREEN_RAW_COLS)
    table_raw = _select_columns(table_df, _TABLE_RAW_COLS)

    # 重複排除シート用に列を絞る（基本列 + ドメイン詳細列）
    screen_dedup = _select_columns(screen_dedup_df, _SCREEN_DEDUP_COLS + _DOMAIN_DETAIL_COLS)
    table_dedup = _select_columns(table_dedup_df, _TABLE_DEDUP_COLS + _DOMAIN_DETAIL_COLS)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        screen_raw.to_excel(writer, sheet_name="画面項目_抽出", index=False)
        table_raw.to_excel(writer, sheet_name="テーブル定義_抽出", index=False)
        screen_dedup.to_excel(writer, sheet_name="画面項目_重複排除", index=False)
        table_dedup.to_excel(writer, sheet_name="テーブル定義_重複排除", index=False)

    wb = load_workbook(output_file)

    # シート1: VLOOKUP列（K列 = 一致ドメイン名を重複排除シートから引く）
    ws1 = wb["画面項目_抽出"]
    vlookup_col_s = len(_SCREEN_RAW_COLS) + 1  # K列
    ws1.cell(row=1, column=vlookup_col_s, value="VLOOKUP")
    # 画面項目_重複排除のA列=項目名称, J列=一致ドメイン名 → col_index=10
    for r in range(2, ws1.max_row + 1):
        ws1.cell(row=r, column=vlookup_col_s,
                 value=f'=IFERROR(VLOOKUP(B{r},画面項目_重複排除!A:J,10,FALSE),"")')

    # シート2: VLOOKUP列（G列 = 一致ドメイン名を重複排除シートから引く）
    ws2 = wb["テーブル定義_抽出"]
    vlookup_col_t = len(_TABLE_RAW_COLS) + 1  # G列
    ws2.cell(row=1, column=vlookup_col_t, value="VLOOKUP")
    # テーブル定義_重複排除のA列=論理項目名, F列=一致ドメイン名 → col_index=6
    for r in range(2, ws2.max_row + 1):
        ws2.cell(row=r, column=vlookup_col_t,
                 value=f'=IFERROR(VLOOKUP(B{r},テーブル定義_重複排除!A:F,6,FALSE),"")')

    # 判定結果列に色付け
    for sheet_name in ("画面項目_重複排除", "テーブル定義_重複排除"):
        ws = wb[sheet_name]
        _apply_result_colors(ws, ws.max_row)

    wb.save(output_file)
    print(f"[INFO] 保存完了: {output_file}")
    return output_file


def _select_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """DataFrameから存在する列のみを選択する。"""
    existing = [c for c in cols if c in df.columns]
    return df[existing].copy()


def _apply_result_colors(ws, max_row: int) -> None:
    """判定結果列にセル色を適用する。"""
    from openpyxl.styles import PatternFill

    fills = {
        "確定": PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid"),
        "候補": PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid"),
        "選択必要": PatternFill(start_color="FFE0B2", end_color="FFE0B2", fill_type="solid"),
        "一致なし": PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid"),
        "対象外": PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid"),
    }
    header_row = [cell.value for cell in ws[1]]
    if "判定結果" not in header_row:
        return
    col_idx = header_row.index("判定結果") + 1
    for row_num in range(2, max_row + 1):
        cell = ws.cell(row=row_num, column=col_idx)
        fill = fills.get(cell.value)
        if fill:
            cell.fill = fill
