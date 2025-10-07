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
# スコアリング関連
EXACT_MATCH_SCORE = 1.0  # 完全一致スコア
PARTIAL_MATCH_SCORE = 0.9  # 片方包含時のスコア
FALLBACK_EXACT_THRESHOLD = 0.95  # LLMフォールバック時の完全一致判定閾値

# ヘッダー検出関連
DEFAULT_HEADER_SCAN_ROWS = 10  # ヘッダー行を探索する行数
EXCEL_DATA_START_ROW = 3  # Excelデータ開始行（2段ヘッダー想定）

# 進捗表示関連
PROGRESS_LOG_INTERVAL = 10  # 進捗ログを出力する間隔（件数）

# リトライ関連
RETRY_BACKOFF_MULTIPLIER = 1.2  # リトライ時のバックオフ係数（秒）

# マッチタイプ定数
MATCH_TYPE_EXACT = "完全一致"
MATCH_TYPE_EXACT_PARTS = "完全一致（部品ごと）"
MATCH_TYPE_PARTIAL = "一部一致"
MATCH_TYPE_NONE = "一致なし"

# 列名定数（内部使用）
COL_TERM = "_term"
COL_PHYS = "_phys"
COL_PHYS_ABBR = "_phys_abbr"
COL_NO = "_no"
COL_TERM_NORM = "__term_norm"
COL_SCREEN = "_screen"
COL_SRC_FILE = "_src_file"
COL_SRC_SHEET = "_src_sheet"

# LLMプロンプト定数
LLM_SYSTEM_PROMPT = (
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

LLM_USER_PROMPT_TEMPLATE = (
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
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "true").lower() != "false",
 
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
    "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "#"),
    "VOCAB_TERM_COL": os.getenv("VOCAB_TERM_COL", "論理名"),
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名*"),
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
 
    # --- 類似度設定
    "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.72")),  # 候補プールの下限
    "TOP_K": int(os.getenv("TOP_K", "3")),  # 直接候補の上位件数
 
    # --- 出力
    "OUT_DIR": os.getenv("OUT_DIR", "out"),
 
    # --- 実行制御
    "TIMEOUT_SEC": float(os.getenv("TIMEOUT_SEC", "30")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "6")),
    "RETRY": int(os.getenv("RETRY", "30")),
 
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
    s = re.sub(r"[\-/・·•･,\(\)\[\]_]+", " ", s)    # 区切り記号はスペースへ
    return re.sub(r"\s+", " ", s)
 
 
def local_similarity(a: str, b: str) -> float:
    """簡易類似度：完全一致=1.0 / 片包含=0.9 / それ以外はdifflibのratio。"""
    a_n, b_n = zenkaku_hankaku_norm(a), zenkaku_hankaku_norm(b)
    if not a_n or not b_n:
        return 0.0
    if a_n == b_n:
        return EXACT_MATCH_SCORE
    if a_n in b_n or b_n in a_n:
        return PARTIAL_MATCH_SCORE
    return difflib.SequenceMatcher(None, a_n, b_n).ratio()
 
@dataclass
class Candidate:
    term: str
    score: float
 
# ====== Excel I/O =============================================================
 
def _int_env(name: str) -> Optional[int]:
    """環境変数を整数として取得。変換失敗時はNone。"""
    v = os.getenv(name, "")
    try:
        return int(v) if v else None
    except (ValueError, TypeError):
        return None
 
HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", str(DEFAULT_HEADER_SCAN_ROWS)))
SCREEN_HEADER_ROW = _int_env("SCREEN_HEADER_ROW")
VOCAB_HEADER_ROW = _int_env("VOCAB_HEADER_ROW")
 
 
def _normalize_text(text: str) -> str:
    """テキストをNFKC正規化し、小文字化・トリム。"""
    return unicodedata.normalize("NFKC", text).strip().lower()


def _pick_sheet_or_fallback(xls: pd.ExcelFile, preferred: Optional[str]) -> str:
    """優先シートが無ければ先頭。NFKCで厳密同名も考慮。"""
    if preferred and preferred in xls.sheet_names:
        return preferred
    if preferred:
        want = _normalize_text(preferred)
        for name in xls.sheet_names:
            if _normalize_text(name) == want:
                return name
    return xls.sheet_names[0]
 
 
