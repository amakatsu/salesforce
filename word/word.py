#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel→単語照合→レポート生成（LLM補助）
 
"""
from __future__ import annotations
 
import argparse
import concurrent.futures as cf
import difflib
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
 
# ====== 定数（読みやすさのため一箇所に集約） ===============================
# 「事実上の完全一致」と見なすスコア（difflibは1.0に非常に近づく）
HARD_EXACT_SCORE = 1.0  # 完全一致のみに限定
# LLMフォールバック時に"完全一致"扱いにする安全側の下限
FALLBACK_EXACT_FLOOR = 0.95
 
# ====== 設定（.envで上書き可） =============================================
DEFAULT_CONFIG: Dict[str, Any] = {
    # --- API（OpenAI互換）
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "OPENAI_PATH": os.getenv("OPENAI_PATH", "/chat/completions"),
    "OPENAI_HEADERS_JSON": os.getenv("OPENAI_HEADERS_JSON", "{\"api-key\":\"8b843f2df20548899f93c0624452ea68\",\"apim-user-id\":\"PIT04447\"}"),
    "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", "false").lower() != "false",
    "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "false").lower() != "false",
 
    # --- 生成パラメタ
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "800")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7")),
    "TOP_P": float(os.getenv("TOP_P", "0.95")),
    "PRESENCE_PENALTY": float(os.getenv("PRESENCE_PENALTY", "0.0")),
    "FREQUENCY_PENALTY": float(os.getenv("FREQUENCY_PENALTY", "0.0")),
 
    # --- 入力検出
    "SCREEN_GLOB": os.getenv("SCREEN_GLOB", "*画面項目定義*.xlsx"),
    "VOCAB_GLOB": os.getenv("VOCAB_GLOB", "*単語名一覧*.xlsx"),
 
    # --- シート/列（必要に応じて引数で上書き）
    # シート名は複数指定可能（カンマ区切り）例: "画面項目定義,システム設計書,IF定義書"
    # ワイルドカード指定可能（*）例: "*" で全シート、"画面*" で「画面」で始まるシート
    # デフォルト "*" で全シートを読み込むことで、ファイル構造に依存しない柔軟な運用が可能
    "SCREEN_SHEET": os.getenv("SCREEN_SHEET", "*"),
    "VOCAB_SHEET": os.getenv("VOCAB_SHEET", "*"),
    "SCREEN_COL": os.getenv("SCREEN_COL", "項目名称"),
    "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "論理名"),
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名（正式名称）"),
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
    "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "No"),
 
    # --- 類似度設定
    "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),  # 候補プールの下限
    "TOP_K": int(os.getenv("TOP_K", "3")),  # 直接候補の上位件数
 
    # --- 出力
    "OUT_DIR": os.getenv("OUT_DIR", "out"),
 
    # --- 実行制御
    "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
    "RETRY": int(os.getenv("RETRY", "2")),
 
    # --- レート制限（サーバー負荷対策）
    # 同時実行するAPI呼び出しの最大数（MAX_WORKERSより小さい値にするとAPI負荷を抑制）
    "MAX_CONCURRENT_API": int(os.getenv("MAX_CONCURRENT_API", "5"))
}
 
# ====== 文字列正規化／類似度 =================================================
 
def zenkaku_hankaku_norm(text: str) -> str:
    """NFKC正規化 + 小文字化 + 記号/空白の正規化で**照合の土台**を整える。"""
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = re.sub(r"[\u3000\s]+", " ", s)          # 全角/半角スペースを単一化
    s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)    # 区切り記号はスペースへ
    return re.sub(r"\s+", " ", s)
 
 
def local_similarity(a: str, b: str) -> float:
    """簡易類似度：完全一致=1.0 / 片包含=0.9 / それ以外はdifflibのratio。"""
    a_n, b_n = zenkaku_hankaku_norm(a), zenkaku_hankaku_norm(b)
    if not a_n or not b_n:
        return 0.0
    if a_n == b_n:
        return 1.0
    if a_n in b_n or b_n in a_n:
        return 0.9
    return difflib.SequenceMatcher(None, a_n, b_n).ratio()
 
@dataclass
class Candidate:
    term: str
    score: float
 
# ====== Excel I/O =============================================================
 
def _int_env(name: str) -> Optional[int]:
    v = os.getenv(name, "")
    try:
        return int(v) if v else None
    except Exception:
        return None
 
HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", "10"))
SCREEN_HEADER_ROW = _int_env("SCREEN_HEADER_ROW")
VOCAB_HEADER_ROW = _int_env("VOCAB_HEADER_ROW")
 
 
def _pick_sheet_or_fallback(xls: pd.ExcelFile, preferred: Optional[str]) -> str:
    """優先シートが無ければ先頭。NFKCで厳密同名も考慮。"""
    if preferred and preferred in xls.sheet_names:
        return preferred
    if preferred:
        norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()
        want = norm(preferred)
        for name in xls.sheet_names:
            if norm(name) == want:
                return name
    return xls.sheet_names[0]
 
 
def _pick_matching_sheets(xls: pd.ExcelFile, preferred: Optional[str]) -> List[str]:
    """設定シート名にマッチする全てのシートを返す。ワイルドカード対応。"""
    if not preferred:
        return [xls.sheet_names[0]]
 
    norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()
 
    # 複数パターンをカンマ区切りで分割
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]
 
    all_matches = []
 
    for pattern in patterns:
        want = norm(pattern)
 
        # ワイルドカード対応（*を正規表現に変換）
        import re as regex_module
        regex_pattern = want.replace('*', '.*')
        for name in xls.sheet_names:
            if regex_module.match(regex_pattern, norm(name)):
                all_matches.append(name)
 
    # 重複を除去して順序を保持
    result = []
    seen = set()
    for sheet in all_matches:
        if sheet not in seen:
            result.append(sheet)
            seen.add(sheet)
 
    # マッチするものがなければ先頭シート
    return result if result else [xls.sheet_names[0]]
 
 
def _detect_header_row(path: Path, sheet_name: str, required_cols: List[str], scan_rows: int) -> int:
    """先頭scan_rows行で必須列がそろう行を**ヘッダ行**とみなす。"""
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)
    req = {zenkaku_hankaku_norm(c) for c in required_cols if c}
    for i in range(len(head_df)):
        row_vals = {zenkaku_hankaku_norm(x) for x in head_df.iloc[i].values if str(x) not in {"", "nan", "一致なし"}}
        if req.issubset(row_vals):
            return i
    raise KeyError(f"必須列{sorted(required_cols)}を含むヘッダ行が見つかりません: {path.name}/{sheet_name}")
 
 
def read_excel_with_header_detection(path: Path, sheet_name: Optional[str], required_cols: List[str],
                                     explicit_header_row_1based: Optional[int] = None,
                                     scan_rows: int = 30) -> Tuple[pd.DataFrame, int]:
    """ヘッダ行が1行目とは限らないExcelに対応。"""
    if explicit_header_row_1based is not None:
        hdr0 = max(0, explicit_header_row_1based - 1)
        return pd.read_excel(path, sheet_name=sheet_name, header=hdr0), hdr0
    if not HEADER_DETECT:
        return pd.read_excel(path, sheet_name=sheet_name), 0
    # ヘッダ行の自動検出
    header_row = _detect_header_row(path, sheet_name, required_cols, scan_rows)
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row), header_row
 
 
def load_screen_and_vocab(dir_path: Path, cfg: Dict[str, Any],
                          screen_col_override: Optional[str] = None,
                          vocab_col_override: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """単一ディレクトリから『画面項目定義』群と『単語帳』群を収集して前処理。"""
    screen_files = sorted(dir_path.glob(cfg["SCREEN_GLOB"]))
    vocab_files = sorted(dir_path.glob(cfg["VOCAB_GLOB"]))
    if not screen_files:
        raise FileNotFoundError(f"画面項目定義ファイルが見つかりません: {dir_path}/{cfg['SCREEN_GLOB']}")
    if not vocab_files:
        raise FileNotFoundError(f"単語帳ファイルが見つかりません: {dir_path}/{cfg['VOCAB_GLOB']}")
 
    screen_col = screen_col_override or cfg["SCREEN_COL"]
    term_col = vocab_col_override or cfg["VOCAB_TERM_COL"]
    phys_col = cfg["VOCAB_PHYS_COL"]
    phys_abbr_col = cfg["VOCAB_PHYS_ABBR_COL"]
    no_col = cfg["VOCAB_NO_COL"]
 
    # --- 画面項目定義を縦結合（複数シート対応）
    screen_frames: List[pd.DataFrame] = []
    for path in screen_files:
        xls = pd.ExcelFile(path)
        matching_sheets = _pick_matching_sheets(xls, cfg["SCREEN_SHEET"]) if cfg["SCREEN_SHEET"] else [xls.sheet_names[0]]
 
        for sheet_used in matching_sheets:
            try:
                df_s, _ = read_excel_with_header_detection(path, sheet_used, [screen_col], SCREEN_HEADER_ROW, HEADER_SCAN_ROWS)
                if screen_col not in df_s.columns:
                    print(f"[警告] {path.name}（{sheet_used}）: 必須列 '{screen_col}' が存在しません - スキップ")
                    continue
                df_s["__source_file"], df_s["__source_sheet"] = path.name, sheet_used
                screen_frames.append(df_s)
                print(f"[INFO] 画面項目定義読み込み: {path.name} / {sheet_used} ({len(df_s)}件)")
            except Exception as e:
                print(f"[警告] {path.name}（{sheet_used}）の読み込みエラー: {e} - スキップ")
 
    # --- 単語帳を縦結合（複数シート対応）
    vocab_frames: List[pd.DataFrame] = []
    for path in vocab_files:
        xls = pd.ExcelFile(path)
        matching_sheets = _pick_matching_sheets(xls, cfg["VOCAB_SHEET"]) if cfg["VOCAB_SHEET"] else [xls.sheet_names[0]]
 
        for sheet_used in matching_sheets:
            try:
                df_v, _ = read_excel_with_header_detection(path, sheet_used, [term_col, phys_col, no_col], VOCAB_HEADER_ROW, HEADER_SCAN_ROWS)
                missing = [c for c in [term_col, phys_col, no_col] if c not in df_v.columns]
                if missing:
                    print(f"[警告] {path.name}（{sheet_used}）: 必須列が不足: {missing} - スキップ")
                    continue
                if phys_abbr_col not in df_v.columns:
                    df_v[phys_abbr_col] = ""  # 任意列は空で補完
                vocab_frames.append(df_v)
                print(f"[INFO] 単語帳読み込み: {path.name} / {sheet_used} ({len(df_v)}件)")
            except Exception as e:
                print(f"[警告] {path.name}（{sheet_used}）の読み込みエラー: {e} - スキップ")
 
    # データフレームの結合（空チェック付き）
    if not screen_frames:
        raise FileNotFoundError(f"読み込み可能な画面項目定義シートが見つかりません")
    if not vocab_frames:
        raise FileNotFoundError(f"読み込み可能な単語帳シートが見つかりません")
 
    df_screen = pd.concat(screen_frames, ignore_index=True)
    df_vocab = pd.concat(vocab_frames, ignore_index=True)
 
    print(f"[INFO] 合計読み込み: 画面項目定義 {len(df_screen)}件, 単語帳 {len(df_vocab)}件")
 
    # --- 欠損・空行の整理
    df_screen[screen_col] = df_screen[screen_col].fillna("")
    for c in [term_col, phys_col, no_col, phys_abbr_col]:
        df_vocab[c] = df_vocab[c].fillna("")
    df_screen = df_screen[df_screen[screen_col].astype(str).str.strip() != ""].copy()
    df_vocab = df_vocab[df_vocab[term_col].astype(str).str.strip() != ""].copy()
 
    # --- 照合キー追加・列名整理
    df_vocab["__term_norm"] = df_vocab[term_col].astype(str).map(zenkaku_hankaku_norm)
    df_vocab = df_vocab.rename(columns={term_col: "_term", phys_col: "_phys", phys_abbr_col: "_phys_abbr", no_col: "_no"})
    df_screen = df_screen.rename(columns={screen_col: "_screen", "__source_file": "_src_file", "__source_sheet": "_src_sheet"})
 
    return df_screen, df_vocab
 
# ====== 候補生成（ローカル） ==================================================
 
def top_k_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """画面項目 vs 単語帳の**直接照合**で上位k件を返却。"""
    scored = [Candidate(term, local_similarity(screen_name, term)) for term in vocab_terms]
    scored.sort(key=lambda c: c.score, reverse=True)
    return [c for c in scored[:k] if c.score >= threshold]
 
 
def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語対策：unigram/bigram に分解してパーツ単位で候補を拾う。"""
    tokens = [t for t in zenkaku_hankaku_norm(screen_name).split(" ") if t]
    grams = set(tokens)
    for i in range(len(tokens) - 1):
        grams.add(tokens[i] + " " + tokens[i + 1])
    pool: List[Candidate] = []
    for g in grams:
        for vt in vocab_terms:
            s = local_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))
    # 同一単語は最大スコアを採用
    best_by_term: Dict[str, float] = {}
    for cand in pool:
        best_by_term[cand.term] = max(best_by_term.get(cand.term, 0.0), cand.score)
    merged = [Candidate(t, sc) for t, sc in best_by_term.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[: max(k, 10)]
 
# ====== APIクライアント =======================================================
class ApiClient:
    """OpenAI互換APIへの最小ラッパ（ヘッダ/プロキシ/SSL検証対応）。"""
    def __init__(self, cfg: Dict[str, Any]):
        self.base_url = cfg["OPENAI_BASE_URL"].rstrip("/")
        self.path = cfg["OPENAI_PATH"]
        self.timeout = cfg["TIMEOUT_SEC"]
        self.verify = cfg["VERIFY_SSL"]
        self.session = requests.Session()  # ThreadPool内ではスレッド毎の生成を推奨
        # プロキシ
        proxies: Dict[str, str] = {}
        if cfg.get("HTTP_PROXY"):
            proxies["http"] = cfg["HTTP_PROXY"]
        if cfg.get("HTTPS_PROXY"):
            proxies["https"] = cfg["HTTPS_PROXY"]
        if proxies:
            self.session.proxies.update(proxies)
        # ヘッダ
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if cfg.get("OPENAI_SEND_AUTH") and cfg.get("OPENAI_API_KEY"):
            headers["Authorization"] = f"Bearer {cfg['OPENAI_API_KEY']}"
        if cfg.get("OPENAI_ORG_ID"):
            headers["OpenAI-Organization"] = cfg["OPENAI_ORG_ID"]
        extra = cfg.get("OPENAI_HEADERS_JSON")
        if extra:
            try:
                headers.update(json.loads(extra))
            except Exception:
                pass
        self.headers = headers
 
    def post_json(self, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{self.path}"
        resp = self.session.post(url, headers=self.headers, json=body, timeout=self.timeout, verify=self.verify)
        resp.raise_for_status()
        return resp.json()
 
# ====== LLM呼び出し（プロンプト詳細は割愛） ================================
LLM_SYSTEM = (
    "あなたは業務システムの画面設計と単語統一の専門家です。"
    "与えられた『画面項目名』と『単語帳候補（上位スコア順）』を比較して、"
    "「完全一致 / 一部一致 / 一致なし」を厳密に判定し、理由を日本語で簡潔に述べてください。"
    "複合語の可能性を検討し、必要なら組み合わせ単語を返す。"
    "全一致タイプでローワーキャメルの物理名を1つ提案。"
    "JSONのみを返すこと。"
    "禀はrinと読むこと"
)
 
LLM_USER_TEMPLATE = (
    """
    # 画面項目名
    {screen_name}
 
    # 単語帳候補（上位スコア順）
    {candidates_json}
 
    # 厳密 JSON 仕様（複合語対応）
    {{
      "match_type": "完全一致" | "一部一致" | "一致なし",
      "matched_term": string | null,
      "matched_terms": string[] | null,
      "reason": string,
      "proposed_name": string,
      "coverage_ratio": number | null
    }}
 
    制約:
    - 完全一致 は意味も表記も等しい場合のみ。
    - 一部一致 は略語/語順違い/同義近似など採用余地がある場合。
    - 複合語が適切なら matched_terms を優先。
    - 一致なし は候補が不適切な場合。簡潔かつ具体的に。
    - proposed_name は必須。coverage_ratio は 0.0~1.0。
    - 返答は JSON のみ。
    """
)
 
 
def build_llm_payload(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any]) -> Dict[str, Any]:
    """LLM呼び出しペイロードを構築（厳密JSON指定）。"""
    cand_payload = [{"term": c.term, "local_score": round(c.score, 4)} for c in candidates]
    return {
        "model": cfg["OPENAI_MODEL"],
        "max_tokens": cfg["MAX_TOKENS"],
        "temperature": cfg["TEMPERATURE"],
        "top_p": cfg["TOP_P"],
        "presence_penalty": cfg["PRESENCE_PENALTY"],
        "frequency_penalty": cfg["FREQUENCY_PENALTY"],
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": LLM_SYSTEM},
            {"role": "user", "content": LLM_USER_TEMPLATE.format(
                screen_name=screen_name,
                candidates_json=json.dumps(cand_payload, ensure_ascii=False, indent=2),
            )},
        ],
    }
 
 
