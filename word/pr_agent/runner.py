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

            Logger.print_colored("✅ カスタムAIハンドラーを注入しました (LiteLLMAIHandler -> CustomAzureAIHandler)", Colors.GREEN)
            return True

        except Exception as e:
            Logger.warning(f"カスタムAIハンドラーの注入に失敗: {str(e)}")
            Logger.warning("デフォルトのlitellmハンドラーを使用します")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    async def run(
        pr_url: str,
        command: str = "review",
        extra_args: Optional[List[str]] = None,
        settings_path: Optional[str] = None
    ) -> bool:
        """PR-Agentを実行"""
        resolved_path = Path(__file__).resolve()
        if len(resolved_path.parents) >= 3:
            project_root = resolved_path.parents[2]
        else:
            project_root = Path.cwd()

        original_cwd = Path.cwd()
        changed_cwd = False

        try:
            if original_cwd != project_root:
                os.chdir(project_root)
                changed_cwd = True
                Logger.debug(f"PR-Agent設定ディレクトリを {project_root} に切り替えました")

            # カスタムAIハンドラーを注入
            PRAgentRunner._inject_custom_ai_handler()

            # GitLabプロバイダーを強制設定（URL判定前に設定を読み込ませる）
            os.environ['CONFIG__GIT_PROVIDER'] = 'gitlab'

            if settings_path:
                config_path = Path(settings_path).resolve(strict=False)
            else:
                config_path = project_root / ".pr_agent.toml"

            os.environ['PR_AGENT_SETTINGS_PATH'] = str(config_path)
            if not config_path.exists():
                Logger.warning(f"設定ファイルが存在しません: {config_path}")
            Logger.info(f"設定ファイルを使用: {config_path}")

            from pr_agent.agent.pr_agent import PRAgent
            from pr_agent.config_loader import get_settings
            import toml

            # 設定を強制的に事前読み込み
            settings = get_settings()
            settings.config.git_provider = 'gitlab'

            # TOMLファイルから直接extra_instructionsを読み込み
            Logger.info("=== PR-Agent 設定確認 ===")
            try:
                # TOMLファイルを直接読み込み
                toml_config = toml.load(str(config_path))
                Logger.info(f"TOMLファイル読み込み成功: {config_path}")

                # pr_reviewerセクションのextra_instructionsを取得
                if 'pr_reviewer' in toml_config and 'extra_instructions' in toml_config['pr_reviewer']:
                    extra_inst_from_file = toml_config['pr_reviewer']['extra_instructions']
                    Logger.info(f"TOMLファイルからextra_instructions読み込み: 長さ={len(extra_inst_from_file)}")

                    # dynaconf経由の設定を確認
                    extra_inst_dynaconf = settings.pr_reviewer.extra_instructions
                    Logger.info(f"dynaconf経由のextra_instructions: 長さ={len(extra_inst_dynaconf) if extra_inst_dynaconf else 0}")

                    # dynaconfで読み込めていない場合は直接設定
                    if not extra_inst_dynaconf or len(extra_inst_dynaconf) == 0:
                        Logger.warning("dynaconfがextra_instructionsを読み込めていません。直接設定します。")
                        settings.pr_reviewer.extra_instructions = extra_inst_from_file
                        Logger.info(f"✅ extra_instructionsを直接設定しました（長さ: {len(extra_inst_from_file)}）")
                        Logger.info(f"プレビュー: {extra_inst_from_file[:200]}...")
                    else:
                        Logger.info("✅ dynaconfでextra_instructionsが正しく読み込まれています")

                else:
                    Logger.warning("TOMLファイルにpr_reviewer.extra_instructionsが見つかりません")

            except Exception as e:
                Logger.error(f"TOML読み込みエラー: {str(e)}")
                import traceback
                Logger.error(traceback.format_exc())

            Logger.info("==========================")

            # GitLab Tokenを環境変数から取得
            gitlab_token = os.getenv('GITLAB_TOKEN', '')
            if gitlab_token:
                if not hasattr(settings, 'gitlab'):
                    settings.gitlab = {}
                settings.gitlab.personal_access_token = gitlab_token
                Logger.info("GitLab Token設定完了")
            else:
                Logger.warning("GITLAB_TOKEN環境変数が設定されていません")

            Logger.info(f"Git Provider強制設定: {settings.config.git_provider}")

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
                Logger.error("詳細: handle_request が False を返しました")

            return result

        except ImportError as e:
            Logger.error("PR-Agent がインストールされていません")
            Logger.print_colored("   pip install pr-agent でインストールしてください", Colors.WHITE)
            Logger.debug(f"ImportError詳細: {str(e)}")
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
            Logger.debug("リクエスト情報:")
            Logger.debug(f"  - URL: {pr_url}")
            Logger.debug(f"  - コマンド: {command}")
            Logger.debug(f"  - 追加引数: {extra_args}")

            return False
        finally:
            if changed_cwd:
                os.chdir(original_cwd)
                Logger.debug(f"作業ディレクトリを復元: {original_cwd}")

    @staticmethod
    def run_sync(
        pr_url: str,
        command: str = "review",
        extra_args: Optional[List[str]] = None,
        settings_path: Optional[str] = None
    ) -> bool:
        """PR-Agentを同期実行（Web環境用）

        Streamlit等の既存イベントループ内で動作する環境向けの同期ラッパー。
        既にイベントループが実行中の場合はnest_asyncioを使用して実行。
        """
        try:
            # 既存のイベントループをチェック
            try:
                loop = asyncio.get_running_loop()
                # イベントループが既に実行中の場合
                import nest_asyncio
                nest_asyncio.apply()
                Logger.print_colored("🔄 既存イベントループを検出、nest_asyncioを適用", Colors.YELLOW)
                return asyncio.run(PRAgentRunner.run(pr_url, command, extra_args, settings_path))
            except RuntimeError:
                # イベントループが実行中でない場合（通常のCLI実行）
                return asyncio.run(PRAgentRunner.run(pr_url, command, extra_args, settings_path))
        except ImportError:
            Logger.error("nest_asyncio がインストールされていません")
            Logger.print_colored("   pip install nest_asyncio でインストールしてください", Colors.WHITE)
            return False
        except Exception as e:
            Logger.error(f"同期実行でエラーが発生しました: {str(e)}")
            import traceback
            Logger.print_colored(traceback.format_exc(), Colors.RED)
            return False
