#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel→用語照合→レポート生成（LLM補助）
 
やること
  1) 指定ディレクトリから Excel を読み込み（単語帳 / 画面項目定義）
  2) OpenAI 互換 API に問い合わせて「一致判定・理由・命名提案」を JSON で返してもらう
  3) 完全一致 / 部分一致 / 不一致 に分類して、理由・提案名を含むレポートを出力
 
前提
  - Python 3.10+
  - pip install pandas openpyxl python-dotenv requests
  - .env に API 情報を設定（下の CONFIG 参照）
 
出力
  - ./out/match_result.xlsx
    - results  : 行明細（source_file/source_sheet を含む）
    - summary  : 完全一致/一部一致/none/total の件数
    - by_file  : 取り込んだファイル別の項目数と冒頭サンプル
 
使い方
  $ python excel_term_matcher.py --dir ./data
  # 列名がデフォルトと違う場合：
  $ python excel_term_matcher.py --dir ./data \
      --screen-col 項目名 --vocab-col 用語
 
実装ポリシー
  - まずはローカル類似度（正規化＋部分一致＋difflib）で候補を 3 件まで出し、
    LLM には「候補と原文」を渡して *最終判定* と *理由* と *不一致時の新提案* を求める。
  - LLM レスポンスは厳密 JSON を要求し、破損時は自動で再試行。
  - ネットワーク障害時はローカル判定のみでフォールバック（reason に明記）。
