#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開発支援ツール - トップページ
"""
import streamlit as st

# ページ設定
st.set_page_config(
    page_title="開発支援ツール",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# メインタイトル
st.title("🛠️ 開発支援ツール")

# ヒーローセクション
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
    <h2 style='color: white; margin: 0 0 1rem 0;'>開発効率を向上させるツール集</h2>
    <p style='color: #e0e7ff; margin: 0; font-size: 1.1rem;'>
        左のサイドバーから利用したいツールを選択してください
    </p>
</div>
""", unsafe_allow_html=True)

# 利用可能なツール一覧
st.markdown("## 📋 利用可能なツール")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: white;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                height: 200px;'>
        <h3 style='color: #667eea; margin-top: 0;'>📝 単語照合ツール</h3>
        <p style='color: #4a5568; margin-bottom: 1rem;'>
            Excel単語帳との照合により、lowerCamelCase形式の物理名を自動提案します。
        </p>
        <p style='color: #718096; font-size: 0.9rem;'>
            ✅ 完全一致判定<br>
            ✅ 未登録語検出<br>
            ✅ LLM自動提案
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: white;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #f56565;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                height: 200px;'>
いJいち
れつさ        <h3 style='color: #f56565; margin-top: 0;'>🔍 ドメイン照合ツール</h3>
        <p style='color: #4a5568; margin-bottom: 1rem;'>
            画面項目に対応するドメインの存在チェックと新規ドメイン提案を行います。
        </p>
        <p style='color: #718096; font-size: 0.9rem;'>
            ✅ ドメイン存在チェック<br>
            ✅ ドメイン情報自動取得<br>
            ✅ 新規ドメイン提案
        </p>
    </div>
    """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div style='background: white;
#                 padding: 1.5rem;
#                 border-radius: 10px;
#                 border-left: 4px solid #48bb78;
#                 box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
#                 height: 200px;'>
#         <h3 style='color: #48bb78; margin-top: 0;'>🤖 PR-Agent</h3>
#         <p style='color: #4a5568; margin-bottom: 1rem;'>
#             プルリクエストの自動レビューとコード品質チェックを実施します。
#         </p>
#         <p style='color: #718096; font-size: 0.9rem;'>
#             ✅ コードレビュー<br>
#             ✅ 改善提案<br>
#             ✅ テスト提案
#         </p>
#     </div>
#     """, unsafe_allow_html=True)

st.markdown("---")

# 使い方ガイド
st.markdown("## 💡 使い方")

st.markdown("""
### 🚀 クイックスタート

1. **左のサイドバーからツールを選択**
   - 📝 単語照合ツール
   - 🔍 ドメイン照合ツール

2. **各ツールの画面で必要な情報を入力**
   - ファイルアップロード
   - パラメータ設定
   - API認証情報（単語照合ツールのみ必要）

3. **実行ボタンをクリック**
   - 処理進捗をリアルタイム確認
   - 結果をプレビュー
   - 必要に応じてダウンロード

### 📝 注意事項

- 単語照合ツールはAPI認証が必要です。事前にAPIキーを準備してください
- 大量データの処理には時間がかかる場合があります
- ファイルサイズの制限に注意してください
""")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    開発支援ツール v1.0 | Powered by Streamlit
</div>
""", unsafe_allow_html=True)
