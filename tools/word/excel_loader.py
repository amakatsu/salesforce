#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel ローダー
画面項目定義・単語帳の読み込み
"""
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd


def normalize_for_matching(text: str) -> str:
    """
    マッチング用の正規化（全角→半角、小文字化）

    Args:
        text: 正規化するテキスト

    Returns:
        正規化されたテキスト
    """
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    return re.sub(r"[\u3000\s]+", " ", s)


def pick_matching_sheets(xls: pd.ExcelFile, pattern: Optional[str]) -> List[str]:
    """
    パターンに一致するシートを取得

    Args:
        xls: Excelファイル
        pattern: シート名パターン（"*"で全シート、カンマ区切りで複数指定可）

    Returns:
        マッチするシート名のリスト
    """
    if not pattern or pattern.strip() == "*":
        return xls.sheet_names

    patterns = [p.strip() for p in pattern.split(",")]
    result = []

    for p in patterns:
        if p == "*":
            return xls.sheet_names

        # 完全一致チェック（NFKC正規化考慮）
        p_norm = normalize_for_matching(p)
        for sheet in xls.sheet_names:
            if normalize_for_matching(sheet) == p_norm and sheet not in result:
                result.append(sheet)

        # ワイルドカード一致
        if "*" in p:
            regex = p.replace("*", ".*")
            for sheet in xls.sheet_names:
                if re.match(regex, sheet, re.IGNORECASE) and sheet not in result:
                    result.append(sheet)

    return result if result else [xls.sheet_names[0]]


def detect_header_row_with_required_cols(
    path: Path,
    sheet_name: str,
    required_cols: List[str],
    scan_rows: int = 30
) -> int:
    """
    必須列を含むヘッダー行を検出

    Args:
        path: Excelファイルパス
        sheet_name: シート名
        required_cols: 必須列名のリスト
        scan_rows: スキャンする行数

    Returns:
        ヘッダー行のインデックス

    Raises:
        KeyError: 必須列が見つからない場合
    """
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    req = {normalize_for_matching(c) for c in required_cols if c}

    for i in range(len(head_df)):
        row_vals = {
            normalize_for_matching(x)
            for x in head_df.iloc[i].values
            if str(x) not in {"", "nan", "一致なし"}
        }
        if req.issubset(row_vals):
            return i

    raise KeyError(
        f"必須列{sorted(required_cols)}を含むヘッダ行が見つかりません: "
        f"{path.name}/{sheet_name}"
    )


def load_excel_with_auto_header(
    path: Path,
    sheet_name: Optional[str],
    required_cols: List[str],
    explicit_header_row: Optional[int] = None,
    scan_rows: int = 30
) -> Tuple[pd.DataFrame, int]:
    """
    Excelファイルを自動ヘッダー検出で読み込み

    Args:
        path: Excelファイルパス
        sheet_name: シート名
        required_cols: 必須列名のリスト
        explicit_header_row: 明示的なヘッダー行（1-based）
        scan_rows: ヘッダー検出時のスキャン行数

    Returns:
        (DataFrame, ヘッダー行インデックス)
    """
    # 明示的に指定されている場合
    if explicit_header_row is not None:
        hdr0 = max(0, explicit_header_row - 1)
        return pd.read_excel(path, sheet_name=sheet_name, header=hdr0), hdr0

    # 環境変数でヘッダー検出無効化されている場合
    if os.getenv("HEADER_DETECT", "true").lower() == "false":
        return pd.read_excel(path, sheet_name=sheet_name), 0

    # 自動検出
    header_row = detect_header_row_with_required_cols(
        path, sheet_name, required_cols, scan_rows
    )
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row), header_row