"""
from __future__ import annotations
 
import argparse
import os
import re
import json
import time
import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import difflib
import concurrent.futures as cf
 
import pandas as pd
import requests
from dotenv import load_dotenv
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
 
# =============================================================
# CONFIG（必要に応じて .env で上書き）
# =============================================================
DEFAULT_CONFIG = {
    # API 設定（OpenAI 互換）
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    # 送信パラメータ（curl互換の指定を.envで上書き可能）
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "800")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
    "TOP_P": float(os.getenv("TOP_P", "0.95")),
    "PRESENCE_PENALTY": float(os.getenv("PRESENCE_PENALTY", "0.0")),
    "FREQUENCY_PENALTY": float(os.getenv("FREQUENCY_PENALTY", "0.0")),
 
    # 任意: パス/追加ヘッダー/組織/プロキシなど
    "OPENAI_PATH": os.getenv("OPENAI_PATH", "/chat/completions"),
    "OPENAI_HEADERS_JSON": os.getenv("OPENAI_HEADERS_JSON", "{\"api-key\":\"8b843f2df20548899f93c0624452ea68\",\"apim-user-id\":\"PIT04447\"}"),  # 既定でAPIMヘッダを付与
    "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", "false").lower() != "false",
    "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "false").lower() != "false",  # 既定でSSL検証OFF（curl -k 相当）,
 
    "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
    "RETRY": int(os.getenv("RETRY", "2")),
 
    # 入力ファイル検出
    "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
    "VOCAB_GLOB": os.getenv("VOCAB_GLOB", "*単語帳*.xlsx"),
 
    # シート名 / 列名（--screen-col/--vocab-col で上書き推奨）
    "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "画面項目定義"),  # 未指定なら先頭シート
    "VOCAB_SHEET": os.getenv("VOCAB_SHEET", "単語"),
    # 画面項目の論理名列
    "SCREEN_COL": os.getenv("SCREEN_COL", "項目名称"),
    # 単語帳の列（論理名=用語、物理名、No）
    "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "論理名"),
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名（正式名称）"),
    # 省略物理名（あれば優先して出力に使用）
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
    "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "No"),
 
    # 正規化・一致判定の閾値
    "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),
    "TOP_K": int(os.getenv("TOP_K", "3")),
 
    # 出力先
    "OUT_DIR": os.getenv("OUT_DIR", "out"),
}
 
# =============================================================
# ユーティリティ
# =============================================================
 
def zenkaku_hankaku_norm(s: str) -> str:
    """日本語を含む文字列の *最低限* の正規化。
    - NFKC で幅・互換文字を正規化
    - 大文字→小文字
    - 先頭末尾の空白除去
    - 連続空白の単一化
    - 記号の一部を空白化してトークン境界を作る
    依存を増やさずに“そこそこ”効く線を狙う。
    """
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s)).lower().strip()
    # 記号→空白（/・,()-_ など）
    s = re.sub(r"[\u3000\s]+", " ", s)  # 全角/半角スペースまとめ
    s = re.sub(r"[\-/・,()\[\]_]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s
 
 
def local_similarity(a: str, b: str) -> float:
    a_n = zenkaku_hankaku_norm(a)
    b_n = zenkaku_hankaku_norm(b)
    if not a_n or not b_n:
        return 0.0
    # 完全一致は満点
    if a_n == b_n:
        return 1.0
    # 部分一致（片方がもう片方を包含）
    if a_n in b_n or b_n in a_n:
        return 0.9
    # それ以外は difflib の近似
    return difflib.SequenceMatcher(None, a_n, b_n).ratio()
 
 
@dataclass
class Candidate:
    term: str
    score: float
 
 
# =============================================================
# Excel I/O
# =============================================================
 
def _get_int_env(name: str) -> Optional[int]:
    v = os.getenv(name, "")
    if v is None or v == "":
        return None
    try:
        return int(v)
    except Exception:
        return None
 
# ヘッダー関連の設定（.env で上書き可能）
HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"  # 既定: 自動検出ON
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", "10"))            # 先頭から何行スキャンするか
SCREEN_HEADER_ROW = _get_int_env("SCREEN_HEADER_ROW")                   # 明示指定（1始まり）
VOCAB_HEADER_ROW  = _get_int_env("VOCAB_HEADER_ROW")                    # 明示指定（1始まり）
 
 
def read_first_sheet(path: Path, sheet_name: Optional[str]) -> pd.DataFrame:
    if sheet_name:
        return pd.read_excel(path, sheet_name=sheet_name)
    # シート未指定なら先頭
    xls = pd.ExcelFile(path)
    return pd.read_excel(path, sheet_name=xls.sheet_names[0])
 
 
def read_excel_with_header_detection(path: Path, sheet_name: Optional[str], required_cols: List[str],
                                     explicit_header_row_1based: Optional[int] = None,
                                     scan_rows: int = 10) -> Tuple[pd.DataFrame, int]:
    """列名が1行目でなくても、ヘッダー行を検出して読み込む。
    戻り値: (DataFrame, 採用したヘッダーの0始まり行番号)
    - explicit_header_row_1based が指定されればそれを優先
    - そうでなければ先頭から scan_rows 行を header=None で読み、
      必須列 required_cols をすべて含む行をヘッダーとみなす
    """
    if explicit_header_row_1based is not None:
        hdr0 = max(0, explicit_header_row_1based - 1)
        df = pd.read_excel(path, sheet_name=sheet_name, header=hdr0)
        return df, hdr0
 
    if not HEADER_DETECT:
        # 既定: 1行目をヘッダーとして読む
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df, 0
 
    # 先頭 scan_rows 行を素で読む（ヘッダー無し）
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    required = {str(c) for c in required_cols if c}
 
    header_row_idx: Optional[int] = None
    for i in range(len(head_df)):
        row_vals = set(str(x).strip() for x in list(head_df.iloc[i].values)
                       if str(x) not in {"", "nan", "一致なし"})
        if required.issubset(row_vals):
            header_row_idx = i
            break
 
    if header_row_idx is None:
        preview = "\n".join(
            [
                f"row{i+1}: " + ", ".join(str(x) for x in head_df.iloc[i].values[:10])
                for i in range(min(5, len(head_df)))
            ]
        )
        raise KeyError(
            f"必須列 {sorted(required)} を含むヘッダー行が見つかりませんでした。\n"
            f"シート先頭{scan_rows}行を確認しましたが一致なし。\nサンプル:\n{preview}"
        )
 
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row_idx)
    return df, header_row_idx
 
def load_screen_and_vocab(
    dir_path: Path,
    cfg: Dict[str, Any],
    screen_col_override: Optional[str] = None,
    vocab_col_override: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
 
    screen_files = sorted(dir_path.glob(cfg["SCREEN_GLOB"]))
    vocab_files  = sorted(dir_path.glob(cfg["VOCAB_GLOB"]))
    if not screen_files:
        raise FileNotFoundError(f"画面項目定義ファイルが見つかりません: {dir_path}/{cfg['SCREEN_GLOB']}")
    if not vocab_files:
        raise FileNotFoundError(f"単語帳ファイルが見つかりません: {dir_path}/{cfg['VOCAB_GLOB']}")
 
    # 必須列名（共通設定 or 引数上書き）
    screen_col    = screen_col_override or cfg["SCREEN_COL"]
    term_col      = vocab_col_override or cfg["VOCAB_TERM_COL"]
    phys_col      = cfg["VOCAB_PHYS_COL"]
    phys_abbr_col = cfg["VOCAB_PHYS_ABBR_COL"]  # 任意
    no_col        = cfg["VOCAB_NO_COL"]
 
    # --- 画面項目定義：各ファイルでヘッダー検出＆列バリデーション ---
    df_s_list: List[pd.DataFrame] = []
    for p in screen_files:
        xls = pd.ExcelFile(p)
        sheet_used = cfg["SCREEN_SHEET"] or xls.sheet_names[0]
        df_s, hdr = read_excel_with_header_detection(
            p, sheet_used,
            required_cols=[screen_col],
            explicit_header_row_1based=SCREEN_HEADER_ROW,
            scan_rows=HEADER_SCAN_ROWS,
        )
        if screen_col not in df_s.columns:
            raise KeyError(f"{p.name}（{sheet_used}）: 必須列 '{screen_col}' が見つかりません。列: {list(df_s.columns)}")
 
        df_s["__source_file"]  = p.name
        df_s["__source_sheet"] = sheet_used
        df_s_list.append(df_s)
 
    # --- 単語帳：各ファイルでヘッダー検出＆列バリデーション ---
    df_v_list: List[pd.DataFrame] = []
    for p in vocab_files:
        xls = pd.ExcelFile(p)
        sheet_used = cfg["VOCAB_SHEET"] or xls.sheet_names[0]
        df_v, hdr = read_excel_with_header_detection(
            p, sheet_used,
            required_cols=[term_col, phys_col, no_col],
            explicit_header_row_1based=VOCAB_HEADER_ROW,
            scan_rows=HEADER_SCAN_ROWS,
        )
        missing = [c for c in [term_col, phys_col, no_col] if c not in df_v.columns]
        if missing:
            raise KeyError(f"{p.name}（{sheet_used}）: 必須列が不足しています: {missing} 列: {list(df_v.columns)}")
        if phys_abbr_col not in df_v.columns:
            df_v[phys_abbr_col] = ""  # 省略物理名は任意列：無ければ空列を追加
 
        df_v_list.append(df_v)
 
    # --- 集約＆前処理 ---
    df_screen = pd.concat(df_s_list, ignore_index=True)
    df_vocab  = pd.concat(df_v_list, ignore_index=True)
 
    # NaN→空文字、空行除去
    df_screen[screen_col] = df_screen[screen_col].fillna("")
    for c in [term_col, phys_col, no_col, phys_abbr_col]:
        df_vocab[c] = df_vocab[c].fillna("")
 
    df_screen = df_screen[df_screen[screen_col].astype(str).str.strip() != ""].copy()
    df_vocab  = df_vocab[df_vocab[term_col].astype(str).str.strip() != ""].copy()
 
    # 照合用キー
    df_vocab["__term_norm"] = df_vocab[term_col].astype(str).map(zenkaku_hankaku_norm)
 
    # 標準名へ
    df_vocab  = df_vocab.rename(columns={term_col: "_term", phys_col: "_phys", phys_abbr_col: "_phys_abbr", no_col: "_no"})
    df_screen = df_screen.rename(columns={screen_col: "_screen"})
    df_screen = df_screen.rename(columns={"__source_file": "_src_file", "__source_sheet": "_src_sheet"})
 
    return df_screen, df_vocab
 
 
# =============================================================
# 候補生成（ローカル）
# =============================================================
 
def top_k_candidates(name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    scored = [Candidate(t, local_similarity(name, t)) for t in vocab_terms]
    scored.sort(key=lambda c: c.score, reverse=True)
    return [c for c in scored[:k] if c.score >= threshold]
 
 
def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語を想定し、トークン/バイグラムでも候補を拾う。
    - 画面項目を正規化→トークン化→ unigram + bigram を作成
    - 各 n-gram に対し vocab との類似度を評価
    - 上位候補をまとめて重複排除
    """
    tokens = [t for t in zenkaku_hankaku_norm(screen_name).split(" ") if t]
    grams = set(tokens)
    for i in range(len(tokens)-1):
        grams.add(tokens[i] + " " + tokens[i+1])
    pool: List[Candidate] = []
    for g in grams:
        for vt in vocab_terms:
            s = local_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))
    # 重複語は最高スコアのみ
    best: Dict[str, float] = {}
    for c in pool:
        best[c.term] = max(best.get(c.term, 0.0), c.score)
    merged = [Candidate(t, sc) for t, sc in best.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[: max(k, 10)]  # 複合語用に少し広めに返す
 
 
# =============================================================
# HTTP / API クライアント層（カスタムヘッダー・プロキシ等）
# =============================================================
class ApiClient:
    def __init__(self, cfg: Dict[str, Any]):
        self.base = cfg["OPENAI_BASE_URL"].rstrip("/")
        self.path = cfg.get("OPENAI_PATH", "/chat/completions")
        self.timeout = cfg["TIMEOUT_SEC"]
        self.verify = cfg["VERIFY_SSL"]
        self.session = requests.Session()
        proxies = {}
        if cfg.get("HTTP_PROXY"): proxies["http"] = cfg["HTTP_PROXY"]
        if cfg.get("HTTPS_PROXY"): proxies["https"] = cfg["HTTPS_PROXY"]
        if proxies:
            self.session.proxies.update(proxies)
 
        # ベースヘッダー
        headers = {"Content-Type": "application/json"}
        if cfg.get("OPENAI_SEND_AUTH") and cfg.get("OPENAI_API_KEY"):
            headers["Authorization"] = f"Bearer {cfg['OPENAI_API_KEY']}"
        if cfg.get("OPENAI_ORG_ID"):
            headers["OpenAI-Organization"] = cfg["OPENAI_ORG_ID"]
        # 追加ヘッダー（JSON で指定）
        extra = cfg.get("OPENAI_HEADERS_JSON")
        if extra:
            try:
                headers.update(json.loads(extra))
            except Exception:
                pass
        self.headers = headers
 
    def post_json(self, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base}{self.path}"
        resp = self.session.post(url, headers=self.headers, json=body, timeout=self.timeout, verify=self.verify)
        resp.raise_for_status()
        return resp.json()
 
# =============================================================
# LLM 呼び出し
# =============================================================
# 統合されたシャープなプロンプトに移行済み
 
 
# =============================================================
# 段階的一致判定システム - 定数
# =============================================================

# 一致判定の閾値
PERFECT_MATCH_THRESHOLD = 0.95
HIGH_CONFIDENCE_THRESHOLD = 0.9
COMPOUND_MATCH_THRESHOLD = 0.8
MIN_COMPOUND_COVERAGE = 0.7
MIN_TOKEN_LENGTH = 2

# LLM設定
MAX_CANDIDATES_FOR_LLM = 5
LLM_MAX_TOKENS = 400
LLM_TEMPERATURE = 0.3

# 一致タイプ
MATCH_TYPE_PERFECT = "完全一致"
MATCH_TYPE_PARTIAL = "一部一致"
MATCH_TYPE_NONE = "一致なし"

# =============================================================
# 段階的一致判定システム - 処理関数
# =============================================================
 
def fallback_reason(screen_name: str, candidates: List[Candidate]) -> Dict[str, Any]:
    if not candidates:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "reason": "API不達/候補なし。後で単語帳を拡充してください。",
            "proposed_name": simple_proposal(screen_name),
        }
    top = candidates[0]
    if top.score >= PERFECT_MATCH_THRESHOLD:
        return create_match_result(
            match_type=MATCH_TYPE_PERFECT,
            matched_term=top.term,
            reason=f"ローカル完全一致（score={top.score:.2f}）",
            physical_name=simple_proposal(top.term),
            coverage_ratio=1.0
        )
    return create_match_result(
        match_type=MATCH_TYPE_PARTIAL,
        matched_term=top.term,
        reason=f"ローカル近似一致（score={top.score:.2f}）。APIフォールバック。",
        physical_name=simple_proposal(top.term),
        coverage_ratio=top.score
    )
 
 
