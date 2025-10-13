#!/usr/bin/env python3
"""
カスタムAIハンドラー - Azure OpenAI用
litellmをバイパスして、独自のHTTPリクエストでAzure OpenAI APIを呼び出す
"""
import os
import json
import asyncio
import aiohttp
from typing import Tuple, Optional, Dict, Any
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.config_loader import get_settings
from pr_agent.log import get_logger


class CustomAzureAIHandler(BaseAiHandler):
    """
    Azure OpenAI用のカスタムAIハンドラー
    litellmを使わずに直接HTTPリクエストを送信
    """

    def __init__(self):
        """
        Azure OpenAI API設定を初期化
        """
        self.logger = get_logger()

        # 設定から値を取得
        settings = get_settings()

        # API Base URL
        self.api_base = settings.get("OPENAI.API_BASE") or os.getenv("OPENAI_BASE_URL", "")
        if not self.api_base:
            raise ValueError("OPENAI.API_BASE or OPENAI_BASE_URL is required")

        # API Key
        self.api_key = settings.get("OPENAI.KEY") or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI.KEY or OPENAI_API_KEY is required")

        # User ID (Azure APIM用)
        self.user_id = settings.get("OPENAI.USER_ID") or os.getenv("APIM_USER_ID", "")

        # API Path
        self.api_path = settings.get("OPENAI.PATH") or os.getenv("OPENAI_PATH", "/chat/completions")

        # カスタムヘッダー（設定ファイルから取得）
        self.custom_headers = settings.get("config.custom_headers", {})

        # タイムアウト設定
        self.timeout = settings.config.get("ai_timeout", 120)

        # リトライ設定
        self.max_retries = 3
        self.retry_delay = 2

        self.logger.info(f"CustomAzureAIHandler initialized with base_url={self.api_base}")

    def _build_headers(self) -> Dict[str, str]:
        """
        HTTPリクエストヘッダーを構築
        """
        headers = {
            "Content-Type": "application/json",
        }

        # カスタムヘッダーを追加（設定ファイルから）
        if self.custom_headers:
            headers.update(self.custom_headers)
        else:
            # デフォルトヘッダー（環境変数から）
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
        temperature: float = 0.2,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        リクエストボディを構築
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        # 画像がある場合
        if img_path:
            messages[1]["content"] = [
                {"type": "text", "text": user},
                {"type": "image_url", "image_url": {"url": img_path}}
            ]

        body = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": get_settings().config.get("max_model_tokens", 32000),
        }

        # seedがある場合
        seed = get_settings().config.get("seed", -1)
        if temperature > 0 and seed >= 0:
            raise ValueError(f"Seed ({seed}) is not supported with temperature ({temperature}) > 0")
        elif seed >= 0:
            self.logger.info(f"Using fixed seed of {seed}")
            body["seed"] = seed

        return body

    async def _make_request(
        self,
        url: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        非同期HTTPリクエストを実行（リトライ機能付き）
        """
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=body) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:
                            # Rate limit - リトライ
                            retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                            self.logger.warning(f"Rate limit hit, retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            error_text = await response.text()
                            self.logger.error(f"API request failed: {response.status} - {error_text}")
                            raise Exception(f"API request failed: {response.status} - {error_text}")

            except asyncio.TimeoutError:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except Exception as e:
                self.logger.error(f"Request error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

        raise Exception(f"Failed after {self.max_retries} retries")

    async def chat_completion(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        img_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        チャット補完を実行

        Args:
            model: モデル名
            system: システムプロンプト
            user: ユーザープロンプト
            temperature: 温度パラメータ
            img_path: 画像URL（オプション）

        Returns:
            (response_text, finish_reason) のタプル
        """
        try:
            # URL構築
            url = self.api_base.rstrip('/') + self.api_path

            # ヘッダー構築
            headers = self._build_headers()

            # リクエストボディ構築
            body = self._build_request_body(model, system, user, temperature, img_path)

            # デバッグログ
            self.logger.debug("Prompts", artifact={"system": system, "user": user})
            if get_settings().config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nSystem prompt:\n{system}")
                self.logger.info(f"\nUser prompt:\n{user}")

            # HTTPリクエスト実行
            self.logger.info(f"Sending request to {url}")
            response_data = await self._make_request(url, headers, body)

            # レスポンス解析
            if not response_data.get("choices"):
                raise Exception("No choices in response")

            choice = response_data["choices"][0]
            resp = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")

            # デバッグログ
            self.logger.debug(f"\nAI response:\n{resp}")
            if get_settings().config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nAI response:\n{resp}")

            # 詳細ログ
            response_log = {
                "model": model,
                "system": system,
                "user": user,
                "output": resp,
                "finish_reason": finish_reason,
                "usage": response_data.get("usage", {}),
            }
            self.logger.debug("Full_response", artifact=response_log)

            return resp, finish_reason

        except Exception as e:
            self.logger.error(f"Error during AI inference: {str(e)}")
            raise

    @property
    def deployment_id(self):
        """
        デプロイメントID（Azure用）
        """
        return get_settings().get("OPENAI.DEPLOYMENT_ID", None)
