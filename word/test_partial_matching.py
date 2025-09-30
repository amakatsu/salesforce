#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部分一致テストの強化版
複合語、曖昧マッチング、エッジケースを包括的にテスト
"""

import os
import tempfile
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# テストモードを有効化
os.environ["WORD_MATCHING_TEST_MODE"] = "true"

from word import (
    process, DEFAULT_CONFIG, zenkaku_hankaku_norm,
    local_similarity, phrase_candidates, top_k_candidates,
    Candidate
)
from mock_api import mock_llm_response


class PartialMatchTestSuite:
    """部分一致テストスイート"""

    def __init__(self):
        self.test_results = []
        self.vocab_terms = [
            # 基本単語
            '顧客', '顧客コード', '顧客名', '顧客名称',
            '商品', '商品コード', '商品名', '商品分類',
            '注文', '注文番号', '注文日', '注文金額',
            '融資', '管理', '番号', 'コード', '名称', '日付',
            '削除', 'フラグ', '有効', '無効', '状態',
            'システム', '画面', '項目', '定義', '設計',
            # 複合語関連
            '申込', '審査', '承認', '契約', '実行',
            '金利', '期間', '返済', '残高', '利息',
            # 略語・省略形
            'ID', 'No', 'CD', 'NM', 'FLG', 'DT'
        ]

    def run_all_tests(self):
        """全ての部分一致テストを実行"""
        print("=" * 70)
        print("部分一致テスト強化版")
        print("=" * 70)

        # 1. 基本的な部分一致テスト
        self.test_basic_partial_matching()

        # 2. 複合語分解テスト
        self.test_compound_word_decomposition()

        # 3. 語順違いテスト
        self.test_word_order_variations()

        # 4. 略語・省略形テスト
        self.test_abbreviation_matching()

        # 5. 曖昧マッチングテスト
        self.test_fuzzy_matching()

        # 6. エッジケーステスト
        self.test_edge_cases()

        # 7. 統合的なシナリオテスト
        self.test_integrated_scenarios()

        # 結果サマリー
        self.print_test_summary()

    def test_basic_partial_matching(self):
        """基本的な部分一致テスト"""
        print("\n1. 基本的な部分一致テスト:")

        test_cases = [
            # (画面項目名, 期待される一致タイプ, 期待される一致語, 説明)
            ("顧客コード", "完全一致", ["顧客コード"], "完全一致"),
            ("顧客名称", "完全一致", ["顧客名称"], "完全一致"),
            ("顧客情報", "一部一致", ["顧客"], "部分包含"),
            ("コード番号", "一部一致", ["コード", "番号"], "複合語"),
            ("商品管理システム", "一部一致", ["商品", "管理", "システム"], "3語複合"),
            ("削除フラグ", "一部一致", ["削除", "フラグ"], "状態フラグ"),
        ]

        for screen_item, expected_type, expected_terms, description in test_cases:
            result = self._test_single_item(screen_item, expected_type, expected_terms)
            print(f"   {result['status']} {description}: '{screen_item}' → {result['actual_type']}")
            if result['details']:
                print(f"      {result['details']}")

    def test_compound_word_decomposition(self):
        """複合語分解テスト"""
        print("\n2. 複合語分解テスト:")

        test_cases = [
            # 2語複合
            ("融資管理", ["融資", "管理"]),
            ("注文番号", ["注文", "番号"]),
            ("商品分類", ["商品", "分類"]),
            ("顧客名称", ["顧客名称"]),  # 完全一致が優先

            # 3語複合
            ("融資管理番号", ["融資", "管理", "番号"]),
            ("商品分類コード", ["商品", "分類", "コード"]),
            ("顧客注文情報", ["顧客", "注文"]),

            # 記号込み複合語
            ("融資・管理", ["融資", "管理"]),
            ("融資_管理", ["融資", "管理"]),
            ("融資（管理）", ["融資", "管理"]),
        ]

        for screen_item, expected_components in test_cases:
            candidates = phrase_candidates(screen_item, self.vocab_terms, 10, 0.7)
            found_components = [c.term for c in candidates if c.score >= 0.8]

            # 期待される構成要素がすべて見つかるかチェック
            missing = set(expected_components) - set(found_components)
            extra = set(found_components) - set(expected_components)

            if not missing and not extra:
                status = "✅"
                details = f"完全一致: {found_components}"
            else:
                status = "⚠️"
                details = f"発見: {found_components}, 期待: {expected_components}"
                if missing:
                    details += f", 不足: {list(missing)}"
                if extra:
                    details += f", 余分: {list(extra)}"

            print(f"   {status} '{screen_item}' → {details}")

    def test_word_order_variations(self):
        """語順違いテスト"""
        print("\n3. 語順違いテスト:")

        test_pairs = [
            ("管理融資", "融資管理"),
            ("番号注文", "注文番号"),
            ("コード商品", "商品コード"),
            ("システム管理", "管理システム"),
        ]

        for variant1, variant2 in test_pairs:
            candidates1 = phrase_candidates(variant1, self.vocab_terms, 5, 0.7)
            candidates2 = phrase_candidates(variant2, self.vocab_terms, 5, 0.7)

            terms1 = {c.term for c in candidates1 if c.score >= 0.8}
            terms2 = {c.term for c in candidates2 if c.score >= 0.8}

            # 同じ構成要素が検出されるかチェック
            if terms1 == terms2 and len(terms1) >= 2:
                status = "✅"
                details = f"同一構成要素検出: {terms1}"
            else:
                status = "⚠️"
                details = f"'{variant1}': {terms1}, '{variant2}': {terms2}"

            print(f"   {status} 語順テスト: {details}")

    def test_abbreviation_matching(self):
        """略語・省略形テスト"""
        print("\n4. 略語・省略形テスト:")

        # 略語辞書（実際の運用では設定ファイルで管理）
        abbreviation_map = {
            "CD": "コード",
            "NM": "名称",
            "ID": "番号",
            "FLG": "フラグ",
            "DT": "日付",
        }

        test_cases = [
            ("顧客CD", ["顧客", "コード"]),
            ("商品NM", ["商品", "名称"]),
            ("削除FLG", ["削除", "フラグ"]),
            ("注文DT", ["注文", "日付"]),
        ]

        for screen_item, expected_expansion in test_cases:
            # 現在の実装での結果
            candidates = phrase_candidates(screen_item, self.vocab_terms, 5, 0.7)
            found_terms = [c.term for c in candidates if c.score >= 0.7]

            # 略語展開後の理想的な結果と比較
            has_base_term = any(term in found_terms for term in expected_expansion[:-1])

            if has_base_term:
                status = "✅"
                details = f"ベース語検出: {found_terms}"
            else:
                status = "⚠️"
                details = f"要改善 - 発見: {found_terms}, 期待: {expected_expansion}"

            print(f"   {status} '{screen_item}' → {details}")

    def test_fuzzy_matching(self):
        """曖昧マッチングテスト"""
        print("\n5. 曖昧マッチングテスト:")

        test_cases = [
            # 表記ゆれ
            ("クライアント", ["顧客"], "表記ゆれ"),
            ("プロダクト", ["商品"], "カタカナ英語"),
            ("オーダー", ["注文"], "カタカナ英語"),

            # 誤字・タイポ
            ("顧容", ["顧客"], "誤字"),
            ("商晶", ["商品"], "誤字"),

            # 部分文字列
            ("顧客情報", ["顧客"], "包含関係"),
            ("商品データ", ["商品"], "包含関係"),
        ]

        for screen_item, expected_matches, test_type in test_cases:
            similarity_scores = []
            for term in self.vocab_terms:
                score = local_similarity(screen_item, term)
                if score >= 0.6:  # 曖昧マッチングの閾値
                    similarity_scores.append((term, score))

            similarity_scores.sort(key=lambda x: x[1], reverse=True)
            found_matches = [term for term, score in similarity_scores[:3]]

            # 期待される一致語が含まれているかチェック
            match_found = any(expected in found_matches for expected in expected_matches)

            if match_found:
                status = "✅"
                details = f"マッチ検出: {similarity_scores[:2]}"
            else:
                status = "⚠️"
                details = f"要改善 - 発見: {found_matches}, 期待: {expected_matches}"

            print(f"   {status} {test_type}: '{screen_item}' → {details}")

    def test_edge_cases(self):
        """エッジケーステスト"""
        print("\n6. エッジケーステスト:")

        edge_cases = [
            # 長い複合語
            ("顧客情報管理システム画面項目定義", "超長複合語"),

            # 単一文字
            ("A", "単一文字"),
            ("1", "数字"),

            # 空文字・特殊文字
            ("", "空文字"),
            ("！@#", "特殊文字のみ"),

            # 非常に類似した語
            ("顧客コード1", "数字付き"),
            ("顧客コード２", "全角数字付き"),

            # スペース・記号の連続
            ("顧客　　コード", "スペース連続"),
            ("顧客・・・コード", "記号連続"),
        ]

        for screen_item, case_type in edge_cases:
            try:
                if not screen_item:  # 空文字のテスト
                    normalized = zenkaku_hankaku_norm(screen_item)
                    status = "✅" if normalized == "" else "❌"
                    print(f"   {status} {case_type}: 空文字 → '{normalized}'")
                    continue

                candidates = phrase_candidates(screen_item, self.vocab_terms, 3, 0.5)

                if len(screen_item) >= 10:  # 長い語のテスト
                    status = "✅" if len(candidates) > 0 else "⚠️"
                    print(f"   {status} {case_type}: '{screen_item[:20]}...' → {len(candidates)}件の候補")
                else:
                    status = "✅"
                    print(f"   {status} {case_type}: '{screen_item}' → {len(candidates)}件の候補")

            except Exception as e:
                print(f"   ❌ {case_type}: '{screen_item}' → エラー: {e}")

    def test_integrated_scenarios(self):
        """統合的なシナリオテスト"""
        print("\n7. 統合的なシナリオテスト:")

        # 実際のExcelファイルを模擬したテストデータ
        test_data = self._create_realistic_test_data()

        try:
            test_dir = self._create_test_excel_files(test_data)

            # 設定
            config = DEFAULT_CONFIG.copy()
            config.update({
                "TEST_MODE": True,
                "MAX_WORKERS": 2,
                "OUT_DIR": str(test_dir / "output")
            })

            # 処理実行
            df_result = process(test_dir, None, None, config)

            # 結果分析
            match_counts = df_result['match_type'].value_counts()

            print(f"   ✅ 統合テスト完了: {len(df_result)}件処理")
            print(f"      完全一致: {match_counts.get('完全一致', 0)}件")
            print(f"      一部一致: {match_counts.get('一部一致', 0)}件")
            print(f"      一致なし: {match_counts.get('一致なし', 0)}件")

            # 複合語の検出率
            compound_matches = df_result[df_result['matched_terms'].notna()]
            print(f"      複合語検出: {len(compound_matches)}件")

            # 問題のある結果をハイライト
            no_matches = df_result[df_result['match_type'] == '一致なし']
            if len(no_matches) > len(df_result) * 0.3:  # 30%以上が一致なしなら要注意
                print(f"   ⚠️  一致なし率が高め: {len(no_matches)/len(df_result)*100:.1f}%")

            # クリーンアップ
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)

        except Exception as e:
            print(f"   ❌ 統合テストエラー: {e}")

    def _test_single_item(self, screen_item: str, expected_type: str, expected_terms: List[str]) -> Dict[str, Any]:
        """単一項目のテスト"""
        candidates = phrase_candidates(screen_item, self.vocab_terms, 10, 0.7)

        if not candidates:
            mock_result = {"match_type": "一致なし", "matched_term": None, "matched_terms": None}
        else:
            mock_result = mock_llm_response(screen_item, candidates)

        actual_type = mock_result["match_type"]
        actual_terms = []

        if mock_result.get("matched_term"):
            actual_terms = [mock_result["matched_term"]]
        elif mock_result.get("matched_terms"):
            actual_terms = mock_result["matched_terms"]

        # 結果評価
        type_match = actual_type == expected_type
        term_overlap = len(set(actual_terms) & set(expected_terms)) > 0

        if type_match and (term_overlap or expected_type == "一致なし"):
            status = "✅"
            details = ""
        else:
            status = "⚠️"
            details = f"期待: {expected_type}({expected_terms}), 実際: {actual_type}({actual_terms})"

        return {
            "status": status,
            "actual_type": actual_type,
            "actual_terms": actual_terms,
            "details": details
        }

    def _create_realistic_test_data(self) -> Dict[str, List[str]]:
        """現実的なテストデータを作成"""
        return {
            "screen_items": [
                # 基本項目
                "顧客コード", "顧客名称", "商品コード", "商品名称",

                # 複合語項目
                "融資管理番号", "商品分類コード", "注文受付日",
                "削除フラグ", "有効期間", "承認状態",

                # 複雑な項目
                "顧客情報管理システム", "商品分類マスタ",
                "注文金額合計", "融資・返済スケジュール",

                # 略語・記号込み
                "顧客CD", "商品NM", "注文No.", "削除FLG",

                # 誤字・表記ゆれ
                "顧容コード", "商晶名称", "クライアント情報",

                # エッジケース
                "A001", "項目（備考）", "データ１", "システム　画面",

                # 一致しないもの
                "謎の項目", "不明なデータ", "XXXコード",
            ],

            "vocab_terms": self.vocab_terms
        }

    def _create_test_excel_files(self, test_data: Dict[str, List[str]]) -> Path:
        """テスト用Excelファイルを作成"""
        test_dir = Path(tempfile.mkdtemp())

        # 画面項目定義ファイル
        screen_data = {"項目名称": test_data["screen_items"]}
        screen_file = test_dir / "部分一致テスト_画面項目定義.xlsx"
        with pd.ExcelWriter(screen_file, engine='openpyxl') as writer:
            pd.DataFrame(screen_data).to_excel(writer, sheet_name='画面項目定義', index=False)

        # 単語帳ファイル
        vocab_data = {
            'No': list(range(1, len(test_data["vocab_terms"]) + 1)),
            '論理名': test_data["vocab_terms"],
            '物理名（正式名称）': [f"term_{i:03d}" for i in range(len(test_data["vocab_terms"]))],
            '物理名（略称）': [f"t{i:03d}" for i in range(len(test_data["vocab_terms"]))]
        }
        vocab_file = test_dir / "部分一致テスト_単語帳.xlsx"
        with pd.ExcelWriter(vocab_file, engine='openpyxl') as writer:
            pd.DataFrame(vocab_data).to_excel(writer, sheet_name='単語', index=False)

        return test_dir

    def print_test_summary(self):
        """テスト結果サマリー"""
        print("\n" + "=" * 70)
        print("部分一致テスト完了")
        print("=" * 70)
        print("📋 テスト内容:")
        print("  1. 基本的な部分一致")
        print("  2. 複合語分解")
        print("  3. 語順違い")
        print("  4. 略語・省略形")
        print("  5. 曖昧マッチング")
        print("  6. エッジケース")
        print("  7. 統合シナリオ")
        print("\n💡 改善提案:")
        print("  - 略語辞書の追加検討")
        print("  - 表記ゆれ辞書の整備")
        print("  - 複合語分解ルールの改善")
        print("  - 業務ドメイン知識の反映")


if __name__ == "__main__":
    test_suite = PartialMatchTestSuite()
    test_suite.run_all_tests()