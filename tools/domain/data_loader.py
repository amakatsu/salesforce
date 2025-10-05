#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメイン・テーブル定義データローダー
"""
import re
import unicodedata
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from .models import DomainDef, TableDef, TargetItem


def normalize_for_matching(text: str) -> str:
    """
    マッチング用の正規化

    Args:
        text: 正規化するテキスト

    Returns:
        正規化されたテキスト
    """
    if text is None or text == "":
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    return re.sub(r"[\u3000\s]+", " ", s)


def pick_matching_sheets(xls: pd.ExcelFile, pattern: str) -> List[str]:
    """
    パターンに一致するシートを取得

    Args:
        xls: Excelファイル
        pattern: シート名パターン

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

        p_norm = normalize_for_matching(p)
        for sheet in xls.sheet_names:
            if normalize_for_matching(sheet) == p_norm and sheet not in result:
                result.append(sheet)

    return result if result else [xls.sheet_names[0]]


def detect_header_row(
    path: Path,
    sheet_name: str,
    required_cols: List[str],
    scan_rows: int
) -> int:
    """
    必須列を含むヘッダー行を検出

    Args:
        path: Excelファイルパス
        sheet_name: シート名
        required_cols: 必須列名
        scan_rows: スキャン行数

    Returns:
        ヘッダー行インデックス

    Raises:
        KeyError: 必須列が見つからない
    """
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    req = {normalize_for_matching(c) for c in required_cols if c}

    for i in range(len(head_df)):
        row_vals = {
            normalize_for_matching(x)
            for x in head_df.iloc[i].values
            if str(x) not in {"", "nan"}
        }
        if req.issubset(row_vals):
            return i

    raise KeyError(
        f"必須列{sorted(required_cols)}を含むヘッダ行が見つかりません: "
        f"{path.name}/{sheet_name}"
    )


def load_domains(dir_path: Path, cfg: Dict[str, Any]) -> Dict[str, DomainDef]:
    """
    ドメイン定義を読み込み

    Args:
        dir_path: 入力ディレクトリ
        cfg: 設定

    Returns:
        ドメイン定義の辞書（キー: 正規化されたドメイン名）
    """
    from common.normalizers import normalize_text as norm_text

    files = sorted(dir_path.glob(cfg["DOMAIN_GLOB"]))
    if not files:
        raise FileNotFoundError("ドメイン定義ファイルが見つかりません")

    domains = {}
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = pick_matching_sheets(xls, cfg["DOMAIN_SHEET"])

        for sheet in sheets:
            try:
                header_row = detect_header_row(
                    path, sheet,
                    [cfg["DOMAIN_NAME_COL"], cfg["DOMAIN_TYPE_COL"]],
                    cfg.get("HEADER_SCAN_ROWS", 10)
                )
                df = pd.read_excel(path, sheet_name=sheet, header=header_row)

                for idx, row in df.iterrows():
                    name = str(row.get(cfg["DOMAIN_NAME_COL"], "")).strip()
                    if name:
                        row_number = header_row + idx + 2
                        domains[norm_text(name)] = DomainDef(
                            name=name,
                            data_type=str(row.get(cfg["DOMAIN_TYPE_COL"], "")).strip(),
                            length=str(row.get(cfg.get("DOMAIN_LENGTH_COL", "桁数"), "")).strip()
                            if cfg.get("DOMAIN_LENGTH_COL") in df.columns else None,
                            validation=str(row.get(cfg.get("DOMAIN_VALIDATION_COL", "単項目チェック"), "")).strip()
                            if cfg.get("DOMAIN_VALIDATION_COL") in df.columns else "",
                            row_number=row_number,
                            source_file=path.name,
                            source_sheet=sheet
                        )

                print(f"[INFO] ドメイン定義読み込み: {path.name}/{sheet} ({len(df)}件)")
            except Exception as e:
                print(f"[WARNING] シートスキップ: {path.name}/{sheet} ({e})")

    print(f"[INFO] 合計ドメイン定義: {len(domains)}件")
    return domains


def load_tables(dir_path: Path, cfg: Dict[str, Any]) -> Dict[str, TableDef]:
    """
    テーブル定義を読み込み

    Args:
        dir_path: 入力ディレクトリ
        cfg: 設定

    Returns:
        テーブル定義の辞書（キー: 項目名）
    """
    from common.normalizers import normalize_text as norm_text

    files = sorted(dir_path.glob(cfg["TABLE_GLOB"]))
    if not files:
        raise FileNotFoundError("テーブル定義ファイルが見つかりません")

    tables = {}
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = pick_matching_sheets(xls, cfg["TABLE_SHEET"])

        for sheet in sheets:
            try:
                header_row = detect_header_row(
                    path, sheet,
                    [cfg["TABLE_NAME_COL"], cfg["TABLE_ITEM_COL"]],
                    cfg.get("HEADER_SCAN_ROWS", 10)
                )
                df = pd.read_excel(path, sheet_name=sheet, header=header_row)

                for idx, row in df.iterrows():
                    item_name = str(row.get(cfg["TABLE_ITEM_COL"], "")).strip()
                    if item_name:
                        row_number = header_row + idx + 2
                        table_def = TableDef(
                            table_name=str(row.get(cfg["TABLE_NAME_COL"], "")).strip(),
                            item_name=item_name,
                            column_name=str(row.get(cfg.get("TABLE_COLUMN_COL", "カラム名"), "")).strip()
                            if cfg.get("TABLE_COLUMN_COL") in df.columns else "",
                            data_type=str(row.get(cfg.get("TABLE_TYPE_COL", "データ型"), "")).strip()
                            if cfg.get("TABLE_TYPE_COL") in df.columns else "",
                            length=str(row.get(cfg.get("TABLE_LENGTH_COL", "桁数"), "")).strip()
                            if cfg.get("TABLE_LENGTH_COL") in df.columns else None,
                            row_number=row_number,
                            source_file=path.name,
                            source_sheet=sheet
                        )
                        tables[norm_text(item_name)] = table_def

                print(f"[INFO] テーブル定義読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[WARNING] シートスキップ: {path.name}/{sheet} ({e})")

    print(f"[INFO] 合計テーブルカラム: {len(tables)}件")
    return tables


def load_targets(dir_path: Path, cfg: Dict[str, Any]) -> List[TargetItem]:
    """
    対象一覧を読み込み

    Args:
        dir_path: 入力ディレクトリ
        cfg: 設定

    Returns:
        対象項目のリスト
    """
    files = sorted(dir_path.glob(cfg["TARGET_GLOB"]))
    if not files:
        raise FileNotFoundError("対象一覧ファイルが見つかりません")

    targets = []
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = pick_matching_sheets(xls, cfg["TARGET_SHEET"])

        for sheet in sheets:
            try:
                header_row = detect_header_row(
                    path, sheet,
                    [cfg["TARGET_ITEM_COL"]],
                    cfg.get("HEADER_SCAN_ROWS", 10)
                )
                df = pd.read_excel(path, sheet_name=sheet, header=header_row)

                for idx, row in df.iterrows():
                    item_name = str(row.get(cfg["TARGET_ITEM_COL"], "")).strip()
                    if item_name:
                        row_number = header_row + idx + 2
                        targets.append(TargetItem(
                            item_name=item_name,
                            row_number=row_number,
                            source_file=path.name,
                            source_sheet=sheet
                        ))

                print(f"[INFO] 対象一覧読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[WARNING] シートスキップ: {path.name}/{sheet} ({e})")

    print(f"[INFO] 合計対象項目: {len(targets)}件")
    return targets