def call_llm(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any], client: Optional[ApiClient] = None, api_semaphore: Optional[threading.Semaphore] = None) -> Dict[str, Any]:
    """LLM呼び出し。失敗時はフォールバック。"""
    # テストモード判定
    if cfg.get("TEST_MODE", False) or os.getenv("WORD_MATCHING_TEST_MODE", "false").lower() == "true":
        try:
            from mock_api import mock_llm_response
            return mock_llm_response(screen_name, candidates)
        except ImportError:
            print("[警告] mock_api.pyが見つかりません。フォールバックを使用します。")
            return fallback_reason(screen_name, candidates)
 
    client = client or ApiClient(cfg)
    payload = build_llm_payload(screen_name, candidates, cfg)
 
    # サーバー負荷対策：セマフォで同時実行API数を制限
    if api_semaphore:
        api_semaphore.acquire()
 
    try:
        for attempt in range(cfg["RETRY"] + 1):
            try:
                data = client.post_json(payload)
                content = data["choices"][0]["message"]["content"]
                result = json.loads(content)
                # ざっくり必須キーを確認
                if not {"match_type", "matched_term", "reason", "proposed_name"}.issubset(result):
                    raise ValueError("LLM JSON schema mismatch")
                return result
            except Exception:
                if attempt < cfg["RETRY"]:
                    time.sleep(1.2 * (attempt + 1))  # バックオフ
                    continue
                return fallback_reason(screen_name, candidates)
    finally:
        if api_semaphore:
            api_semaphore.release()
 
 
