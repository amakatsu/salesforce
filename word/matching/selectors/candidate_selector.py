#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ComponentMatcher と類似度計算を組み合わせて候補を整列するコンポーネント。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    from ...settings import DEFAULT_CONFIG
    from ..primitives import Candidate, phrase_candidates, top_k_candidates
    from ..primitives import ComponentMatchResult, ComponentMatcher
    from ...utils import local_similarity, zenkaku_hankaku_norm
except ImportError:  # pragma: no cover - fallback when run as a script
    from settings import DEFAULT_CONFIG  # type: ignore
    from candidates import Candidate, phrase_candidates, top_k_candidates  # type: ignore
    from component_matcher import ComponentMatchResult, ComponentMatcher  # type: ignore
    from utils import local_similarity, zenkaku_hankaku_norm  # type: ignore

__all__ = ["CandidateSelector"]


class CandidateSelector:
    """画面項目名から LLM に渡す候補リストを構築する。"""

    def __init__(
        self,
        vocabulary_terms: List[str],
        normalized_term_lookup: Dict[str, str],
        cfg: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._vocabulary_terms = vocabulary_terms
        self._threshold = (cfg or {}).get("FUZZY_THRESHOLD", DEFAULT_CONFIG["FUZZY_THRESHOLD"])
        self._component_matcher = ComponentMatcher(normalized_term_lookup)

    def select(self, screen_name: str) -> Tuple[ComponentMatchResult, List[Candidate], List[str]]:
        """正規化による分割結果と類似度スコアを併用して候補を整列する。"""

        component_analysis = self._component_matcher.analyze(screen_name)

        # ComponentMatcher で拾えた語は最優先の候補とする
        component_hits: List[Candidate] = []
        if component_analysis.matched_terms:
            for term in component_analysis.matched_terms:
                score = local_similarity(screen_name, term)
                component_hits.append(Candidate(term, max(score, self._threshold)))

        component_terms = {candidate.term for candidate in component_hits}
        other_scores: Dict[str, float] = {}

        # 生の論理名に対する類似度検索（unigram/bigram と直接比較）で候補を補完
        base_candidates = (
            phrase_candidates(screen_name, self._vocabulary_terms, 0, self._threshold)
            + top_k_candidates(screen_name, self._vocabulary_terms, 0, self._threshold)
        )
        for candidate in base_candidates:
            if candidate.term in component_terms:
                continue
            other_scores[candidate.term] = max(other_scores.get(candidate.term, 0.0), candidate.score)

        # 画面名に含まれる語を正規化して拾い漏れを防ぐ
        normalized_screen = zenkaku_hankaku_norm(screen_name).replace(" ", "")
        for vocab_term in self._vocabulary_terms:
            if vocab_term in component_terms or vocab_term in other_scores:
                continue
            term_norm = zenkaku_hankaku_norm(vocab_term).replace(" ", "")
            if term_norm and term_norm in normalized_screen:
                score = local_similarity(screen_name, vocab_term)
                if score >= self._threshold:
                    other_scores[vocab_term] = score

        secondary_candidates = [Candidate(term, score) for term, score in other_scores.items()]
        secondary_candidates.sort(key=lambda candidate: candidate.score, reverse=True)

        ranked_candidates = component_hits + secondary_candidates
        ranked_candidates.sort(key=lambda candidate: candidate.score, reverse=True)

        ranked_terms: List[str] = []
        for candidate in ranked_candidates:
            if candidate.term not in ranked_terms:
                ranked_terms.append(candidate.term)

        return component_analysis, ranked_candidates, ranked_terms
