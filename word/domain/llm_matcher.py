#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B方式 -- LLMパイプライン最終判定

C方式（domain_matcher.py）が収集した MatchEvidence を受け取り、
LLMで最終判定を行うパイプラインの後段。

パイプライン全体像:
    C方式（前処理・情報収集） -> B方式（LLM最終判定）
    domain_matcher.py          -> llm_matcher.py (this)

仕様書 Section 3-6 準拠:
    - C方式が集めた材料（型桁一致候補・同義語ヒット・部分一致）を受け取る
    - バッチでまとめてLLMに投げ、コスト最適化
    - LLM判定結果は「候補提案」として出力（自動確定はしない）
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from word.ai_handlers.common_llm import (
    build_chat_payload,
    build_headers,
    post_chat_requests,
)

if TYPE_CHECKING:
    from .domain_matcher import MatchEvidence
    from pr_agent.config_loader import Settings

logger = logging.getLogger("domain_tool.llm_matcher")

# LLM呼び出し関数の型。外部から注入する。
# (system_prompt: str, user_prompt: str) -> str
LlmCallFn = Callable[[str, str], str]

# ============================================================================
# 結果型
# ============================================================================

# LLMから受け付ける判定結果の値（自動確定 "exact" は禁止）
_VALID_LLM_MATCH_TYPES = frozenset({"suggested", "human_choice", "no_match", "new_domain"})


@dataclass
class MatchResult:
    """LLM最終判定の結果。

    Attributes:
        item_name: 対象項目名（数字除去済み）
        match_type: 判定結果
            - "suggested"    : LLMによる候補提案（最終確定は人間が行う）
            - "human_choice" : 人間選択が必要（フラグ系・コメント/補記系）
            - "no_match"     : 一致なし
        suggested_domain: 提案されたドメイン名（なければ空文字）
        candidates: 人間選択用の候補リスト（human_choice時に使用）
        check_point: 人間への確認事項（例: "改行有無を確認"）
        confidence: 信頼度 0.0--1.0
        reason: 判定理由の説明
        generalized_candidates: 汎化候補（既存ドメイン候補）
    """
    item_name: str
    match_type: str
    suggested_domain: str = ""
    candidates: list[str] | None = None
    check_point: str = ""
    confidence: float = 0.0
    reason: str = ""
    generalized_candidates: list[str] | None = None


# ============================================================================
# 公開API
# ============================================================================


def run_llm_matching(
    evidences: list[MatchEvidence],
    config: dict[str, Any],
    llm_call: LlmCallFn | None = None,
) -> list[MatchResult]:
    """C方式の証拠をもとにLLMで最終判定を行う。

    仕様書 Section 3-6:
      - C方式が集めた材料を受け取り、意味的類似度を最終判断
      - バッチで投げてコスト最適化
      - LLM判定結果は「候補提案」として出力（自動確定はしない）

    Args:
        evidences: C方式が収集した MatchEvidence のリスト。
            is_resolved=True のものは C方式で確定済み（ここでは処理しない）。
            is_resolved=False のもの（needs_llm）がLLM判定対象。
        config: get_domain_config() の返却値。LLM設定を含む。
        llm_call: LLM呼び出し関数。None の場合はC方式の証拠から
            フォールバック判定を行う。

    Returns:
        各 evidence に対応する MatchResult のリスト（入力と同じ順序）
    """
    # LLM判定が必要な evidence のみ抽出（インデックスを保持）
    llm_targets: list[tuple[int, MatchEvidence]] = []
    results: list[MatchResult | None] = [None] * len(evidences)

    for i, ev in enumerate(evidences):
        if ev.is_resolved:
            results[i] = _resolved_evidence_to_result(ev)
        else:
            llm_targets.append((i, ev))

    if not llm_targets:
        logger.info("LLM判定対象なし（全%d件がC方式で確定済み）", len(evidences))
        return [r for r in results if r is not None]

    # LLM呼び出しが利用可能な場合: バッチプロンプトで一括判定
    if llm_call is not None:
        _run_batch_llm(llm_targets, results, llm_call)
    else:
        logger.info(
            "LLM呼び出し未設定 -- %d件をC方式の証拠からフォールバック判定",
            len(llm_targets),
        )
        for idx, ev in llm_targets:
            results[idx] = _fallback_from_evidence(ev)

    return [r for r in results if r is not None]


# ============================================================================
# LLM呼び出し関数ビルダー
# ============================================================================


def _get_settings_config() -> dict[str, Any]:
    """pr-agent settings から config を取得（wordmatching準拠）。"""
    try:
        from pr_agent.config_loader import get_settings
        settings = get_settings()
        return settings.config if hasattr(settings, "config") else {}
    except Exception:
        return {}


