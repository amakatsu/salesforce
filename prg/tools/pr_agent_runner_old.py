#!/usr/bin/env python3
"""
PR-Agent カスタム実行ツール
設定ファイルとPR URLを指定してpr-agentを実行
"""

import argparse
import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

# カラー出力用
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message: str, color: str = Colors.WHITE):
    """色付きメッセージを出力"""
    print(f"{color}{message}{Colors.END}")

def backup_current_config():
    """現在の設定をバックアップ"""
    if Path(".pr_agent.toml").exists():
        shutil.copy(".pr_agent.toml", ".pr_agent.toml.backup")
        print_colored("📋 現在の設定をバックアップしました", Colors.YELLOW)
        return True
    return False

def restore_config():
    """設定を復元"""
    if Path(".pr_agent.toml.backup").exists():
        shutil.copy(".pr_agent.toml.backup", ".pr_agent.toml")
        print_colored("♻️  設定を復元しました", Colors.GREEN)
        return True
    return False

def apply_config(config_path: str, custom_prompt: Optional[str] = None) -> bool:
    """指定された設定ファイルを適用"""
    config_file = Path(config_path)

    if not config_file.exists():
        print_colored(f"❌ 設定ファイルが見つかりません: {config_path}", Colors.RED)
        return False

    # バックアップ作成
    backup_current_config()

    # 設定ファイルをコピー
    shutil.copy(config_file, ".pr_agent.toml")

    # カスタムプロンプト追加
    if custom_prompt:
        append_custom_prompt(custom_prompt)
        print_colored(f"✅ 設定ファイルを適用しました: {config_path} + カスタムプロンプト", Colors.GREEN)
    else:
        print_colored(f"✅ 設定ファイルを適用しました: {config_path}", Colors.GREEN)

    return True

def append_custom_prompt(custom_prompt: str):
    """設定ファイルにカスタムプロンプトを追加"""
    config_file = Path(".pr_agent.toml")

    if not config_file.exists():
        print_colored("⚠️  設定ファイルが存在しません", Colors.YELLOW)
        return

    try:
        # 既存の設定を読み込み
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # extra_instructionsセクションを探してプロンプトを追加
        if 'extra_instructions = """' in content:
            # 既存のextra_instructionsに追加
            content = content.replace(
                'extra_instructions = """',
                f'extra_instructions = """\n{custom_prompt}\n\n--- 元の指示 ---\n'
            )
        elif '[pr_reviewer]' in content:
            # pr_reviewerセクションにextra_instructionsを追加
            content = content.replace(
                '[pr_reviewer]',
                f'[pr_reviewer]\nextra_instructions = """\n{custom_prompt}\n"""'
            )
        else:
            # 新しくpr_reviewerセクションを追加
            content += f'\n\n[pr_reviewer]\nextra_instructions = """\n{custom_prompt}\n"""\n'

        # ファイルに書き戻し
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(content)

        print_colored(f"📝 カスタムプロンプトを追加しました", Colors.CYAN)

    except Exception as e:
        print_colored(f"❌ プロンプト追加エラー: {str(e)}", Colors.RED)

def create_default_config():
    """デフォルト設定ファイルを作成"""
    default_config = """# PR-Agent デフォルト設定

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

[pr_description]
publish_description = true
add_original_user_description = true
extra_instructions = ""

[pr_code_suggestions]
num_code_suggestions = 4
"""

    try:
        # バックアップ作成
        backup_current_config()

        # デフォルト設定ファイルを作成
        with open(".pr_agent.toml", "w", encoding="utf-8") as f:
            f.write(default_config)

        print_colored("📝 デフォルト設定ファイルを作成しました", Colors.CYAN)

    except Exception as e:
        print_colored(f"❌ 設定ファイル作成エラー: {str(e)}", Colors.RED)

def create_default_config_with_prompt(custom_prompt: str):
    """デフォルト設定 + カスタムプロンプトファイルを作成"""
    default_config_with_prompt = f"""# PR-Agent デフォルト設定 + カスタムプロンプト

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
extra_instructions = '''
{custom_prompt}
'''

[pr_description]
publish_description = true
add_original_user_description = true
extra_instructions = ""

[pr_code_suggestions]
num_code_suggestions = 4
"""

    try:
        # バックアップ作成
        backup_current_config()

        # デフォルト設定ファイルを作成
        with open(".pr_agent.toml", "w", encoding="utf-8") as f:
            f.write(default_config_with_prompt)

        print_colored("📝 デフォルト設定 + カスタムプロンプトファイルを作成しました", Colors.CYAN)

    except Exception as e:
        print_colored(f"❌ 設定ファイル作成エラー: {str(e)}", Colors.RED)

