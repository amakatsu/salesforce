#!/usr/bin/env python3
"""
PR-Agent カスタム実行ツール (リファクタリング版)
設定ファイルとPR URLを指定してpr-agentを実行
"""

import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import sys
import shutil
import toml


class Colors:
    """ANSI色コード定数"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Logger:
    """カラー出力付きロガー"""

    @staticmethod
    def print_colored(message: str, color: str = Colors.WHITE) -> None:
        """色付きメッセージを出力"""
        print(f"{color}{message}{Colors.END}")

    @staticmethod
    def success(message: str) -> None:
        """成功メッセージ"""
        Logger.print_colored(f"✅ {message}", Colors.GREEN)

    @staticmethod
    def error(message: str) -> None:
        """エラーメッセージ"""
        Logger.print_colored(f"❌ {message}", Colors.RED)

    @staticmethod
    def warning(message: str) -> None:
        """警告メッセージ"""
        Logger.print_colored(f"⚠️  {message}", Colors.YELLOW)

    @staticmethod
    def info(message: str) -> None:
        """情報メッセージ"""
        Logger.print_colored(f"📄 {message}", Colors.CYAN)

    @staticmethod
    def debug(message: str) -> None:
        """デバッグメッセージ"""
        Logger.print_colored(f"🔍 {message}", Colors.BLUE)


class ConfigManager:
    """設定ファイル管理クラス"""

    CONFIG_FILE = ".pr_agent.toml"
    BACKUP_FILE = ".pr_agent.toml.backup"

    def __init__(self):
        # wordディレクトリのconfigsを参照
        base_dir = Path(__file__).parent / "configs"
        self.config_dirs = {
            "custom": base_dir / "custom"
        }
        self.common_config_path = base_dir / "common.toml"

    def backup_current_config(self) -> bool:
        """現在の設定をバックアップ"""
        if Path(self.CONFIG_FILE).exists():
            shutil.copy(self.CONFIG_FILE, self.BACKUP_FILE)
            Logger.print_colored("📋 現在の設定をバックアップしました", Colors.YELLOW)
            return True
        return False

    def restore_config(self) -> bool:
        """設定を復元"""
        if Path(self.BACKUP_FILE).exists():
            shutil.copy(self.BACKUP_FILE, self.CONFIG_FILE)
            Logger.print_colored("♻️  設定を復元しました", Colors.GREEN)
            return True
        return False

    def get_available_configs(self) -> Dict[str, Dict[str, str]]:
        """利用可能な設定ファイル一覧を取得"""
        configs = {"custom": {}}

        for category, directory in self.config_dirs.items():
            if directory.exists():
                for file in directory.glob("*.toml"):
                    configs[category][file.stem] = str(file)

        return configs

    def list_configs(self) -> None:
        """利用可能な設定一覧を表示"""
        configs = self.get_available_configs()

        Logger.print_colored("📚 利用可能な設定ファイル", Colors.BLUE)
        print("─" * 50)

        category_info = [
            ("custom", "✨ カスタム (custom):", Colors.GREEN)
        ]

        for category, title, color in category_info:
            if configs[category]:
                Logger.print_colored(title, color)
                for name, path in configs[category].items():
                    print(f"  • {name:<30} → {path}")
                print()

    def resolve_config_path(self, config_name: str) -> Optional[str]:
        """設定名から実際のファイルパスを解決"""
        # 直接パス指定の場合
        if Path(config_name).exists():
            return config_name

        # 設定名での検索
        configs = self.get_available_configs()
        all_configs = {}
        for category_configs in configs.values():
            all_configs.update(category_configs)

        if config_name in all_configs:
            return all_configs[config_name]

        # 部分マッチ検索
        matches = [path for name, path in all_configs.items() if config_name in name]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            Logger.warning(f"複数の設定がマッチしました: {', '.join(matches)}")
            return None

        return None

    def apply_config(self, config_path: str, custom_prompt: Optional[str] = None, api_config: Optional[Dict] = None) -> bool:
        """指定された設定ファイルを適用（共通設定とマージ）"""
        config_file = Path(config_path)

        if not config_file.exists():
            Logger.error(f"設定ファイルが見つかりません: {config_path}")
            return False

        self.backup_current_config()

        # 共通設定とカスタム設定をマージ
        merged_config = self._merge_configs(config_path)

        # API設定を追加
        if api_config:
            merged_config = self._inject_api_config(merged_config, api_config)

        # マージした設定を書き込み
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            toml.dump(merged_config, f)

        if custom_prompt:
            self._append_custom_prompt(custom_prompt)
            Logger.success(f"設定ファイルを適用しました: common.toml + {Path(config_path).name} + カスタムプロンプト")
        else:
            Logger.success(f"設定ファイルを適用しました: common.toml + {Path(config_path).name}")

        return True

    def create_default_config(self, custom_prompt: Optional[str] = None, api_config: Optional[Dict] = None) -> None:
        """デフォルト設定ファイルを作成（共通設定ベース）"""
        self.backup_current_config()

        # 共通設定を読み込み
        if self.common_config_path.exists():
            with open(self.common_config_path, 'r', encoding='utf-8') as f:
                common_config = toml.load(f)

            # API設定を追加
            if api_config:
                common_config = self._inject_api_config(common_config, api_config)

            # 共通設定を書き込み
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                toml.dump(common_config, f)

            if custom_prompt:
                self._append_custom_prompt(custom_prompt)
                Logger.info("共通設定 (common.toml) + カスタムプロンプトを適用しました")
            else:
                Logger.info("共通設定 (common.toml) を適用しました")
        else:
            # 共通設定がない場合は従来のテンプレートを使用
            config_template = self._get_default_config_template()
            if custom_prompt:
                config_content = config_template.format(
                    header="# PR-Agent デフォルト設定 + カスタムプロンプト",
                    extra_instructions=f'extra_instructions = """\n{custom_prompt}\n"""'
                )
            else:
                config_content = config_template.format(
                    header="# PR-Agent デフォルト設定",
                    extra_instructions=""
                )
            self._write_config_file(config_content)

    def handle_existing_config_with_prompt(self, custom_prompt: str) -> None:
        """既存設定にプロンプトを追加"""
        Logger.print_colored("🔄 既存の設定ファイルを発見しました", Colors.YELLOW)
        self._append_custom_prompt(custom_prompt)
        Logger.success("既存設定にカスタムプロンプトを追加しました")

    def _get_default_config_template(self) -> str:
        """デフォルト設定テンプレートを取得"""
        return """{header}