def fallback_reason(screen_name: str, candidates: List[Candidate]) -> Dict[str, Any]:
    """ネットワーク障害や破損時の**最小限の結論**。"""
    if not candidates:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "reason": "API不達/候補なし。後日、単語帳の拡充を検討してください。",
            "proposed_name": simple_proposal(screen_name),
        }
    top = candidates[0]
    if top.score >= FALLBACK_EXACT_FLOOR:
        return {
            "match_type": "完全一致",
            "matched_term": top.term,
            "reason": f"ローカル完全一致（score={top.score:.2f}）",
            "proposed_name": simple_proposal(top.term),
        }
    return {
        "match_type": "一部一致",
        "matched_term": top.term,
        "reason": f"ローカル近似一致（score={top.score:.2f}）。APIフォールバック。",
        "proposed_name": simple_proposal(top.term),
    }
 
# ====== 簡易物理名生成 =======================================================
 
def simple_proposal(text: str) -> str:
    """ローワーキャメルの簡易物理名を生成（8〜10文字程度）。"""
    s = zenkaku_hankaku_norm(text)
    tokens = [t for t in re.split(r"\s+", s) if t]
    if not tokens:
        return "newItem"
    # 冗長語の削ぎ落とし
    stop_words = {"コード", "番号", "名称名", "名称名称"}
    core = [w for w in tokens[:3] if w not in stop_words] or tokens[:2]
    # lowerCamelCase化
    name = core[0].lower() + "".join(w.capitalize() for w in core[1:])
    # 長さ制御（長すぎると読みにくい）
    return (name[:8] if len(name) > 10 else name) or "newItem"
 
