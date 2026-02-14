#!/usr/bin/env python3
"""
Common LLM request helpers (chat format) shared by word/domain/gpt5chat.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("word.common_llm")


def _mask_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
    masked = {}
    sensitive_keys = ("key", "token", "secret", "authorization")
    for k, v in headers.items():
        if any(t in k.lower() for t in sensitive_keys):
            masked[k] = "***"
        else:
            masked[k] = v
    return masked


def log_request(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> None:
    summary = {
        "url": url,
        "model": payload.get("model"),
        "max_tokens": payload.get("max_completion_tokens"),
    }
    logger.info("LLM request summary: %s", json.dumps(summary, ensure_ascii=False))
    logger.info("=== HTTP Request Details ===")
    logger.info("URL: %s", url)
    logger.info("Headers: %s", json.dumps(_mask_sensitive_headers(headers), ensure_ascii=False, indent=2))
    logger.info("Request Body (full):\n%s", json.dumps(payload, ensure_ascii=False, indent=2))
    logger.info("===========================")


def log_response(status: int, headers: dict, body: str) -> None:
    logger.info("=== HTTP Response Details ===")
    logger.info("Status: %s", status)
    logger.info("Response Headers: %s", headers)
    logger.info("Response Body (raw):\n%s", body)
    logger.info("============================")


def build_headers(
    api_key: str | None,
    user_id: str | None,
    custom_headers: Dict[str, str] | None,
    extra_headers_json: str | None,
    send_auth: bool = False,
) -> Dict[str, str]:
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if custom_headers:
        headers.update(custom_headers)
    if extra_headers_json:
        try:
            extra = json.loads(extra_headers_json)
            if isinstance(extra, dict):
                headers.update(extra)
        except Exception:
            pass
    if api_key:
        headers.setdefault("api-key", str(api_key))
        if send_auth:
            headers["Authorization"] = f"Bearer {api_key}"
    if user_id:
        headers.setdefault("apim-user-id", str(user_id))
    return headers


def build_chat_payload(
    messages: List[Dict[str, Any]],
    model: str,
    max_tokens: int,
    temperature: Optional[float] = None,
    reasoning_effort: Optional[str] = None,
    verbosity: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "n": 1,
    }
    if temperature is not None and temperature > 0:
        payload["temperature"] = temperature
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    if verbosity:
        payload["verbosity"] = verbosity
    if seed is not None:
        payload["seed"] = seed
    return payload


def post_chat_requests(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    timeout: int = 120,
    verify_ssl: bool = True,
    proxies: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """word.py と同じ requests 送信ロジック。"""
    log_request(url, headers, payload)
    resp = None
    try:
        resp = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
            verify=verify_ssl,
            proxies=proxies,
        )
        resp.raise_for_status()
        log_response(resp.status_code, dict(resp.headers), resp.text[:5000])
        return resp.json()
    except requests.RequestException as exc:
        status = resp.status_code if resp is not None else getattr(exc.response, "status_code", "n/a")
        logger.error("HTTP POST失敗: status=%s error=%s", status, exc)
        if resp is not None:
            logger.error("HTTP レスポンスボディ(エラー):\n%s", resp.text)
        raise


def load_env_settings() -> Dict[str, Any]:
    return {
        "base_url": os.getenv("OPENAI_BASE_URL", ""),
        "path": os.getenv("OPENAI_PATH", "/api/curl/v2/chat/"),
        "model": os.getenv("OPENAI_MODEL", ""),
        "headers_json": os.getenv("OPENAI_HEADERS_JSON", ""),
        "send_auth": os.getenv("OPENAI_SEND_AUTH", "false").lower() == "true",
    }
