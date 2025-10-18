#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ComponentMatcherクラスの単体テスト"""

import unittest
import sys
from pathlib import Path

# wordモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from word.matching.primitives.component_matcher import ComponentMatcher


class TestComponentMatcherInit(unittest.TestCase):
    """ComponentMatcherの初期化テスト"""

    def test_init_with_empty_dict(self):
        """空の辞書で初期化"""
        matcher = ComponentMatcher({})
        self.assertEqual(matcher.norm_to_term, {})
        self.assertEqual(matcher.prefix_map, {})

    def test_init_with_simple_dict(self):
        """シンプルな辞書で初期化"""
        norm_to_term = {"顧客": "顧客", "コード": "コード"}
        matcher = ComponentMatcher(norm_to_term)
        self.assertEqual(len(matcher.norm_to_term), 2)
        self.assertEqual(matcher.norm_to_term["顧客"], "顧客")
        self.assertEqual(matcher.norm_to_term["コード"], "コード")

    def test_init_removes_spaces(self):
        """初期化時にスペースが削除される"""
        norm_to_term = {"顧客 コード": "顧客 コード"}
        matcher = ComponentMatcher(norm_to_term)
        # スペースが削除されたキーで格納される
        self.assertIn("顧客コード", matcher.norm_to_term)

    def test_prefix_map_creation(self):
        """プレフィックスマップが正しく作成される"""
        norm_to_term = {"顧客": "顧客", "顧客番号": "顧客番号"}
        matcher = ComponentMatcher(norm_to_term)
        # "顧"で始まる語が登録されている
        self.assertIn("顧", matcher.prefix_map)
        # 長い順にソートされている（"顧客番号" > "顧客"）
        self.assertEqual(matcher.prefix_map["顧"][0], "顧客番号")
        self.assertEqual(matcher.prefix_map["顧"][1], "顧客")


class TestComponentMatcherAnalyze(unittest.TestCase):
    """ComponentMatcherのanalyzeメソッドテスト"""

    def setUp(self):
        """テスト用の辞書を準備"""
        self.norm_to_term = {
            "顧客": "顧客",
            "コード": "コード",
            "番号": "番号",
            "回収": "回収",
            "稟議番号": "稟議番号",
            "担当者": "担当者",
            "名": "名",
        }
        self.matcher = ComponentMatcher(self.norm_to_term)

    def test_empty_string(self):
        """空文字の解析"""
        result = self.matcher.analyze("")
        self.assertEqual(result.matched_terms, [])
        self.assertEqual(result.unmatched_segments, [])
        self.assertEqual(result.coverage_ratio, 1.0)

    def test_complete_match(self):
        """完全一致のケース"""
        result = self.matcher.analyze("顧客コード")
        self.assertIn("顧客", result.matched_terms)
        self.assertIn("コード", result.matched_terms)
        self.assertEqual(result.unmatched_segments, [])
        self.assertEqual(result.coverage_ratio, 1.0)

    def test_partial_match(self):
        """部分一致のケース"""
        result = self.matcher.analyze("顧客XXXコード")
        self.assertIn("顧客", result.matched_terms)
        self.assertIn("コード", result.matched_terms)
        # 正規化されて小文字になる
        self.assertIn("xxx", result.unmatched_segments)
        # カバー率は0より大きく1未満
        self.assertGreater(result.coverage_ratio, 0.0)
        self.assertLess(result.coverage_ratio, 1.0)

    def test_no_match(self):
        """一致なしのケース"""
        result = self.matcher.analyze("緊急度")
        self.assertEqual(result.matched_terms, [])
        # "緊急度"が未一致として記録される
        self.assertGreater(len(result.unmatched_segments), 0)
        self.assertEqual(result.coverage_ratio, 0.0)

    def test_digits_only(self):
        """数字のみのケース"""
        result = self.matcher.analyze("123")
        self.assertEqual(result.matched_terms, [])
        self.assertEqual(result.unmatched_segments, [])
        self.assertEqual(result.digit_segments, ["123"])
        # 数字のみの場合、has_non_digitはFalse
        self.assertFalse(result.has_non_digit)
        # 非数字文字が0個なので、カバー率は1.0
        self.assertEqual(result.coverage_ratio, 1.0)

    def test_mixed_with_digits(self):
        """数字を含むケース"""
        result = self.matcher.analyze("顧客コード1")
        self.assertIn("顧客", result.matched_terms)
        self.assertIn("コード", result.matched_terms)
        self.assertIn("1", result.digit_segments)
        self.assertTrue(result.has_non_digit)
        self.assertEqual(result.coverage_ratio, 1.0)

    def test_longest_match_priority(self):
        """最長一致が優先される"""
        # "稟議番号"は"稟議"+"番号"ではなく、"稟議番号"全体でマッチするべき
        result = self.matcher.analyze("回収稟議番号")
        self.assertIn("回収", result.matched_terms)
        self.assertIn("稟議番号", result.matched_terms)
        # "番号"単独ではマッチしない（"稟議番号"が優先される）
        # matched_termsに"番号"が単独で含まれていないことを確認
        term_count = result.matched_terms.count("番号")
        self.assertEqual(term_count, 0)

    def test_order_preservation(self):
        """マッチした語の順序が保持される"""
        result = self.matcher.analyze("顧客担当者名")
        # 左から順に: 顧客、担当者、名
        expected_order = ["顧客", "担当者", "名"]
        self.assertEqual(result.matched_terms, expected_order)

    def test_hyphen_in_number(self):
        """数字にハイフンが含まれるケース"""
        result = self.matcher.analyze("1-1")
        # 数字とハイフンが別々に認識される可能性がある
        # このケースは実装依存だが、少なくともエラーが出ないことを確認
        self.assertIsNotNone(result)


class TestComponentMatcherEdgeCases(unittest.TestCase):
    """エッジケースのテスト"""

    def test_duplicate_values_in_dict(self):
        """辞書に重複する値がある場合"""
        norm_to_term = {"こーど": "コード", "コード": "コード"}
        matcher = ComponentMatcher(norm_to_term)
        # 最初に登録されたものが優先される（setdefault使用）
        self.assertIn("こーど", matcher.norm_to_term)

    def test_whitespace_in_screen_name(self):
        """画面項目名にスペースが含まれる場合"""
        norm_to_term = {"顧客": "顧客", "コード": "コード"}
        matcher = ComponentMatcher(norm_to_term)
        # スペースは正規化で削除されるため、マッチする
        result = matcher.analyze("顧客 コード")
        self.assertIn("顧客", result.matched_terms)
        self.assertIn("コード", result.matched_terms)

    def test_very_long_screen_name(self):
        """非常に長い画面項目名"""
        norm_to_term = {"顧客": "顧客"}
        matcher = ComponentMatcher(norm_to_term)
        long_name = "顧客" * 100 + "ABC" * 100
        result = matcher.analyze(long_name)
        # エラーなく実行できることを確認
        self.assertIsNotNone(result)
        self.assertGreater(len(result.matched_terms), 0)


if __name__ == "__main__":
    unittest.main()