# ====== メイン処理 ============================================================
 
def process(dir_path: Path, screen_col: Optional[str], vocab_col: Optional[str], cfg: Dict[str, Any]) -> pd.DataFrame:
    """全体フロー：入力→候補生成→（完全一致なら即決）→LLM判定→集計DataFrame。"""
    df_screen, df_vocab = load_screen_and_vocab(dir_path, cfg, screen_col, vocab_col)
 
    vocab_terms = df_vocab["_term"].astype(str).tolist()
    term_meta = (
        df_vocab[["_term", "_phys", "_phys_abbr", "_no"]]
        .drop_duplicates("_term").set_index("_term").to_dict(orient="index")
    )
    # 正規化キー→原語の辞書（完全一致ショートサーキット用）
    norm_to_term = (
        df_vocab[["__term_norm", "_term"]]
        .drop_duplicates("__term_norm").set_index("__term_norm")["_term"].to_dict()
    )
 
    rows: List[Dict[str, Any]] = []
    api_client = ApiClient(cfg)
 
    # API同時実行数を制限するセマフォ
    max_concurrent_api = cfg.get("MAX_CONCURRENT_API", 3)
    api_semaphore = threading.Semaphore(max_concurrent_api)
 
    def meta_of(term: Optional[str]) -> Dict[str, Any]:
        if not term:
            return {"no": None, "phys": None, "phys_abbr": None}
        m = term_meta.get(str(term)) or {}
        return {"no": m.get("_no"), "phys": m.get("_phys"), "phys_abbr": m.get("_phys_abbr")}
 
    def worker(screen_name: str, src_file: str, src_sheet: Optional[str]) -> Dict[str, Any]:
        """1件の画面項目に対する判定ワーカー（スレッドで実行）。"""
        # --- 0) 正規化ベースの完全一致 → LLMスキップ
        normalized = zenkaku_hankaku_norm(screen_name)
        exact_term = norm_to_term.get(normalized)
        if exact_term:
            m = term_meta.get(exact_term) or {}
            return {
                "source_file": src_file,
                "source_sheet": src_sheet,
                "screen_item": screen_name,
                "match_type": "完全一致",
                "matched_term": exact_term,
                "matched_term_no": m.get("_no"),
                "matched_term_phys": (m.get("_phys_abbr") or m.get("_phys")),
                "matched_terms": None,
                "matched_terms_nos": None,
                "matched_terms_phys": None,
                "local_top_term": exact_term,
                "local_top_term_no": m.get("_no"),
                "local_top_term_phys": (m.get("_phys_abbr") or m.get("_phys")),
                "local_top_score": 1.0,
                "coverage_ratio": 1.0,
                "proposed_name": (m.get("_phys_abbr") or m.get("_phys") or simple_proposal(exact_term)),
                "reason": "正規化完全一致（LLM未呼び出し）",
            }
 
        # --- 1) ローカル候補生成（複合語＋ダイレクト）
        broad_candidates = phrase_candidates(screen_name, vocab_terms, max(cfg["TOP_K"], 6), cfg["FUZZY_THRESHOLD"])
        direct_candidates = top_k_candidates(screen_name, vocab_terms, cfg["TOP_K"], cfg["FUZZY_THRESHOLD"])
        # 単語単位で最高スコアを取り、上位だけ残す
        merged_scores: Dict[str, float] = {}
        for c in broad_candidates + direct_candidates:
            merged_scores[c.term] = max(merged_scores.get(c.term, 0.0), c.score)
        merged: List[Candidate] = [Candidate(t, s) for t, s in merged_scores.items()]
        merged.sort(key=lambda c: c.score, reverse=True)
        merged = merged[: max(cfg["TOP_K"], 10)]
 
        # --- 2) ローカル最高スコアが完全一致（1.0）→ 即決
        if merged and merged[0].score >= HARD_EXACT_SCORE:
            top = merged[0]
            # 追加の完全一致チェック（正規化後の文字列比較）
            norm_screen = zenkaku_hankaku_norm(screen_name)
            norm_term = zenkaku_hankaku_norm(top.term)
            if norm_screen == norm_term:  # 真の完全一致のみ
                m = term_meta.get(top.term) or {}
                return {
                    "source_file": src_file,
                    "source_sheet": src_sheet,
                    "screen_item": screen_name,
                    "match_type": "完全一致",
                    "matched_term": top.term,
                    "matched_term_no": m.get("_no"),
                    "matched_term_phys": (m.get("_phys_abbr") or m.get("_phys")),
                    "matched_terms": None,
                    "matched_terms_nos": None,
                    "matched_terms_phys": None,
                    "local_top_term": top.term,
                    "local_top_term_no": m.get("_no"),
                    "local_top_term_phys": (m.get("_phys_abbr") or m.get("_phys")),
                    "local_top_score": top.score,
                    "coverage_ratio": 1.0,
                    "proposed_name": (m.get("_phys_abbr") or m.get("_phys") or simple_proposal(top.term)),
                    "reason": f"ローカル完全一致（score={top.score:.2f}、LLM未呼び出し）",
                }
 
        # --- 3) LLMに最終判定を委譲（一部一致/一致なし）
        llm = call_llm(screen_name, merged, cfg, api_client, api_semaphore)
 
        # 値の整形
        cov_raw = llm.get("coverage_ratio")
        try:
            coverage_ratio = float(cov_raw) if cov_raw is not None else None
        except Exception:
            coverage_ratio = None
        mt = llm.get("matched_term")
        mt_meta = meta_of(mt)
        matched_terms = llm.get("matched_terms") or []
        mts_metas = [meta_of(t) for t in matched_terms]
 
        return {
            "source_file": src_file,
            "source_sheet": src_sheet,
            "screen_item": screen_name,
            "match_type": llm.get("match_type"),
            "matched_term": mt or None,
            "matched_term_no": mt_meta["no"],
            "matched_term_phys": (mt_meta.get("phys_abbr") or mt_meta.get("phys")),
            "matched_terms": ", ".join(matched_terms) or None,
            "matched_terms_nos": ", ".join([str(m.get("no")) for m in mts_metas if m.get("no")]) or None,
            "matched_terms_phys": ", ".join([str((m.get("phys_abbr") or m.get("phys"))) for m in mts_metas if (m.get("phys_abbr") or m.get("phys"))]) or None,
            "local_top_term": (merged[0].term if merged else None),
            "local_top_term_no": (term_meta.get(merged[0].term) or {}).get("_no") if merged else None,
            "local_top_term_phys": ((term_meta.get(merged[0].term) or {}).get("_phys_abbr") or (term_meta.get(merged[0].term) or {}).get("_phys")) if merged else None,
            "local_top_score": (merged[0].score if merged else None),
            "coverage_ratio": coverage_ratio,
            "reason": llm.get("reason"),
            "proposed_name": llm.get("proposed_name"),
        }
 
    # 並列実行（小規模時は自動で縮退）
    items = df_screen[["_screen", "_src_file", "_src_sheet"]].astype(str).values.tolist()
    max_workers = min(cfg["MAX_WORKERS"], max(1, len(items)))
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker, it[0], it[1], it[2]) for it in items]
        for fut in cf.as_completed(futures):
            try:
                rows.append(fut.result())
            except Exception as e:
                # ワーカー失敗時も処理を止めない
                rows.append({
                    "source_file": "<error>", "source_sheet": "-", "screen_item": "-",
                    "match_type": "一致なし", "reason": f"worker error: {e}", "proposed_name": None,
                })
 
    return pd.DataFrame(rows).reset_index(drop=True)
 
