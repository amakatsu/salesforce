#!/usr/bin/env python3
"""
カスタムAIハンドラー - OpenAI/Gemini統合版
litellmをバイパスして、独自のHTTPリクエストでAzure OpenAI/Gemini APIを呼び出す
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
    OpenAI/Gemini統合カスタムAIハンドラー
    litellmを使わずに直接HTTPリクエストを送信
    プロバイダーは設定から自動判定
    """

    def __init__(self):
        """
        AI API設定を初期化
        """
        self.logger = get_logger()
        settings = get_settings()

        # プロバイダー判定（環境変数を優先、次に設定ファイル）
        self.provider = (
            os.getenv("AI_PROVIDER", "").lower() or
            settings.config.get("ai_provider", "openai").lower()
        )
        self.logger.info(f"AI Provider detected: {self.provider}")
        self.logger.info(f"AI Provider from env: {os.getenv('AI_PROVIDER', 'N/A')}")
        self.logger.info(f"AI Provider from config: {settings.config.get('ai_provider', 'N/A')}")

        if self.provider == "google":
            self._init_gemini(settings)
        else:
            self._init_openai(settings)

        # 共通設定
        self.timeout = settings.config.get("ai_timeout", 120)
        self.max_retries = 3
        self.retry_delay = 2

        self.logger.info(f"CustomAIHandler initialized: provider={self.provider}")

    def _init_openai(self, settings):
        """OpenAI (Azure) 設定を初期化"""
        # API Base URL (複数のキーを試行)
        self.api_base = (
            settings.get("openai.api_base") or
            settings.get("OPENAI.API_BASE") or
            os.getenv("OPENAI_BASE_URL", "")
        )
        if not self.api_base:
            raise ValueError("openai.api_base or OPENAI_BASE_URL is required")

        # API Key (複数のキーを試行)
        self.api_key = (
            settings.get("openai.key") or
            settings.get("OPENAI.KEY") or
            os.getenv("OPENAI_API_KEY", "")
        )
        if not self.api_key:
            raise ValueError("openai.key or OPENAI_API_KEY is required")

        # User ID (Azure APIM用)
        self.user_id = (
            settings.get("openai.user_id") or
            settings.get("OPENAI.USER_ID") or
            os.getenv("APIM_USER_ID", "")
        )

        # API Path
        self.api_path = (
            settings.get("openai.path") or
            settings.get("OPENAI.PATH") or
            os.getenv("OPENAI_PATH", "/chat/completions")
        )

        # カスタムヘッダー（設定ファイルから取得）
        self.custom_headers = settings.get("config.custom_headers", {})

        self.logger.info(f"OpenAI initialized: base_url={self.api_base}")

    def _init_gemini(self, settings):
        """Gemini設定を初期化"""
        # API Key (複数のキーを試行)
        self.api_key = (
            settings.get("gemini.key") or
            settings.config.get("gemini_key") or
            settings.get("GEMINI.KEY") or
            os.getenv("GEMINI_API_KEY", "")
        )
        if not self.api_key:
            raise ValueError("gemini.key or GEMINI_API_KEY is required")

        # Gemini API Base URL
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"

        # モデル名を取得（環境変数を優先）
        self.model = (
            os.getenv("GEMINI_MODEL", "") or
            settings.config.get("model", "gemini-2.0-flash-exp")
        )
        # "gemini/" プレフィックスを削除
        if self.model.startswith("gemini/"):
            self.model = self.model.replace("gemini/", "")

        self.logger.info(f"Gemini initialized: model={self.model}")
        self.logger.info(f"Gemini model from env: {os.getenv('GEMINI_MODEL', 'N/A')}")

    def _build_headers_openai(self) -> Dict[str, str]:
        """OpenAI用HTTPリクエストヘッダーを構築"""
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
            if hasattr(self, 'user_id') and self.user_id:
                headers["apim-user-id"] = self.user_id

        return headers

    def _build_headers_gemini(self) -> Dict[str, str]:
        """Gemini用HTTPリクエストヘッダーを構築"""
        return {
            "Content-Type": "application/json",
        }

    def _build_request_body_openai(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """OpenAI用リクエストボディを構築"""
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

    def _build_request_body_gemini(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gemini用リクエストボディを構築"""
        # Gemini APIはsystem instructionとcontentsを分離
        contents = [
            {
                "role": "user",
                "parts": [{"text": f"{system}\n\n{user}"}]
            }
        ]

        # 画像がある場合（Gemini Vision）
        if img_path:
            # 実装が必要な場合は追加
            self.logger.warning("Image input not yet implemented for Gemini")

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": get_settings().config.get("max_model_tokens", 8192),
            }
        }

        return body

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """ログ出力用に機密情報をマスク"""
        masked = {}
        for key, value in headers.items():
            if any(token in key.lower() for token in ['key', 'token', 'secret', 'authorization']):
                masked[key] = '***'
            else:
                masked[key] = value
        return masked

    def _log_request(self, provider: str, url: str, headers: Dict[str, str], body: Dict[str, Any], model: str, temperature: float) -> None:
        """LLMリクエストの概要をログ出力"""
        max_tokens = body.get('max_tokens') if isinstance(body, dict) else None
        if max_tokens is None and isinstance(body, dict):
            generation_cfg = body.get('generationConfig', {})
            if isinstance(generation_cfg, dict):
                max_tokens = generation_cfg.get('maxOutputTokens')

        request_summary = {
            'provider': provider,
            'url': url,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        try:
            summary_json = json.dumps(request_summary, ensure_ascii=False)
        except TypeError:
            summary_json = str(request_summary)
        self.logger.info(f"LLM request summary: {summary_json}")

        sanitized_headers = self._mask_sensitive_headers(headers)
        self.logger.debug(
            'LLM request payload',
            artifact={
                'headers': sanitized_headers,
                'body': body,
            }
        )

    async def _make_request(
        self,
        url: str,
        headers: Dict[str, str],
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """非同期HTTPリクエストを実行（リトライ機能付き）"""
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

    def _parse_openai_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """OpenAIレスポンスを解析"""
        if not response_data.get("choices"):
            raise Exception("No choices in response")

        choice = response_data["choices"][0]
        resp = choice["message"]["content"]
        finish_reason = choice.get("finish_reason", "stop")

        return resp, finish_reason

    def _parse_gemini_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """Geminiレスポンスを解析"""
        if not response_data.get("candidates"):
            raise Exception("No candidates in response")

        candidate = response_data["candidates"][0]

        # contentからtextを抽出
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise Exception("No parts in candidate content")

        resp = parts[0].get("text", "")
        finish_reason = candidate.get("finishReason", "STOP")

        return resp, finish_reason

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
            # デバッグログ
            self.logger.debug("Prompts", artifact={"system": system, "user": user})
            if get_settings().config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nSystem prompt:\n{system}")
                self.logger.info(f"\nUser prompt:\n{user}")

            if self.provider == "google":
                # Gemini API
                url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"
                headers = self._build_headers_gemini()
                body = self._build_request_body_gemini(system, user, temperature, img_path)

                self.logger.info(f"Sending request to Gemini: {self.model}")
                self._log_request(self.provider, url, headers, body, self.model, temperature)
                response_data = await self._make_request(url, headers, body)
                resp, finish_reason = self._parse_gemini_response(response_data)

            else:
                # OpenAI API (Azure)
                url = self.api_base.rstrip('/') + self.api_path
                headers = self._build_headers_openai()
                body = self._build_request_body_openai(model, system, user, temperature, img_path)

                self.logger.info(f"Sending request to OpenAI: {url}")
                self._log_request(self.provider, url, headers, body, model, temperature)
                response_data = await self._make_request(url, headers, body)
                resp, finish_reason = self._parse_openai_response(response_data)

            # デバッグログ
            self.logger.debug(f"\nAI response:\n{resp}")
            if get_settings().config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nAI response:\n{resp}")

            # 詳細ログ
            response_log = {
                "provider": self.provider,
                "model": model if self.provider != "google" else self.model,
                "system": system,
                "user": user,
                "output": resp,
                "finish_reason": finish_reason,
                "usage": response_data.get("usage", response_data.get("usageMetadata", {})),
            }
            self.logger.debug("Full_response", artifact=response_log)

            return resp, finish_reason

        except Exception as e:
            self.logger.error(f"Error during AI inference: {str(e)}")
            raise

    @property
    def deployment_id(self):
        """デプロイメントID（Azure用）"""
        if self.provider == "google":
            return None
        return get_settings().get("OPENAI.DEPLOYMENT_ID", None)
