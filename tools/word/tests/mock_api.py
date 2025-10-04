#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語照合システム用のモックAPIクライアント
実際のLLM APIを呼び出さずにテスト用のレスポンスを返す
"""

import json
from typing import Any, Dict, List

try:
    from word import Candidate, simple_proposal
except ImportError:
    # 依存関係がない場合の代替実装
    class Candidate:
        def __init__(self, term: str, score: float):
            self.term = term
            self.score = score

    def simple_proposal(text: str) -> str:
        """ローワーキャメルの簡易物理名を生成（8〜10文字程度）。"""
        import re
        import unicodedata

        if text is None:
            return "newItem"

        # 正規化
        s = unicodedata.normalize("NFKC", str(text)).lower().strip()
        s = re.sub(r"[\u3000\s]+", " ", s)
        s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)
        s = re.sub(r"\s+", " ", s)

        tokens = [t for t in re.split(r"\s+", s) if t]
        if not tokens:
            return "newItem"

        # 冗長語の削ぎ落とし
        stop_words = {"コード", "番号", "名称名", "名称名称"}
        core = [w for w in tokens[:3] if w not in stop_words] or tokens[:2]

        # lowerCamelCase化
        name = core[0].lower() + "".join(w.capitalize() for w in core[1:])

        # 長さ制御
        return (name[:8] if len(name) > 10 else name) or "newItem"


class MockApiClient:
    """LLM API呼び出しをモックするクライアント"""

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.call_count = 0
        self.requests = []

    def post_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """モックレスポンスを返す"""
        self.call_count += 1

        # リクエストを記録
        self.requests.append(payload)

        # ユーザーメッセージから画面項目名を抽出
        user_content = payload.get("messages", [{}])[-1].get("content", "")
        screen_name = self._extract_screen_name(user_content)

        # 候補から自動判定
        candidates_json = self._extract_candidates(user_content)

        # シンプルな判定ロジック
        if not candidates_json:
            return self._create_no_match_response(screen_name)

        top_candidate = candidates_json[0]
        score = top_candidate.get("local_score", 0.0)
        term = top_candidate.get("term", "")

        # 複合語判定
        if len(candidates_json) > 1:
            high_score_candidates = [c for c in candidates_json if c.get("local_score", 0) >= 0.8]
            if len(high_score_candidates) >= 2:
                return self._create_compound_match_response(screen_name, high_score_candidates)

        # 単一語判定
        if score >= 0.95:
            return self._create_exact_match_response(screen_name, term)
        elif score >= 0.7:
            return self._create_partial_match_response(screen_name, term, score)
        else:
            return self._create_no_match_response(screen_name)

    def _extract_screen_name(self, content: str) -> str:
        """コンテンツから画面項目名を抽出"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '# 画面項目名' in line and i + 1 < len(lines):
                return lines[i + 1].strip()
        return "unknown_item"

    def _extract_candidates(self, content: str) -> List[Dict]:
        """コンテンツから候補を抽出"""
        try:
            # JSON部分を探して解析
            start_marker = "# 単語帳候補（上位スコア順）"
            if start_marker in content:
                json_start = content.find('[', content.find(start_marker))
                if json_start > -1:
                    # JSONの終わりを探す
                    bracket_count = 0
                    json_end = json_start
                    for i, char in enumerate(content[json_start:], json_start):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                json_end = i + 1
                                break

                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
        except Exception:
            pass
        return []

    def _create_exact_match_response(self, screen_name: str, term: str) -> Dict[str, Any]:
        """完全一致レスポンス"""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "完全一致",
                        "matched_term": term,
                        "matched_terms": None,
                        "reason": f"モックAPI: '{screen_name}'と'{term}'は意味・表記ともに一致します。",
                        "proposed_name": self._generate_physical_name(term),
                        "coverage_ratio": 1.0
                    }, ensure_ascii=False)
                }
            }]
        }

    def _create_partial_match_response(self, screen_name: str, term: str, score: float) -> Dict[str, Any]:
        """部分一致レスポンス"""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "一部一致",
                        "matched_term": term,
                        "matched_terms": None,
                        "reason": f"モックAPI: '{screen_name}'と'{term}'は部分的に一致します（類似度: {score:.2f}）。",
                        "proposed_name": self._generate_physical_name(term),
                        "coverage_ratio": score
                    }, ensure_ascii=False)
                }
            }]
        }

    def _create_compound_match_response(self, screen_name: str, candidates: List[Dict]) -> Dict[str, Any]:
        """複合語一致レスポンス"""
        terms = [c.get("term", "") for c in candidates[:3]]
        avg_score = sum(c.get("local_score", 0) for c in candidates[:3]) / len(candidates[:3])

        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "一部一致",
                        "matched_term": None,
                        "matched_terms": terms,
                        "reason": f"モックAPI: '{screen_name}'は複合語として「{', '.join(terms)}」の組み合わせと一致します。",
                        "proposed_name": self._generate_compound_physical_name(terms),
                        "coverage_ratio": avg_score
                    }, ensure_ascii=False)
                }
            }]
        }

    def _create_no_match_response(self, screen_name: str) -> Dict[str, Any]:
        """一致なしレスポンス"""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "一致なし",
                        "matched_term": None,
                        "matched_terms": None,
                        "reason": f"モックAPI: '{screen_name}'に適合する単語が単語帳に見つかりません。新規単語として追加を検討してください。",
                        "proposed_name": simple_proposal(screen_name),
                        "coverage_ratio": None
                    }, ensure_ascii=False)
                }
            }]
        }

    def _generate_physical_name(self, term: str) -> str:
        """物理名を生成"""
        # 簡易的な日本語→英語変換（テスト用）
        translations = {
            "顧客": "customer",
            "コード": "code",
            "名称": "name",
            "名前": "name",
            "番号": "number",
            "融資": "loan",
            "管理": "management",
            "商品": "product",
            "分類": "category",
            "削除": "delete",
            "フラグ": "flag",
            "日付": "date",
            "金額": "amount",
            "数量": "quantity"
        }

        # 複数の単語に分割して変換
        words = []
        for jp_word, en_word in translations.items():
            if jp_word in term:
                words.append(en_word)

        if words:
            # lowerCamelCase形式
            return words[0].lower() + "".join(w.capitalize() for w in words[1:])
        else:
            return simple_proposal(term)

    def _generate_compound_physical_name(self, terms: List[str]) -> str:
        """複合語の物理名を生成"""
        physical_parts = [self._generate_physical_name(term) for term in terms]
        # 最初の部分は小文字、残りは大文字開始
        if physical_parts:
            return physical_parts[0] + "".join(p.capitalize() for p in physical_parts[1:])
        return "compoundWord"

    def get_call_statistics(self) -> Dict[str, Any]:
        """呼び出し統計を取得"""
        return {
            "total_calls": self.call_count,
            "requests": self.requests
        }


