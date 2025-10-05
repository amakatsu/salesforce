#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM呼び出しハンドラー
プロンプト構築・API呼び出し
"""
import json
import threading
from typing import Dict, Any, List, Optional
from .text_utils import Candidate


# 定数
HARD_EXACT_SCORE = 1.0  # 完全一致のスコア
FALLBACK_EXACT_FLOOR = 0.95  # フォールバック時の完全一致判定閾値


def build_llm_prompt(
    screen_name: str,
    candidates: List[Candidate],
    term_meta: Optional[Dict[str, Dict[str, Any]]] = None
) -> tuple[str, str]:
    """
    LLMプロンプトを構築

    Args:
        screen_name: 画面項目名
        candidates: 候補リスト
        term_meta: 単語のメタデータ（物理名など）

    Returns:
        (システムプロンプト, ユーザープロンプト)
    """
    system_prompt = """あなたは画面項目名と単語を照合する専門家です。
画面項目名に最も適した単語を選択し、JSON形式で回答してください。"""

    candidate_list = []
    for i, cand in enumerate(candidates, 1):
        meta_info = ""
        if term_meta and cand.term in term_meta:
            meta = term_meta[cand.term]
            if meta.get("physical_name"):
                meta_info = f" (物理名: {meta['physical_name']})"
        candidate_list.append(f"{i}. {cand.term} (類似度: {cand.score:.2f}){meta_info}")

    user_prompt = f"""画面項目名: {screen_name}

候補:
{chr(10).join(candidate_list)}

最も適切な候補を選択し、以下のJSON形式で回答してください:
{{"selected": "選択した単語", "confidence": "high/medium/low", "reason": "選択理由"}}"""

    return system_prompt, user_prompt


def call_llm_api(
    screen_name: str,
    candidates: List[Candidate],
    cfg: Dict[str, Any],
    client=None,
    api_semaphore: Optional[threading.Semaphore] = None,
    term_meta: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    LLM APIを呼び出して最適な単語を選択

    Args:
        screen_name: 画面項目名
        candidates: 候補リスト
        cfg: 設定
        client: APIクライアント
        api_semaphore: API同時実行制御用セマフォ
        term_meta: 単語メタデータ

    Returns:
        LLMの応答（JSON）
    """
    system_prompt, user_prompt = build_llm_prompt(screen_name, candidates, term_meta)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": cfg.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": messages,
        "max_tokens": cfg.get("MAX_TOKENS", 800),
        "temperature": cfg.get("TEMPERATURE", 0.7),
        "top_p": cfg.get("TOP_P", 0.95),
        "response_format": {"type": "json_object"}
    }

    # API呼び出し（セマフォで同時実行数制御）
    if api_semaphore:
        with api_semaphore:
            response = client.post_json(payload)
    else:
        response = client.post_json(payload)

    return response


def create_fallback_response(
    screen_name: str,
    candidates: List[Candidate]
) -> Dict[str, Any]:
    """
    LLM呼び出し失敗時のフォールバック応答を生成

    Args:
        screen_name: 画面項目名
        candidates: 候補リスト

    Returns:
        フォールバック応答
    """
    if not candidates:
        return {
            "selected": "",
            "confidence": "none",
            "reason": "候補が見つかりませんでした"
        }

    top_candidate = candidates[0]
    confidence = "high" if top_candidate.score >= FALLBACK_EXACT_FLOOR else "low"

    return {
        "selected": top_candidate.term,
        "confidence": confidence,
        "reason": f"類似度スコア: {top_candidate.score:.2f}（フォールバック）"
    }
