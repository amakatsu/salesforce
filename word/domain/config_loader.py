"""
設定ファイル統一ローダー — 全YAML設定を一元的にロードする

仕様書 Section 4「設定ファイル（YAML外出し）」に基づき、
ドメインチェッカーが使用する4種類の設定ファイルを読み込む。

各ロード関数はモジュール変数でキャッシュし、2回目以降はI/Oなしで返す。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# キャッシュ用モジュール変数
# ---------------------------------------------------------------------------
_type_mapping_cache: dict[str, Any] | None = None
_text_type_mapping_cache: dict[str, Any] | None = None
_special_patterns_cache: dict[str, Any] | None = None
_synonyms_cache: dict[str, Any] | None = None


def _load_yaml(filename: str) -> dict[str, Any]:
    """指定YAMLファイルを読み込んで辞書として返す。"""
    path = _CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------


def load_type_mapping() -> dict[str, Any]:
    """型の大分類マッピングを返す（仕様書 Section 3-2）。

    戻り値の構造:
        {
            "categories": {
                "文字列系": {
                    "screen_types": [...],
                    "table_types": [...],
                    "domain_types": [...]
                },
                ...
            }
        }
    """
    global _type_mapping_cache
    if _type_mapping_cache is None:
        _type_mapping_cache = _load_yaml("type_mapping.yaml")
    return _type_mapping_cache


def load_text_type_mapping() -> dict[str, Any]:
    """テキストタイプ→ドメインデータ型マッピングを返す（仕様書 Section 3-3）。

    戻り値の構造:
        {
            "mappings": {"半角英字": ["半角英字"], ...},
            "default_behavior": "全候補から桁数で判定"
        }
    """
    global _text_type_mapping_cache
    if _text_type_mapping_cache is None:
        _text_type_mapping_cache = _load_yaml("text_type_mapping.yaml")
    return _text_type_mapping_cache


def load_special_patterns() -> dict[str, Any]:
    """特殊パターン定義を返す（仕様書 Section 3-7）。

    戻り値の構造:
        {
            "patterns": {
                "flag": {...},
                "comment": {...},
                "supplement": {...},
                "date_generic": {...},
                "date_individual": {...}
            }
        }
    """
    global _special_patterns_cache
    if _special_patterns_cache is None:
        _special_patterns_cache = _load_yaml("special_patterns.yaml")
    return _special_patterns_cache


def load_synonyms() -> dict[str, Any]:
    """同義語辞書を返す（既存 synonyms.yaml を活用）。

    戻り値の構造:
        {
            "groups": [["金額", "代金", ...], ...]
        }
    """
    global _synonyms_cache
    if _synonyms_cache is None:
        _synonyms_cache = _load_yaml("synonyms.yaml")
    return _synonyms_cache
