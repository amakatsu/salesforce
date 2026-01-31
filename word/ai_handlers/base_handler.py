#!/usr/bin/env python3
"""
AIハンドラー基底クラス
共通ロジック（リトライ、ログ、エラーハンドリング）を提供
"""
import asyncio
import json
import aiohttp
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.config_loader import get_settings
from pr_agent.log import get_logger


class BaseCustomHandler(BaseAiHandler, ABC):
    """
    カスタムAIハンドラーの基底クラス
    リトライ、ログ出力、エラーハンドリングの共通ロジックを提供
    """

    def __init__(self):
        self.logger = get_logger()
        settings = get_settings()

        # 共通設定
        self.timeout = settings.config.get("ai_timeout", 120)
        self.max_retries = 5
        self.retry_delay = 5

        # サブクラスで初期化
        self._initialize(settings)

        self.logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def _initialize(self, settings) -> None:
        """プロバイダー固有の初期化"""
        pass

    @abstractmethod
    def _build_headers(self) -> Dict[str, str]:
        """HTTPリクエストヘッダーを構築"""
        pass

    @abstractmethod
    def _build_request_body(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 1.0,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """リクエストボディを構築"""
        pass

    @abstractmethod
    def _build_url(self, model: str = None) -> str:
        """APIエンドポイントURLを構築"""
        pass

    @abstractmethod
    def _parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """レスポンスを解析して(content, finish_reason)を返す"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """プロバイダー名を返す"""
        pass

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """ログ出力用に機密情報をマスク"""
        masked = {}
        sensitive_keys = ['key', 'token', 'secret', 'authorization']
        for key, value in headers.items():
            if any(token in key.lower() for token in sensitive_keys):
                masked[key] = '***'
            else:
                masked[key] = value
        return masked

    def _log_request(
        self,
        url: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
        model: str,
        temperature: float
    ) -> None:
        """LLMリクエストの概要をログ出力"""
        # max_tokensを取得
        max_tokens = body.get('max_completion_tokens') or body.get('max_tokens')
        if max_tokens is None:
            generation_cfg = body.get('generationConfig', {})
            if isinstance(generation_cfg, dict):
                max_tokens = generation_cfg.get('maxOutputTokens')

        request_summary = {
            'provider': self.provider_name,
            'url': url,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        self.logger.info(f"LLM request summary: {json.dumps(request_summary, ensure_ascii=False)}")

        sanitized_headers = self._mask_sensitive_headers(headers)
        self.logger.info(f"=== HTTP Request Details ===")
        self.logger.info(f"URL: {url}")
        self.logger.info(f"Headers: {json.dumps(sanitized_headers, ensure_ascii=False, indent=2)}")
        self.logger.info(f"Request Body (full):\n{json.dumps(body, ensure_ascii=False, indent=2)}")
        self.logger.info(f"===========================")

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
                            self._log_response(response.status, dict(response.headers), response_data)
                            return response_data

                        elif response.status == 429:
                            retry_after = self._get_retry_after(response, attempt)
                            self.logger.warning(
                                f"⚠️ Rate limit hit (429) on attempt {attempt + 1}/{self.max_retries}. "
                                f"Retrying after {retry_after}s"
                            )
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                error_text = await response.text()
                                raise Exception(f"Rate limit exceeded after {self.max_retries} retries: {error_text}")

                        else:
                            error_text = await response.text()
                            self.logger.error(f"API request failed: {response.status} - {error_text}")
                            raise Exception(f"API request failed: {response.status} - {error_text}")

            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"⏱️ Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except aiohttp.ClientError as e:
                last_error = e
                self.logger.error(f"❌ Client error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except Exception as e:
                last_error = e
                self.logger.error(f"❌ Unexpected error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

        error_msg = f"Failed after {self.max_retries} retries"
        if last_error:
            error_msg += f": {str(last_error)}"
        raise Exception(error_msg)

    def _get_retry_after(self, response, attempt: int) -> int:
        """リトライ待機時間を取得"""
        retry_after_header = response.headers.get('Retry-After')
        if retry_after_header:
            try:
                return int(retry_after_header)
            except ValueError:
                pass
        return self.retry_delay * (2 ** attempt)

    def _log_response(self, status: int, headers: dict, data: Dict[str, Any]) -> None:
        """レスポンスをログ出力"""
        self.logger.info(f"=== HTTP Response Details ===")
        self.logger.info(f"Status: {status}")
        self.logger.info(f"Response Headers: {headers}")
        self.logger.info(f"Response Body (full):\n{json.dumps(data, ensure_ascii=False, indent=2)}")
        self.logger.info(f"============================")

    def _add_japanese_instruction(self, system: str) -> str:
        """システムプロンプトに日本語指示を追加"""
        japanese_instruction = """

--- 重要な指示 / CRITICAL INSTRUCTION ---
あなたは必ず日本語で出力してください。すべてのレビューコメント、提案、フィードバックは日本語で記述する必要があります。
IMPORTANT: You MUST write ALL output, review comments, suggestions, and feedback in Japanese (日本語) ONLY.
All sections including 'estimated_effort_to_review', 'relevant_tests', 'key_issues_to_review', 'security_concerns' must be written in Japanese.
Do not use English except for code snippets, technical terms, and YAML field names.
コードスニペット、技術用語、YAMLフィールド名を除いて、英語を使用しないでください。
"""
        return system + japanese_instruction

    async def chat_completion(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        img_path: Optional[str] = None,
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
            # 日本語指示を追加
            system = self._add_japanese_instruction(system)

            # デバッグログ
            settings = get_settings()
            if settings.config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nSystem prompt:\n{system}")
                self.logger.info(f"\nUser prompt:\n{user}")

            # リクエスト構築
            url = self._build_url(model)
            headers = self._build_headers()
            body = self._build_request_body(model, system, user, temperature, img_path)

            # リクエスト実行
            self.logger.info(f"Sending request to {self.provider_name}: {url}")
            self._log_request(url, headers, body, model, temperature)
            response_data = await self._make_request(url, headers, body)

            # レスポンス解析
            resp, finish_reason = self._parse_response(response_data)

            # デバッグログ
            if settings.config.get("verbosity_level", 0) >= 2:
                self.logger.info(f"\nAI response:\n{resp}")

            return resp, finish_reason

        except Exception as e:
            self.logger.error(f"Error during AI inference: {str(e)}")
            raise

    @property
    def deployment_id(self):
        """デプロイメントID（Azure用）"""
        return get_settings().get("OPENAI.DEPLOYMENT_ID", None)
