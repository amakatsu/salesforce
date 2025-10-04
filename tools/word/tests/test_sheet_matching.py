#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シート名の部分一致テスト
_pick_matching_sheets関数の動作を包括的にテスト
"""

import unicodedata
from typing import List


class MockExcelFile:
    """テスト用のExcelFileモック"""
    def __init__(self, sheet_names: List[str]):
        self.sheet_names = sheet_names


def _pick_matching_sheets(xls: MockExcelFile, preferred: str) -> List[str]:
    """設定シート名にマッチする全てのシートを返す。複数パターン・曖昧マッチング対応。"""
    if not preferred:
        return [xls.sheet_names[0]]

    norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()

    # 複数パターンをカンマ区切りで分割
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]

    all_matches = []

    for pattern in patterns:
        want = norm(pattern)
        exact_matches = []
        fuzzy_matches = []
        partial_matches = []

        for name in xls.sheet_names:
            norm_name = norm(name)

            # 1. 完全一致
            if norm_name == want:
                exact_matches.append(name)
            # 2. 部分包含（双方向）
            elif want in norm_name or norm_name in want:
                partial_matches.append(name)
            # 3. 曖昧マッチ（文字の75%以上が共通）
            else:
                # 簡易的な類似度計算
                common_chars = len(set(want) & set(norm_name))
                similarity = common_chars / max(len(want), len(norm_name)) if max(len(want), len(norm_name)) > 0 else 0
                if similarity >= 0.75:  # 75%以上の類似度
                    fuzzy_matches.append(name)

        # 優先順位: 完全一致 > 部分一致 > 曖昧一致
        if exact_matches:
            all_matches.extend(exact_matches)
        elif partial_matches:
            all_matches.extend(partial_matches)
        elif fuzzy_matches:
            all_matches.extend(fuzzy_matches)

    # 重複を除去して順序を保持
    result = []
    seen = set()
    for sheet in all_matches:
        if sheet not in seen:
            result.append(sheet)
            seen.add(sheet)

    # マッチするものがなければ先頭シート
    return result if result else [xls.sheet_names[0]]


class SheetMatchingTestSuite:
    """シート名マッチングのテストスイート"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_all_tests(self):
        """全てのシート名マッチングテストを実行"""
        print("=" * 80)
        print("シート名部分一致テスト")
        print("=" * 80)

        # 1. 基本的なマッチングテスト
        self.test_basic_matching()

        # 2. 複数シートマッチング
        self.test_multiple_sheet_matching()

        # 3. 複数パターン指定
        self.test_multiple_pattern_matching()

        # 4. 曖昧マッチング
        self.test_fuzzy_matching()

        # 5. エッジケース
        self.test_edge_cases()

        # 6. 実際のシナリオ
        self.test_realistic_scenarios()

        # 7. 注意すべきケース
        self.test_warning_cases()

        # 結果サマリー
        self.print_summary()

    def test_basic_matching(self):
        """基本的なマッチングテスト"""
        print("\n1. 基本的なマッチングテスト:")

        test_cases = [
            # (シート名リスト, パターン, 期待される結果, 説明)
            (["画面項目定義", "単語帳", "その他"], "画面項目定義", ["画面項目定義"], "完全一致"),
            (["画面項目定義1", "画面項目定義2", "他"], "画面項目定義", ["画面項目定義1", "画面項目定義2"], "部分一致複数"),
            (["項目定義", "画面定義", "他"], "画面項目定義", ["項目定義", "画面定義"], "部分一致"),
            (["Sheet1", "Sheet2"], "画面項目定義", ["Sheet1"], "一致なし→先頭"),
            (["画面項目定義書", "画面項目定義"], "画面項目定義", ["画面項目定義"], "完全一致優先"),
        ]

        for sheets, pattern, expected, description in test_cases:
            result = self._run_test(sheets, pattern, expected, description)
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {description}")
            if not result["passed"]:
                print(f"      期待: {expected}, 実際: {result['actual']}")
                self.failed += 1
            else:
                self.passed += 1

    def test_multiple_sheet_matching(self):
        """複数シートマッチングテスト"""
        print("\n2. 複数シートマッチングテスト:")

        test_cases = [
            (["画面1", "画面2", "画面3", "他"], "画面", ["画面1", "画面2", "画面3"], "3シート一致"),
            (["定義A", "定義B", "定義C", "定義D"], "定義", ["定義A", "定義B", "定義C", "定義D"], "4シート一致"),
            (["項目定義書v1", "項目定義書v2", "他"], "項目定義", ["項目定義書v1", "項目定義書v2"], "バージョン番号付き"),
            (["画面定義_本番", "画面定義_開発", "画面定義_検証"], "画面定義", ["画面定義_本番", "画面定義_開発", "画面定義_検証"], "環境別"),
        ]

        for sheets, pattern, expected, description in test_cases:
            result = self._run_test(sheets, pattern, expected, description)
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {description}: {len(result['actual'])}シート検出")
            if not result["passed"]:
                print(f"      期待: {expected}")
                print(f"      実際: {result['actual']}")
                self.failed += 1
            else:
                self.passed += 1

    def test_multiple_pattern_matching(self):
        """複数パターン指定テスト"""
        print("\n3. 複数パターン指定テスト:")

        test_cases = [
            (["画面定義", "システム設計", "IF定義", "他"], "画面定義,システム設計", ["画面定義", "システム設計"], "2パターン"),
            (["定義A", "設計A", "仕様A", "他"], "定義,設計,仕様", ["定義A", "設計A", "仕様A"], "3パターン"),
            (["画面項目", "システム", "データ"], "画面項目定義,システム,マスタ", ["画面項目", "システム"], "一部パターンマッチ"),
        ]

        for sheets, pattern, expected, description in test_cases:
            result = self._run_test(sheets, pattern, expected, description)
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {description}")
            if not result["passed"]:
                print(f"      期待: {expected}, 実際: {result['actual']}")
                self.failed += 1
            else:
                self.passed += 1

    def test_fuzzy_matching(self):
        """曖昧マッチングテスト"""
        print("\n4. 曖昧マッチングテスト:")

        test_cases = [
            (["画面項目詳細", "他"], "画面項目定義", ["画面項目詳細"], "類似シート名"),
            (["項目定義一覧", "他"], "項目定義", ["項目定義一覧"], "接尾語付き"),
            (["システム画面定義", "他"], "画面定義", ["システム画面定義"], "接頭語付き"),
        ]

        for sheets, pattern, expected, description in test_cases:
            result = self._run_test(sheets, pattern, expected, description)
            status = "✅" if result["passed"] else "⚠️"
            print(f"   {status} {description}")
            if not result["passed"]:
                print(f"      期待: {expected}, 実際: {result['actual']}")
                if status == "⚠️":
                    self.warnings += 1
                else:
                    self.failed += 1
            else:
                self.passed += 1

    def test_edge_cases(self):
        """エッジケーステスト"""
        print("\n5. エッジケーステスト:")

        test_cases = [
            (["Sheet1"], "", ["Sheet1"], "パターンなし"),
            (["画面項目定義"], None, ["画面項目定義"], "パターンNone"),
            (["A", "B", "C"], "画面項目定義", ["A"], "全く一致しない→先頭"),
            (["画面項目定義", "画面項目定義　", "画面項目定義 "], "画面項目定義", ["画面項目定義", "画面項目定義　", "画面項目定義 "], "スペース違い"),
            (["画面項目定義", "画面項目定義"], "画面項目定義", ["画面項目定義"], "同名シート重複"),
        ]

        for sheets, pattern, expected, description in test_cases:
            result = self._run_test(sheets, pattern, expected, description)
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {description}")
            if not result["passed"]:
                print(f"      期待: {expected}, 実際: {result['actual']}")
                self.failed += 1
            else:
                self.passed += 1

    def test_realistic_scenarios(self):
        """実際のシナリオテスト"""
        print("\n6. 実際のシナリオテスト:")

        scenarios = [
            {
                "sheets": ["画面項目定義_顧客", "画面項目定義_商品", "画面項目定義_注文", "単語帳", "設計書"],
                "pattern": "画面項目定義",
                "expected": ["画面項目定義_顧客", "画面項目定義_商品", "画面項目定義_注文"],
                "description": "機能別シート"
            },
            {
                "sheets": ["01_画面定義", "02_項目定義", "03_データ定義", "99_その他"],
                "pattern": "定義",
                "expected": ["01_画面定義", "02_項目定義", "03_データ定義"],
                "description": "番号付きシート"
            },
            {
                "sheets": ["システムA画面", "システムB画面", "システムC画面", "マスタ"],
                "pattern": "画面",
                "expected": ["システムA画面", "システムB画面", "システムC画面"],
                "description": "システム別画面"
            },
            {
                "sheets": ["画面項目定義(最新)", "画面項目定義(旧)", "画面項目定義(バックアップ)", "単語帳"],
                "pattern": "画面項目定義",
                "expected": ["画面項目定義(最新)", "画面項目定義(旧)", "画面項目定義(バックアップ)"],
                "description": "バージョン管理"
            },
        ]

        for scenario in scenarios:
            result = self._run_test(
                scenario["sheets"],
                scenario["pattern"],
                scenario["expected"],
                scenario["description"]
            )
            status = "✅" if result["passed"] else "❌"
            print(f"   {status} {scenario['description']}: {len(result['actual'])}シート検出")
            if not result["passed"]:
                print(f"      期待: {scenario['expected']}")
                print(f"      実際: {result['actual']}")
                self.failed += 1
            else:
                self.passed += 1

    def test_warning_cases(self):
        """⚠️ 注意すべきケース - 結果を流用する際の注意点"""
        print("\n7. ⚠️ 注意すべきケース（結果流用時の注意）:")
        print("   ※ 以下のケースでは、部分一致・一致なしの列をそのまま流用すると問題が発生する可能性があります")

        warning_cases = [
            {
                "sheets": ["画面項目定義", "画面項目定義_完全一致", "画面項目定義_部分一致"],
                "pattern": "画面項目定義",
                "expected": ["画面項目定義", "画面項目定義_完全一致", "画面項目定義_部分一致"],
                "description": "「部分一致」という文字列を含むシート名",
                "warning": "シート名に「部分一致」が含まれる場合、列の判定結果と混同する可能性"
            },
            {
                "sheets": ["定義_一致なし確認用", "定義_正常", "定義_テスト"],
                "pattern": "定義",
                "expected": ["定義_一致なし確認用", "定義_正常", "定義_テスト"],
                "description": "「一致なし」という文字列を含むシート名",
                "warning": "シート名に「一致なし」が含まれる場合、列の判定結果と混同する可能性"
            },
            {
                "sheets": ["完全一致テスト", "部分一致テスト", "一致なしテスト"],
                "pattern": "テスト",
                "expected": ["完全一致テスト", "部分一致テスト", "一致なしテスト"],
                "description": "判定結果のキーワードを含む複数シート",
                "warning": "複数の判定結果キーワードがシート名に含まれ、データ統合時に誤判定の原因となる"
            },
            {
                "sheets": ["マスタ_完全一致_v1", "マスタ_完全一致_v2", "マスタ_部分一致_v1"],
                "pattern": "マスタ",
                "expected": ["マスタ_完全一致_v1", "マスタ_完全一致_v2", "マスタ_部分一致_v1"],
                "description": "判定結果を含む複数バージョン",
                "warning": "バージョン違いで判定キーワードが混在し、集計時にデータが混乱する"
            },
        ]

        for case in warning_cases:
            result = self._run_test(
                case["sheets"],
                case["pattern"],
                case["expected"],
                case["description"]
            )
            status = "⚠️" if result["passed"] else "❌"
            print(f"\n   {status} {case['description']}")
            print(f"      検出: {result['actual']}")
            print(f"      ⚠️  注意: {case['warning']}")

            if result["passed"]:
                self.warnings += 1
            else:
                self.failed += 1

    def _run_test(self, sheets: List[str], pattern: str, expected: List[str], description: str) -> dict:
        """個別テストを実行"""
        mock_xls = MockExcelFile(sheets)
        actual = _pick_matching_sheets(mock_xls, pattern)

        passed = sorted(actual) == sorted(expected)

        return {
            "passed": passed,
            "actual": actual,
            "expected": expected,
            "description": description
        }

    def print_summary(self):
        """テスト結果のサマリーを出力"""
        print("\n" + "=" * 80)
        print("テスト結果サマリー")
        print("=" * 80)
        total = self.passed + self.failed + self.warnings
        print(f"合計: {total}件")
        print(f"✅ 成功: {self.passed}件")
        print(f"❌ 失敗: {self.failed}件")
        print(f"⚠️  警告: {self.warnings}件")

        if self.failed == 0:
            print("\n🎉 全テスト成功！")
        else:
            print("\n⚠️  一部のテストが失敗しました")

        if self.warnings > 0:
            print("\n" + "=" * 80)
            print("⚠️  重要な注意事項")
            print("=" * 80)
            print("シート名に「完全一致」「部分一致」「一致なし」などの判定結果キーワードが")
            print("含まれている場合、処理結果の列データと混同される可能性があります。")
            print()
            print("【対策】")
            print("1. シート名に判定結果のキーワードを使用しない")
            print("2. 処理時に __source_sheet 列でシート名を記録し、フィルタリングする")
            print("3. 結果を統合する際は、必ずシート名と判定結果を別々に確認する")
            print("4. テスト用シートは本番データと明確に区別する命名規則を使用する")


