#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドメイン定義総合チェックツール（LLM補助）

機能1【ドメイン提案】: 対象一覧のドメイン指定をチェックし、適切なドメインを提案
機能2【整合性チェック】: ドメイン定義とテーブル定義の型・桁数の整合性をチェック
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import threading
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

# ====== GUI（任意） ===========================================================
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

# ====== 定数 ==================================================================
DEFAULT_CONFIG: Dict[str, Any] = {
    # --- API（OpenAI互換）
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "OPENAI_PATH": os.getenv("OPENAI_PATH", "/chat/completions"),
    "OPENAI_HEADERS_JSON": os.getenv("OPENAI_HEADERS_JSON", '{"api-key":"8b843f2df20548899f93c0624452ea68","apim-user-id":"PIT04447"}'),
    "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", "false").lower() != "false",
    "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "false").lower() != "false",

    # --- 生成パラメタ
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "800")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.5")),
    "TOP_P": float(os.getenv("TOP_P", "0.95")),

    # --- 入力ファイル検出
    "TARGET_GLOB": os.getenv("TARGET_GLOB", "*対象一覧*.xlsx"),
    "DOMAIN_GLOB": os.getenv("DOMAIN_GLOB", "*ドメイン定義*.xlsx"),
    "TABLE_GLOB": os.getenv("TABLE_GLOB", "*テーブル定義*.xlsx"),

    # --- シート/列設定
    "TARGET_SHEET": os.getenv("TARGET_SHEET", "*"),
    "DOMAIN_SHEET": os.getenv("DOMAIN_SHEET", "*"),
    "TABLE_SHEET": os.getenv("TABLE_SHEET", "*"),

    "TARGET_ITEM_COL": os.getenv("TARGET_ITEM_COL", "項目名"),
    "TARGET_DOMAIN_COL": os.getenv("TARGET_DOMAIN_COL", "ドメイン"),
    "TARGET_TABLE_COL": os.getenv("TARGET_TABLE_COL", "テーブル名"),
    "TARGET_COLUMN_COL": os.getenv("TARGET_COLUMN_COL", "カラム名"),

    "DOMAIN_NAME_COL": os.getenv("DOMAIN_NAME_COL", "ドメイン名"),
    "DOMAIN_TYPE_COL": os.getenv("DOMAIN_TYPE_COL", "データ型"),
    "DOMAIN_LENGTH_COL": os.getenv("DOMAIN_LENGTH_COL", "桁数"),
    "DOMAIN_PRECISION_COL": os.getenv("DOMAIN_PRECISION_COL", "精度"),
    "DOMAIN_SCALE_COL": os.getenv("DOMAIN_SCALE_COL", "スケール"),
    "DOMAIN_DESC_COL": os.getenv("DOMAIN_DESC_COL", "説明"),

    "TABLE_NAME_COL": os.getenv("TABLE_NAME_COL", "テーブル名"),
    "TABLE_COLUMN_COL": os.getenv("TABLE_COLUMN_COL", "カラム名"),
    "TABLE_DOMAIN_COL": os.getenv("TABLE_DOMAIN_COL", "ドメイン"),
    "TABLE_TYPE_COL": os.getenv("TABLE_TYPE_COL", "データ型"),
    "TABLE_LENGTH_COL": os.getenv("TABLE_LENGTH_COL", "桁数"),
    "TABLE_PRECISION_COL": os.getenv("TABLE_PRECISION_COL", "精度"),
    "TABLE_SCALE_COL": os.getenv("TABLE_SCALE_COL", "スケール"),

    # --- 出力
    "OUT_DIR": os.getenv("OUT_DIR", "out"),

    # --- 実行制御
    "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
    "RETRY": int(os.getenv("RETRY", "2")),
    "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5")),

    # --- 機能制御
    "CHECK_MODE": os.getenv("CHECK_MODE", "both")  # both, suggestion, validation
}

# ====== 正規化関数 ============================================================
def normalize_text(text: str) -> str:
    """NFKC正規化 + 小文字化"""
    if text is None or text == "":
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    return re.sub(r"[\u3000\s]+", " ", s)

