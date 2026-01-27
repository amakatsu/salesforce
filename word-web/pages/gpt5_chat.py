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
    on_retry=None,
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
                if on_retry:
                    on_retry(attempt + 1, max_retries, delay)
                time.sleep(delay)
                continue
            detail = response.text[:200]
            raise RuntimeError(
                f"GPT-5 APIがエラーを返しました (HTTP {response.status_code}): {detail}"
            )
        if attempt < max_retries:
            delay = min(2 ** attempt, 10)
            if on_retry:
                on_retry(attempt + 1, max_retries, delay)
            time.sleep(delay)
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
    max_tokens = 8192
    reasoning_effort = "high"

    if st.button("🧹 会話をリセット", use_container_width=True):
        st.session_state.chat_history = []
        track_usage(action="会話リセット", tool_name="GPT-5チャット")
        st.rerun()

# チャット履歴（最小装飾）
_render_chat_history(st.session_state.chat_history)

# リトライ状況表示
retry_status = st.empty()

def _on_submit() -> None:
    prompt = st.session_state.get("user_input", "")
    if not prompt or st.session_state.is_processing:
        return
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.session_state.is_processing = True

# 入力欄: Streamlit標準のチャット入力を使用して常に下部に固定
st.chat_input(
    "メッセージを入力",
    key="user_input",
    disabled=st.session_state.is_processing,
    on_submit=_on_submit,
)

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
            st.session_state.user_input = ""
            st.rerun()