def build_llm_call(config: dict[str, Any]) -> LlmCallFn:
    """OpenAI互換API向けの LLM 呼び出し関数を構築する（wordmatching準拠）。"""
    settings_cfg = _get_settings_config()

    base_url = str(config.get("OPENAI_BASE_URL", settings_cfg.get("openai.api_base", ""))).rstrip("/")
    path = str(config.get("OPENAI_PATH", settings_cfg.get("openai.path", "")))
    url = f"{base_url}{path}"
    timeout = float(config.get("TIMEOUT_SEC", settings_cfg.get("ai_timeout", 120)))
    verify = bool(config.get("OPENAI_VERIFY_SSL", config.get("VERIFY_SSL", True)))

    headers: dict[str, str] = {"Content-Type": "application/json"}
    # pr-agent custom_headers 優先
    custom_headers = settings_cfg.get("custom_headers", {})
    if isinstance(custom_headers, str):
        try:
            custom_headers = json.loads(custom_headers)
        except json.JSONDecodeError:
            custom_headers = {}
    extra = config.get("OPENAI_HEADERS_JSON")
    api_key = config.get("OPENAI_API_KEY") or settings_cfg.get("openai.key") or settings_cfg.get("openai_key")
    headers = build_headers(
        api_key=api_key,
        user_id=settings_cfg.get("openai.user_id"),
        custom_headers=custom_headers if isinstance(custom_headers, dict) else {},
        extra_headers_json=extra,
        send_auth=bool(config.get("OPENAI_SEND_AUTH")),
    )
    if config.get("OPENAI_ORG_ID"):
        headers["OpenAI-Organization"] = str(config["OPENAI_ORG_ID"])

    proxies: dict[str, str] = {}
    if config.get("HTTP_PROXY"):
        proxies["http"] = config["HTTP_PROXY"]
    if config.get("HTTPS_PROXY"):
        proxies["https"] = config["HTTPS_PROXY"]

    model = config.get("OPENAI_MODEL", settings_cfg.get("model", ""))
    max_tokens = int(config.get("MAX_TOKENS", settings_cfg.get("max_model_tokens", 2048)))
    temperature = float(config.get("TEMPERATURE", 1.0))
    top_p = float(config.get("TOP_P", 1.0))
    reasoning_effort = "low"
    verbosity = "low"
    seed = config.get("SEED")

    def _call(system_prompt: str, user_prompt: str) -> str:
        payload = build_chat_payload(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
            max_tokens=max_tokens,
            temperature=None,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            seed=seed if isinstance(seed, int) else None,
        )
        proxies = {}
        if config.get("HTTP_PROXY"):
            proxies["http"] = config["HTTP_PROXY"]
        if config.get("HTTPS_PROXY"):
            proxies["https"] = config["HTTPS_PROXY"]
        data = post_chat_requests(
            url,
            headers,
            payload,
            timeout=int(timeout),
            verify_ssl=verify,
            proxies=proxies or None,
        )
        return data["choices"][0]["message"]["content"]

    return _call


# ============================================================================
# LLMシステムプロンプト（仕様書 Section 3-6 準拠）
# ============================================================================

_SYSTEM_PROMPT = """\
あなたはデータベース設計の専門家です。
画面項目名とドメイン定義の対応付けを行います。

■ 判定の大前提（仕様書 Section 3）
- 型・桁が一致しない候補は既に除外済みです（型桁一致は必須条件）
- あなたが判断するのは「名前の意味的一致」のみです
- 判定結果は全て「候補提案」です。最終確定は人間が行います

■ 判断に使える情報
提供される情報を総合的に判断してください:
1. 大分類（文字列系/数値系/日付系/コード系等）
2. テキストタイプ（半角英字/全角文字等 -- 画面項目定義のみ）
3. 桁数照合の詳細（文字数一致/バイト長一致/整数部桁数等）
4. 同義語辞書のヒット状況
5. 外部コードの一致状況
6. 部分一致スコア（接頭辞・接尾辞の共通部分率）
7. 名前類似度スコア

■ 特殊パターン（自動割当禁止 -> 人間選択方式）
以下のパターンは自動でドメインを確定せず、選択肢を提示して人間に選ばせること。

1. フラグ系（フラグ / FLG / flag）:
   - 同じ型桁でも業務的意味が異なるフラグが多数存在する
   - -> 候補を全て列挙し、人間に選択させる
   - 出力: "match_type": "human_choice", "candidates": [候補リスト]

2. コメント・補記系（コメント / 補記 / 備考 / 注記 / メモ）:
   - 改行の有無でドメインが異なる可能性がある
   - -> 改行有無の確認を促し、候補を提示して人間に選択させる
   - 出力: "match_type": "human_choice", "check_point": "改行有無を確認"

■ 注意
- 末尾数字は既に除去済み（例: 顧客名1 -> 顧客名）
- 同じデータ型・桁数でも、意味が異なれば別ドメイン
- "exact" は使用禁止。必ず "suggested" / "human_choice" / "no_match" のいずれか
- ドメイン一覧に適切な候補がない場合は "new_domain" を返して新規候補名を提案すること
"""