def detect_perfect_match(screen_name: str, candidates: List[Candidate], term_meta: Dict) -> Optional[Dict[str, Any]]:
    """完全一致を検出"""
    screen_norm = zenkaku_hankaku_norm(screen_name)

    for c in candidates:
        term_norm = zenkaku_hankaku_norm(c.term)
        if screen_norm == term_norm and c.score >= PERFECT_MATCH_THRESHOLD:
            return create_match_result(
                match_type=MATCH_TYPE_PERFECT,
                matched_term=c.term,
                reason=f"正規化後文字列完全一致（score={c.score:.2f}）",
                physical_name=get_physical_name(c.term, term_meta),
                coverage_ratio=1.0
            )
    return None


def create_match_result(match_type: str, matched_term: str = None, matched_terms: List[str] = None,
                       reason: str = "", physical_name: str = "", coverage_ratio: float = 0.0) -> Dict[str, Any]:
    """一致結果を作成"""
    return {
        "match_type": match_type,
        "matched_term": matched_term,
        "matched_terms": matched_terms,
        "reason": reason,
        "proposed_name": physical_name,
        "coverage_ratio": coverage_ratio
    }


def get_physical_name(term: str, term_meta: Dict) -> str:
    """用語の物理名を取得（略称優先）"""
    if not term or not term_meta:
        return term or ""

    meta = term_meta.get(term) or {}
    return meta.get("_phys_abbr") or meta.get("_phys") or term