def normalize_data_type(dtype: str) -> str:
    """データ型の正規化"""
    if not dtype:
        return ""
    dt = normalize_text(dtype)
    type_map = {
        "varchar": "varchar", "varchar2": "varchar", "char": "char",
        "int": "integer", "integer": "integer", "bigint": "bigint",
        "decimal": "decimal", "numeric": "decimal", "number": "decimal",
        "date": "date", "datetime": "datetime", "timestamp": "timestamp",
        "boolean": "boolean", "bool": "boolean"
    }
    for key, value in type_map.items():
        if key in dt:
            return value
    return dt

# ====== データクラス ==========================================================
@dataclass
class DomainDef:
    """ドメイン定義"""
    name: str
    data_type: str
    length: Optional[str]
    precision: Optional[str]
    scale: Optional[str]
    description: str

@dataclass
class TableDef:
    """テーブル定義"""
    table_name: str
    column_name: str
    domain: str
    data_type: str
    length: Optional[str]
    precision: Optional[str]
    scale: Optional[str]

@dataclass
class TargetItem:
    """対象項目"""
    item_name: str
    domain: str
    table_name: str
    column_name: str
    source_file: str
    source_sheet: str

# ====== Excel I/O =============================================================
HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", "10"))

def _pick_matching_sheets(xls: pd.ExcelFile, preferred: Optional[str]) -> List[str]:
    if not preferred:
        return [xls.sheet_names[0]]
    norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]
    all_matches = []
    for pattern in patterns:
        want = norm(pattern)
        regex_pattern = want.replace('*', '.*')
        for name in xls.sheet_names:
            if re.match(regex_pattern, norm(name)):
                all_matches.append(name)
    result = []
    seen = set()
    for sheet in all_matches:
        if sheet not in seen:
            result.append(sheet)
            seen.add(sheet)
    return result if result else [xls.sheet_names[0]]

def _detect_header_row(path: Path, sheet_name: str, required_cols: List[str], scan_rows: int) -> int:
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    req = {normalize_text(c) for c in required_cols if c}
    for i in range(len(head_df)):
        row_vals = {normalize_text(x) for x in head_df.iloc[i].values if str(x) not in {"", "nan"}}
        if req.issubset(row_vals):
            return i
    raise KeyError(f"必須列{sorted(required_cols)}を含むヘッダ行が見つかりません: {path.name}/{sheet_name}")

def read_excel_auto(path: Path, sheet_name: Optional[str], required_cols: List[str]) -> pd.DataFrame:
    if not HEADER_DETECT:
        return pd.read_excel(path, sheet_name=sheet_name)
    header_row = _detect_header_row(path, sheet_name, required_cols, HEADER_SCAN_ROWS)
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row)

def load_domains(dir_path: Path, cfg: Dict[str, Any]) -> Dict[str, DomainDef]:
    files = sorted(dir_path.glob(cfg["DOMAIN_GLOB"]))
    if not files:
        raise FileNotFoundError(f"ドメイン定義ファイルが見つかりません")
    domains = {}
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = _pick_matching_sheets(xls, cfg["DOMAIN_SHEET"])
        for sheet in sheets:
            try:
                df = read_excel_auto(path, sheet, [cfg["DOMAIN_NAME_COL"], cfg["DOMAIN_TYPE_COL"]])
                for _, row in df.iterrows():
                    name = str(row.get(cfg["DOMAIN_NAME_COL"], "")).strip()
                    if name:
                        domains[normalize_text(name)] = DomainDef(
                            name=name,
                            data_type=str(row.get(cfg["DOMAIN_TYPE_COL"], "")).strip(),
                            length=str(row.get(cfg["DOMAIN_LENGTH_COL"], "")).strip() if cfg["DOMAIN_LENGTH_COL"] in df.columns else None,
                            precision=str(row.get(cfg["DOMAIN_PRECISION_COL"], "")).strip() if cfg["DOMAIN_PRECISION_COL"] in df.columns else None,
                            scale=str(row.get(cfg["DOMAIN_SCALE_COL"], "")).strip() if cfg["DOMAIN_SCALE_COL"] in df.columns else None,
                            description=str(row.get(cfg["DOMAIN_DESC_COL"], "")).strip() if cfg["DOMAIN_DESC_COL"] in df.columns else ""
                        )
                print(f"[INFO] ドメイン定義読み込み: {path.name}/{sheet} ({len(domains)}件)")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計ドメイン定義: {len(domains)}件")
    return domains

