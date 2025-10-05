#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel→単語照合→レポート生成（LLM補助）
メイン処理
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# 共通モジュール
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.api_backend import create_api_backend
from common.config import get_common_config, get_tool_config
from common.cli_utils import app_root, ask_directory

# wordモジュール
from word.text_utils import (
    Candidate,
    normalize_text,
    calculate_similarity,
    find_top_candidates,
    generate_simple_physical_name
)
from word.llm_handler import call_llm_api, create_fallback_response, HARD_EXACT_SCORE
from word.excel_loader import (
    pick_matching_sheets,
    load_excel_with_auto_header
)
 
# ====== GUI（任意） ===========================================================
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False
 
# ====== 設定 ==================================================================
DEFAULT_CONFIG: Dict[str, Any] = {
    **get_common_config(),   # 共通設定（API、LLMパラメータ等）
    **get_tool_config("word")  # ツール固有設定（config.yamlから取得）
}

# ====== ヘルパー関数 ==========================================================

def _int_env(name: str) -> Optional[int]:
    """環境変数から整数を取得"""
    v = os.getenv(name, "")
    try:
        return int(v) if v else None
    except Exception:
        return None

# ヘッダー検出設定
_tool_cfg = get_tool_config("word")
HEADER_DETECT = os.getenv("HEADER_DETECT", str(_tool_cfg.get("HEADER_DETECT", True))).lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", str(_tool_cfg.get("HEADER_SCAN_ROWS", 30))))
SCREEN_HEADER_ROW = _int_env("SCREEN_HEADER_ROW")
VOCAB_HEADER_ROW = _int_env("VOCAB_HEADER_ROW")

 
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
        matching_sheets = pick_matching_sheets(xls, cfg["SCREEN_SHEET"]) if cfg["SCREEN_SHEET"] else [xls.sheet_names[0]]

        for sheet_used in matching_sheets:
            try:
                df_s, _ = load_excel_with_auto_header(path, sheet_used, [screen_col], SCREEN_HEADER_ROW, HEADER_SCAN_ROWS)
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
        matching_sheets = pick_matching_sheets(xls, cfg["VOCAB_SHEET"]) if cfg["VOCAB_SHEET"] else [xls.sheet_names[0]]

        for sheet_used in matching_sheets:
            try:
                df_v, _ = load_excel_with_auto_header(path, sheet_used, [term_col, phys_col, no_col], VOCAB_HEADER_ROW, HEADER_SCAN_ROWS)
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
    df_vocab["__term_norm"] = df_vocab[term_col].astype(str).map(normalize_text)
    df_vocab = df_vocab.rename(columns={term_col: "_term", phys_col: "_phys", phys_abbr_col: "_phys_abbr", no_col: "_no"})
    df_screen = df_screen.rename(columns={screen_col: "_screen", "__source_file": "_src_file", "__source_sheet": "_src_sheet"})

    return df_screen, df_vocab
 
# ====== 候補生成（ローカル） ==================================================

