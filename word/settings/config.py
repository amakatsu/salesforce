#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""設定とプロンプトの定義"""

import os
from typing import Any, Dict, Optional

# ====== 定数 ==================================================================

# 「事実上の完全一致」と見なすスコア（difflibは1.0に非常に近づく）
HARD_EXACT_SCORE = 1.0  # 完全一致のみに限定
# LLMフォールバック時に"完全一致"扱いにする安全側の下限
FALLBACK_EXACT_FLOOR = 0.95

# ====== 設定（.envで上書き可） ===============================================

DEFAULT_CONFIG: Dict[str, Any] = {
    # --- API（OpenAI互換）
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://170.49.125.91:53000/api/curl/v1/chat/"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "OPENAI_PATH": os.getenv("OPENAI_PATH", "/chat/completions"),
    "OPENAI_HEADERS_JSON": os.getenv("OPENAI_HEADERS_JSON", "{\"api-key\":\"QXwXLlZijq1U8WwiYfIu3znm3wWK3qIG\",\"apim-user-id\":\"PIT03077\"}"),
    "OPENAI_SEND_AUTH": os.getenv("OPENAI_SEND_AUTH", "false").lower() != "false",
    "OPENAI_ORG_ID": os.getenv("OPENAI_ORG_ID", ""),
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
    "VERIFY_SSL": os.getenv("VERIFY_SSL", "true").lower() != "false",
    # --- 生成パラメタ
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "800")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.3")),  # 精度向上のため0.7→0.3に下げて決定的な出力を促す
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
    "VOCAB_PHYS_COL": os.getenv("VOCAB_PHYS_COL", "物理名（正式名称）,物理名"),
    "VOCAB_PHYS_ABBR_COL": os.getenv("VOCAB_PHYS_ABBR_COL", "物理名（略称）"),
    "VOCAB_NO_COL": os.getenv("VOCAB_NO_COL", "No,#"),
    # --- 類似度設定
    "FUZZY_THRESHOLD": float(os.getenv("FUZZY_THRESHOLD", "0.68")),  # 候補プールの下限（精度向上のため0.72→0.68に下げてより多くの候補を拾う）
    "TOP_K": int(os.getenv("TOP_K", "5")),  # 直接候補の上位件数（精度向上のため3→5に増加）

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

# ====== Excel I/O 設定 ========================================================

HEADER_DETECT = os.getenv("HEADER_DETECT", "true").lower() != "false"
HEADER_SCAN_ROWS = int(os.getenv("HEADER_SCAN_ROWS", "30"))


def _int_env(name: str) -> Optional[int]:
    """環境変数を整数に変換（存在しない場合はNone）"""
    v = os.getenv(name, "")
    try:
        return int(v) if v else None
    except Exception:
        return None


SCREEN_HEADER_ROW = _int_env("SCREEN_HEADER_ROW")
VOCAB_HEADER_ROW = _int_env("VOCAB_HEADER_ROW")

# ====== LLMプロンプト ==========================================================

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
   - ★重要: 一部一致判定時の注意点
     * 候補の意味的コンテキストを必ず考慮すること
     * **より長い文字列で一致する候補がある場合、必ずそちらを優先すること（最長一致の原則）**
     * 例: 「重要度」→「重要」(2文字一致) vs 「要」(1文字一致) → 「重要」を優先
     * 例: 「有無フラグ」→「有無」(2文字一致) vs 「有」(1文字一致) or 「無」(1文字一致) → 「有無」を優先
     * 例: 「担当者名」→「担当者」(3文字一致) vs 「担当」(2文字一致) → 「担当者」を優先
     * 例: 「顧客番号」→「顧客番号」(4文字一致) vs 「顧客」(2文字一致) + 「番号」(2文字一致) → 「顧客番号」を優先
     * 部分文字列一致だけでなく、業務的な意味の整合性を確認すること
     * 最長一致の原則: 常に最も長く一致する候補を選択すること
3) expected_match_hint = "digits_only"
   - 数字は照合対象外（unmatched_termsに含めない）
   - 数字以外の部分が全て一致していれば「完全一致（部品ごと）」
   - 例: 「顧客コード1」→「顧客コード」が一致 → 「完全一致（部品ごと）」、proposed_name=「customerCode1」
   - 数字は物理名に必ず含めるが、一致判定には影響しない
4) expected_match_hint = "no_component_hit"
   - ComponentMatcherで一致なし。候補リストから文字列として完全に含まれるものを探す
   - 判定基準: 画面項目名を分解したとき、候補の論理名が **文字列として完全一致** する部分があるか
   - 例: 「顧客担当者名」→「顧客」「担当者」「名」のように分割でき、各部分が候補に存在すれば「一部一致」
   - 例: 「重要度」→「重要」は文字列として含まれるが、「要」は部分一致なので不適切
   - 例: 「有無フラグ」→「有無」は文字列として完全一致するが、「有」「無」への分割は不適切（意味が異なる）
   - スコアは参考程度。文字列の完全一致性を最優先すること
   - 曖昧な場合や、文字列として完全に分割できない場合は「一致なし」を選ぶ
