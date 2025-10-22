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
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;'>
    <h1 style='color: white; margin: 0 0 1rem 0; font-size: 3rem; font-weight: 700;'>
        🛠️ ツール
    </h1>
    <p style='color: #e0e7ff; margin: 0; font-size: 1.3rem; font-weight: 300;'>
        開発をサポートするツール集
    </p>
</div>
""", unsafe_allow_html=True)

# タブでツールを切り替え
tab1, tab2, tab3= st.tabs([
    "🏠 ツール一覧",
    "📊 システム構成",
    "🛠️ 技術スタック"])

with tab1:
    st.header("利用可能なツール")
    st.markdown("用途に合わせて以下のツールを選択してください。")

    col_excel, col_domain, col_pr_agent = st.columns(3)

    with col_excel:
        st.markdown("""
        <div style='background: #e8f5e9; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #4caf50;'>
            <h4 style='color: #2e7d32; margin-top: 0;'>📝 Excel単語照合ツール</h4>
            <ul style='margin: 0;'>
                <li>Excelファイルの単語照合</li>
                <li>単語帳との突合チェック</li>
                <li>一致/不一致の色分け表示</li>
                <li>結果のCSV出力</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Excel単語照合ツールを開く", key="open_word_matching", type="primary", use_container_width=True):
            st.switch_page("pages/1_word_matching.py")

    with col_domain:
        st.markdown("""
        <div style='background: #fff3e0; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #ff9800;'>
            <h4 style='color: #e65100; margin-top: 0;'>🔍 ドメインチェックツール</h4>
            <ul style='margin: 0;'>
                <li>ドメイン名の検証</li>
                <li>URL形式のチェック</li>
                <li>DNSレコード確認</li>
                <li>バッチ処理対応</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 ドメインチェックツールを開く", key="open_domain_checker", type="primary", use_container_width=True):
            st.switch_page("pages/2_domain_check.py")

    with col_pr_agent:
        st.markdown("""
        <div style='background: #f3e5f5; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #9c27b0;'>
            <h4 style='color: #6a1b9a; margin-top: 0;'>🤖 PR-Agent</h4>
            <ul style='margin: 0;'>
                <li><strong>AIによる自動コードレビュー</strong><br/>
                    Gemini/OpenAIを使用した詳細な分析
                </li>
                <li><strong>ドメイン特化設定</strong><br/>
                    Java、Salesforce、DTO、Batch/Shell/SQL、API YAML
                </li>
                <li><strong>複数コマンド対応</strong><br/>
                    review、improve、describe、ask、add_docs
                </li>
                <li><strong>GitLab MRへの自動投稿</strong><br/>
                    レビュー結果を直接MRにコメント
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 PR-Agentを開く", key="open_pr_agent", type="primary", use_container_width=True):
            st.switch_page("pages/3_pr_agent.py")
        st.info("⏱️ 実行時間: 2～3時間程度（AIによる詳細な分析を実施）")

with tab2:
    st.header("システム構成")
    st.markdown("アプリ全体のつながりとPR-Agentの実行サイクルを図でまとめています。")

    st.subheader("🏗️ 全体アーキテクチャ")
    arch_diagram = """
    digraph Architecture {
        rankdir=LR;
        graph [fontname="MS Gothic", bgcolor="white", ranksep=1.0];
        node [shape=box, style="rounded,filled", color="#475569", fontname="MS Gothic", fontcolor="#1f2937", fillcolor="#ffffff"];
        edge [color="#475569", arrowsize=0.8, fontname="MS Gothic"];

        user [shape=oval, fillcolor="#fde68a", label="ユーザー\n(Webブラウザ)"];
        tracker [shape=note, fillcolor="#f3e8ff", label="usage_tracker.py"];
        docker [fillcolor="#ddd6fe", label="Docker\nコンテナ"];

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
            tool_word [label="Excel照合\n(word/word_matching)"];
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

        subgraph cluster_services {
            label="外部サービス";
            color="#fecaca";
            style="filled,rounded";
            fillcolor="#fee2e2";
            fontcolor="#1f2937";
            svc_gitlab [label="GitLab API"];
            svc_gemini [label="Gemini API"];
            svc_openai [label="OpenAI API"];
        }

        user -> app -> pages;
        app -> tracker [style=dashed, label="利用記録"];
        app -> data_env [style=dashed, label="環境変数"];
        pages -> tool_word;
        pages -> tool_domain;
        pages -> tool_pr;
        data_excel -> tool_word;
        data_excel -> tool_domain;
        data_configs -> tool_word [style=dashed];
        data_configs -> tool_domain [style=dashed];
        data_configs -> tool_pr;
        tool_pr -> docker;
        docker -> svc_gitlab;
        docker -> svc_gemini;
        docker -> svc_openai;
    }
    """
    st.graphviz_chart(arch_diagram)

    st.subheader("🔄 PR-Agent実行フロー")
    flow_diagram = """
    digraph PRAgentFlow {
        rankdir=LR;
        graph [fontname="MS Gothic", bgcolor="white", nodesep=1.0];
        node [shape=box, style="rounded,filled", color="#475569", fontname="MS Gothic", fontcolor="#1f2937", fillcolor="#ffffff"];
        edge [color="#475569", arrowsize=0.8, fontname="MS Gothic"];

        step1 [label="1. MR URL入力\n(ユーザー)"];
        step2 [label="2. 入力検証\nStreamlit UI"];
        step3 [label="3. 設定読込\nconfigs/*.toml"];
        step4 [label="4. Dockerで\nPR-Agent起動"];
        step5 [label="5. GitLabから\n差分を取得"];
        step6 [label="6. LLMへレビュー依頼\n(Gemini / OpenAI)"];
        step7 [label="7. 解析結果を整理"];
        step8 [label="8. GitLabに\nコメント投稿"];
        step9 [label="9. ログと結果を\nUIへ返却"];

        step1 -> step2 -> step3 -> step4 -> step5 -> step6 -> step7 -> step8 -> step9;

        gitlab [shape=ellipse, fillcolor="#fecaca", label="GitLab API"];
        llm [shape=ellipse, fillcolor="#bbf7d0", label="LLM"];
        logs [shape=note, fillcolor="#bfdbfe", label="実行ログ"];

        step5 -> gitlab [style=dashed, label="API呼び出し"];
        step6 -> llm [style=dashed, label="プロンプト送信"];
        step9 -> logs [style=dashed, label="画面表示"];
    }
    """
    st.graphviz_chart(flow_diagram)

    st.subheader("📁 ディレクトリ構成")
    st.code(
        """word-web/
├─ app.py            # ホーム+各タブ
├─ pages/            # サブページ群
│  ├─ 1_word_matching.py
│  ├─ 2_domain_check.py
│  ├─ 3_pr_agent.py
│  ├─ 4_about.py
│  └─ 99_admin.py
└─ requirements.txt  # Webアプリ依存

word/
├─ configs/          # PR-Agent用TOML
│  ├─ common.toml
│  └─ custom/…
├─ custom_llm_handler.py
└─ Excelデータなど
        """
    )

with tab3:
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