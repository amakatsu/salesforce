#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Settings package exposing default configuration constants."""

from .config import (
    DEFAULT_CONFIG,
    HARD_EXACT_SCORE,
    FALLBACK_EXACT_FLOOR,
    HEADER_DETECT,
    HEADER_SCAN_ROWS,
    SCREEN_HEADER_ROW,
    VOCAB_HEADER_ROW,
    LLM_SYSTEM,
    LLM_USER_TEMPLATE,
)

__all__ = [
    "DEFAULT_CONFIG",
    "HARD_EXACT_SCORE",
    "FALLBACK_EXACT_FLOOR",
    "HEADER_DETECT",
    "HEADER_SCAN_ROWS",
    "SCREEN_HEADER_ROW",
    "VOCAB_HEADER_ROW",
    "LLM_SYSTEM",
    "LLM_USER_TEMPLATE",
]
