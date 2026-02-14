#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C方式マッチングエンジン — 前処理・情報収集

項目（画面項目定義 / テーブル定義）とドメイン定義の照合において、
確定ケースは直接判定し、曖昧なケースはB方式（LLM）に渡す
判断材料（MatchEvidence）を収集する。

パイプライン設計:
    C方式（本モジュール）= 前処理・情報収集
    B方式（llm_matcher.py）= Cの結果を受けて最終判断

判定フロー（domain_checker_spec.md Section 3-1 準拠）:
    1. 対象外判定 → 属性列が全て空なら「対象外」で終了
    2. 特殊パターン判定（フラグ / 日付 / コメント・補記）
    3. 大分類判定 → 不一致ならアウト
    4. 桁数一致判定（最重要・大前提）→ 不一致なら即アウト
    5. テキストタイプで絞り込み（画面項目定義のみ）
    6. C方式: 項目名の部分一致＋同義語辞書で材料収集
    7. B方式: LLMに材料を渡して最終判定
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:
    from .domain_check import (
        DomainDef,
        normalize_text,
        normalize_data_type,
        calc_similarity,
    )
except ImportError:
    from domain_check import (
        DomainDef,
        normalize_text,
        normalize_data_type,
        calc_similarity,
    )


# ===========================================================================
# データ構造
# ===========================================================================

@dataclass
class MatchEvidence:
    """C方式が収集した判断材料。

    is_resolved=True: C方式だけで判定完了。resolve_without_llm() で変換可。
    is_resolved=False: B方式（LLM）に判断を委ねる。証拠が格納されている。
    """

    item_name: str
    data_type: str
    digits: str

    # 確定ケース
    is_resolved: bool
    match_type: str  # exact | special_flag | special_date
                     # | special_date_individual | special_comment
                     # | no_type_digits_match | out_of_scope | needs_llm
    resolved_domain: str | None

    # 証拠（B方式に渡す）
    type_digits_matches: list[dict] = field(default_factory=list)
    partial_match_scores: dict[str, float] = field(default_factory=dict)
    synonym_hits: dict[str, list[str]] = field(default_factory=dict)
    detail_matches: dict = field(default_factory=dict)
    reason: str = ""


@dataclass
class MatchResult:
    """最終判定結果（C確定 or B確定）。"""

    item_name: str
    match_type: str
    domain_name: str | None
    confidence: float
    reason: str


# ===========================================================================
# 前処理
# ===========================================================================

_DIGITS_RE = re.compile(r"\d+")


def strip_digits(name: str) -> str:
    """項目名から数字を除去する。比較時に使用。

    例: "受注日付1" → "受注日付", "ああ1" → "ああ"
    """
    return _DIGITS_RE.sub("", name)


# ===========================================================================
# 値比較ユーティリティ
# ===========================================================================

def _clean_str(val) -> str:
    """値を比較用の文字列に正規化する。None/空は空文字列。"""
    if val is None:
        return ""
    return str(val).strip()


def _compare_value(item_val, domain_val) -> bool | None:
    """2つの値を比較する。

    Returns:
        True:  両方に値があり一致
        False: 両方に値があり不一致
        None:  どちらかが空（比較不能 = フィルタ対象外）
    """
    a = _clean_str(item_val)
    b = _clean_str(domain_val)
    if not a or not b:
        return None
    return a == b


def _compare_value_either(item_val, *domain_vals) -> bool | None:
    """item_val がドメイン側の複数値のいずれかと一致するか比較する。

    テーブル定義の length ↔ 最大文字数 or バイト数_最大 で使用。
    """
    a = _clean_str(item_val)
    if not a:
        return None
    has_domain_val = False
    for dv in domain_vals:
        b = _clean_str(dv)
        if b:
            has_domain_val = True
            if a == b:
                return True
    return False if has_domain_val else None


def _compare_min_max(
    item_min, item_max, domain_min, domain_max,
) -> bool | None:
    """最小値・最大値のペア比較。"""
    min_match = _compare_value(item_min, domain_min)
    max_match = _compare_value(item_max, domain_max)

    if min_match is None and max_match is None:
        return None
    if min_match is False or max_match is False:
        return False
    return True