5) component_tokens も unmatched_fragments も空
   - 画面項目が空 or 数字のみ。創作をせず安全側で判定
6) unmatched_terms / unmatched_notes は同じ長さの配列。数字のみ断片は unmatched_terms に含めない
7) coverage_ratio は component_analysis.coverage_ratio を採用。未提供時のみ自分で計算
8) ★重要: 略称の優先
   - 候補に略称（_phys_abbr）が存在する場合は、必ず略称を優先して使用
   - 略称がない場合のみ、正式名称（_phys）を使用
### 物理名命名ルール（厳密）
1) lowerCamelCase を必ず守る（例: shinseiDate）
2) 文字数制限（match_typeによって異なる）:
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
6) ★重要: 候補の physical_name がある語の優先順位
   - 略称（_phys_abbr）が存在する場合は、必ず略称を優先して使用
   - 略称がない場合は、正式名称（_phys）を使用
   - 候補にある語の physical_name は**必ず優先**して採用
7) ★重要: 数字の扱い
   - 論理名に数字が含まれている場合、物理名にも必ず数字を含める
   - 数字は物理名の適切な位置に配置する（例: 「顧客コード1」→「customerCode1」）
   - 数字間のハイフン（-）は「and」に置き換える（例: 「1-1」→「1and1」、「項目2-3」→「item2and3」）
   - ただし、数字は一致判定の対象外（候補の不足判定unmatched_termsには含めない）
   - 数字以外の部分が全て一致していれば「完全一致（部品ごと）」として扱う
8) 余計な語を追加しない。画面項目の意味を最少構成で表現
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
### reason フィールドの記述ルール（最重要）
reason フィールドには、以下の内容を丁寧に、分かりやすく記述すること：

1) **一致した語の説明**（完全一致・一部一致の場合）
   - どの語が単語帳に登録されていたか
   - それぞれの語に対応する物理名は何か

2) **未登録語の物理名提案とその理由**（一部一致・一致なしの場合）
   - 未登録語に対してどのような物理名を提案したか
   - なぜその物理名を選んだのか（英語/ローマ字の選択理由、業務的な意味など）
   - 例: 「「担当者」は未登録のため「personInCharge」を提案しました。業務上、人を表す語には英語の person を使用し、担当の意味を明確にするため InCharge を付加しました」

3) **数字の扱い**（数字が含まれる場合）
   - 数字部分はどう扱ったか

4) **注意事項**（必要な場合）
   - 単語帳への追加を推奨する語があればその理由

**重要**: reasonフィールドにタグ（[component_full]など）は不要です。自然な日本語で、分かりやすく記述してください。

### unmatched_notes フィールドの記述ルール
unmatched_notes フィールドには、unmatched_terms の各要素について以下を記述：
- その語に対してどのような物理名を提案したか
- なぜその物理名を選んだのか（業務的な意味、英語/ローマ字の選択理由など）
- 例: 「業務担当者を表す英語表現として personInCharge を採用。person で人を表し、inCharge で担当の意味を明確化」

