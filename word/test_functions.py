#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語照合システムの個別機能テスト（依存関係なし）
"""

import unicodedata
import difflib
import re
from typing import List


# word.pyから抽出した個別関数（依存関係なし）
def zenkaku_hankaku_norm(text: str) -> str:
    """NFKC正規化 + 小文字化 + 記号/空白の正規化で**照合の土台**を整える。"""
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).lower().strip()
    s = re.sub(r"[\u3000\s]+", " ", s)          # 全角/半角スペースを単一化
    s = re.sub(r"[\-/・·•･,()\[\]_]+", " ", s)    # 区切り記号はスペースへ
    return re.sub(r"\s+", " ", s)


def local_similarity(a: str, b: str) -> float:
    """簡易類似度：完全一致=1.0 / 片包含=0.9 / それ以外はdifflibのratio。"""
    a_n, b_n = zenkaku_hankaku_norm(a), zenkaku_hankaku_norm(b)
    if not a_n or not b_n:
        return 0.0
    if a_n == b_n:
        return 1.0
    if a_n in b_n or b_n in a_n:
        return 0.9
    return difflib.SequenceMatcher(None, a_n, b_n).ratio()


class Candidate:
    def __init__(self, term: str, score: float):
        self.term = term
        self.score = score

    def __repr__(self):
        return f"Candidate('{self.term}', {self.score:.3f})"


def top_k_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """画面項目 vs 単語帳の**直接照合**で上位k件を返却。"""
    scored = [Candidate(term, local_similarity(screen_name, term)) for term in vocab_terms]
    scored.sort(key=lambda c: c.score, reverse=True)
    return [c for c in scored[:k] if c.score >= threshold]


def phrase_candidates(screen_name: str, vocab_terms: List[str], k: int, threshold: float) -> List[Candidate]:
    """複合語対策：unigram/bigram に分解してパーツ単位で候補を拾う。"""
    tokens = [t for t in zenkaku_hankaku_norm(screen_name).split(" ") if t]
    grams = set(tokens)
    for i in range(len(tokens) - 1):
        grams.add(tokens[i] + " " + tokens[i + 1])
    pool: List[Candidate] = []
    for g in grams:
        for vt in vocab_terms:
            s = local_similarity(g, vt)
            if s >= threshold:
                pool.append(Candidate(vt, s))
    # 同一単語は最大スコアを採用
    best_by_term = {}
    for cand in pool:
        best_by_term[cand.term] = max(best_by_term.get(cand.term, 0.0), cand.score)
    merged = [Candidate(t, sc) for t, sc in best_by_term.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[: max(k, 10)]


class MockExcelFile:
    def __init__(self, sheet_names):
        self.sheet_names = sheet_names


def _pick_matching_sheets(xls: MockExcelFile, preferred: str) -> List[str]:
    """設定シート名にマッチする全てのシートを返す。複数パターン・曖昧マッチング対応。"""
    if not preferred:
        return [xls.sheet_names[0]]

    norm = lambda s: unicodedata.normalize("NFKC", s).strip().lower()

    # 複数パターンをカンマ区切りで分割
    patterns = [p.strip() for p in preferred.split(",") if p.strip()]
    if not patterns:
        return [xls.sheet_names[0]]

    all_matches = []

    for pattern in patterns:
        want = norm(pattern)
        exact_matches = []
        fuzzy_matches = []
        partial_matches = []

        for name in xls.sheet_names:
            norm_name = norm(name)

            # 1. 完全一致
            if norm_name == want:
                exact_matches.append(name)
            # 2. 部分包含（双方向）
            elif want in norm_name or norm_name in want:
                partial_matches.append(name)
            # 3. 曖昧マッチ（文字の75%以上が共通）
            else:
                # 簡易的な類似度計算
                common_chars = len(set(want) & set(norm_name))
                similarity = common_chars / max(len(want), len(norm_name)) if max(len(want), len(norm_name)) > 0 else 0
                if similarity >= 0.75:  # 75%以上の類似度
                    fuzzy_matches.append(name)

        # 優先順位: 完全一致 > 部分一致 > 曖昧一致
        if exact_matches:
            all_matches.extend(exact_matches)
        elif partial_matches:
            all_matches.extend(partial_matches)
        elif fuzzy_matches:
            all_matches.extend(fuzzy_matches)

    # 重複を除去して順序を保持
    result = []
    seen = set()
    for sheet in all_matches:
        if sheet not in seen:
            result.append(sheet)
            seen.add(sheet)

    # マッチするものがなければ先頭シート
    return result if result else [xls.sheet_names[0]]


def run_comprehensive_test():
    """総合的な機能テスト"""
    print("=" * 60)
    print("単語照合システム 個別機能テスト")
    print("=" * 60)

    # 1. テキスト正規化テスト
    print("\n1. テキスト正規化テスト:")
    norm_test_cases = [
        ("融資・管理", "融資 管理"),
        ("顧客　コード", "顧客 コード"),
        ("商品_番号", "商品 番号"),
        ("ＡＢＣ", "abc"),
        ("項目（詳細）", "項目 詳細"),
        ("融資•管理", "融資 管理"),  # 別の中点文字
        ("融資･管理", "融資 管理"),  # 半角中点
    ]

    all_passed = True
    for input_text, expected in norm_test_cases:
        result = zenkaku_hankaku_norm(input_text)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"   {status} '{input_text}' → '{result}' (期待値: '{expected}')")

    # 2. 類似度計算テスト
    print("\n2. 類似度計算テスト:")
    similarity_test_cases = [
        ("顧客コード", "顧客コード", 1.0),
        ("顧客コード", "顧客", 0.9),
        ("顧客", "顧客コード", 0.9),
        ("融資", "融資管理", 0.9),
        ("全く異なる", "別の文字列", lambda x: x < 0.5),
    ]

    for text1, text2, expected in similarity_test_cases:
        result = local_similarity(text1, text2)
        if callable(expected):
            passed = expected(result)
            status = "✅" if passed else "❌"
            print(f"   {status} '{text1}' vs '{text2}' → {result:.3f} (条件: < 0.5)")
        else:
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{text1}' vs '{text2}' → {result:.3f} (期待値: {expected})")
        if status == "❌":
            all_passed = False

    # 3. 候補生成テスト
    print("\n3. 候補生成テスト:")
    vocab_terms = ['顧客コード', '顧客名', '融資', '管理', '商品', '分類', '削除', 'フラグ']

    test_queries = [
        ("顧客コード", "完全一致"),
        ("融資管理", "複合語"),
        ("商品分類", "複合語"),
        ("削除フラグ", "複合語"),
    ]

    for query, test_type in test_queries:
        print(f"\n   {test_type}テスト: '{query}'")

        # 直接候補
        direct_candidates = top_k_candidates(query, vocab_terms, 3, 0.7)
        print(f"     直接候補: {[f'{c.term}({c.score:.2f})' for c in direct_candidates]}")

        # 複合語候補
        phrase_cands = phrase_candidates(query, vocab_terms, 5, 0.7)
        print(f"     複合語候補: {[f'{c.term}({c.score:.2f})' for c in phrase_cands]}")

    # 4. シート選択テスト
    print("\n4. シート選択テスト:")
    sheet_test_cases = [
        (['画面項目定義1', '画面項目定義2', '他のシート'], '画面項目定義', 2),
        (['設計書', 'システム仕様', '画面定義'], '画面項目定義,設計書', 2),
        (['画面項目詳細', 'システム概要'], '画面項目定義', 1),  # 曖昧マッチ
    ]

    for sheet_names, pattern, expected_count in sheet_test_cases:
        mock_xls = MockExcelFile(sheet_names)
        result = _pick_matching_sheets(mock_xls, pattern)
        status = "✅" if len(result) == expected_count else "❌"
        print(f"   {status} シート: {sheet_names}")
        print(f"       パターン: '{pattern}' → {result}")
        if status == "❌":
            all_passed = False

    # 5. モックAPIテスト
    print("\n5. モックAPIテスト:")
    try:
        from mock_api import mock_llm_response

        mock_test_cases = [
            ([Candidate('顧客コード', 1.0)], '顧客コード', '完全一致'),
            ([Candidate('顧客', 0.8)], '顧客コード', '一部一致'),
            ([Candidate('融資', 0.9), Candidate('管理', 0.85)], '融資管理', '一部一致'),
            ([Candidate('全然違う', 0.3)], '不明な項目', '一致なし'),
        ]

        for candidates, screen_name, expected_type in mock_test_cases:
            result = mock_llm_response(screen_name, candidates)
            status = "✅" if result['match_type'] == expected_type else "❌"
            print(f"   {status} '{screen_name}' → {result['match_type']} (期待値: {expected_type})")
            if status == "❌":
                all_passed = False

    except ImportError:
        print("   ⚠️  mock_api.pyが利用できません")

    # 結果サマリー
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 全テスト成功！")
    else:
        print("⚠️  一部のテストが失敗しました")

    return all_passed


if __name__ == "__main__":
    run_comprehensive_test()