# ===========================================================================
# YAML設定（暫定インライン定義）
# ashigaru1 の config_loader.py 完成後、_load_mappings() 内の1行を有効化
# ===========================================================================

# --- 型の大分類マッピング (Section 3-2) ---

_DEFAULT_TYPE_MAPPING: dict = {
    "screen": {
        "文字列系": ["テキスト", "テキストエリア", "テーブルカラムテキスト"],
        "数値系": ["数値"],
        "日付系": ["日付"],
        "真偽値系": ["チェックボックス"],
        "コード系": ["コンボボックス", "ラジオボタン"],
    },
    "table": {
        "文字列系": ["CHAR", "VARCHAR", "NCHAR", "NVARCHAR", "CLOB"],
        "数値系": ["NUMBER", "INT", "INTEGER", "DECIMAL", "FLOAT"],
        "日付系": ["DATE", "TIMESTAMP"],
        "バイナリ系": ["RAW", "ROWID"],
    },
    "domain": {
        "文字列系": [
            "半角文字", "半角英字", "半角数字", "半角カナ", "半角英数字", "半角英数字記号",
            "全角文字", "全角英字", "全角数字", "全角ひらがな", "全角カタカナ",
            "全角英数字", "全角英数字記号", "全半角混合",
        ],
        "数値系": ["数値（整数）", "数値（少数）"],
        "日付系": ["日付"],
        "真偽値系": ["真偽値"],
        "コード系": ["コード"],
    },
}

# --- テキストタイプ → ドメインデータ型の対応 (Section 3-3) ---

_DEFAULT_TEXT_TYPE_MAPPING: dict = {
    "半角英字": ["半角英字"],
    "半角数字": ["半角数字"],
    "半角英数字": ["半角英数字"],
    "半角カナ文字": ["半角カナ"],
    "半角文字": ["半角文字", "半角英数字記号"],
    "全角文字": ["全角文字", "全角ひらがな", "全角カタカナ"],
    "全半角混合": ["全半角混合"],
}

# --- 特殊パターン定義 (Section 3-7) ---

_DEFAULT_SPECIAL_PATTERNS: dict = {
    "flag": {
        "keywords": ["フラグ", "flag"],
        "types": ["boolean", "bool", "チェックボックス"],
        "digits": ["0", "1", "0-1", "0,1"],
        "match_type": "special_flag",
        "output": "以下から選択: 0/1, 0/9, null/1, スペース/1",
    },
    "comment": {
        "keywords": ["コメント", "補記", "備考", "メモ"],
        "match_type": "special_comment",
        "output": "改行あり/なしを確認して選択してください",
    },
    "date": {
        "keywords": ["日付", "日時", "date", "時刻"],
        "generic_types": ["date", "datetime", "timestamp", "日付"],
        "generic_formats": [
            "yyyymmdd", "yyyy-mm-dd", "yyyymmddhhmmss", "yyyy-mm-dd hh:mm:ss",
        ],
        "individual_string_types": ["varchar", "char", "テキスト"],
        "individual_format_regex": r"yyyy[/.]mm|mm[/.]dd|yyyy年|hh:mm|hh24|yy/mm",
        "generic_match_type": "special_date",
        "generic_output": "汎用日付",
        "individual_match_type": "special_date_individual",
    },
}


def _load_mappings() -> tuple[dict, dict, dict]:
    """設定マッピングを読み込む。

    Returns: (type_mapping, text_type_mapping, special_patterns)
    """
    # TODO: ashigaru1 の config_loader.py 完成後、以下を有効化:
    # from .config_loader import load_type_mapping, load_text_type_mapping, load_special_patterns
    # return load_type_mapping(), load_text_type_mapping(), load_special_patterns()
    return _DEFAULT_TYPE_MAPPING, _DEFAULT_TEXT_TYPE_MAPPING, _DEFAULT_SPECIAL_PATTERNS


# ===========================================================================
# 対象外判定 (Section 3-1)
# ===========================================================================

_SCREEN_ATTR_KEYS = [
    "text_type", "min_chars", "max_chars", "max_bytes",
    "min_value", "max_value", "external_code",
]
_TABLE_ATTR_KEYS = ["data_type", "length", "integer_digits", "decimal_digits"]