def create_compound_physical_name(matched_terms: List[str], term_meta: Dict, fallback_name: str) -> str:
    """複合語の物理名を作成"""
    phys_parts = []
    for term in matched_terms:
        phys = get_physical_name(term, term_meta)
        if phys:
            phys_parts.append(phys)

    return simple_proposal(" ".join(phys_parts)) if phys_parts else simple_proposal(fallback_name)


def enhanced_match_detection(screen_name: str, candidates: List[Candidate], term_meta: Dict, cfg: Dict[str, Any], api_client: ApiClient) -> Dict[str, Any]:
    """段階的な一致判定：Python事前処理 + LLM最終判定"""
    if not candidates:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": "候補なし",
            "proposed_name": simple_proposal(screen_name),
            "coverage_ratio": 0.0
        }

    screen_norm = zenkaku_hankaku_norm(screen_name)
    screen_tokens = set(screen_norm.split())

    # 段階1: 完全一致の検出
    perfect_match = detect_perfect_match(screen_name, candidates, term_meta)
    if perfect_match:
        return perfect_match

    # 段階2: 高精度部分一致の検出
    high_confidence_match = detect_high_confidence_partial_match(screen_name, candidates, term_meta)
    if high_confidence_match:
        return high_confidence_match

    # 段階3: LLMによる複雑な判定（トークン最適化済み）
    return optimized_llm_call(screen_name, candidates, term_meta, cfg, api_client)


