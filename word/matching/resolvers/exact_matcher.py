#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正規化辞書を使って完全一致ショートカット。"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from ...utils import normalize_term_no, zenkaku_hankaku_norm

__all__ = ["ExactMatchResolver"]


def _simple_proposal(text: str) -> str:
    """ローワーキャメルの簡易物理名を生成（8〜10文字程度）。"""

    normalized = zenkaku_hankaku_norm(text)
    tokens = [t for t in re.split(r"\s+", normalized) if t]
    if not tokens:
        return "newItem"
    stop_words = {"コード", "番号", "名称名", "名称名称"}
    core = [w for w in tokens[:3] if w not in stop_words] or tokens[:2]
    name = core[0].lower() + "".join(w.capitalize() for w in core[1:])
    return name or "newItem"


class ExactMatchResolver:
    """正規化辞書を使って完全一致（LLM不要のケース）を検出する。"""

    def __init__(self, normalized_lookup: Dict[str, str], term_metadata: Dict[str, Dict[str, Any]]) -> None:
        self._normalized_lookup = normalized_lookup
        self._term_metadata = term_metadata

    def resolve(
        self,
        screen_name: str,
        src_file: str,
        src_sheet: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """正規化完全一致が見つかれば結果行の辞書を返し、無ければ ``None``。"""

        normalized = zenkaku_hankaku_norm(screen_name)
        exact_term = self._normalized_lookup.get(normalized)
        if not exact_term:
            return None

        meta = self._term_metadata.get(exact_term) or {}
        matched_no = normalize_term_no(meta.get("_no"))
        matched_phys = meta.get("_phys_abbr") or meta.get("_phys")
        proposed_name = matched_phys or _simple_proposal(exact_term)
        return {
            "source_file": src_file,
            "source_sheet": src_sheet,
            "screen_item": screen_name,
            "match_type": "完全一致",
            "matched_term": exact_term,
            "matched_term_no": matched_no,
            "matched_term_phys": matched_phys,
            "matched_terms": f"{exact_term}(1.00)",
            "matched_terms_nos": None,
            "matched_terms_phys": None,
            "local_top_term": exact_term,
            "local_top_term_no": matched_no,
            "local_top_term_phys": matched_phys,
            "local_top_score": 1.0,
            "coverage_ratio": 1.0,
            "reason": "正規化完全一致（LLM未呼び出し）",
            "proposed_name": proposed_name,
            "unmatched_terms": None,
            "unmatched_note": None,
        }