def get_available_configs() -> dict:
    """利用可能な設定ファイル一覧を取得"""
    configs = {
        "templates": {},
        "presets": {},
        "language_specific": {}
    }

    # テンプレート
    templates_dir = Path("configs/templates")
    if templates_dir.exists():
        for file in templates_dir.glob("*.toml"):
            configs["templates"][file.stem] = str(file)

    # プリセット
    presets_dir = Path("configs/presets")
    if presets_dir.exists():
        for file in presets_dir.glob("*.toml"):
            configs["presets"][file.stem] = str(file)

    # 言語固有
    lang_dir = Path("configs/language-specific")
    if lang_dir.exists():
        for file in lang_dir.glob("*.toml"):
            configs["language_specific"][file.stem] = str(file)

    return configs

def list_configs():
    """利用可能な設定一覧を表示"""
    configs = get_available_configs()

    print_colored("📚 利用可能な設定ファイル", Colors.BLUE)
    print("─" * 50)

    if configs["templates"]:
        print_colored("📄 テンプレート (templates):", Colors.CYAN)
        for name, path in configs["templates"].items():
            print(f"  • {name:<30} → {path}")
        print()

    if configs["presets"]:
        print_colored("🎯 プリセット (presets):", Colors.PURPLE)
        for name, path in configs["presets"].items():
            print(f"  • {name:<30} → {path}")
        print()

    if configs["language_specific"]:
        print_colored("🔧 言語固有 (language-specific):", Colors.YELLOW)
        for name, path in configs["language_specific"].items():
            print(f"  • {name:<30} → {path}")

def resolve_config_path(config_name: str) -> Optional[str]:
    """設定名から実際のファイルパスを解決"""
    configs = get_available_configs()

    # 直接パス指定の場合
    if Path(config_name).exists():
        return config_name

    # 設定名での検索
    all_configs = {}
    all_configs.update(configs["templates"])
    all_configs.update(configs["presets"])
    all_configs.update(configs["language_specific"])

    if config_name in all_configs:
        return all_configs[config_name]

    # 部分マッチ検索
    matches = [path for name, path in all_configs.items() if config_name in name]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print_colored(f"⚠️  複数の設定がマッチしました: {', '.join(matches)}", Colors.YELLOW)
        return None

    return None

def validate_pr_url(url: str) -> bool:
    """PR URLの形式を検証"""
    valid_patterns = [
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "dev.azure.com",
        "/pull/",
        "/merge_requests/",
        "/-/merge_requests/"
    ]

    return any(pattern in url for pattern in valid_patterns)

async def run_pr_agent(pr_url: str, command: str = "review", extra_args: list = None) -> bool:
    """PR-Agentを実行"""
    try:
        # PR-Agentのインポート
        from pr_agent.agent.pr_agent import PRAgent

        print_colored(f"🚀 PR-Agent を実行しています...", Colors.BLUE)
        print_colored(f"   URL: {pr_url}", Colors.WHITE)
        print_colored(f"   コマンド: {command}", Colors.WHITE)

        # PR-Agentインスタンス作成・実行
        agent = PRAgent()

        # コマンド引数を準備
        request_args = [command]
        if extra_args:
            request_args.extend(extra_args)

        # 実行
        result = await agent.handle_request(pr_url, request_args)

        if result:
            print_colored("✅ PR-Agent の実行が完了しました", Colors.GREEN)
        else:
            print_colored("⚠️  PR-Agent の実行でエラーが発生しました", Colors.YELLOW)

        return result

    except ImportError:
        print_colored("❌ PR-Agent がインストールされていません", Colors.RED)
        print_colored("   pip install pr-agent でインストールしてください", Colors.WHITE)
        return False
    except Exception as e:
        print_colored(f"❌ エラーが発生しました: {str(e)}", Colors.RED)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="PR-Agent カスタム実行ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # セキュリティ特化レビュー
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c security-focused

  # パフォーマンス特化レビュー
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c performance-focused

  # 高精度レビュー（コマンド指定）
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c high-precision-config --command improve

  # 直接パス指定
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c ./custom-config.toml

  # カスタムプロンプト追加
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c security-focused --prompt "特にXSS脆弱性を重点的にチェックしてください"

  # 複数オプション組み合わせ
  python pr_agent_runner.py -u "https://github.com/user/repo/pull/123" -c performance-focused --command improve --prompt "メモリ使用量の最適化を最優先にしてください"

  # 設定一覧表示
  python pr_agent_runner.py --list

  # 設定復元
  python pr_agent_runner.py --restore
