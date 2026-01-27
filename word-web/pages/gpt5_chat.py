#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-5 チャットページ
シンプルなチャットUIから GPT-5 (OpenAI/Azure Proxy) に会話を投げる
"""
import json
import os
import time
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


def _call_gpt5(
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    reasoning_effort: str,
    max_retries: int = 3,
) -> str:
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
    payload["reasoning_effort"] = reasoning_effort or "high"
    payload["verbosity"] = "high"

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                url,
                headers=_load_openai_headers(),
                json=payload,
                timeout=120,
            )
        except requests.exceptions.Timeout as exc:
            last_error = RuntimeError("GPT-5 APIがタイムアウトしました。少し待って再試行してください。")
        except requests.exceptions.RequestException as exc:
            last_error = RuntimeError(f"GPT-5 APIリクエストに失敗しました: {exc}")
        else:
            if response.ok:
                break
            if response.status_code == 429 and attempt < max_retries:
                retry_after = response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = min(int(retry_after), 30)
                else:
                    delay = min(2 ** attempt, 10)
                time.sleep(delay)
                continue
            detail = response.text[:200]
            raise RuntimeError(
                f"GPT-5 APIがエラーを返しました (HTTP {response.status_code}): {detail}"
            )
        if attempt < max_retries:
            time.sleep(min(2 ** attempt, 10))
        else:
            raise last_error

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
st.title("💬 GPT-5 チャット（API疎通検証用）")
st.caption("APIへの疎通確認や動作チェックを行うための試験用チャットです。")
st.markdown(
    """
    <style>
    .user-row {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin: 0.35rem 0;
    }
    .user-bubble {
        background: linear-gradient(135deg, #93c5fd, #bfdbfe);
        color: #0f172a;
        padding: 0.75rem 1rem;
        border-radius: 1rem 0.4rem 1rem 1rem;
        max-width: 65%;
        display: inline-block;
        white-space: pre-wrap;
        word-break: break-word;
        text-align: left;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.15);
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
    max_tokens = 8192
    reasoning_effort = "high"

    if st.button("🧹 会話をリセット", use_container_width=True):
        st.session_state.chat_history = []
        track_usage(action="会話リセット", tool_name="GPT-5チャット")
        st.rerun()

# チャット履歴（ユーザーは右寄せ）をレンダリング
_render_chat_history(st.session_state.chat_history)

# 入力欄: Streamlit標準のチャット入力を使用して常に下部に固定
user_prompt = st.chat_input("メッセージを入力")

# ユーザーメッセージがあれば先に履歴に追加し、このターンで即描画
if user_prompt:
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    _render_user_message(user_prompt)

    # API呼び出し（入力後すぐに実行）
    messages_payload = [{"role": "system", "content": st.session_state.system_prompt}]
    messages_payload.extend(st.session_state.chat_history)

    with st.spinner("GPT-5 が考えています…"):
        try:
            reply = _call_gpt5(messages_payload, temperature, max_tokens, reasoning_effort)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            track_usage(action="メッセージ送信", tool_name="GPT-5チャット")
        except Exception as exc:
            error_msg = f"❌ エラー: {exc}"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            track_usage(action="エラー", tool_name="GPT-5チャット", username=str(exc))
