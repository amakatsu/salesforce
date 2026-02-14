#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-5 チャットページ
シンプルなチャットUIから GPT-5 (OpenAI/Azure Proxy) に会話を投げる
"""
import json
import os
import time
from pathlib import Path
from typing import List, Dict

import streamlit as st

from word.ai_handlers.common_llm import (
    build_headers,
    build_chat_payload,
    post_chat_requests,
    load_env_settings,
)
from dotenv import load_dotenv

# .env をロード
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# 利用トラッキング
from pages.util.usage_tracker import track_usage  # noqa: E402


# =============================================================================
# 表示用ヘルパー
# =============================================================================

def _render_chat_history(history: List[Dict[str, str]]) -> None:
    """これまでの履歴を描画"""
    for message in history:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        with st.chat_message(role):
            st.markdown(content)


# =============================================================================
# 設定ヘルパー
# =============================================================================

def _call_gpt5(
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    reasoning_effort: str,
    max_retries: int = 3,
    on_retry=None,
) -> str:
    """GPT-5 へチャットリクエストを送る"""
    env_cfg = load_env_settings()
    base_url = env_cfg["base_url"]
    api_path = env_cfg["path"]
    model_name = env_cfg["model"] or "gpt-5"

    if not base_url:
        raise ValueError("OPENAI_BASE_URL が設定されていません (.env)")

    url = base_url.rstrip("/") + api_path
    headers = build_headers(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        user_id=None,
        custom_headers=None,
        extra_headers_json=env_cfg["headers_json"],
        send_auth=env_cfg["send_auth"],
    )
    payload = build_chat_payload(
        messages=messages,
        model=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        reasoning_effort=reasoning_effort or "high",
        verbosity="high",
    )

    def _on_retry(attempt, total, delay):
        if on_retry:
            on_retry(attempt, total, delay)

    data = post_chat_requests(
        url,
        headers,
        payload,
        timeout=120,
        verify_ssl=True,
        proxies=None,
    )
    return data["choices"][0]["message"]["content"]

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("GPT-5 API応答のJSON解析に失敗しました") from exc

    choices = data.get("choices")
    if not choices:
        raise RuntimeError("GPT-5 API応答に choices フィールドがありません")

    message = choices[0].get("message", {})
    content = message.get("content")
    if not content:
        raise RuntimeError("GPT-5 API応答にメッセージ内容が含まれていません")

    return content


def _build_messages_payload(history: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
    """APIに渡すメッセージ配列を構築（systemを先頭に付与）"""
    messages = [{"role": "system", "content": system_prompt}]
    for message in history:
        role = message.get("role")
        content = message.get("content", "")
        if not role or role == "system":
            continue
        if content == "":
            continue
        messages.append({"role": role, "content": content})
    return messages


# =============================================================================
# Streamlit UI
# =============================================================================

st.set_page_config(page_title="GPT-5 チャット", page_icon="💬", layout="wide")
st.title("💬 GPT-5 チャット（API疎通検証用）")
st.caption("APIへの疎通確認や動作チェックを行うための試験用チャットです。")
st.markdown(
    """
    <style>
    [data-testid="stChatMessage"] {
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = (
        "You are GPT-5, a helpful assistant for Japanese developers. Reply in Japanese unless code or"
        " technical keywords require English."
    )
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""
track_usage(action="ページ訪問", tool_name="GPT-5チャット")

with st.sidebar:
    st.subheader("⚙️ 設定")
    st.session_state.system_prompt = st.text_area(
        "システムプロンプト",
        value=st.session_state.system_prompt,
        height=120,
        help="モデルへの基本指示。デフォルトでは日本語で回答するよう指定しています。",
    )
    temperature = 1.0
    max_tokens = 128000
    reasoning_effort = "high"

    if st.button("🧹 会話をリセット", use_container_width=True):
        st.session_state.chat_history = []
        track_usage(action="会話リセット", tool_name="GPT-5チャット")
        st.rerun()

# チャット履歴（最小装飾）
_render_chat_history(st.session_state.chat_history)

# リトライ状況表示
retry_status = st.empty()

# 入力欄: Streamlit標準のチャット入力を使用して常に下部に固定
user_prompt = None
if st.session_state.is_processing:
    st.caption("⏳ 応答待ち…")
else:
    user_prompt = st.chat_input("メッセージを入力")

# 送信時: 履歴に追加して次のrerunでAPI呼び出し
if user_prompt:
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    st.session_state.pending_prompt = user_prompt
    st.session_state.is_processing = True
    st.rerun()

# 送信済みプロンプトがあればAPI応答まで取得
if st.session_state.is_processing and st.session_state.pending_prompt:
    messages_payload = _build_messages_payload(
        st.session_state.chat_history, st.session_state.system_prompt
    )

    def _on_retry(attempt: int, max_retries: int, delay: int) -> None:
        retry_status.info(f"⚠️ 429/一時エラーのため再試行 {attempt}/{max_retries}（{delay}秒後）")

    with st.spinner("GPT-5 が考えています…"):
        try:
            reply = _call_gpt5(
                messages_payload,
                temperature,
                max_tokens,
                reasoning_effort,
                on_retry=_on_retry,
            )
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            track_usage(action="メッセージ送信", tool_name="GPT-5チャット")
        except Exception as exc:
            error_msg = f"❌ エラー: {exc}"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            track_usage(action="エラー", tool_name="GPT-5チャット", username=str(exc))
        finally:
            retry_status.empty()
            st.session_state.is_processing = False
            st.session_state.pending_prompt = ""
            st.rerun()