def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語対策：unigram/bigram に分解してパーツ単位で候補を拾う。"""
    tokens = [t for t in normalize_text(screen_name).split(" ") if t]
    grams = set(tokens)
    for i in range(len(tokens) - 1):
        grams.add(tokens[i] + " " + tokens[i + 1])
    pool: List[Candidate] = []
    for g in grams:
        for vt in vocab_terms:
            s = calculate_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))
    # 同一単語は最大スコアを採用
    best_by_term: Dict[str, float] = {}
    for cand in pool:
        best_by_term[cand.term] = max(best_by_term.get(cand.term, 0.0), cand.score)
    merged = [Candidate(t, sc) for t, sc in best_by_term.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[: max(k, 10)]

# ====== LLM呼び出し（プロンプト詳細は割愛） ================================
LLM_SYSTEM = (
    "あなたは業務システム開発における命名規則の専門家です。\n"
    "画面項目名と単語帳を照合し、lowerCamelCase形式の物理名を提案することが使命です。\n"
    "\n"
    "# タスク\n"
    "与えられた画面項目名に対して:\n"
    "1. 単語帳候補との一致度を判定\n"
    "2. 候補の physical_name を活用して最適な物理名を生成\n"
    "3. 不足する語は自分で補完して完全な物理名を構築\n"
    "\n"
    "# 重要: あなたに渡される画面項目名は、既に単一語での完全一致判定を通過しています\n"
    "# つまり、単一の候補と完全一致するものは既に除外されています\n"
    "\n"
    "# 判定基準（厳密に適用）\n"
    "- **完全一致（部品ごと）**: 画面項目名を複数の語に分解でき、全ての語が単語帳の候補で充足される場合\n"
    "  例1: 「回収稟議番号」で「回収」と「稟議番号」が両方候補にある → 完全一致（部品ごと）\n"
    "  例2: 「銀行取引一覧」で「銀行」「取引」「一覧」が全て候補にある → 完全一致（部品ごと）\n"
    "  重要: 未登録語が1つもない場合のみ完全一致（部品ごと）\n"
    "- **一部一致**: 画面項目名を複数の語に分解でき、その一部が単語帳にあるが、一部は未登録の場合\n"
    "  例1: 「顧客担当者名」で「顧客」と「名」が候補にあり、「担当者」は未登録 → 一部一致\n"
    "  例2: 「新規申込日」で「申込」「日」はあるが、「新規」は未登録 → 一部一致\n"
    "- **一致なし**: 画面項目名のどの語も単語帳に存在しない、または候補が全て不適切な場合のみ\n"
    "  例: 「稟議承認日」で「稟議」「承認」「日」全てが候補にない → 一致なし\n"
    "\n"
    "\n"
    "# ネーミングルール（厳格に遵守）\n"
    "\n"
    "## 基本原則\n"
    "1. **lowerCamelCase形式**: 必ず小文字始まり（例: ○ shinseiDate / × ShinseiDate）\n"
    "2. **推奨文字数**: 8文字程度を目安とする（最大15文字まで許容）\n"
    "3. **誰が見ても意味が容易にわかる名称**にする\n"
    "\n"
    "## 言語選択ルール\n"
    "1. **原則: 英単語を使用**\n"
    "2. **例外: 以下の場合のみ日本語ローマ字表記（ヘボン式）を使用**\n"
    "   - 日本人にとって極端に馴染みの薄い英単語の場合（例: 稟議 → ringi, 禀 → rin）\n"
    "   - 行内・融資内で一般的に用いられている単語（例: 案件番号 → lcNo）\n"
    "   - 別名をつけたほうが望ましいもの（例: 当行 → mufgBank）\n"
    "3. **ヘボン式ローマ字の詳細**\n"
    "   - し→shi, ち→chi, つ→tsu, ふ→fu, じ→ji, ず→zu\n"
    "   - しゃ→sha, しゅ→shu, しょ→sho, ちゃ→cha, ちゅ→chu, ちょ→cho\n"
    "   - じゃ→ja, じゅ→ju, じょ→jo\n"
    "   - 撥音「ん」: b,m,p の前は m、それ以外は n（例: 申込→moushikomi, 案件→anken）\n"
    "   - 長音: 母音を重ねる（例: 交付→kofu, 照会→shokai）\n"
    "4. **混在ルール**\n"
    "   - **原則: 英語と日本語ローマ字の混在は禁止**（例: NG customerRingi）\n"
    "   - **例外**: 行内で一般的に用いられている場合のみ許可（例: lcNo = loanCase + Number）\n"
    "   - 1つの物理名はすべて英語、またはすべて日本語ローマ字に統一することを推奨\n"
    "\n"
    "## 略語使用ルール\n"
    "1. **原則: 略語は使用しない**\n"
    "2. **例外: 以下の条件を両方満たす場合のみ許可**\n"
    "   - 名称が9文字以上となる場合\n"
    "   - 略語を用いたほうがわかりやすい場合\n"
    "3. 略語を使用する場合も、誰が見ても意味がわかること\n"
    "\n"
    "## 複合語ルール\n"
    "1. 原則: 単語レベルで定義し、複合語は単語帳の単語を組み合わせる\n"
    "2. 例外: 単語を組み合わせて違和感がある場合のみ複合語での定義を認める\n"
    "   - 例: 案件番号 → case + no だと違和感 → lcNo として定義可\n"
    "\n"
    "## 表記揺れの考慮\n"
    "- コード = CD = code\n"
    "- 番号 = No = number\n"
    "- 名称 = 名 = name\n"
    "- フラグ = flag\n"
    "\n"
    "# 物理名生成の優先順位（最重要）\n"
    "1. **候補の physical_name を最優先**: 候補に physical_name がある場合は必ずそれを使用\n"
    "2. **不足語の補完**: 候補にない語は、ネーミングルール従って自分で英語名/ローマ字を考案\n"
    "3. **最小限の命名**: 余分な語を追加せず、画面項目名の意味を正確に表現する最短形を目指す\n"
    "4. **文字数制約**: 8文字程度が理想、最大15文字（ただし意味が不明瞭になるなら文字数より明瞭さ優先）\n"
    "\n"
    "# 思考プロセス\n"
    "以下の手順で分析してください:\n"
    "1. 画面項目名を意味のある語に分解（例: 「顧客担当者名」→「顧客」「担当者」「名」）\n"
    "2. 各語が候補リストにあるか確認\n"
    "3. 一致状況を判定:\n"
    "   - 完全一致（部品ごと）: 分解した全ての語が候補にある（未登録語なし）\n"
    "   - 一部一致: 分解した語の一部が候補にあり、一部は未登録\n"
    "   - 一致なし: どの語も候補にない\n"
    "4. 候補にある語はその physical_name を使用、ない語は自分で考案\n"
    "5. 適切な語順で lowerCamelCase に結合\n"
    "\n"
    "# 出力\n"
    "- JSON形式のみ出力（説明文・前置き・後置きは一切不要）\n"
    "- 必ず提示された全キーを含める\n"
    "- null許容キーは適切に null を設定\n"
)
 
LLM_USER_TEMPLATE = (
    """画面項目名: {screen_name}

