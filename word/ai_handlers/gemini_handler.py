#!/usr/bin/env python3
"""
Google Gemini ハンドラー
"""
import os
import re
from typing import Tuple, Optional, Dict, Any

from pr_agent.config_loader import get_settings

from .base_handler import BaseCustomHandler


class GeminiHandler(BaseCustomHandler):
    """
    Google Gemini API対応ハンドラー

    設定例:
        - GEMINI_API_KEY: your-api-key
        - model: gemini-2.0-flash-exp
    """

    @property
    def provider_name(self) -> str:
        return "google"

    def _initialize(self, settings) -> None:
        """Gemini設定を初期化"""
        # API Key
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

        # モデル名
        self.model = (
            os.getenv("GEMINI_MODEL", "") or
            settings.config.get("model", "gemini-2.0-flash-exp")
        )
        # "gemini/" プレフィックスを削除
        if self.model.startswith("gemini/"):
            self.model = self.model.replace("gemini/", "")

        self.logger.info(f"Gemini initialized: model={self.model}")

    def _build_url(self, model: str = None) -> str:
        """APIエンドポイントURLを構築"""
        actual_model = model or self.model
        # gemini/ プレフィックスを削除
        if actual_model.startswith("gemini/"):
            actual_model = actual_model.replace("gemini/", "")
        return f"{self.api_base}/models/{actual_model}:generateContent?key={self.api_key}"

    def _build_headers(self) -> Dict[str, str]:
        """HTTPリクエストヘッダーを構築"""
        return {"Content-Type": "application/json"}

    def _build_request_body(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 1.0,
        img_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gemini用リクエストボディを構築"""
        # Gemini APIはsystem instructionを専用フィールドで受け付ける
        system_instruction = {"role": "system", "parts": [{"text": system}]}
        user_parts = [{"text": user}]

        # 画像がある場合（未実装）
        if img_path:
            self.logger.warning("Image input not yet implemented for Gemini")

        settings = get_settings()
        # PR-Agent設定(common.toml)から取得。未設定時は128000をフォールバック
        max_tokens = settings.config.get("max_model_tokens", 128000)

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
                "maxOutputTokens": max_tokens,
            }
        }

        return body

    def _parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, str]:
        """Geminiレスポンスを解析"""
        if not response_data.get("candidates"):
            raise Exception("No candidates in response")

        candidate = response_data["candidates"][0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            raise Exception("No parts in candidate content")

        text = parts[0].get("text", "")
        finish_reason = candidate.get("finishReason", "STOP")

        return text, finish_reason

    @staticmethod
    def _contains_japanese(text: str) -> bool:
        """日本語(ひらがな・カタカナ・漢字)が含まれるか判定"""
        if not text:
            return False
        return bool(re.search(r'[\u3040-\u30ff\u31f0-\u31ff\u4e00-\u9faf]', text))

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
        チャット補完を実行（日本語リトライ対応）
        """
        resp, finish_reason = await super().chat_completion(
            model, system, user, temperature, img_path
        )

        # 日本語が含まれていない場合、リトライ
        if not self._contains_japanese(resp) and not _locale_retry:
            self.logger.warning("Gemini response may not contain Japanese characters. Retrying...")
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

        return resp, finish_reason

    @property
    def deployment_id(self):
        """GeminiにはデプロイメントIDはない"""
        return None
