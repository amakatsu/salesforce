#!/usr/bin/env python3
"""
PR-Agent CLI ツール
独自ホスティングのGitLab URLに対応
"""

import argparse
import sys
from pathlib import Path

# wordディレクトリをパスに追加
word_dir = Path(__file__).parent
if str(word_dir) not in sys.path:
    sys.path.insert(0, str(word_dir))

from pr_agent import ConfigManager, PRAgentRunner, UrlValidator, Logger, Colors


def main():
    parser = argparse.ArgumentParser(
        description="PR-Agent CLI - GitLab PR レビューツール（独自ホスティング対応）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 標準のGitLab.com PR
  python pr_agent_cli.py review https://gitlab.com/org/repo/-/merge_requests/123

  # 独自ホスティングのGitLab PR
  python pr_agent_cli.py review https://git.example.com/org/repo/-/merge_requests/123 --gitlab-url https://git.example.com

  # 設定ファイル適用後にレビュー
  python pr_agent_cli.py apply-config educational
  python pr_agent_cli.py review https://gitlab.com/org/repo/-/merge_requests/123

環境変数:
  GITLAB_TOKEN       - GitLab Personal Access Token
  OPENAI_API_KEY     - OpenAI API Key (またはAzure OpenAI)
  OPENAI_BASE_URL    - Azure OpenAI Base URL (オプション)
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # apply-config コマンド
    apply_parser = subparsers.add_parser("apply-config", help="設定ファイルを適用")
    apply_parser.add_argument("config_name", help="設定名（例: educational）")
    apply_parser.add_argument("--prompt", help="カスタムプロンプト")
    apply_parser.add_argument("--gitlab-url", help="独自ホスティングのGitLab URL（例: https://git.example.com）")

    # list-configs コマンド
    subparsers.add_parser("list-configs", help="利用可能な設定一覧を表示")

    # review コマンド
    review_parser = subparsers.add_parser("review", help="PRをレビュー")
    review_parser.add_argument("pr_url", help="PR URL")
    review_parser.add_argument("--gitlab-url", help="独自ホスティングのGitLab URL（例: https://git.example.com）")
    review_parser.add_argument("--settings", help="設定ファイルパス")
    review_parser.add_argument("--debug-level", type=int, choices=[0, 1, 2, 3], default=1,
                               help="デバッグレベル (0:エラーのみ, 1:情報, 2:デバッグ, 3:HTTP詳細)")

    # describe コマンド
    describe_parser = subparsers.add_parser("describe", help="PR説明を生成")
    describe_parser.add_argument("pr_url", help="PR URL")
    describe_parser.add_argument("--gitlab-url", help="独自ホスティングのGitLab URL（例: https://git.example.com）")
    describe_parser.add_argument("--settings", help="設定ファイルパス")
    describe_parser.add_argument("--debug-level", type=int, choices=[0, 1, 2, 3], default=1,
                               help="デバッグレベル (0:エラーのみ, 1:情報, 2:デバッグ, 3:HTTP詳細)")

    # improve コマンド
    improve_parser = subparsers.add_parser("improve", help="コード改善提案")
    improve_parser.add_argument("pr_url", help="PR URL")
    improve_parser.add_argument("--gitlab-url", help="独自ホスティングのGitLab URL（例: https://git.example.com）")
    improve_parser.add_argument("--settings", help="設定ファイルパス")
    improve_parser.add_argument("--debug-level", type=int, choices=[0, 1, 2, 3], default=1,
                               help="デバッグレベル (0:エラーのみ, 1:情報, 2:デバッグ, 3:HTTP詳細)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config_manager = ConfigManager()

    try:
        if args.command == "list-configs":
            config_manager.list_configs()

        elif args.command == "apply-config":
            config_path = config_manager.resolve_config_path(args.config_name)
            if not config_path:
                Logger.error(f"設定が見つかりません: {args.config_name}")
                return

            # GitLab URL設定
            gitlab_url = args.gitlab_url if hasattr(args, 'gitlab_url') else None

            success = config_manager.apply_config(
                config_path,
                custom_prompt=args.prompt,
                gitlab_url=gitlab_url
            )
            if not success:
                sys.exit(1)

        elif args.command in ["review", "describe", "improve"]:
            pr_url = args.pr_url

            # URL検証
            if not UrlValidator.validate(pr_url):
                Logger.error(f"無効なURL: {pr_url}")
                sys.exit(1)

            # GitLab URL設定
            gitlab_url = args.gitlab_url if hasattr(args, 'gitlab_url') else None

            if gitlab_url:
                Logger.info(f"独自GitLab URLを使用: {gitlab_url}")

            # デバッグレベル設定
            debug_level = args.debug_level if hasattr(args, 'debug_level') else 1

            # PR-Agent実行
            success = PRAgentRunner.run_sync(
                pr_url=pr_url,
                command=args.command,
                settings_path=args.settings,
                gitlab_url=gitlab_url,
                debug_level=debug_level
            )

            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        Logger.warning("\n中断されました")
        sys.exit(130)
    except Exception as e:
        Logger.error(f"エラーが発生しました: {str(e)}")
        import traceback
        Logger.print_colored(traceback.format_exc(), Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
