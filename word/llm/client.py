#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLMクライアントとペイロード構築"""

import json
import re
import sys
import threading
import time
from string import Template
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from ..matching.primitives import Candidate, ComponentMatchResult
try:
    from ..settings import LLM_SYSTEM, LLM_USER_TEMPLATE
except ImportError:  # pragma: no cover - fallback when run as a script
    from settings import LLM_SYSTEM, LLM_USER_TEMPLATE  # type: ignore
    from matching.primitives import Candidate, ComponentMatchResult  # type: ignore
try:
    from ..utils import zenkaku_hankaku_norm, normalize_term_no
except ImportError:  # pragma: no cover - fallback when run as a script
    from utils import zenkaku_hankaku_norm, normalize_term_no  # type: ignore
class LLMExecutor:
    """LLM呼び出し時のクライアントとセマフォを束ねた実行ヘルパー。"""

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.client = ApiClient(cfg)
        self.semaphore = threading.Semaphore(cfg.get("MAX_CONCURRENT_API", 3))

    def __call__(
        self,
        screen_name: str,
        candidates: List[Candidate],
        term_metadata: Optional[Dict[str, Dict[str, Any]]],
        component_result: Optional[ComponentMatchResult],
        extra_component_terms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return call_llm(
            screen_name,
            candidates,
            self.cfg,
            self.client,
            self.semaphore,
            term_metadata,
            component_result,
            extra_component_terms=extra_component_terms,
        )





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


def build_candidate_payload(
    candidates: List[Candidate],
    component_result: Optional[ComponentMatchResult],
    term_metadata: Optional[Dict[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """候補リストを LLM へ渡す辞書形式に整形する。"""

    payload: List[Dict[str, Any]] = []
    component_terms = set(component_result.matched_terms) if component_result else set()
    component_order: Dict[str, int] = {}
    if component_result:
        for order, term in enumerate(component_result.matched_terms, start=1):
            component_order.setdefault(term, order)

    for rank, candidate in enumerate(candidates, start=1):
        item: Dict[str, Any] = {
            "term": candidate.term,
            "normalized_term": zenkaku_hankaku_norm(candidate.term),
            "local_score": round(candidate.score, 4),
            "local_rank": rank,
            "from_component": candidate.term in component_terms,
        }
        if item["from_component"]:
            component_rank = component_order.get(candidate.term)
            if component_rank is not None:
                item["component_rank"] = component_rank
        if term_metadata:
            meta = term_metadata.get(candidate.term)
            if meta:
                term_no = normalize_term_no(meta.get("_no"))
                if term_no is not None:
                    item["term_no"] = term_no
                phys_abbr = (meta.get("_phys_abbr") or "").strip()
                phys_full = (meta.get("_phys") or "").strip()
                if phys_abbr:
                    item["physical_name"] = phys_abbr
                    if phys_full and phys_full != phys_abbr:
                        item["physical_name_full"] = phys_full
                elif phys_full:
                    item["physical_name"] = phys_full
        payload.append(item)
    return payload


def build_llm_payload(
    screen_name: str,
    candidates: List[Candidate],
    cfg: Dict[str, Any],
    term_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    component_result: Optional[ComponentMatchResult] = None,
    extra_component_terms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """LLM呼び出しペイロードを構築（厳密JSON指定）。"""

    cand_payload = build_candidate_payload(candidates, component_result, term_metadata)
    component_payload: Optional[Dict[str, Any]] = None
    if component_result:
        hint = "no_component_hit"
        if component_result.matched_terms:
            if not component_result.unmatched_segments and (
                component_result.has_non_digit or not component_result.digit_segments
            ):
                hint = "component_full"
            elif not component_result.has_non_digit and component_result.digit_segments:
                hint = "digits_only"
            else:
                hint = "component_partial"
        tokens_for_llm = extra_component_terms or component_result.matched_terms
        component_payload = {
            "normalized_screen": zenkaku_hankaku_norm(screen_name),
            "component_tokens": tokens_for_llm,
            "component_tokens_norm": component_result.matched_norms,
            "unmatched_fragments": component_result.unmatched_segments,
            "digit_segments": component_result.digit_segments,
            "coverage_ratio": round(component_result.coverage_ratio, 4),
            "has_non_digit": component_result.has_non_digit,
            "expected_match_hint": hint,
        }
        if extra_component_terms and extra_component_terms != component_result.matched_terms:
            component_payload["component_tokens_original"] = component_result.matched_terms
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
            {
                "role": "user",
                "content": Template(LLM_USER_TEMPLATE).safe_substitute(
                    screen_name=screen_name,
                    component_json=(
                        json.dumps(component_payload, ensure_ascii=False, indent=2)
                        if component_payload is not None
                        else "null"
                    ),
                    candidates_json=json.dumps(cand_payload, ensure_ascii=False, indent=2),
                ),
            },
        ],
    }


def call_llm(
    screen_name: str,
    candidates: List[Candidate],
    cfg: Dict[str, Any],
    client: Optional[ApiClient] = None,
    api_semaphore: Optional[threading.Semaphore] = None,
    term_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    component_result: Optional[ComponentMatchResult] = None,
    extra_component_terms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """LLM呼び出し。失敗時はフォールバック。"""

    client = client or ApiClient(cfg)
    payload = build_llm_payload(
        screen_name,
        candidates,
        cfg,
        term_metadata=term_metadata,
        component_result=component_result,
        extra_component_terms=extra_component_terms,
    )
    # サーバー負荷対策：セマフォで同時実行API数を制限
    if api_semaphore:
        api_semaphore.acquire()
    try:
        for attempt in range(cfg["RETRY"] + 1):
            try:
                data = client.post_json(payload)
                content = data["choices"][0]["message"]["content"]
                result = json.loads(content)
                return result
            except Exception as e:
                # API認証エラーの場合はリトライせずに即座に例外を投げる
                error_msg = str(e)
                print(f"[ERROR] LLM API failed for {screen_name}: {error_msg}", file=sys.stderr)
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    if status_code in [401, 403]:
                        raise Exception(f"API認証エラー (HTTP {status_code}): APIキーまたはユーザIDが無効です") from e
                # その他のエラーの場合はリトライ
                if attempt < cfg["RETRY"]:
                    time.sleep(1.2 * (attempt + 1))  # バックオフ
                    continue
                return fallback_reason(screen_name, candidates, term_metadata, error_msg)
    finally:
        if api_semaphore:
            api_semaphore.release()


def fallback_reason(
    screen_name: str,
    candidates: List[Candidate],
    term_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
    """ネットワーク障害や破損時の**最小限の結論**。"""

    def _error_prefix() -> str:
        return f"APIエラー: {error_message}" if error_message else "API応答なし"

    if not candidates:
        reason = _error_prefix()
        if not error_message:
            reason = "API不達/候補なし。後日、単語帳の拡充を検討してください。"
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "reason": reason,
            "proposed_name": simple_proposal(screen_name),
        }

    top = candidates[0]
    local_hint = f"ローカル候補: {top.term} (score={top.score:.2f})"
    reason = f"{_error_prefix()} / {local_hint}"
    if not error_message:
        reason = f"API応答なし / {local_hint}"
    return {
        "match_type": "一致なし",
        "matched_term": None,
        "reason": reason,
        "proposed_name": simple_proposal(top.term),
    }


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
    return name or "newItem"


def summarize_matched_terms(
    matched_terms: List[str],
    meta_lookup: Callable[[str], Dict[str, Any]],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """一致語とメタ情報を表示用に整形する。"""

    if not matched_terms:
        return None, None, None

    metas = [meta_lookup(term) for term in matched_terms]
    numbers = [
        str(no)
        for no in (normalize_term_no(meta.get("no")) for meta in metas)
        if no is not None
    ]
    phys_names = [
        str(meta.get("phys_abbr") or meta.get("phys") or "")
        for meta in metas
        if (meta.get("phys_abbr") or meta.get("phys"))
    ]
    display = ", ".join(str(term) for term in matched_terms)
    joined_numbers = ", ".join(numbers) if numbers else None
    joined_phys = ", ".join(phys_names) if phys_names else None
    return display or None, joined_numbers, joined_phys
