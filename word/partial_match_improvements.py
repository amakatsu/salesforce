#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
word.pyの部分一致機能を改善するパッチ提案

以下の機能を追加：
1. 略語辞書による展開
2. 表記ゆれ対応
3. より精密な複合語分解
4. 曖昧マッチングの改善
"""

import unicodedata
import re
import difflib
from typing import List, Dict, Optional


# ========== 改善された関数群 ==========

def enhanced_zenkaku_hankaku_norm(text: str, use_abbreviation_dict: bool = True) -> str:
    """改良版正規化：略語展開も含む"""
    if text is None:
        return ""

    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = re.sub(r"[\u3000\s]+", " ", s)
    s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)
    s = re.sub(r"\s+", " ", s)

    if use_abbreviation_dict:
        # 略語辞書による展開
        abbreviation_dict = {
            "cd": "コード", "code": "コード",
            "nm": "名称", "name": "名称",
            "id": "番号", "no": "番号", "num": "番号",
            "flg": "フラグ", "flag": "フラグ",
            "dt": "日付", "date": "日付",
            "amt": "金額", "amount": "金額",
            "qty": "数量", "quantity": "数量",
            "sys": "システム", "system": "システム",
            "mgmt": "管理", "management": "管理",
            "info": "情報", "information": "情報",
        }

        tokens = s.split()
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(abbreviation_dict.get(token, token))
        s = " ".join(expanded_tokens)

    return s


def enhanced_local_similarity(a: str, b: str) -> float:
    """改良版類似度計算：表記ゆれも考慮"""
    # 表記ゆれ辞書
    variation_dict = {
        "クライアント": "顧客", "カスタマー": "顧客", "ユーザー": "顧客",
        "プロダクト": "商品", "アイテム": "商品", "製品": "商品",
        "オーダー": "注文", "リクエスト": "注文",
        "デリート": "削除", "リムーブ": "削除",
        "ステータス": "状態", "コンディション": "状態",
    }

    # 表記ゆれ変換
    a_converted = a
    b_converted = b
    for variation, standard in variation_dict.items():
        if variation in a:
            a_converted = a.replace(variation, standard)
        if variation in b:
            b_converted = b.replace(variation, standard)

    # 正規化
    a_n = enhanced_zenkaku_hankaku_norm(a_converted)
    b_n = enhanced_zenkaku_hankaku_norm(b_converted)

    if not a_n or not b_n:
        return 0.0
    if a_n == b_n:
        return 1.0
    if a_n in b_n or b_n in a_n:
        return 0.9

    # 編集距離 + 文字重複度のハイブリッド
    edit_sim = difflib.SequenceMatcher(None, a_n, b_n).ratio()
    char_overlap = len(set(a_n) & set(b_n))
    char_sim = char_overlap / max(len(set(a_n)), len(set(b_n)), 1)

    return edit_sim * 0.7 + char_sim * 0.3


def enhanced_phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List:
    """改良版複合語候補生成"""
    from word import Candidate

    # 基本分割（スペース区切り）
    tokens = [t for t in enhanced_zenkaku_hankaku_norm(screen_name).split(" ") if t]

    # 語彙ベース分割の改良版
    enhanced_tokens = []
    for token in tokens:
        if len(token) >= 3:
            # より精密な分割ロジック
            splits = _advanced_vocab_split(token, vocab_terms)
            if len(splits) > 1:
                enhanced_tokens.extend(splits)
            else:
                enhanced_tokens.append(token)
        else:
            enhanced_tokens.append(token)

    # unigram/bigram/trigram生成
    grams = set(enhanced_tokens)
    for i in range(len(enhanced_tokens) - 1):
        grams.add(enhanced_tokens[i] + " " + enhanced_tokens[i + 1])
    for i in range(len(enhanced_tokens) - 2):  # trigram追加
        grams.add(enhanced_tokens[i] + " " + enhanced_tokens[i + 1] + " " + enhanced_tokens[i + 2])

    # 候補スコア計算（改良版類似度使用）
    pool = []
    for g in grams:
        for vt in vocab_terms:
            s = enhanced_local_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))

    # 同一単語は最大スコアを採用
    best_by_term = {}
    for cand in pool:
        best_by_term[cand.term] = max(best_by_term.get(cand.term, 0.0), cand.score)

    merged = [Candidate(t, sc) for t, sc in best_by_term.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[:max(k, 15)]  # 候補数を増加


def _advanced_vocab_split(text: str, vocab_terms: List[str]) -> List[str]:
    """高度な語彙ベース分割"""
    if len(text) <= 2:
        return [text]

    # 語彙を正規化長でソート（最長マッチのため）
    sorted_vocab = sorted(
        [v for v in set(vocab_terms) if len(enhanced_zenkaku_hankaku_norm(v)) >= 2],
        key=lambda x: len(enhanced_zenkaku_hankaku_norm(x)),
        reverse=True
    )

    tokens = []
    i = 0
    normalized_text = enhanced_zenkaku_hankaku_norm(text)

    while i < len(normalized_text):
        matched = False
        best_match = None
        best_length = 0

        # 最長マッチを探す（改良：複数候補から最適選択）
        for vocab in sorted_vocab:
            norm_vocab = enhanced_zenkaku_hankaku_norm(vocab)
            if (normalized_text[i:].startswith(norm_vocab) and
                len(norm_vocab) >= 2 and
                len(norm_vocab) > best_length):

                # より厳密な境界チェック
                end_pos = i + len(norm_vocab)
                if (end_pos == len(normalized_text) or
                    normalized_text[end_pos] in " "):
                    best_match = vocab
                    best_length = len(norm_vocab)

        if best_match:
            tokens.append(best_match)
            i += best_length
            matched = True

        if not matched:
            i += 1

    return [t for t in tokens if len(enhanced_zenkaku_hankaku_norm(t)) >= 2]


def enhanced_mock_llm_response(screen_name: str, candidates: List, use_enhanced_logic: bool = True):
    """改良版モックLLMレスポンス"""
    from word import simple_proposal

    if not candidates:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": f"改良版: '{screen_name}'に対する候補が見つかりません。",
            "proposed_name": simple_proposal(screen_name),
            "coverage_ratio": None
        }

    # 候補をスコア別に分類
    high_score_candidates = [c for c in candidates if c.score >= 0.95]
    good_candidates = [c for c in candidates if 0.8 <= c.score < 0.95]
    ok_candidates = [c for c in candidates if 0.7 <= c.score < 0.8]

    # 改良された判定ロジック
    if high_score_candidates:
        # 高スコア候補がある場合
        top = high_score_candidates[0]
        return {
            "match_type": "完全一致",
            "matched_term": top.term,
            "matched_terms": None,
            "reason": f"改良版: '{screen_name}'と'{top.term}'は高精度一致です（スコア: {top.score:.3f}）。",
            "proposed_name": simple_proposal(top.term),
            "coverage_ratio": 1.0
        }

    elif len(good_candidates) >= 2:
        # 複数の良好候補→複合語
        terms = [c.term for c in good_candidates[:3]]
        avg_score = sum(c.score for c in good_candidates[:3]) / len(good_candidates[:3])
        return {
            "match_type": "一部一致",
            "matched_term": None,
            "matched_terms": terms,
            "reason": f"改良版: '{screen_name}'は複合語として「{', '.join(terms)}」と一致します（平均スコア: {avg_score:.3f}）。",
            "proposed_name": _generate_compound_name(terms),
            "coverage_ratio": avg_score
        }

    elif good_candidates:
        # 単一の良好候補
        top = good_candidates[0]
        return {
            "match_type": "一部一致",
            "matched_term": top.term,
            "matched_terms": None,
            "reason": f"改良版: '{screen_name}'と'{top.term}'は部分一致です（スコア: {top.score:.3f}）。",
            "proposed_name": simple_proposal(top.term),
            "coverage_ratio": top.score
        }

    elif ok_candidates:
        # 中程度の候補
        top = ok_candidates[0]
        return {
            "match_type": "一部一致",
            "matched_term": top.term,
            "matched_terms": None,
            "reason": f"改良版: '{screen_name}'と'{top.term}'は曖昧一致です（スコア: {top.score:.3f}）。確認推奨。",
            "proposed_name": simple_proposal(top.term),
            "coverage_ratio": top.score
        }

    else:
        return {
            "match_type": "一致なし",
            "matched_term": None,
            "matched_terms": None,
            "reason": f"改良版: '{screen_name}'に適合する単語が見つかりません（最高スコア: {candidates[0].score:.3f}）。",
            "proposed_name": simple_proposal(screen_name),
            "coverage_ratio": None
        }


def _generate_compound_name(terms: List[str]) -> str:
    """複合語の物理名生成"""
    translation_dict = {
        "顧客": "customer", "商品": "product", "注文": "order",
        "コード": "code", "番号": "number", "名称": "name",
        "管理": "management", "システム": "system", "情報": "info",
        "削除": "delete", "フラグ": "flag", "状態": "status",
        "融資": "loan", "申込": "application", "審査": "review"
    }

    parts = []
    for term in terms[:3]:
        if term in translation_dict:
            parts.append(translation_dict[term])
        else:
            # フォールバック
            clean = re.sub(r'[^a-zA-Z]', '', term.lower())
            parts.append(clean[:4] if clean else "item")

    if parts:
        return parts[0] + "".join(p.capitalize() for p in parts[1:])
    return "compoundItem"


# ========== テスト関数 ==========

def test_improvements():
    """改善機能のテスト"""
    print("=" * 60)
    print("部分一致改善機能テスト")
    print("=" * 60)

    vocab_terms = [
        '顧客', '顧客コード', '顧客名', '商品', '商品コード', '商品名',
        '注文', '注文番号', '融資', '管理', '番号', 'コード', '名称',
        'システム', '削除', 'フラグ', '状態', '情報', '申込', '審査'
    ]

    test_cases = [
        ("顧客CD", "略語展開テスト"),
        ("クライアント情報", "表記ゆれテスト"),
        ("融資管理システム", "3語複合語テスト"),
        ("商晶コード", "誤字対応テスト"),
        ("プロダクト名称", "カタカナ英語テスト"),
        ("申込審査フラグ", "複雑複合語テスト"),
    ]

    for screen_name, test_type in test_cases:
        print(f"\n🔍 {test_type}: '{screen_name}'")

        # 従来版
        from word import phrase_candidates, Candidate
        old_candidates = phrase_candidates(screen_name, vocab_terms, 10, 0.7)

        # 改良版
        new_candidates = enhanced_phrase_candidates(screen_name, vocab_terms, 10, 0.7)

        print(f"   従来版: {len(old_candidates)}件")
        for c in old_candidates[:3]:
            print(f"     - {c.term} ({c.score:.3f})")

        print(f"   改良版: {len(new_candidates)}件")
        for c in new_candidates[:3]:
            print(f"     - {c.term} ({c.score:.3f})")

        # モック判定結果
        if new_candidates:
            result = enhanced_mock_llm_response(screen_name, new_candidates)
            print(f"   → 結論: {result['match_type']}")
            if result.get('matched_terms'):
                print(f"     複合語: {result['matched_terms']}")
            elif result.get('matched_term'):
                print(f"     一致語: {result['matched_term']}")


if __name__ == "__main__":
    test_improvements()