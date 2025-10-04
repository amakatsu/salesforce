# PR-Agent パッケージ構成解説

## 概要
PR-Agent v0.3.0 は、QodoAI が開発したAIベースのプルリクエスト分析・支援ツールです。
複数のAIプロバイダーに対応し、プルリクエストの自動レビュー、説明生成、コード改善提案などを行います。

## プロジェクト構造

```
pr_agent/
├── agent/                          # メインエージェント
│   ├── pr_agent.py                 # 基本PRエージェント
│   └── pr_agent_local.py           # ローカル用PRエージェント
├── algo/                           # アルゴリズム・コア機能
│   ├── ai_handlers/                # AIハンドラー
│   │   ├── base_ai_handler.py      # 抽象基底クラス
│   │   ├── litellm_ai_handler.py   # LiteLLMハンドラー(デフォルト)
│   │   ├── openai_ai_handler.py    # OpenAI直接ハンドラー
│   │   └── langchain_ai_handler.py # LangChainハンドラー
│   ├── cli_args.py                 # CLI引数処理
│   ├── file_filter.py              # ファイルフィルタリング
│   ├── git_patch_processing.py     # Gitパッチ処理
│   ├── language_handler.py         # 言語固有処理
│   ├── pr_processing.py            # PR処理
│   ├── token_handler.py            # トークン管理
│   ├── types.py                    # 型定義
│   └── utils.py                    # ユーティリティ
├── git_providers/                  # Git プロバイダー連携
│   ├── github_provider.py          # GitHub
│   ├── gitlab_provider.py          # GitLab
│   ├── bitbucket_provider.py       # Bitbucket
│   ├── azuredevops_provider.py     # Azure DevOps
│   ├── gerrit_provider.py          # Gerrit
│   ├── gitea_provider.py           # Gitea
│   ├── codecommit_provider.py      # AWS CodeCommit
│   ├── local_git_provider.py       # ローカルGit
│   └── git_provider.py             # 基底クラス
├── tools/                          # PR操作ツール
│   ├── pr_reviewer.py              # PRレビュー
│   ├── pr_description.py           # PR説明生成
│   ├── pr_code_suggestions.py      # コード改善提案
│   ├── pr_questions.py             # PR質問機能
│   ├── pr_line_questions.py        # 行別質問
│   ├── pr_add_docs.py              # ドキュメント追加
│   ├── pr_generate_labels.py       # ラベル自動生成
│   ├── pr_update_changelog.py      # チェンジログ更新
│   ├── pr_similar_issue.py         # 類似issue検索
│   ├── pr_help_docs.py             # ヘルプドキュメント
│   ├── pr_help_message.py          # ヘルプメッセージ
│   └── pr_config.py                # 設定管理
├── settings/                       # 設定ファイル
│   ├── configuration.toml          # メイン設定
│   ├── .secrets_template.toml      # 機密情報テンプレート
│   ├── ignore.toml                 # 除外設定
│   ├── language_extensions.toml    # 言語拡張子
│   ├── pr_reviewer_prompts.toml    # レビュープロンプト
│   ├── pr_description_prompts.toml # 説明生成プロンプト
│   └── code_suggestions/           # コード提案プロンプト
│       ├── pr_code_suggestions_prompts.toml
│       ├── pr_code_suggestions_prompts_not_decoupled.toml
│       └── pr_code_suggestions_reflect_prompts.toml
├── servers/                        # サーバー機能
├── identity_providers/             # ID プロバイダー
├── secret_providers/               # シークレット プロバイダー
├── log/                           # ログ機能
├── cli.py                         # CLI エントリーポイント
├── cli_pip.py                     # pip 用CLI
└── config_loader.py               # 設定ローダー
```

## 主要コンポーネント

### 1. AIハンドラー (`algo/ai_handlers/`)

#### 基本構造
- **BaseAiHandler** - 抽象基底クラス
- 全ハンドラーは `chat_completion()` メソッドを実装

#### 具象ハンドラー
1. **LiteLLMAIHandler** (デフォルト)
   - 複数AIプロバイダー統一対応
   - OpenAI, Claude, Gemini, AWS Bedrock等
   - 設定ファイルでモデル切り替え可能

2. **OpenAIHandler**
   - OpenAI API直接利用
   - Azure OpenAI対応
   - 高性能・細かい制御向け

