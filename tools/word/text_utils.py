#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト処理ユーティリティ
正規化・類似度計算
"""
import re
import unicodedata
import difflib
from typing import List
from dataclasses import dataclass


@dataclass
class Candidate:
    """候補単語"""
    term: str
    score: float


def normalize_text(text: str) -> str:
    """
    NFKC正規化 + 小文字化 + 記号/空白の正規化

    Args:
        text: 正規化するテキスト

    Returns:
        正規化されたテキスト
    """
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = re.sub(r"[\u3000\s]+", " ", s)          # 全角/半角スペースを単一化
    s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)    # 区切り記号はスペースへ
    return re.sub(r"\s+", " ", s)


def calculate_similarity(a: str, b: str) -> float:
    """
    簡易類似度計算

    Args:
        a: 比較文字列1
        b: 比較文字列2

    Returns:
        類似度（0.0～1.0）
        - 1.0: 完全一致
        - 0.9: 片方が他方を含む
        - その他: difflib.SequenceMatcher.ratio()
    """
    a_n, b_n = normalize_text(a), normalize_text(b)
    if not a_n or not b_n:
        return 0.0
    if a_n == b_n:
        return 1.0
    if a_n in b_n or b_n in a_n:
        return 0.9
    return difflib.SequenceMatcher(None, a_n, b_n).ratio()


def find_top_candidates(
    target: str,
    vocab_terms: List[str],
    k: int,
    threshold: float
) -> List[Candidate]:
    """
    上位K件の類似候補を取得

    Args:
        target: 対象文字列
        vocab_terms: 単語リスト
        k: 上位K件
        threshold: 類似度の閾値

    Returns:
        上位K件の候補リスト
    """
    scores = [(term, calculate_similarity(target, term)) for term in vocab_terms]
    scores = [(term, score) for term, score in scores if score >= threshold]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [Candidate(term=t, score=s) for t, s in scores[:k]]


def generate_simple_physical_name(text: str) -> str:
    """
    簡易的な物理名を生成（英数字・アンダースコアのみ）

    Args:
        text: 元のテキスト

    Returns:
        物理名（小文字・スネークケース）
    """
    if not text:
        return ""
    # NFKC正規化
    normalized = unicodedata.normalize("NFKC", str(text))
    # 英数字とアンダースコアのみ残す
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", normalized)
    # 小文字化
    return cleaned.lower().strip("_")
