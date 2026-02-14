#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本語同義語辞書 — C方式（domain_matcher）用

同義語データは synonyms.yaml に外出し。本モジュールはロードとAPIを提供する。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import FrozenSet, Optional, Set

import yaml

# ============================================================================
# YAML読み込み
# ============================================================================

_YAML_PATH = Path(__file__).parent / "synonyms.yaml"


def _load_groups_from_yaml(path: Path) -> list[FrozenSet[str]]:
    """synonyms.yaml から同義語グループを読み込む"""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [frozenset(group) for group in data["groups"]]


SYNONYM_GROUPS: list[FrozenSet[str]] = _load_groups_from_yaml(_YAML_PATH)

# ============================================================================
# テキスト正規化
# ============================================================================

_TRAILING_DIGITS = re.compile(r"\d+$")


def _normalize(text: str) -> str:
    """NFKC正規化 + 小文字化 + 前後空白除去"""
    return unicodedata.normalize("NFKC", text).lower().strip()


def strip_digits(name: str) -> str:
    """項目名末尾の数字を除去する。

    判定フローの最初のステップ。
    「顧客名1」→「顧客名」、「TEL2」→「TEL」のように
    連番付き項目名を正規化して比較精度を上げる。

    >>> strip_digits("ああ1")
    'ああ'
    >>> strip_digits("TEL2")
    'TEL'
    >>> strip_digits("住所")
    '住所'
    >>> strip_digits("123")
    '123'
    """
    result = _TRAILING_DIGITS.sub("", name)
    return result if result else name

# ============================================================================
# 逆引きインデックス
# ============================================================================


def _build_lookup() -> dict[str, FrozenSet[str]]:
    """語 → 所属グループの逆引き辞書を構築"""
    lookup: dict[str, FrozenSet[str]] = {}
    for group in SYNONYM_GROUPS:
        for word in group:
            lookup[_normalize(word)] = group
    return lookup


_LOOKUP = _build_lookup()

# ============================================================================
# 公開API
# ============================================================================


def are_synonyms(word_a: str, word_b: str) -> bool:
    """2つの語が同義語リストで同グループか判定する。

    >>> are_synonyms("金額", "価格")
    True
    >>> are_synonyms("金額", "住所")
    False
    >>> are_synonyms("備考", "補記")
    True
    """
    key_a = _normalize(word_a)
    key_b = _normalize(word_b)
    if key_a == key_b:
        return True
    group = _LOOKUP.get(key_a)
    if group is None:
        return False
    return key_b in {_normalize(w) for w in group}


def get_synonym_group(word: str) -> Optional[Set[str]]:
    """指定語の同義語グループを返す。登録されていなければ None。

    >>> sorted(get_synonym_group("備考"))
    ['コメント', 'メモ', '備考', '注記', '補記']
    """
    group = _LOOKUP.get(_normalize(word))
    if group is None:
        return None
    return set(group)


def find_synonym_match(item_suffix: str, domain_suffix: str) -> bool:
    """項目名末尾語とドメイン名末尾語が同義語か判定する。

    C方式の名前比較ステップで使用。
    渡された語同士を同義語グループで照合する。

    >>> find_synonym_match("金額", "価格")
    True
    >>> find_synonym_match("コメント", "補記")
    True
    """
    return are_synonyms(item_suffix, domain_suffix)
