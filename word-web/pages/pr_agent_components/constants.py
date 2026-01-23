# -*- coding: utf-8 -*-
"""
PR-Agent 定数・設定定義
"""

# セッション状態のキー
MODAL_STATE_KEY = "config_modal_open"
INPUT_METHOD_KEY = "input_method_selector"

# PR-Agentコマンドの説明
COMMAND_DESCRIPTIONS = {
    "review": "📝 コードレビュー - コードの問題点、改善提案、ベストプラクティスを分析",
    "improve": "✨ コード改善 - 具体的なコード改善案を提示（リファクタリング、最適化など）",
    "describe": "📋 MR説明生成 - MRの内容を分析して説明文を自動生成",
    "ask": "❓ 質問応答 - MRに関する質問に回答（例: セキュリティリスクは？）",
    "generate_labels": "🏷️ ラベル生成 - MRの内容に基づいて適切なラベルを提案",
    "add_docs": "📚 ドキュメント追加 - コードのドキュメントを自動生成"
}

# コマンドと設定セクションのマッピング
COMMAND_SECTION_MAP = {
    "review": ["pr_reviewer"],
    "improve": ["pr_improve", "pr_code_suggestions"],
    "describe": ["pr_description"],
    "ask": ["pr_questions"],
    "generate_labels": ["pr_generate_labels"],
    "add_docs": ["pr_add_docs"]
}

# 設定フォーム用セクション定義
CONFIG_SECTIONS = {
    "pr_reviewer": {
        "label": "📝 レビュー設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "レビュー時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "require_score_review": {"type": "checkbox", "label": "スコアレビューを要求", "default": True},
            "require_tests_review": {"type": "checkbox", "label": "テストレビューを要求", "default": True},
            "require_estimate_effort_to_review": {"type": "checkbox", "label": "レビュー工数見積もり", "default": True},
            "enable_review_labels_effort": {"type": "checkbox", "label": "工数ラベル有効", "default": True},
            "enable_review_labels_security": {"type": "checkbox", "label": "セキュリティラベル有効", "default": True},
        }
    },
    "pr_code_suggestions": {
        "label": "✨ コード提案設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "コード提案時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "commitable_code_suggestions": {"type": "checkbox", "label": "コミット可能な形式で提案", "default": True},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_improve": {
        "label": "🔧 コード改善設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "コード改善時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_description": {
        "label": "📋 MR説明設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "MR説明生成時のAIへの追加指示"},
            "publish_description": {"type": "checkbox", "label": "説明を公開", "default": True},
            "add_original_user_description": {"type": "checkbox", "label": "元の説明を追加", "default": True},
            "enable_pr_type": {"type": "checkbox", "label": "PR種別を有効", "default": True},
            "use_bullet_points": {"type": "checkbox", "label": "箇条書き形式", "default": True},
            "enable_semantic_files_types": {"type": "checkbox", "label": "ファイル種別分類を有効", "default": True},
            "generate_ai_title": {"type": "checkbox", "label": "AIタイトル生成", "default": False},
        }
    },
    "pr_questions": {
        "label": "❓ 質問応答設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "質問応答時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_add_docs": {
        "label": "📚 ドキュメント設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "ドキュメント生成時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_generate_labels": {
        "label": "🏷️ ラベル生成設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "ラベル生成時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_update_changelog": {
        "label": "📜 Changelog設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "Changelog更新時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_similar_issue": {
        "label": "🔍 類似Issue設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "類似Issue検索時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
}

# Geminiモデルリスト
GEMINI_MODELS = [
    "gemini/gemini-2.0-flash-exp",
    "gemini/gemini-1.5-pro-latest",
    "gemini/gemini-1.5-flash-latest",
    "gemini/gemini-1.5-flash-002"
]

# AIプロバイダーリスト
AI_PROVIDERS = ["OpenAI (Azure)", "Gemini"]
