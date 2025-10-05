# PR-Agent カスタマイズガイド

PR-Agent v0.3.0 のカスタマイズ方法とセットアップガイドです。

## 📋 目次

- [概要](#概要)
- [インストール](#インストール)
- [基本的な使い方](#基本的な使い方)
- [設定ファイルカスタマイズ](#設定ファイルカスタマイズ)
- [カスタムハンドラー作成](#カスタムハンドラー作成)
- [新しいコマンド追加](#新しいコマンド追加)
- [プロンプトカスタマイズ](#プロンプトカスタマイズ)
- [高度な設定](#高度な設定)
- [トラブルシューティング](#トラブルシューティング)

## 🔍 概要

PR-Agent は QodoAI が開発したAIベースのプルリクエスト分析・支援ツールです。
このガイドでは、組織やプロジェクトのニーズに合わせてPR-Agentをカスタマイズする方法を説明します。

### 主要機能
- 🔍 **PRレビュー**: AIによる自動コードレビューと改善提案
- 📝 **PR説明生成**: タイトルと説明の自動生成
- 💡 **コード改善提案**: パフォーマンスとセキュリティの改善提案
- ❓ **質問機能**: PRに関する質問とコンテキスト理解
- 🏷️ **ラベル生成**: 適切なラベルの自動付与
- 📚 **ドキュメント生成**: コードドキュメントの自動追加

### 対応プラットフォーム
- GitHub (GitHub Enterprise含む)
- GitLab (GitLab.com, Self-hosted)
- Bitbucket (Cloud, Server)
- Azure DevOps
- AWS CodeCommit
- Gerrit
- Gitea

## 📁 プロジェクト構造

```
📦 pr-agent/
├── 📄 README.md                           # メインガイド（最初に読む）
├── 📄 pr_agent.py                         # メイン実行コマンド
├── 📄 .pr_agent.toml                      # ローカル開発用デフォルト設定
│
├── 📁 configs/                            # 設定ファイル群（Web UIから選択可能）
│   ├── 📁 templates/                      # 基本テンプレート
│   │   ├── 📄 configuration-example.toml  # 基本設定テンプレート
│   │   └── 📄 high-precision-config.toml  # 高精度レビュー設定
│   │
│   ├── 📁 presets/                        # 用途別プリセット
│   │   ├── 📄 security-focused.toml       # 🔒 セキュリティ特化（OWASP Top 10）
│   │   ├── 📄 performance-focused.toml    # ⚡ パフォーマンス特化
│   │   └── 📄 educational.toml            # 👨‍🎓 教育・新人向け
│   │
│   └── 📁 language-specific/              # 言語固有設定
│       └── 📄 python-high-precision.toml  # Python専用高精度設定
│
├── 📁 tools/                              # 実行ツール
│   ├── 📄 pr_agent_runner.py              # PR-Agent実行エンジン
│   └── 📄 switch_config.py                # 設定切り替えツール
│
└── 📁 docs/                               # 詳細ドキュメント
    ├── 📄 README.md                       # ドキュメント目次
    ├── 📄 quick-reference.md              # クイックリファレンス
    ├── 📄 usage-examples.md               # 使用例集
    ├── 📄 customization-guide.md          # カスタマイズ完全ガイド
    ├── 📄 precision-enhancement-guide.md  # レビュー精度向上ガイド
    └── 📄 PR-Agent-Structure.md           # PR-Agent内部構造
```

### 設定ファイルの配置ルール

- **`pr-agent/.pr_agent.toml`**: ローカル開発時のデフォルト設定（CLI実行用）
- **`tools/.pr_agent.toml`**: Dockerコンテナ内のグローバルデフォルト設定（`/root/.pr_agent.toml`にコピーされる）
- **`configs/`**: Web UIから選択可能な設定ファイル群
  - `presets/`: 用途別の設定（セキュリティ、パフォーマンス等）
  - `language-specific/`: 言語固有の最適化設定
  - `templates/`: カスタマイズのベーステンプレート

## 🚀 インストール

### 前提条件
- Python 3.8以上
- Git
- 対象のGitプラットフォームのAPIアクセス権

### インストール手順

```bash
# PR-Agentのインストール
pip install pr-agent

# または開発版
pip install git+https://github.com/Codium-ai/pr-agent.git
```

### 環境変数設定

```bash
# OpenAI API (推奨)
export OPENAI_API_KEY="your-openai-api-key"

# GitHub設定
export GITHUB_TOKEN="your-github-token"

# GitLab設定
export GITLAB_TOKEN="your-gitlab-token"

# その他のプロバイダー
export ANTHROPIC_API_KEY="your-claude-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

## 🎯 基本的な使い方

### コマンドライン使用

```bash
# PRレビュー実行
pr-agent --pr_url="https://github.com/user/repo/pull/123" review

# PR説明生成
pr-agent --pr_url="https://github.com/user/repo/pull/123" describe

# コード改善提案
pr-agent --pr_url="https://github.com/user/repo/pull/123" improve

# 質問機能
pr-agent --pr_url="https://github.com/user/repo/pull/123" ask "このPRのセキュリティ影響は？"

# ラベル生成
pr-agent --pr_url="https://github.com/user/repo/pull/123" generate_labels

# ヘルプ表示
pr-agent --help
```

### プログラム内使用

```python
import asyncio
from pr_agent.agent.pr_agent import PRAgent

async def review_pr():
    agent = PRAgent()
    result = await agent.handle_request(
        "https://github.com/user/repo/pull/123",
        ["review"]
    )
    return result

# 実行
result = asyncio.run(review_pr())
```

## ⚙️ 設定ファイルカスタマイズ

### 設定ファイルの場所

PR-Agentは以下の優先順位で設定を読み込みます：

1. **CLI引数** (最優先)
2. **リポジトリ設定** (`.pr_agent.toml`)
3. **ユーザー設定** (`~/.pr_agent/configuration.toml`)
4. **システム設定** (パッケージ内設定)

### リポジトリ固有設定

プロジェクトルートに `.pr_agent.toml` を作成：

```toml
# プロジェクト固有の設定
[config]
model = "gpt-4"
response_language = "ja-JP"
verbosity_level = 1

[pr_reviewer]
extra_instructions = """
このプロジェクトでは以下の点を重視してレビューしてください：
- セキュリティベストプラクティス
- パフォーマンス最適化
- コードの可読性
- テストカバレッジ
"""
require_tests_review = true
require_score_review = true
```

### 詳細な設定例

完全な設定例は [`configuration-example.toml`](./configuration-example.toml) を参照してください。

## 🔧 カスタムハンドラー作成

### 1. カスタムAIハンドラー作成

```python
# custom_ai_handler.py
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.config_loader import get_settings
import httpx
import json

class CustomAIHandler(BaseAiHandler):
    """
    カスタムAIプロバイダー用ハンドラー
    """

    def __init__(self):
        super().__init__()
        self.api_key = get_settings().custom_ai.api_key
        self.endpoint = get_settings().custom_ai.endpoint

    @property
    def deployment_id(self):
        return "custom-deployment"

    async def chat_completion(self, model: str, system: str, user: str,
                            temperature: float = 0.2, img_path: str = None):
        """
        カスタムAI APIへのリクエスト実装
        """
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": temperature
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                finish_reason = result["choices"][0]["finish_reason"]

                return content, finish_reason

        except Exception as e:
            raise Exception(f"カスタムAI API エラー: {str(e)}")
```

### 2. ハンドラーの使用

```python
# main.py
from pr_agent.agent.pr_agent import PRAgent
from functools import partial
from custom_ai_handler import CustomAIHandler

# カスタムハンドラーでPRAgentを初期化
agent = PRAgent(ai_handler=partial(CustomAIHandler))

# 使用
result = await agent.handle_request(pr_url, ["review"])
```

### 3. 設定ファイルでの設定

```toml
# .pr_agent.toml
[custom_ai]
api_key = "your-custom-api-key"
endpoint = "https://your-custom-ai-api.com/v1/chat/completions"
model = "your-custom-model"
```

## 🆕 新しいコマンド追加

### 1. カスタムツールクラス作成

```python
# tools/pr_security_check.py
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.algo.ai_handlers.litellm_ai_handler import LiteLLMAIHandler
from pr_agent.config_loader import get_settings
from pr_agent.git_providers import get_git_provider_with_context
from functools import partial

class PRSecurityCheck:
    """
    セキュリティ専用チェックツール
    """

    def __init__(self, pr_url: str, ai_handler: partial[BaseAiHandler,] = LiteLLMAIHandler, args: list = None):
        self.pr_url = pr_url
        self.ai_handler = ai_handler
        self.args = args
        self.git_provider = get_git_provider_with_context(pr_url)

    async def run(self):
        """
        セキュリティチェック実行
        """
        # PR情報取得
        pr_info = self.git_provider.get_pr_info()
        pr_diff = self.git_provider.get_pr_diff()

        # セキュリティ専用プロンプト
        system_prompt = get_settings().pr_security_check.system_prompt
        user_prompt = self._generate_security_prompt(pr_info, pr_diff)

        # AI実行
        ai_handler = self.ai_handler()
        response, _ = await ai_handler.chat_completion(
            model=get_settings().config.model,
            system=system_prompt,
            user=user_prompt,
            temperature=0.1  # セキュリティチェックは保守的に
        )

        # 結果をコメントとして投稿
        self.git_provider.publish_comment(response)
        return response

    def _generate_security_prompt(self, pr_info, pr_diff):
        """
        セキュリティチェック用プロンプト生成
        """
        return f"""
        以下のPRをセキュリティ観点でチェックしてください：

        PRタイトル: {pr_info.title}
        PR説明: {pr_info.description}

        変更内容:
        {pr_diff}

        チェック項目：
        - SQLインジェクション脆弱性
        - XSS脆弱性
        - 認証・認可の不備
        - 機密情報の漏洩
        - 入力値検証の不備
        - セキュアコーディング違反

        問題があれば詳細に説明し、修正方法を提案してください。
        """
```

### 2. コマンド登録

```python
# agent/pr_agent.py の command2class に追加
from pr_agent.tools.pr_security_check import PRSecurityCheck

command2class = {
    # 既存コマンド...
    "security_check": PRSecurityCheck,  # 新規追加
    "sec": PRSecurityCheck,            # エイリアス
}
```

### 3. プロンプト設定ファイル作成

```toml
# settings/pr_security_check.toml
[pr_security_check]
system_prompt = """
あなたはセキュリティエキスパートです。
プルリクエストのコード変更をセキュリティ観点で詳細に分析してください。

分析観点：
1. 脆弱性の特定（OWASP Top 10準拠）
2. セキュアコーディングガイドライン遵守
3. 機密情報の適切な取り扱い
4. 入力検証とサニタイゼーション
5. 認証・認可の実装

出力形式：
- ✅ 問題なし / ⚠️ 注意 / 🚨 重大な問題
- 具体的な修正方法の提案
- セキュリティベストプラクティスの推奨
"""
```

### 4. 使用例

```bash
# セキュリティチェック実行
pr-agent --pr_url="https://github.com/user/repo/pull/123" security_check

# エイリアス使用
pr-agent --pr_url="https://github.com/user/repo/pull/123" sec
```

## 📝 プロンプトカスタマイズ

### 既存プロンプトの修正

```toml
# settings/pr_reviewer_prompts.toml のカスタマイズ
[pr_review_prompt]
system = """
あなたは経験豊富な日本人シニアエンジニアです。
プルリクエストを以下の観点でレビューしてください：

🔍 コード品質
- 可読性と保守性
- パフォーマンス影響
- エラーハンドリング

🛡️ セキュリティ
- 脆弱性の有無
- 入力検証
- 認証・認可

🧪 テスト
- テストカバレッジ
- テストの妥当性
- エッジケース

📚 ドキュメント
- コメントの適切性
- APIドキュメント更新

日本語で丁寧にレビューし、建設的な改善提案をしてください。
"""

user = """
以下のPRをレビューしてください：

## PR情報
- タイトル: {{ pr_title }}
- 説明: {{ pr_description }}
- 変更ファイル数: {{ num_files }}
- 追加行数: {{ additions }}
- 削除行数: {{ deletions }}

## 変更内容
{{ pr_diff }}

## 特別な注意事項
このプロジェクトでは{{ extra_instructions }}を重視しています。

よろしくお願いします。
"""
```

### 条件付きプロンプト

```python
# tools/pr_reviewer.py でのカスタマイズ例
def _get_system_prompt(self):
    base_prompt = get_settings().pr_review_prompt.system

    # 言語固有の追加指示
    if self.main_language == "python":
        base_prompt += "\nPythonコード: PEP8準拠とtype hintsの使用を確認してください。"
    elif self.main_language == "javascript":
        base_prompt += "\nJavaScriptコード: ESLint準拠とセキュリティ（XSS等）を重視してください。"
    elif self.main_language == "java":
        base_prompt += "\nJavaコード: チェック例外処理とメモリリークに注意してください。"

    # ファイル数による指示調整
    if len(self.git_provider.get_files()) > 10:
        base_prompt += "\n大規模な変更です。影響範囲を特に注意深く確認してください。"

    return base_prompt
```

## 🔧 高度な設定

### 組織向け設定テンプレート

```toml
# 大企業向け設定例
[config]
model = "gpt-4"
response_language = "ja-JP"
verbosity_level = 1
ai_timeout = 180
temperature = 0.1  # 保守的な応答

# セキュリティ重視設定
[pr_reviewer]
require_tests_review = true
require_score_review = true
extra_instructions = """
企業セキュリティガイドライン準拠を確認：
- OWASP Top 10 チェック
- 機密情報の適切な取り扱い
- ログ出力での機密情報漏洩防止
- サードパーティライブラリのセキュリティ
"""

# 厳格なコード品質
[pr_code_suggestions]
suggestions_score_threshold = 8
focus_only_on_problems = true
commitable_code_suggestions = false

# 除外設定
[config]
ignore_pr_authors = ["dependabot", "renovate", "github-actions"]
ignore_pr_labels = ["dependencies", "auto-update"]
patch_extension_skip_types = [".md", ".txt", ".json", ".yml", ".png", ".jpg"]
```

### CI/CD統合

#### GitHub Actions

```yaml
# .github/workflows/pr-agent.yml
name: PR Agent

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  pr-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install PR Agent
        run: pip install pr-agent

      - name: Run PR Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          pr-agent --pr_url="${{ github.event.pull_request.html_url }}" review

      - name: Generate PR Description
        if: github.event.action == 'opened'
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          pr-agent --pr_url="${{ github.event.pull_request.html_url }}" describe
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
pr-agent:
  stage: review
  image: python:3.11-slim
  script:
    - pip install pr-agent
    - pr-agent --pr_url="$CI_MERGE_REQUEST_PROJECT_URL/-/merge_requests/$CI_MERGE_REQUEST_IID" review
  only:
    - merge_requests
  variables:
    GITLAB_TOKEN: $GITLAB_TOKEN
    OPENAI_API_KEY: $OPENAI_API_KEY
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. API制限エラー

```bash
# エラー: Rate limit exceeded
# 解決方法: 複数のAPIキーを設定

export OPENAI_API_KEY="key1,key2,key3"  # カンマ区切りで複数設定
```

#### 2. 大きなPRでタイムアウト

```toml
[config]
ai_timeout = 300                    # タイムアウト延長
large_patch_policy = "clip"         # 大きなパッチを切り詰め
max_model_tokens = 16000           # トークン制限調整

[pr_reviewer]
max_context_tokens = 20000         # コンテキスト制限調整
```

#### 3. 日本語出力が不安定

```toml
[config]
response_language = "ja-JP"
temperature = 0.0                   # 温度を下げて安定化

[pr_reviewer]
extra_instructions = "必ず日本語で回答してください。英語は使用しないでください。"
```

#### 4. プライベートリポジトリでエラー

```bash
# GitHub Enterprise
export GITHUB_BASE_URL="https://github.enterprise.com/api/v3"

# GitLab Self-hosted
export GITLAB_URL="https://gitlab.company.com"
```

### ログとデバッグ

```toml
[config]
log_level = "DEBUG"                 # 詳細ログ
verbosity_level = 2                 # 最大詳細度
output_relevant_configurations = true  # 設定情報出力
```

```bash
# ログファイル出力
pr-agent --pr_url="..." review --log_file="pr-agent.log"
```

## 📚 詳細ドキュメント

このリポジトリには詳細なドキュメントが用意されています：

### **📁 [docs/](./docs/) - 詳細ドキュメント集**
- **[使用例集](./docs/usage-examples.md)** - 実践的な使用方法
- **[プロジェクト構造](./docs/project-structure.md)** - ファイル・ディレクトリ構成
- **[カスタマイズガイド](./docs/customization-guide.md)** - カスタマイズ方法
- **[精度向上ガイド](./docs/precision-enhancement-guide.md)** - レビュー品質改善
- **[プロンプト切り替え](./docs/custom-prompt-switching-guide.md)** - プロンプト管理
- **[内部構造解説](./docs/PR-Agent-Structure.md)** - 技術詳細

### **🔗 外部リンク**
- [PR-Agent 公式ドキュメント](https://qodo-merge-docs.qodo.ai/)
- [GitHub](https://github.com/Codium-ai/pr-agent)
- [設定リファレンス](https://qodo-merge-docs.qodo.ai/configuration/)
- [コミュニティ](https://discord.gg/SgSxuQ65GF)

## 🤝 コントリビューション

バグ報告や機能要求は [GitHub Issues](https://github.com/Codium-ai/pr-agent/issues) まで。

## 📄 ライセンス

GNU Affero General Public License v3.0

---

*このガイドはPR-Agent v0.3.0用に作成されています。*