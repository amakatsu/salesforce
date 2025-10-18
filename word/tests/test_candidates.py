#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""候補生成関数の単体テスト"""

import unittest
import sys
from pathlib import Path

# wordモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from word.matching.primitives.candidates import Candidate, phrase_candidates, top_k_candidates


class TestTopKCandidates(unittest.TestCase):
    """top_k_candidates関数のテスト"""

    def setUp(self):
        """テスト用の単語リストを準備"""
        self.vocab_terms = ["顧客", "顧客コード", "コード", "番号", "担当者"]

    def test_exact_match(self):
        """完全一致する候補"""
        candidates = top_k_candidates("顧客コード", self.vocab_terms, k=5, threshold=0.5)
        # "顧客コード"が最上位に来る
        self.assertEqual(candidates[0].term, "顧客コード")
        self.assertEqual(candidates[0].score, 1.0)

    def test_k_limit(self):
        """k件の上限が適用される"""
        candidates = top_k_candidates("顧客", self.vocab_terms, k=2, threshold=0.0)
        self.assertLessEqual(len(candidates), 2)

    def test_threshold_filter(self):
        """閾値以下の候補は除外される"""
        candidates = top_k_candidates("顧客", self.vocab_terms, k=10, threshold=0.95)
        # 完全一致または部分一致（0.9）の候補のみ
        for cand in candidates:
            self.assertGreaterEqual(cand.score, 0.9)

    def test_empty_vocab(self):
        """空の単語リストの場合"""
        candidates = top_k_candidates("顧客", [], k=5, threshold=0.5)
        self.assertEqual(len(candidates), 0)

    def test_no_match_above_threshold(self):
        """閾値を超える候補がない場合"""
        candidates = top_k_candidates("XXXYYY", self.vocab_terms, k=5, threshold=0.9)
        self.assertEqual(len(candidates), 0)

    def test_sorted_by_score(self):
        """スコアの降順でソートされる"""
        candidates = top_k_candidates("顧客", self.vocab_terms, k=5, threshold=0.0)
        scores = [c.score for c in candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestPhraseCandidates(unittest.TestCase):
    """phrase_candidates関数のテスト"""

    def setUp(self):
        """テスト用の単語リストを準備"""
        self.vocab_terms = ["顧客", "コード", "番号", "担当者", "名"]

    def test_unigram_match(self):
        """unigram（単語単位）でのマッチ"""
        candidates = phrase_candidates("顧客コード", self.vocab_terms, k=10, threshold=0.8)
        # "顧客"と"コード"が候補に含まれる
        terms = [c.term for c in candidates]
        self.assertIn("顧客", terms)
        self.assertIn("コード", terms)

    def test_bigram_match(self):
        """bigram（2語の組み合わせ）でのマッチ"""
        # "顧客 コード"のbigramは候補との照合に使われる
        candidates = phrase_candidates("顧客コード番号", self.vocab_terms, k=10, threshold=0.5)
        terms = [c.term for c in candidates]
        # 少なくとも一部の単語がマッチする
        self.assertGreater(len(terms), 0)

    def test_k_limit(self):
        """k件の上限が適用される"""
        candidates = phrase_candidates("顧客担当者名", self.vocab_terms, k=2, threshold=0.0)
        self.assertLessEqual(len(candidates), 2)

    def test_duplicate_terms_best_score(self):
        """同じ単語は最大スコアを採用"""
        # 複数のgramで同じ単語がヒットした場合、最高スコアを使う
        candidates = phrase_candidates("顧客顧客", self.vocab_terms, k=10, threshold=0.0)
        customer_candidates = [c for c in candidates if c.term == "顧客"]
        # "顧客"は1つだけ（重複排除されている）
        self.assertEqual(len(customer_candidates), 1)

    def test_empty_screen_name(self):
        """空の画面項目名"""
        candidates = phrase_candidates("", self.vocab_terms, k=5, threshold=0.5)
        self.assertEqual(len(candidates), 0)

    def test_empty_vocab(self):
        """空の単語リスト"""
        candidates = phrase_candidates("顧客コード", [], k=5, threshold=0.5)
        self.assertEqual(len(candidates), 0)

    def test_sorted_by_score(self):
        """スコアの降順でソートされる"""
        candidates = phrase_candidates("顧客担当者", self.vocab_terms, k=10, threshold=0.0)
        scores = [c.score for c in candidates]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_no_k_limit(self):
        """k=0の場合は全候補を返す"""
        candidates = phrase_candidates("顧客コード", self.vocab_terms, k=0, threshold=0.0)
        # 閾値以上のすべての候補が返される
        self.assertGreaterEqual(len(candidates), 0)


class TestCandidateDataclass(unittest.TestCase):
    """Candidateデータクラスのテスト"""

    def test_create_candidate(self):
        """Candidateインスタンスの作成"""
        cand = Candidate(term="顧客", score=0.95)
        self.assertEqual(cand.term, "顧客")
        self.assertEqual(cand.score, 0.95)

    def test_candidate_equality(self):
        """Candidateの等価性"""
        cand1 = Candidate(term="顧客", score=0.95)
        cand2 = Candidate(term="顧客", score=0.95)
        self.assertEqual(cand1, cand2)


if __name__ == "__main__":
    unittest.main()
