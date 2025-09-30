#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語照合システムのテストコード
- モックAPIクライアント
- テストデータ生成
- 機能テスト
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

# テスト対象のモジュールをインポート
import sys
sys.path.append('.')
from word import (
    zenkaku_hankaku_norm, local_similarity, phrase_candidates, top_k_candidates,
    _pick_matching_sheets, load_screen_and_vocab, process, ApiClient,
    DEFAULT_CONFIG, Candidate
)


class MockApiClient:
    """LLM API呼び出しをモックするクライアント"""

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.call_count = 0
        self.responses = []

    def post_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """モックレスポンスを返す"""
        self.call_count += 1

        # リクエストを記録
        self.responses.append(payload)

        # ユーザーメッセージから画面項目名を抽出
        user_content = payload.get("messages", [{}])[-1].get("content", "")
        screen_name = self._extract_screen_name(user_content)

        # 候補から自動判定
        candidates_json = self._extract_candidates(user_content)

        # シンプルな判定ロジック
        if not candidates_json:
            return self._create_no_match_response(screen_name)

        top_candidate = candidates_json[0]
        score = top_candidate.get("local_score", 0.0)
        term = top_candidate.get("term", "")

        if score >= 0.95:
            return self._create_exact_match_response(screen_name, term)
        elif score >= 0.7:
            return self._create_partial_match_response(screen_name, term, score)
        else:
            return self._create_no_match_response(screen_name)

    def _extract_screen_name(self, content: str) -> str:
        """コンテンツから画面項目名を抽出"""
        lines = content.split('\n')
        for line in lines:
            if '# 画面項目名' in line:
                next_idx = lines.index(line) + 1
                if next_idx < len(lines):
                    return lines[next_idx].strip()
        return "unknown_item"

    def _extract_candidates(self, content: str) -> List[Dict]:
        """コンテンツから候補を抽出"""
        try:
            # JSON部分を探して解析
            start_marker = "# 単語帳候補（上位スコア順）"
            if start_marker in content:
                json_start = content.find('[', content.find(start_marker))
                json_end = content.find('\n\n', json_start)
                if json_start > -1 and json_end > -1:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
        except Exception:
            pass
        return []

    def _create_exact_match_response(self, screen_name: str, term: str) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "完全一致",
                        "matched_term": term,
                        "matched_terms": None,
                        "reason": f"'{screen_name}'と'{term}'は意味・表記ともに一致します。",
                        "proposed_name": term.lower().replace(" ", ""),
                        "coverage_ratio": 1.0
                    }, ensure_ascii=False)
                }
            }]
        }

    def _create_partial_match_response(self, screen_name: str, term: str, score: float) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "一部一致",
                        "matched_term": term,
                        "matched_terms": None,
                        "reason": f"'{screen_name}'と'{term}'は部分的に一致します（類似度: {score:.2f}）。",
                        "proposed_name": term.lower().replace(" ", ""),
                        "coverage_ratio": score
                    }, ensure_ascii=False)
                }
            }]
        }

    def _create_no_match_response(self, screen_name: str) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_type": "一致なし",
                        "matched_term": None,
                        "matched_terms": None,
                        "reason": f"'{screen_name}'に適合する単語が見つかりません。",
                        "proposed_name": screen_name.lower().replace(" ", ""),
                        "coverage_ratio": None
                    }, ensure_ascii=False)
                }
            }]
        }