def load_tables(dir_path: Path, cfg: Dict[str, Any]) -> Dict[Tuple[str, str], TableDef]:
    files = sorted(dir_path.glob(cfg["TABLE_GLOB"]))
    if not files:
        raise FileNotFoundError(f"テーブル定義ファイルが見つかりません")
    tables = {}
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = _pick_matching_sheets(xls, cfg["TABLE_SHEET"])
        for sheet in sheets:
            try:
                df = read_excel_auto(path, sheet, [cfg["TABLE_NAME_COL"], cfg["TABLE_COLUMN_COL"]])
                for _, row in df.iterrows():
                    table_name = str(row.get(cfg["TABLE_NAME_COL"], "")).strip()
                    column_name = str(row.get(cfg["TABLE_COLUMN_COL"], "")).strip()
                    if table_name and column_name:
                        key = (normalize_text(table_name), normalize_text(column_name))
                        tables[key] = TableDef(
                            table_name=table_name,
                            column_name=column_name,
                            domain=str(row.get(cfg["TABLE_DOMAIN_COL"], "")).strip() if cfg["TABLE_DOMAIN_COL"] in df.columns else "",
                            data_type=str(row.get(cfg["TABLE_TYPE_COL"], "")).strip() if cfg["TABLE_TYPE_COL"] in df.columns else "",
                            length=str(row.get(cfg["TABLE_LENGTH_COL"], "")).strip() if cfg["TABLE_LENGTH_COL"] in df.columns else None,
                            precision=str(row.get(cfg["TABLE_PRECISION_COL"], "")).strip() if cfg["TABLE_PRECISION_COL"] in df.columns else None,
                            scale=str(row.get(cfg["TABLE_SCALE_COL"], "")).strip() if cfg["TABLE_SCALE_COL"] in df.columns else None
                        )
                print(f"[INFO] テーブル定義読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計テーブルカラム: {len(tables)}件")
    return tables

def load_targets(dir_path: Path, cfg: Dict[str, Any]) -> List[TargetItem]:
    files = sorted(dir_path.glob(cfg["TARGET_GLOB"]))
    if not files:
        print(f"[警告] 対象一覧ファイルが見つかりません（機能1はスキップ）")
        return []
    items = []
    for path in files:
        xls = pd.ExcelFile(path)
        sheets = _pick_matching_sheets(xls, cfg["TARGET_SHEET"])
        for sheet in sheets:
            try:
                df = read_excel_auto(path, sheet, [cfg["TARGET_ITEM_COL"], cfg["TARGET_TABLE_COL"]])
                for _, row in df.iterrows():
                    item = TargetItem(
                        item_name=str(row.get(cfg["TARGET_ITEM_COL"], "")).strip(),
                        domain=str(row.get(cfg["TARGET_DOMAIN_COL"], "")).strip() if cfg["TARGET_DOMAIN_COL"] in df.columns else "",
                        table_name=str(row.get(cfg["TARGET_TABLE_COL"], "")).strip(),
                        column_name=str(row.get(cfg["TARGET_COLUMN_COL"], "")).strip(),
                        source_file=path.name,
                        source_sheet=sheet
                    )
                    if item.item_name:
                        items.append(item)
                print(f"[INFO] 対象一覧読み込み: {path.name}/{sheet}")
            except Exception as e:
                print(f"[警告] {path.name}({sheet}) エラー: {e}")
    print(f"[INFO] 合計対象項目: {len(items)}件")
    return items

