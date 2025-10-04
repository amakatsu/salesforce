#!/usr/bin/env python3
"""
PR-Agent 設定切り替えツール
"""

import argparse
import shutil
import sys
from pathlib import Path

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
        print_colored("📄 テンプレート:", Colors.CYAN)
        for name, path in configs["templates"].items():
            print(f"  • {name:<30} → {path}")
        print()

    if configs["presets"]:
        print_colored("🎯 プリセット:", Colors.PURPLE)
        for name, path in configs["presets"].items():
            desc = get_config_description(name)
            print(f"  • {name:<30} → {desc}")
        print()

    if configs["language_specific"]:
        print_colored("🔧 言語固有:", Colors.YELLOW)
        for name, path in configs["language_specific"].items():
            print(f"  • {name:<30} → {path}")

def get_config_description(config_name: str) -> str:
    """設定ファイルの説明を取得"""
    descriptions = {
        "security-focused": "🔒 セキュリティ特化（OWASP Top 10準拠）",
        "performance-focused": "⚡ パフォーマンス特化（計算量・メモリ効率）",
        "educational": "👨‍🎓 教育用（新人向け丁寧説明）",
        "configuration-example": "📄 基本設定（バランス型）",
        "high-precision-config": "🎯 高精度（最高品質レビュー）"
    }
    return descriptions.get(config_name, f"configs/presets/{config_name}.toml")

def resolve_config_path(config_name: str) -> str:
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
        print_colored(f"⚠️  複数の設定がマッチしました:", Colors.YELLOW)
        for match in matches:
            print(f"   • {match}")
        return None

    return None

def show_current_config():
    """現在の設定を表示"""
    if not Path(".pr_agent.toml").exists():
        print_colored("⚠️  設定ファイルが存在しません", Colors.YELLOW)
        return

    print_colored("🔍 現在の設定", Colors.BLUE)
    print("─" * 30)

    try:
        with open(".pr_agent.toml", "r", encoding="utf-8") as f:
            content = f.read()

        # extra_instructionsの最初の数行を表示（モード判定用）
        lines = content.split("\n")
        in_instructions = False
        instruction_lines = []

        for line in lines:
            if "extra_instructions" in line and '"""' in line:
                in_instructions = True
                continue
            elif in_instructions:
                if '"""' in line:
                    break
                if line.strip():
                    instruction_lines.append(line.strip())
                    if len(instruction_lines) >= 3:
                        break

        if instruction_lines:
            for line in instruction_lines[:3]:
                print(f"  {line}")
        else:
            print("  標準設定")

    except Exception as e:
        print_colored(f"❌ 設定ファイルの読み込みエラー: {e}", Colors.RED)

def switch_config(config_name: str) -> bool:
    """設定を切り替え"""
    config_path = resolve_config_path(config_name)

    if not config_path:
        print_colored(f"❌ 設定ファイルが見つかりません: {config_name}", Colors.RED)
        return False

    if not Path(config_path).exists():
        print_colored(f"❌ ファイルが存在しません: {config_path}", Colors.RED)
        return False

    # バックアップ
    backup_current_config()

    # 設定ファイルをコピー
    shutil.copy(config_path, ".pr_agent.toml")

    # 成功メッセージ
    desc = get_config_description(config_name)
    print_colored(f"✅ 設定を切り替えました: {desc}", Colors.GREEN)

    return True

def main():
    parser = argparse.ArgumentParser(
        description="PR-Agent 設定切り替えツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python switch_config.py security-focused     # セキュリティ特化に切り替え
  python switch_config.py performance-focused  # パフォーマンス特化に切り替え
  python switch_config.py educational          # 教育用に切り替え
  python switch_config.py --list               # 利用可能な設定一覧
  python switch_config.py --status             # 現在の設定表示
  python switch_config.py --restore            # 設定復元
"""
    )

    parser.add_argument(
        "config",
        nargs="?",
        help="設定ファイル名（security-focused, performance-focused, educational等）"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="利用可能な設定一覧を表示"
    )

    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="現在の設定を表示"
    )

    parser.add_argument(
        "--restore", "-r",
        action="store_true",
        help="設定を元に戻す"
    )

    args = parser.parse_args()

    # オプション処理
    if args.list:
        list_configs()
        return

    if args.status:
        show_current_config()
        return

    if args.restore:
        if restore_config():
            print_colored("✅ 設定を復元しました", Colors.GREEN)
        else:
            print_colored("❌ バックアップファイルが見つかりません", Colors.RED)
        return

    # 設定名チェック
    if not args.config:
        print_colored("❌ 設定名が指定されていません", Colors.RED)
        print_colored("利用可能な設定:", Colors.WHITE)
        list_configs()
        sys.exit(1)

    # 設定切り替え実行
    if switch_config(args.config):
        print_colored(f"🚀 設定切り替え完了。PR-Agentを実行してください", Colors.BLUE)
    else:
        print_colored("利用可能な設定:", Colors.WHITE)
        list_configs()
        sys.exit(1)

if __name__ == "__main__":
    main()