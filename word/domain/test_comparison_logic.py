#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比較ロジック検証スクリプト

殿の確定指示に基づく2つの比較仕様を検証する:

  比較A: テーブル定義 vs ドメイン定義
    - テーブル側データ型      ←→ ドメイン側カラム定義
    - テーブル側桁数(整数)     ←→ カラム定義の桁
    - テーブル側小数桁         ←→ カラム定義の小数桁
    - 文字列の場合の桁        ←→ 文字列長
    - フォールバック: カラム定義列が空 → 従来のデータ型比較

  比較B: 項目定義（画面） vs ドメイン定義
    - テキストタイプ          ←→ データ型
    - 文字列の場合の桁        ←→ 文字列～最大桁

テストケースはサンプルExcelから抽出した代表的なデータに基づく:
  - out/sample_domain.xlsx
  - out/sample_table.xlsx
  - out/sample_screen.xlsx
"""

import sys
from pathlib import Path

import pytest

# プロジェクトルート（word/）をパスに追加してインポート可能にする
_word_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_word_root))

from domain.domain_check import (
    DomainDef,
    TableItem,
    ScreenItem,
    _parse_column_def,
    _parse_column_def_type,
    _parse_length_from_type,
    _parse_numeric_from_type,
)
from domain.domain_matcher import (
    _clean_str,
    _compare_value,
    _compare_value_either,
    _compute_detail_matches,
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
    code_id="",
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
        min_value=None,
        max_value=None,
        regex=None,
        code_id=code_id,
        row_number=1,
        source_file="test.xlsx",
        source_sheet="テスト",
    )


def make_table_item(name, data_type, *, length=None, integer_part=None, decimal_part=None):
    """テスト用TableItemを簡潔に生成する"""
    return TableItem(
        item_name=name,
        data_type=data_type,
        length=length,
        integer_part=integer_part,
        decimal_part=decimal_part,
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
        min_value=None,
        max_value=None,
        code_id=code_id,
        row_number=1,
        source_file="test.xlsx",
        source_sheet="テスト",
    )


# ============================================================
# 1. カラム定義パース: 桁数抽出
# ============================================================

class TestParseColumnDef:
    """_parse_column_def: カラム定義文字列 → 桁数"""

    def test_char_12(self):
        assert _parse_column_def("CHAR(12)") == 12

    def test_varchar2_200(self):
        assert _parse_column_def("VARCHAR2(200)") == 200

    def test_number_3(self):
        assert _parse_column_def("NUMBER(3)") == 3

    def test_number_10_2(self):
        assert _parse_column_def("NUMBER(10,2)") == 10

    def test_nvarchar2_30(self):
        assert _parse_column_def("NVARCHAR2(30)") == 30

    def test_lowercase(self):
        assert _parse_column_def("varchar(20)") == 20

    def test_empty_returns_none(self):
        assert _parse_column_def("") is None

    def test_none_returns_none(self):
        assert _parse_column_def(None) is None


# ============================================================
# 2. カラム定義パース: 型名抽出
# ============================================================

class TestParseColumnDefType:
    """_parse_column_def_type: カラム定義文字列 → 型名"""

    def test_char(self):
        assert _parse_column_def_type("CHAR(12)").lower() == "char"

    def test_varchar2(self):
        assert _parse_column_def_type("VARCHAR2(200)").lower() == "varchar2"

    def test_number(self):
        assert _parse_column_def_type("NUMBER(3)").lower() == "number"

    def test_empty(self):
        assert _parse_column_def_type("") == ""

    def test_none(self):
        assert _parse_column_def_type(None) == ""


# ============================================================
# 3. 数値型パース: precision / scale
# ============================================================

class TestParseNumericFromType:
    """_parse_numeric_from_type: 数値型 → (precision, scale)"""

    def test_number_3(self):
        precision, scale = _parse_numeric_from_type("NUMBER(3)")
        assert precision == 3
        assert scale is None

    def test_number_10_2(self):
        precision, scale = _parse_numeric_from_type("NUMBER(10,2)")
        assert precision == 10
        assert scale == 2

    def test_decimal_8_2(self):
        precision, scale = _parse_numeric_from_type("DECIMAL(8,2)")
        assert precision == 8
        assert scale == 2

    def test_empty(self):
        assert _parse_numeric_from_type("") == (None, None)

    def test_non_numeric_type(self):
        """CHAR型は数値パースの対象外"""
        assert _parse_numeric_from_type("CHAR(12)") == (None, None)


# ============================================================
# 4. 文字列型パース: 長さ抽出
# ============================================================

class TestParseLengthFromType:
    """_parse_length_from_type: 文字列型 → 長さ"""

    def test_varchar2_100_byte(self):
        assert _parse_length_from_type("VARCHAR2(100 BYTE)") == 100

    def test_varchar2_50_char(self):
        assert _parse_length_from_type("VARCHAR2(50 CHAR)") == 50

    def test_char_12(self):
        assert _parse_length_from_type("CHAR(12)") == 12


# ============================================================
# 5. 値比較ユーティリティ
# ============================================================

class TestCompareValue:
    """_compare_value / _compare_value_either のテスト"""

    def test_equal_values(self):
        assert _compare_value("12", "12") is True

    def test_unequal_values(self):
        assert _compare_value("8", "12") is False

    def test_item_empty_returns_none(self):
        """項目側が空 → 比較不能"""
        assert _compare_value("", "12") is None

    def test_domain_empty_returns_none(self):
        """ドメイン側が空 → 比較不能"""
        assert _compare_value("12", "") is None

    def test_both_empty_returns_none(self):
        assert _compare_value("", "") is None

    def test_none_returns_none(self):
        assert _compare_value(None, "12") is None
        assert _compare_value("12", None) is None


class TestCompareValueEither:
    """_compare_value_either: 複数候補のいずれかと一致するか"""

    def test_first_matches(self):
        assert _compare_value_either("5", "5", "10") is True

    def test_second_matches(self):
        assert _compare_value_either("10", "5", "10") is True

    def test_none_matches(self):
        assert _compare_value_either("7", "5", "10") is False

    def test_item_empty(self):
        assert _compare_value_either("", "5", "10") is None


class TestCleanStr:
    """_clean_str: 比較用の値正規化"""

    def test_float_to_int(self):
        """12.0 → "12" に正規化"""
        assert _clean_str(12.0) == "12"

    def test_float_string(self):
        """文字列 "12.0" → "12" """
        assert _clean_str("12.0") == "12"

    def test_none_to_empty(self):
        assert _clean_str(None) == ""

    def test_strip_whitespace(self):
        assert _clean_str("  5  ") == "5"


# ============================================================
# 6. 比較A: テーブル定義 vs ドメイン定義（カラム定義あり）
#    Oracle型を直接比較する新ロジック
# ============================================================

class TestComparisonA_WithColumnDef:
    """
    カラム定義列がある場合:
      テーブル側データ型      ←→  カラム定義の型（column_def_type）
      テーブル側桁数          ←→  カラム定義の桁
    """

    def test_案件番号_char12_完全一致(self):
        """テーブル char(12) ↔ ドメイン CHAR(12) → 型・桁ともに一致"""
        table = make_table_item("案件番号", "char", length="12")
        domain = make_domain(
            "案件番号", "半角英数字",
            column_def_type="char", max_char="12",
        )
        # 型一致: char == char
        assert table.data_type.lower() == domain.column_def_type.lower()
        # 桁一致: 12 == 12
        assert _compare_value(table.length, domain.max_char) is True

    def test_Agentコード_char2_完全一致(self):
        """テーブル char(2) ↔ ドメイン CHAR(2) → 完全一致"""
        table = make_table_item("Agentコード", "char", length="2")
        domain = make_domain(
            "Agentコード", "コード",
            column_def_type="char", max_char="2",
        )
        assert table.data_type.lower() == domain.column_def_type.lower()
        assert _compare_value(table.length, domain.max_char) is True

    def test_組織店名_varchar2_桁不一致(self):
        """テーブル varchar2(20) ↔ ドメイン VARCHAR2(22) → 型一致だが桁不一致"""
        table = make_table_item("組織店名", "varchar2", length="20")
        domain = make_domain(
            "Agent名称", "全半角混合文字",
            column_def_type="varchar2", max_char="22",
        )
        assert table.data_type.lower() == domain.column_def_type.lower()
        assert _compare_value(table.length, domain.max_char) is False  # 20 ≠ 22

    def test_案件枝番_number3_整数桁比較(self):
        """テーブル number(10,0) ↔ ドメイン NUMBER(3) → 桁不一致"""
        table = make_table_item(
            "条件指示番号", "number",
            integer_part="10", decimal_part="0",
        )
        domain = make_domain(
            "案件枝番", "数値（整数）",
            column_def_type="number", integer_digits="3",
        )
        assert table.data_type.lower() == domain.column_def_type.lower()
        assert _compare_value(table.integer_part, domain.integer_digits) is False  # 10 ≠ 3


# ============================================================
# 7. 比較A: フォールバック（カラム定義なし）
#    カラム定義列が空 → 従来のデータ型比較
# ============================================================

class TestComparisonA_Fallback:
    """
    ドメインの カラム定義 が空（column_def_type=None）の場合、
    従来のデータ型（日本語型名）による比較にフォールバックする。

    sample_domain.xlsx でカラム定義が空のドメイン:
      ON未実施店, WFステータスコード, アラーム, エリアポストコード,
      オペレーションセンター, 改定内容, 開店日, 勘定店区分, 完了日区分
    """

    def test_column_def_type_is_none(self):
        """フォールバック条件: column_def_type が None であること"""
        domain = make_domain("ON未実施店", "半角数字", column_def_type=None)
        assert domain.column_def_type is None

    def test_アラーム_文字列長は有効(self):
        """カラム定義なしでも文字列長の比較は機能する"""
        table = make_table_item("アラーム", "char", length="3")
        domain = make_domain(
            "アラーム", "半角数字",
            column_def_type=None, max_char="3",
        )
        assert domain.column_def_type is None
        assert _compare_value(table.length, domain.max_char) is True  # 3 == 3

    def test_改定内容_varchar2_80(self):
        """カラム定義なしのフォールバック + 文字列長一致"""
        table = make_table_item("改定内容", "varchar2", length="80")
        domain = make_domain(
            "改定内容", "全半角混合文字",
            column_def_type=None, max_char="80",
        )
        assert domain.column_def_type is None
        assert _compare_value(table.length, domain.max_char) is True

    def test_WFステータスコード_コード型(self):
        """カラム定義なし + コード型 → データ型による大分類比較"""
        domain = make_domain(
            "WFステータスコード", "コード",
            column_def_type=None, min_char="5", max_char="5",
        )
        assert domain.column_def_type is None
        assert domain.data_type == "コード"


# ============================================================
# 8. 比較B: 項目定義（画面） vs ドメイン定義
#    テキストタイプ ←→ データ型
#    文字列桁      ←→ 文字列～最大桁
# ============================================================

class TestComparisonB_ScreenVsDomain:
    """
    sample_screen.xlsx の組織店番1/2（テキストタイプ=半角英数字, 桁=4-5）と
    sample_domain.xlsx のエリア店番（半角数字, 桁=4-5）を基にしたテスト。
    """

    def test_組織店番_最大桁一致(self):
        """画面 最大桁=5 ↔ ドメイン 文字列最大=5 → 一致"""
        screen = make_screen_item(
            "組織店番１",
            text_type="半角英数字", min_digits="4", max_digits="5",
        )
        domain = make_domain(
            "エリア店番", "半角数字",
            column_def_type="varchar2", min_char="4", max_char="5",
        )
        assert _compare_value(screen.max_digits, domain.max_char) is True

    def test_桁数不一致(self):
        """画面 最大桁=10 ↔ ドメイン 最大文字数=5 → 不一致"""
        screen = make_screen_item("テスト項目", text_type="半角英数字", max_digits="10")
        domain = make_domain("テストドメイン", "半角数字", max_char="5")
        assert _compare_value(screen.max_digits, domain.max_char) is False

    def test_ボタンは全属性空_対象外(self):
        """ボタン項目（回収新規等）はテキストタイプなし → ドメイン不要"""
        screen = make_screen_item("回収新規", data_type="ボタン")
        assert not screen.text_type
        assert screen.max_digits is None
        assert screen.max_bytes is None
        assert not screen.code_id


# ============================================================
# 9. 顧客番号: 同名ドメイン・桁数違い
#    テーブルとドメインの両方に同名で桁数が異なるレコードが存在
# ============================================================

class TestSameNameDifferentDigits:
    """
    sample_domain.xlsx: 顧客番号 CHAR(8) と 顧客番号 CHAR(10) が共存
    sample_table.xlsx:  顧客番号 char(8) と 顧客番号 char(10) が共存
    → 桁数で正しいドメインを選択できることを検証
    """

    def test_顧客番号_8桁のテーブルは8桁のドメインに一致(self):
        table = make_table_item("顧客番号", "char", length="8")
        domain_8 = make_domain("顧客番号", "半角数字", column_def_type="char", max_char="8")
        assert _compare_value(table.length, domain_8.max_char) is True

    def test_顧客番号_8桁のテーブルは10桁のドメインに不一致(self):
        table = make_table_item("顧客番号", "char", length="8")
        domain_10 = make_domain("顧客番号", "半角数字", column_def_type="char", max_char="10")
        assert _compare_value(table.length, domain_10.max_char) is False

    def test_顧客番号_10桁のテーブルは10桁のドメインに一致(self):
        table = make_table_item("顧客番号", "char", length="10")
        domain_10 = make_domain("顧客番号", "半角数字", column_def_type="char", max_char="10")
        assert _compare_value(table.length, domain_10.max_char) is True

    def test_支店番号_テーブル6桁vsドメイン5桁_不一致(self):
        """sample_table: 支店番号 char(6) / sample_domain: 支店番号 CHAR(5)"""
        table = make_table_item("支店番号", "char", length="6")
        domain = make_domain("支店番号", "半角数字", column_def_type="char", max_char="5")
        assert _compare_value(table.length, domain.max_char) is False  # 6 ≠ 5


# ============================================================
# 10. _compute_detail_matches 統合テスト
#     domain_matcher.py の桁数照合ロジック
# ============================================================

class TestComputeDetailMatches:
    """
    _compute_detail_matches はドメインとの詳細照合を行う。
    大分類フィルタ通過後に呼ばれ、桁数の一致/不一致を判定する。
    """

    def test_テーブル文字列_長さ一致(self):
        """テーブルの文字列型: length ↔ max_char or max_byte"""
        item = {"source": "table", "length": "12", "max_chars": "12"}
        domain = make_domain("案件番号", "半角英数字", max_char="12", max_byte="12")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_length_match"] is True

    def test_テーブル文字列_長さ不一致(self):
        """テーブルの文字列型: 長さが異なる"""
        item = {"source": "table", "length": "20", "max_chars": "20"}
        domain = make_domain("テスト", "半角英数字", max_char="22", max_byte="22")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_length_match"] is False

    def test_テーブル数値_整数桁一致(self):
        """テーブルの数値型: integer_digits 一致"""
        item = {"source": "table", "integer_digits": "3", "decimal_digits": "0"}
        domain = make_domain("案件枝番", "数値（整数）", integer_digits="3")
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_integer_digits_match"] is True

    def test_テーブル数値_整数桁不一致(self):
        """テーブルの数値型: integer_digits 不一致"""
        item = {"source": "table", "integer_digits": "10", "decimal_digits": "0"}
        domain = make_domain("案件枝番", "数値（整数）", integer_digits="3")
        details = _compute_detail_matches(item, domain, "数値系")
        assert details["numeric_integer_digits_match"] is False

    def test_画面文字列_最大文字数一致(self):
        """画面項目の文字列型: max_chars ↔ max_char"""
        item = {"source": "screen", "max_chars": "5"}
        domain = make_domain("エリア店番", "半角数字", max_char="5")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is True

    def test_画面文字列_最大文字数不一致(self):
        """画面項目の文字列型: max_chars 不一致"""
        item = {"source": "screen", "max_chars": "10"}
        domain = make_domain("テスト", "半角数字", max_char="5")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["string_max_chars_match"] is False

    def test_外部コード一致(self):
        """外部コードの照合（全分類共通）"""
        item = {"source": "table", "external_code": "cv_code00006"}
        domain = make_domain("Agentコード", "コード", code_id="cv_code00006")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is True

    def test_外部コード不一致(self):
        """外部コードが異なる"""
        item = {"source": "table", "external_code": "cv_code00001"}
        domain = make_domain("Agentコード", "コード", code_id="cv_code00006")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is False

    def test_外部コードなし_比較不能(self):
        """外部コードが空 → None（比較不能）"""
        item = {"source": "table", "external_code": ""}
        domain = make_domain("テスト", "半角数字", code_id="")
        details = _compute_detail_matches(item, domain, "文字列系")
        assert details["external_code_match"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