def _is_out_of_scope(item: dict) -> bool:
    """属性列が全て空なら対象外と判定する。

    画面項目: テキストタイプ〜外部コードが全て空 → 対象外
    テーブル定義: データ型〜少数桁が全て空 → 対象外
    """
    source = item.get("source", "screen")
    check_keys = _SCREEN_ATTR_KEYS if source == "screen" else _TABLE_ATTR_KEYS
    return all(not _clean_str(item.get(k)) for k in check_keys)


# ===========================================================================
# 特殊パターン判定 (Section 3-7, YAML設定ベース)
# ===========================================================================

def _resolved(
    name: str, type_norm: str, digits: str,
    match_type: str, domain: str | None, reason: str,
) -> MatchEvidence:
    """確定済み MatchEvidence を生成するヘルパー。"""
    return MatchEvidence(
        item_name=name,
        data_type=type_norm,
        digits=digits,
        is_resolved=True,
        match_type=match_type,
        resolved_domain=domain,
        reason=reason,
    )


def _check_special_patterns(
    name_stripped: str, type_norm: str, digits: str,
    patterns_cfg: dict,
) -> MatchEvidence | None:
    """特殊パターンを順に判定する。該当すれば確定済み MatchEvidence を返す。"""
    # フラグ
    flag = _check_flag_pattern(name_stripped, type_norm, digits, patterns_cfg.get("flag", {}))
    if flag is not None:
        return flag

    # コメント・補記
    comment = _check_comment_pattern(name_stripped, patterns_cfg.get("comment", {}))
    if comment is not None:
        return comment

    # 日付
    date = _check_date_pattern(name_stripped, type_norm, digits, patterns_cfg.get("date", {}))
    if date is not None:
        return date

    return None


def _check_flag_pattern(
    name_stripped: str, type_norm: str, digits: str,
    cfg: dict,
) -> MatchEvidence | None:
    """フラグ系: 項目名にキーワード含む + boolean/0-1 → 人間に選択肢を提示。"""
    keywords = cfg.get("keywords", [])
    if not any(kw in name_stripped for kw in keywords):
        return None

    types = frozenset(cfg.get("types", []))
    digit_patterns = frozenset(cfg.get("digits", []))
    if type_norm not in types and digits not in digit_patterns:
        return None

    return _resolved(
        name_stripped, type_norm, digits,
        match_type=cfg.get("match_type", "special_flag"),
        domain=cfg.get("output", ""),
        reason=f"フラグ系: 項目名に「フラグ」含む → 人間選択",
    )


def _check_comment_pattern(
    name_stripped: str, cfg: dict,
) -> MatchEvidence | None:
    """コメント・補記系: 項目名にキーワード含む → 人間に選択肢を提示。"""
    for kw in cfg.get("keywords", []):
        if kw in name_stripped:
            return _resolved(
                name_stripped, "", "",
                match_type=cfg.get("match_type", "special_comment"),
                domain=cfg.get("output", ""),
                reason=f"コメント・補記系: 項目名に「{kw}」含む → 人間選択",
            )
    return None


def _check_date_pattern(
    name_stripped: str, type_norm: str, digits: str,
    cfg: dict,
) -> MatchEvidence | None:
    """日付系パターン判定。

    - date型 + yyyyMMdd系 → 汎用日付ドメイン確定
    - string型 + yyyy/MM等 → 個別ドメイン定義必要として確定
    """
    keywords = cfg.get("keywords", [])
    if not any(kw in name_stripped for kw in keywords):
        return None

    digits_lower = digits.lower().replace(" ", "") if digits else ""

    # date型 + 標準フォーマット → 汎用日付
    generic_types = frozenset(cfg.get("generic_types", []))
    generic_formats = frozenset(cfg.get("generic_formats", []))
    if type_norm in generic_types:
        if not digits_lower or digits_lower in generic_formats:
            return _resolved(
                name_stripped, type_norm, digits,
                match_type=cfg.get("generic_match_type", "special_date"),
                domain=cfg.get("generic_output", "汎用日付"),
                reason=f"汎用日付: date型 + 標準フォーマット（{digits or 'なし'}）",
            )

    # string型 + カスタムフォーマット → 個別ドメイン必要
    individual_types = frozenset(cfg.get("individual_string_types", []))
    individual_re = cfg.get("individual_format_regex", "")
    if type_norm in individual_types or not type_norm:
        if digits and individual_re and re.search(individual_re, digits, re.IGNORECASE):
            return _resolved(
                name_stripped, type_norm, digits,
                match_type=cfg.get("individual_match_type", "special_date_individual"),
                domain=None,
                reason=f"個別日付: 文字列型 + カスタムフォーマット（{digits}）→ 個別ドメイン定義が必要",
            )

    return None


