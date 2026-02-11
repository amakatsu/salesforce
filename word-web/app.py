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
from pages.util.usage_tracker import track_usage
from pages.util import layout_utils

# ページ設定
st.set_page_config(
    page_title="ツール",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
layout_utils.apply_fullscreen_layout()

# 利用記録（初回訪問時のみ）
if 'visited_home' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="ホーム")
    st.session_state.visited_home = True

# メインタイトル
st.title("🛠️ ツール")

st.caption("開発をサポートするツール集")

# タブでツールを切り替え
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 ツール一覧",
    "📊 システム構成",
    "🔄 PR-Agent実行フロー",
    "🛠️ 技術スタック"])

CARD_STYLE = "padding:1.2rem;border-radius:10px;border-left:5px solid"

with tab1:
    st.header("利用可能なツール")
    st.markdown("用途に合わせて以下のツールを選択してください。")

    col_excel, col_domain, col_pr_agent = st.columns(3)

    with col_excel:
        st.markdown(
            f"""
            <div style='background:#e8f5e9;{CARD_STYLE};border-color:#4caf50'>
                <h4 style='margin:0 0 .5rem 0;'>📝 単語マッチングツール</h4>
                <ul>
                    <li>Excelファイルの単語照合</li>
                    <li>単語帳との突合チェック</li>
                    <li>一致/不一致の色分け表示</li>
                    <li>結果のCSV出力</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📝 単語マッチングツールを開く", key="open_word_matching", type="primary", use_container_width=True):
            st.switch_page("pages/word_matching.py")

    with col_domain:
        st.markdown(
            f"""
            <div style='background:#fff3e0;{CARD_STYLE};border-color:#ff9800'>
                <h4 style='margin:0 0 .5rem 0;'>🔍 ドメインチェックツール</h4>
                <ul>
                    <li>ドメイン名の検証</li>
                    <li>URL形式のチェック</li>
                    <li>DNSレコード確認</li>
                    <li>バッチ処理対応</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔍 ドメインチェックツールを開く", key="open_domain_checker", type="primary", use_container_width=True):
            st.switch_page("pages/domain_checker.py")

    with col_pr_agent:
        st.markdown(
            f"""
            <div style='background:#f3e5f5;{CARD_STYLE};border-color:#9c27b0'>
                <h4 style='margin:0 0 .5rem 0;'>🤖 PR-Agent</h4>
                <ul>
                    <li><strong>AIによる自動コードレビュー</strong></li>
                    <li><strong>ドメイン特化設定</strong></li>
                    <li><strong>複数コマンド対応</strong></li>
                    <li><strong>GitLab MRへの自動投稿</strong></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🤖 PR-Agentを開く", key="open_pr_agent", type="primary", use_container_width=True):
            st.switch_page("pages/pr_agent.py")
        st.info("⏱️ 実行時間: 2～3分程度（MRのサイズによって変動）")

    st.markdown("### 🤖 AIアシスタント")
    chat_col, _, _ = st.columns([1, 1, 1])
    with chat_col:
        st.markdown("""
        <div style='background: #e0f2fe; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #0284c7;'>
            <h4 style='color: #0369a1; margin-top: 0;'>💬 GPT-5 チャット</h4>
            <ul style='margin: 0;'>
                <li>API疎通や挙動確認向けの試験用チャット</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬 GPT-5 チャットを開く", key="open_gpt5_chat", type="primary", use_container_width=True):
            st.switch_page("pages/gpt5_chat.py")

with tab2:
    st.header("システム構成")
    st.markdown("アプリ全体のつながりとPR-Agentの実行サイクルを図でまとめています。")

    st.subheader("🏗️ 全体アーキテクチャ")
    arch_diagram = """
    digraph Architecture {
        rankdir=LR;
        graph [fontname="MS Gothic", bgcolor="white", ranksep=1.5, compound=true];
        node [shape=box, style="rounded,filled", color="#475569", fontname="MS Gothic", fontcolor="#1f2937", fillcolor="#ffffff"];
        edge [color="#475569", arrowsize=0.8, fontname="MS Gothic", penwidth=2.0];

        user [shape=oval, fillcolor="#fde68a", label="ユーザー\n(Webブラウザ)"];

        subgraph cluster_ui {
            label="Streamlit UI";
            color="#bfdbfe";
            style="filled,rounded";
            fillcolor="#e0f2fe";
            fontcolor="#1f2937";
            app [label="app.py\nホームタブ"];
            pages [label="pages/\nサブページ"];
        }

        subgraph cluster_tools {
            label="ツール処理";
            color="#bbf7d0";
            style="filled,rounded";
            fillcolor="#dcfce7";
            fontcolor="#1f2937";
            tool_word [label="単語マッチング\n(word/word_matching)"];
            tool_domain [label="ドメインチェック\n(word/domain_check)"];
            tool_pr [label="PR-Agent実行\n(word/pr_agent)"];
        }

        subgraph cluster_data {
            label="データ / 設定";
            color="#fde68a";
            style="filled,rounded";
            fillcolor="#fef3c7";
            fontcolor="#1f2937";
            data_env [label=".env / Secrets"];
            data_configs [label="configs/*.toml"];
            data_excel [label="Excel / CSV"];
        }

        subgraph cluster_git {
            label="Git サービス";
            color="#fecaca";
            style="filled,rounded";
            fillcolor="#fee2e2";
            fontcolor="#1f2937";
            svc_gitlab [label="GitLab API"];
        }

        subgraph cluster_llm {
            label="LLM サービス";
            color="#c7d2fe";
            style="filled,rounded";
            fillcolor="#e0e7ff";
            fontcolor="#1f2937";
            svc_gemini [label="Gemini API"];
            svc_openai [label="OpenAI API"];
        }

        // クラスター間の接続（矢印を大幅削減）
        user -> app [lhead=cluster_ui, label="操作"];
        app -> data_excel [ltail=cluster_ui, lhead=cluster_data, label="アップロード"];
        app -> tool_word [ltail=cluster_ui, lhead=cluster_tools, label="実行"];
        data_env -> tool_word [ltail=cluster_data, lhead=cluster_tools, style=dashed, label="設定読込"];
        tool_pr -> svc_gitlab [ltail=cluster_tools, lhead=cluster_git, label="API"];
        tool_pr -> svc_gemini [ltail=cluster_tools, lhead=cluster_llm, label="AI解析"];
    }
    """
    st.graphviz_chart(arch_diagram)

with tab3:
    st.header("PR-Agent実行フロー")
    st.markdown("PR-Agentがどのように動作するか、3つの層に分けて説明します。")
    st.caption("💡 紫色=UI層 / 青色=自前バックエンド / 緑色=OSS(PR-Agent)")

    flow_diagram = """
    digraph PRAgentFlow {
        rankdir=TB;
        graph [fontname="MS Gothic", bgcolor="white"];
        node [shape=box, style="rounded,filled", color="#475569", fontname="MS Gothic", fontcolor="#1f2937"];
        edge [color="#475569", arrowsize=0.8, fontname="MS Gothic"];

        subgraph cluster_ui {
            label="🖥️ UI層 (Streamlit)";
            style="filled,rounded";
            color="#a855f7";
            fillcolor="#f3e8ff";
            fontcolor="#6b21a8";

            step1 [label="① ユーザーがMR URL入力", fillcolor="#e9d5ff"];
            step2 [label="② 設定ファイル選択/編集", fillcolor="#e9d5ff"];
            step3 [label="③ AIプロバイダー選択", fillcolor="#e9d5ff"];
            step9 [label="⑨ ログ・結果をUI表示", fillcolor="#e9d5ff"];
        }

        subgraph cluster_backend {
            label="🔧 自前バックエンド";
            style="filled,rounded";
            color="#3b82f6";
            fillcolor="#dbeafe";
            fontcolor="#1e40af";

            step4 [label="④ 設定適用・環境構築", fillcolor="#bfdbfe"];
            step6 [label="⑥ カスタムLLMハンドラー\n(社内LLM対応)", fillcolor="#bfdbfe"];
        }

        subgraph cluster_oss {
            label="📦 OSS (PR-Agent)";
            style="filled,rounded";
            color="#10b981";
            fillcolor="#d1fae5";
            fontcolor="#065f46";

            step5 [label="⑤ GitLabからMR情報取得", fillcolor="#bbf7d0"];
            step7 [label="⑦ レビュー結果を整形", fillcolor="#bbf7d0"];
            step8 [label="⑧ GitLabにコメント投稿", fillcolor="#bbf7d0"];
        }

        gitlab [shape=cylinder, fillcolor="#fecaca", label="GitLab"];
        ai [shape=ellipse, fillcolor="#c7d2fe", label="AI\n(Gemini/OpenAI)"];

        step1 -> step2 -> step3;
        step3 -> step4 [label="入力データ"];
        step4 -> step5 [label="起動"];
        step5 -> gitlab [label="API呼び出し", style=dashed];
        gitlab -> step5 [label="差分返却", style=dashed];
        step5 -> step6 [label="差分データ"];
        step6 -> ai [label="プロンプト送信", style=dashed];
        ai -> step6 [label="解析結果", style=dashed];
        step6 -> step7 [label="AIレスポンス"];
        step7 -> step8;
        step8 -> gitlab [label="コメント投稿", style=dashed];
        step8 -> step9 [label="結果データ"];
    }
    """
    st.graphviz_chart(flow_diagram)

with tab4:
    st.header("技術スタック")
    st.markdown("主要コンポーネントをカテゴリ別に整理しています。")

    tech_diagram = """
    digraph TechStack {
        graph [fontname="MS Gothic", ranksep=1.2];
        node [shape=box, style="rounded,filled", color="#94a3b8", fontname="MS Gothic", fontcolor="#1f2937"];
        edge [color="#94a3b8", style=dashed];

        subgraph cluster_frontend {
            label="フロントエンド";
            color="#bfdbfe";
            streamlit [label="Streamlit 1.32.0", fillcolor="#dbeafe"];
            graphviz_tool [label="Graphviz", fillcolor="#dbeafe"];
        }

        subgraph cluster_backend {
            label="バックエンド";
            color="#ddd6fe";
            python [label="Python 3.11", fillcolor="#ede9fe"];
            pandas [label="pandas 2.2.1", fillcolor="#ede9fe"];
            openpyxl [label="openpyxl 3.1.2", fillcolor="#ede9fe"];
        }

        subgraph cluster_ai {
            label="自動化・AI";
            color="#bbf7d0";
            pr_agent [label="PR-Agent (Codium AI)", fillcolor="#dcfce7"];
            gemini [label="Google Gemini API", fillcolor="#dcfce7"];
            openai [label="OpenAI API", fillcolor="#dcfce7"];
        }

        subgraph cluster_infra {
            label="インフラ";
            color="#fde68a";
            docker [label="Docker", fillcolor="#fef3c7"];
            gitlab [label="GitLab API", fillcolor="#fef3c7"];
            dotenv [label="python-dotenv", fillcolor="#fef3c7"];
        }

        streamlit -> graphviz_tool;
        graphviz_tool -> python;
        python -> pandas;
        python -> openpyxl;
        pr_agent -> gemini;
        pr_agent -> openai;
        pr_agent -> gitlab;
        dotenv -> python;
        docker -> pr_agent;
    }
    """
    st.graphviz_chart(tech_diagram)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            """
            **主要ライブラリ**
            - Streamlit: UIフレームワーク
            - pandas / openpyxl: Excel処理
            - python-dotenv: 環境変数管理
            - Graphviz: st.graphviz_chart で図表描画
            """
        )

    with col_right:
        st.markdown(
            """
            **プラットフォーム / サービス**
            - Docker: 実行環境の統一
            - GitLab API: MR情報取得・投稿
            - Gemini / OpenAI API: LLMレビュー
            - PR-Agent: AIコードレビュー自動化
            """
        )

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 2rem;'>
    <p style='margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;'>Version 1.0.0</p>
</div>
""", unsafe_allow_html=True)
