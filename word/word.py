#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import concurrent.futures as cf
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv

# 主要コンポーネントをインポート
from .settings import DEFAULT_CONFIG
from .utils import normalize_term_no
from .llm.client import LLMExecutor
from .matching.selectors import CandidateSelector
from .matching.resolvers import ExactMatchResolver
from .matching.formatters import build_result_row
from .io import load_screen_and_vocab, save_outputs
# .envファイルを読み込み（Streamlitからインポートされる前に環境変数を設定）
# Dockerコンテナ内: /app/word/word.py → /app/.env
from pathlib import Path as _EnvPath
_env_file = _EnvPath(__file__).parent.parent / '.env'
if _env_file.exists():
    load_dotenv(_env_file)
del _env_file, _EnvPath


# ====== メイン処理 ============================================================


def process(
    dir_path: Path,
    screen_col: Optional[str],
    vocab_col: Optional[str],
    cfg: Dict[str, Any],
    progress_callback=None,
) -> pd.DataFrame:
    """Excelから画面項目と単語帳を取り込み、候補生成〜LLM判定までを一気通貫で実行。

    流れ:
        1. Excelから画面項目の一覧と単語帳（論理名/物理名/番号）をDataFrameとして読み込む。
        2. 単語帳を基に、候補探索と結果整形に使うキャッシュを構築する。
        3. 画面項目ごとに、
            a. 正規化による完全一致を確認し、即決できれば終了。
            b. ComponentMatcherと類似度で候補語を抽出し、LLMに判定を依頼。
            c. LLMの応答とメタ情報をまとめて1行の結果として整形。
        4. 全件を並列処理し、結果DataFrameを返す。
    """

    # --- 1) 画面項目Excelと単語帳Excelを読み込み、DataFrameに整形
    df_screen, df_vocab = load_screen_and_vocab(dir_path, cfg, screen_col, vocab_col)
    total_items = len(df_screen)
    processed_count = 0

    # --- 2) 単語帳を加工し、候補抽出と結果整形の両方で参照するキャッシュを準備
    # vocabulary_terms: 類似度/N-gram 計算に使う「生の論理名」のリスト（正規化だけでは拾えない候補用）
    vocabulary_terms = df_vocab["_term"].astype(str).tolist()
    # term_metadata: 物理名・略称・番号を保持し、LLM ペイロード／最終出力の双方で参照する辞書
    term_metadata = (
        df_vocab[["_term", "_phys", "_phys_abbr", "_no"]]
        .drop_duplicates("_term").set_index("_term").to_dict(orient="index")
    )
    # normalized_term_lookup: 正規化キー→論理名の逆引き辞書（完全一致ショートカットと ComponentMatcher の分割に使用）
    normalized_term_lookup = (
        df_vocab[["__term_norm", "_term"]]
        .drop_duplicates("__term_norm").set_index("__term_norm")["_term"].to_dict()
    )

    # --- 3) 候補抽出ロジックと完全一致解決・LLM 実行エンジンを初期化
    candidate_selector = CandidateSelector(vocabulary_terms, normalized_term_lookup, cfg)
    exact_match_resolver = ExactMatchResolver(normalized_term_lookup, term_metadata)
    result_rows: List[Dict[str, Any]] = []  # 最終的に返す結果行を蓄積
    llm_executor = LLMExecutor(cfg)  # LLM 呼び出しクライアントとセマフォをまとめて管理

    # --- 4) LLM 応答から論理名を受け取った際にメタ情報を補完するヘルパー
    def lookup_term_metadata(term: Optional[str]) -> Dict[str, Any]:
        """LLM応答で戻る論理名をキーに、物理名や番号を引き当てる。"""

        if not term:
            return {"no": None, "phys": None, "phys_abbr": None}
        meta = term_metadata.get(str(term)) or {}
        return {
            "no": normalize_term_no(meta.get("_no")),
            "phys": meta.get("_phys"),
            "phys_abbr": meta.get("_phys_abbr"),
        }

    # --- 5) 処理進捗をログ出力し、必要ならコールバックへ通知
    def report_progress() -> None:
        pct = processed_count * 100 / total_items if total_items else 0
        if processed_count % 10 == 0 or processed_count == total_items:
            print(f"[INFO] {processed_count}/{total_items} 件処理済み ({pct:.1f}%)")
        if progress_callback:
            progress_callback(processed_count, total_items)

    # --- 6) 各画面項目を判定するワーカー（完全一致 → 候補抽出 → LLM 判定の順に処理）
    def worker(screen_name: str, src_file: str, src_sheet: Optional[str]) -> Dict[str, Any]:
        """1件の画面項目に対する判定ワーカー（スレッドで実行）。"""

        # 6-1) 正規化完全一致で即座に確定
        exact_row = exact_match_resolver.resolve(screen_name, src_file, src_sheet)
        if exact_row:
            return exact_row

        # 6-2) candidate_selector.select で候補抽出（正規化辞書で分割しつつ、生論理名で類似度評価まで一体処理）
        component_analysis, ranked_candidates, ranked_terms = candidate_selector.select(screen_name)

        # 6-3) LLMで最終判定を実施
        llm_response = llm_executor(
            screen_name,
            ranked_candidates,
            term_metadata,
            component_analysis,
            extra_component_terms=ranked_terms,
        )

        # 6-4) 判定結果を整形して返却
        return build_result_row(
            screen_name,
            src_file,
            src_sheet,
            component_analysis,
            ranked_candidates,
            ranked_terms,
            llm_response,
            term_metadata,
            lookup_term_metadata,
        )

    # --- 7) 画面項目ごとの判定をスレッドプールで並列処理
    screen_rows_for_workers = (
        df_screen[["_screen", "_src_file", "_src_sheet"]]
        .astype(str)
        .values
        .tolist()
    )  # Excelの行をワーカーに渡しやすい形に整える
    worker_count = min(cfg["MAX_WORKERS"], max(1, len(screen_rows_for_workers)))
    with cf.ThreadPoolExecutor(max_workers=worker_count) as executor:
        worker_futures = [
            executor.submit(worker, row[0], row[1], row[2]) for row in screen_rows_for_workers
        ]
        for future in cf.as_completed(worker_futures):
            try:
                result_row = future.result()
            except Exception as exc:
                result_row = {
                    "source_file": "<error>",
                    "source_sheet": "-",
                    "screen_item": "-",
                    "match_type": "一致なし",
                    "reason": f"worker error: {exc}",
                    "proposed_name": None,
                }
            result_rows.append(result_row)
            processed_count += 1
            report_progress()
    return pd.DataFrame(result_rows).reset_index(drop=True)
