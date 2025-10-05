#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel ファイル I/O 共通モジュール
ヘッダー検出・読み込み処理を一元管理
"""
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional


def detect_header_row(
    path: Path,
    sheet_name: str = 0,
    scan_rows: int = 10
) -> Optional[int]:
    """
    Excelファイルのヘッダー行を検出

    Args:
        path: Excelファイルのパス
        sheet_name: シート名またはインデックス
        scan_rows: スキャンする行数

    Returns:
        ヘッダー行のインデックス（見つからない場合はNone）
    """
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)

    for i in range(scan_rows):
        row = head_df.iloc[i]
        non_null = row.dropna()
        if len(non_null) >= 2:  # 少なくとも2列に値がある
            return i

    return None


def read_excel_with_auto_header(
    path: Path,
    sheet_name: str = 0,
    header_row: Optional[int] = None,
    scan_rows: int = 10
) -> Tuple[pd.DataFrame, int]:
    """
    Excelファイルを読み込み（ヘッダー自動検出）

    Args:
        path: Excelファイルのパス
        sheet_name: シート名またはインデックス
        header_row: ヘッダー行（Noneの場合は自動検出）
        scan_rows: ヘッダー検出時のスキャン行数

    Returns:
        tuple: (DataFrame, ヘッダー行インデックス)
    """
    # ヘッダー行が指定されている場合
    if header_row is not None:
        df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
        return df, header_row

    # ヘッダー行を自動検出
    detected_header = detect_header_row(path, sheet_name, scan_rows)

    if detected_header is not None:
        df = pd.read_excel(path, sheet_name=sheet_name, header=detected_header)
        return df, detected_header
    else:
        # ヘッダーが見つからない場合はデフォルト（0行目）
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df, 0


def read_excel_simple(
    path: Path,
    sheet_name: str = 0,
    header_row: Optional[int] = None
) -> pd.DataFrame:
    """
    Excelファイルをシンプルに読み込み

    Args:
        path: Excelファイルのパス
        sheet_name: シート名またはインデックス
        header_row: ヘッダー行（Noneの場合は0行目）

    Returns:
        DataFrame
    """
    if header_row is not None:
        return pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    else:
        return pd.read_excel(path, sheet_name=sheet_name)