# ====== APIクライアント =======================================================
class ApiClient:
    def __init__(self, cfg: Dict[str, Any]):
        self.base_url = cfg["OPENAI_BASE_URL"].rstrip("/")
        self.path = cfg["OPENAI_PATH"]
        self.timeout = cfg["TIMEOUT_SEC"]
        self.verify = cfg["VERIFY_SSL"]
        self.session = requests.Session()
        proxies: Dict[str, str] = {}
        if cfg.get("HTTP_PROXY"):
            proxies["http"] = cfg["HTTP_PROXY"]
        if cfg.get("HTTPS_PROXY"):
            proxies["https"] = cfg["HTTPS_PROXY"]
        if proxies:
            self.session.proxies.update(proxies)
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if cfg.get("OPENAI_SEND_AUTH") and cfg.get("OPENAI_API_KEY"):
            headers["Authorization"] = f"Bearer {cfg['OPENAI_API_KEY']}"
        extra = cfg.get("OPENAI_HEADERS_JSON")
        if extra:
            try:
                headers.update(json.loads(extra))
            except:
                pass
        self.headers = headers

    def post_json(self, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{self.path}"
        resp = self.session.post(url, headers=self.headers, json=body, timeout=self.timeout, verify=self.verify)
        resp.raise_for_status()
        return resp.json()

# ====== LLMプロンプト（機能1: ドメイン提案） ==================================
LLM_SUGGESTION_SYSTEM = (
    "あなたはデータベース設計の専門家です。\n"
    "テーブル定義とドメイン候補から、適切なドメインを提案します。\n"
    "ドメインが不要な技術的カラムも見分けます。\n"
)

LLM_SUGGESTION_USER = """対象項目: {item_name}
テーブル: {table_name}.{column_name}
テーブル定義: データ型={table_type}, 桁数={table_length}

ドメイン候補:
{domain_candidates}

出力JSON:
{{
  "domain_required": true | false,
  "reason": string,
  "recommended_domain": string | null,
  "confidence": "high" | "medium" | "low"
}}

判定基準:
- domain_required: 業務意味を持つならtrue、技術的カラム(ID自動採番等)ならfalse
- recommended_domain: domain_required=trueなら候補から選択、falseならnull
- confidence: high=完全一致、medium=型一致、low=推測

JSON以外出力禁止。
"""

# ====== LLMプロンプト（機能2: 整合性チェック） ================================
LLM_VALIDATION_SYSTEM = (
    "あなたはデータベース設計の専門家です。\n"
    "ドメイン定義とテーブル定義の差異を分析し、重要度を評価します。\n"
)

LLM_VALIDATION_USER = """テーブル: {table_name}.{column_name}
指定ドメイン: {domain_name}

ドメイン定義: 型={domain_type}, 桁数={domain_length}, 精度={domain_precision}, スケール={domain_scale}
テーブル定義: 型={table_type}, 桁数={table_length}, 精度={table_precision}, スケール={table_scale}

差異: {differences}

出力JSON:
{{
  "severity": "critical" | "warning" | "info" | "acceptable",
  "is_valid": true | false,
  "reason": string,
  "recommendation": string
}}

重要度:
- critical: データ損失の危険
- warning: 業務上問題の可能性
- info: 統一推奨だが問題なし
- acceptable: 実質的に同じ

JSON以外出力禁止。
"""

def call_llm(prompt_system: str, prompt_user: str, cfg: Dict[str, Any],
             client: ApiClient, api_semaphore: threading.Semaphore) -> Dict[str, Any]:
    payload = {
        "model": cfg["OPENAI_MODEL"],
        "max_tokens": cfg["MAX_TOKENS"],
        "temperature": cfg["TEMPERATURE"],
        "top_p": cfg["TOP_P"],
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ]
    }
    if api_semaphore:
        api_semaphore.acquire()
    try:
        for attempt in range(cfg["RETRY"] + 1):
            try:
                data = client.post_json(payload)
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as e:
                if attempt < cfg["RETRY"]:
                    time.sleep(1.2 * (attempt + 1))
                    continue
                return {"error": str(e)}
    finally:
        if api_semaphore:
            api_semaphore.release()

# ====== 処理関数 ==============================================================
def compare_spec(domain: DomainDef, table: TableDef) -> Tuple[bool, List[str]]:
    """ドメイン定義とテーブル定義を比較"""
    type_match = normalize_data_type(domain.data_type) == normalize_data_type(table.data_type)
    diffs = []
    if not type_match:
        diffs.append(f"データ型: {domain.data_type} vs {table.data_type}")

    # 桁数比較
    if domain.length and table.length:
        if normalize_text(domain.length) != normalize_text(table.length):
            diffs.append(f"桁数: {domain.length} vs {table.length}")

    # 精度・スケール比較
    if domain.precision and table.precision:
        if normalize_text(domain.precision) != normalize_text(table.precision):
            diffs.append(f"精度: {domain.precision} vs {table.precision}")
    if domain.scale and table.scale:
        if normalize_text(domain.scale) != normalize_text(table.scale):
            diffs.append(f"スケール: {domain.scale} vs {table.scale}")

    return (type_match and len(diffs) == 0), diffs

