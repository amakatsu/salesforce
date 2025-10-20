#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
利用者トラッキング - メモリベース（シンプル版）
"""
from datetime import datetime
from typing import Dict, List

# グローバル変数で利用履歴を保持
_usage_history: List[Dict] = []


def track_usage(action: str, tool_name: str = "", username: str = "匿名"):
    """
    利用記録を追加

    Args:
        action: アクション名（例: "ホーム訪問", "実行ボタン押下"）
        tool_name: ツール名（例: "単語照合", "PR-Agent"）
        username: ユーザー名（デフォルト: 匿名）
    """
    global _usage_history

    record = {
        'action': action,
        'tool_name': tool_name,
        'username': username,
        'timestamp': datetime.now()
    }

    _usage_history.append(record)


def get_usage_stats() -> Dict:
    """
    利用統計を取得

    Returns:
        Dict: {
            'total_actions': 総アクション数,
            'history': 利用履歴リスト
        }
    """
    return {
        'total_actions': len(_usage_history),
        'history': _usage_history
    }


def clear_history():
    """利用履歴をクリア"""
    global _usage_history
    _usage_history = []