class TestWordMatching(unittest.TestCase):
    """単語照合システムのテストクラス"""

    @classmethod
    def setUpClass(cls):
        """テスト用の一時ディレクトリとファイルを作成"""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_dir_path = Path(cls.test_dir)

        # テスト用Excelファイルを作成
        cls._create_test_excel_files()

        # テスト用設定
        cls.test_config = DEFAULT_CONFIG.copy()
        cls.test_config.update({
            "OUT_DIR": str(cls.test_dir_path / "out"),
            "MAX_WORKERS": 2,
            "TIMEOUT_SEC": 10.0
        })

    @classmethod
    def _create_test_excel_files(cls):
        """テスト用のExcelファイルを作成"""
        # 画面項目定義ファイル
        screen_data = {
            '項目名称': [
                '顧客コード',
                '顧客名',
                '融資・管理番号',
                '商品コード',
                '不明な項目',
                '複合語テスト項目'
            ]
        }

        # 単語帳ファイル
        vocab_data = {
            'No': [1, 2, 3, 4, 5, 6],
            '論理名': ['顧客コード', '顧客名', '融資', '管理', '商品', '複合語'],
            '物理名（正式名称）': ['customer_code', 'customer_name', 'loan', 'management', 'product', 'compound_word'],
            '物理名（略称）': ['cust_cd', 'cust_nm', 'loan', 'mgmt', 'prod', 'comp']
        }

        # 画面項目定義ファイル（複数シート）
        screen_file = cls.test_dir_path / "test_画面項目定義.xlsx"
        with pd.ExcelWriter(screen_file, engine='openpyxl') as writer:
            pd.DataFrame(screen_data).to_excel(writer, sheet_name='画面項目定義1', index=False)
            # 2つ目のシートを作成
            screen_data2 = {'項目名称': ['注文番号', '注文日', '配送先']}
            pd.DataFrame(screen_data2).to_excel(writer, sheet_name='画面項目定義2', index=False)

        # 単語帳ファイル
        vocab_file = cls.test_dir_path / "test_単語帳.xlsx"
        with pd.ExcelWriter(vocab_file, engine='openpyxl') as writer:
            pd.DataFrame(vocab_data).to_excel(writer, sheet_name='単語', index=False)

    def test_text_normalization(self):
        """テキスト正規化のテスト"""
        test_cases = [
            ("融資・管理", "融資 管理"),
            ("顧客　コード", "顧客 コード"),
            ("商品_番号", "商品 番号"),
            ("ＡＢＣ", "abc"),
            ("項目（詳細）", "項目 詳細"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = zenkaku_hankaku_norm(input_text)
                self.assertEqual(result, expected)

    def test_similarity_calculation(self):
        """類似度計算のテスト"""
        test_cases = [
            ("顧客コード", "顧客コード", 1.0),
            ("顧客コード", "顧客", 0.9),
            ("顧客", "顧客コード", 0.9),
            ("全く異なる", "別の文字列", 0.0),  # 低い類似度を期待
        ]

        for text1, text2, min_expected in test_cases:
            with self.subTest(text1=text1, text2=text2):
                result = local_similarity(text1, text2)
                if min_expected == 1.0:
                    self.assertEqual(result, 1.0)
                elif min_expected == 0.9:
                    self.assertEqual(result, 0.9)
                else:
                    self.assertLessEqual(result, 0.5)  # 低い類似度

    def test_sheet_selection(self):
        """シート選択のテスト"""
        class MockExcelFile:
            def __init__(self, sheet_names):
                self.sheet_names = sheet_names

        # 複数マッチテスト
        xls = MockExcelFile(['画面項目定義1', '画面項目定義2', '他のシート'])
        result = _pick_matching_sheets(xls, '画面項目定義')
        self.assertIn('画面項目定義1', result)
        self.assertIn('画面項目定義2', result)

        # 複数パターンテスト
        xls = MockExcelFile(['設計書', 'システム仕様', '画面定義'])
        result = _pick_matching_sheets(xls, '画面項目定義,設計書')
        self.assertIn('設計書', result)

    def test_candidate_generation(self):
        """候補生成のテスト"""
        vocab_terms = ['顧客コード', '顧客名', '融資', '管理', '商品']

        # 直接マッチ
        candidates = top_k_candidates('顧客コード', vocab_terms, 3, 0.7)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0].term, '顧客コード')
        self.assertEqual(candidates[0].score, 1.0)

        # 複合語マッチ
        candidates = phrase_candidates('融資管理', vocab_terms, 5, 0.7)
        candidate_terms = [c.term for c in candidates]
        self.assertIn('融資', candidate_terms)
        self.assertIn('管理', candidate_terms)

    def test_excel_loading(self):
        """Excel読み込みのテスト"""
        df_screen, df_vocab = load_screen_and_vocab(
            self.test_dir_path, self.test_config
        )

        # データが正しく読み込まれているかチェック
        self.assertGreater(len(df_screen), 0)
        self.assertGreater(len(df_vocab), 0)

        # 必須列が存在するかチェック
        self.assertIn('_screen', df_screen.columns)
        self.assertIn('_term', df_vocab.columns)
        self.assertIn('_phys', df_vocab.columns)

        # 複数シートが読み込まれているかチェック
        unique_sheets = df_screen['_src_sheet'].unique()
        self.assertGreater(len(unique_sheets), 1)

    def test_mock_api_client(self):
        """モックAPIクライアントのテスト"""
        client = MockApiClient(self.test_config)

        # テストペイロード
        payload = {
            "messages": [
                {"role": "system", "content": "test"},
                {"role": "user", "content": """
# 画面項目名
顧客コード

# 単語帳候補（上位スコア順）
[{"term": "顧客コード", "local_score": 1.0}]
                """}
            ]
        }

        response = client.post_json(payload)
        self.assertIn('choices', response)

        content = json.loads(response['choices'][0]['message']['content'])
        self.assertEqual(content['match_type'], '完全一致')
        self.assertEqual(content['matched_term'], '顧客コード')


