#!/usr/bin/env python3
"""
PR-Agent ユーティリティモジュール
カラー出力とロギング機能
"""
import os
import logging
import threading
from typing import Optional, List, Dict
from datetime import datetime


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


class SessionLogBuffer:
    """セッションごとのログバッファ"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logs: List[Dict] = []
        self.lock = threading.Lock()

    def add_log(self, level: str, message: str, color: str):
        """ログエントリを追加"""
        with self.lock:
            self.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'color': color
            })

    def get_logs(self) -> List[Dict]:
        """ログエントリを取得"""
        with self.lock:
            return self.logs.copy()

    def clear(self):
        """ログをクリア"""
        with self.lock:
            self.logs.clear()


class Logger:
    """セッション対応カラー出力付きロガー"""

    # デバッグレベル（環境変数 DEBUG_LEVEL で設定可能）
    # 0: エラーのみ
    # 1: エラー + 警告 + 情報（デフォルト）
    # 2: 上記 + デバッグ
    # 3: 上記 + HTTPリクエスト詳細
    DEBUG_LEVEL = int(os.getenv('DEBUG_LEVEL', '1'))

    # セッションログバッファ（スレッドローカル）
    _local = threading.local()
    _buffers: Dict[str, SessionLogBuffer] = {}
    _buffers_lock = threading.Lock()

    @staticmethod
    def set_session(session_id: Optional[str] = None) -> None:
        """現在のスレッドにセッションIDを設定"""
        Logger._local.session_id = session_id
        if session_id:
            with Logger._buffers_lock:
                if session_id not in Logger._buffers:
                    Logger._buffers[session_id] = SessionLogBuffer(session_id)

    @staticmethod
    def get_session_id() -> Optional[str]:
        """現在のスレッドのセッションIDを取得"""
        return getattr(Logger._local, 'session_id', None)

    @staticmethod
    def get_session_logs(session_id: str) -> List[Dict]:
        """指定セッションのログを取得"""
        with Logger._buffers_lock:
            if session_id in Logger._buffers:
                return Logger._buffers[session_id].get_logs()
            return []

    @staticmethod
    def clear_session_logs(session_id: str) -> None:
        """指定セッションのログをクリア"""
        with Logger._buffers_lock:
            if session_id in Logger._buffers:
                Logger._buffers[session_id].clear()

    @staticmethod
    def set_debug_level(level: int) -> None:
        """デバッグレベルを設定"""
        Logger.DEBUG_LEVEL = level

    @staticmethod
    def _log_to_buffer(level: str, message: str, color: str) -> None:
        """セッションバッファにログを追加"""
        session_id = Logger.get_session_id()
        if session_id:
            with Logger._buffers_lock:
                if session_id in Logger._buffers:
                    Logger._buffers[session_id].add_log(level, message, color)

    @staticmethod
    def print_colored(message: str, color: str = Colors.WHITE) -> None:
        """色付きメッセージを出力"""
        print(f"{color}{message}{Colors.END}")

    @staticmethod
    def success(message: str) -> None:
        """成功メッセージ"""
        formatted = f"✅ {message}"
        Logger._log_to_buffer('SUCCESS', formatted, Colors.GREEN)
        Logger.print_colored(formatted, Colors.GREEN)

    @staticmethod
    def error(message: str) -> None:
        """エラーメッセージ（常に表示）"""
        formatted = f"❌ {message}"
        Logger._log_to_buffer('ERROR', formatted, Colors.RED)
        Logger.print_colored(formatted, Colors.RED)

    @staticmethod
    def warning(message: str) -> None:
        """警告メッセージ（DEBUG_LEVEL >= 1）"""
        if Logger.DEBUG_LEVEL >= 1:
            formatted = f"⚠️  {message}"
            Logger._log_to_buffer('WARNING', formatted, Colors.YELLOW)
            Logger.print_colored(formatted, Colors.YELLOW)

    @staticmethod
    def info(message: str) -> None:
        """情報メッセージ（DEBUG_LEVEL >= 1）"""
        if Logger.DEBUG_LEVEL >= 1:
            formatted = f"📄 {message}"
            Logger._log_to_buffer('INFO', formatted, Colors.CYAN)
            Logger.print_colored(formatted, Colors.CYAN)

    @staticmethod
    def debug(message: str) -> None:
        """デバッグメッセージ（DEBUG_LEVEL >= 2）"""
        if Logger.DEBUG_LEVEL >= 2:
            formatted = f"🔍 {message}"
            Logger._log_to_buffer('DEBUG', formatted, Colors.BLUE)
            Logger.print_colored(formatted, Colors.BLUE)

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
