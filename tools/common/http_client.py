#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP クライアント共通モジュール
セッション管理・プロキシ設定・SSL検証を一元管理
"""
import os
import requests
from typing import Optional


class HttpClient:
    """
    HTTP通信用の共通クライアント
    プロキシ設定やSSL検証の設定を一元管理
    """

    def __init__(
        self,
        timeout: float = 30.0,
        verify_ssl: Optional[bool] = None,
        proxies: Optional[dict] = None
    ):
        """
        Args:
            timeout: タイムアウト秒数
            verify_ssl: SSL検証の有効/無効（Noneの場合は環境変数から取得）
            proxies: プロキシ設定（Noneの場合は環境変数から取得）
        """
        self.timeout = timeout

        # SSL検証設定
        if verify_ssl is None:
            self.verify_ssl = os.getenv("VERIFY_SSL", "true").lower() != "false"
        else:
            self.verify_ssl = verify_ssl

        # セッション作成
        self.session = requests.Session()

        # プロキシ設定
        if proxies is None:
            proxies = self._get_proxies_from_env()

        if proxies:
            self.session.proxies.update(proxies)

    @staticmethod
    def _get_proxies_from_env() -> dict:
        """
        環境変数からプロキシ設定を取得

        Returns:
            プロキシ設定の辞書
        """
        proxies = {}
        if os.getenv("HTTP_PROXY"):
            proxies["http"] = os.getenv("HTTP_PROXY")
        if os.getenv("HTTPS_PROXY"):
            proxies["https"] = os.getenv("HTTPS_PROXY")
        return proxies

    def post_json(
        self,
        url: str,
        headers: dict,
        payload: dict,
        timeout: Optional[float] = None
    ) -> requests.Response:
        """
        JSON形式でPOSTリクエストを送信

        Args:
            url: リクエストURL
            headers: リクエストヘッダー
            payload: リクエストボディ（辞書形式）
            timeout: タイムアウト秒数（Noneの場合はデフォルト値を使用）

        Returns:
            Responseオブジェクト

        Raises:
            requests.exceptions.HTTPError: HTTPエラーが発生した場合
        """
        resp = self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout or self.timeout,
            verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp
