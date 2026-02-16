#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比較B検証テスト — 画面項目定義 vs ドメイン定義

仕様根拠:
  - matching_mapping.md Section 10-5 (比較B)
  - domain_checker_spec.md Section 3-4 (比較B)

比較B定義:
  項目定義の列         ←→  ドメイン定義の列       比較内容
  テキストタイプ       ←→  データ型               日本語データ型同士
  最大桁（文字列）     ←→  最大文字数             文字列長の一致
  最大バイト数         ←→  最大バイト長           バイト長の一致
  最小値 / 最大値      ←→  最小値 / 最大値        数値範囲の照合
  外部コード           ←→  参照外部コード         外部コードの照合
"""

import sys
from pathlib import Path

import pytest

# プロジェクトルート（word/）をパスに追加してインポート可能にする
_word_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_word_root))

from domain.domain_check import DomainDef, ScreenItem
from domain.domain_matcher import (
    _clean_str,
    _compare_min_max,
    _compare_value,
    _compute_detail_matches,
    _filter_by_text_type,
    _DEFAULT_TEXT_TYPE_MAPPING,
    _DEFAULT_TYPE_MAPPING,
    _classify_major_type,
    collect_evidence,
    normalize_text,
    strip_digits,
)


# ============================================================
# テスト用ファクトリ関数
# ============================================================

def make_domain(
    name,
    data_type,
    *,
    column_def_type=None,
    column_def_raw=None,
    max_char=None,
    max_byte=None,
    min_char=None,
    min_byte=None,
    integer_digits=None,
    decimal_digits=None,
    min_value=None,
    max_value=None,
    code_id="",
    regex=None,
):
    """テスト用DomainDefを簡潔に生成する"""
    return DomainDef(
        name=name,
        data_type=data_type,
        column_def_type=column_def_type,
        column_def_raw=column_def_raw,
        min_char=min_char,
        max_char=max_char,
        min_byte=min_byte,
        max_byte=max_byte,
        integer_digits=integer_digits,
        decimal_digits=decimal_digits,
        min_value=min_value,
        max_value=max_value,
        regex=regex,
        code_id=code_id,
        row_number=1,
        source_file="test.xlsx",
        source_sheet="テスト",
    )


def make_screen_item(
    name,
    *,
    data_type="",
    text_type="",
    max_digits=None,
    max_bytes=None,
    min_digits=None,
    min_value=None,
    max_value=None,
    code_id="",
):
    """テスト用ScreenItemを簡潔に生成する"""
    return ScreenItem(
        item_name=name,
        data_type=data_type,
        text_type=text_type,
        min_digits=min_digits,
        max_digits=max_digits,
        max_bytes=max_bytes,
        min_value=min_value,
        max_value=max_value,
        code_id=code_id,
        row_number=1,
        source_file="test.xlsx",
        source_sheet="テスト",
    )


def _screen_item_to_dict(item: ScreenItem) -> dict:
    """ScreenItem を collect_evidence 用の dict に変換する"""
    return {
        "item_name": item.item_name,
        "data_type": item.data_type,
        "text_type": item.text_type,
        "min_chars": item.min_digits,
        "max_chars": item.max_digits,
        "max_bytes": item.max_bytes,
        "min_value": item.min_value,
        "max_value": item.max_value,
        "external_code": item.code_id,
        "source": "screen",
    }


# ============================================================
# A. テキストタイプ ←→ データ型の一致/不一致
# ============================================================

class TestTextTypeFiltering:
    """_filter_by_text_type: テキストタイプでドメイン候補を絞り込む

    仕様: text_type_mapping.yaml に基づき候補を絞る。
    結果が空になったらフォールバック（全候補を返す）。
    """

    def _make_filtered(self, domains):
        """テスト用のFilteredDomain辞書を作る（details空）"""
        return {
            normalize_text(d.name): (d, {})
            for d in domains
        }

    def test_半角英数字は半角英数字ドメインのみ残す(self):
        domains = [
            make_domain("半角英数字ドメイン", "半角英数字"),
            make_domain("全角文字ドメイン", "全角文字"),
            make_domain("半角文字ドメイン", "半角文字"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("半角英数字", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        domain_types = {d.data_type for d, _ in result.values()}
        assert "半角英数字" in domain_types
        assert "全角文字" not in domain_types

    def test_半角文字は半角文字と半角英数字記号を残す(self):
        domains = [
            make_domain("半角文字ドメイン", "半角文字"),
            make_domain("半角英数字記号ドメイン", "半角英数字記号"),
            make_domain("全角カタカナドメイン", "全角カタカナ"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("半角文字", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        domain_types = {d.data_type for d, _ in result.values()}
        assert "半角文字" in domain_types
        assert "半角英数字記号" in domain_types
        assert "全角カタカナ" not in domain_types

    def test_全角文字はひらがなカタカナも含む(self):
        domains = [
            make_domain("全角文字ドメイン", "全角文字"),
            make_domain("全角ひらがなドメイン", "全角ひらがな"),
            make_domain("全角カタカナドメイン", "全角カタカナ"),
            make_domain("半角数字ドメイン", "半角数字"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("全角文字", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        domain_types = {d.data_type for d, _ in result.values()}
        assert "全角文字" in domain_types
        assert "全角ひらがな" in domain_types
        assert "全角カタカナ" in domain_types
        assert "半角数字" not in domain_types

    def test_マッピング外のテキストタイプは絞り込みなし(self):
        domains = [
            make_domain("D1", "半角英数字"),
            make_domain("D2", "全角文字"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("その他", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        assert len(result) == len(filtered), "マッピング外は全候補を返すべき"

    def test_空テキストタイプは絞り込みなし(self):
        domains = [
            make_domain("D1", "半角英数字"),
            make_domain("D2", "全角文字"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        assert len(result) == len(filtered), "空テキストタイプは全候補を返すべき"

    def test_絞り込み結果が空ならフォールバック(self):
        domains = [
            make_domain("D1", "数値（整数）"),
        ]
        filtered = self._make_filtered(domains)
        result = _filter_by_text_type("半角英字", filtered, _DEFAULT_TEXT_TYPE_MAPPING)
        assert len(result) == len(filtered), "結果が空ならフォールバックして全候補を返すべき"


# ============================================================
# B. 最大桁 ←→ 最大文字数 の一致/不一致
# ============================================================

class TestScreenStringDigitsMatch:
    """画面項目の文字列系: 最大桁 ←→ domain.max_char, 最大バイト数 ←→ domain.max_byte

    仕様: string_max_chars_match, string_max_bytes_match で判定
    """

    def test_最大桁が最大文字数と一致(self):
        domain = make_domain("テストドメイン", "半角英数字", max_char="20")
        item = {"max_chars": "20", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is True

    def test_最大桁が最大文字数と不一致(self):
        domain = make_domain("テストドメイン", "半角英数字", max_char="20")
        item = {"max_chars": "30", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is False

    def test_最大バイト数が最大バイト長と一致(self):
        domain = make_domain("テストドメイン", "全角文字", max_byte="60")
        item = {"max_bytes": "60", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_bytes_match"] is True

    def test_最大バイト数が最大バイト長と不一致(self):
        domain = make_domain("テストドメイン", "全角文字", max_byte="60")
        item = {"max_bytes": "120", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_bytes_match"] is False

    def test_ドメイン側が空ならNone_比較不能(self):
        domain = make_domain("テストドメイン", "半角英数字", max_char=None)
        item = {"max_chars": "20", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is None

    def test_画面側が空ならNone_比較不能(self):
        domain = make_domain("テストドメイン", "半角英数字", max_char="20")
        item = {"max_chars": None, "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is None

    def test_小数付き桁数は正規化して比較(self):
        """12.0 → 12 に正規化されて一致する"""
        domain = make_domain("テストドメイン", "半角英数字", max_char="12")
        item = {"max_chars": "12.0", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is True


# ============================================================
# C. 最小値/最大値 ←→ 最小値/最大値 の一致/不一致
# ============================================================

class TestScreenNumericMinMaxMatch:
    """画面項目の数値系: 最小値/最大値 ←→ domain.min_value/domain.max_value

    仕様: numeric_min_max_match で判定。_compare_min_max() を使用。
    """

    def test_最小値最大値が両方一致(self):
        domain = make_domain("金額ドメイン", "数値（整数）", min_value="0", max_value="999999")
        item = {"min_value": "0", "max_value": "999999", "source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_min_max_match"] is True

    def test_最大値のみ不一致(self):
        domain = make_domain("金額ドメイン", "数値（整数）", min_value="0", max_value="999999")
        item = {"min_value": "0", "max_value": "99999", "source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_min_max_match"] is False

    def test_最小値のみ不一致(self):
        domain = make_domain("金額ドメイン", "数値（整数）", min_value="1", max_value="999999")
        item = {"min_value": "0", "max_value": "999999", "source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_min_max_match"] is False

    def test_両方空ならNone_比較不能(self):
        domain = make_domain("金額ドメイン", "数値（整数）")
        item = {"source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_min_max_match"] is None

    def test_片方だけ値がある場合も判定可能(self):
        """最大値のみ両方にあれば比較する"""
        domain = make_domain("金額ドメイン", "数値（整数）", max_value="100")
        item = {"max_value": "100", "source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_min_max_match"] is True


# ============================================================
# D. 外部コード ←→ 参照外部コード の一致/不一致
# ============================================================

class TestExternalCodeMatch:
    """全分類共通: external_code ←→ domain.code_id

    仕様: external_code_match で判定。全分類共通で比較される。
    """

    def test_外部コードが一致(self):
        domain = make_domain("コードドメイン", "コード", code_id="CD001")
        item = {"external_code": "CD001", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is True

    def test_外部コードが不一致(self):
        domain = make_domain("コードドメイン", "コード", code_id="CD001")
        item = {"external_code": "CD999", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is False

    def test_画面側が空ならNone(self):
        domain = make_domain("コードドメイン", "コード", code_id="CD001")
        item = {"external_code": "", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is None

    def test_ドメイン側が空ならNone(self):
        domain = make_domain("コードドメイン", "コード", code_id="")
        item = {"external_code": "CD001", "source": "screen"}
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is None

    def test_数値系でも外部コード比較は実行される(self):
        """外部コードは全分類共通で比較される仕様"""
        domain = make_domain("金額ドメイン", "数値（整数）", code_id="NUM001")
        item = {"external_code": "NUM001", "source": "screen"}
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["external_code_match"] is True


# ============================================================
# E. 統合テスト: collect_evidence で比較Bフロー全体を検証
# ============================================================

class TestComparisonBIntegration:
    """collect_evidence を通した比較Bの統合検証

    画面項目をdict化して collect_evidence に渡し、
    比較Bのフロー全体が仕様通りに動作するかを確認する。
    """

    def _make_domains(self, domain_list):
        """テスト用ドメイン辞書（正規化名キー）を作る"""
        return {normalize_text(d.name): d for d in domain_list}

    def test_テキストタイプ一致かつ桁数一致で完全一致(self):
        """画面項目「ユーザ名」(半角英数字, 最大桁20) vs ドメイン「ユーザ名」(半角英数字, max_char=20)"""
        domain = make_domain("ユーザ名", "半角英数字", max_char="20")
        domains = self._make_domains([domain])
        item = _screen_item_to_dict(make_screen_item(
            "ユーザ名", data_type="テキスト", text_type="半角英数字", max_digits="20",
        ))
        ev = collect_evidence(item, domains, {})
        assert ev.is_resolved is True
        assert ev.match_type == "exact"
        assert ev.resolved_domain == "ユーザ名"

    def test_名前一致だが桁数不一致でLLM送り(self):
        """同名ドメインがあるが桁数が異なる → is_resolved=False"""
        domain = make_domain("ユーザ名", "半角英数字", max_char="50")
        domains = self._make_domains([domain])
        item = _screen_item_to_dict(make_screen_item(
            "ユーザ名", data_type="テキスト", text_type="半角英数字", max_digits="20",
        ))
        ev = collect_evidence(item, domains, {})
        assert ev.is_resolved is False
        assert ev.match_type == "needs_llm"

    def test_テキストタイプ不一致でもフォールバックで候補に含まれる(self):
        """テキストタイプが半角英字だがドメインが全角文字のみの場合、フォールバック"""
        domain = make_domain("住所", "全角文字", max_char="100")
        domains = self._make_domains([domain])
        item = _screen_item_to_dict(make_screen_item(
            "住所", data_type="テキスト", text_type="半角英字", max_digits="100",
        ))
        ev = collect_evidence(item, domains, {})
        # テキストタイプ不一致だが、フォールバックにより候補に含まれ、
        # 名前一致 + 桁数一致 → exact になるはず
        assert ev.is_resolved is True
        assert ev.match_type == "exact"

    def test_対象外判定_属性列が全て空(self):
        """テキストタイプ～外部コードが全て空 → out_of_scope"""
        domain = make_domain("ダミー", "半角英数字", max_char="20")
        domains = self._make_domains([domain])
        item = _screen_item_to_dict(make_screen_item("ボタン名"))
        ev = collect_evidence(item, domains, {})
        assert ev.is_resolved is True
        assert ev.match_type == "out_of_scope"

    def test_外部コード一致でconfidence加点(self):
        """外部コード一致 → resolve_without_llm で confidence + 0.05"""
        from domain.domain_matcher import resolve_without_llm

        domain = make_domain("区分コード", "コード", max_char="3", code_id="CD001")
        domains = self._make_domains([domain])
        item = _screen_item_to_dict(make_screen_item(
            "区分コード",
            data_type="コンボボックス",
            text_type="",
            max_digits="3",
            code_id="CD001",
        ))
        ev = collect_evidence(item, domains, {})
        assert ev.is_resolved is True
        result = resolve_without_llm(ev)
        assert result is not None
        assert result.confidence > 1.0 - 0.01  # 1.0 + 0.05 → capped at 1.0


# ============================================================
# F. 値比較ユーティリティの単体テスト
# ============================================================

class TestCompareMinMax:
    """_compare_min_max: 最小値・最大値のペア比較"""

    def test_両方一致(self):
        assert _compare_min_max("0", "100", "0", "100") is True

    def test_最小値不一致(self):
        assert _compare_min_max("1", "100", "0", "100") is False

    def test_最大値不一致(self):
        assert _compare_min_max("0", "200", "0", "100") is False

    def test_両方空(self):
        assert _compare_min_max(None, None, None, None) is None

    def test_片方だけ値あり_一致(self):
        assert _compare_min_max(None, "100", None, "100") is True

    def test_片方だけ値あり_不一致(self):
        assert _compare_min_max(None, "200", None, "100") is False


class TestCleanStr:
    """_clean_str: 値の正規化"""

    def test_float_integer(self):
        assert _clean_str(12.0) == "12"

    def test_float_decimal(self):
        assert _clean_str(12.5) == "12.5"

    def test_string_trailing_zero(self):
        assert _clean_str("20.0") == "20"

    def test_none_returns_empty(self):
        assert _clean_str(None) == ""

    def test_normal_string(self):
        assert _clean_str("abc") == "abc"
