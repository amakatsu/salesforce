#!/usr/bin/env python3
"""
PR-Agent パッケージ
PR-Agentのカスタム実行ツールのコアモジュール群

モジュール構成:
- utils: 色付きログ出力ユーティリティ (Colors, Logger)
- config: TOML設定ファイル管理 (ConfigManager)
- validators: URL検証 (UrlValidator)
- runner: PR-Agent実行ロジック (PRAgentRunner)
"""

from .utils import Colors, Logger
from .config import ConfigManager
from .config_repository import (
    ConfigRepository,
    ConfigConflictError,
    ConfigFileInfo,
    SaveResult,
)
from .validators import UrlValidator
from .runner import PRAgentRunner

__all__ = [
    'Colors',
    'Logger',
    'ConfigManager',
    'UrlValidator',
    'PRAgentRunner',
    'ConfigRepository',
    'ConfigConflictError',
    'ConfigFileInfo',
    'SaveResult',
]

__version__ = '2.0.0'
