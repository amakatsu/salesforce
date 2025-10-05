#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リトライロジック共通モジュール
エラー処理・リトライ・バックオフを提供
"""
import time
import requests
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')


def with_retry(
    max_retries: int = 2,
    backoff_factor: float = 1.2,
    retry_on_auth_error: bool = False
) -> Callable:
    """
    リトライ機能を追加するデコレータ

    Args:
        max_retries: 最大リトライ回数
        backoff_factor: バックオフ係数（指数バックオフの基数）
        retry_on_auth_error: 認証エラー時にもリトライするか

    Returns:
        デコレータ関数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    # 認証エラーは即座に失敗（設定で変更可能）
                    if not retry_on_auth_error and e.response.status_code in [401, 403]:
                        raise Exception(
                            f"API認証エラー (HTTP {e.response.status_code}): "
                            "APIキーまたはユーザIDが無効です"
                        ) from e

                    # 最後の試行でエラーが発生したら再スロー
                    if attempt >= max_retries:
                        raise

                    # バックオフして再試行
                    time.sleep(backoff_factor * (attempt + 1))
                except Exception as e:
                    # 最後の試行でエラーが発生したら再スロー
                    if attempt >= max_retries:
                        raise

                    # バックオフして再試行
                    time.sleep(backoff_factor * (attempt + 1))

            # ここには到達しない（安全のため）
            raise Exception("リトライが予期せず終了しました")

        return wrapper
    return decorator


def retry_on_exception(
    func: Callable[..., T],
    max_retries: int = 2,
    backoff_factor: float = 1.2,
    retry_on_auth_error: bool = False,
    *args,
    **kwargs
) -> T:
    """
    関数を実行し、例外が発生した場合はリトライする

    Args:
        func: 実行する関数
        max_retries: 最大リトライ回数
        backoff_factor: バックオフ係数
        retry_on_auth_error: 認証エラー時にもリトライするか
        *args: funcへの位置引数
        **kwargs: funcへのキーワード引数

    Returns:
        関数の実行結果

    Raises:
        Exception: 最大リトライ回数を超えた場合
    """
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            # 認証エラーは即座に失敗（設定で変更可能）
            if not retry_on_auth_error and e.response.status_code in [401, 403]:
                raise Exception(
                    f"API認証エラー (HTTP {e.response.status_code}): "
                    "APIキーまたはユーザIDが無効です"
                ) from e

            # 最後の試行でエラーが発生したら再スロー
            if attempt >= max_retries:
                raise

            # バックオフして再試行
            time.sleep(backoff_factor * (attempt + 1))
        except Exception as e:
            # 最後の試行でエラーが発生したら再スロー
            if attempt >= max_retries:
                raise

            # バックオフして再試行
            time.sleep(backoff_factor * (attempt + 1))

    # ここには到達しない（安全のため）
    raise Exception("リトライが予期せず終了しました")