def process_domain_suggestion(targets: List[TargetItem], domains: Dict[str, DomainDef],
                              tables: Dict[Tuple[str, str], TableDef],
                              cfg: Dict[str, Any], client: ApiClient,
                              api_semaphore: threading.Semaphore) -> pd.DataFrame:
    """機能1: ドメイン提案"""
    rows = []
    for item in targets:
        domain_key = normalize_text(item.domain)
        domain_exists = domain_key in domains if domain_key else False

        table_key = (normalize_text(item.table_name), normalize_text(item.column_name))
        table_def = tables.get(table_key)

        if domain_exists:
            rows.append({
                "source_file": item.source_file,
                "item_name": item.item_name,
                "specified_domain": item.domain,
                "check_result": "OK",
                "reason": "ドメイン定義に存在",
                "recommended_domain": item.domain
            })
        elif not table_def:
            rows.append({
                "source_file": item.source_file,
                "item_name": item.item_name,
                "specified_domain": item.domain or "(未指定)",
                "check_result": "エラー",
                "reason": "テーブル定義が見つかりません",
                "recommended_domain": None
            })
        else:
            # LLM判定
            domain_list = [f"{d.name} ({d.data_type})" for d in list(domains.values())[:10]]
            llm_result = call_llm(
                LLM_SUGGESTION_SYSTEM,
                LLM_SUGGESTION_USER.format(
                    item_name=item.item_name,
                    table_name=table_def.table_name,
                    column_name=table_def.column_name,
                    table_type=table_def.data_type,
                    table_length=table_def.length or "未指定",
                    domain_candidates="\n".join(domain_list)
                ),
                cfg, client, api_semaphore
            )
            if "error" not in llm_result:
                check_result = "ドメイン不要" if not llm_result.get("domain_required") else "要定義"
                rows.append({
                    "source_file": item.source_file,
                    "item_name": item.item_name,
                    "specified_domain": item.domain or "(未指定)",
                    "check_result": check_result,
                    "reason": llm_result.get("reason", ""),
                    "recommended_domain": llm_result.get("recommended_domain")
                })
    return pd.DataFrame(rows)

def process_domain_validation(tables: Dict[Tuple[str, str], TableDef],
                              domains: Dict[str, DomainDef],
                              cfg: Dict[str, Any], client: ApiClient,
                              api_semaphore: threading.Semaphore) -> pd.DataFrame:
    """機能2: 整合性チェック"""
    rows = []
    for (table_key), table_def in tables.items():
        if not table_def.domain:
            continue

        domain_key = normalize_text(table_def.domain)
        domain = domains.get(domain_key)

        if not domain:
            rows.append({
                "table_name": table_def.table_name,
                "column_name": table_def.column_name,
                "domain_name": table_def.domain,
                "check_result": "エラー",
                "severity": "critical",
                "reason": "ドメイン定義が存在しません",
                "recommendation": "ドメイン定義を追加"
            })
            continue

        is_match, diffs = compare_spec(domain, table_def)

        if is_match:
            rows.append({
                "table_name": table_def.table_name,
                "column_name": table_def.column_name,
                "domain_name": domain.name,
                "check_result": "OK",
                "severity": "acceptable",
                "domain_type": domain.data_type,
                "table_type": table_def.data_type,
                "reason": "完全一致",
                "recommendation": "問題なし"
            })
        else:
            # LLM判定
            llm_result = call_llm(
                LLM_VALIDATION_SYSTEM,
                LLM_VALIDATION_USER.format(
                    table_name=table_def.table_name,
                    column_name=table_def.column_name,
                    domain_name=domain.name,
                    domain_type=domain.data_type,
                    domain_length=domain.length or "未指定",
                    domain_precision=domain.precision or "未指定",
                    domain_scale=domain.scale or "未指定",
                    table_type=table_def.data_type,
                    table_length=table_def.length or "未指定",
                    table_precision=table_def.precision or "未指定",
                    table_scale=table_def.scale or "未指定",
                    differences="\n".join(diffs)
                ),
                cfg, client, api_semaphore
            )
            if "error" not in llm_result:
                rows.append({
                    "table_name": table_def.table_name,
                    "column_name": table_def.column_name,
                    "domain_name": domain.name,
                    "check_result": "OK" if llm_result.get("is_valid") else "不一致",
                    "severity": llm_result.get("severity", "warning"),
                    "domain_type": domain.data_type,
                    "table_type": table_def.data_type,
                    "reason": llm_result.get("reason", ""),
                    "recommendation": llm_result.get("recommendation", "")
                })
    return pd.DataFrame(rows)