def detect_high_confidence_partial_match(screen_name: str, candidates: List[Candidate], term_meta: Dict) -> Optional[Dict[str, Any]]:
    """高精度な部分一致をPythonで検出"""
    screen_norm = zenkaku_hankaku_norm(screen_name)
    screen_tokens = set(screen_norm.split())

    # 包含関係による部分一致（高スコア）
    for c in candidates:
        if c.score >= HIGH_CONFIDENCE_THRESHOLD:
            term_norm = zenkaku_hankaku_norm(c.term)
            # 完全包含パターン
            if (screen_norm in term_norm or term_norm in screen_norm) and len(screen_norm) >= MIN_TOKEN_LENGTH + 1:
                coverage = min(len(term_norm), len(screen_norm)) / max(len(term_norm), len(screen_norm))
                return create_match_result(
                    match_type=MATCH_TYPE_PARTIAL,
                    matched_term=c.term,
                    reason=f"文字列包含による部分一致（score={c.score:.2f}）",
                    physical_name=get_physical_name(c.term, term_meta),
                    coverage_ratio=coverage
                )

    # 複合語の単純パターン検出
    compound_match = detect_simple_compound_match(screen_name, candidates, term_meta)
    if compound_match:
        return compound_match

    return None


def detect_simple_compound_match(screen_name: str, candidates: List[Candidate], term_meta: Dict) -> Optional[Dict[str, Any]]:
    """単純な複合語パターンをPythonで検出"""
    screen_norm = zenkaku_hankaku_norm(screen_name)
    screen_tokens = [t for t in screen_norm.split() if len(t) >= MIN_TOKEN_LENGTH]

    if len(screen_tokens) < 2:
        return None

    # 各トークンに対応する候補を探す
    matched_terms = []
    total_coverage = 0

    for token in screen_tokens:
        best_match = None
        best_score = 0
        for c in candidates:
            term_norm = zenkaku_hankaku_norm(c.term)
            if token in term_norm or term_norm in token:
                score = local_similarity(token, term_norm)
                if score > best_score and score >= COMPOUND_MATCH_THRESHOLD:
                    best_match = c.term
                    best_score = score
        if best_match:
            matched_terms.append(best_match)
            total_coverage += best_score

    # 複数用語の組み合わせで高カバレッジの場合
    if len(matched_terms) >= 2 and total_coverage / len(screen_tokens) >= MIN_COMPOUND_COVERAGE:
        # 複合語の物理名提案を作成
        compound_physical_name = create_compound_physical_name(matched_terms, term_meta, screen_name)
        coverage_ratio = total_coverage / len(screen_tokens)

        return create_match_result(
            match_type=MATCH_TYPE_PARTIAL,
            matched_terms=matched_terms,
            reason=f"複数用語の組み合わせ（{len(matched_terms)}語、カバレッジ={coverage_ratio:.2f}）",
            physical_name=compound_physical_name,
            coverage_ratio=coverage_ratio
        )

    return None


