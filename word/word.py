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
    - summary  : exact/partial/none/total の件数
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
    "SCREEN_SHEET": os.getenv("SCREEN_SHEET", None),  # 未指定なら先頭シート
    "VOCAB_SHEET": os.getenv("VOCAB_SHEET", None),
    # 画面項目の論理名列
    "SCREEN_COL": os.getenv("SCREEN_COL", "項目名"),
    # 単語帳の列（論理名=用語、物理名、No）
    "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "用語"),
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名"),
    # 省略物理名（あれば優先して出力に使用）
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名省略"),
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
                       if str(x) not in {"", "nan", "None"})
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
LLM_SYSTEM = (
    "あなたは業務システムの画面設計と用語統一の専門家です。"
    "与えられた『画面項目名』と『単語帳候補（上位スコア順）』を比較して、"
    "“完全一致 / 部分一致 / 一致なし” を厳密に判定し、理由を日本語で簡潔に述べてください。"
    "複合語（複数の用語を組み合わせた項目名）の可能性も必ず検討し、"
    "複数用語の組み合わせで項目名を構成できる場合は、対応する用語リストを返してください。"
    "一致なしの場合は、ドメインの命名規約に沿って *新しい推奨項目名* を1つ提案してください。"
    "JSON だけを返し、余計な文章は付けないでください。"
)


LLM_USER_TEMPLATE = (
    """
    # 画面項目名
    {screen_name}

    # 単語帳候補（上位スコア順）
    {candidates_json}

    # 厳密 JSON 仕様（複合語対応）
    {
      "match_type": "exact" | "partial" | "none",
      "matched_term": string | null,            // 単一語で最も適合する場合のみ
      "matched_terms": string[] | null,         // 複数語の組み合わせで構成できる場合
      "reason": string,
      "proposed_name": string | null,
      "coverage_ratio": number | null           // 0.0~1.0: 原文の語がどれだけ用語でカバーされたか
    }

    制約:
    - exact は意味も表記も等しい場合のみ。
    - partial は略語違い、語順違い、同義近似などで採用余地がある場合。
    - 複合語が適切な場合は matched_terms を優先し、matched_term は null。
    - none は候補が不適切な場合。簡潔で具体的な理由を出すこと。
    - proposed_name は none のときのみ非 null。命名規則: 日本語で簡潔、重複語を避け、一般的・説明的。
    - coverage_ratio は推定でよいが 0.0~1.0 の数値で返すこと。
    - 返答は JSON のみ。説明文やマークダウンは出力しない。
    """
)



def build_llm_payload(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any]) -> Dict[str, Any]:
    cand_payload = [
        {"term": c.term, "local_score": round(c.score, 4)} for c in candidates
    ]
    return {
        "model": cfg["OPENAI_MODEL"],
        "max_tokens": cfg.get("MAX_TOKENS"),
        "temperature": cfg.get("TEMPERATURE", 0.7),
        "top_p": cfg.get("TOP_P", 0.95),
        "presence_penalty": cfg.get("PRESENCE_PENALTY", 0.0),
        "frequency_penalty": cfg.get("FREQUENCY_PENALTY", 0.0),
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": LLM_SYSTEM},
            {
                "role": "user",
                "content": LLM_USER_TEMPLATE.format(
                    screen_name=screen_name,
                    candidates_json=json.dumps(cand_payload, ensure_ascii=False, indent=2),
                ),
            },
        ],
    }


def call_llm(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any], client: Optional[ApiClient] = None) -> Dict[str, Any]:
    client = client or ApiClient(cfg)
    payload = build_llm_payload(screen_name, candidates, cfg)
    for attempt in range(cfg["RETRY"] + 1):
        try:
            data = client.post_json(payload)
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)
            if not set(["match_type", "matched_term", "reason", "proposed_name"]).issubset(result):
                raise ValueError("LLM JSON schema mismatch")
            return result
        except Exception:
            if attempt < cfg["RETRY"]:
                time.sleep(1.2 * (attempt + 1))
                continue
            return fallback_reason(screen_name, candidates)



def fallback_reason(screen_name: str, candidates: List[Candidate]) -> Dict[str, Any]:
    if not candidates:
        return {
            "match_type": "none",
            "matched_term": None,
            "reason": "API不達/候補なし。後で単語帳を拡充してください。",
            "proposed_name": simple_proposal(screen_name),
        }
    top = candidates[0]
    if top.score >= 0.95:
        return {
            "match_type": "exact",
            "matched_term": top.term,
            "reason": f"ローカル完全一致（score={top.score:.2f}）",
            "proposed_name": None,
        }
    return {
        "match_type": "partial",
        "matched_term": top.term,
        "reason": f"ローカル近似一致（score={top.score:.2f}）。APIフォールバック。",
        "proposed_name": None,
    }


def simple_proposal(screen_name: str) -> str:
    # 乱暴だが、記号を落として語を連結し、末尾の『名』や『フラグ』などを過度に重複させない
    s = zenkaku_hankaku_norm(screen_name)
    s = re.sub(r"\s+", " ", s)
    tokens = [t for t in s.split(" ") if t]
    if not tokens:
        return "新規項目"
    # 代表 2–3 語まで
    core = tokens[:3]
    # よくある冗長語の削り（例）
    stop = {"コード", "番号", "名称名", "名称名称"}
    core = [w for w in core if w not in stop]
    return "".join(core) or "新規項目"


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

        llm = call_llm(screen_name, merged, cfg, api_client)

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

    # 件数サマリ
    cnt = df["match_type"].value_counts(dropna=False).to_dict()
    summary_df = pd.DataFrame([
        {"metric": "exact", "count": cnt.get("exact", 0)},
        {"metric": "partial", "count": cnt.get("partial", 0)},
        {"metric": "none", "count": cnt.get("none", 0)},
        {"metric": "total", "count": len(df)},
    ])

    # ファイル別サマリ
    by_file_df = (
        df.groupby(["source_file", "source_sheet"])['screen_item']
          .agg(item_count='count', items=lambda s: ", ".join(map(str, s.head(50))))
          .reset_index()
    )

    # Excel一冊に複数シートで保存
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="results", index=False)
        summary_df.to_excel(writer, sheet_name="summary", index=False)
        by_file_df.to_excel(writer, sheet_name="by_file", index=False)

    print(f"保存: {xlsx}")

# =============================================================
# CLI
# =============================================================

def main():
    load_dotenv()  # .env の読み込み（あれば）

    parser = argparse.ArgumentParser(description="Excel 用語照合（LLM 補助）")
    parser.add_argument("--dir", required=True, help="Excel を置いたディレクトリ")
    parser.add_argument("--screen-col", help="画面項目定義の列名（デフォルト: 項目名）")
    parser.add_argument("--vocab-col", help="単語帳の列名（デフォルト: 用語）")
    args = parser.parse_args()

    cfg = DEFAULT_CONFIG.copy()

    # バリデーション（最低限）
    if cfg.get("OPENAI_SEND_AUTH") and not cfg.get("OPENAI_API_KEY"):
        print("[警告] OPENAI_SEND_AUTH=true ですが OPENAI_API_KEY が未設定です。Authorization は送信されません。")

    dir_path = Path(args.dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {dir_path}")

    df = process(dir_path, args.screen_col, args.vocab_col, cfg)
    save_outputs(df, cfg)


if __name__ == "__main__":
    main()
