#!/usr/bin/env python3
"""
PR-Agent 設定管理モジュール
TOML設定ファイルの読み込み、マージ、適用を担当
"""

import shutil
import toml
from pathlib import Path
from typing import Dict, Optional

from .utils import Logger, Colors


class ConfigManager:
    """設定ファイル管理クラス"""

    def __init__(self):
        resolved_path = Path(__file__).resolve()

        # プロジェクトルート（wordディレクトリの一つ上）を推定
        if len(resolved_path.parents) >= 3:
            self.project_root = resolved_path.parents[2]
        else:
            self.project_root = Path.cwd()

        self.config_file = self.project_root / ".pr_agent.toml"
        self.backup_file = self.project_root / ".pr_agent.toml.backup"

        # wordディレクトリのconfigsを参照
        base_dir = resolved_path.parents[1] / "configs"
        self.config_dirs = {
            "custom": base_dir / "custom"
        }
        self.common_config_path = base_dir / "common.toml"

    def backup_current_config(self) -> bool:
        """現在の設定をバックアップ"""
        if self.config_file.exists():
            shutil.copy(self.config_file, self.backup_file)
            Logger.print_colored("📋 現在の設定をバックアップしました", Colors.YELLOW)
            return True
        return False

    def restore_config(self) -> bool:
        """設定を復元"""
        if self.backup_file.exists():
            shutil.copy(self.backup_file, self.config_file)
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
        with open(self.config_file, 'w', encoding='utf-8') as f:
            toml.dump(merged_config, f)

        if custom_prompt:
            self._append_custom_prompt(custom_prompt)
            Logger.success(f"設定ファイルを適用しました: common.toml + {Path(config_path).name} + カスタムプロンプト")
        else:
            Logger.success(f"設定ファイルを適用しました: common.toml + {Path(config_path).name}")

        Logger.debug(f".pr_agent.toml 出力先: {self.config_file}")

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
            with open(self.config_file, 'w', encoding='utf-8') as f:
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

        Logger.debug(f".pr_agent.toml 出力先: {self.config_file}")

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
git_provider = "gitlab"

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
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            Logger.error(f"設定ファイル作成エラー: {str(e)}")
            raise

    def _append_custom_prompt(self, custom_prompt: str) -> None:
        """設定ファイルにカスタムプロンプトを追加"""
        if not self.config_file.exists():
            Logger.warning("設定ファイルが存在しません")
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                content = f.read()

            content = self._inject_prompt_into_config(content, custom_prompt)

            with open(self.config_file, "w", encoding="utf-8") as f:
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
            elif (
                key == "extra_instructions"
                and isinstance(result.get(key), str)
                and isinstance(value, str)
            ):
                base_instr = result.get(key, "").strip()
                custom_instr = value.strip()
                if base_instr and custom_instr:
                    combined = f"{custom_instr}\n\n--- 共通指示 ---\n{base_instr}"
                elif custom_instr:
                    combined = custom_instr
                else:
                    combined = base_instr
                result[key] = combined
            else:
                result[key] = value
        return result

    def _inject_api_config(self, config: Dict, api_config: Dict) -> Dict:
        """API設定を設定ファイルに注入 (OpenAI/Gemini対応)"""
        if 'config' not in config:
            config['config'] = {}

        # GitLabを明示的に指定（PR-AgentのURL判定をオーバーライド）
        config['config']['git_provider'] = 'gitlab'

        # プロバイダー判定（デフォルトはopenai）
        provider = api_config.get('provider', 'openai').lower()

        if provider == 'gemini':
            # Gemini設定
            config['config']['ai_provider'] = 'google'

            if 'gemini' not in config:
                config['gemini'] = {}

            # Gemini API Key
            if 'api_key' in api_config:
                config['config']['gemini_key'] = api_config['api_key']
                config['gemini']['key'] = api_config['api_key']

            # Geminiモデル指定
            if 'model' in api_config:
                config['config']['model'] = api_config['model']
            else:
                # デフォルトモデル
                config['config']['model'] = 'gemini/gemini-2.0-flash-exp'

            Logger.info(f"Gemini設定を適用: モデル={config['config']['model']}")

        else:
            # OpenAI設定（既存のロジック）
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

            Logger.info(f"OpenAI設定を適用: プロバイダー={config['config'].get('ai_provider', 'openai')}")

        return config
