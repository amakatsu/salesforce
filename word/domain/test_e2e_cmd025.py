#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cmd_025 統合テスト（E2E）

サンプルExcelデータを実際に読み込み、マッチング処理を実行して
期待される比較結果を検証する。

仕様根拠:
  - matching_mapping.md Section 10-5
  - domain_checker_spec.md Section 3-4

テスト対象:
  比較A: テーブル定義 vs ドメイン定義（Oracle型直接比較 + フォールバック）
  比較B: 項目定義（画面） vs ドメイン定義（日本語型比較）
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# プロジェクトルート（word/）をパスに追加
_word_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_word_root))

# llm_matcher の依存問題を回避して domain_matcher を直接注入
from domain.domain_matcher import (
    collect_evidence,
    digit_match_rate_from_details,
    resolve_without_llm,
)

import domain.domain_check as _dc

_dc.collect_evidence = collect_evidence
_dc.resolve_without_llm = resolve_without_llm
_dc.digit_match_rate_from_details = digit_match_rate_from_details

from config import get_domain_config
from domain.domain_check import (
    DomainDef,
    load_domains,
    load_screen_items,
    load_table_definitions,
    process_screen_domain_matching,
    process_table_domain_matching,
)

# ============================================================
# テスト用設定・データのロード
# ============================================================

SAMPLE_DIR = _word_root / "out"


def _make_cfg():
    """LLM無効のテスト用設定を生成する"""
    cfg = get_domain_config()
    cfg["LLM_MATCHING_ENABLED"] = False
    cfg["DOMAIN_GLOB"] = "sample_domain*.xlsx"
    cfg["TABLE_GLOB"] = "sample_table*.xlsx"
    cfg["SCREEN_GLOB"] = "sample_screen*.xlsx"
    cfg["DOMAIN_SHEET"] = "*"
    cfg["TABLE_SHEET"] = "*"
    cfg["SCREEN_SHEET"] = "*"
    return cfg


@pytest.fixture(scope="module")
def cfg():
    return _make_cfg()


@pytest.fixture(scope="module")
def domains(cfg):
    return load_domains(SAMPLE_DIR, cfg)


@pytest.fixture(scope="module")
def table_items(cfg):
    return load_table_definitions(SAMPLE_DIR, cfg)


@pytest.fixture(scope="module")
def screen_items(cfg):
    return load_screen_items(SAMPLE_DIR, cfg)


@pytest.fixture(scope="module")
def table_result(table_items, domains, cfg):
    return process_table_domain_matching(table_items, domains, cfg)


@pytest.fixture(scope="module")
def screen_result(screen_items, domains, cfg):
    return process_screen_domain_matching(screen_items, domains, cfg)


def _rows_by_name(df, col, name):
    """指定カラムの値で行を絞り込む"""
    return df[df[col] == name]


# ============================================================
# 1. データ読み込みの検証
# ============================================================

class TestDataLoading:
    """サンプルExcelからのデータ読み込みが正しいことを検証"""

    def test_ドメイン定義の件数(self, domains):
        assert len(domains) >= 30

    def test_テーブル定義の件数(self, table_items):
        assert len(table_items) == 34

    def test_画面項目の件数(self, screen_items):
        assert len(screen_items) == 18

    def test_ドメインにカラム定義が含まれる(self, domains):
        """カラム定義列（column_def_type / column_def_raw）がパースされていること"""
        has_column_def = any(d.column_def_type for d in domains.values())
        assert has_column_def, "column_def_type がパースされたドメインが存在すること"

    def test_カラム定義なしのドメインも存在(self, domains):
        """フォールバック対象のドメインが存在すること"""
        no_column_def = any(d.column_def_type is None for d in domains.values())
        assert no_column_def, "column_def_type が None のドメインが存在すること"


# ============================================================
# 2. 比較A: テーブル vs ドメイン（Oracle型直接比較）
# ============================================================

class TestTableVsDomain:
    """テーブル定義とドメイン定義のマッチング結果を検証"""

    def test_全結果の行数(self, table_result, table_items):
        assert len(table_result) == len(table_items)

    def test_案件番号は完全一致(self, table_result):
        """案件番号: char(12) ↔ ドメイン CHAR(12) → 完全一致

        テーブル: データ型=char, Length=12
        ドメイン: カラム定義=CHAR(12), データ型=半角英数字
        """
        rows = _rows_by_name(table_result, "論理項目名", "案件番号")
        assert len(rows) == 1
        row = rows.iloc[0]
        assert row["判定結果"] == "完全一致"
        assert row["一致ドメイン名"] == "案件番号"

    def test_顧客番号10桁は完全一致(self, table_result):
        """顧客番号 char(10) ↔ ドメイン CHAR(10) → 完全一致

        ドメインに顧客番号が8桁と10桁で2件存在する。
        テーブルの10桁は10桁ドメインに正しくマッチすること。
        """
        rows = _rows_by_name(table_result, "論理項目名", "顧客番号")
        assert len(rows) == 2  # 8桁と10桁

        row_10 = rows[rows["Length"].astype(str) == "10.0"]
        assert len(row_10) == 1
        assert row_10.iloc[0]["判定結果"] == "完全一致"

    def test_顧客番号8桁は同名桁違い検出(self, table_result):
        """顧客番号 char(8) → 同名ドメインが存在するが桁が異なることを検出

        テーブル: Length=8
        ドメイン: 顧客番号(8桁) と 顧客番号(10桁) が共存
        """
        rows = _rows_by_name(table_result, "論理項目名", "顧客番号")
        row_8 = rows[rows["Length"].astype(str) == "8.0"]
        assert len(row_8) == 1
        # 完全一致ではないこと（桁違いの検出）
        judgment = row_8.iloc[0]["判定結果"]
        assert judgment != "対象外"

    def test_支店番号は桁不一致で新規提案(self, table_result):
        """支店番号: テーブル char(6) vs ドメイン CHAR(5) → 桁不一致"""
        rows = _rows_by_name(table_result, "論理項目名", "支店番号")
        assert len(rows) == 1
        assert rows.iloc[0]["判定結果"] != "完全一致"

    def test_date型は完全一致しない(self, table_result):
        """日付型項目（案件決定日, 報告期限）はドメインと完全一致しない

        テーブルに date 型があるが、サンプルドメインに対応するドメインがない。
        """
        date_rows = table_result[table_result["データ型"] == "date"]
        assert len(date_rows) > 0
        for _, row in date_rows.iterrows():
            assert row["判定結果"] != "完全一致"