[config]
model = "gpt-4"
temperature = 0.2
response_language = "ja-JP"
max_model_tokens = 32000
reasoning_effort = "medium"

[pr_reviewer]
require_score_review = true
require_tests_review = true
require_estimate_effort_to_review = true
num_code_suggestions = 4
enable_review_labels_effort = true
enable_review_labels_security = true
{extra_instructions}

[pr_description]
publish_description = true
add_original_user_description = true
extra_instructions = ""

[pr_code_suggestions]
num_code_suggestions = 4
"""

    def _write_config_file(self, content: str) -> None:
        """設定ファイルを書き込み"""
        try:
            self.backup_current_config()
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            Logger.error(f"設定ファイル作成エラー: {str(e)}")
            raise

    def _append_custom_prompt(self, custom_prompt: str) -> None:
        """設定ファイルにカスタムプロンプトを追加"""
        config_file = Path(self.CONFIG_FILE)

        if not config_file.exists():
            Logger.warning("設定ファイルが存在しません")
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()

            content = self._inject_prompt_into_config(content, custom_prompt)

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(content)

            Logger.print_colored("📝 カスタムプロンプトを追加しました", Colors.CYAN)

        except Exception as e:
            Logger.error(f"プロンプト追加エラー: {str(e)}")

    def _inject_prompt_into_config(self, content: str, custom_prompt: str) -> str:
        """設定内容にプロンプトを注入"""
        if 'extra_instructions = """' in content:
            # 既存のextra_instructionsに追加
            return content.replace(
                'extra_instructions = """',
                f'extra_instructions = """\n{custom_prompt}\n\n--- 元の指示 ---\n'
            )
        elif '[pr_reviewer]' in content:
            # pr_reviewerセクションにextra_instructionsを追加
            return content.replace(
                '[pr_reviewer]',
                f'[pr_reviewer]\nextra_instructions = """\n{custom_prompt}\n"""'
            )
        else:
            # 新しくpr_reviewerセクションを追加
            return content + f'\n\n[pr_reviewer]\nextra_instructions = """\n{custom_prompt}\n"""\n'

    def _merge_configs(self, custom_config_path: str) -> Dict:
        """共通設定とカスタム設定をマージ"""
        # 共通設定を読み込み
        common_config = {}
        if self.common_config_path.exists():
            with open(self.common_config_path, 'r', encoding='utf-8') as f:
                common_config = toml.load(f)

        # カスタム設定を読み込み
        custom_config = {}
        if Path(custom_config_path).exists():
            with open(custom_config_path, 'r', encoding='utf-8') as f:
                custom_config = toml.load(f)

        # マージ（カスタム設定が優先）
        merged = self._deep_merge(common_config, custom_config)
        return merged

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """辞書を再帰的にマージ"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _inject_api_config(self, config: Dict, api_config: Dict) -> Dict:
        """API設定を設定ファイルに注入"""
        if 'config' not in config:
            config['config'] = {}

        if 'openai' not in config:
            config['openai'] = {}

        # OpenAI API Key
        if 'api_key' in api_config:
            config['config']['openai_key'] = api_config['api_key']
            config['openai']['key'] = api_config['api_key']

        # OpenAI Base URL (Azure OpenAI用)
        if 'base_url' in api_config:
            config['config']['ai_provider'] = 'openai'
            config['openai']['api_base'] = api_config['base_url']

        # User ID (Azure APIM用)
        if 'user_id' in api_config:
            config['openai']['user_id'] = api_config['user_id']

        # OpenAI Path
        if 'api_path' in api_config:
            config['openai']['path'] = api_config['api_path']

        # カスタムヘッダー (Azure OpenAIのapim-user-id等)
        if 'custom_headers' in api_config:
            config['config']['custom_headers'] = api_config['custom_headers']

        return config


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


class PRAgentRunner:
    """PR-Agent実行クラス"""

    @staticmethod
    def _inject_custom_ai_handler():
        """カスタムAIハンドラーをPR-Agentに注入"""
        try:
            # カスタムハンドラーをインポート
            import sys
            from pathlib import Path

            # wordディレクトリをパスに追加
            word_dir = Path(__file__).parent
            if str(word_dir.parent) not in sys.path:
                sys.path.insert(0, str(word_dir.parent))

            from word.ai_handlers.custom_ai_handler import CustomAzureAIHandler

            # PR-AgentのLiteLLMAIHandlerを置き換え
            from pr_agent.algo.ai_handlers import litellm_ai_handler

            # LiteLLMAIHandlerクラスをカスタムハンドラーで置き換え
            original_handler = litellm_ai_handler.LiteLLMAIHandler
            litellm_ai_handler.LiteLLMAIHandler = CustomAzureAIHandler

            # 他のモジュールからのインポートも置き換え
            import pr_agent.agent.pr_agent as pr_agent_module
            pr_agent_module.LiteLLMAIHandler = CustomAzureAIHandler

            Logger.print_colored("✅ カスタムAIハンドラーを注入しました (LiteLLMAIHandler -> CustomAzureAIHandler)", Colors.GREEN)
            return True

        except Exception as e:
            Logger.warning(f"カスタムAIハンドラーの注入に失敗: {str(e)}")
            Logger.warning("デフォルトのlitellmハンドラーを使用します")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    async def run(pr_url: str, command: str = "review", extra_args: Optional[List[str]] = None) -> bool:
        """PR-Agentを実行"""
        try:
            # カスタムAIハンドラーを注入
            PRAgentRunner._inject_custom_ai_handler()

            from pr_agent.agent.pr_agent import PRAgent

            Logger.print_colored("🚀 PR-Agent を実行しています...", Colors.BLUE)
            Logger.print_colored(f"   URL: {pr_url}", Colors.WHITE)
            Logger.print_colored(f"   コマンド: {command}", Colors.WHITE)

            agent = PRAgent()
            request_args = [command]
            if extra_args:
                request_args.extend(extra_args)

            result = await agent.handle_request(pr_url, request_args)

            if result:
                Logger.success("PR-Agent の実行が完了しました")
            else:
                Logger.warning("PR-Agent の実行でエラーが発生しました")

            return result

        except ImportError:
            Logger.error("PR-Agent がインストールされていません")
            Logger.print_colored("   pip install pr-agent でインストールしてください", Colors.WHITE)
            return False
        except Exception as e:
            Logger.error(f"エラーが発生しました: {str(e)}")
            return False


class ArgumentParser:
    """引数解析クラス"""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """引数パーサーを作成"""
        parser = argparse.ArgumentParser(
            description="PR-Agent カスタム実行ツール",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=ArgumentParser._get_usage_examples()
        )

        ArgumentParser._add_arguments(parser)
        return parser

    @staticmethod
    def _get_usage_examples() -> str:
        """使用例を取得"""
        return """