単語帳候補（local_score降順）:
{candidates_json}

---
タスク: 上記の画面項目名に対して、lowerCamelCaseの物理名を提案してください。

処理ステップ:
1. 画面項目名を意味のある語に分解
2. 各語が候補リストに存在するかチェック
3. physical_name生成:
   - 候補にある語 → その physical_name を使用（必須）
   - 候補にない語 → ネーミングルールに従い自分で考案
   - 全てを lowerCamelCase で結合

出力JSON:
{{
  "match_type": "完全一致（部品ごと）" | "一部一致" | "一致なし",
  "matched_term": null,
  "matched_terms": string[] | null,
  "reason": string,
  "proposed_name": string,
  "coverage_ratio": number | null,
  "unmatched_terms": string[] | null,
  "unmatched_notes": string[] | null
}}

フィールド定義:
- match_type: 「完全一致（部品ごと）」「一部一致」「一致なし」のいずれか
  - 完全一致（部品ごと）: 分解した全ての語が候補で充足（unmatched_terms が空）
  - 一部一致: 一部の語が候補にあり、一部は未登録（unmatched_terms に値あり）
  - 一致なし: どの語も候補にない
- matched_term: 常に null（単一語での完全一致用フィールドは使用しない）
- matched_terms: 完全一致または一部一致時の語リスト（例: ["回収", "稟議番号"]）、一致なしの場合は null
- proposed_name: 必須、lowerCamelCase、8-15文字推奨
- coverage_ratio: 0.0-1.0、完全一致（部品ごと）=1.0、一致なし=null または 0.0
- unmatched_terms: 候補にない語のリスト（完全一致（部品ごと）の場合は空配列またはnull）
- unmatched_notes: unmatched_terms各要素の説明（要素数一致）
- reason: 判定理由を1文で

具体例1（完全一致（部品ごと））:
入力: "回収稟議番号"
候補: [{{"term": "回収", "physical_name": "kaishu"}}, {{"term": "稟議番号", "physical_name": "ringiNo"}}]
出力: {{"match_type": "完全一致（部品ごと）", "matched_term": null, "matched_terms": ["回収", "稟議番号"], "proposed_name": "kaishuRingiNo", "coverage_ratio": 1.0, "unmatched_terms": null, "unmatched_notes": null, "reason": "全ての語が候補で充足"}}

