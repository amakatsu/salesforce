#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized configuration loader for word-related tools.
Values primarily come from environment variables (.env/ENC).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)


def _as_bool(value: str) -> bool:
    return value.lower() != "false"


def get_word_config() -> Dict[str, Any]:
    """Return config for word matching tool."""
    return {
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:54000"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "PBkBKGPT0SpkSub001OAI001MDL015"),
        "OPENAI_PATH": os.getenv("OPENAI_PATH", "/api/curl/v2/chat/"),
        "OPENAI_HEADERS_JSON": os.getenv(
            "OPENAI_HEADERS_JSON",
            '{"api-key":"QXwXLlZijq1U8WwiYfIu3znm3wWK3qIG","apim-user-id":"PIT03077"}',
        ),
        "OPENAI_SEND_AUTH": _as_bool(os.getenv("OPENAI_SEND_AUTH", "false")),
        "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
        "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
        "VERIFY_SSL": _as_bool(os.getenv("VERIFY_SSL", "true")),
        "MAX_TOKENS": 8192,
        "TEMPERATURE": 1.0,
        "TOP_P": 1.0,
        "PRESENCE_PENALTY": float(os.getenv("PRESENCE_PENALTY", "0.0")),
        "FREQUENCY_PENALTY": float(os.getenv("FREQUENCY_PENALTY", "0.0")),
        "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
        "VOCAB_GLOB": os.getenv("VOCAB_GLOB", "*単語名一覧*.xlsx"),
        "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "*"),
        "VOCAB_SHEET": os.getenv("VOCAB_SHEET", "*"),
        "SCREEN_COL": os.getenv("SCREEN_COL", "項目名称"),
        "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "論理名"),
        "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名（正式名称）,物理名"),
        "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
        "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "No,#"),
        "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.68")),
        "TOP_K": int(os.getenv("TOP_K", "5")),
        "OUT_DIR": os.getenv("OUT_DIR", "out"),
        "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
        "RETRY": int(os.getenv("RETRY", "30")),
        "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),
    }


def get_domain_config() -> Dict[str, Any]:
    """Return config for domain check tool."""
    return {
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:54000"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "PBkBKGPT0SpkSub001OAI001MDL015"),
        "OPENAI_PATH": os.getenv("OPENAI_PATH", "/api/curl/v2/chat/"),
        "OPENAI_HEADERS_JSON": os.getenv(
            "OPENAI_HEADERS_JSON",
            '{"api-key":"8b843f2df20548899f93c0624452ea68","apim-user-id":"PIT04447"}',
        ),
        "OPENAI_SEND_AUTH": _as_bool(os.getenv("OPENAI_SEND_AUTH", "false")),
        "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
        "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
        "VERIFY_SSL": _as_bool(os.getenv("VERIFY_SSL", "false")),
        "MAX_TOKENS": 8192,
        "TEMPERATURE": 1.0,
        "TOP_P": 1.0,
        "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
        "DOMAIN_GLOB": os.getenv("DOMAIN_GLOB", "*ドメイン定義*.xlsx"),
        "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "*"),
        "DOMAIN_SHEET": os.getenv("DOMAIN_SHEET", "*"),
        "SCREEN_ITEM_COL": os.getenv("SCREEN_ITEM_COL", "項目名称"),
        "SCREEN_TYPE_COL": os.getenv("SCREEN_TYPE_COL", "フィールド"),
        "SCREEN_LENGTH_COL": os.getenv("SCREEN_LENGTH_COL", "長さ"),
        "SCREEN_FORMAT_COL": os.getenv("SCREEN_FORMAT_COL", "編集形式"),
        "SCREEN_REQUIRED_COL": os.getenv("SCREEN_REQUIRED_COL", "必須"),
        "SCREEN_ITEM_COL_IDX": int(os.getenv("SCREEN_ITEM_COL_IDX", "-1")),
        "SCREEN_TYPE_COL_IDX": int(os.getenv("SCREEN_TYPE_COL_IDX", "6")),
        "SCREEN_LENGTH_COL_IDX": int(os.getenv("SCREEN_LENGTH_COL_IDX", "7")),
        "SCREEN_FORMAT_COL_IDX": int(os.getenv("SCREEN_FORMAT_COL_IDX", "8")),
        "SCREEN_REQUIRED_COL_IDX": int(os.getenv("SCREEN_REQUIRED_COL_IDX", "9")),
        "DOMAIN_NAME_COL": os.getenv("DOMAIN_NAME_COL", "ドメイン名"),
        "DOMAIN_TYPE_COL": os.getenv("DOMAIN_TYPE_COL", "データ型"),
        "DOMAIN_MIN_CHAR_COL": os.getenv("DOMAIN_MIN_CHAR_COL", "最小文字数"),
        "DOMAIN_MAX_CHAR_COL": os.getenv("DOMAIN_MAX_CHAR_COL", "最大文字数"),
        "DOMAIN_MIN_BYTE_COL": os.getenv("DOMAIN_MIN_BYTE_COL", "最小バイト数"),
        "DOMAIN_MAX_BYTE_COL": os.getenv("DOMAIN_MAX_BYTE_COL", "最大バイト数"),
        "DOMAIN_DECIMAL_COL": os.getenv("DOMAIN_DECIMAL_COL", "小数部バイト数"),
        "DOMAIN_MIN_VALUE_COL": os.getenv("DOMAIN_MIN_VALUE_COL", "最小値"),
        "DOMAIN_MAX_VALUE_COL": os.getenv("DOMAIN_MAX_VALUE_COL", "最大値"),
        "DOMAIN_REGEX_COL": os.getenv("DOMAIN_REGEX_COL", "書式（正規表現）"),
        "DOMAIN_CODE_ID_COL": os.getenv("DOMAIN_CODE_ID_COL", "参照外部コードID"),
        "DOMAIN_NAME_COL_IDX": int(os.getenv("DOMAIN_NAME_COL_IDX", "-1")),
        "DOMAIN_TYPE_COL_IDX": int(os.getenv("DOMAIN_TYPE_COL_IDX", "-1")),
        "DOMAIN_MIN_CHAR_COL_IDX": int(os.getenv("DOMAIN_MIN_CHAR_COL_IDX", "5")),
        "DOMAIN_MAX_CHAR_COL_IDX": int(os.getenv("DOMAIN_MAX_CHAR_COL_IDX", "6")),
        "DOMAIN_MIN_BYTE_COL_IDX": int(os.getenv("DOMAIN_MIN_BYTE_COL_IDX", "7")),
        "DOMAIN_MAX_BYTE_COL_IDX": int(os.getenv("DOMAIN_MAX_BYTE_COL_IDX", "8")),
        "DOMAIN_DECIMAL_COL_IDX": int(os.getenv("DOMAIN_DECIMAL_COL_IDX", "9")),
        "DOMAIN_MIN_VALUE_COL_IDX": int(os.getenv("DOMAIN_MIN_VALUE_COL_IDX", "10")),
        "DOMAIN_MAX_VALUE_COL_IDX": int(os.getenv("DOMAIN_MAX_VALUE_COL_IDX", "11")),
        "DOMAIN_REGEX_COL_IDX": int(os.getenv("DOMAIN_REGEX_COL_IDX", "12")),
        "DOMAIN_CODE_ID_COL_IDX": int(os.getenv("DOMAIN_CODE_ID_COL_IDX", "13")),
        "OUT_DIR": os.getenv("OUT_DIR", "out"),
        "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
        "RETRY": int(os.getenv("RETRY", "2")),
        "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),
        "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),
    }


__all__ = ["get_word_config", "get_domain_config"]