def optimized_llm_call(screen_name: str, candidates: List[Candidate], term_meta: Dict, cfg: Dict[str, Any], api_client: ApiClient) -> Dict[str, Any]:
    """トークン最適化されたLLM呼び出し"""
    # 候補を絞り込み
    top_candidates = candidates[:MAX_CANDIDATES_FOR_LLM]

    # シャープで集中的なプロンプト
    sharp_system = (
        "用語統一の専門家として判定してください。\n\n"
        "判定:\n"
        "完全一致→意味・表記が等しい\n"
        "部分一致→略語・語順・同義語・複合語の一部\n"
        "一致なし→適切な候補なし\n\n"
        "物理名:\n"
        "完全一致→候補physをそのまま使用\n"
        "その他→ローワーキャメル8文字程度で新規作成（英語優先、わかりやすく）\n\n"
        "JSONのみ。"
    )

    # 最小限の候補情報
    cand_payload = []
    for c in top_candidates:
        meta = term_meta.get(c.term) or {}
        phys = meta.get("_phys_abbr") or meta.get("_phys")
        cand_payload.append({
            "term": c.term,
            "phys": phys,
            "score": round(c.score, 2)
        })

    payload = {
        "model": cfg["OPENAI_MODEL"],
        "max_tokens": min(cfg.get("MAX_TOKENS", LLM_MAX_TOKENS), LLM_MAX_TOKENS),
        "temperature": LLM_TEMPERATURE,
        "messages": [
            {"role": "system", "content": sharp_system},
            {
                "role": "user",
                "content": f"""項目名: {screen_name}
候補: {json.dumps(cand_payload, ensure_ascii=False)}

複合語→matched_terms、単一語→matched_term

{{"match_type": "", "matched_term": null, "matched_terms": [], "reason": "", "proposed_name": "", "coverage_ratio": 0.0}}"""
            }
        ]
    }

    # LLM呼び出し（失敗時はフォールバック）
    try:
        data = api_client.post_json(payload)
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)

        # 物理名の最終調整
        if result.get("match_type") == MATCH_TYPE_PERFECT and result.get("matched_term"):
            result["proposed_name"] = get_physical_name(result["matched_term"], term_meta)

        return result
    except Exception:
        return fallback_reason(screen_name, candidates)


def simple_proposal(screen_name: str) -> str:
    """ローワーキャメルケースの物理名を簡易生成"""
    s = zenkaku_hankaku_norm(screen_name)
    s = re.sub(r"\s+", " ", s)
    tokens = [t for t in s.split(" ") if t]
    if not tokens:
        return "newItem"

    # 代表 2–3 語まで
    core = tokens[:3]
    # よくある冗長語の削り（例）
    stop = {"コード", "番号", "名称名", "名称名称"}
    core = [w for w in core if w not in stop]

    if not core:
        return "newItem"

    # ローワーキャメルケースに変換（簡易版）
    # 最初の語は小文字、以降は最初の文字を大文字に
    result = core[0].lower()
    for word in core[1:]:
        if word:
            result += word.capitalize()

    # 8文字程度に制限
    if len(result) > 10:
        result = result[:8]

    return result or "newItem"
 
 
# =============================================================
# メイン処理
# =============================================================
 
