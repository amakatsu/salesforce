#!/usr/bin/env python3
"""
PR-Agent 実行モジュール
PR-Agentのカスタムハンドラー注入と実行を担当
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional

from .utils import Logger, Colors


class PRAgentRunner:
    """PR-Agent実行クラス"""

    @staticmethod
    def _inject_custom_ai_handler():
        """カスタムAIハンドラーをPR-Agentに注入"""
        try:
            # カスタムハンドラーをインポート
            # wordディレクトリをパスに追加
            word_dir = Path(__file__).parent.parent
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

            # 成功ログは省略（ノイズ削減）
            return True

        except Exception as e:
            Logger.warning(f"カスタムAIハンドラーの注入に失敗: {str(e)}")
            Logger.warning("デフォルトのlitellmハンドラーを使用します")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _determine_gitlab_url(pr_url: str, gitlab_url: Optional[str]) -> Optional[str]:
        # 優先順位: 1. ユーザー入力(gitlab_url) > 2. PR URLから抽出 > 3. common.toml
        if gitlab_url:
            return gitlab_url.rstrip('/') if gitlab_url else None

        import re
        match = re.match(r'(https?://[^/]+)', pr_url)
        if match:
            extracted = match.group(1).rstrip('/')
            return extracted

        return None

    @staticmethod
    def _resolve_config_path(project_root: Path, settings_path: Optional[str]) -> Path:
        if settings_path:
            return Path(settings_path).resolve(strict=False)
        return project_root / ".pr_agent.toml"

    @staticmethod
    def _write_gitlab_url_to_config(config_path: Path, gitlab_url: str) -> None:
        import toml
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = toml.load(f)
        else:
            config_data = {}

        if 'gitlab' not in config_data:
            config_data['gitlab'] = {}
        config_data['gitlab']['url'] = gitlab_url

        with open(config_path, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)

    @staticmethod
    def _load_settings(config_path: Path):
        from pr_agent.config_loader import get_settings
        import importlib
        import pr_agent.config_loader

        importlib.reload(pr_agent.config_loader)

        settings = get_settings()
        if config_path.exists():
            settings.reload()
            settings.load_file(str(config_path))
        return settings

    @staticmethod
    def _reset_logger(settings, pr_agent_log_level: str, debug_level: Optional[int]) -> str:
        from pr_agent.log import setup_logger
        final_log_level = settings.get("config.log_level") if settings.get("config.log_level") else pr_agent_log_level
        if debug_level is not None:
            final_log_level = pr_agent_log_level
        setup_logger(level=final_log_level)
        return final_log_level

    @staticmethod
    def _attach_loguru_handler(session_id: Optional[str], final_log_level: str) -> Optional[int]:
        from pr_agent.log import get_logger
        if not session_id:
            return None

        pr_logger = get_logger()

        def loguru_to_session_buffer(message):
            """loguruのログをセッションバッファに追加"""
            record = message.record
            level = record["level"].name
            text = record["message"]

            from .utils import Colors
            color_map = {
                "DEBUG": Colors.BLUE,
                "INFO": Colors.CYAN,
                "SUCCESS": Colors.GREEN,
                "WARNING": Colors.YELLOW,
                "ERROR": Colors.RED,
                "CRITICAL": Colors.RED
            }
            color = color_map.get(level, Colors.WHITE)
            Logger._log_to_buffer(level, text, color)

        handler_id = pr_logger.add(loguru_to_session_buffer, level=final_log_level, format="{message}")
        return handler_id

    @staticmethod
    async def run(
        pr_url: str,
        command: str = "review",
        extra_args: Optional[List[str]] = None,
        settings_path: Optional[str] = None,
        gitlab_url: Optional[str] = None,
        debug_level: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """PR-Agentを実行

        Args:
            session_id: セッションID（Streamlitなどのマルチセッション環境でログを分離するため）
        """
        # セッションIDを設定（ログ分離のため）
        if session_id:
            Logger.set_session(session_id)

        resolved_path = Path(__file__).resolve()
        if len(resolved_path.parents) >= 3:
            project_root = resolved_path.parents[2]
        else:
            project_root = Path.cwd()

        original_cwd = Path.cwd()
        changed_cwd = False

        try:
            # デバッグレベル設定（ツールのログ出力 + PR-Agentログレベル）
            pr_agent_log_level = "WARNING"  # デフォルト: 警告以上のみ
            if debug_level is not None:
                Logger.set_debug_level(debug_level)
                # debug_levelに応じてPR-Agentのログレベルを設定
                if debug_level >= 2:
                    pr_agent_log_level = "DEBUG"  # 詳細ログ
                elif debug_level >= 1:
                    pr_agent_log_level = "INFO"   # 情報ログ
                else:
                    pr_agent_log_level = "ERROR"  # エラーのみ

            if original_cwd != project_root:
                os.chdir(project_root)
                changed_cwd = True

            # カスタムAIハンドラーを注入
            PRAgentRunner._inject_custom_ai_handler()

            # 1) GitLabプロバイダーを強制設定（URL判定前に設定を読み込ませる）
            os.environ['CONFIG__GIT_PROVIDER'] = 'gitlab'

            # 2) GitLab URLを決定
            determined_gitlab_url = PRAgentRunner._determine_gitlab_url(pr_url, gitlab_url)
            if determined_gitlab_url and not determined_gitlab_url.startswith(('http://', 'https://')):
                determined_gitlab_url = f'https://{determined_gitlab_url}'

            # 3) 設定ファイルパスを決定
            config_path = PRAgentRunner._resolve_config_path(project_root, settings_path)

            # 4) GitLab URLが決定された場合、設定ファイルに書き出す
            if determined_gitlab_url:
                PRAgentRunner._write_gitlab_url_to_config(config_path, determined_gitlab_url)

            # 5) PR-Agentに設定ファイルを指示
            os.environ['PR_AGENT_SETTINGS_PATH'] = str(config_path)
            if not config_path.exists():
                Logger.warning(f"設定ファイルが存在しません: {config_path}")

            from pr_agent.agent.pr_agent import PRAgent

            # 6-7) Dynaconf設定をリロードしてtomlを反映
            settings = PRAgentRunner._load_settings(config_path)

            # 8) 設定の最終適用はDynaconfの読み込み結果に委ねる

            # 9-10) PR-Agentロガーを再初期化し、必要ならセッションに流す
            final_log_level = PRAgentRunner._reset_logger(settings, pr_agent_log_level, debug_level)
            loguru_handler_id = PRAgentRunner._attach_loguru_handler(session_id, final_log_level)
            # 11) PR-Agent本体を実行
            Logger.print_colored("🚀 PR-Agent を実行しています...", Colors.BLUE)

            agent = PRAgent()
            request_args = [command]
            if extra_args:
                request_args.extend(extra_args)

            result = await agent.handle_request(pr_url, request_args)

            if result:
                Logger.success("PR-Agent の実行が完了しました")
            else:
                Logger.warning("PR-Agent の実行でエラーが発生しました")
                Logger.error("詳細: handle_request が False を返しました")

            return result

        except ImportError as e:
            Logger.error("PR-Agent がインストールされていません")
            Logger.print_colored("   pip install pr-agent でインストールしてください", Colors.WHITE)
            import traceback
            Logger.print_colored(f"\n{traceback.format_exc()}", Colors.RED)
            return False
        except Exception as e:
            Logger.error(f"エラーが発生しました: {str(e)}")
            Logger.error(f"エラー種別: {type(e).__name__}")

            # トレースバックを表示
            import traceback
            Logger.print_colored("\n=== エラー詳細 ===", Colors.RED)
            Logger.print_colored(traceback.format_exc(), Colors.RED)
            Logger.print_colored("==================\n", Colors.RED)

            # リクエスト情報を表示
            return False
        finally:
            # loguruハンドラーを削除（セッション間でログが混在しないように）
            if loguru_handler_id is not None:
                try:
                    from pr_agent.log import get_logger
                    get_logger().remove(loguru_handler_id)
                except Exception:
                    pass  # 削除に失敗しても続行
            if changed_cwd:
                os.chdir(original_cwd)

    @staticmethod
    def run_sync(
        pr_url: str,
        command: str = "review",
        extra_args: Optional[List[str]] = None,
        settings_path: Optional[str] = None,
        gitlab_url: Optional[str] = None,
        debug_level: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """PR-Agentを同期実行（Web環境用）

        Streamlit等の既存イベントループ内で動作する環境向けの同期ラッパー。
        既にイベントループが実行中の場合はnest_asyncioを使用して実行。

        Args:
            session_id: セッションID（Streamlitなどのマルチセッション環境でログを分離するため）
        """
        try:
            # 既存のイベントループをチェック
            try:
                loop = asyncio.get_running_loop()
                # イベントループが既に実行中の場合
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(PRAgentRunner.run(pr_url, command, extra_args, settings_path, gitlab_url, debug_level, session_id))
            except RuntimeError:
                # イベントループが実行中でない場合（通常のCLI実行）
                return asyncio.run(PRAgentRunner.run(pr_url, command, extra_args, settings_path, gitlab_url, debug_level, session_id))
        except ImportError:
            Logger.error("nest_asyncio がインストールされていません")
            Logger.print_colored("   pip install nest_asyncio でインストールしてください", Colors.WHITE)
            return False
        except Exception as e:
            Logger.error(f"同期実行でエラーが発生しました: {str(e)}")
            import traceback
            Logger.print_colored(traceback.format_exc(), Colors.RED)
            return False
