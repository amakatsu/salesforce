#!/usr/bin/env python3
"""
PR-Agent バリデータモジュール
URL検証などの検証機能
"""


class UrlValidator:
    """URL検証クラス"""

    VALID_PATTERNS = [
        "github.com", "gitlab.com", "bitbucket.org", "dev.azure.com",
        "/pull/", "/merge_requests/", "/-/merge_requests/"
    ]

    @classmethod
    def validate_pr_url(cls, url: str) -> bool:
        """PR URLの形式を検証"""
        return any(pattern in url for pattern in cls.VALID_PATTERNS)