# ====== 出力 ================================================================
 
def save_outputs(df: pd.DataFrame, cfg: Dict[str, Any]) -> None:
    """結果をExcel/CSV/JSONLで保存（MultiIndex対応・条件付き色付け付き）"""
    from pathlib import Path
    import pandas as pd
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import PatternFill
    from openpyxl.formatting.rule import FormulaRule
 
    out_dir = Path(cfg["OUT_DIR"]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = out_dir / "match_result.xlsx"
 
    # --- 1) まず一次元カラムで整える（この段階では MultiIndex にしない）
    ordered_cols = [
        # 元情報
        "source_file","source_sheet",
        # 照合対象
        "screen_item",
        # 結果
        "match_type",
        # 一致した単語（主要）
        "matched_term","matched_term_no","matched_term_phys",
        # 提案
        "proposed_name",
        # 複数一致（補足）
        "matched_terms","matched_terms_nos","matched_terms_phys",
        # 判定詳細
        "coverage_ratio","reason",
        # 参考（ローカル候補）
        "local_top_term","local_top_term_no","local_top_term_phys","local_top_score",
    ]
    for c in ordered_cols:
        if c not in df.columns:
            df[c] = None
 
    # 注意事項列
    def _warn(row):
        mt = (row.get("match_type") or "")
        if mt == "一部一致":
            return "⚠️ 部分一致：内容を確認の上、必要に応じて単語帳を追加・修正してください"
        if mt == "一致なし":
            return "⚠️ 一致なし：単語帳への追加を検討してください"
        return ""
    df["注意事項"] = df.apply(_warn, axis=1)
 
    # 一次元で並べ替え
    df = df[ordered_cols + ["注意事項"]]
 
    # --- 2) 一括で MultiIndex 化（列数とタプル数を一致させる）
    header_map = {
        "source_file": ("【元情報】", "読み込み元ファイル"),
        "source_sheet": ("【元情報】", "読み込み元シート"),
        "screen_item": ("【照合対象】", "画面項目名"),
        "match_type": ("【結果】", "一致状況"),
        "matched_term": ("【一致した単語】", "論理名"),
        "matched_term_no": ("【一致した単語】", "列番号"),
        "matched_term_phys": ("【一致した単語】", "物理名"),
        "proposed_name": ("【提案】", "推奨物理名"),
        "matched_terms": ("【複数一致】", "論理名"),
        "matched_terms_nos": ("【複数一致】", "列番号"),
        "matched_terms_phys": ("【複数一致】", "物理名"),
        "coverage_ratio": ("【判定詳細】", "カバー率"),
        "reason": ("【判定詳細】", "理由"),
        "local_top_term": ("【参考:ローカル候補】", "論理名"),
        "local_top_term_no": ("【参考:ローカル候補】", "列番号"),
        "local_top_term_phys": ("【参考:ローカル候補】", "物理名"),
        "local_top_score": ("【参考:ローカル候補】", "スコア"),
        "注意事項": ("【注意】", "注意事項"),
    }
    df.columns = pd.MultiIndex.from_tuples([header_map[c] for c in df.columns])
    df.columns.names = [None, None]  # ← "Length of names must match..." 回避
 
    # --- 3) サマリ/ファイル別サマリ
    status_counts = df[("【結果】", "一致状況")].value_counts(dropna=False).to_dict()
    summary_df = pd.DataFrame([
        {"メトリクス": "完全一致", "件数": status_counts.get("完全一致", 0)},
        {"メトリクス": "一部一致", "件数": status_counts.get("一部一致", 0)},
        {"メトリクス": "一致なし", "件数": status_counts.get("一致なし", 0)},
        {"メトリクス": "合計", "件数": len(df)},
    ])
 
    group_keys = [("【元情報】", "読み込み元ファイル"),
                  ("【元情報】", "読み込み元シート")]
    target_col = ("【照合対象】", "画面項目名")
    by_file_df = (
        df.groupby(group_keys)
          .agg(
              項目数=(target_col, "count"),
              項目名サンプル=(target_col, lambda s: ", ".join(map(str, s.dropna().head(50))))
          )
          .reset_index()
    )
 
    # --- 4) Excel へ保存
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="結果", index=True)
        summary_df.to_excel(w, sheet_name="サマリ", index=True)
        by_file_df.to_excel(w, sheet_name="ファイル別サマリ", index=True)
 
        # --- 5) 条件付き書式（「一部一致」「一致なし」を色付け）
        if len(df) > 0:
            ws = w.sheets["結果"]
 
            # 2段見出しなのでデータ開始行は 3 行目
            start_row = 3
            end_row = start_row + len(df) - 1
 
            # 列インデックス（1始まり）を取得
            col_index = {col: i+1 for i, col in enumerate(df.columns)}
            mt_idx = col_index[("【結果】", "一致状況")]
            si_idx = col_index[("【照合対象】", "画面項目名")]
 
            mt_col = get_column_letter(mt_idx)
            si_col = get_column_letter(si_idx)
 
            # 塗り色
            fill_yellow = PatternFill(start_color="FFF3B3", end_color="FFF3B3", fill_type="solid")
            fill_red = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
 
            # 一部一致（match_type 列自体）
            rng_mt = f"{mt_col}{start_row}:{mt_col}{end_row}"
            ws.conditional_formatting.add(
                rng_mt,
                FormulaRule(formula=[f'{mt_col}{start_row}="一部一致"'], fill=fill_yellow)
            )
            # 一致なし（match_type 列自体）
            ws.conditional_formatting.add(
                rng_mt,
                FormulaRule(formula=[f'{mt_col}{start_row}="一致なし"'], fill=fill_red)
            )
 
            # 画面項目名列も同じ条件で色付け（列は固定、行は相対）
            rng_si = f"{si_col}{start_row}:{si_col}{end_row}"
            ws.conditional_formatting.add(
                rng_si,
                FormulaRule(formula=[f'${mt_col}{start_row}="一部一致"'], fill=fill_yellow)
            )
            ws.conditional_formatting.add(
                rng_si,
                FormulaRule(formula=[f'${mt_col}{start_row}="一致なし"'], fill=fill_red)
            )
 
    print(f"保存: {xlsx_path}")
 
 