# ===========================================================================
# 大分類判定 (Section 3-2)
# ===========================================================================

def _classify_major_type(type_str: str, source: str, type_mapping: dict) -> str:
    """型文字列を大分類に変換する。部分一致で検索。

    Args:
        type_str: 生のデータ型文字列
        source: "screen" | "table" | "domain"
        type_mapping: 大分類マッピング辞書

    Returns: "文字列系" | "数値系" | "日付系" | "真偽値系" | "コード系" | "バイナリ系" | "不明"
    """
    if not type_str or not type_str.strip():
        return "不明"

    clean = type_str.strip()
    clean_upper = clean.upper()
    source_map = type_mapping.get(source, {})

    for category, patterns in source_map.items():
        for p in patterns:
            # 部分一致: パターンが型に含まれる or 型がパターンに含まれる
            if p.upper() in clean_upper or clean_upper in p.upper():
                return category
    return "不明"


def _filter_by_major_type(
    item_major: str,
    domains: Dict[str, DomainDef],
    type_mapping: dict,
) -> Dict[str, DomainDef]:
    """大分類が一致するドメインのみ返す。

    項目の大分類が「不明」の場合は全ドメインを通す（桁数で判定へ回す）。
    """
    if item_major == "不明":
        return dict(domains)

    matched: Dict[str, DomainDef] = {}
    for key, domain in domains.items():
        d_major = _classify_major_type(domain.data_type, "domain", type_mapping)
        if d_major == "不明" or d_major == item_major:
            matched[key] = domain
    return matched


# ===========================================================================
# 桁数照合（詳細照合）(Section 3-4)
# ===========================================================================

FilteredDomain = tuple[DomainDef, dict]


def _compute_detail_matches(
    item: dict, domain: DomainDef, item_major: str,
) -> dict:
    """大分類に基づいてデータ型別の桁数照合を実施する。

    大分類フィルタ通過後に呼ばれるため、型の不一致チェックは不要。
    """
    details: dict = {}
    is_table = item.get("source") == "table"

    # --- 文字列系 ---
    if item_major == "文字列系":
        if is_table:
            table_length = item.get("length") or item.get("max_chars")
            details["string_length_match"] = _compare_value_either(
                table_length, domain.max_char, domain.max_byte,
            )
        else:
            details["string_max_chars_match"] = _compare_value(
                item.get("max_chars"), domain.max_char,
            )
            details["string_max_bytes_match"] = _compare_value(
                item.get("max_bytes"), domain.max_byte,
            )

    # --- 数値系 ---
    elif item_major == "数値系":
        if is_table:
            details["numeric_integer_digits_match"] = _compare_value(
                item.get("integer_digits"), _clean_str(domain.integer_digits),
            )
            details["numeric_decimal_digits_match"] = _compare_value(
                item.get("decimal_digits"), _clean_str(domain.decimal_digits),
            )
        else:
            details["numeric_min_max_match"] = _compare_min_max(
                item.get("min_value"), item.get("max_value"),
                domain.min_value, domain.max_value,
            )

    # --- 外部コード（全分類共通）---
    details["external_code_match"] = _compare_value(
        item.get("external_code"), domain.code_id,
    )

    # --- 書式（参考情報として記録）---
    if _clean_str(domain.regex):
        details["has_regex"] = True

    return details


def _has_hard_mismatch(details: dict) -> bool:
    """詳細照合結果に False（明確な不一致）があるか判定する。"""
    return any(v is False for v in details.values())


def _filter_by_digits(
    item: dict,
    domains: Dict[str, DomainDef],
    item_major: str,
) -> Dict[str, FilteredDomain]:
    """桁数照合で明確な不一致があるドメインを除外する。"""
    matched: Dict[str, FilteredDomain] = {}
    for key, domain in domains.items():
        details = _compute_detail_matches(item, domain, item_major)
        if _has_hard_mismatch(details):
            continue
        matched[key] = (domain, details)
    return matched


