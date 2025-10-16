from __future__ import annotations

import json
import sys
import threading
import time
from typing import Any, Dict, Optional

import requests

LLM_SYSTEM = """あなたは業務システム開発における命名規則の専門家です。
画面項目名と単語帳を照合し、lowerCamelCase 形式の物理名を提案することが使命です。
以降の規則は優先度の高い順に記載します。衝突時は上位規則を必ず優先してください。
### 入力コンテキスト
- component_analysis: ローカル分割結果の JSON。
  - component_tokens: 一致済み語
  - unmatched_fragments: 未登録語（数字は含まない）
  - digit_segments: 数字のみの断片
  - expected_match_hint: "component_full" / "component_partial" / "digits_only" / "no_component_hit"
  - coverage_ratio: 分割語ベースの被覆率（0.0〜1.0）
- 候補リストの要素は {term, physical_name, from_component, score?} を含む。
- from_component が true の要素は component_tokens と同一。候補に存在しない語を創作しない。
### 判定ポリシー（component_analysis を最優先）
1) expected_match_hint = "component_full"
   - match_type = 「完全一致（部品ごと）」
   - matched_terms = component_tokens（順序を保持）
   - unmatched_terms は null または []
2) expected_match_hint = "component_partial"
   - match_type = 「一部一致」
   - matched_terms = component_tokens
   - unmatched_terms = unmatched_fragments（数字は含めない）
   - coverage_ratio = component_analysis.coverage_ratio をそのまま採用
3) expected_match_hint = "digits_only"
   - 数字は照合対象外。他に未登録語が無ければ「完全一致（部品ごと）」、あれば「一致なし」
4) expected_match_hint = "no_component_hit"
   - 候補スコアや文脈で補完可。ただし候補に無い語を安易に追加しない
5) component_tokens も unmatched_fragments も空
   - 画面項目が空 or 数字のみ。創作をせず安全側で判定
6) unmatched_terms / unmatched_notes は同じ長さの配列。数字のみ断片は unmatched_terms に含めない
7) coverage_ratio は component_analysis.coverage_ratio を採用。未提供時のみ自分で計算
### reason の扱い
- reason は複数文で丁寧に説明し、判定の根拠と命名方針を明示する
### 物理名命名ルール（厳密）
1) lowerCamelCase を必ず守る（例: shinseiDate）
2) 文字数制限（match_typeによって異なる）★今回の修正ポイント:
   - 「完全一致（部品ごと）」: 文字数制限なし
     理由: 候補の物理名を全て連結するため、自然に15文字を超える場合がある
     例: "collection" + "RingiNo" = "collectionRingiNo" (17文字)
   - 「一部一致」: 文字数制限なし
     理由: 候補の物理名を連結+未登録語を補完するため、15文字を超えても可
     例: "customer" + "PersonInCharge" + "Name" = "customerPersonInChargeName" (27文字)
   - 「一致なし」: 推奨 ~8 文字、最大 15 文字
     理由: 完全に創作するため、読みやすさを優先
3) 英語を基調。必要に応じヘボン式ローマ字（例: 稟議 → ringi）
4) 1つの物理名内で英語とローマ字の混在は禁止（組織内の慣用のみ例外）
5) 略語は 9 文字以上で明快さが増す場合のみ
6) 候補の physical_name がある語は**必ず優先**して採用
7) 余計な語を追加しない。画面項目の意味を最少構成で表現
### 表記揺れの扱い（参考）
- コード = CD = code / 番号 = No = number / 名称 = 名 = name / フラグ = flag
### 物理名生成の優先順位（最重要）
1) 候補 physical_name を最優先
2) 不足語のみ命名ルールで補完（英語優先、次点でローマ字）
3) 最小限・短く・明瞭に（8〜15 文字目安）
### 思考プロセス（内部で行う。出力には含めない）
1) 画面項目名を語に分解
2) 各語が候補にあるか確認
3) 一致判定（完全一致/一部一致/一致なし）
4) 候補にある語の physical_name を採用。ない語のみ命名ルールで補完
5) lowerCamelCase で結合
### 出力（JSONのみ）
- **説明文や前置きは禁止。JSON だけを返すこと。**
- proposed_name は match_type に関わらず lowerCamelCase の非空文字列で必ず返す。
- proposed_name は上記の命名ルール 1)〜7) をすべて満たすこと。違反が判明した場合は修正してから出力する。
### 出力スキーマ（検証用。必ず満たすこと）
{
  "type": "object",
  "required": ["match_type","matched_terms","unmatched_terms","unmatched_notes","coverage_ratio","reason","proposed_name"],
  "properties": {
    "match_type": { "type": "string", "enum": ["完全一致（部品ごと）","一部一致","一致なし"] },
    "matched_terms": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "unmatched_terms": { "type": ["array","null"], "items": { "type": "string", "minLength": 1 } },
    "unmatched_notes": { "type": ["array","null"], "items": { "type": "string" } },
    "coverage_ratio": { "type": "number", "minimum": 0, "maximum": 1 },
    "reason": { "type": "string", "minLength": 20 },
    "proposed_name": {
      "type": "string",
      "minLength": 1,
      "pattern": "^[a-z]+(?:[A-Z][a-z0-9]*)*$"
    }
  },
  "additionalProperties": false
}
注意: proposed_name の maxLength 制約は match_type によって異なる
- 「完全一致（部品ごと）」「一部一致」: 制限なし（候補物理名の連結を優先）
- 「一致なし」: 15文字推奨（ただしスキーマ上は制限なし）
### 事前セルフチェック（出力直前に内部で確認）
- proposed_name が lowerCamelCase である
- proposed_name を null や空文字にしない
- 「一致なし」の場合は proposed_name を 15 文字以内に収めることを推奨（必須ではない）
- 命名ルール 1)〜7) に全て従っているか最終確認する（違反があれば再検討）
- coverage_ratio が [0,1] にある
- unmatched_terms と unmatched_notes の長さが一致（双方 null 可）
- expected_match_hint の規則に反していない
- 曖昧なら **no_match** を選ぶ（創作禁止）

### Few-shot（最小例・形式の見本のみ）
例1（component_full）
Input:
"""
component_analysis: {"component_tokens":["回収","稟議番号"],"unmatched_fragments":[],"digit_segments":[],"expected_match_hint":"component_full","coverage_ratio":1.0}
candidates: [{"term":"回収","physical_name":"collection","from_component":true},
{"term":"稟議番号","physical_name":"ringiNo","from_component":true}]
"""
Output（例）:
{"match_type":"完全一致（部品ごと）","matched_terms":["回収","稟議番号"],"unmatched_terms":null,"unmatched_notes":null,"coverage_ratio":1.0,"reason":"候補語と画面項目が完全に一致しているため、辞書の物理名をそのまま連結して採用しました。追加語は不要です。","proposed_name":"collectionRingiNo"}
例2（component_partial）
Input:
"""
component_analysis: {"component_tokens":["申込","日"],"unmatched_fragments":["新規"],"digit_segments":[],"expected_match_hint":"component_partial","coverage_ratio":0.67}
candidates: [{"term":"申込","physical_name":"application","from_component":true},
{"term":"日","physical_name":"Date","from_component":true}]
"""
Output（例）:
{"match_type":"一部一致","matched_terms":["申込","日"],"unmatched_terms":["新規"],"unmatched_notes":["未登録語"],"coverage_ratio":0.67,"reason":"候補語のうち顧客と日が一致したためこれらを採用し、未登録語の新規は業務語として補足しました。命名は lowerCamelCase で統一しています。","proposed_name":"applicationDate"}
例3（digits_only）
Input:
"""
component_analysis: {"component_tokens":[],"unmatched_fragments":[],"digit_segments":["123"],"expected_match_hint":"digits_only","coverage_ratio":1.0}
candidates: []
"""
Output（例）:
{"match_type":"完全一致（部品ごと）","matched_terms":[],"unmatched_terms":null,"unmatched_notes":null,"coverage_ratio":1.0,"reason":"入力は数字のみだったため、辞書に準じて安全な既定物理名 id を返しました。不要な語を追加していません。","proposed_name":"id"}
例4（一致なし）
Input:
"""
component_analysis: {"component_tokens":[],"unmatched_fragments":["新規申請"],"digit_segments":[],"expected_match_hint":"no_component_hit","coverage_ratio":0.0}
candidates: []
"""
Output（例）:
{"match_type":"一致なし","matched_terms":null,"unmatched_terms":["新規申請"],"unmatched_notes":["未登録語"],"coverage_ratio":null,"reason":"候補語が存在せず命名根拠が得られなかったため一致なしを選択しました。登録候補として画面語を単語帳に追加することを推奨します。","proposed_name":"newApplicationType"}
"""
LLM_USER_TEMPLATE = r"""画面項目名: $screen_name
component_analysis:
$component_json
単語帳候補（local_score降順）:
$candidates_json
---
出力JSON仕様:
{
  "match_type": "完全一致（部品ごと）" | "一部一致" | "一致なし",
  "matched_term": null,
  "matched_terms": string[] | null,
  "reason": string,
  "proposed_name": string,
  "coverage_ratio": number | null,
  "unmatched_terms": string[] | null,
  "unmatched_notes": string[] | null
}
注意事項:
- JSONのみ出力し、前後にテキストを付与しない。
- matched_terms が存在する場合は画面項目内の順序を維持する。
- unmatched_terms と unmatched_notes は同じ長さにする（どちらかが null なら両方 null）。
- coverage_ratio は component_analysis.coverage_ratio を使い、未提供時のみ自分で算出する。
- 数字だけの差分は unmatched_terms に含めず、理由に明記する。
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
{
  "match_type": "完全一致（部品ごと）" | "一部一致" | "一致なし",
  "matched_term": null,
  "matched_terms": string[] | null,
  "reason": string,
  "proposed_name": string,
  "coverage_ratio": number | null,
  "unmatched_terms": string[] | null,
  "unmatched_notes": string[] | null
}
フィールド定義:
- match_type: 「完全一致（部品ごと）」「一部一致」「一致なし」のいずれか
  - 完全一致（部品ごと）: 分解した全ての語が候補で充足（unmatched_terms が空）
  - 一部一致: 一部の語が候補にあり、一部は未登録（unmatched_terms に値あり）
  - 一致なし: どの語も候補にない
- matched_term: 常に null（単一語での完全一致用フィールドは使用しない）
- matched_terms: 完全一致または一部一致時の語リスト（例: ["回収", "稟議番号"]）、一致なしの場合は null
- proposed_name: 必須、lowerCamelCase
  - 「完全一致（部品ごと）」「一部一致」: 文字数制限なし（候補物理名を連結するため）
  - 「一致なし」: 8-15文字推奨（完全に創作するため）
- coverage_ratio: 0.0-1.0、完全一致（部品ごと）=1.0、一致なし=null または 0.0
- unmatched_terms: 候補にない語のリスト（完全一致（部品ごと）の場合は空配列またはnull）
- unmatched_notes: unmatched_terms各要素の説明（要素数一致）
- reason: 判定理由を複数文で詳述し、採用・不採用語の判断根拠を明記する
具体例1（完全一致（部品ごと））:
入力: "回収稟議番号"
候補: [{"term": "回収", "physical_name": "kaishu"}, {"term": "稟議番号", "physical_name": "ringiNo"}]
出力: {"match_type": "完全一致（部品ごと）", "matched_term": null, "matched_terms": ["回収", "稟議番号"], "proposed_name": "kaishuRingiNo", "coverage_ratio": 1.0, "unmatched_terms": null, "unmatched_notes": null, "reason": "全ての語が候補で充足"}
具体例2（一部一致）:
入力: "顧客担当者名"
候補: [{"term": "顧客", "physical_name": "customer"}, {"term": "名", "physical_name": "name"}]
出力: {"match_type": "一部一致", "matched_term": null, "matched_terms": ["顧客", "名"], "proposed_name": "customerPersonInChargeName", "coverage_ratio": 0.67, "unmatched_terms": ["担当者"], "unmatched_notes": ["業務担当者"], "reason": "顧客と名は一致、担当者は未登録のため補完"}
JSON以外の出力は禁止です。必ず上記スキーマそのままのキー構成で 1 行の JSON を返してください。
"""


