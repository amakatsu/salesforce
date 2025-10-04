#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
単語照合システムの簡易テスト実行スクリプト
"""

import os
import tempfile
import pandas as pd
from pathlib import Path

# テストモードを有効化
os.environ["WORD_MATCHING_TEST_MODE"] = "true"

from word import process, DEFAULT_CONFIG


def create_sample_data():
    """サンプルテストデータを作成"""
    test_dir = Path(tempfile.mkdtemp())
    print(f"テストデータ作成: {test_dir}")

    # 画面項目定義データ
    screen_data = {
        '項目名称': [
            '顧客コード',       # 完全一致
            '顧客名称',         # 完全一致
            '融資・管理番号',   # 複合語（分割テスト）
            '商品分類',         # 部分一致
            '謎の項目',         # 一致なし
            '削除フラグ'        # 部分一致
        ]
    }

    # 単語帳データ
    vocab_data = {
        'No': [1, 2, 3, 4, 5, 6, 7, 8],
        '論理名': ['顧客コード', '顧客名称', '融資', '管理', '商品', '分類', '削除', 'フラグ'],
        '物理名（正式名称）': [
            'customer_code', 'customer_name', 'loan', 'management',
            'product', 'category', 'delete', 'flag'
        ],
        '物理名（略称）': [
            'cust_cd', 'cust_nm', 'loan', 'mgmt',
            'prod', 'cat', 'del', 'flg'
        ]
    }

    # Excelファイル作成
    screen_file = test_dir / "テスト_画面項目定義.xlsx"
    with pd.ExcelWriter(screen_file, engine='openpyxl') as writer:
        pd.DataFrame(screen_data).to_excel(writer, sheet_name='画面項目定義', index=False)

    vocab_file = test_dir / "テスト_単語帳.xlsx"
    with pd.ExcelWriter(vocab_file, engine='openpyxl') as writer:
        pd.DataFrame(vocab_data).to_excel(writer, sheet_name='単語', index=False)

    return test_dir


def run_test():
    """テスト実行"""
    print("=" * 60)
    print("単語照合システム テスト実行")
    print("=" * 60)

    try:
        # テストデータ作成
        test_dir = create_sample_data()

        # 設定
        config = DEFAULT_CONFIG.copy()
        config.update({
            "TEST_MODE": True,
            "MAX_WORKERS": 2,
            "OUT_DIR": str(test_dir / "output")
        })

        print("\n📁 テストデータ:")
        print(f"   ディレクトリ: {test_dir}")

        # 処理実行
        print("\n🚀 処理開始...")
        df_result = process(test_dir, None, None, config)

        print(f"\n✅ 処理完了: {len(df_result)}件")

        # 結果表示
        print("\n📊 結果サマリー:")
        match_summary = df_result['match_type'].value_counts()
        for match_type, count in match_summary.items():
            print(f"   {match_type}: {count}件")

        print("\n📋 詳細結果:")
        display_cols = ['screen_item', 'match_type', 'matched_term', 'matched_terms', 'local_top_score', 'reason']
        result_display = df_result[display_cols].copy()

        for i, row in result_display.iterrows():
            print(f"\n   {i+1}. {row['screen_item']}")
            print(f"      → {row['match_type']}: {row['matched_term'] or row['matched_terms'] or 'なし'}")
            score_str = f"{row['local_top_score']:.3f}" if pd.notna(row['local_top_score']) else 'N/A'
            print(f"      → スコア: {score_str}")
            print(f"      → 理由: {row['reason']}")

        # 出力ファイル確認
        output_file = Path(config["OUT_DIR"]) / "match_result.xlsx"
        if output_file.exists():
            print(f"\n💾 出力ファイル作成: {output_file}")

        print("\n✅ テスト成功！")

        return True

    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # クリーンアップ
        try:
            import shutil
            if 'test_dir' in locals():
                shutil.rmtree(test_dir, ignore_errors=True)
                print(f"\n🧹 テストデータ削除: {test_dir}")
        except Exception:
            pass


def test_individual_functions():
    """個別機能のテスト"""
    print("\n" + "=" * 40)
    print("個別機能テスト")
    print("=" * 40)

    from word import (
        zenkaku_hankaku_norm, local_similarity,
        top_k_candidates, phrase_candidates
    )

    # 1. 正規化テスト
    print("\n1. テキスト正規化テスト:")
    test_cases = [
        "融資・管理",
        "顧客　コード",
        "商品_番号",
        "項目（詳細）"
    ]
    for text in test_cases:
        normalized = zenkaku_hankaku_norm(text)
        print(f"   '{text}' → '{normalized}'")

    # 2. 類似度テスト
    print("\n2. 類似度計算テスト:")
    similarity_cases = [
        ("顧客コード", "顧客コード"),
        ("顧客コード", "顧客"),
        ("融資", "融資管理"),
        ("全く違う", "別の単語")
    ]
    for text1, text2 in similarity_cases:
        score = local_similarity(text1, text2)
        print(f"   '{text1}' vs '{text2}' → {score:.3f}")

    # 3. 候補生成テスト
    print("\n3. 候補生成テスト:")
    vocab_terms = ['顧客コード', '顧客名', '融資', '管理', '商品', '分類']

    test_queries = ["顧客コード", "融資管理", "商品分類"]
    for query in test_queries:
        candidates = top_k_candidates(query, vocab_terms, 3, 0.6)
        print(f"   '{query}'の候補:")
        for c in candidates[:3]:
            print(f"     - {c.term} (スコア: {c.score:.3f})")

        # 複合語候補もテスト
        phrase_cands = phrase_candidates(query, vocab_terms, 5, 0.6)
        if phrase_cands and len(phrase_cands) != len(candidates):
            print(f"   '{query}'の複合語候補:")
            for c in phrase_cands[:3]:
                print(f"     - {c.term} (スコア: {c.score:.3f})")

    print("\n✅ 個別機能テスト完了")


if __name__ == '__main__':
    print("🧪 単語照合システム - 総合テスト")

    # 個別機能テスト
    test_individual_functions()

    # 統合テスト
    success = run_test()

    if success:
        print("\n🎉 全テスト完了！")
    else:
        print("\n💥 テスト失敗")
        exit(1)