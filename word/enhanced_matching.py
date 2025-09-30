#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部分一致機能の改善提案
テストで発見された問題を解決する拡張機能
"""

import unicodedata
import re
import difflib
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class EnhancedCandidate:
    """拡張候補クラス"""
    term: str
    score: float
    match_type: str  # "exact", "partial", "compound", "fuzzy", "abbreviation"
    components: List[str] = None  # 複合語の構成要素


class EnhancedMatcher:
    """拡張マッチングエンジン"""

    def __init__(self):
        # 略語辞書
        self.abbreviation_dict = {
            "cd": "コード",
            "code": "コード",
            "nm": "名称",
            "name": "名称",
            "id": "番号",
            "no": "番号",
            "num": "番号",
            "flg": "フラグ",
            "flag": "フラグ",
            "dt": "日付",
            "date": "日付",
            "amt": "金額",
            "amount": "金額",
            "qty": "数量",
            "quantity": "数量",
            "sys": "システム",
            "system": "システム",
            "mgmt": "管理",
            "management": "管理",
            "info": "情報",
            "information": "情報",
        }

        # 表記ゆれ辞書
        self.variation_dict = {
            "クライアント": "顧客",
            "カスタマー": "顧客",
            "ユーザー": "顧客",
            "プロダクト": "商品",
            "アイテム": "商品",
            "オーダー": "注文",
            "リクエスト": "注文",
            "デリート": "削除",
            "ステータス": "状態",
            "コンディション": "状態",
        }

        # 同義語グループ
        self.synonym_groups = [
            {"顧客", "クライアント", "カスタマー", "ユーザー"},
            {"商品", "プロダクト", "アイテム", "製品"},
            {"注文", "オーダー", "リクエスト", "依頼"},
            {"削除", "デリート", "消去", "除去"},
            {"状態", "ステータス", "コンディション"},
            {"管理", "マネジメント", "制御", "統制"},
            {"システム", "シス", "sys"},
        ]

    def enhanced_normalize(self, text: str) -> str:
        """拡張正規化：略語展開も含む"""
        if not text:
            return ""

        # 基本正規化
        s = unicodedata.normalize("NFKC", str(text)).lower().strip()
        s = re.sub(r"[\u3000\s]+", " ", s)
        s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)
        s = re.sub(r"\s+", " ", s)

        # 略語展開
        tokens = s.split()
        expanded_tokens = []
        for token in tokens:
            if token in self.abbreviation_dict:
                expanded_tokens.append(self.abbreviation_dict[token])
            else:
                expanded_tokens.append(token)

        return " ".join(expanded_tokens)

    def find_enhanced_candidates(self, screen_name: str, vocab_terms: List[str],
                                threshold: float = 0.6) -> List[EnhancedCandidate]:
        """拡張候補検索"""
        candidates = []

        # 1. 完全一致
        exact_matches = self._find_exact_matches(screen_name, vocab_terms)
        candidates.extend(exact_matches)

        # 2. 部分一致（包含関係）
        partial_matches = self._find_partial_matches(screen_name, vocab_terms, threshold)
        candidates.extend(partial_matches)

        # 3. 複合語分解
        compound_matches = self._find_compound_matches(screen_name, vocab_terms, threshold)
        candidates.extend(compound_matches)

        # 4. 表記ゆれ
        variation_matches = self._find_variation_matches(screen_name, vocab_terms, threshold)
        candidates.extend(variation_matches)

        # 5. 曖昧マッチング
        fuzzy_matches = self._find_fuzzy_matches(screen_name, vocab_terms, threshold)
        candidates.extend(fuzzy_matches)

        # 重複除去とスコア順ソート
        unique_candidates = self._deduplicate_candidates(candidates)
        unique_candidates.sort(key=lambda c: c.score, reverse=True)

        return unique_candidates

    def _find_exact_matches(self, screen_name: str, vocab_terms: List[str]) -> List[EnhancedCandidate]:
        """完全一致検索"""
        candidates = []
        normalized_screen = self.enhanced_normalize(screen_name)

        for term in vocab_terms:
            normalized_term = self.enhanced_normalize(term)
            if normalized_screen == normalized_term:
                candidates.append(EnhancedCandidate(
                    term=term,
                    score=1.0,
                    match_type="exact"
                ))

        return candidates

    def _find_partial_matches(self, screen_name: str, vocab_terms: List[str],
                             threshold: float) -> List[EnhancedCandidate]:
        """部分一致検索（包含関係）"""
        candidates = []
        normalized_screen = self.enhanced_normalize(screen_name)

        for term in vocab_terms:
            normalized_term = self.enhanced_normalize(term)

            # 双方向包含チェック
            if normalized_term in normalized_screen:
                score = len(normalized_term) / len(normalized_screen)
                if score >= threshold:
                    candidates.append(EnhancedCandidate(
                        term=term,
                        score=min(0.9, score),  # 部分一致は最大0.9
                        match_type="partial"
                    ))
            elif normalized_screen in normalized_term:
                score = len(normalized_screen) / len(normalized_term)
                if score >= threshold:
                    candidates.append(EnhancedCandidate(
                        term=term,
                        score=min(0.9, score),
                        match_type="partial"
                    ))

        return candidates

    def _find_compound_matches(self, screen_name: str, vocab_terms: List[str],
                              threshold: float) -> List[EnhancedCandidate]:
        """複合語分解マッチング"""
        candidates = []
        normalized_screen = self.enhanced_normalize(screen_name)
        screen_tokens = [t for t in normalized_screen.split() if t]

        # 各語彙に対して、スクリーン名のトークンとの類似度を計算
        for term in vocab_terms:
            normalized_term = self.enhanced_normalize(term)

            # トークンレベルでの一致チェック
            for token in screen_tokens:
                similarity = self._calculate_token_similarity(token, normalized_term)
                if similarity >= threshold:
                    candidates.append(EnhancedCandidate(
                        term=term,
                        score=similarity,
                        match_type="compound",
                        components=screen_tokens
                    ))

        return candidates

    def _find_variation_matches(self, screen_name: str, vocab_terms: List[str],
                               threshold: float) -> List[EnhancedCandidate]:
        """表記ゆれマッチング"""
        candidates = []

        # 表記ゆれ辞書による変換
        converted_screen = screen_name
        for variation, standard in self.variation_dict.items():
            if variation in screen_name:
                converted_screen = screen_name.replace(variation, standard)
                break

        if converted_screen != screen_name:
            # 変換後の語で再検索
            for term in vocab_terms:
                similarity = self._calculate_similarity(converted_screen, term)
                if similarity >= threshold:
                    candidates.append(EnhancedCandidate(
                        term=term,
                        score=similarity * 0.95,  # 表記ゆれは少し減点
                        match_type="variation"
                    ))

        # 同義語グループによるマッチング
        for group in self.synonym_groups:
            screen_words = set(self.enhanced_normalize(screen_name).split())
            if screen_words & group:  # 共通要素があれば
                for term in vocab_terms:
                    term_words = set(self.enhanced_normalize(term).split())
                    if term_words & group:
                        overlap_ratio = len(screen_words & term_words) / len(screen_words | term_words)
                        if overlap_ratio >= threshold:
                            candidates.append(EnhancedCandidate(
                                term=term,
                                score=overlap_ratio * 0.9,
                                match_type="synonym"
                            ))

        return candidates

    def _find_fuzzy_matches(self, screen_name: str, vocab_terms: List[str],
                           threshold: float) -> List[EnhancedCandidate]:
        """曖昧マッチング（編集距離ベース）"""
        candidates = []
        normalized_screen = self.enhanced_normalize(screen_name)

        for term in vocab_terms:
            normalized_term = self.enhanced_normalize(term)

            # 編集距離による類似度
            edit_similarity = difflib.SequenceMatcher(None, normalized_screen, normalized_term).ratio()

            # 文字レベルの重複度
            char_overlap = len(set(normalized_screen) & set(normalized_term))
            char_similarity = char_overlap / max(len(set(normalized_screen)), len(set(normalized_term)), 1)

            # 複合スコア
            fuzzy_score = (edit_similarity * 0.7 + char_similarity * 0.3)

            if fuzzy_score >= threshold:
                candidates.append(EnhancedCandidate(
                    term=term,
                    score=fuzzy_score * 0.8,  # 曖昧マッチは減点
                    match_type="fuzzy"
                ))

        return candidates

    def _calculate_token_similarity(self, token: str, term: str) -> float:
        """トークンと語彙の類似度計算"""
        if token == term:
            return 1.0
        if token in term or term in token:
            return 0.9
        return difflib.SequenceMatcher(None, token, term).ratio()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """基本類似度計算"""
        norm1 = self.enhanced_normalize(text1)
        norm2 = self.enhanced_normalize(text2)

        if norm1 == norm2:
            return 1.0
        if norm1 in norm2 or norm2 in norm1:
            return 0.9
        return difflib.SequenceMatcher(None, norm1, norm2).ratio()

    def _deduplicate_candidates(self, candidates: List[EnhancedCandidate]) -> List[EnhancedCandidate]:
        """候補の重複除去（最高スコアを保持）"""
        best_candidates = {}

        for candidate in candidates:
            key = candidate.term
            if key not in best_candidates or candidate.score > best_candidates[key].score:
                best_candidates[key] = candidate

        return list(best_candidates.values())

    def generate_compound_explanation(self, screen_name: str, matched_candidates: List[EnhancedCandidate]) -> Dict:
        """複合語の説明を生成"""
        compound_candidates = [c for c in matched_candidates if c.match_type in ["compound", "partial"]]

        if len(compound_candidates) >= 2:
            terms = [c.term for c in compound_candidates[:3]]
            avg_score = sum(c.score for c in compound_candidates[:3]) / len(compound_candidates[:3])

            return {
                "match_type": "一部一致",
                "matched_term": None,
                "matched_terms": terms,
                "reason": f"複合語として「{', '.join(terms)}」の組み合わせと一致",
                "coverage_ratio": avg_score,
                "proposed_name": self._generate_compound_name(terms)
            }

        elif compound_candidates:
            candidate = compound_candidates[0]
            return {
                "match_type": "一部一致",
                "matched_term": candidate.term,
                "matched_terms": None,
                "reason": f"部分一致: '{candidate.match_type}' マッチング",
                "coverage_ratio": candidate.score,
                "proposed_name": self._generate_physical_name(candidate.term)
            }

        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": "適合する語彙が見つかりませんでした",
            "coverage_ratio": None,
            "proposed_name": self._generate_physical_name(screen_name)
        }

    def _generate_compound_name(self, terms: List[str]) -> str:
        """複合語の物理名生成"""
        # 簡易的な変換ルール
        translations = {
            "顧客": "customer",
            "商品": "product",
            "注文": "order",
            "コード": "code",
            "番号": "number",
            "名称": "name",
            "管理": "management",
            "システム": "system",
            "情報": "info",
            "データ": "data",
            "フラグ": "flag",
            "状態": "status",
            "日付": "date",
            "金額": "amount"
        }

        parts = []
        for term in terms[:3]:  # 最大3語まで
            if term in translations:
                parts.append(translations[term])
            else:
                # フォールバック：ひらがな化して最初の3文字
                parts.append(re.sub(r'[^a-z]', '', term.lower())[:3] or "item")

        if parts:
            return parts[0] + "".join(p.capitalize() for p in parts[1:])
        return "compoundItem"

    def _generate_physical_name(self, term: str) -> str:
        """単一語の物理名生成"""
        translations = {
            "顧客": "customer",
            "商品": "product",
            "注文": "order",
            "コード": "code",
            "番号": "number",
            "名称": "name",
        }
        return translations.get(term, re.sub(r'[^a-z]', '', term.lower())[:8] or "item")


# テスト関数
def test_enhanced_matching():
    """拡張マッチング機能のテスト"""
    print("=" * 60)
    print("拡張マッチング機能テスト")
    print("=" * 60)

    matcher = EnhancedMatcher()
    vocab_terms = [
        '顧客', '顧客コード', '顧客名', '商品', '商品コード', '商品名',
        '注文', '注文番号', '融資', '管理', '番号', 'コード', '名称',
        'システム', '削除', 'フラグ', '状態', '情報'
    ]

    test_cases = [
        "顧客CD",           # 略語
        "クライアント情報",  # 表記ゆれ
        "融資管理システム",  # 複合語
        "商晶コード",       # 誤字
        "プロダクト名称",    # カタカナ英語
    ]

    for screen_name in test_cases:
        print(f"\n🔍 '{screen_name}' の分析:")
        candidates = matcher.find_enhanced_candidates(screen_name, vocab_terms, threshold=0.6)

        for i, candidate in enumerate(candidates[:5]):
            print(f"  {i+1}. {candidate.term} (スコア: {candidate.score:.3f}, タイプ: {candidate.match_type})")

        # 複合語説明生成
        explanation = matcher.generate_compound_explanation(screen_name, candidates)
        print(f"  → 結論: {explanation['match_type']}")
        if explanation.get('matched_terms'):
            print(f"     複合語: {explanation['matched_terms']}")
        elif explanation.get('matched_term'):
            print(f"     一致語: {explanation['matched_term']}")


if __name__ == "__main__":
    test_enhanced_matching()