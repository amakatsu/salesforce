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
    """設定ファイル管理クラス（セッション分離対応）"""

    def __init__(self, session_id: Optional[str] = None):
        resolved_path = Path(__file__).resolve()

        # プロジェクトルート（wordディレクトリの一つ上）を推定
        if len(resolved_path.parents) >= 3:
            self.project_root = resolved_path.parents[2]
        else:
            self.project_root = Path.cwd()

        # 各セッション用の設定ファイルを分離する（同一プロセス内の混線防止）
        self.session_id = session_id
        self.global_config_file = self.project_root / ".pr_agent.toml"
        self.global_backup_file = self.project_root / ".pr_agent.toml.backup"
        self.sessions_dir = self.project_root / ".pr_agent_sessions"

        if self.session_id:
            # セッション単位の設定ファイル（ユーザ間のトークン混線を防ぐ）
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = self.sessions_dir / f"{self.session_id}.toml"
            self.backup_file = self.sessions_dir / f"{self.session_id}.toml.backup"
        else:
            # セッションIDがない場合は共有設定ファイルを使用
            self.config_file = self.global_config_file
            self.backup_file = self.global_backup_file

        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # 共有設定をセッション設定に同期（古いタブでも最新設定を反映する）
        self._seed_session_config()

        # wordディレクトリの共通設定
        configs_base = resolved_path.parents[1] / "configs"
        self.common_config_path = configs_base / "common.toml"

    def _seed_session_config(self) -> None:
        """共有設定をベースにセッションファイルを作成／更新（初期値の引き継ぎ用）"""
        if not self.session_id:
            return

        if not self.config_file.exists():
            if self.global_config_file.exists():
                shutil.copy(self.global_config_file, self.config_file)
            else:
                self.config_file.touch()
        else:
            # セッションファイルが古い可能性があるため、共有設定が新しければコピー
            try:
                session_mtime = self.config_file.stat().st_mtime
                global_mtime = self.global_config_file.stat().st_mtime if self.global_config_file.exists() else 0
                if global_mtime > session_mtime:
                    shutil.copy(self.global_config_file, self.config_file)
            except FileNotFoundError:
                pass

    def _sync_shared_config(self) -> None:
        """セッションファイルでマージした結果を .pr_agent.toml に反映"""
        # 共有ファイルへの同期は競合要因になるため無効化
        return

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
            self._sync_shared_config()
            return True
        return False

    def apply_config(self, config_path: str, custom_prompt: Optional[str] = None, api_config: Optional[Dict] = None, gitlab_url: Optional[str] = None, gitlab_token: Optional[str] = None, verbosity: Optional[int] = None, preview_mode: bool = False, pr_command: Optional[str] = None, global_settings: Optional[Dict] = None) -> bool:
        """指定された設定ファイルを適用（共通設定とマージ）"""
        config_file = Path(config_path)

        if not config_file.exists():
            Logger.error(f"設定ファイルが見つかりません: {config_path}")
            return False

        self.backup_current_config()

        merged_config = self._merge_configs(config_path)
        self._finalize_and_write(
            merged_config, custom_prompt=custom_prompt, api_config=api_config,
            gitlab_url=gitlab_url, gitlab_token=gitlab_token,
            verbosity=verbosity, preview_mode=preview_mode, pr_command=pr_command,
            global_settings=global_settings,
        )

        source_label = f"common.toml + {config_file.name}"
        if custom_prompt:
            Logger.success(f"設定ファイルを適用しました: {source_label} + カスタムプロンプト")
        else:
            Logger.success(f"設定ファイルを適用しました: {source_label}")

        Logger.debug(f".pr_agent.toml 出力先: {self.config_file}")
        return True

    def create_default_config(self, custom_prompt: Optional[str] = None, api_config: Optional[Dict] = None, gitlab_url: Optional[str] = None, gitlab_token: Optional[str] = None, verbosity: Optional[int] = None, preview_mode: bool = False, pr_command: Optional[str] = None, global_settings: Optional[Dict] = None) -> None:
        """デフォルト設定ファイルを作成（共通設定ベース）"""
        self.backup_current_config()

        if self.common_config_path.exists():
            with open(self.common_config_path, 'r', encoding='utf-8') as f:
                base_config = toml.load(f)

            self._finalize_and_write(
                base_config, custom_prompt=custom_prompt, api_config=api_config,
                gitlab_url=gitlab_url, gitlab_token=gitlab_token,
                verbosity=verbosity, preview_mode=preview_mode, pr_command=pr_command,
                global_settings=global_settings,
            )

            if custom_prompt:
                Logger.info("共通設定 (common.toml) + カスタムプロンプトを適用しました")
            else:
                Logger.info("共通設定 (common.toml) を適用しました")
        else:
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

    def _finalize_and_write(self, config: Dict, *, custom_prompt: Optional[str] = None,
                            api_config: Optional[Dict] = None, gitlab_url: Optional[str] = None,
                            gitlab_token: Optional[str] = None, verbosity: Optional[int] = None,
                            preview_mode: bool = False, pr_command: Optional[str] = None,
                            global_settings: Optional[Dict] = None) -> None:
        """設定にランタイム値を注入し、ファイルに書き出す。

        apply_config / create_default_config の共通後処理。
        「TOMLを読む → この関数を通す → 実行」の流れで統一される。

        global_settings（UIからの明示的な設定）はTOMLの既存値を上書きする。
        ユーザが画面上で変更した値を最終出力に確実に反映するため。
        """
        cfg = config.setdefault('config', {})
        cfg.setdefault('verbosity_level', 2)

        if global_settings:
            self._inject_global_settings(config, global_settings)
        if api_config:
            self._inject_api_config(config, api_config)
        if gitlab_url:
            self._inject_gitlab_url(config, gitlab_url)
        if gitlab_token:
            self._inject_gitlab_token(config, gitlab_token)
        if verbosity is not None:
            self._inject_verbosity(config, verbosity)
        if preview_mode and pr_command:
            Logger.info(f"🔍 プレビューモードが有効です（コマンド: {pr_command}）")
            self._inject_preview_mode(config, pr_command)
        elif preview_mode:
            Logger.warning("⚠️ プレビューモードが指定されていますが、コマンドが不明です")

        with open(self.config_file, 'w', encoding='utf-8') as f:
            toml.dump(config, f)

        if custom_prompt:
            self._append_custom_prompt(custom_prompt)

    def handle_existing_config_with_prompt(self, custom_prompt: str) -> None:
        """既存設定にプロンプトを追加"""
        Logger.print_colored("🔄 既存の設定ファイルを発見しました", Colors.YELLOW)
        self._append_custom_prompt(custom_prompt)
        Logger.success("既存設定にカスタムプロンプトを追加しました")

    def _get_default_config_template(self) -> str:
        """デフォルト設定テンプレートを取得"""
        # common.toml が存在しない場合のフォールバックテンプレート
        return """{header}

[config]
model = "PBkBKGPT0SpkSub001OAI001MDL015"
temperature = 1.0
response_language = "ja-JP"
max_model_tokens = 128000
custom_model_max_tokens = 128000
reasoning_effort = "low"
verbosity = "low"
verbosity_level = 2
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
        cfg = config.setdefault('config', {})
        cfg['git_provider'] = 'gitlab'

        provider = api_config.get('provider', 'openai').lower()

        if provider == 'gemini':
            cfg['ai_provider'] = 'google'
            gemini = config.setdefault('gemini', {})

            if 'api_key' in api_config:
                cfg['gemini_key'] = api_config['api_key']
                gemini['key'] = api_config['api_key']

            cfg['model'] = api_config.get('model', 'gemini/gemini-2.0-flash-exp')
            cfg['custom_model_max_tokens'] = 1000000

            Logger.info(f"Gemini設定を適用: モデル={cfg['model']}, max_tokens=1000000")

        else:
            openai = config.setdefault('openai', {})
            cfg['ai_provider'] = 'openai'

            if 'api_key' in api_config:
                cfg['openai_key'] = api_config['api_key']
                openai['key'] = api_config['api_key']
            if 'base_url' in api_config:
                openai['api_base'] = api_config['base_url']
            if 'user_id' in api_config:
                openai['user_id'] = api_config['user_id']
            if 'api_path' in api_config:
                openai['path'] = api_config['api_path']
            if 'custom_headers' in api_config:
                cfg['custom_headers'] = api_config['custom_headers']

            Logger.info(f"OpenAI設定を適用: プロバイダー={cfg.get('ai_provider', 'openai')}")

        return config

    def _inject_gitlab_url(self, config: Dict, gitlab_url: str) -> Dict:
        """GitLab URLを設定ファイルに注入"""
        normalized_url = gitlab_url.rstrip('/')
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = f'https://{normalized_url}'

        config.setdefault('gitlab', {})['url'] = normalized_url
        Logger.info(f"GitLab URL設定を適用: {normalized_url}")
        return config

    def _inject_gitlab_token(self, config: Dict, gitlab_token: str) -> Dict:
        """GitLab Tokenを設定ファイルに注入"""
        config.setdefault('gitlab', {})['personal_access_token'] = gitlab_token
        Logger.info("GitLab Token設定を適用")
        return config

    def _inject_verbosity(self, config: Dict, verbosity: int) -> Dict:
        """Verbosity設定を設定ファイルに注入（TOMLに既存値があればそちらを優先）"""
        config.setdefault('config', {}).setdefault('verbosity_level', verbosity)
        Logger.info(f"Verbosity設定を適用: verbosity_level={config['config']['verbosity_level']}")
        return config

    def _inject_preview_mode(self, config: Dict, pr_command: str) -> Dict:
        """プレビューモード設定を設定ファイルに注入（GitLabへの投稿を無効化）"""
        cfg = config.setdefault('config', {})
        cfg['publish_output'] = False
        cfg['publish_output_progress'] = False
        Logger.info("プレビューモード設定を適用: publish_output=False")
        return config

    def _inject_global_settings(self, config: Dict, global_settings: Dict) -> Dict:
        """グローバル設定をconfigセクションに注入（UIで明示的に設定された値で上書き）"""
        cfg = config.setdefault('config', {})
        for key, value in global_settings.items():
            cfg[key] = value
        Logger.info(f"グローバル設定を適用: {list(global_settings.keys())}")
        return config