使用例:
  # セキュリティ特化レビュー
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c security-focused

  # パフォーマンス特化レビュー
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c performance-focused

  # カスタムプロンプト追加
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c security-focused --prompt "XSS脆弱性を重点チェック"

  # 設定一覧表示
  python pr_agent_runner.py --list

  # 設定復元
  python pr_agent_runner.py --restore
"""

    @staticmethod
    def _add_arguments(parser: argparse.ArgumentParser) -> None:
        """引数を追加"""
        parser.add_argument("-u", "--url", help="PR URL (GitHub, GitLab, Bitbucket等)")
        parser.add_argument("-c", "--config", help="設定ファイル名またはパス（任意、指定されない場合はデフォルト設定）")
        parser.add_argument("--command", default="review",
                          choices=["review", "describe", "improve", "ask", "generate_labels", "add_docs", "update_changelog"],
                          help="実行するコマンド (デフォルト: review)")
        parser.add_argument("--question", help="askコマンド用の質問")
        parser.add_argument("--prompt", help="カスタムプロンプト（extra_instructionsに追加）")
        parser.add_argument("--list", action="store_true", help="利用可能な設定一覧を表示")
        parser.add_argument("--restore", action="store_true", help="設定を元に戻す")
        parser.add_argument("--dry-run", action="store_true", help="設定適用のみ（PR-Agent実行なし）")


class PRAgentCLI:
    """PR-Agent CLIメインクラス"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.url_validator = UrlValidator()
        self.pr_agent_runner = PRAgentRunner()

    def run(self) -> None:
        """メイン実行"""
        parser = ArgumentParser.create_parser()
        args = parser.parse_args()

        try:
            if args.list:
                self.config_manager.list_configs()
                return

            if args.restore:
                self._handle_restore()
                return

            if not args.url:
                Logger.error("PR URLが指定されていません (-u オプション)")
                parser.print_help()
                sys.exit(1)

            self._validate_url(args.url)
            self._handle_config(args)

            if args.dry_run:
                Logger.debug("Dry-run モード: 設定適用のみ完了")
                return

            self._run_pr_agent(args)

        except KeyboardInterrupt:
            Logger.warning("\n実行がキャンセルされました")
            sys.exit(1)
        except Exception as e:
            Logger.error(f"予期しないエラー: {str(e)}")
            sys.exit(1)

    def _handle_restore(self) -> None:
        """設定復元を処理"""
        if self.config_manager.restore_config():
            Logger.success("設定を復元しました")
        else:
            Logger.error("バックアップファイルが見つかりません")

    def _validate_url(self, url: str) -> None:
        """URL検証"""
        if not self.url_validator.validate_pr_url(url):
            Logger.warning("PR URLの形式が正しくない可能性があります")
            Logger.print_colored(f"   指定されたURL: {url}", Colors.WHITE)

    def _handle_config(self, args) -> None:
        """設定処理"""
        if args.config:
            self._apply_specified_config(args.config, args.prompt)
        else:
            self._handle_default_config(args.prompt)

    def _apply_specified_config(self, config_name: str, custom_prompt: Optional[str]) -> None:
        """指定された設定を適用"""
        config_path = self.config_manager.resolve_config_path(config_name)
        if not config_path:
            Logger.error(f"設定ファイルが見つかりません: {config_name}")
            Logger.print_colored("利用可能な設定:", Colors.WHITE)
            self.config_manager.list_configs()
            sys.exit(1)

        if not self.config_manager.apply_config(config_path, custom_prompt):
            sys.exit(1)

    def _handle_default_config(self, custom_prompt: Optional[str]) -> None:
        """デフォルト設定を処理"""
        Logger.info("デフォルト設定を使用します")

        if Path(ConfigManager.CONFIG_FILE).exists() and custom_prompt:
            self.config_manager.handle_existing_config_with_prompt(custom_prompt)
        else:
            self.config_manager.create_default_config(custom_prompt)
            if custom_prompt:
                Logger.success("デフォルト設定 + カスタムプロンプトを作成しました")
            else:
                Logger.success("デフォルト設定ファイルを作成しました")

    def _run_pr_agent(self, args) -> None:
        """PR-Agentを実行"""
        Logger.print_colored("🎯 PR-Agent を実行します", Colors.BOLD)
        Logger.print_colored(f"   URL: {args.url}", Colors.WHITE)
        Logger.print_colored(f"   コマンド: {args.command}", Colors.WHITE)

        extra_args = []
        if args.command == "ask" and args.question:
            extra_args.append(args.question)

        result = asyncio.run(self.pr_agent_runner.run(args.url, args.command, extra_args))
        if result:
            Logger.print_colored("🎉 完了しました！", Colors.GREEN)
        else:
            sys.exit(1)


def main():
    """エントリーポイント"""
    cli = PRAgentCLI()
    cli.run()


if __name__ == "__main__":
    main()