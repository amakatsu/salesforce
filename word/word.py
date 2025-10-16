from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from .config import (
    DEFAULT_CONFIG,
    TK_AVAILABLE,
    app_root,
    ask_directory,
    build_arg_parser,
    load_runtime_env,
    messagebox,
)
from .processing import process, save_outputs


def main() -> None:
    load_runtime_env()
    try:
        os.chdir(app_root())
    except Exception:
        pass
    parser = build_arg_parser()
    args = parser.parse_args()
    cfg = DEFAULT_CONFIG.copy()
    if cfg.get("OPENAI_SEND_AUTH") and not cfg.get("OPENAI_API_KEY"):
        print("[警告] OPENAI_SEND_AUTH=true ですが OPENAI_API_KEY が未設定です。Authorization は送信されません。")
    in_dir = args.in_dir or args.dir
    if not in_dir and not args.no_gui:
        in_dir = ask_directory("入力ディレクトリ（画面項目定義・単語帳）を選択")
        if not in_dir:
            try:
                in_dir = input("入力ディレクトリのパスを入力してください: ").strip()
            except Exception:
                in_dir = None
    if not in_dir:
        raise FileNotFoundError("入力ディレクトリが指定されていません。--dir かダイアログで指定してください。")
    if args.out_dir:
        cfg["OUT_DIR"] = args.out_dir
    else:
        if not args.no_gui:
            chosen = ask_directory("出力ディレクトリ（保存先）を選択（キャンセルで既定の out）")
            if chosen:
                cfg["OUT_DIR"] = chosen
    root_dir = Path(in_dir)
    if not root_dir.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {root_dir}")
    df = process(root_dir, args.screen_col, args.vocab_col, cfg)
    save_outputs(df, cfg)
    if TK_AVAILABLE and not args.no_gui and messagebox:
        try:
            messagebox.showinfo(
                "完了",
                f"出力が完了しました。保存先: {Path(cfg['OUT_DIR']).resolve()}\match_result.xlsx",
            )
        except Exception:
            pass


__all__ = [
    "DEFAULT_CONFIG",
    "main",
    "process",
    "save_outputs",
]


if __name__ == "__main__":
    main()