# ============================================================================
# バッチLLM処理
# ============================================================================


def _run_batch_llm(
    targets: list[tuple[int, MatchEvidence]],
    results: list[MatchResult | None],
    llm_call: LlmCallFn,
) -> None:
    """バッチプロンプトでLLMを呼び出し、結果を results に書き込む。"""
    target_evidences = [ev for _, ev in targets]
    prompt = _build_batch_prompt(target_evidences)

    try:
        raw_response = llm_call(_SYSTEM_PROMPT, prompt)
        parsed = _parse_llm_response(raw_response)
    except Exception:
        logger.exception("LLM呼び出しに失敗 -- フォールバック判定に切り替え")
        for idx, ev in targets:
            results[idx] = _fallback_from_evidence(ev)
        return

    # パース結果を index で突合
    parsed_by_index = {item.get("index"): item for item in parsed}

    for seq, (idx, ev) in enumerate(targets, 1):
        llm_item = parsed_by_index.get(seq)
        if llm_item is not None:
            results[idx] = _llm_response_to_result(ev, llm_item)
        else:
            logger.warning(
                "LLM応答に index=%d が見つからない（項目: %s）-- フォールバック",
                seq, ev.item_name,
            )
            results[idx] = _fallback_from_evidence(ev)


# ============================================================================
# プロンプト構築
# ============================================================================


def _build_batch_prompt(evidences: list[MatchEvidence]) -> str:
    """複数件をまとめた効率的なバッチプロンプトを構築する。

    仕様書準拠で以下の情報を含める:
    - 大分類（data_type）
    - 型桁一致候補（ドメイン名＋類似度）
    - 同義語ヒット
    - 部分一致スコア
    - 桁数照合の詳細
    - 外部コード一致状況
    """
    items_section: list[str] = []

    for i, ev in enumerate(evidences, 1):
        lines = [
            f"[{i}] 項目名: {ev.item_name}（数字除去済み）",
            f"    大分類: {ev.data_type or '不明'}",
            f"    桁数: {ev.digits or '不明'}",
        ]

        # 型桁一致候補（list[dict] から展開）
        candidates = ev.type_digits_matches
        if candidates:
            candidate_parts: list[str] = []
            for c in candidates:
                name = c.get("domain_name", "?")
                sim = c.get("name_similarity", 0)
                syn_flag = " [同義語HIT]" if c.get("has_synonym_hit") else ""
                digit = c.get("digit_match_rate")
                digit_text = f" / 桁一致率{digit:.0%}" if isinstance(digit, (int, float)) else ""
                candidate_parts.append(f"{name}（類似度{sim:.0%}{digit_text}{syn_flag}）")
            lines.append(f"    型桁一致候補: {', '.join(candidate_parts)}")
        else:
            lines.append("    型桁一致候補: なし")

        # 同義語ヒット詳細
        if ev.synonym_hits:
            syn_details = [
                f"{domain}: {', '.join(syns)}"
                for domain, syns in ev.synonym_hits.items()
            ]
            lines.append(f"    同義語ヒット: {'; '.join(syn_details)}")

        # 桁数照合の詳細（detail_matches から抽出）
        detail_summary = _summarize_detail_matches(ev.detail_matches)
        if detail_summary:
            lines.append(f"    桁数照合: {detail_summary}")

        # 部分一致スコア（上位3件）
        if ev.partial_match_scores:
            top_partials = sorted(
                ev.partial_match_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            partial_text = ", ".join(
                f"{name}({score:.0%})" for name, score in top_partials
            )
            lines.append(f"    部分一致: {partial_text}")

        items_section.append("\n".join(lines))

    items_text = "\n\n".join(items_section)

    return f"""\
以下の{len(evidences)}件の項目について、最適なドメインを判定してください。
**各項目は1件ずつ丁寧に判断**し、拙速に結論を出さないでください。

前提条件:
- 型（大分類）が不一致の候補は既に除外済み
- 項目名の末尾数字は除去済み（顧客名1 -> 顧客名）
- 候補は最大20件まで提示される
- 判定結果は全て「候補提案」（最終確定は人間が行う）

判断基準:
- **日本語の意味比較と桁一致率を同じ重要度**で評価する（文字列類似度は参考情報）
- **データ型（大分類）一致は前提条件**として扱う
- 意味が一致しており、**桁一致率も十分に高い**（目安: 0.80以上）場合は候補を提案（suggested）
- 意味が合っていても桁一致率が低い、または桁一致率は高いが意味が合わない場合は新規ドメイン提案（new_domain）

追加要件:
- **和名が大きく異なっていても、意味が近く、データ型/桁数が一致する既存ドメインがある場合は**
  new_domain を選ぶ際に "generalized_candidates" に既存ドメイン名を列挙する。

特殊パターン（自動割当禁止 -> 人間選択方式）:
- フラグ系（フラグ/FLG/flag）-> 候補を全て列挙し human_choice
- コメント/補記系（コメント/補記/備考/注記/メモ）-> 改行有無の確認を促し human_choice

{items_text}

各項目に対して以下のJSON配列で回答してください。
理由（reason）には **意味の一致根拠** と **桁一致率の評価** の両方を必ず書いてください。

通常: {{"index": N, "match_type": "suggested", "domain": "名前", "confidence": 0.0-1.0, "reason": "意味: ... / 桁: ..."}}
新規: {{"index": N, "match_type": "new_domain", "domain": "新規候補名", "confidence": 0.0-1.0, "reason": "意味: ... / 桁: ...", "generalized_candidates": ["既存候補...", "..."]}}
フラグ系: {{"index": N, "match_type": "human_choice", "candidates": ["候補..."], "reason": "フラグ系"}}
コメント系: {{"index": N, "match_type": "human_choice", "check_point": "改行有無を確認", "candidates": ["候補..."], "reason": "改行有無"}}
該当なし: {{"index": N, "match_type": "no_match", "reason": "理由"}}

JSON配列以外出力禁止。
"""


# ============================================================================
# LLM応答パーサー
# ============================================================================

_CODE_BLOCK_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
    re.DOTALL,
)