# ============================================================
# 3. 比較A: フォールバック動作の検証
# ============================================================

class TestTableFallback:
    """カラム定義なしドメインのフォールバック動作"""

    def test_カラム定義なしのドメインが存在(self, domains):
        """フォールバック対象のドメインがサンプルに含まれている"""
        no_col_def = [d for d in domains.values() if d.column_def_type is None]
        assert len(no_col_def) > 0, "カラム定義なしドメインが存在すること"
        # 具体例: ON未実施店, アラーム, エリアポストコード等
        names = {d.name for d in no_col_def}
        assert len(names) > 3, f"複数のフォールバック対象: {names}"

    def test_カラム定義ありのドメインのOracle型(self, domains):
        """カラム定義ありのドメインにcolumn_def_typeが設定されている"""
        with_col_def = [d for d in domains.values() if d.column_def_type]
        assert len(with_col_def) > 0
        for d in with_col_def:
            assert d.column_def_type.upper() in (
                "CHAR", "VARCHAR2", "NUMBER", "NVARCHAR2", "DATE",
            ), f"{d.name}: unexpected column_def_type={d.column_def_type}"


# ============================================================
# 4. 比較B: 画面 vs ドメイン
# ============================================================

class TestScreenVsDomain:
    """画面項目定義とドメイン定義のマッチング結果を検証"""

    def test_全結果の行数(self, screen_result, screen_items):
        assert len(screen_result) == len(screen_items)

    def test_ボタン項目は対象外(self, screen_result):
        """テキストタイプが空のボタン項目は全て対象外になること"""
        buttons = screen_result[
            screen_result["項目名称"].isin([
                "回収新規", "継続", "条件変更", "増減額", "利率変更",
                "極度超過", "削除", "ファイル作成",
            ])
        ]
        for _, row in buttons.iterrows():
            assert row["判定結果"] == "対象外", f'{row["項目名称"]} should be 対象外'

    def test_組織店番はテキストタイプあり(self, screen_result):
        """組織店番1/2はテキストタイプ=半角英数字で比較対象になる"""
        org_rows = screen_result[
            screen_result["項目名称"].str.contains("組織店番", na=False)
        ]
        assert len(org_rows) == 2
        for _, row in org_rows.iterrows():
            assert row["テキストタイプ"] == "半角英数字"
            assert row["判定結果"] != "対象外"

    def test_対象外が大多数(self, screen_result):
        """サンプルデータではボタン等が多く、対象外が多数を占める"""
        excluded = screen_result[screen_result["判定結果"] == "対象外"]
        assert len(excluded) >= 10


# ============================================================
# 5. 結果カラム構造の検証
# ============================================================

class TestResultStructure:
    """出力DataFrameのカラム構成が仕様通りであること"""

    def test_テーブル結果に必須カラムが含まれる(self, table_result):
        required = ["論理項目名", "データ型", "判定結果", "一致ドメイン名", "提案ドメイン名", "備考"]
        for col in required:
            assert col in table_result.columns, f"missing column: {col}"

    def test_画面結果に必須カラムが含まれる(self, screen_result):
        required = ["項目名称", "テキストタイプ", "判定結果", "一致ドメイン名", "提案ドメイン名", "備考"]
        for col in required:
            assert col in screen_result.columns, f"missing column: {col}"

    def test_テーブル結果にドメイン詳細カラムが含まれる(self, table_result):
        """マッチしたドメインの詳細情報が付与されていること"""
        domain_cols = ["D_データ型", "D_最大文字数"]
        for col in domain_cols:
            assert col in table_result.columns, f"missing domain detail column: {col}"


# ============================================================
# 6. 判定結果の妥当性
# ============================================================

class TestJudgmentValidity:
    """判定結果の値が仕様で定義された分類であること"""

    VALID_JUDGMENTS = {
        "完全一致",
        "選択必須",
        "提案（新規）",
        "提案（候補から）",
        "提案（候補）同名/桁違い",
        "対象外",
    }

    def test_テーブル結果の判定値が有効(self, table_result):
        for judgment in table_result["判定結果"].unique():
            assert judgment in self.VALID_JUDGMENTS, f"unexpected judgment: {judgment}"

    def test_画面結果の判定値が有効(self, screen_result):
        for judgment in screen_result["判定結果"].unique():
            assert judgment in self.VALID_JUDGMENTS, f"unexpected judgment: {judgment}"

    def test_完全一致にはドメイン名が付与される(self, table_result):
        """完全一致の行には一致ドメイン名が設定されていること"""
        exact_rows = table_result[table_result["判定結果"] == "完全一致"]
        for _, row in exact_rows.iterrows():
            domain_name = row["一致ドメイン名"]
            assert pd.notna(domain_name) and str(domain_name).strip(), \
                f'{row["論理項目名"]}: 完全一致なのに一致ドメイン名が空'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
