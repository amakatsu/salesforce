#!/usr/bin/env python3
"""
PR-Agent バリデータモジュール
URL検証などの検証機能
"""
import re
from urllib.parse import urlparse


class UrlValidator:
    """URL検証クラス（独自ホスティング対応）"""

    # PR/MRパスのパターン
    PR_PATTERNS = [
        r"/pull/\d+",              # GitHub PR
        r"/merge_requests/\d+",    # GitLab MR (従来)
        r"/-/merge_requests/\d+",  # GitLab MR (新形式)
    ]

    # 既知のGitホスティングドメイン（参考用）
    KNOWN_HOSTS = [
        "github.com", "gitlab.com", "bitbucket.org", "dev.azure.com"
    ]

    @classmethod
    def validate_pr_url(cls, url: str) -> bool:
        """
        PR/MR URLの形式を検証（独自ホスティング対応）

        検証内容:
        1. 有効なURL形式か（http/https）
        2. PR/MRパスを含むか

        Args:
            url: 検証するURL

        Returns:
            bool: 有効なPR/MR URLならTrue
        """
        if not url:
            return False

        try:
            # URLパース
            parsed = urlparse(url)

            # スキームチェック（http or https）
            if parsed.scheme not in ['http', 'https']:
                return False

            # ホスト名が存在するか
            if not parsed.netloc:
                return False

            # PR/MRパスパターンチェック
            for pattern in cls.PR_PATTERNS:
                if re.search(pattern, parsed.path):
                    return True

            return False

        except Exception:
            return False

    @classmethod
    def validate_gitlab_url(cls, url: str) -> bool:
        """
        GitLab URL（ベースURL）の形式を検証

        Args:
            url: 検証するURL（例: https://git.example.com）

        Returns:
            bool: 有効なURLならTrue
        """
        if not url:
            return False

        try:
            parsed = urlparse(url)

            # スキームチェック
            if parsed.scheme not in ['http', 'https']:
                return False

            # ホスト名が存在するか
            if not parsed.netloc:
                return False

            # パスがないか、ルートのみ
            if parsed.path and parsed.path not in ['', '/']:
                return False

            return True

        except Exception:
            return False

    @classmethod
    def normalize_gitlab_url(cls, url: str) -> str:
        """
        GitLab URLを正規化

        - trailing slashを削除
        - スキームがない場合はhttpsを追加

        Args:
            url: 正規化するURL

        Returns:
            str: 正規化されたURL
        """
        if not url:
            return url

        # trailing slashを削除
        normalized = url.rstrip('/')

        # スキームがない場合はhttpsを追加
        if not normalized.startswith(('http://', 'https://')):
            normalized = f'https://{normalized}'

        return normalized

    @classmethod
    def validate(cls, url: str) -> bool:
        """
        汎用URL検証（後方互換性のため）

        Args:
            url: 検証するURL

        Returns:
            bool: 有効なURLならTrue
        """
        return cls.validate_pr_url(url)