# ====== 出力 ==================================================================
def save_outputs(df_suggestion: Optional[pd.DataFrame], df_validation: Optional[pd.DataFrame],
                cfg: Dict[str, Any]) -> None:
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import PatternFill
    from openpyxl.formatting.rule import FormulaRule

    out_dir = Path(cfg["OUT_DIR"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = out_dir / "domain_check_result.xlsx"

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        if df_suggestion is not None and len(df_suggestion) > 0:
            df_suggestion.to_excel(w, sheet_name="ドメイン提案", index=False)
            ws = w.sheets["ドメイン提案"]
            # 色付け
            if "check_result" in df_suggestion.columns:
                result_col_idx = list(df_suggestion.columns).index("check_result") + 1
                result_col = get_column_letter(result_col_idx)
                fill_green = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
                fill_yellow = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
                fill_red = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
                rng = f"{result_col}2:{result_col}{len(df_suggestion)+1}"
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{result_col}2="OK"'], fill=fill_green))
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{result_col}2="要定義"'], fill=fill_yellow))
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{result_col}2="エラー"'], fill=fill_red))

        if df_validation is not None and len(df_validation) > 0:
            df_validation.to_excel(w, sheet_name="整合性チェック", index=False)
            ws = w.sheets["整合性チェック"]
            # 色付け
            if "severity" in df_validation.columns:
                sev_col_idx = list(df_validation.columns).index("severity") + 1
                sev_col = get_column_letter(sev_col_idx)
                fill_red = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
                fill_yellow = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
                fill_green = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
                rng = f"{sev_col}2:{sev_col}{len(df_validation)+1}"
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{sev_col}2="critical"'], fill=fill_red))
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{sev_col}2="warning"'], fill=fill_yellow))
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{sev_col}2="acceptable"'], fill=fill_green))

    print(f"保存: {xlsx_path}")

# ====== CLI ===================================================================
def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def ask_directory(title: str) -> Optional[str]:
    if not TK_AVAILABLE:
        return None
    try:
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title=title)
        root.destroy()
        return path or None
    except:
        return None

def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="ドメイン定義総合チェックツール")
    parser.add_argument("--dir", help="入力ディレクトリ")
    parser.add_argument("--out-dir", help="出力ディレクトリ")
    parser.add_argument("--mode", choices=["both", "suggestion", "validation"], default="both",
                       help="実行モード: both=両方, suggestion=ドメイン提案のみ, validation=整合性チェックのみ")
    parser.add_argument("--no-gui", action="store_true")
    args = parser.parse_args()

    cfg = DEFAULT_CONFIG.copy()
    cfg["CHECK_MODE"] = args.mode

    in_dir = args.dir
    if not in_dir and not args.no_gui:
        in_dir = ask_directory("入力ディレクトリを選択")
    if not in_dir:
        print("入力ディレクトリが指定されていません")
        return

    if args.out_dir:
        cfg["OUT_DIR"] = args.out_dir

    root_dir = Path(in_dir)
    if not root_dir.exists():
        print(f"ディレクトリが存在しません: {root_dir}")
        return

    # データ読み込み
    domains = load_domains(root_dir, cfg)
    tables = load_tables(root_dir, cfg)

    api_client = ApiClient(cfg)
    api_semaphore = threading.Semaphore(cfg["MAX_CONCURRENT_API"])

    df_suggestion = None
    df_validation = None

    # 機能1: ドメイン提案
    if cfg["CHECK_MODE"] in ["both", "suggestion"]:
        targets = load_targets(root_dir, cfg)
        if targets:
            print("\n[機能1] ドメイン提案処理開始...")
            df_suggestion = process_domain_suggestion(targets, domains, tables, cfg, api_client, api_semaphore)

    # 機能2: 整合性チェック
    if cfg["CHECK_MODE"] in ["both", "validation"]:
        print("\n[機能2] 整合性チェック処理開始...")
        df_validation = process_domain_validation(tables, domains, cfg, api_client, api_semaphore)

    save_outputs(df_suggestion, df_validation, cfg)

    if TK_AVAILABLE and not args.no_gui:
        try:
            messagebox.showinfo("完了", f"処理完了\n保存先: {Path(cfg['OUT_DIR']).resolve()}")
        except:
            pass

if __name__ == "__main__":
    main()
