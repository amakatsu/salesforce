#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理者ダッシュボード - 利用者数と時間
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter

# 認証チェック（最優先）
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# 認証されていない場合は即座に停止（インポート前）
if not st.session_state.admin_authenticated:
    # ページ設定（認証前）
    st.set_page_config(
        page_title="管理者ログイン",
        page_icon="🔐",
        layout="centered"
    )

    # モダンなログイン画面
    st.markdown("""
    <style>
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin: 2rem auto;
            max-width: 400px;
        }
        .login-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .login-subtitle {
            color: #e0e7ff;
            text-align: center;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="login-title">管理者ログイン</h2>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">このページは管理者専用です</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    password = st.text_input("パスワード", type="password", placeholder="パスワードを入力してください")

    if st.button("🚀 ログイン", type="primary", use_container_width=True):
        ADMIN_PASSWORD = "admin123"

        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ パスワードが間違っています")

    st.stop()

# 認証済み - ここからインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from usage_tracker import get_usage_stats, clear_history, track_usage

# ページ設定（認証後）
st.set_page_config(
    page_title="管理者ダッシュボード",
    page_icon="📊",
    layout="wide"
)

# カスタムCSS（モダンなデザイン）
st.markdown("""
<style>
    /* グローバルスタイル */
    .main {
        background-color: #f8fafc;
    }

    /* ヘッダースタイル */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }

    .dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }

    .dashboard-subtitle {
        color: #e0e7ff;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* メトリックカード */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* テーブルスタイル */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }

    /* セクションヘッダー */
    .section-header {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-left: 1rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ページ訪問記録（初回のみ）
if 'visited_admin' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="管理者ダッシュボード")
    st.session_state.visited_admin = True

# ヘッダー
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📊 管理者ダッシュボード</h1>
    <p class="dashboard-subtitle">システムの利用状況をリアルタイムで監視</p>
</div>
""", unsafe_allow_html=True)

# ログアウトボタン（右上）
col_logout1, col_logout2 = st.columns([6, 1])
with col_logout2:
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

# 統計情報取得
stats = get_usage_stats()

# KPIメトリクス
st.markdown('<h2 class="section-header">📈 主要指標</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# 総アクション数
with col1:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">総アクション数</p>
    </div>
    """.format(stats['total_actions']), unsafe_allow_html=True)

# ツール別集計
tool_counts = Counter(record.get('tool_name', '-') for record in stats['history'])
page_visits = sum(1 for record in stats['history'] if record['action'] == 'ページ訪問')
button_clicks = sum(1 for record in stats['history'] if record['action'] == '実行ボタン押下')

with col2:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">ページ訪問数</p>
    </div>
    """.format(page_visits), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">実行ボタン押下数</p>
    </div>
    """.format(button_clicks), unsafe_allow_html=True)

with col4:
    unique_tools = len([tool for tool in tool_counts.keys() if tool != '-'])
    st.markdown("""
    <div class="metric-card">
        <p class="metric-value">{}</p>
        <p class="metric-label">利用ツール数</p>
    </div>
    """.format(unique_tools), unsafe_allow_html=True)

st.markdown("---")

# 時系列の利用状況（折れ線グラフ）
if stats['history']:
    st.markdown('<h2 class="section-header">📈 時系列の利用状況</h2>', unsafe_allow_html=True)

    # 時間ごとのアクション数を集計
    time_series_data = {}
    for record in stats['history']:
        timestamp = record['timestamp']
        # 時間単位で丸める（分・秒を切り捨て）
        hour_key = timestamp.replace(minute=0, second=0, microsecond=0)

        if hour_key not in time_series_data:
            time_series_data[hour_key] = 0
        time_series_data[hour_key] += 1

    # DataFrameに変換してソート
    if time_series_data:
        df_timeseries = pd.DataFrame([
            {'時刻': time_key, 'アクション数': count}
            for time_key, count in sorted(time_series_data.items())
        ])

        # 折れ線グラフを表示
        st.line_chart(df_timeseries.set_index('時刻'))

        # 詳細情報を表示
        with st.expander("📊 時間別詳細データを見る"):
            df_timeseries['時刻'] = df_timeseries['時刻'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_timeseries, use_container_width=True, hide_index=True)

st.markdown("---")

# ツール別利用状況
if stats['history']:
    st.markdown('<h2 class="section-header">🛠️ ツール別利用状況</h2>', unsafe_allow_html=True)

    # ツール別のアクション数を集計（'-'を除外）
    tool_data = []
    for tool_name, count in tool_counts.most_common():
        if tool_name != '-':
            tool_page_visits = sum(1 for record in stats['history']
                                   if record.get('tool_name') == tool_name and record['action'] == 'ページ訪問')
            tool_button_clicks = sum(1 for record in stats['history']
                                      if record.get('tool_name') == tool_name and record['action'] == '実行ボタン押下')
            tool_data.append({
                'ツール名': tool_name,
                '総アクション数': count,
                'ページ訪問': tool_page_visits,
                '実行回数': tool_button_clicks
            })

    if tool_data:
        df_tools = pd.DataFrame(tool_data)

        # ツール別アクション数の棒グラフ
        st.bar_chart(df_tools.set_index('ツール名')['総アクション数'])

        # 詳細テーブル
        st.dataframe(df_tools, use_container_width=True, hide_index=True)

st.markdown("---")

# アクション履歴
st.markdown('<h2 class="section-header">⏰ アクション履歴（最新50件）</h2>', unsafe_allow_html=True)

if stats['history']:
    # データ整形
    history_data = []
    for i, record in enumerate(reversed(stats['history'][-50:]), 1):  # 最新50件
        # アクションタイプに応じた絵文字
        action_emoji = {
            'ページ訪問': '👁️',
            '実行ボタン押下': '▶️'
        }.get(record['action'], '📝')

        history_data.append({
            'No': i,
            'アクション': f"{action_emoji} {record['action']}",
            'ツール': record.get('tool_name', '-'),
            'ユーザー': record.get('username', '匿名'),
            '実行時刻': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
else:
    st.info("📭 まだ履歴がありません")

st.markdown("---")

# 管理ボタン
st.markdown('<h2 class="section-header">⚙️ 管理機能</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 データを更新", type="primary", use_container_width=True):
        st.rerun()

with col2:
    if st.button("📥 CSVエクスポート", use_container_width=True):
        if stats['history']:
            export_data = []
            for record in stats['history']:
                export_data.append({
                    'アクション': record['action'],
                    'ツール': record.get('tool_name', '-'),
                    'ユーザー': record.get('username', '匿名'),
                    '実行時刻': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                })

            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"usage_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("エクスポートするデータがありません")

with col3:
    if st.button("🗑️ 履歴をクリア", type="secondary", use_container_width=True):
        clear_history()
        st.success("✅ 履歴をクリアしました")
        st.rerun()

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 0.9em; padding: 2rem;'>
    管理者ダッシュボード v2.0 | Powered by Streamlit 🚀
</div>
""", unsafe_allow_html=True)
