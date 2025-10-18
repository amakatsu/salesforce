#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLMペイロード構築のテスト"""

import unittest
import sys
import json
from pathlib import Path

# wordモジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from word.llm.client import (
    build_candidate_payload,
    build_llm_payload,
)
from word.settings import DEFAULT_CONFIG
from word.matching.primitives.candidates import Candidate
from word.matching.primitives.component_matcher import ComponentMatchResult


class TestBuildCandidatePayload(unittest.TestCase):
    """build_candidate_payload関数のテスト"""

    def test_simple_candidates(self):
        """シンプルな候補リストの変換"""
        candidates = [
            Candidate(term="顧客", score=0.95),
            Candidate(term="コード", score=0.85)
        ]
        payload = build_candidate_payload(candidates, None, None)

        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["term"], "顧客")
        self.assertAlmostEqual(payload[0]["local_score"], 0.95, places=4)
        self.assertEqual(payload[0]["local_rank"], 1)
        self.assertEqual(payload[1]["local_rank"], 2)

    def test_with_term_metadata(self):
        """メタ情報を含む候補"""
        candidates = [Candidate(term="顧客", score=0.95)]
        term_metadata = {
            "顧客": {
                "_no": "123",
                "_phys": "customer",
                "_phys_abbr": "cust"
            }
        }
        payload = build_candidate_payload(candidates, None, term_metadata)

        self.assertEqual(payload[0]["term_no"], 123)
        # 略称が優先される
        self.assertEqual(payload[0]["physical_name"], "cust")
        self.assertEqual(payload[0]["physical_name_full"], "customer")

    def test_with_component_result(self):
        """コンポーネント分析結果を含む"""
        candidates = [
            Candidate(term="顧客", score=0.95),
            Candidate(term="コード", score=0.85)
        ]
        comp_result = ComponentMatchResult(
            matched_terms=["顧客"],
            matched_norms=["顧客"],
            unmatched_segments=[],
            coverage_ratio=1.0,
            unmatched_count=0,
            has_non_digit=True,
            digit_segments=[]
        )
        payload = build_candidate_payload(candidates, comp_result, None)

        # "顧客"はコンポーネントマッチしている
        self.assertTrue(payload[0]["from_component"])
        self.assertEqual(payload[0]["component_rank"], 1)
        # "コード"はコンポーネントマッチしていない
        self.assertFalse(payload[1]["from_component"])

    def test_empty_candidates(self):
        """空の候補リスト"""
        payload = build_candidate_payload([], None, None)
        self.assertEqual(len(payload), 0)


class TestBuildLLMPayload(unittest.TestCase):
    """build_llm_payload関数のテスト"""

    def test_basic_payload_structure(self):
        """基本的なペイロード構造"""
        candidates = [Candidate(term="顧客", score=0.95)]
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客コード", candidates, cfg)

        # 必須フィールドの存在確認
        self.assertIn("model", payload)
        self.assertIn("max_tokens", payload)
        self.assertIn("temperature", payload)
        self.assertIn("messages", payload)
        self.assertIn("response_format", payload)

        # メッセージの構造
        messages = payload["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")

    def test_with_component_result(self):
        """コンポーネント分析結果を含むペイロード"""
        candidates = [Candidate(term="顧客", score=0.95)]
        comp_result = ComponentMatchResult(
            matched_terms=["顧客"],
            matched_norms=["顧客"],
            unmatched_segments=["コード"],
            coverage_ratio=0.5,
            unmatched_count=3,
            has_non_digit=True,
            digit_segments=[]
        )
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客コード", candidates, cfg, component_result=comp_result)

        # ユーザーメッセージにcomponent_analysisが含まれている
        user_content = payload["messages"][1]["content"]
        self.assertIn("component_analysis", user_content)
        self.assertIn("expected_match_hint", user_content)

    def test_json_response_format(self):
        """JSON応答形式が指定されている"""
        candidates = []
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客", candidates, cfg)

        self.assertEqual(payload["response_format"]["type"], "json_object")

    def test_config_parameters(self):
        """設定パラメータが正しく反映される"""
        candidates = []
        cfg = DEFAULT_CONFIG.copy()
        cfg["MAX_TOKENS"] = 500
        cfg["TEMPERATURE"] = 0.1
        cfg["TOP_P"] = 0.9
        payload = build_llm_payload("顧客", candidates, cfg)

        self.assertEqual(payload["max_tokens"], 500)
        self.assertEqual(payload["temperature"], 0.1)
        self.assertEqual(payload["top_p"], 0.9)

    def test_component_full_hint(self):
        """完全一致ヒントの生成"""
        candidates = []
        comp_result = ComponentMatchResult(
            matched_terms=["顧客", "コード"],
            matched_norms=["顧客", "コード"],
            unmatched_segments=[],
            coverage_ratio=1.0,
            unmatched_count=0,
            has_non_digit=True,
            digit_segments=[]
        )
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客コード", candidates, cfg, component_result=comp_result)

        user_content = payload["messages"][1]["content"]
        self.assertIn("component_full", user_content)

    def test_component_partial_hint(self):
        """部分一致ヒントの生成"""
        candidates = []
        comp_result = ComponentMatchResult(
            matched_terms=["顧客"],
            matched_norms=["顧客"],
            unmatched_segments=["xxx"],
            coverage_ratio=0.5,
            unmatched_count=3,
            has_non_digit=True,
            digit_segments=[]
        )
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客xxxコード", candidates, cfg, component_result=comp_result)

        user_content = payload["messages"][1]["content"]
        self.assertIn("component_partial", user_content)

    def test_digits_only_hint(self):
        """数字のみヒントの生成"""
        candidates = []
        comp_result = ComponentMatchResult(
            matched_terms=[],
            matched_norms=[],
            unmatched_segments=[],
            coverage_ratio=1.0,
            unmatched_count=0,
            has_non_digit=False,
            digit_segments=["123"]
        )
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("123", candidates, cfg, component_result=comp_result)

        user_content = payload["messages"][1]["content"]
        # 数字のみの場合はコンポーネント分析結果に数字セグメントが含まれる
        self.assertIn("\"digit_segments\"", user_content)
        self.assertIn("\"123\"", user_content)


class TestPayloadJSONValidity(unittest.TestCase):
    """ペイロードのJSON有効性テスト"""

    def test_payload_is_json_serializable(self):
        """ペイロードがJSON変換可能"""
        candidates = [Candidate(term="顧客", score=0.95)]
        cfg = DEFAULT_CONFIG.copy()
        payload = build_llm_payload("顧客コード", candidates, cfg)

        # JSON変換できることを確認
        try:
            json_str = json.dumps(payload, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Payload is not JSON serializable: {e}")


if __name__ == "__main__":
    unittest.main()