# ====== CLI ================================================================
 
def app_root() -> Path:
    if getattr(sys, "frozen", False):  # PyInstaller
        return Path(sys.executable).parent
    return Path(__file__).parent
 
 
def ask_directory(title: str, initial: Optional[str] = None) -> Optional[str]:
    if not TK_AVAILABLE:
        return None
    try:
        root = tk.Tk(); root.withdraw()
        path = filedialog.askdirectory(title=title, initialdir=initial or str(app_root()))
        root.destroy()
        return path or None
    except Exception:
        return None
 
 
def main() -> None:
    load_dotenv()
    # ダブルクリック実行時のカレントずれ防止
    try:
        os.chdir(app_root())
    except Exception:
        pass
 
    parser = argparse.ArgumentParser(description="Excel 単語照合（LLM 補助）")
    parser.add_argument("--dir", help="入力ディレクトリ（画面項目定義・単語帳）")
    parser.add_argument("--in-dir", help="上と同じ（--dir と同義。後方互換）")
    parser.add_argument("--out-dir", help="出力ディレクトリ（既定: out）")
    parser.add_argument("--screen-col", help="画面項目定義の列名（デフォルト: 項目名称）")
    parser.add_argument("--vocab-col", help="単語帳の列名（デフォルト: 論理名）")
    parser.add_argument("--no-gui", action="store_true", help="ダイアログを使わない（サーバ/CI向け）")
    args = parser.parse_args()
 
    cfg = DEFAULT_CONFIG.copy()
 
    if cfg.get("OPENAI_SEND_AUTH") and not cfg.get("OPENAI_API_KEY"):
        print("[警告] OPENAI_SEND_AUTH=true ですが OPENAI_API_KEY が未設定です。Authorization は送信されません。")
 
    # 入力ディレクトリの解決
    in_dir = args.in_dir or args.dir
    if not in_dir and not args.no_gui:
        in_dir = ask_directory("入力ディレクトリ（画面項目定義・単語帳）を選択")
        if not in_dir:
            try:
                in_dir = input("入力ディレクトリのパスを入力してください: ").strip()
            except Exception:
                in_dir = None
    if not in_dir:
        raise FileNotFoundError("入力ディレクトリが指定されていません。--dir かダイアログで指定してください。")
 
    # 出力先の解決
    if args.out_dir:
        cfg["OUT_DIR"] = args.out_dir
    else:
        if not args.no_gui:
            chosen = ask_directory("出力ディレクトリ（保存先）を選択（キャンセルで既定の out）")
            if chosen:
                cfg["OUT_DIR"] = chosen
 
    # 実行
    root_dir = Path(in_dir)
    if not root_dir.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {root_dir}")
 
    df = process(root_dir, args.screen_col, args.vocab_col, cfg)
    save_outputs(df, cfg)
 
    if TK_AVAILABLE and not args.no_gui:
        try:
            messagebox.showinfo("完了", f"出力が完了しました。保存先: {Path(cfg['OUT_DIR']).resolve()}\\match_result.xlsx")
        except Exception:
            pass
 
 
if __name__ == "__main__":
 
    main()
 
 
