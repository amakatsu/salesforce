#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通設定（CLI/Web両用）
YAMLファイルベースの設定を一元管理（環境変数で上書き可能）
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


# 設定ファイルのパス
_CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"
_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def _load_config_file() -> Dict[str, Any]:
    """
    YAMLファイルから設定を読み込み（キャッシュ）

    Returns:
        設定辞書
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    if not _CONFIG_FILE.exists():
        # デフォルト設定（config.yamlがない場合）
        _CONFIG_CACHE = {
            "api": {
                "base_url": "https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu",
                "model": "gpt-4o-mini",
                "path": "/chat/completions",
                "timeout_sec": 30,
                "send_auth": False,
                "org_id": ""
            },
            "proxy": {
                "http": "",
                "https": "",
                "verify_ssl": True
            },
            "llm": {
                "max_tokens": 800,
                "temperature": 0.7,
                "top_p": 0.95,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0
            },
            "execution": {
                "max_workers": 6,
                "retry": 2,
                "max_concurrent_api": 5
            }
        }
        return _CONFIG_CACHE

    with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f)

    return _CONFIG_CACHE


def get_base_api_config() -> Dict[str, Any]:
    """
    API関連の基本設定を取得（YAMLファイル優先、環境変数で上書き可）

    Returns:
        API設定の辞書
    """
    cfg = _load_config_file()
    api_cfg = cfg.get("api", {})
    proxy_cfg = cfg.get("proxy", {})
    exec_cfg = cfg.get("execution", {})

    return {
        # --- API（OpenAI互換）
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", api_cfg.get("base_url", "")),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", api_cfg.get("model", "gpt-4o-mini")),
        "OPENAI_PATH": os.getenv("OPENAI_PATH", api_cfg.get("path", "/chat/completions")),
        "OPENAI_HEADERS_JSON": os.getenv("OPENAI_HEADERS_JSON", api_cfg.get("headers_json", "{}")),
        "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", str(api_cfg.get("send_auth", False))).lower() != "false",
        "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", api_cfg.get("org_id", "")),

        # --- プロキシ設定
        "HTTP_PROXY": os.getenv("HTTP_PROXY", proxy_cfg.get("http", "")),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY", proxy_cfg.get("https", "")),
        "VERIFY_SSL": os.getenv("VERIFY_SSL", str(proxy_cfg.get("verify_ssl", True))).lower() != "false",

        # --- 実行制御
        "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", str(api_cfg.get("timeout_sec", 30)))),
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", str(exec_cfg.get("max_workers", 6)))),
        "RETRY": int(os.getenv("RETRY", str(exec_cfg.get("retry", 2)))),
        "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", str(exec_cfg.get("max_concurrent_api", 5)))),
    }


def get_llm_params_config() -> Dict[str, Any]:
    """
    LLM生成パラメータの設定を取得（YAMLファイル優先、環境変数で上書き可）

    Returns:
        LLMパラメータ設定の辞書
    """
    cfg = _load_config_file()
    llm_cfg = cfg.get("llm", {})

    return {
        "MAX_TOKENS": int(os.getenv("MAX_TOKENS", str(llm_cfg.get("max_tokens", 800)))),
        "TEMPERATURE": float(os.getenv("TEMPERATURE", str(llm_cfg.get("temperature", 0.7)))),
        "TOP_P": float(os.getenv("TOP_P", str(llm_cfg.get("top_p", 0.95)))),
        "PRESENCE_PENALTY": float(os.getenv("PRESENCE_PENALTY", str(llm_cfg.get("presence_penalty", 0.0)))),
        "FREQUENCY_PENALTY": float(os.getenv("FREQUENCY_PENALTY", str(llm_cfg.get("frequency_penalty", 0.0)))),
    }


def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """
    ツール固有の設定を取得（YAMLファイル優先、環境変数で上書き可）

    Args:
        tool_name: ツール名（"word", "domain" など）

    Returns:
        ツール固有設定の辞書
    """
    cfg = _load_config_file()
    tool_cfg = cfg.get(tool_name, {})

    # 環境変数で上書き（大文字・アンダースコア形式に変換）
    result = {}
    for key, value in tool_cfg.items():
        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            result[env_key] = env_value
        else:
            result[env_key] = value

    return result


def get_common_config() -> Dict[str, Any]:
    """
    共通設定を統合して取得

    Returns:
        統合された設定辞書
    """
    config = {}
    config.update(get_base_api_config())
    config.update(get_llm_params_config())
    return config