def _pick_matching_sheets(xls: pd.ExcelFile, preferred: Optional[str]) -> List[str]:
    """設定シート名にマッチする全てのシートを返す。ワイルドカード対応。"""
    if not preferred:
        return [xls.sheet_names[0]]

    # 複数パターンをカンマ区切りで分割
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]

    # 全シート名を正規化
    norm_sheets = {_normalize_text(name): name for name in xls.sheet_names}

    # パターンマッチング（重複除去はdictで自動処理）
    matches = {}
    for pattern in patterns:
        regex_pattern = _normalize_text(pattern).replace('*', '.*')
        for norm_name, original_name in norm_sheets.items():
            if re.match(regex_pattern, norm_name) and original_name not in matches:
                matches[original_name] = True

    return list(matches.keys()) if matches else [xls.sheet_names[0]]
 
 
def _pick_matching_column(df: pd.DataFrame, col_pattern: str) -> Optional[str]:
    """列名パターンにマッチする最初の列を返す。ワイルドカード対応。"""
    if not col_pattern:
        return None

    # 完全一致チェック
    if col_pattern in df.columns:
        return col_pattern

    want = _normalize_text(col_pattern)

    # NFKC正規化で一致チェック
    for col in df.columns:
        if _normalize_text(str(col)) == want:
            return col

    # ワイルドカードパターンマッチング
    regex_pattern = want.replace('*', '.*')
    for col in df.columns:
        if re.match(regex_pattern, _normalize_text(str(col))):
            return col

    return None


def _detect_header_row(path: Path, sheet_name: str, required_cols: List[str], scan_rows: int) -> int:
    """先頭scan_rows行で必須列がそろう行をヘッダ行とみなす。ワイルドカード対応。"""
    head_df = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=scan_rows)

    # ワイルドカードを正規表現パターンに変換
    patterns = [zenkaku_hankaku_norm(col).replace('*', '.*') for col in required_cols if col]

    for row_idx, row in head_df.iterrows():
        # 行の有効な値を正規化
        row_values = [zenkaku_hankaku_norm(str(v)) for v in row if str(v) not in {"", "nan", "一致なし"}]

        # 全てのパターンがいずれかの値にマッチするかチェック
        if all(any(re.match(pat, val) for val in row_values) for pat in patterns):
            return row_idx

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
                # ワイルドカード対応の列名マッチング
                matched_col = _pick_matching_column(df_s, screen_col)
                if not matched_col:
                    print(f"[警告] {path.name}（{sheet_used}）: 必須列 '{screen_col}' にマッチする列が存在しません - スキップ")
                    continue
                # マッチした列名を統一名にリネーム
                if matched_col != screen_col:
                    print(f"[INFO] {path.name}（{sheet_used}）: 列 '{matched_col}' を '{screen_col}' として使用")
                    df_s = df_s.rename(columns={matched_col: screen_col})
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

                # ワイルドカード対応の列名マッチング（必須列）
                matched_term_col = _pick_matching_column(df_v, term_col)
                matched_phys_col = _pick_matching_column(df_v, phys_col)
                matched_no_col = _pick_matching_column(df_v, no_col)

                missing = []
                if not matched_term_col:
                    missing.append(term_col)
                if not matched_phys_col:
                    missing.append(phys_col)
                if not matched_no_col:
                    missing.append(no_col)

                if missing:
                    print(f"[警告] {path.name}（{sheet_used}）: 必須列が不足: {missing} - スキップ")
                    continue

                # マッチした列名を統一名にリネーム
                rename_map = {}
                if matched_term_col != term_col:
                    print(f"[INFO] {path.name}（{sheet_used}）: 列 '{matched_term_col}' を '{term_col}' として使用")
                    rename_map[matched_term_col] = term_col
                if matched_phys_col != phys_col:
                    print(f"[INFO] {path.name}（{sheet_used}）: 列 '{matched_phys_col}' を '{phys_col}' として使用")
                    rename_map[matched_phys_col] = phys_col
                if matched_no_col != no_col:
                    print(f"[INFO] {path.name}（{sheet_used}）: 列 '{matched_no_col}' を '{no_col}' として使用")
                    rename_map[matched_no_col] = no_col

                if rename_map:
                    df_v = df_v.rename(columns=rename_map)

                # 任意列（物理名略称）のマッチング
                matched_phys_abbr_col = _pick_matching_column(df_v, phys_abbr_col)
                if matched_phys_abbr_col and matched_phys_abbr_col != phys_abbr_col:
                    print(f"[INFO] {path.name}（{sheet_used}）: 列 '{matched_phys_abbr_col}' を '{phys_abbr_col}' として使用")
                    df_v = df_v.rename(columns={matched_phys_abbr_col: phys_abbr_col})
                elif not matched_phys_abbr_col:
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
    df_vocab[COL_TERM_NORM] = df_vocab[term_col].astype(str).map(zenkaku_hankaku_norm)
    df_vocab = df_vocab.rename(columns={
        term_col: COL_TERM,
        phys_col: COL_PHYS,
        phys_abbr_col: COL_PHYS_ABBR,
        no_col: COL_NO
    })
    df_screen = df_screen.rename(columns={
        screen_col: COL_SCREEN,
        "__source_file": COL_SRC_FILE,
        "__source_sheet": COL_SRC_SHEET
    })
 
    return df_screen, df_vocab
 
