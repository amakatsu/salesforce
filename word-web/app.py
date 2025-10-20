#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開発支援ツール - トップページ
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 利用トラッキングをインポート
sys.path.insert(0, str(Path(__file__).parent))
from usage_tracker import track_usage

# ページ設定
st.set_page_config(
    page_title="ツール",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 利用記録（初回訪問時のみ）
if 'visited_home' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="ホーム")
    st.session_state.visited_home = True

# メインタイトル
st.title("🛠️ ツール")

# ヒーローセクション
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
    <h2 style='color: white; margin: 0 0 1rem 0;'>ツール集</h2>
    <p style='color: #e0e7ff; margin: 0; font-size: 1.1rem;'>
        左のサイドバーから利用したいツールを選択してください
    </p>
</div>
""", unsafe_allow_html=True)