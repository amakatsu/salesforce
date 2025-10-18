#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""候補生成関数"""

from dataclasses import dataclass
from typing import List, Dict

try:
    from ...utils import zenkaku_hankaku_norm, local_similarity
except ImportError:  # pragma: no cover - fallback when run as a script
    from utils import zenkaku_hankaku_norm, local_similarity  # type: ignore


@dataclass
class Candidate:
    term: str
    score: float


def top_k_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """画面項目 vs 単語帳の**直接照合**で上位k件を返却。"""

    scored = [Candidate(term, local_similarity(screen_name, term)) for term in vocab_terms]
    scored.sort(key=lambda c: c.score, reverse=True)
    if k and k > 0:
        scored = scored[:k]
    return [c for c in scored if c.score >= threshold]


def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語対策：unigram/bigram に分解してパーツ単位で候補を拾う。"""

    tokens = [t for t in zenkaku_hankaku_norm(screen_name).split(" ") if t]
    grams = set(tokens)
    for i in range(len(tokens) - 1):
        grams.add(tokens[i] + " " + tokens[i + 1])
    pool: List[Candidate] = []
    for g in grams:
        for vt in vocab_terms:
            s = local_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))
    # 同一単語は最大スコアを採用
    best_by_term: Dict[str, float] = {}
    for cand in pool:
        best_by_term[cand.term] = max(best_by_term.get(cand.term, 0.0), cand.score)
    merged = [Candidate(t, sc) for t, sc in best_by_term.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    if k and k > 0:
        return merged[:k]
    return merged