### 出力スキーマ（検証用。必ず満たすこと）
{
  "type": "object",
  "required": ["match_type","matched_terms","unmatched_terms","unmatched_notes","coverage_ratio","reason","proposed_name"],
  "properties": {
    "match_type": { "type": "string", "enum": ["完全一致（部品ごと）","一部一致","一致なし"] },
    "matched_terms": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "unmatched_terms": { "type": ["array","null"], "items": { "type": "string", "minLength": 1 } },
    "unmatched_notes": { "type": ["array","null"], "items": { "type": "string", "minLength": 10 } },
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
- reason は分かりやすく丁寧に記述されているか（タグなし、20文字以上）
- unmatched_notes は各要素が丁寧に記述されているか（10文字以上）
- coverage_ratio が [0,1] にある
- unmatched_terms と unmatched_notes の長さが一致（双方 null 可）
- expected_match_hint の規則に反していない
- 候補との意味的整合性を確認したか（部分文字列一致だけで判断していないか）
- 曖昧なら **no_match** を選ぶ（創作禁止）

### Few-shot（形式の見本）
例1（完全一致・部品ごと）
Input:
\"\"\"
component_analysis: {\"component_tokens\":[\"回収\",\"稟議番号\"],\"unmatched_fragments\":[],\"digit_segments\":[],\"expected_match_hint\":\"component_full\",\"coverage_ratio\":1.0}
candidates: [{\"term\":\"回収\",\"physical_name\":\"collection\",\"from_component\":true},
{\"term\":\"稟議番号\",\"physical_name\":\"ringiNo\",\"from_component\":true}]
\"\"\"
Output:
{\"match_type\":\"完全一致（部品ごと）\",\"matched_terms\":[\"回収\",\"稟議番号\"],\"unmatched_terms\":null,\"unmatched_notes\":null,\"coverage_ratio\":1.0,\"reason\":\"「回収」は単語帳に登録されており物理名「collection」、「稟議番号」は単語帳に登録されており物理名「ringiNo」を使用しました。全ての語が単語帳で充足されています。\",\"proposed_name\":\"collectionRingiNo\"}

例2（一部一致）
Input:
\"\"\"
component_analysis: {\"component_tokens\":[\"顧客\",\"名\"],\"unmatched_fragments\":[\"担当者\"],\"digit_segments\":[],\"expected_match_hint\":\"component_partial\",\"coverage_ratio\":0.67}
candidates: [{\"term\":\"顧客\",\"physical_name\":\"customer\",\"from_component\":true},
{\"term\":\"名\",\"physical_name\":\"Name\",\"from_component\":true}]
\"\"\"
Output:
{\"match_type\":\"一部一致\",\"matched_terms\":[\"顧客\",\"名\"],\"unmatched_terms\":[\"担当者\"],\"unmatched_notes\":[\"業務担当者を表す英語表現として personInCharge を採用しました。person で人を表し、inCharge で担当の意味を明確化することで、業務上の役割を正確に表現しています\"],\"coverage_ratio\":0.67,\"reason\":\"「顧客」は単語帳に登録されており物理名「customer」、「名」は単語帳に登録されており物理名「Name」を使用しました。「担当者」は未登録のため、業務担当者を表す英語表現 personInCharge を提案しました。この語は単語帳への追加を推奨します。\",\"proposed_name\":\"customerPersonInChargeName\"}

例3（数字のみ）
Input:
\"\"\"
component_analysis: {\"component_tokens\":[],\"unmatched_fragments\":[],\"digit_segments\":[\"1\",\"1\"],\"expected_match_hint\":\"digits_only\",\"coverage_ratio\":1.0}
candidates: []
\"\"\"
Output:
{\"match_type\":\"完全一致（部品ごと）\",\"matched_terms\":[],\"unmatched_terms\":null,\"unmatched_notes\":null,\"coverage_ratio\":1.0,\"reason\":\"画面項目名は数字のみ（1-1）で構成されており、数字は照合対象外ですが、物理名には数字を保持し、ハイフンは「and」に置き換えて「1and1」を提案しました。\",\"proposed_name\":\"1and1\"}

例4（一致なし）
Input:
\"\"\"
component_analysis: {\"component_tokens\":[],\"unmatched_fragments\":[\"緊急度\"],\"digit_segments\":[],\"expected_match_hint\":\"no_component_hit\",\"coverage_ratio\":0.0}
candidates: []
\"\"\"
Output:
{\"match_type\":\"一致なし\",\"matched_terms\":null,\"unmatched_terms\":[\"緊急度\"],\"unmatched_notes\":[\"緊急の度合いを表す英語 urgency を採用しました。業務上、優先度や重要度を表す一般的な英語表現として適切です\"],\"coverage_ratio\":0.0,\"reason\":\"「緊急度」は単語帳に登録されていないため、緊急の度合いを表す英語 urgency を提案しました。この語は単語帳への追加を推奨します。\",\"proposed_name\":\"urgency\"}
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
- reason は自然な日本語で丁寧に記述する（タグ不要、20文字以上）。
  * 一致した語とその物理名を説明
  * 未登録語に対する物理名提案とその理由を詳細に説明
- unmatched_notes は各要素について10文字以上で丁寧に記述する。
  * その語に対する物理名提案
  * なぜその物理名を選んだのかの理由（業務的意味、英語/ローマ字の選択理由など）
- coverage_ratio は component_analysis.coverage_ratio を使い、未提供時のみ自分で算出する。
- 数字だけの差分は unmatched_terms に含めず、理由に明記する。
- 候補との意味的整合性を必ず確認する（最長一致の原則に従い、より長い文字列で一致する候補を優先）。
- 論理名に数字が含まれる場合、物理名にも必ず数字を含める。
  * 例: 「顧客コード1」→「customerCode1」（数字の1を含める）
  * 例: 「申請日2」→「applicationDate2」（数字の2を含める）
- 略称（physical_name_abbr）が存在する場合は、必ず略称を優先して使用する。
---
タスク: 上記の画面項目名に対して、lowerCamelCaseの物理名を提案してください。
処理ステップ:
1. 画面項目名を意味のある語に分解
2. 各語が候補リストに存在するかチェック（意味的整合性も確認）
3. proposed_name生成:
   - 候補にある語 → その physical_name を使用（必須）
   - 候補にない語 → ネーミングルールに従い自分で考案（理由を reason と unmatched_notes に記載）
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
- unmatched_notes: unmatched_terms各要素の説明（10文字以上で丁寧に）
  * その語に対する物理名提案とその理由を記載
  * 英語/ローマ字の選択理由、業務的な意味などを含める
- reason: 判定理由を丁寧に記述（20文字以上）
  * タグ不要、自然な日本語で
  * 一致した語とその物理名、未登録語への提案とその理由を含める
JSON以外の出力は禁止です。必ず上記スキーマそのままのキー構成で 1 行の JSON を返してください。
"""