# ===========================================================================
# テキストタイプ絞り込み (Section 3-3, 画面項目定義のみ)
# ===========================================================================

def _filter_by_text_type(
    text_type: str,
    filtered: Dict[str, FilteredDomain],
    text_type_mapping: dict,
) -> Dict[str, FilteredDomain]:
    """テキストタイプでドメイン候補を絞り込む。

    画面項目定義のみ適用。テーブル定義はテキストタイプがないためスキップ。
    text_type が「その他」やマッピング外の場合は絞り込みなし。
    """
    if not text_type:
        return dict(filtered)

    allowed = text_type_mapping.get(text_type.strip())
    if not allowed:
        return dict(filtered)

    allowed_set = set(allowed)
    result = {
        key: (domain, details)
        for key, (domain, details) in filtered.items()
        if domain.data_type.strip() in allowed_set
    }

    # 絞り込みすぎ防止: 全候補がなくなったらフォールバック
    return result if result else dict(filtered)


# ===========================================================================
# 項目名比較（フィルタ通過後）
# ===========================================================================

def _check_exact_name_match(
    name_stripped: str,
    filtered: Dict[str, FilteredDomain],
    type_norm: str, digits: str,
) -> MatchEvidence | None:
    """数字除去後の項目名で完全一致を検索する。"""
    for key, (domain, details) in filtered.items():
        domain_name_stripped = strip_digits(key)
        if name_stripped == domain_name_stripped:
            ev = _resolved(
                name_stripped, type_norm, digits,
                match_type="exact",
                domain=domain.name,
                reason=f"完全一致: 名前（数字除去後）+ 型桁一致（{domain.name}）",
            )
            ev.detail_matches = details
            return ev
    return None


def _check_synonym_matches(
    name_stripped: str,
    filtered: Dict[str, FilteredDomain],
    synonyms: dict | None,
) -> dict[str, list[str]]:
    """同義語辞書を使って、フィルタ通過ドメインから同義語ヒットを検索する。

    Returns:
        { ドメイン名: [ヒットした同義語の正規形, ...] }
    """
    if not synonyms:
        return {}

    hits: dict[str, list[str]] = {}
    for key, (domain, _details) in filtered.items():
        domain_stripped = strip_digits(key)
        matched_syns = _find_synonym_hits(name_stripped, domain_stripped, synonyms)
        if matched_syns:
            hits[domain.name] = matched_syns
    return hits


def _find_synonym_hits(
    item_name: str, domain_key: str,
    synonyms: dict,
) -> list[str]:
    """同義語辞書から項目名↔ドメイン名の共通ヒットを検索する。

    synonyms: { "正規形": ["同義語1", "同義語2", ...] } （YAMLから読み込み）
    """
    hits = []
    for canonical, variants in synonyms.items():
        all_forms = [canonical] + list(variants)
        item_hit = any(form in item_name for form in all_forms)
        domain_hit = any(form in domain_key for form in all_forms)
        if item_hit and domain_hit:
            hits.append(canonical)
    return hits


# ===========================================================================
# 証拠収集（LLM判定用）
# ===========================================================================

def _calc_partial_match_score(item_name: str, domain_key: str) -> float:
    """接頭辞・接尾辞の共通部分から部分一致率を計算する。"""
    if not item_name or not domain_key:
        return 0.0

    prefix_len = 0
    for a, b in zip(item_name, domain_key):
        if a != b:
            break
        prefix_len += 1

    suffix_len = 0
    for a, b in zip(reversed(item_name), reversed(domain_key)):
        if a != b:
            break
        suffix_len += 1

    max_len = max(len(item_name), len(domain_key))
    return max(prefix_len, suffix_len) / max_len if max_len > 0 else 0.0


