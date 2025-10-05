#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データモデル定義
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DomainDef:
    """ドメイン定義"""
    name: str
    data_type: str
    length: Optional[str]
    validation: str
    row_number: int
    source_file: str
    source_sheet: str


@dataclass
class TableDef:
    """テーブル定義"""
    table_name: str
    item_name: str
    column_name: str
    data_type: str
    length: Optional[str]
    row_number: int
    source_file: str
    source_sheet: str


@dataclass
class TargetItem:
    """対象項目"""
    item_name: str
    row_number: int
    source_file: str
    source_sheet: str
