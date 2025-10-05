#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIバックエンド共通クラス
CLI/Web両方から使用可能
"""
import os
import json
from typing import Dict, Any, Optional
from .http_client import HttpClient
from .retry import retry_on_exception


class ApiBackend:
    """
    Azure OpenAI API呼び出しの共通バックエンド
    各ツールで統一したAPI呼び出しを提供
    """

    def __init__(
        self,
        api_key: str,
        user_id: str,
        base_url: str = None,
        model: str = None,
        timeout: float = 30.0
    ):
        """
        Args:
            api_key: Azure OpenAI APIキー
            user_id: APIM User ID
            base_url: APIのベースURL（デフォルト: 環境変数から取得）
            model: モデル名（デフォルト: gpt-4o-mini）
            timeout: タイムアウト秒数
        """
        self.base_url = base_url or os.getenv(
            "OPENAI_BASE_URL",
            "https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu"
        )
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.path = os.getenv("OPENAI_PATH", "/chat/completions")

        # ヘッダー構築
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
            "apim-user-id": user_id
        }

        # HTTPクライアント作成
        self.http_client = HttpClient(timeout=timeout)

    def call_llm(
        self,
        messages: list,
        max_tokens: int = 800,
        temperature: float = 0.7,
        top_p: float = 0.95,
        response_format: Optional[Dict[str, str]] = None,
        retry: int = 2
    ) -> Dict[str, Any]:
        """
        LLMを呼び出す

        Args:
            messages: メッセージリスト [{"role": "system", "content": "..."}, ...]
            max_tokens: 最大トークン数
            temperature: 温度パラメータ
            top_p: Top-pパラメータ
            response_format: レスポンス形式（例: {"type": "json_object"}）
            retry: リトライ回数

        Returns:
            APIレスポンス（JSON）
        """
        url = f"{self.base_url}{self.path}"

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }

        if response_format:
            payload["response_format"] = response_format

        # リトライロジックを使用してAPI呼び出し
        def _call():
            resp = self.http_client.post_json(url, self.headers, payload)
            return resp.json()

        return retry_on_exception(_call, max_retries=retry)

    def get_headers_json(self) -> str:
        """
        ヘッダーをJSON文字列として取得
        既存ツールとの互換性のため

        Returns:
            JSON文字列（ヘッダー情報）
        """
        return json.dumps({
            "api-key": self.headers["api-key"],
            "apim-user-id": self.headers["apim-user-id"]
        })

    def post_json(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        既存のApiClientとの互換性のためのメソッド
        JSONペイロードを直接POSTする

        Args:
            body: リクエストボディ（辞書形式）

        Returns:
            APIレスポンス（JSON）
        """
        url = f"{self.base_url}{self.path}"

        # HTTPクライアントを使用してPOST
        resp = self.http_client.post_json(url, self.headers, body)
        return resp.json()


def create_api_backend(cfg: Dict[str, Any]) -> ApiBackend:
    """
    設定辞書からApiBackendインスタンスを作成（CLI用）

    Args:
        cfg: 設定辞書（OPENAI_HEADERS_JSONからapi-keyとapim-user-idを取得）

    Returns:
        ApiBackendインスタンス
    """
    # OPENAI_HEADERS_JSONからAPI KeyとUser IDを抽出
    headers_json = cfg.get("OPENAI_HEADERS_JSON", "{}")
    try:
        headers = json.loads(headers_json)
        api_key = headers.get("api-key", "")
        user_id = headers.get("apim-user-id", "")
    except:
        api_key = ""
        user_id = ""

    return ApiBackend(
        api_key=api_key,
        user_id=user_id,
        base_url=cfg.get("OPENAI_BASE_URL"),
        model=cfg.get("OPENAI_MODEL"),
        timeout=cfg.get("TIMEOUT_SEC", 30.0)
    )
