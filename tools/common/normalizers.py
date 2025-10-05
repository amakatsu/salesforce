#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ正規化ユーティリティ
テキスト・データ型の正規化処理を提供
"""
import re


def normalize_text(text: str) -> str:
    """
    テキストを正規化（全角→半角、小文字化、空白削除）

    Args:
        text: 正規化するテキスト

    Returns:
        正規化されたテキスト
    """
    if not isinstance(text, str):
        return str(text)

    # 全角英数字を半角に変換
    text = text.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz'
    ))
    text = text.translate(str.maketrans(
        '0123456789',
        '0123456789'
    ))

    # 空白を削除
    text = re.sub(r'\s+', '', text)

    return text.lower()


def normalize_data_type(dtype: str) -> str:
    """
    データ型を正規化

    Args:
        dtype: データ型文字列

    Returns:
        正規化されたデータ型
    """
    if not isinstance(dtype, str):
        return ""

    dtype_lower = dtype.lower().strip()

    # 文字列型
    if "varchar" in dtype_lower or "char" in dtype_lower or "string" in dtype_lower:
        return "varchar"

    # 数値型
    if "int" in dtype_lower or "integer" in dtype_lower:
        return "int"
    if "decimal" in dtype_lower or "numeric" in dtype_lower or "number" in dtype_lower:
        return "decimal"
    if "float" in dtype_lower or "double" in dtype_lower or "real" in dtype_lower:
        return "float"

    # 日付型
    if "date" in dtype_lower:
        return "date"
    if "time" in dtype_lower and "stamp" in dtype_lower:
        return "timestamp"
    if "time" in dtype_lower:
        return "time"

    # その他
    if "bool" in dtype_lower:
        return "boolean"
    if "text" in dtype_lower or "clob" in dtype_lower:
        return "text"
    if "blob" in dtype_lower or "binary" in dtype_lower:
        return "blob"

    # 正規化できない場合はそのまま返す
    return dtype_lower


def normalize_column_name(name: str) -> str:
    """
    カラム名を正規化（英数字とアンダースコアのみ）

    Args:
        name: カラム名

    Returns:
        正規化されたカラム名
    """
    if not isinstance(name, str):
        return str(name)

    # 全角を半角に変換
    name = normalize_text(name)

    # 英数字とアンダースコア以外を削除
    name = re.sub(r'[^a-z0-9_]', '', name)

    return name


def extract_digits(text: str) -> int:
    """
    テキストから数字を抽出

    Args:
        text: テキスト

    Returns:
        抽出された数字（見つからない場合は0）
    """
    if not isinstance(text, str):
        text = str(text)

    # 数字のみを抽出
    digits = re.findall(r'\d+', text)

    if digits:
        return int(digits[0])
    else:
        return 0