_GROUP_SYSTEM_PROMPT = """\
あなたはデータベース設計の専門家です。
新規ドメイン提案の中から、意味が近いものをグルーピングします。
"""


def _parse_llm_response(response: str) -> list[dict[str, Any]]:
    """LLMの応答JSONをパースする。

    マークダウンコードブロック（```json ... ```）にも対応する。
    match_type のバリデーションを行い、不正な値はログ警告を出す。

    Returns:
        パース結果の辞書リスト。パース失敗時は空リスト。
    """
    text = response.strip()

    # マークダウンコードブロックを除去
    code_match = _CODE_BLOCK_RE.search(text)
    if code_match:
        text = code_match.group(1).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("LLM応答のJSONパースに失敗: %.200s", text)
        return []

    items = parsed if isinstance(parsed, list) else [parsed]

    # バリデーション: match_type の値チェック
    validated: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        match_type = item.get("match_type", "")
        if match_type not in _VALID_LLM_MATCH_TYPES:
            logger.warning(
                "LLMが不正な match_type を返却: '%s'（項目 index=%s）"
                " -- 'suggested' に強制変換",
                match_type, item.get("index"),
            )
            item["match_type"] = "suggested"
        validated.append(item)

    return validated


def _extract_json(text: str) -> Any:
    raw = text.strip()
    code_match = _CODE_BLOCK_RE.search(raw)
    if code_match:
        raw = code_match.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _build_new_domain_group_prompt(items: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        "以下の新規提案候補について、日本語の意味が近いものをグルーピングしてください。",
        "条件: データ型と桁定義が一致するもの同士のみグループ化する。",
        "出力は JSON 配列で、各要素は {\"group\": [index,...], \"reason\": \"...\"} とする。",
        "index は 1 始まり。1件だけのグループは出力しない。",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines.append(
            f"[{i}] name={item.get('name','')}, data_type={item.get('data_type','')}, digits={item.get('digits','')}"
        )
    return "\n".join(lines)


def group_new_domain_proposals(
    items: list[dict[str, Any]],
    llm_call: LlmCallFn | None,
) -> list[dict[str, Any]]:
    """新規提案の汎化候補をLLMでグルーピングする。"""
    if not items or llm_call is None:
        return []
    prompt = _build_new_domain_group_prompt(items)
    try:
        response = llm_call(_GROUP_SYSTEM_PROMPT, prompt)
    except Exception:
        return []
    parsed = _extract_json(response)
    if not isinstance(parsed, list):
        return []
    valid_groups: list[dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        group = item.get("group")
        if not isinstance(group, list) or len(group) <= 1:
            continue
        # index validation
        if not all(isinstance(i, int) and 1 <= i <= len(items) for i in group):
            continue
        valid_groups.append(item)
    return valid_groups


# ============================================================================
# 結果変換
# ============================================================================


def _llm_response_to_result(
    ev: MatchEvidence, llm_item: dict[str, Any],
) -> MatchResult:
    """LLMの応答1件を MatchResult に変換する。

    自動確定禁止: match_type が "exact" の場合は "suggested" に強制変換。
    """
    match_type = llm_item.get("match_type", "no_match")
    if match_type not in _VALID_LLM_MATCH_TYPES:
        match_type = "suggested"

    return MatchResult(
        item_name=ev.item_name,
        match_type=match_type,
        suggested_domain=llm_item.get("domain", ""),
        candidates=llm_item.get("candidates"),
        check_point=llm_item.get("check_point", ""),
        confidence=float(llm_item.get("confidence", 0.0)),
        reason=llm_item.get("reason", ""),
        generalized_candidates=llm_item.get("generalized_candidates"),
    )


def _resolved_evidence_to_result(ev: MatchEvidence) -> MatchResult:
    """C方式で確定済みの evidence を MatchResult に変換する。"""
    return MatchResult(
        item_name=ev.item_name,
        match_type=ev.match_type,
        suggested_domain=ev.resolved_domain or "",
        confidence=1.0 if ev.match_type == "exact" else 0.95,
        reason=ev.reason,
        generalized_candidates=None,
    )


def _fallback_from_evidence(ev: MatchEvidence) -> MatchResult:
    """LLM未使用時、C方式の証拠からフォールバック判定を行う。

    型桁一致候補の中から最有力候補を選び「suggested」として返す。
    候補がなければ「no_match」。
    """
    best_domain, confidence, reason = _pick_best_candidate(ev)

    if not best_domain:
        return MatchResult(
            item_name=ev.item_name,
            match_type="no_match",
            confidence=0.0,
            reason=f"型桁一致候補なし。{ev.reason}",
            generalized_candidates=None,
        )

    return MatchResult(
        item_name=ev.item_name,
        match_type="suggested",
        suggested_domain=best_domain,
        confidence=confidence,
        reason=reason,
        generalized_candidates=None,
    )


# ============================================================================
# 内部ヘルパー
# ============================================================================


def _pick_best_candidate(
    ev: MatchEvidence,
) -> tuple[str, float, str]:
    """C方式の収集情報から最有力候補を選出する。

    同義語ヒットがあればそれを優先し、なければ名前類似度で選ぶ。

    Returns:
        (ドメイン名, 信頼度, 判定理由) のタプル。候補なしの場合は ("", 0.0, "")。
    """
    candidates = ev.type_digits_matches
    if not candidates:
        return ("", 0.0, "")

    # 同義語ヒットのある候補を優先
    synonym_domains = set(ev.synonym_hits.keys()) if ev.synonym_hits else set()
    syn_candidates = [
        c for c in candidates if c.get("domain_name") in synonym_domains
    ]

    if syn_candidates:
        best = syn_candidates[0]
        domain_name = best.get("domain_name", "")
        sim = best.get("name_similarity", 0.0)
        hit_syns = ev.synonym_hits.get(domain_name, [])
        return (
            domain_name,
            max(sim, 0.6),
            f"同義語ヒット（{', '.join(hit_syns)}）+ 類似度{sim:.0%}",
        )

    # 名前類似度が最も高い候補を選択（candidates は類似度降順にソート済み）
    best = candidates[0]
    domain_name = best.get("domain_name", "")
    sim = best.get("name_similarity", 0.0)
    return (
        domain_name,
        sim,
        f"名前類似度{sim:.0%}（C方式フォールバック）",
    )


def _summarize_detail_matches(details: dict) -> str:
    """detail_matches の照合結果を人間可読なサマリ文字列に変換する。"""
    if not details:
        return ""

    parts: list[str] = []

    _LABELS = {
        "string_max_chars_match": "最大文字数",
        "string_max_bytes_match": "最大バイト長",
        "string_length_match": "文字列長",
        "numeric_integer_digits_match": "整数部桁数",
        "numeric_decimal_digits_match": "小数部桁数",
        "numeric_min_max_match": "数値範囲",
        "external_code_match": "外部コード",
    }

    for key, label in _LABELS.items():
        val = details.get(key)
        if val is True:
            parts.append(f"{label}=一致")
        elif val is False:
            parts.append(f"{label}=不一致")

    return ", ".join(parts) if parts else ""