# ====== 候補生成（ローカル） ==================================================
 
def top_k_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """画面項目 vs 単語帳の**直接照合**で上位k件を返却。"""
    scored = [Candidate(term, local_similarity(screen_name, term)) for term in vocab_terms]
    scored.sort(key=lambda c: c.score, reverse=True)
    return [c for c in scored[:k] if c.score >= threshold]
 
 
def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語対策：unigram/bigram に分解してパーツ単位で候補を拾う。"""
    tokens = zenkaku_hankaku_norm(screen_name).split()
    grams = set(tokens + [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)])

    # 各単語の最高スコアを辞書内包表記で収集
    best_scores = {}
    for gram in grams:
        for term in vocab_terms:
            score = local_similarity(gram, term)
            if score >= threshold:
                best_scores[term] = max(best_scores.get(term, 0.0), score)

    # スコア降順でソート
    candidates = sorted([Candidate(t, s) for t, s in best_scores.items()],
                       key=lambda c: c.score, reverse=True)
    return candidates[:max(k, 10)]
 
# ====== APIクライアント =======================================================
class ApiClient:
    """OpenAI互換APIへの最小ラッパ（ヘッダ/プロキシ/SSL検証対応）。"""
    def __init__(self, cfg: Dict[str, Any]):
        self.base_url = cfg["OPENAI_BASE_URL"].rstrip("/")
        self.path = cfg["OPENAI_PATH"]
        self.timeout = cfg["TIMEOUT_SEC"]
        # PyInstallerビルド時の証明書検証対応
        if cfg["VERIFY_SSL"]:
            self.verify = CA_BUNDLE
        else:
            self.verify = False
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
        """APIリクエストを送信してJSONレスポンスを返す。"""
        url = f"{self.base_url}{self.path}"
        resp = self.session.post(url, headers=self.headers, json=body,
                                timeout=self.timeout, verify=self.verify)
        resp.raise_for_status()
        return resp.json()
 
# ====== LLM呼び出し ==========================================================

def build_llm_payload(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any], term_meta: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """LLM呼び出しペイロードを構築（厳密JSON指定）。"""
    cand_payload = []
    for c in candidates:
        item = {"term": c.term, "local_score": round(c.score, 4)}
        if term_meta and c.term in term_meta:
            meta = term_meta[c.term]
            phys = meta.get("_phys_abbr") or meta.get("_phys")
            if phys:
                item["physical_name"] = phys
        cand_payload.append(item)
    return {
        "model": cfg["OPENAI_MODEL"],
        "max_tokens": cfg["MAX_TOKENS"],
        "temperature": cfg["TEMPERATURE"],
        "top_p": cfg["TOP_P"],
        "presence_penalty": cfg["PRESENCE_PENALTY"],
        "frequency_penalty": cfg["FREQUENCY_PENALTY"],
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": LLM_USER_PROMPT_TEMPLATE.format(
                screen_name=screen_name,
                candidates_json=json.dumps(cand_payload, ensure_ascii=False, indent=2),
            )},
        ],
    }


 
 
def call_llm(screen_name: str, candidates: List[Candidate], cfg: Dict[str, Any], client: Optional[ApiClient] = None, api_semaphore: Optional[threading.Semaphore] = None, term_meta: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """LLM呼び出し。失敗時はフォールバック。"""
    # テストモード判定
    if cfg.get("TEST_MODE", False) or os.getenv("WORD_MATCHING_TEST_MODE", "false").lower() == "true":
        try:
            from tests.mock_api import mock_llm_response
            return mock_llm_response(screen_name, candidates)
        except ImportError:
            print("[警告] tests/mock_api.pyが見つかりません。フォールバックを使用します。")
            return fallback_reason(screen_name, candidates)
 
    client = client or ApiClient(cfg)
    payload = build_llm_payload(screen_name, candidates, cfg, term_meta)
 
    # セマフォで同時実行API数を制限
    if api_semaphore:
        api_semaphore.acquire()

    try:
        for attempt in range(cfg["RETRY"] + 1):
            try:
                data = client.post_json(payload)
                return json.loads(data["choices"][0]["message"]["content"])
            except Exception as e:
                # 認証エラーは即座に例外を投げる
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) in [401, 403]:
                    raise Exception(f"API認証エラー: APIキーまたはユーザIDが無効です") from e
                # リトライ上限に達していなければバックオフして再試行
                if attempt < cfg["RETRY"]:
                    time.sleep(RETRY_BACKOFF_MULTIPLIER * (attempt + 1))
                else:
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
    if top.score >= FALLBACK_EXACT_THRESHOLD:
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
    """lowerCamelCaseの簡易物理名を生成（8〜10文字程度）。"""
    tokens = zenkaku_hankaku_norm(text).split()
    if not tokens:
        return "newItem"

    # 冗長語を除外してコア要素を取得
    stop_words = {"コード", "番号", "名称名", "名称名称"}
    core = [w for w in tokens[:3] if w not in stop_words] or tokens[:2]

    # lowerCamelCase化して長さ制御
    name = core[0].lower() + "".join(w.capitalize() for w in core[1:])
    return name[:8] if len(name) > 10 else name or "newItem"
 
# ====== メイン処理 ============================================================
 
def process(dir_path: Path, screen_col: Optional[str], vocab_col: Optional[str], cfg: Dict[str, Any], progress_callback=None) -> pd.DataFrame:
    """全体フロー：入力→候補生成→（完全一致なら即決）→LLM判定→集計DataFrame。"""
    df_screen, df_vocab = load_screen_and_vocab(dir_path, cfg, screen_col, vocab_col)
    # 全体件数（進捗ログ用）
    total_items = len(df_screen)
    processed_count = 0
 
    vocab_terms = df_vocab[COL_TERM].astype(str).tolist()
    term_meta = df_vocab[[COL_TERM, COL_PHYS, COL_PHYS_ABBR, COL_NO]].drop_duplicates(COL_TERM).set_index(COL_TERM).to_dict(orient="index")
    norm_to_term = df_vocab[[COL_TERM_NORM, COL_TERM]].drop_duplicates(COL_TERM_NORM).set_index(COL_TERM_NORM)[COL_TERM].to_dict()
 
    rows: List[Dict[str, Any]] = []
    api_client = ApiClient(cfg)
 
    # API同時実行数を制限するセマフォ
    max_concurrent_api = cfg.get("MAX_CONCURRENT_API", 3)
    api_semaphore = threading.Semaphore(max_concurrent_api)
 
    def _log_progress(count: int, total: int) -> None:
        """進捗ログを出力（定期的 or 完了時）。"""
        pct = count * 100 / total if total else 0
        if count % PROGRESS_LOG_INTERVAL == 0 or count == total:
            print(f"[INFO] {count}/{total} 件処理済み ({pct:.1f}%)")
        if progress_callback:
            progress_callback(count, total)

    def _get_metadata(term: Optional[str]) -> Dict[str, Any]:
        """単語のメタデータを取得。"""
        if not term:
            return {"no": None, "phys": None, "phys_abbr": None}
        m = term_meta.get(str(term), {})
        return {"no": m.get(COL_NO), "phys": m.get(COL_PHYS), "phys_abbr": m.get(COL_PHYS_ABBR)}

    def _get_phys_name(metadata: Dict[str, Any], fallback: str = "") -> str:
        """物理名を取得（略称 > 正式名称 > フォールバック）。"""
        return metadata.get("phys_abbr") or metadata.get("phys") or simple_proposal(fallback)

    def _build_exact_match_result(screen_name: str, src_file: str, src_sheet: Optional[str],
                                   term: str, metadata: Dict[str, Any], score: float, reason: str) -> Dict[str, Any]:
        """完全一致結果の辞書を構築。"""
        phys_name = _get_phys_name(metadata)
        term_no = metadata.get("no")
        return {
            "source_file": src_file,
            "source_sheet": src_sheet,
            "screen_item": screen_name,
            "match_type": MATCH_TYPE_EXACT,
            "matched_term": term,
            "matched_term_no": term_no,
            "matched_term_phys": phys_name,
            "matched_terms": None,
            "matched_terms_nos": None,
            "matched_terms_phys": None,
            "local_top_term": term,
            "local_top_term_no": term_no,
            "local_top_term_phys": phys_name,
            "local_top_score": score,
            "coverage_ratio": 1.0,
            "proposed_name": _get_phys_name(metadata, term),
            "reason": reason,
            "unmatched_terms": None,
            "unmatched_note": None,
        }
 
    def worker(screen_name: str, src_file: str, src_sheet: Optional[str]) -> Dict[str, Any]:
        """1件の画面項目に対する判定ワーカー（スレッドで実行）。"""
        # --- 0) 正規化ベースの完全一致 → LLMスキップ
        exact_term = norm_to_term.get(zenkaku_hankaku_norm(screen_name))
        if exact_term:
            return _build_exact_match_result(
                screen_name, src_file, src_sheet, exact_term,
                _get_metadata(exact_term), EXACT_MATCH_SCORE,
                "正規化完全一致（LLM未呼び出し）"
            )
 
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
        if merged and merged[0].score >= EXACT_MATCH_SCORE:
            top = merged[0]
            if zenkaku_hankaku_norm(screen_name) == zenkaku_hankaku_norm(top.term):
                return _build_exact_match_result(
                    screen_name, src_file, src_sheet, top.term,
                    _get_metadata(top.term), top.score,
                    f"ローカル完全一致（score={top.score:.2f}、LLM未呼び出し）"
                )
 
        # --- 3) LLMに最終判定を委譲（一部一致/一致なし）
        llm = call_llm(screen_name, merged, cfg, api_client, api_semaphore, term_meta)
 
        # 値の整形ヘルパー
        safe_float = lambda v: float(v) if v not in (None, "") else None
        join_if_exists = lambda items, sep=", ": sep.join(str(i) for i in items) if items else None

        # メタデータ取得
        mt_meta = _get_metadata(llm.get("matched_term"))
        matched_terms = llm.get("matched_terms") or []
        mts_metas = [_get_metadata(t) for t in matched_terms]
        top_meta = _get_metadata(merged[0].term) if merged else {}

        return {
            "source_file": src_file,
            "source_sheet": src_sheet,
            "screen_item": screen_name,
            "match_type": llm.get("match_type"),
            "matched_term": llm.get("matched_term"),
            "matched_term_no": mt_meta.get("no"),
            "matched_term_phys": _get_phys_name(mt_meta),
            "matched_terms": join_if_exists(matched_terms),
            "matched_terms_nos": join_if_exists([m.get("no") for m in mts_metas if m.get("no")]),
            "matched_terms_phys": join_if_exists([_get_phys_name(m) for m in mts_metas if _get_phys_name(m)]),
            "local_top_term": merged[0].term if merged else None,
            "local_top_term_no": top_meta.get("no"),
            "local_top_term_phys": _get_phys_name(top_meta),
            "local_top_score": merged[0].score if merged else None,
            "coverage_ratio": safe_float(llm.get("coverage_ratio")),
            "reason": llm.get("reason"),
            "proposed_name": llm.get("proposed_name"),
            "unmatched_terms": join_if_exists(llm.get("unmatched_terms") or []),
            "unmatched_note": join_if_exists(llm.get("unmatched_notes") or [], " / "),
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
                _log_progress(processed_count, total_items)
            except Exception as e:
                # ワーカー失敗時も処理を止めない
                error_row = {
                    "source_file": "<error>", "source_sheet": "-", "screen_item": "-",
                    "match_type": "一致なし", "reason": f"worker error: {e}", "proposed_name": None,
                }
                rows.append(error_row)
                processed_count += 1
                _log_progress(processed_count, total_items)
 
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
 
        # --- 5) 条件付き書式（「一部一致」「一致なし」を色付け）
        if len(df) > 0:
            ws = w.sheets["結果"]
 
            # 2段見出しなのでデータ開始行
            start_row = EXCEL_DATA_START_ROW
            end_row = start_row + len(df) - 1
 
            # 列インデックス（1始まり）を取得
            col_index = {col: i+1 for i, col in enumerate(df.columns)}
            mt_idx = col_index[("【結果】", "一致状況")]
            si_idx = col_index[("【対象項目】", "項目名")]
 
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
 
 
def detect_and_save_proxy() -> None:
    """システムのプロキシ設定を検出して.envに保存"""
    import urllib.request

    # 既に.envにプロキシ設定がある場合はスキップ
    if os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"):
        return

    # システムプロキシを自動検出
    proxies = urllib.request.getproxies()

    if proxies:
        env_path = app_root() / ".env"
        env_lines = []

        # 既存の.envを読み込み
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                env_lines = f.readlines()

        # プロキシ設定を追加
        proxy_settings = []
        if "http" in proxies:
            proxy_settings.append(f"HTTP_PROXY={proxies['http']}\n")
            print(f"[INFO] 検出されたHTTPプロキシ: {proxies['http']}")
        if "https" in proxies:
            proxy_settings.append(f"HTTPS_PROXY={proxies['https']}\n")
            print(f"[INFO] 検出されたHTTPSプロキシ: {proxies['https']}")

        if proxy_settings:
            # 既存のプロキシ設定行を削除
            env_lines = [line for line in env_lines if not line.startswith("HTTP_PROXY=") and not line.startswith("HTTPS_PROXY=")]

            # 新しいプロキシ設定を追加
            env_lines.extend(["\n# 自動検出されたプロキシ設定\n"] + proxy_settings)

            # .envに書き込み
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(env_lines)

            print(f"[INFO] プロキシ設定を {env_path} に保存しました")

            # 環境変数に即座に反映
            for key, value in proxies.items():
                if key == "http":
                    os.environ["HTTP_PROXY"] = value
                elif key == "https":
                    os.environ["HTTPS_PROXY"] = value


def main() -> None:
    # PyInstallerでビルドされたEXEの場合、.envファイルを明示的に読み込む
    if getattr(sys, "frozen", False):
        # EXEの場合: 実行ファイルと同じディレクトリ or 一時展開先の.envを探す
        exe_dir = Path(sys.executable).parent
        env_candidates = [
            exe_dir / ".env",  # EXEと同じフォルダ
            Path(sys._MEIPASS) / ".env" if hasattr(sys, "_MEIPASS") else None,  # 一時展開先
            app_root() / ".env",  # 元のディレクトリ
        ]
        for env_path in env_candidates:
            if env_path and env_path.exists():
                load_dotenv(env_path)
                print(f"[INFO] .envファイルを読み込みました: {env_path}")
                break
    else:
        # 通常のPython実行時
        load_dotenv()
        detect_and_save_proxy()

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
 
 