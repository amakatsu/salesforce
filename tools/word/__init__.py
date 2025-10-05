#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語マッチングツール
"""
from .text_utils import (
    Candidate,
    normalize_text,
    calculate_similarity,
    find_top_candidates,
    generate_simple_physical_name
)
from .llm_handler import (
    build_llm_prompt,
    call_llm_api,
    create_fallback_response
)
from .excel_loader import (
    pick_matching_sheets,
    detect_header_row_with_required_cols,
    load_excel_with_auto_header
)

__all__ = [
    # Text Utils
    'Candidate',
    'normalize_text',
    'calculate_similarity',
    'find_top_candidates',
    'generate_simple_physical_name',
    # LLM Handler
    'build_llm_prompt',
    'call_llm_api',
    'create_fallback_response',
    # Excel Loader
    'pick_matching_sheets',
    'detect_header_row_with_required_cols',
    'load_excel_with_auto_header',
]