"""
    )

    parser.add_argument(
        "-u", "--url",
        help="PR URL (GitHub, GitLab, Bitbucket等)"
    )

    parser.add_argument(
        "-c", "--config",
        help="設定ファイル名またはパス（任意、指定されない場合はデフォルト設定）"
    )

    parser.add_argument(
        "--command",
        default="review",
        choices=["review", "describe", "improve", "ask", "generate_labels", "add_docs", "update_changelog"],
        help="実行するコマンド (デフォルト: review)"
    )

    parser.add_argument(
        "--question",
        help="askコマンド用の質問"
    )

    parser.add_argument(
        "--prompt",
        help="カスタムプロンプト（extra_instructionsに追加）"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="利用可能な設定一覧を表示"
    )

    parser.add_argument(
        "--restore",
        action="store_true",
        help="設定を元に戻す"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="設定適用のみ（PR-Agent実行なし）"
    )

    args = parser.parse_args()

    # 設定一覧表示
    if args.list:
        list_configs()
        return

    # 設定復元
    if args.restore:
        if restore_config():
            print_colored("✅ 設定を復元しました", Colors.GREEN)
        else:
            print_colored("❌ バックアップファイルが見つかりません", Colors.RED)
        return

    # 引数チェック
    if not args.url:
        print_colored("❌ PR URLが指定されていません (-u オプション)", Colors.RED)
        parser.print_help()
        sys.exit(1)

    # PR URL検証
    if not validate_pr_url(args.url):
        print_colored("⚠️  PR URLの形式が正しくない可能性があります", Colors.YELLOW)
        print_colored(f"   指定されたURL: {args.url}", Colors.WHITE)

    # 設定ファイル解決（任意）
    config_path = None
    if args.config:
        config_path = resolve_config_path(args.config)
        if not config_path:
            print_colored(f"❌ 設定ファイルが見つかりません: {args.config}", Colors.RED)
            print_colored("利用可能な設定:", Colors.WHITE)
            list_configs()
            sys.exit(1)

        # 設定適用
        if not apply_config(config_path, args.prompt):
            sys.exit(1)
    else:
        # デフォルト設定使用
        print_colored("📄 デフォルト設定を使用します", Colors.CYAN)

        # 既存の設定があるかチェック
        if Path(".pr_agent.toml").exists():
            print_colored("🔄 既存の設定ファイルを発見しました", Colors.YELLOW)
            if args.prompt:
                # 既存設定にプロンプトを追加
                append_custom_prompt(args.prompt)
                print_colored("✅ 既存設定にカスタムプロンプトを追加しました", Colors.GREEN)
        else:
            # 新しい設定ファイルを作成
            if args.prompt:
                create_default_config_with_prompt(args.prompt)
                print_colored("✅ デフォルト設定 + カスタムプロンプトを作成しました", Colors.GREEN)
            else:
                create_default_config()
                print_colored("✅ デフォルト設定ファイルを作成しました", Colors.GREEN)

    # Dry run モード
    if args.dry_run:
        print_colored("🔍 Dry-run モード: 設定適用のみ完了", Colors.CYAN)
        return

    # PR-Agent実行
    print_colored(f"🎯 PR-Agent を実行します", Colors.BOLD)
    print_colored(f"   設定: {config_path}", Colors.WHITE)
    print_colored(f"   URL: {args.url}", Colors.WHITE)
    print_colored(f"   コマンド: {args.command}", Colors.WHITE)

    # askコマンドの場合、質問を追加
    extra_args = []
    if args.command == "ask" and args.question:
        extra_args.append(args.question)

    # 非同期実行
    try:
        result = asyncio.run(run_pr_agent(args.url, args.command, extra_args))
        if result:
            print_colored("🎉 完了しました！", Colors.GREEN)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print_colored("\n⚠️  実行がキャンセルされました", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"❌ 予期しないエラー: {str(e)}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()