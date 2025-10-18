#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM 応答を最終的な結果行に整形するユーティリティ。"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

try:
    from ..primitives import Candidate, ComponentMatchResult
    from ...llm.client import summarize_matched_terms
    from ...utils import normalize_term_no
except ImportError:  # pragma: no cover - fallback when run as a script
    from word.matching.primitives.candidates import Candidate  # type: ignore
    from word.matching.primitives.component_matcher import ComponentMatchResult  # type: ignore
    from word.llm.client import summarize_matched_terms  # type: ignore
    from word.utils import normalize_term_no  # type: ignore

__all__ = ["build_result_row"]


def build_result_row(
    screen_name: str,
    src_file: str,
    src_sheet: Optional[str],
    component_analysis: ComponentMatchResult,
    ranked_candidates: List[Candidate],
    ranked_terms: List[str],
    llm_response: Dict[str, Any],
    term_metadata: Dict[str, Dict[str, Any]],
    lookup_term_metadata: Callable[[Optional[str]], Dict[str, Any]],
) -> Dict[str, Any]:
    """LLM の応答にメタ情報を補完し、出力 1 行分の辞書に整形する。"""

    llm_match_type = llm_response.get("match_type")
    llm_matched_term = llm_response.get("matched_term")

    if component_analysis.matched_terms:
        matched_term_val: Optional[str] = None
        coverage_ratio = component_analysis.coverage_ratio
    else:
        matched_term_val = llm_matched_term
        cov_raw = llm_response.get("coverage_ratio")
        try:
            coverage_ratio = float(cov_raw) if cov_raw is not None else None
        except Exception:
            coverage_ratio = None

    mt_meta = lookup_term_metadata(matched_term_val)
    matched_terms_display, joined_matched_terms_nos, joined_matched_terms_phys = summarize_matched_terms(
        ranked_terms, lookup_term_metadata
    )

    llm_unmatched_terms: List[str] = []
    llm_unmatched_notes: List[str] = []
    try:
        llm_unmatched_terms = llm_response.get("unmatched_terms") or []
        llm_unmatched_notes = llm_response.get("unmatched_notes") or []
    except Exception:
        pass

    unmatched_terms = None
    unmatched_note = None
    if component_analysis.matched_terms:
        if component_analysis.unmatched_segments:
            unmatched_terms = ", ".join(component_analysis.unmatched_segments)
            if llm_unmatched_notes:
                unmatched_note = " / ".join(llm_unmatched_notes)
    else:
        if llm_unmatched_terms and llm_unmatched_notes:
            unmatched_terms = ", ".join(llm_unmatched_terms)
            unmatched_note = " / ".join(llm_unmatched_notes)
    if unmatched_note is None and llm_unmatched_notes:
        unmatched_note = " / ".join(llm_unmatched_notes)

    final_match_type = llm_match_type
    if component_analysis.matched_terms:
        final_match_type = "一部一致" if component_analysis.unmatched_segments else "完全一致（部品ごと）"
    elif final_match_type == "完全一致（部品ごと）":
        final_match_type = "一部一致"

    local_top = ranked_candidates[0] if ranked_candidates else None
    local_top_term = local_top.term if local_top else None
    local_top_score = local_top.score if local_top else None
    local_top_meta = term_metadata.get(local_top_term) or {} if local_top else {}
    local_top_term_no = normalize_term_no(local_top_meta.get("_no")) if local_top else None
    local_top_term_phys = None
    if local_top:
        local_top_term_phys = local_top_meta.get("_phys_abbr") or local_top_meta.get("_phys")

    return {
        "source_file": src_file,
        "source_sheet": src_sheet,
        "screen_item": screen_name,
        "match_type": final_match_type,
        "matched_term": matched_term_val,
        "matched_term_no": mt_meta.get("no"),
        "matched_term_phys": mt_meta.get("phys_abbr") or mt_meta.get("phys"),
        "matched_terms": matched_terms_display,
        "matched_terms_nos": joined_matched_terms_nos,
        "matched_terms_phys": joined_matched_terms_phys,
        "local_top_term": local_top_term,
        "local_top_term_no": local_top_term_no,
        "local_top_term_phys": local_top_term_phys,
        "local_top_score": local_top_score,
        "coverage_ratio": coverage_ratio,
        "reason": llm_response.get("reason"),
        "proposed_name": llm_response.get("proposed_name"),
        "unmatched_terms": unmatched_terms,
        "unmatched_note": unmatched_note,
    }
