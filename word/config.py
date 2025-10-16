from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)

try:
    import tkinter as tk  # type: ignore
    from tkinter import filedialog, messagebox  # type: ignore

    TK_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    TK_AVAILABLE = False
    tk = None  # type: ignore
    filedialog = None  # type: ignore
    messagebox = None  # type: ignore

HARD_EXACT_SCORE = 1.0
FALLBACK_EXACT_FLOOR = 0.95

DEFAULT_CONFIG: Dict[str, Any] = {
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:53000/api/curl/v1/chat/"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "OPENAI_PATH": os.getenv("OPENAI_PATH", "/chat/completions"),
    "OPENAI_HEADERS_JSON": os.getenv(
        "OPENAI_HEADERS_JSON",
        '{"api-key":"QXwXLlZijq1U8WwiYfIu3znm3wWK3qIG","apim-user-id":"PIT03077"}',
    ),
    "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", "false").lower() != "false",
    "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "true").lower() != "false",
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "800")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
    "TOP_P": float(os.getenv("TOP_P", "0.95")),
    "PRESENCE_PENALTY": float(os.getenv("PRESENCE_PENALTY", "0.0")),
    "FREQUENCY_PENALTY": float(os.getenv("FREQUENCY_PENALTY", "0.0")),
    "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
    "VOCAB_GLOB": os.getenv("VOCAB_GLOB", "*単語名一覧*.xlsx"),
    "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "*"),
    "VOCAB_SHEET": os.getenv("VOCAB_SHEET", "*"),
    "SCREEN_COL": os.getenv("SCREEN_COL", "項目名称"),
    "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "論理名"),
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名（正式名称）,物理名"),
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
    "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "No,#"),
    "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),
    "TOP_K": int(os.getenv("TOP_K", "3")),
    "OUT_DIR": os.getenv("OUT_DIR", "out"),
    "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
    "RETRY": int(os.getenv("RETRY", "30")),
    "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),
}


def load_runtime_env() -> None:
    """Load .env in the current working directory if present."""

    load_dotenv()


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def ask_directory(title: str, initial: Optional[str] = None) -> Optional[str]:
    if not TK_AVAILABLE:
        return None
    try:  # pragma: no cover - GUI interaction
        root = tk.Tk()  # type: ignore[call-arg]
        root.withdraw()
        path = filedialog.askdirectory(title=title, initialdir=initial or str(app_root()))  # type: ignore[arg-type]
        root.destroy()
        return path or None
    except Exception:
        return None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Excel 単語照合（LLM 補助）")
    parser.add_argument("--dir", help="入力ディレクトリ（画面項目定義・単語帳）")
    parser.add_argument("--in-dir", help="上と同じ（--dir と同義。後方互換）")
    parser.add_argument("--out-dir", help="出力ディレクトリ（既定: out）")
    parser.add_argument("--screen-col", help="画面項目定義の列名（デフォルト: 項目名称）")
    parser.add_argument("--vocab-col", help="単語帳の列名（デフォルト: 論理名）")
    parser.add_argument("--no-gui", action="store_true", help="ダイアログを使わない（サーバ/CI向け）")
    return parser


__all__ = [
    "DEFAULT_CONFIG",
    "FALLBACK_EXACT_FLOOR",
    "HARD_EXACT_SCORE",
    "TK_AVAILABLE",
    "app_root",
    "ask_directory",
    "build_arg_parser",
    "load_runtime_env",
    "messagebox",
]