def mock_llm_response(screen_name: str, candidates: List[Candidate]) -> Dict[str, Any]:
    """word.py内で使用されるシンプルなモック関数"""
    if not candidates:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": f"テストモード: '{screen_name}'に対する候補が見つかりません。",
            "proposed_name": simple_proposal(screen_name),
            "coverage_ratio": None
        }

    top = candidates[0]

    # 簡単なルールベース判定
    if top.score >= 0.95:
        return {
            "match_type": "完全一致",
            "matched_term": top.term,
            "matched_terms": None,
            "reason": f"テストモード: '{screen_name}'と'{top.term}'は完全一致です（スコア: {top.score:.2f}）。",
            "proposed_name": simple_proposal(top.term),
            "coverage_ratio": 1.0
        }
    elif top.score >= 0.7:
        # 複合語の可能性をチェック
        if len(candidates) > 1 and any(c.score >= 0.8 for c in candidates[1:3]):
            matched_terms = [c.term for c in candidates[:3] if c.score >= 0.8]
            return {
                "match_type": "一部一致",
                "matched_term": None,
                "matched_terms": matched_terms,
                "reason": f"テストモード: '{screen_name}'は複合語として「{', '.join(matched_terms)}」と一致します。",
                "proposed_name": "".join([simple_proposal(t) for t in matched_terms[:2]]),
                "coverage_ratio": sum(c.score for c in candidates[:len(matched_terms)]) / len(matched_terms)
            }
        else:
            return {
                "match_type": "一部一致",
                "matched_term": top.term,
                "matched_terms": None,
                "reason": f"テストモード: '{screen_name}'と'{top.term}'は部分一致です（スコア: {top.score:.2f}）。",
                "proposed_name": simple_proposal(top.term),
                "coverage_ratio": top.score
            }
    else:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": f"テストモード: '{screen_name}'に適合する単語が見つかりません（最高スコア: {top.score:.2f}）。",
            "proposed_name": simple_proposal(screen_name),
            "coverage_ratio": None
        }