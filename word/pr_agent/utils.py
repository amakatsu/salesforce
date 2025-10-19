#!/usr/bin/env python3
"""
PR-Agent ユーティリティモジュール
カラー出力とロギング機能
"""


class Colors:
    """ANSI色コード定数"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Logger:
    """カラー出力付きロガー"""

    @staticmethod
    def print_colored(message: str, color: str = Colors.WHITE) -> None:
        """色付きメッセージを出力"""
        print(f"{color}{message}{Colors.END}")

    @staticmethod
    def success(message: str) -> None:
        """成功メッセージ"""
        Logger.print_colored(f"✅ {message}", Colors.GREEN)

    @staticmethod
    def error(message: str) -> None:
        """エラーメッセージ"""
        Logger.print_colored(f"❌ {message}", Colors.RED)

    @staticmethod
    def warning(message: str) -> None:
        """警告メッセージ"""
        Logger.print_colored(f"⚠️  {message}", Colors.YELLOW)

    @staticmethod
    def info(message: str) -> None:
        """情報メッセージ"""
        Logger.print_colored(f"📄 {message}", Colors.CYAN)

    @staticmethod
    def debug(message: str) -> None:
        """デバッグメッセージ"""
        Logger.print_colored(f"🔍 {message}", Colors.BLUE)
