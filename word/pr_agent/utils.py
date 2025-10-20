#!/usr/bin/env python3
"""
PR-Agent ユーティリティモジュール
カラー出力とロギング機能
"""
import os
import logging


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

    # デバッグレベル（環境変数 DEBUG_LEVEL で設定可能）
    # 0: エラーのみ
    # 1: エラー + 警告 + 情報（デフォルト）
    # 2: 上記 + デバッグ
    # 3: 上記 + HTTPリクエスト詳細
    DEBUG_LEVEL = int(os.getenv('DEBUG_LEVEL', '1'))

    @staticmethod
    def set_debug_level(level: int) -> None:
        """デバッグレベルを設定"""
        Logger.DEBUG_LEVEL = level
        Logger.info(f"デバッグレベルを {level} に設定しました")

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
        """エラーメッセージ（常に表示）"""
        Logger.print_colored(f"❌ {message}", Colors.RED)

    @staticmethod
    def warning(message: str) -> None:
        """警告メッセージ（DEBUG_LEVEL >= 1）"""
        if Logger.DEBUG_LEVEL >= 1:
            Logger.print_colored(f"⚠️  {message}", Colors.YELLOW)

    @staticmethod
    def info(message: str) -> None:
        """情報メッセージ（DEBUG_LEVEL >= 1）"""
        if Logger.DEBUG_LEVEL >= 1:
            Logger.print_colored(f"📄 {message}", Colors.CYAN)

    @staticmethod
    def debug(message: str) -> None:
        """デバッグメッセージ（DEBUG_LEVEL >= 2）"""
        if Logger.DEBUG_LEVEL >= 2:
            Logger.print_colored(f"🔍 {message}", Colors.BLUE)

    @staticmethod
    def http_request(method: str, url: str, headers: dict = None, body: str = None) -> None:
        """HTTPリクエスト詳細（DEBUG_LEVEL >= 3）"""
        if Logger.DEBUG_LEVEL >= 3:
            Logger.print_colored(f"\n{'='*80}", Colors.PURPLE)
            Logger.print_colored(f"🌐 HTTP Request: {method} {url}", Colors.PURPLE)

            if headers:
                Logger.print_colored("📋 Headers:", Colors.CYAN)
                for key, value in headers.items():
                    # 認証情報をマスク
                    if key.lower() in ['authorization', 'private-token', 'api-key']:
                        masked_value = value[:10] + '***' if len(value) > 10 else '***'
                        Logger.print_colored(f"  {key}: {masked_value}", Colors.WHITE)
                    else:
                        Logger.print_colored(f"  {key}: {value}", Colors.WHITE)

            if body:
                Logger.print_colored("📦 Body:", Colors.CYAN)
                # JSONの場合は整形して表示
                try:
                    import json
                    formatted = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
                    # 長すぎる場合は切り詰め
                    if len(formatted) > 1000:
                        formatted = formatted[:1000] + "\n... (truncated)"
                    Logger.print_colored(formatted, Colors.WHITE)
                except:
                    # JSON以外の場合はそのまま表示
                    display_body = body[:500] + "... (truncated)" if len(body) > 500 else body
                    Logger.print_colored(f"  {display_body}", Colors.WHITE)

            Logger.print_colored(f"{'='*80}\n", Colors.PURPLE)

    @staticmethod
    def http_response(status_code: int, headers: dict = None, body: str = None) -> None:
        """HTTPレスポンス詳細（DEBUG_LEVEL >= 3）"""
        if Logger.DEBUG_LEVEL >= 3:
            color = Colors.GREEN if 200 <= status_code < 300 else Colors.RED
            Logger.print_colored(f"\n{'='*80}", Colors.PURPLE)
            Logger.print_colored(f"📥 HTTP Response: {status_code}", color)

            if headers:
                Logger.print_colored("📋 Headers:", Colors.CYAN)
                for key, value in list(headers.items())[:10]:  # 最初の10個のみ表示
                    Logger.print_colored(f"  {key}: {value}", Colors.WHITE)

            if body:
                Logger.print_colored("📦 Body:", Colors.CYAN)
                try:
                    import json
                    formatted = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
                    if len(formatted) > 1000:
                        formatted = formatted[:1000] + "\n... (truncated)"
                    Logger.print_colored(formatted, Colors.WHITE)
                except:
                    display_body = body[:500] + "... (truncated)" if len(body) > 500 else body
                    Logger.print_colored(f"  {display_body}", Colors.WHITE)

            Logger.print_colored(f"{'='*80}\n", Colors.PURPLE)
