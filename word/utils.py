#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility helpers for normalization and similarity."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any, Optional

__all__ = ["zenkaku_hankaku_norm", "local_similarity", "normalize_term_no"]


def zenkaku_hankaku_norm(text: Optional[str]) -> str:
    """Normalize full/half width characters, punctuation, and whitespace."""

    if text is None:
        return ""

    normalized = unicodedata.normalize("NFKC", str(text)).strip()
    normalized = normalized.lower()
    normalized = normalized.replace("(", " ").replace(")", " ")
    normalized = re.sub(r"[-_/・]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def local_similarity(left: Optional[str], right: Optional[str]) -> float:
    """Return a similarity score with special handling for substrings and blanks."""

    if not left or not right:
        return 0.0

    left_norm = zenkaku_hankaku_norm(left)
    right_norm = zenkaku_hankaku_norm(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    if left_norm in right_norm or right_norm in left_norm:
        return 0.9
    return SequenceMatcher(a=left_norm, b=right_norm).ratio()


def normalize_term_no(value: Any) -> Optional[int]:
    """Normalize No column values to integers when possible."""

    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    value_str = str(value).strip()
    if not value_str:
        return None
    try:
        return int(float(value_str))
    except ValueError:
        return None