def process(dir_path: Path, screen_col: Optional[str], vocab_col: Optional[str], cfg: Dict[str, Any]) -> pd.DataFrame:
    df_screen, df_vocab = load_screen_and_vocab(dir_path, cfg, screen_col, vocab_col)
 
    vocab_terms = df_vocab["_term"].astype(str).tolist()
    term_meta = (
        df_vocab[["_term", "_phys", "_phys_abbr", "_no"]]
        .drop_duplicates("_term")
        .set_index("_term")
        .to_dict(orient="index")
    )
 
    rows: List[Dict[str, Any]] = []
    api_client = ApiClient(cfg)
 
    def worker(screen_name: str, src_file: str, src_sheet: Optional[str]) -> Dict[str, Any]:
        cands_broad = phrase_candidates(screen_name, vocab_terms, max(cfg["TOP_K"], 6), cfg["FUZZY_THRESHOLD"])
        cands_direct = top_k_candidates(screen_name, vocab_terms, cfg["TOP_K"], cfg["FUZZY_THRESHOLD"])
        merged_map: Dict[str, float] = {}
        for c in cands_broad + cands_direct:
            merged_map[c.term] = max(merged_map.get(c.term, 0.0), c.score)
        merged = [Candidate(t, s) for t, s in merged_map.items()]
        merged.sort(key=lambda c: c.score, reverse=True)
        merged = merged[: max(cfg["TOP_K"], 10)]
 
        # より精密な事前処理と段階的判定
        llm = enhanced_match_detection(screen_name, merged, term_meta, cfg, api_client)
 
        cov = llm.get("coverage_ratio")
        try:
            cov = float(cov) if cov is not None else None
        except Exception:
            cov = None
 
        top = merged[0].term if merged else None
        top_score = merged[0].score if merged else None
 
        def meta_of(term: Optional[str]):
            if not term:
                return {"no": None, "phys": None, "phys_abbr": None}
            m = term_meta.get(str(term)) or {}
            return {"no": m.get("_no"), "phys": m.get("_phys"), "phys_abbr": m.get("_phys_abbr")}
 
        mt = llm.get("matched_term")
        mts = llm.get("matched_terms") or []
        mt_meta = meta_of(mt)
        mts_meta = [meta_of(t) for t in mts]
 
        return {
            "source_file": src_file,
            "source_sheet": src_sheet,
            "screen_item": screen_name,
            "match_type": llm.get("match_type"),
            "matched_term": mt or None,
            "matched_term_no": mt_meta["no"],
            "matched_term_phys": (mt_meta.get("phys_abbr") or mt_meta.get("phys")),
            "matched_terms": ", ".join(mts) or None,
            "matched_terms_nos": ", ".join([str(m.get("no")) for m in mts_meta if m.get("no")]) or None,
            "matched_terms_phys": ", ".join([str((m.get("phys_abbr") or m.get("phys"))) for m in mts_meta if (m.get("phys_abbr") or m.get("phys"))]) or None,
            "local_top_term": top,
            "local_top_term_no": (term_meta.get(top) or {}).get("_no") if top else None,
            "local_top_term_phys": ((term_meta.get(top) or {}).get("_phys_abbr") or (term_meta.get(top) or {}).get("_phys")) if top else None,
            "local_top_score": top_score,
            "coverage_ratio": cov,
            "reason": llm.get("reason"),
            "proposed_name": llm.get("proposed_name"),
        }
 
    items = df_screen[["_screen", "_src_file", "_src_sheet"]].astype(str).values.tolist()
    with cf.ThreadPoolExecutor(max_workers=cfg["MAX_WORKERS"]) as ex:
        futures = [ex.submit(worker, it[0], it[1], it[2]) for it in items]
        for fut in cf.as_completed(futures):
            rows.append(fut.result())
 
    df = pd.DataFrame(rows).reset_index(drop=True)
    return df
 