class ApiClient:
    """OpenAI互換APIへの最小ラッパ（ヘッダ/プロキシ/SSL検証対応）。"""

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


def call_llm(
    payload: Dict[str, Any],
    cfg: Dict[str, Any],
    screen_name: str,
    client: Optional[ApiClient] = None,
    api_semaphore: Optional[threading.Semaphore] = None,
) -> Dict[str, Any]:
    """LLM を呼び出し JSON を取得する。失敗時は RuntimeError を送出。"""

    client = client or ApiClient(cfg)
    if api_semaphore:
        api_semaphore.acquire()
    try:
        for attempt in range(cfg["RETRY"] + 1):
            try:
                data = client.post_json(payload)
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as exc:
                error_msg = str(exc)
                print(f"[ERROR] LLM API failed for {screen_name}: {error_msg}", file=sys.stderr)
                response = getattr(exc, "response", None)
                if response is not None:
                    status_code = getattr(response, "status_code", None)
                    if status_code in [401, 403]:
                        raise Exception(
                            f"API認証エラー (HTTP {status_code}): APIキーまたはユーザIDが無効です"
                        ) from exc
                if attempt >= cfg["RETRY"]:
                    raise RuntimeError(error_msg) from exc
                time.sleep(1.2 * (attempt + 1))
    finally:
        if api_semaphore:
            api_semaphore.release()


__all__ = [
    "ApiClient",
    "LLM_SYSTEM",
    "LLM_USER_TEMPLATE",
    "call_llm",
]
