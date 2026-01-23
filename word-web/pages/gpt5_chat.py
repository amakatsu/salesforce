#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-5 チャットページ
シンプルなチャットUIから GPT-5 (OpenAI/Azure Proxy) に会話を投げる
"""
import json
import os
from html import escape
from pathlib import Path
from typing import List, Dict

import streamlit as st

import requests
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

def _render_user_message(content: str) -> None:
    """ユーザー側メッセージを右寄せで描画"""
    safe = escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="user-row">
            <div class="user-bubble">{safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chat_history(history: List[Dict[str, str]]) -> None:
    """これまでの履歴を描画"""
    for message in history:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        if role == "user":
            _render_user_message(content)
        else:
            with st.chat_message(role):
                st.markdown(content)


# =============================================================================
# 設定ヘルパー
# =============================================================================

def _load_openai_headers() -> Dict[str, str]:
    """OPENAI_HEADERS_JSON をヘッダー辞書へ変換"""
    headers = {"Content-Type": "application/json"}
    headers_json = os.getenv("OPENAI_HEADERS_JSON", "")
    if headers_json:
        try:
            parsed = json.loads(headers_json)
            headers.update(parsed)
        except json.JSONDecodeError:
            st.warning("OPENAI_HEADERS_JSON をパースできませんでした。")
    return headers


def _call_gpt5(messages: List[Dict[str, str]], temperature: float, max_tokens: int, reasoning_effort: str) -> str:
    """GPT-5 へチャットリクエストを送る"""
    base_url = os.getenv("OPENAI_BASE_URL", "")
    api_path = os.getenv("OPENAI_PATH", "/api/curl/v2/chat/")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5")

    if not base_url:
        raise ValueError("OPENAI_BASE_URL が設定されていません (.env)")

    url = base_url.rstrip("/") + api_path
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
        "n": 1,
    }
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    try:
        response = requests.post(
            url,
            headers=_load_openai_headers(),
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("GPT-5 APIがタイムアウトしました。少し待って再試行してください。") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"GPT-5 APIリクエストに失敗しました: {exc}") from exc

    if not response.ok:
        detail = response.text[:200]
        raise RuntimeError(
            f"GPT-5 APIがエラーを返しました (HTTP {response.status_code}): {detail}"
        )

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


# =============================================================================
# Streamlit UI
# =============================================================================

st.set_page_config(page_title="GPT-5 チャット", page_icon="💬", layout="wide")
st.title("💬 GPT-5 チャット")
st.caption("簡単な質問やテキスト生成を GPT-5 に依頼できます。")
st.markdown(
    """
    <style>
    .user-row {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin: 0.25rem 0;
    }
    .user-bubble {
        background-color: rgba(126, 187, 253, 0.25);
        color: inherit;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        max-width: 70%;
        white-space: pre-wrap;
        word-break: break-word;
        margin-left: auto;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
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
if "pending_response" not in st.session_state:
    st.session_state.pending_response = False
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None

track_usage(action="ページ訪問", tool_name="GPT-5チャット")

with st.sidebar:
    st.subheader("⚙️ 設定")
    st.session_state.system_prompt = st.text_area(
        "システムプロンプト",
        value=st.session_state.system_prompt,
        height=120,
        help="モデルへの基本指示。デフォルトでは日本語で回答するよう指定しています。",
    )
    temperature = st.slider("温度 (創造性)", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.slider("最大トークン数", 256, 4096, 1024, 64)
    reasoning_effort = st.selectbox(
        "reasoning_effort",
        options=["", "medium", "high"],
        index=1,
        help="空欄の場合は送信しません。",
    )

    if st.button("🧹 会話をリセット", use_container_width=True):
        st.session_state.chat_history = []
        track_usage(action="会話リセット", tool_name="GPT-5チャット")
        st.experimental_rerun()

# 過去のメッセージを表示（ユーザーは右寄せ）
_render_chat_history(st.session_state.chat_history)

if st.session_state.pending_response:
    st.info("GPT-5 からの返信を待機中です…", icon="⏳")

prompt = st.chat_input("メッセージを入力", disabled=st.session_state.pending_response)

if prompt and not st.session_state.pending_response:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.queued_prompt = prompt
    st.session_state.pending_response = True
    st.experimental_rerun()

if st.session_state.pending_response and st.session_state.queued_prompt:
    placeholder = st.empty()
    with placeholder.container():
        with st.chat_message("assistant"):
            st.markdown("_GPT-5 が考えています…_")

    messages_payload = [{"role": "system", "content": st.session_state.system_prompt}]
    messages_payload.extend(st.session_state.chat_history)

    try:
        reply = _call_gpt5(messages_payload, temperature, max_tokens, reasoning_effort)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        placeholder.empty()
        with st.chat_message("assistant"):
            st.markdown(reply)
        track_usage(action="メッセージ送信", tool_name="GPT-5チャット")
    except Exception as exc:
        placeholder.empty()
        with st.chat_message("assistant"):
            st.error(f"❌ エラー: {exc}")
        track_usage(action="エラー", tool_name="GPT-5チャット", username=str(exc))
    finally:
        st.session_state.pending_response = False
        st.session_state.queued_prompt = None
