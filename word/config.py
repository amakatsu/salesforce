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
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:53000"),
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
        "MAX_TOKENS": 128000,  # LLMへのリクエスト時の max_completion_tokens。API上限に合わせて設定
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
        "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "120")),
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
        "RETRY": int(os.getenv("RETRY", "30")),
        "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),
    }


def get_domain_config() -> Dict[str, Any]:
    """Return config for domain check tool."""
    return {
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:53000"),
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
        "MAX_TOKENS": 128000,
        "TEMPERATURE": 1.0,
        "TOP_P": 1.0,
        # --- 入力ファイル Glob/Sheet ---
        "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
        "DOMAIN_GLOB": os.getenv("DOMAIN_GLOB", "*ドメイン定義*.xlsx"),
        "TABLE_GLOB": os.getenv("TABLE_GLOB", "*テーブル定義*.xlsx"),
        "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "*"),
        "DOMAIN_SHEET": os.getenv("DOMAIN_SHEET", "*"),
        "TABLE_SHEET": os.getenv("TABLE_SHEET", "*"),
        # --- 画面項目定義 列名（確定仕様: 10列） ---
        "SCREEN_FILE_COL": os.getenv("SCREEN_FILE_COL", "ファイル名"),  # ※ 確定仕様の対象列には含まれない。出力用
        "SCREEN_ITEM_COL": os.getenv("SCREEN_ITEM_COL", "項目名称"),
        "SCREEN_TYPE_COL": os.getenv("SCREEN_TYPE_COL", "型"),
        "SCREEN_TEXT_TYPE_COL": os.getenv("SCREEN_TEXT_TYPE_COL", "テキストタイプ"),
        "SCREEN_MIN_DIGITS_COL": os.getenv("SCREEN_MIN_DIGITS_COL", "最小桁"),
        "SCREEN_MAX_DIGITS_COL": os.getenv("SCREEN_MAX_DIGITS_COL", "最大桁"),
        "SCREEN_MAX_BYTES_COL": os.getenv("SCREEN_MAX_BYTES_COL", "最大バイト数"),
        "SCREEN_MIN_VALUE_COL": os.getenv("SCREEN_MIN_VALUE_COL", "最小値"),
       "SCREEN_MAX_VALUE_COL": os.getenv("SCREEN_MAX_VALUE_COL", "最大値"),
        "SCREEN_EXT_CODE_COL": os.getenv("SCREEN_EXT_CODE_COL", "外部コード"),
        # --- ドメイン定義 列名（確定仕様: 12列） ---
        "DOMAIN_NAME_COL": os.getenv("DOMAIN_NAME_COL", "ドメイン名"),
        "DOMAIN_TYPE_COL": os.getenv("DOMAIN_TYPE_COL", "データ型"),
        "DOMAIN_STR_MIN_CHARS_COL": os.getenv("DOMAIN_STR_MIN_CHARS_COL", "最小文字数"),
        "DOMAIN_STR_MAX_CHARS_COL": os.getenv("DOMAIN_STR_MAX_CHARS_COL", "最大文字数"),
        "DOMAIN_BYTES_MIN_COL": os.getenv("DOMAIN_BYTES_MIN_COL", "最小バイト長"),
        "DOMAIN_BYTES_MAX_COL": os.getenv("DOMAIN_BYTES_MAX_COL", "最大バイト長"),
        "DOMAIN_INT_DIGITS_COL": os.getenv("DOMAIN_INT_DIGITS_COL", "整数部桁数"),
        "DOMAIN_DEC_DIGITS_COL": os.getenv("DOMAIN_DEC_DIGITS_COL", "小数部桁数"),
        "DOMAIN_NUM_MIN_COL": os.getenv("DOMAIN_NUM_MIN_COL", "最小値"),
        "DOMAIN_NUM_MAX_COL": os.getenv("DOMAIN_NUM_MAX_COL", "最大値"),
        "DOMAIN_EXT_CODE_COL": os.getenv("DOMAIN_EXT_CODE_COL", "参照外部コード"),
        "DOMAIN_REGEX_COL": os.getenv("DOMAIN_REGEX_COL", "書式（正規表現）"),
        # --- テーブル定義 列名（確定仕様: 6列） ---
        "TABLE_FILE_COL": os.getenv("TABLE_FILE_COL", "ファイル名"),
        "TABLE_ITEM_COL": os.getenv("TABLE_ITEM_COL", "論理項目名"),
        "TABLE_TYPE_COL": os.getenv("TABLE_TYPE_COL", "データ型"),
        "TABLE_LENGTH_COL": os.getenv("TABLE_LENGTH_COL", "Length"),
        "TABLE_INT_COL": os.getenv("TABLE_INT_COL", "全体数値"),
        "TABLE_DEC_COL": os.getenv("TABLE_DEC_COL", "少数桁"),
        # --- 出力シート名 ---
        "SHEET_SCREEN_RAW": os.getenv("SHEET_SCREEN_RAW", "画面項目_抽出"),
        "SHEET_TABLE_RAW": os.getenv("SHEET_TABLE_RAW", "テーブル定義_抽出"),
        "SHEET_SCREEN_DEDUP": os.getenv("SHEET_SCREEN_DEDUP", "画面項目_重複排除"),
        "SHEET_TABLE_DEDUP": os.getenv("SHEET_TABLE_DEDUP", "テーブル定義_重複排除"),
        # --- マッチング判定 設定 ---
        "SYNONYM_FILE_PATH": os.getenv("SYNONYM_FILE_PATH", "word/domain/synonyms.yaml"),
        "DOMAIN_MAPPING_PATH": os.getenv("DOMAIN_MAPPING_PATH", "word/domain/domain_mapping.yaml"),
        "MATCHING_STRIP_NUMBERS": _as_bool(os.getenv("MATCHING_STRIP_NUMBERS", "true")),
        "MATCHING_PARTIAL_THRESHOLD": int(os.getenv("MATCHING_PARTIAL_THRESHOLD", "2")),
        "MATCHING_FLAG_KEYWORDS": os.getenv("MATCHING_FLAG_KEYWORDS", "フラグ,FLG,flag"),
        "MATCHING_DATE_KEYWORDS": os.getenv("MATCHING_DATE_KEYWORDS", "日付,日,年月日"),
        "MATCHING_GENERIC_FLAG_DOMAIN": os.getenv("MATCHING_GENERIC_FLAG_DOMAIN", "以下から選択: 0/1, 0/9, null/1, スペース/1"),
        "MATCHING_GENERIC_DATE_DOMAIN": os.getenv("MATCHING_GENERIC_DATE_DOMAIN", "ドメイン（日付）"),
        "MATCHING_COMMENT_KEYWORDS": os.getenv("MATCHING_COMMENT_KEYWORDS", "コメント,補記"),
        "MATCHING_GENERIC_COMMENT_DOMAIN": os.getenv("MATCHING_GENERIC_COMMENT_DOMAIN", "改行あり/なしを確認して選択してください"),
        # --- LLM判定 設定（B方式用・将来用） ---
        "LLM_MATCHING_ENABLED": _as_bool(os.getenv("LLM_MATCHING_ENABLED", "true")),
        "LLM_CANDIDATE_TOP_N": int(os.getenv("LLM_CANDIDATE_TOP_N", "20")),
        "LLM_CANDIDATE_MIN_SIM": float(os.getenv("LLM_CANDIDATE_MIN_SIM", "0.4")),
        "LLM_CANDIDATE_MIN_DIGIT": float(os.getenv("LLM_CANDIDATE_MIN_DIGIT", "0.4")),
        "SYNONYM_PARTIAL_SIM_THRESHOLD": float(os.getenv("SYNONYM_PARTIAL_SIM_THRESHOLD", "0.78")),
        "LLM_MATCHING_BATCH_SIZE": int(os.getenv("LLM_MATCHING_BATCH_SIZE", "5")),
        # --- 出力・実行制御 ---
        "OUT_DIR": os.getenv("OUT_DIR", "out"),
        "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "120")),
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
        "RETRY": int(os.getenv("RETRY", "2")),
        "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),
        "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),
    }


__all__ = ["get_word_config", "get_domain_config"]