def _gather_evidence_for_llm(
    name_stripped: str, type_norm: str, digits: str,
    filtered: Dict[str, FilteredDomain],
    synonyms: dict | None,
    top_n: int = 5,
) -> MatchEvidence:
    """フィルタ通過ドメインの中から、LLM判定用の証拠を収集する。"""
    candidates: list[dict] = []
    partial_scores: dict[str, float] = {}
    synonym_map = _check_synonym_matches(name_stripped, filtered, synonyms)
    best_details: dict = {}

    for key, (domain, details) in filtered.items():
        domain_stripped = strip_digits(key)
        sim = calc_similarity(name_stripped, domain_stripped)

        candidates.append({
            "domain_name": domain.name,
            "domain_type": domain.data_type,
            "name_similarity": round(sim, 3),
            "has_synonym_hit": domain.name in synonym_map,
            "detail": details,
        })

        partial = _calc_partial_match_score(name_stripped, domain_stripped)
        if partial > 0.3:
            partial_scores[domain.name] = round(partial, 3)

    candidates.sort(key=lambda c: c["name_similarity"], reverse=True)
    candidates = candidates[:top_n]

    if candidates:
        best_details = candidates[0].get("detail", {})

    parts = []
    if candidates:
        top = candidates[0]
        parts.append(f"最上位候補: {top['domain_name']}（類似度{top['name_similarity']:.0%}）")
    if synonym_map:
        parts.append(f"同義語ヒット: {len(synonym_map)}件")
    parts.append(f"フィルタ通過: {len(filtered)}件中上位{len(candidates)}件")

    return MatchEvidence(
        item_name=name_stripped,
        data_type=type_norm,
        digits=digits,
        is_resolved=False,
        match_type="needs_llm",
        resolved_domain=None,
        type_digits_matches=candidates,
        partial_match_scores=partial_scores,
        synonym_hits=synonym_map,
        detail_matches=best_details,
        reason=" / ".join(parts),
    )


# ===========================================================================
# 公開 API
# ===========================================================================

def collect_evidence(
    item: dict,
    domains: Dict[str, DomainDef],
    config: dict,
    synonyms: dict | None = None,
) -> MatchEvidence:
    """1項目の判断材料を収集する。確定ケースは is_resolved=True で返す。

    判定フロー（domain_checker_spec.md Section 3-1 準拠）:
        0. 対象外判定 → 属性列が全て空なら対象外
        1. 特殊パターン判定 → 該当すれば確定
        2. 大分類判定 → 不一致ならアウト
        3. 桁数一致判定 → 不一致なら即アウト
        4. テキストタイプで絞り込み（画面のみ）
        5. 項目名比較 → 完全一致=確定 / 同義語=候補 / 他=LLM

    Args:
        item: 項目情報辞書。source キーで画面項目/テーブル定義を区別する。
              共通: item_name(必須), data_type(必須), source("screen"|"table")
              画面項目: text_type(テキストタイプ), min_chars(最小桁), max_chars(最大桁),
                        max_bytes(最大バイト数), min_value(最小値), max_value(最大値),
                        external_code(外部コード)
              テーブル定義: length(Length), integer_digits(全体数値),
                            decimal_digits(少数桁)
        domains: ドメイン定義辞書（正規化名キー → DomainDef）
        config: 設定辞書（FUZZY_THRESHOLD 等）
        synonyms: 同義語辞書 { "正規形": ["同義語", ...] }。None可。
    """
    type_mapping, text_type_mapping, special_patterns = _load_mappings()

    item_name = item.get("item_name", "")
    raw_data_type = item.get("data_type", "")
    text_type = item.get("text_type", "")
    source = item.get("source", "screen")

    name_norm = normalize_text(item_name)
    type_norm = normalize_data_type(raw_data_type)
    max_chars = item.get("max_chars") or item.get("length") or item.get("digits", "")
    digits_clean = _clean_str(max_chars)
    name_stripped = strip_digits(name_norm)

    # Step 0: 対象外判定
    if _is_out_of_scope(item):
        return _resolved(
            name_stripped, type_norm, digits_clean,
            match_type="out_of_scope",
            domain=None,
            reason="対象外: 属性列が全て空",
        )

    # Step 1: 特殊パターン判定
    sp = _check_special_patterns(name_stripped, type_norm, digits_clean, special_patterns)
    if sp is not None:
        return sp

    # Step 2: 大分類判定でドメインフィルタ
    item_major = _classify_major_type(raw_data_type, source, type_mapping)
    major_filtered = _filter_by_major_type(item_major, domains, type_mapping)
    if not major_filtered:
        return _resolved(
            name_stripped, type_norm, digits_clean,
            match_type="no_type_digits_match",
            domain=None,
            reason=f"大分類不一致: 型={raw_data_type}（{item_major}）に一致するドメインなし",
        )

    # Step 3: 桁数一致判定（最重要・大前提）
    digits_filtered = _filter_by_digits(item, major_filtered, item_major)
    if not digits_filtered:
        return _resolved(
            name_stripped, type_norm, digits_clean,
            match_type="no_type_digits_match",
            domain=None,
            reason=f"桁数不一致: 大分類={item_major}, 桁={digits_clean or '(空)'} に一致するドメインなし",
        )

    # Step 4: テキストタイプで絞り込み（画面項目定義のみ）
    if source == "screen" and text_type:
        final_filtered = _filter_by_text_type(text_type, digits_filtered, text_type_mapping)
    else:
        final_filtered = digits_filtered

    # Step 5a: 完全一致（数字除去後の名前）
    exact = _check_exact_name_match(
        name_stripped, final_filtered, type_norm, digits_clean,
    )
    if exact is not None:
        return exact

    # Step 5b/5c: 同義語ヒット + LLM用証拠を収集
    return _gather_evidence_for_llm(
        name_stripped, type_norm, digits_clean,
        final_filtered, synonyms,
    )