def create_test_excel_with_warnings():
    """⚠️ 注意が必要なExcelファイル例を生成"""
    print("\n" + "=" * 80)
    print("⚠️ 実際の業務での注意事項")
    print("=" * 80)
    print("""
以下のようなシート構成は避けるべきです：

❌ 悪い例：
├─ 画面項目定義_完全一致
├─ 画面項目定義_部分一致
├─ 画面項目定義_一致なし
└─ 単語帳

理由：処理結果の「完全一致」「部分一致」「一致なし」列と
      シート名が混同され、データ分析時に誤判定される

✅ 良い例：
├─ 画面項目定義_顧客
├─ 画面項目定義_商品
├─ 画面項目定義_注文
└─ 単語帳

または：
├─ 01_画面項目定義
├─ 02_システム項目定義
├─ 03_IF項目定義
└─ 単語帳

【推奨される命名規則】
- 機能・業務別: 画面項目定義_顧客、画面項目定義_商品
- 番号別: 01_画面定義、02_項目定義
- システム別: システムA_画面、システムB_画面
- 環境別: 画面定義_本番、画面定義_開発
- バージョン別: 画面定義_v1、画面定義_v2

【避けるべきキーワード】
- 完全一致、一致、マッチ
- 部分一致、部分マッチ
- 一致なし、不一致、ミスマッチ
- これらを含む類似語
    """)


if __name__ == "__main__":
    test_suite = SheetMatchingTestSuite()
    test_suite.run_all_tests()

    # 追加の注意事項
    create_test_excel_with_warnings()