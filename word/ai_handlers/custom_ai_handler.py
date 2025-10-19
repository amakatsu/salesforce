#!/usr/bin/env python3
"""
カスタムAIハンドラー - OpenAI/Gemini統合版
litellmをバイパスして、独自のHTTPリクエストでAzure OpenAI/Gemini APIを呼び出す
"""
import os
import json
import asyncio
import aiohttp
import re
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
        # レート制限対策：リトライ回数と待機時間を増やす
        self.max_retries = 10  # 3 → 10に増加
        self.retry_delay = 5   # 2 → 5秒に増加（初回待機時間）

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

        # OPENAI_HEADERS_JSONからapi-keyとapim-user-idを抽出
        headers_json_str = os.getenv("OPENAI_HEADERS_JSON", "")
        parsed_headers = {}
        if headers_json_str:
            try:
                parsed_headers = json.loads(headers_json_str)
                self.logger.info(f"Parsed OPENAI_HEADERS_JSON: {list(parsed_headers.keys())}")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse OPENAI_HEADERS_JSON: {e}")

        # API Key (複数のキーを試行)
        self.api_key = (
            settings.get("openai.key") or
            settings.get("OPENAI.KEY") or
            os.getenv("OPENAI_API_KEY", "") or
            parsed_headers.get("api-key", "")
        )
        if not self.api_key:
            raise ValueError("openai.key or OPENAI_API_KEY or OPENAI_HEADERS_JSON['api-key'] is required")

        # User ID (Azure APIM用)
        self.user_id = (
            settings.get("openai.user_id") or
            settings.get("OPENAI.USER_ID") or
            os.getenv("APIM_USER_ID", "") or
            parsed_headers.get("apim-user-id", "")
        )

        # API Path
        self.api_path = (
            settings.get("openai.path") or
            settings.get("OPENAI.PATH") or
            os.getenv("OPENAI_PATH", "/chat/completions")
        )

        # カスタムヘッダー（設定ファイルから取得）
        self.custom_headers = settings.get("config.custom_headers", {})

        self.logger.info(f"OpenAI initialized: base_url={self.api_base}, has_api_key={bool(self.api_key)}, has_user_id={bool(self.user_id)}")

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
        # Gemini APIはsystem instructionを専用フィールドで受け付ける
        system_instruction = {"role": "system", "parts": [{"text": system}]}
        user_parts = [{"text": user}]

        # 画像がある場合（Gemini Vision）
        if img_path:
            self.logger.warning("Image input not yet implemented for Gemini")

        body = {
            "systemInstruction": system_instruction,
            "contents": [
                {
                    "role": "user",
                    "parts": user_parts,
                }
            ],
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

        # HTTPリクエストの詳細をINFOレベルで出力（画面に表示されるように）
        self.logger.info(f"=== HTTP Request Details ===")
        self.logger.info(f"URL: {url}")
        self.logger.info(f"Headers: {json.dumps(sanitized_headers, ensure_ascii=False, indent=2)}")
        # リクエストボディを全文表示
        request_body_json = json.dumps(body, ensure_ascii=False, indent=2)
        self.logger.info(f"Request Body (full):\n{request_body_json}")
        self.logger.info(f"===========================")

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
        """非同期HTTPリクエストを実行（リトライ機能付き・エクスポネンシャルバックオフ）"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"API request attempt {attempt + 1}/{self.max_retries}")
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=body) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            # レスポンスの詳細をINFOレベルで出力
                            self.logger.info(f"=== HTTP Response Details ===")
                            self.logger.info(f"Status: {response.status}")
                            self.logger.info(f"Response Headers: {dict(response.headers)}")
                            # レスポンスボディを全文表示
                            response_body_json = json.dumps(response_data, ensure_ascii=False, indent=2)
                            self.logger.info(f"Response Body (full):\n{response_body_json}")
                            self.logger.info(f"============================")
                            return response_data
                        elif response.status == 429:
                            # Rate limit - エクスポネンシャルバックオフでリトライ
                            retry_after_header = response.headers.get('Retry-After')
                            if retry_after_header:
                                try:
                                    retry_after = int(retry_after_header)
                                except ValueError:
                                    retry_after = self.retry_delay * (2 ** attempt)
                            else:
                                # エクスポネンシャルバックオフ: 5, 10, 20, 40, 80... 秒
                                retry_after = self.retry_delay * (2 ** attempt)

                            self.logger.warning(
                                f"⚠️ Rate limit hit (429) on attempt {attempt + 1}/{self.max_retries}. "
                                f"Retrying after {retry_after}s (exponential backoff)"
                            )

                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                error_text = await response.text()
                                last_error = Exception(f"Rate limit exceeded after {self.max_retries} retries: {error_text}")
                                raise last_error
                        else:
                            error_text = await response.text()
                            self.logger.error(f"API request failed: {response.status} - {error_text}")
                            last_error = Exception(f"API request failed: {response.status} - {error_text}")
                            raise last_error

            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"⏱️ Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    backoff_time = self.retry_delay * (attempt + 1)
                    self.logger.info(f"Retrying after {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise

            except aiohttp.ClientError as e:
                last_error = e
                self.logger.error(f"❌ Client error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = self.retry_delay * (attempt + 1)
                    self.logger.info(f"Retrying after {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise

            except Exception as e:
                last_error = e
                self.logger.error(f"❌ Unexpected error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = self.retry_delay * (attempt + 1)
                    self.logger.info(f"Retrying after {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise

        # すべてのリトライが失敗した場合
        error_msg = f"Failed after {self.max_retries} retries"
        if last_error:
            error_msg += f": {str(last_error)}"
        raise Exception(error_msg)

    def _parse_openai_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """OpenAIレスポンスを解析"""
        if not response_data.get("choices"):
            raise Exception("No choices in response")

        choice = response_data["choices"][0]
        resp = choice["message"]["content"]
        finish_reason = choice.get("finish_reason", "stop")

        return resp, finish_reason


    @staticmethod
    def _contains_japanese(text: str) -> bool:
        """日本語(ひらがな・カタカナ・漢字)が含まれるか判定"""
        if not text:
            return False
        return bool(re.search(r'[\u3040-\u30ff\u31f0-\u31ff\u4e00-\u9faf]', text))

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
        img_path: Optional[str] = None,
        _locale_retry: bool = False
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
            # システムプロンプトに日本語指示を追加（PR-Agentのextra_instructionsが反映されない問題への対応）
            japanese_instruction = """

--- 重要な指示 / CRITICAL INSTRUCTION ---
あなたは必ず日本語で出力してください。すべてのレビューコメント、提案、フィードバックは日本語で記述する必要があります。
IMPORTANT: You MUST write ALL output, review comments, suggestions, and feedback in Japanese (日本語) ONLY.
All sections including 'estimated_effort_to_review', 'relevant_tests', 'key_issues_to_review', 'security_concerns' must be written in Japanese.
Do not use English except for code snippets, technical terms, and YAML field names.
コードスニペット、技術用語、YAMLフィールド名を除いて、英語を使用しないでください。
"""
            system = system + japanese_instruction

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
                if not self._contains_japanese(resp):
                    self.logger.warning("Gemini response may not contain Japanese characters.")
                    if not _locale_retry:
                        reinforce = (
                            "\nIMPORTANT: これ以降の出力はすべて日本語で行ってください。"
                            "英語で回答してはいけません。必ず日本語で丁寧に説明してください。"
                        )
                        return await self.chat_completion(
                            model,
                            system + reinforce,
                            user,
                            temperature,
                            img_path,
                            _locale_retry=True
                        )

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
