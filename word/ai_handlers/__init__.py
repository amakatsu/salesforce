"""
カスタムAIハンドラー
PR-Agentで使用する独自のHTTPリクエストハンドラー

クラス構成:
    BaseCustomHandler  - 基底クラス（リトライ、ログ等の共通処理）
    ├── OpenAIHandler  - OpenAI/Azure/GPT-5 Cline Proxy
    └── GeminiHandler  - Google Gemini

使用例:
    # ファクトリーで自動選択
    handler = create_ai_handler()

    # 明示的にプロバイダー指定
    handler = create_ai_handler(provider="openai")
    handler = create_ai_handler(provider="google")

    # 後方互換 (CustomAzureAIHandler)
    handler = CustomAzureAIHandler()
"""
import os
from pr_agent.config_loader import get_settings

from .base_handler import BaseCustomHandler
from .openai_handler import OpenAIHandler
from .gemini_handler import GeminiHandler
from .custom_ai_handler import CustomAzureAIHandler


def create_ai_handler(provider: str = None) -> BaseCustomHandler:
    """
    AIハンドラーのファクトリー関数

    Args:
        provider: プロバイダー名 ("openai", "google")
                  指定しない場合は環境変数/設定から自動判定

    Returns:
        BaseCustomHandler: プロバイダーに応じたハンドラーインスタンス
    """
    if provider is None:
        # 環境変数を優先、次に設定ファイル
        provider = (
            os.getenv("AI_PROVIDER", "").lower() or
            get_settings().config.get("ai_provider", "openai").lower()
        )

    if provider == "google" or provider == "gemini":
        return GeminiHandler()
    else:
        return OpenAIHandler()


__all__ = [
    'BaseCustomHandler',
    'OpenAIHandler',
    'GeminiHandler',
    'CustomAzureAIHandler',  # 後方互換
    'create_ai_handler',
]