3. **LangChainOpenAIHandler**
   - LangChainエコシステム統合
   - Runnable Interface対応
   - 複雑なワークフロー連携向け

#### ハンドラーの使い方
```python
# デフォルト (LiteLLM)
agent = PRAgent()

# カスタムハンドラー指定
from functools import partial
from pr_agent.algo.ai_handlers.openai_ai_handler import OpenAIHandler
agent = PRAgent(ai_handler=partial(OpenAIHandler))
```

### 2. PRツール (`tools/`)

#### 主要ツール
- **pr_reviewer.py** - PRレビューと改善提案
- **pr_description.py** - PRタイトル・説明自動生成
- **pr_code_suggestions.py** - コード改善提案
- **pr_questions.py** - PRに関する質問機能
- **pr_add_docs.py** - ドキュメント自動追加
- **pr_generate_labels.py** - ラベル自動生成

#### 使用例
```bash
# PRレビュー
cli.py --pr_url=<URL> review

# PR説明生成
cli.py --pr_url=<URL> describe

# コード改善提案
cli.py --pr_url=<URL> improve

# 質問機能
cli.py --pr_url=<URL> ask "このPRについて教えて"
```

### 3. Git プロバイダー (`git_providers/`)

#### 対応プラットフォーム
- **GitHub** - フル機能対応
- **GitLab** - GitLab.com, self-hosted
- **Bitbucket** - Cloud, Server
- **Azure DevOps** - Azure Repos
- **Gerrit** - コードレビューシステム
- **Gitea** - 軽量Git サービス
- **AWS CodeCommit** - AWS管理Git
- **Local Git** - ローカルリポジトリ

### 4. 設定システム (`settings/`)

#### 設定ファイル構成
- **configuration.toml** - メイン設定 (モデル、API、全般)
- **プロンプトファイル** - 各機能のプロンプトテンプレート
- **言語設定** - プログラミング言語固有設定
- **除外設定** - 分析対象外ファイル設定

#### 主要設定項目
```toml
[config]
model="o4-mini"                    # 使用モデル
git_provider="github"              # Gitプロバイダー
publish_output=true                # 出力公開
verbosity_level=0                  # ログレベル
ai_timeout=120                     # AI応答タイムアウト
response_language="en-US"          # 応答言語
```

## カスタムハンドラーの作成

### 1. ハンドラークラス作成
```python
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler

class CustomAIHandler(BaseAiHandler):
    def __init__(self):
        super().__init__()
        # 初期化処理

    @property
    def deployment_id(self):
        return "custom-deployment"

    async def chat_completion(self, model: str, system: str, user: str,
                            temperature: float = 0.2, img_path: str = None):
        # カスタムAI APIの実装
        pass
```

### 2. ハンドラー使用
```python
from pr_agent.agent.pr_agent import PRAgent
from functools import partial

agent = PRAgent(ai_handler=partial(CustomAIHandler))
```

### 3. 設定追加（必要に応じて）
```toml
[custom_ai]
api_key="your-api-key"
endpoint="your-endpoint"
```

## 主要依存関係

### AI/ML ライブラリ
- **openai** - OpenAI API
- **anthropic** - Claude API
- **google-generativeai** - Gemini API
- **litellm** - 統一AIプロバイダーインターフェース

### Git統合
- **GitPython** - Git操作
- **PyGithub** - GitHub API
- **python-gitlab** - GitLab API

### Web/API
- **fastapi** - Web API フレームワーク
- **uvicorn** - ASGI サーバー
- **aiohttp** - 非同期HTTP

### クラウド
- **boto3** - AWS SDK
- **azure-devops** - Azure DevOps API
- **google-cloud-aiplatform** - Google Cloud AI

## 拡張ポイント

### 1. 新しいAIプロバイダー追加
- `BaseAiHandler` を継承
- `chat_completion()` メソッド実装
- エラーハンドリング・リトライ機能追加

### 2. 新しいGitプロバイダー追加
- `git_provider.py` の基底クラスを継承
- プロバイダー固有API実装

### 3. 新しいツール追加
- `tools/` ディレクトリに追加
- `command2class` 辞書に登録
- 対応するプロンプトファイル作成

### 4. カスタムプロンプト
- `settings/` ディレクトリのTOMLファイル編集
- Jinja2テンプレート使用可能

## ライセンス
GNU Affero General Public License v3.0

---
*Generated for PR-Agent v0.3.0*