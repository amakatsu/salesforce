#!/usr/bin/env python3
"""
カスタムAIハンドラー - 後方互換ラッパー

このモジュールは後方互換性のために維持されています。
新規コードでは以下を使用してください:
    from word.ai_handlers import create_ai_handler, OpenAIHandler, GeminiHandler
"""
import os
from typing import Tuple, Optional

from pr_agent.config_loader import get_settings
from pr_agent.log import get_logger

from .openai_handler import OpenAIHandler
from .gemini_handler import GeminiHandler


class CustomAzureAIHandler:
    """
    後方互換用ラッパークラス

    プロバイダーに応じてOpenAIHandler/GeminiHandlerに委譲する。
    既存コードからの呼び出しを維持するためのクラス。

    新規コードでは create_ai_handler() または
    OpenAIHandler/GeminiHandler を直接使用してください。
    """

    def __init__(self):
        self.logger = get_logger()
        settings = get_settings()

        # プロバイダー判定
        self.provider = (
            os.getenv("AI_PROVIDER", "").lower() or
            settings.config.get("ai_provider", "openai").lower()
        )
        self.logger.info(f"CustomAzureAIHandler: provider={self.provider}")

        # 適切なハンドラーをインスタンス化
        if self.provider == "google":
            self._handler = GeminiHandler()
        else:
            self._handler = OpenAIHandler()

    async def chat_completion(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        img_path: Optional[str] = None,
        _locale_retry: bool = False
    ) -> Tuple[str, str]:
        """チャット補完を実行（委譲）"""
        if self.provider == "google":
            return await self._handler.chat_completion(
                model, system, user, temperature, img_path, _locale_retry
            )
        else:
            return await self._handler.chat_completion(
                model, system, user, temperature, img_path
            )

    @property
    def deployment_id(self):
        """デプロイメントID（Azure用）"""
        return self._handler.deployment_id
