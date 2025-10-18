#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""コンポーネントマッチャー - 辞書語彙による簡易分割"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List

try:
    from ...utils import zenkaku_hankaku_norm
except ImportError:  # pragma: no cover - fallback when run as a script
    from utils import zenkaku_hankaku_norm  # type: ignore


@dataclass
class ComponentMatchResult:
    matched_terms: List[str]
    matched_norms: List[str]
    unmatched_segments: List[str]
    coverage_ratio: float
    unmatched_count: int
    has_non_digit: bool
    digit_segments: List[str]


class ComponentMatcher:
    """辞書語彙による簡易分割。数字はカバー率計算から除外。"""

    def __init__(self, norm_to_term: Dict[str, str]):
        trimmed: Dict[str, str] = {}
        for norm_value, original in norm_to_term.items():
            key = norm_value.replace(" ", "")
            if not key:
                continue
            trimmed.setdefault(key, original)
        self.norm_to_term = trimmed
        self.prefix_map: Dict[str, List[str]] = {}
        for norm_value in self.norm_to_term.keys():
            first = norm_value[0]
            self.prefix_map.setdefault(first, []).append(norm_value)
        for values in self.prefix_map.values():
            values.sort(key=len, reverse=True)
        self.nondigit_len: Dict[str, int] = {
            key: sum(1 for ch in key if not ch.isdigit()) for key in self.norm_to_term.keys()
        }

    def analyze(self, screen_name: str) -> ComponentMatchResult:
        normalized = zenkaku_hankaku_norm(screen_name)
        flat = normalized.replace(" ", "")
        if not flat:
            return ComponentMatchResult([], [], [], 1.0, 0, False, [])
        total_non_digit = sum(1 for ch in flat if not ch.isdigit())
        has_non_digit = total_non_digit > 0
        @lru_cache(maxsize=None)
        def walk(idx: int):
            if idx >= len(flat):
                return (0, 0, 0, [])
            best = None
            ch = flat[idx]
            if ch.isdigit():
                j = idx
                while j < len(flat) and flat[j].isdigit():
                    j += 1
                nxt = walk(j)
                if nxt is not None:
                    candidate = (nxt[0], nxt[1], nxt[2], [("digit", flat[idx:j], None)] + nxt[3])
                    best = self._better(best, candidate)
            if ch in self.prefix_map:
                for norm_term in self.prefix_map[ch]:
                    end = idx + len(norm_term)
                    if flat.startswith(norm_term, idx):
                        nxt = walk(end)
                        if nxt is None:
                            continue
                        term_non_digit = self.nondigit_len.get(norm_term, 0)
                        candidate = (
                            nxt[0],
                            nxt[1] + term_non_digit,
                            nxt[2] + 1,
                            [("term", norm_term, self.norm_to_term.get(norm_term, norm_term))] + nxt[3],
                        )
                        best = self._better(best, candidate)
            if not ch.isdigit():
                nxt = walk(idx + 1)
                if nxt is not None:
                    candidate = (nxt[0] + 1, nxt[1], nxt[2], [("unmatched", ch, None)] + nxt[3])
                    best = self._better(best, candidate)
            return best
        result = walk(0)
        if result is None:
            return ComponentMatchResult([], [], [], 0.0, total_non_digit, has_non_digit, [])
        _, matched_non_digit, _, steps = result
        matched_terms: List[str] = []
        matched_norms: List[str] = []
        unmatched_segments: List[str] = []
        digit_segments: List[str] = []
        buffer_unmatched = ""
        for step_type, value, extra in steps:
            if step_type == "term":
                if buffer_unmatched:
                    unmatched_segments.append(buffer_unmatched)
                    buffer_unmatched = ""
                matched_norms.append(value)
                matched_terms.append(extra or value)
            elif step_type == "digit":
                if buffer_unmatched:
                    unmatched_segments.append(buffer_unmatched)
                    buffer_unmatched = ""
                digit_segments.append(value)
            elif step_type == "unmatched":
                buffer_unmatched += value
        if buffer_unmatched:
            unmatched_segments.append(buffer_unmatched)
        coverage = 1.0
        if has_non_digit:
            coverage = matched_non_digit / total_non_digit if total_non_digit else 0.0
            if coverage > 1.0:
                coverage = 1.0
        unmatched_count = sum(len(seg) for seg in unmatched_segments)
        return ComponentMatchResult(
            matched_terms=matched_terms,
            matched_norms=matched_norms,
            unmatched_segments=unmatched_segments,
            coverage_ratio=coverage,
            unmatched_count=unmatched_count,
            has_non_digit=has_non_digit,
            digit_segments=digit_segments,
        )

    @staticmethod
    def _better(current, candidate):
        """重み付きで候補を比較する。未一致が少なく、被覆が高く、語数が少ないものを優先。"""

        if current is None:
            return candidate
        # 未一致文字数が少ない方を優先
        if candidate[0] != current[0]:
            return candidate if candidate[0] < current[0] else current
        # 被覆率（非数字の一致文字数）が多い方を優先
        if candidate[1] != current[1]:
            return candidate if candidate[1] > current[1] else current
        # 同条件なら語数が少ない（=長い語を選択）方を優先
        if candidate[2] != current[2]:
            return candidate if candidate[2] < current[2] else current
        return candidate