def collect_evidence_batch(
    items: list[dict],
    domains: Dict[str, DomainDef],
    config: dict,
    synonyms: dict | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[MatchEvidence]:
    """全項目の判断材料を一括収集する。

    Args:
        items: [{"item_name": ..., "data_type": ..., ...}, ...]
               各 dict は collect_evidence() の item 引数と同じ形式。
        domains: ドメイン定義辞書
        config: 設定辞書
        synonyms: 同義語辞書（None可、YAMLから読み込み）
        progress_callback: 進捗コールバック (processed, total)
    """
    total = len(items)
    results: list[MatchEvidence] = []

    for i, item in enumerate(items):
        ev = collect_evidence(
            item=item,
            domains=domains,
            config=config,
            synonyms=synonyms,
        )
        results.append(ev)

        if progress_callback and ((i + 1) % 10 == 0 or i + 1 == total):
            progress_callback(i + 1, total)

    return results


def resolve_without_llm(evidence: MatchEvidence) -> MatchResult | None:
    """確定ケース（is_resolved=True）を MatchResult に変換する。

    未確定ケースは None を返す（B方式に委ねる）。
    外部コード一致や数値桁数一致は確信度を加点する。
    """
    if not evidence.is_resolved:
        return None

    confidence_map = {
        "exact": 1.0,
        "special_flag": 0.95,
        "special_date": 0.95,
        "special_date_individual": 0.90,
        "special_comment": 0.95,
        "no_type_digits_match": 1.0,
        "out_of_scope": 1.0,
    }

    confidence = confidence_map.get(evidence.match_type, 0.8)

    # 外部コード一致で加点
    if evidence.detail_matches.get("external_code_match") is True:
        confidence = min(confidence + 0.05, 1.0)

    # 数値系: 整数部+小数部の両方一致で加点
    int_match = evidence.detail_matches.get("numeric_integer_digits_match")
    dec_match = evidence.detail_matches.get("numeric_decimal_digits_match")
    if int_match is True and dec_match is True:
        confidence = min(confidence + 0.03, 1.0)

    return MatchResult(
        item_name=evidence.item_name,
        match_type=evidence.match_type,
        domain_name=evidence.resolved_domain,
        confidence=confidence,
        reason=evidence.reason,
    )


def build_llm_context(evidence: MatchEvidence) -> dict:
    """未確定ケースの evidence をLLMに渡す形式に変換する。

    B方式（llm_matcher.py）がこの辞書をプロンプトに埋め込んで
    最終判定を行う。
    """
    return {
        "item": {
            "name": evidence.item_name,
            "data_type": evidence.data_type,
            "digits": evidence.digits,
        },
        "candidates": evidence.type_digits_matches,
        "partial_matches": evidence.partial_match_scores,
        "synonym_hits": evidence.synonym_hits,
        "detail_matches": evidence.detail_matches,
        "summary": evidence.reason,
    }