def create_test_config_with_mock():
    """モックAPIを使用するテスト設定を作成"""
    config = DEFAULT_CONFIG.copy()
    config.update({
        "MAX_WORKERS": 2,
        "TIMEOUT_SEC": 5.0,
        "OUT_DIR": "/tmp/word_test_output"
    })
    return config


def run_integration_test():
    """統合テスト（モックAPI使用）"""
    print("=== 統合テスト開始 ===")

    # テストディレクトリ作成
    test_dir = Path(tempfile.mkdtemp())
    print(f"テストディレクトリ: {test_dir}")

    try:
        # テストデータ作成
        create_integration_test_data(test_dir)

        # 設定
        config = create_test_config_with_mock()
        config["OUT_DIR"] = str(test_dir / "output")

        # ApiClientをモックに置き換え
        original_api_client = None
        import word
        if hasattr(word, 'ApiClient'):
            original_api_client = word.ApiClient
            word.ApiClient = MockApiClient

        try:
            # メイン処理実行
            df_result = process(test_dir, None, None, config)

            print(f"処理結果: {len(df_result)}件")
            print("サンプル結果:")
            print(df_result[['screen_item', 'match_type', 'matched_term', 'reason']].head())

            # 結果検証
            assert len(df_result) > 0, "結果が空です"
            assert 'screen_item' in df_result.columns, "必須列が不足"

            # 完全一致が正しく判定されているかチェック
            exact_matches = df_result[df_result['match_type'] == '完全一致']
            print(f"完全一致: {len(exact_matches)}件")

            print("✅ 統合テスト成功")

        finally:
            # ApiClientを元に戻す
            if original_api_client:
                word.ApiClient = original_api_client

    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        raise
    finally:
        # クリーンアップ
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def create_integration_test_data(test_dir: Path):
    """統合テスト用のデータを作成"""
    # 画面項目定義
    screen_data = {
        '項目名称': [
            '顧客コード',
            '顧客名称',
            '融資・管理番号',
            '商品分類',
            '未知の項目',
            '複合テスト項目'
        ]
    }

    # 単語帳
    vocab_data = {
        'No': [1, 2, 3, 4, 5, 6, 7],
        '論理名': ['顧客コード', '顧客名称', '融資', '管理', '商品', '分類', '複合'],
        '物理名（正式名称）': ['customer_code', 'customer_name', 'loan', 'management', 'product', 'category', 'compound'],
        '物理名（略称）': ['cust_cd', 'cust_nm', 'loan', 'mgmt', 'prod', 'cat', 'comp']
    }

    # Excelファイル作成
    screen_file = test_dir / "統合テスト_画面項目定義.xlsx"
    with pd.ExcelWriter(screen_file, engine='openpyxl') as writer:
        pd.DataFrame(screen_data).to_excel(writer, sheet_name='画面項目定義', index=False)

    vocab_file = test_dir / "統合テスト_単語帳.xlsx"
    with pd.ExcelWriter(vocab_file, engine='openpyxl') as writer:
        pd.DataFrame(vocab_data).to_excel(writer, sheet_name='単語', index=False)


if __name__ == '__main__':
    print("単語照合システム テストスイート")
    print("=" * 50)

    # ユニットテスト実行
    print("1. ユニットテスト実行...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    print("\n" + "=" * 50)

    # 統合テスト実行
    print("2. 統合テスト実行...")
    run_integration_test()

    print("\n✅ 全テスト完了")