具体例2（一部一致）:
入力: "顧客担当者名"
候補: [{{"term": "顧客", "physical_name": "customer"}}, {{"term": "名", "physical_name": "name"}}]
出力: {{"match_type": "一部一致", "matched_term": null, "matched_terms": ["顧客", "名"], "proposed_name": "customerPersonInChargeName", "coverage_ratio": 0.67, "unmatched_terms": ["担当者"], "unmatched_notes": ["業務担当者"], "reason": "顧客と名は一致、担当者は未登録のため補完"}}

JSON以外の出力禁止。即座にJSONのみ返してください。
    """
)

# ====== メイン処理 ============================================================
 
def process(dir_path: Path, screen_col: Optional[str], vocab_col: Optional[str], cfg: Dict[str, Any], progress_callback=None) -> pd.DataFrame:
    """全体フロー：入力→候補生成→（完全一致なら即決）→LLM判定→集計DataFrame。"""
    df_screen, df_vocab = load_screen_and_vocab(dir_path, cfg, screen_col, vocab_col)
    # 全体件数（進捗ログ用）
    total_items = len(df_screen)
    processed_count = 0
 
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
    api_client = create_api_backend(cfg)
 
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
        normalized = normalize_text(screen_name)
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
                "proposed_name": (m.get("_phys_abbr") or m.get("_phys") or generate_simple_physical_name(exact_term)),
                "reason": "正規化完全一致（LLM未呼び出し）",
                "unmatched_terms": None,
                "unmatched_note": None,
            }

        # --- 1) ローカル候補生成（複合語＋ダイレクト）
        broad_candidates = phrase_candidates(screen_name, vocab_terms, max(cfg["TOP_K"], 6), cfg["FUZZY_THRESHOLD"])
        direct_candidates = find_top_candidates(screen_name, vocab_terms, cfg["TOP_K"], cfg["FUZZY_THRESHOLD"])
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
            norm_screen = normalize_text(screen_name)
            norm_term = normalize_text(top.term)
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
                    "proposed_name": (m.get("_phys_abbr") or m.get("_phys") or generate_simple_physical_name(top.term)),
                    "reason": f"ローカル完全一致（score={top.score:.2f}、LLM未呼び出し）",
                    "unmatched_terms": None,
                    "unmatched_note": None,
                }

        # --- 3) LLMに最終判定を委譲（一部一致/一致なし）
        # Build custom prompt for this file's specific requirements
        system_prompt = LLM_SYSTEM
        user_prompt = LLM_USER_TEMPLATE.format(
            screen_name=screen_name,
            candidates_json=json.dumps([{
                "term": c.term,
                "local_score": round(c.score, 4),
                **({"physical_name": (term_meta.get(c.term) or {}).get("_phys_abbr") or (term_meta.get(c.term) or {}).get("_phys")}
                   if term_meta and c.term in term_meta and ((term_meta.get(c.term) or {}).get("_phys_abbr") or (term_meta.get(c.term) or {}).get("_phys"))
                   else {})
            } for c in merged], ensure_ascii=False, indent=2)
        )
        llm = call_llm_api(system_prompt, user_prompt, cfg, api_client, api_semaphore)
 
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

        # 未登録語の整形（配列→文字列変換）
        unmatched_terms = None
        unmatched_note = None
        try:
            llm_unmatched_terms = llm.get("unmatched_terms") or []
            llm_unmatched_notes = llm.get("unmatched_notes") or []
            if llm_unmatched_terms and llm_unmatched_notes:
                unmatched_terms = ", ".join(llm_unmatched_terms)
                unmatched_note = " / ".join(llm_unmatched_notes)
        except Exception:
            pass

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
            "unmatched_terms": unmatched_terms,
            "unmatched_note": unmatched_note,
        }
 
    # 並列実行（小規模時は自動で縮退）
    items = df_screen[["_screen", "_src_file", "_src_sheet"]].astype(str).values.tolist()
    max_workers = min(cfg["MAX_WORKERS"], max(1, len(items)))
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker, it[0], it[1], it[2]) for it in items]
        for fut in cf.as_completed(futures):
            try:
                row = fut.result()
                rows.append(row)
                processed_count += 1
                # 進捗ログ: 10件ごとに出力
                pct = processed_count * 100 / total_items if total_items else 0
                if processed_count % 10 == 0 or processed_count == total_items:
                    print(f"[INFO] {processed_count}/{total_items} 件処理済み ({pct:.1f}%)")
                # コールバック呼び出し（リアルタイム進捗）
                if progress_callback:
                    progress_callback(processed_count, total_items)
            except Exception as e:
                # ワーカー失敗時も処理を止めない
                error_row = {
                    "source_file": "<error>", "source_sheet": "-", "screen_item": "-",
                    "match_type": "一致なし", "reason": f"worker error: {e}", "proposed_name": None,
                }
                rows.append(error_row)
                processed_count += 1
                # エラー行でも進捗ログ
                pct = processed_count * 100 / total_items if total_items else 0
                if processed_count % 10 == 0 or processed_count == total_items:
                    print(f"[INFO] {processed_count}/{total_items} 件処理済み ({pct:.1f}%)")
                # コールバック呼び出し（リアルタイム進捗）
                if progress_callback:
                    progress_callback(processed_count, total_items)
 
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
    # 列順を変更: 一致した単語の後に複数一致した単語群を配置し、提案列をその後ろに移動
    ordered_cols = [
        # 元情報
        "source_file","source_sheet",
        # 照合対象
        "screen_item",
        # 結果
        "match_type",
        # 一致した単語（主要）
        "matched_term","matched_term_no","matched_term_phys",
        # 複数一致（補足）を先に配置
        "matched_terms","matched_terms_nos","matched_terms_phys",
        # 提案を後ろに移動
        "proposed_name",
        # 判定詳細
        "coverage_ratio","reason",
        # 参考（ローカル候補）
        "local_top_term","local_top_term_no","local_top_term_phys","local_top_score",
        # 登録候補
        "unmatched_terms","unmatched_note",
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
        # 元情報
        "source_file": ("【元情報】", "ファイル名"),
        "source_sheet": ("【元情報】", "シート名"),
        # 照合対象
        "screen_item": ("【対象項目】", "項目名"),
        # 結果
        "match_type": ("【結果】", "一致状況"),
        # 一致した単語（主要）
        "matched_term": ("【一致した単語】", "論理名"),
        "matched_term_no": ("【一致した単語】", "列番号"),
        "matched_term_phys": ("【一致した単語】", "物理名"),
        # 複数一致した単語群
        "matched_terms": ("【複数一致した単語群】", "論理名"),
        "matched_terms_nos": ("【複数一致した単語群】", "列番号"),
        "matched_terms_phys": ("【複数一致した単語群】", "物理名"),
        # 提案
        "proposed_name": ("【提案】", "推奨物理名"),
        # 判定詳細
        "coverage_ratio": ("【判定詳細】", "カバー率"),
        "reason": ("【判定詳細】", "理由"),
        # ローカル候補
        "local_top_term": ("【ローカル候補】", "論理名"),
        "local_top_term_no": ("【ローカル候補】", "列番号"),
        "local_top_term_phys": ("【ローカル候補】", "物理名"),
        "local_top_score": ("【ローカル候補】", "スコア"),
        # 注意事項
        "注意事項": ("【注意事項】", "注意事項"),
        # 登録候補
        "unmatched_terms": ("【登録候補】", "未登録語"),
        "unmatched_note": ("【登録候補】", "コメント"),
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
 
    group_keys = [("【元情報】", "ファイル名"),
                  ("【元情報】", "シート名")]
    target_col = ("【対象項目】", "項目名")
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
        # MultiIndex列はExcel保存時にヘッダーとデータの間に空白行が入る問題があるため、
        # ヘッダーとデータを分けて書き込むことで余分な空白行を回避する。
        # 最初にヘッダーのみ（データなし）を書き込み
        df.drop(df.index).to_excel(w, sheet_name="結果", index=True)
        # 次に実際のデータをヘッダーなしで1行下から追記
        df.to_excel(w, sheet_name="結果", startrow=1, header=False, index=True)
        summary_df.to_excel(w, sheet_name="サマリ", index=True)
        by_file_df.to_excel(w, sheet_name="ファイル別サマリ", index=True)

    print(f"保存: {xlsx_path}")
 
 
# ====== CLI ================================================================
 
def main() -> None:
    """
    メイン処理（CLI実行用）
    ※ 設定はconfig.yamlから読み込まれます（環境変数で上書き可）
    """
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
 
 