#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI用の共通設定モジュール
Streamlit UIヘルパー関数のみ（バックエンドロジックは tools/common/ に配置）
"""
import streamlit as st
import os
import sys
import json
from pathlib import Path

# 共通設定を読み込み
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common.config import _load_config_file


def render_api_credentials_section(title="🔑 API認証情報"):
    """
    API認証情報セクションを描画（config.yamlのデフォルト値を使用）

    Args:
        title: セクションタイトル

    Returns:
        tuple: (api_key, user_id)
    """
    st.subheader(title)

    # config.yamlからデフォルト値を取得
    cfg = _load_config_file()
    api_cfg = cfg.get("api", {})
    headers_json = api_cfg.get("headers_json", "{}")

    # デフォルトのAPI Key/User IDを抽出
    default_api_key = ""
    default_user_id = ""
    try:
        headers = json.loads(headers_json)
        default_api_key = headers.get("api-key", "")
        default_user_id = headers.get("apim-user-id", "")
    except:
        pass

    # 環境変数で上書き可能
    default_api_key = os.getenv("OPENAI_API_KEY", default_api_key)
    default_user_id = os.getenv("APIM_USER_ID", default_user_id)

    api_key = st.text_input(
        "Azure OpenAI API Key",
        value=default_api_key,
        type="password",
        help="Azure OpenAI APIキー（config.yamlのデフォルト値を使用）"
    )

    user_id = st.text_input(
        "User ID (apim-user-id)",
        value=default_user_id,
        help="API Management のユーザID（config.yamlのデフォルト値を使用）"
    )

    return api_key, user_id


def get_custom_prompt(placeholder_text, help_text="追加の指示やコンテキスト情報"):
    """
    カスタムプロンプト入力欄を取得する共通関数

    Args:
        placeholder_text: プレースホルダーテキスト
        help_text: ヘルプテキスト

    Returns:
        str: カスタムプロンプト
    """
    custom_prompt = st.text_area(
        "カスタムプロンプト（オプション）",
        placeholder=placeholder_text,
        height=150,
        help=help_text
    )

    return custom_prompt


def get_llm_settings(default_max_tokens=500, default_temperature=0.2):
    """
    LLM設定を取得する共通関数

    Args:
        default_max_tokens: デフォルトのMax Tokens
        default_temperature: デフォルトのTemperature

    Returns:
        dict: LLM設定
    """
    max_tokens = st.number_input(
        "Max Tokens",
        value=default_max_tokens,
        min_value=100,
        max_value=1500,
        help="LLMが生成する最大トークン数"
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=default_temperature,
        step=0.1,
        help="生成の多様性（0に近いほど安定）"
    )

    return {
        "max_tokens": max_tokens,
        "temperature": temperature
    }


# カスタムプロンプトのプレースホルダーテンプレート
CUSTOM_PROMPT_TEMPLATES = {
    "word_matching": """例:
# 命名規則の追加ルール
- 略語は大文字3文字以内
- 日付は必ず Date で終わる

# 業務固有ルール
- 顧客関連は必ず customer で始める
- 注文関連は必ず order で始める
""",

    "domain_check": """例:
# ドメイン選定ルール
- 金額は必ず金額ドメインを使用
- 日付は必ず日付ドメインを使用

# プロジェクト固有ルール
- 顧客コードは10桁固定
- 商品コードは8桁固定
""",

    "pr_agent": """例:
# 重点チェック項目
- XSS脆弱性を重点的にチェック
- パフォーマンスへの影響を確認

# プロジェクト固有ルール
- インデント: 4スペース
- 命名規則: snake_case

# 注意事項
- この機能は本番環境で使用される重要な機能です
"""
}
