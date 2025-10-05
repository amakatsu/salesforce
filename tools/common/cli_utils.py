#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI ユーティリティ共通モジュール
GUI・パス解決などのヘルパー関数
"""
import sys
from pathlib import Path
from typing import Optional


def app_root() -> Path:
    """アプリケーションルートディレクトリを取得"""
    if getattr(sys, "frozen", False):
        # PyInstallerでビルドされた場合
        return Path(sys.executable).parent
    else:
        # 通常のPython実行時
        return Path(__file__).parent.parent


def ask_directory(title: str, initial: Optional[str] = None) -> Optional[str]:
    """
    GUIダイアログでディレクトリを選択

    Args:
        title: ダイアログのタイトル
        initial: 初期ディレクトリ

    Returns:
        選択されたディレクトリパス（キャンセル時はNone）
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        path = filedialog.askdirectory(title=title, initialdir=initial)
        root.destroy()
        return path or None
    except:
        return None