def save_outputs(df: pd.DataFrame, cfg: Dict[str, Any]):
    out_dir = Path(cfg["OUT_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx = out_dir / "match_result.xlsx"
 
    # 列の並び（元ファイル情報を先頭に配置）
    cols = [
        "source_file", "source_sheet",
        "screen_item", "match_type",
        "matched_term", "matched_term_no", "matched_term_phys",
        "matched_terms", "matched_terms_nos", "matched_terms_phys",
        "local_top_term", "local_top_term_no", "local_top_term_phys", "local_top_score",
        "coverage_ratio", "proposed_name", "reason",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]
 
    # 列名を業務ユーザーにとって分かりやすく変更
    df.columns = [
        "読み込み元ファイル", "読み込み元シート",
        "画面項目名", "単語帳との一致状況",
        "単語帳で一致した用語", "一致用語の番号", "一致用語のシステム名",
        "複数用語での一致", "複数用語の番号", "複数用語のシステム名",
        "最も近い用語", "最も近い用語の番号", "最も近い用語のシステム名", "類似度スコア",
        "単語帳カバー率", "推奨物理名", "判定理由",
    ]
 
    # 件数サマリ
    cnt = df["単語帳との一致状況"].value_counts(dropna=False).to_dict()
    summary_df = pd.DataFrame([
        {"メトリクス": "完全一致", "件数": cnt.get("完全一致", 0)},
        {"メトリクス": "部分一致", "件数": cnt.get("一部一致", 0)},
        {"メトリクス": "一致なし", "件数": cnt.get("一致なし", 0)},
        {"メトリクス": "合計", "件数": len(df)},
    ])
 
    # ファイル別サマリ
    by_file_df = (
        df.groupby(["読み込み元ファイル", "読み込み元シート"])['画面項目名']
          .agg(項目数='count', 項目名サンプル=lambda s: ", ".join(map(str, s.head(50))))
          .reset_index()
    )
 
    # Excel一冊に複数シートで保存
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="結果", index=False)
        summary_df.to_excel(writer, sheet_name="サマリ", index=False)
        by_file_df.to_excel(writer, sheet_name="ファイル別サマリ", index=False)
 
    print(f"保存: {xlsx}")
 
# =============================================================
# CLI（対話入力対応：引数が無ければフォルダ選択ダイアログ）
# =============================================================
 
def app_root() -> Path:
    if getattr(sys, "frozen", False):  # PyInstaller onefile
        return Path(sys.executable).parent
    return Path(__file__).parent
 
 
def ask_directory(title: str, initial: Optional[str] = None) -> Optional[str]:
    try:
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title=title, initialdir=initial or str(app_root()))
        root.destroy()
        return path if path else None
    except Exception:
        return None
 
 
def main():
    load_dotenv()  # .env の読み込み（あれば）
 
    # EXE と同じ場所を作業ディレクトリに（ダブルクリック起動のズレ防止）
    try:
        os.chdir(app_root())
    except Exception:
        pass
 
    parser = argparse.ArgumentParser(description="Excel 用語照合（LLM 補助）")
    parser.add_argument("--dir", help="入力ディレクトリ（画面項目定義・単語帳）")
    parser.add_argument("--in-dir", help="上と同じ（--dir と同義。後方互換）")
    parser.add_argument("--out-dir", help="出力ディレクトリ（既定: out）")
    parser.add_argument("--screen-col", help="画面項目定義の列名（デフォルト: 項目名）")
    parser.add_argument("--vocab-col", help="単語帳の列名（デフォルト: 用語）")
    args = parser.parse_args()
 
    cfg = DEFAULT_CONFIG.copy()
 
    # 認証ヘッダにBearerを付ける設定だがキーがない場合の注意
    if cfg.get("OPENAI_SEND_AUTH") and not cfg.get("OPENAI_API_KEY"):
        print("[警告] OPENAI_SEND_AUTH=true ですが OPENAI_API_KEY が未設定です。Authorization は送信されません。")
 
    # 入力ディレクトリの解決（引数→ダイアログ→コンソール）
    in_dir = args.in_dir or args.dir
    if not in_dir:
        in_dir = ask_directory("入力ディレクトリ（画面項目定義・単語帳）を選択")
        if not in_dir:
            try:
                in_dir = input("入力ディレクトリのパスを入力してください: ").strip()
            except Exception:
                in_dir = None
 
    if not in_dir:
        raise FileNotFoundError("入力ディレクトリが指定されていません。--dir かダイアログで指定してください。")
 
    # 出力ディレクトリの解決（引数優先。無ければ既定 'out'。ユーザーが選ぶ場合はダイアログで上書き可）
    if args.out_dir:
        cfg["OUT_DIR"] = args.out_dir
    else:
        # 任意：ダイアログで明示選択したい場合のみ選ばせる（キャンセルなら既定 'out' 維持）
        chosen = ask_directory("出力ディレクトリ（保存先）を選択（キャンセルで既定の out）")
        if chosen:
            cfg["OUT_DIR"] = chosen
 
    dir_path = Path(in_dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {dir_path}")
 
    df = process(dir_path, args.screen_col, args.vocab_col, cfg)
    save_outputs(df, cfg)
    try:
        messagebox.showinfo("完了", f"出力が完了しました。保存先: {Path(cfg['OUT_DIR']).resolve()}\match_result.xlsx")
    except Exception:
        pass
 
 
if __name__ == "__main__":
    main()