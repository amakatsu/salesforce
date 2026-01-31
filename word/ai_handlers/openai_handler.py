#!/usr/bin/env python3
"""
OpenAI/Azure OpenAI/GPT-5 Cline Proxy ハンドラー
設定ファイル:
- .env: 環境変数を定義（API認証情報など）
- common.toml: PR-Agent設定（モデルパラメータなど）
"""
import os
import json
from typing import Tuple, Optional, Dict, Any

from pr_agent.config_loader import get_settings

from .base_handler import BaseCustomHandler


class OpenAIHandler(BaseCustomHandler):
    """
    OpenAI/Azure OpenAI/GPT-5 Cline Proxy対応ハンドラー
    """

    @property
    def provider_name(self) -> str:
        return "openai"

    def _initialize(self, settings) -> None:
        """OpenAI設定を初期化"""

        # ─────────────────────────────────────────────────────────
        # 設定ソース: settings (toml) 優先、env はフォールバック
        # ─────────────────────────────────────────────────────────
        custom_headers = settings.config.get("custom_headers", {})
        if isinstance(custom_headers, str):
            try:
                custom_headers = json.loads(custom_headers)
            except json.JSONDecodeError:
                custom_headers = {}

        parsed_headers = custom_headers if isinstance(custom_headers, dict) else {}
        self.parsed_headers = parsed_headers

        self.api_base = settings.get("openai.api_base")
        if not self.api_base:
            raise ValueError("openai.api_base is required")

        self.api_key = (
            settings.get("openai.key")
            or settings.config.get("openai_key")
            or self.parsed_headers.get("api-key", "")
        )
        if not self.api_key:
            raise ValueError("openai.key or openai_key or api-key is required")

        self.user_id = (
            settings.get("openai.user_id")
            or self.parsed_headers.get("apim-user-id", "")
        )

        self.api_path = settings.get("openai.path")
        if not self.api_path:
            raise ValueError("openai.path is required")

        # ログ出力
        full_url = self.api_base.rstrip('/') + self.api_path
        self.logger.info(f"OpenAI initialized (GPT-5 Cline Proxy対応)")
        self.logger.info(f"  - Endpoint: {full_url}")
        self.logger.info(f"  - has_api_key: {bool(self.api_key)}")
        self.logger.info(f"  - has_user_id: {bool(self.user_id)}")

    def _parse_headers_json(self) -> Dict[str, str]:
        """
        OPENAI_HEADERS_JSON をパース
        """
        return {}

    def _build_url(self, model: str = None) -> str:
        """APIエンドポイントURLを構築"""
        return self.api_base.rstrip('/') + self.api_path

    def _build_headers(self) -> Dict[str, str]:
        """
        HTTPリクエストヘッダーを構築

        ヘッダー:
        - Content-Type: application/json
        - api-key: API認証キー
        - apim-user-id: Azure APIM用ユーザーID
        """
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["api-key"] = self.api_key
        if self.user_id:
            headers["apim-user-id"] = self.user_id

        return headers

    def _build_request_body(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 1.0,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        リクエストボディを構築

        {
            "messages": [...],
            "model": .env OPENAI_MODEL
            "max_completion_tokens": common.toml max_model_tokens (8192)
            "n": 1
            "reasoning_effort": common.toml (high)
            "verbosity": common.toml (high)
        }
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        if img_path:
            messages[1]["content"] = [
                {"type": "text", "text": user},
                {"type": "image_url", "image_url": {"url": img_path}}
            ]

        settings = get_settings()

        # model priority: common.toml [config].model > .env OPENAI_MODEL (ignore explicit arg)
        actual_model = settings.config.get("model", "")
        if not actual_model:
            raise ValueError("Model is required (config.model)")
        self.logger.info(f"Using model: {actual_model}")

        # max_completion_tokens: common.toml [config] max_model_tokens
        max_tokens = settings.config.get("max_model_tokens", 8192)

        body = {
            "messages": messages,
            "model": actual_model,
            "max_completion_tokens": max_tokens,
            "n": 1,
        }

        if temperature > 0:
            body["temperature"] = temperature

        # reasoning_effort: common.toml [config]
        reasoning_effort = settings.config.get("reasoning_effort", "low")
        if reasoning_effort:
            body["reasoning_effort"] = reasoning_effort

        # verbosity: common.toml [config]
        verbosity = settings.config.get("verbosity", "low")
        if verbosity:
            body["verbosity"] = verbosity

        # seed: common.toml [config]
        seed = settings.config.get("seed", -1)
        if seed >= 0:
            if temperature > 0:
                raise ValueError(f"Seed ({seed}) is not supported with temperature > 0")
            body["seed"] = seed

        return body

    def _parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """OpenAIレスポンスを解析"""
        if not response_data.get("choices"):
            raise Exception("No choices in response")

        choice = response_data["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice.get("finish_reason", "stop")

        return content, finish_reason
