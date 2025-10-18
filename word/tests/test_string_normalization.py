#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文字列正規化・類似度関数の単体テスト"""

import unittest
import sys
from pathlib import Path

# wordモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from word.utils import zenkaku_hankaku_norm, local_similarity, normalize_term_no


class TestZenkakuHankakuNorm(unittest.TestCase):
    """zenkaku_hankaku_norm関数のテスト"""

    def test_none_input(self):
        """None入力の場合は空文字を返す"""
        self.assertEqual(zenkaku_hankaku_norm(None), "")

    def test_empty_string(self):
        """空文字入力の場合は空文字を返す"""
        self.assertEqual(zenkaku_hankaku_norm(""), "")

    def test_nfkc_normalization(self):
        """NFKC正規化が適用される"""
        # 全角英数→半角英数
        self.assertEqual(zenkaku_hankaku_norm("ＡＢＣ１２３"), "abc123")

    def test_lowercase_conversion(self):
        """小文字化が適用される"""
        self.assertEqual(zenkaku_hankaku_norm("ABC"), "abc")
        self.assertEqual(zenkaku_hankaku_norm("AbCdEf"), "abcdef")

    def test_whitespace_normalization(self):
        """全角/半角スペースが単一スペースに統一される"""
        self.assertEqual(zenkaku_hankaku_norm("顧客　コード"), "顧客 コード")
        self.assertEqual(zenkaku_hankaku_norm("顧客  コード"), "顧客 コード")

    def test_symbol_normalization(self):
        """区切り記号がスペースに置き換えられる"""
        self.assertEqual(zenkaku_hankaku_norm("顧客-コード"), "顧客 コード")
        self.assertEqual(zenkaku_hankaku_norm("顧客/コード"), "顧客 コード")
        self.assertEqual(zenkaku_hankaku_norm("顧客・コード"), "顧客 コード")

    def test_strip_whitespace(self):
        """前後の空白が削除される"""
        self.assertEqual(zenkaku_hankaku_norm("  顧客コード  "), "顧客コード")

    def test_complex_case(self):
        """複雑なケース"""
        input_str = "　顧客ＩＤ・コード(１２３)　"
        # 括弧がスペースに変換されるため、末尾にスペースが残る
        expected = "顧客id コード 123 "
        self.assertEqual(zenkaku_hankaku_norm(input_str), expected)


class TestLocalSimilarity(unittest.TestCase):
    """local_similarity関数のテスト"""

    def test_exact_match(self):
        """完全一致は1.0を返す"""
        self.assertEqual(local_similarity("顧客コード", "顧客コード"), 1.0)

    def test_normalized_similarity(self):
        """正規化後の類似度をチェック"""
        # 元の文字列が異なる場合、正規化後も異なる可能性がある
        score1 = local_similarity("顧客コード", "顧客　コード")
        # ある程度の類似度があることを確認
        self.assertGreater(score1, 0.8)

        score2 = local_similarity("顧客-コード", "顧客/コード")
        # 記号が正規化されるため、高い類似度になる
        self.assertEqual(score2, 1.0)

    def test_partial_match_substring(self):
        """片方がもう片方を含む場合は0.9を返す"""
        self.assertEqual(local_similarity("顧客", "顧客コード"), 0.9)
        self.assertEqual(local_similarity("顧客コード", "顧客"), 0.9)

    def test_empty_strings(self):
        """空文字の場合は0.0を返す"""
        self.assertEqual(local_similarity("", ""), 0.0)
        self.assertEqual(local_similarity("顧客", ""), 0.0)

    def test_none_input(self):
        """None入力の場合は0.0を返す"""
        self.assertEqual(local_similarity(None, "顧客"), 0.0)
        self.assertEqual(local_similarity("顧客", None), 0.0)

    def test_similar_strings(self):
        """類似文字列はdifflibによるスコアを返す"""
        score = local_similarity("顧客番号", "顧客コード")
        self.assertGreater(score, 0.0)
        self.assertLess(score, 0.9)


class TestNormalizeTermNo(unittest.TestCase):
    """normalize_term_no関数のテスト"""

    def test_integer_input(self):
        """整数入力はそのまま返す"""
        self.assertEqual(normalize_term_no(123), 123)

    def test_float_input(self):
        """浮動小数点数は整数に変換される"""
        self.assertEqual(normalize_term_no(123.0), 123)
        self.assertEqual(normalize_term_no(123.9), 123)

    def test_string_integer(self):
        """数字文字列は整数に変換される"""
        self.assertEqual(normalize_term_no("123"), 123)
        self.assertEqual(normalize_term_no("  123  "), 123)

    def test_string_float(self):
        """浮動小数点数文字列は整数に変換される"""
        self.assertEqual(normalize_term_no("123.0"), 123)

    def test_none_input(self):
        """None入力の場合はNoneを返す"""
        self.assertIsNone(normalize_term_no(None))

    def test_invalid_string(self):
        """無効な文字列の場合はNoneを返す"""
        self.assertIsNone(normalize_term_no("abc"))
        self.assertIsNone(normalize_term_no(""))

    def test_whitespace_string(self):
        """空白のみの文字列はNoneを返す"""
        self.assertIsNone(normalize_term_no("   "))


if __name__ == "__main__":
    unittest.main()
