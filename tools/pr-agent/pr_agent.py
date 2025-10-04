#!/usr/bin/env python3
"""
PR-Agent 簡単実行スクリプト
MT対象（PR URL）と設定ファイルを指定してpr-agentを実行

使用例:
    # 引数なし（対話型モード）
    python pr_agent.py

    # 基本実行
    python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused

    # コマンド指定
    python pr_agent.py -u "https://github.com/user/repo/pull/123" -c performance-focused --command improve

    # カスタムプロンプト追加
    python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused --prompt "XSS脆弱性を重点チェック"

    # 設定一覧確認
    python pr_agent.py --list

    # 設定復元
    python pr_agent.py --restore

利用可能なオプション:
    -u, --url       PR URL（必須、対話型モードでは入力プロンプト）
    -c, --config    設定ファイル名またはパス（任意、対話型モードでは選択メニュー）
    --command       実行コマンド（review, describe, improve, ask, generate_labels, add_docs）
    --prompt        カスタムプロンプト（既存設定に追加）
    --question      askコマンド用の質問
    --list          利用可能な設定一覧表示
    --restore       設定復元
    --dry-run       設定適用のみ（PR-Agent実行なし）
"""

import sys
import subprocess
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

def get_available_configs():
    """利用可能な設定ファイル一覧を取得"""
    configs = []

    # テンプレート
    templates_dir = Path("configs/templates")
    if templates_dir.exists():
        for file in templates_dir.glob("*.toml"):
            configs.append((file.stem, str(file), "📄 テンプレート"))

    # プリセット
    presets_dir = Path("configs/presets")
    if presets_dir.exists():
        for file in presets_dir.glob("*.toml"):
            configs.append((file.stem, str(file), "🎯 プリセット"))

    # 言語固有
    lang_dir = Path("configs/language-specific")
    if lang_dir.exists():
        for file in lang_dir.glob("*.toml"):
            configs.append((file.stem, str(file), "🔧 言語固有"))

    return configs

def interactive_mode():
    """対話型モードで引数を収集"""
    print_colored("🤖 PR-Agent 対話型セットアップ", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    # PR URL入力
    print_colored("\n📍 ステップ1: PR URLを入力してください", Colors.CYAN)
    print_colored("例: https://github.com/user/repo/pull/123", Colors.WHITE)
    pr_url = input("PR URL: ").strip()

    if not pr_url:
        print_colored("❌ PR URLが入力されていません", Colors.RED)
        sys.exit(1)

    # 設定ファイル選択（任意）
    print_colored("\n⚙️  ステップ2: 設定を選択してください（任意）", Colors.CYAN)

    configs = get_available_configs()
    selected_config = None

    if configs:
        print_colored("\n利用可能な設定:", Colors.WHITE)
        print_colored("  0. デフォルト設定を使用", Colors.WHITE)
        for i, (name, path, category) in enumerate(configs, 1):
            print_colored(f"  {i}. {category} {name}", Colors.WHITE)
            print_colored(f"     → {path}", Colors.WHITE)

        while True:
            try:
                choice = input(f"\n選択 (0-{len(configs)}, Enter=0): ").strip()
                if not choice:
                    choice = "0"
                choice_num = int(choice)
                if choice_num == 0:
                    selected_config = None  # デフォルト設定
                    break
                elif 1 <= choice_num <= len(configs):
                    selected_config = configs[choice_num - 1][0]
                    break
                else:
                    print_colored(f"❌ 0から{len(configs)}の数字を入力してください", Colors.RED)
            except ValueError:
                print_colored("❌ 数字を入力してください", Colors.RED)
    else:
        print_colored("⚠️  カスタム設定ファイルが見つかりません。デフォルト設定を使用します。", Colors.YELLOW)
        selected_config = None

    # コマンド選択
    print_colored("\n🔧 ステップ3: 実行するコマンドを選択してください", Colors.CYAN)
    commands = [
        ("review", "🔍 PRレビュー（デフォルト）"),
        ("describe", "📝 PR説明生成"),
        ("improve", "💡 コード改善提案"),
        ("ask", "❓ 質問"),
        ("generate_labels", "🏷️ ラベル生成"),
        ("add_docs", "📚 ドキュメント追加")
    ]

    print_colored("\n利用可能なコマンド:", Colors.WHITE)
    for i, (cmd, desc) in enumerate(commands, 1):
        print_colored(f"  {i}. {desc}", Colors.WHITE)

    while True:
        try:
            cmd_choice = input(f"\nコマンド選択 (1-{len(commands)}, Enter=1): ").strip()
            if not cmd_choice:
                cmd_choice = "1"
            cmd_num = int(cmd_choice)
            if 1 <= cmd_num <= len(commands):
                selected_command = commands[cmd_num - 1][0]
                break
            else:
                print_colored(f"❌ 1から{len(commands)}の数字を入力してください", Colors.RED)
        except ValueError:
            print_colored("❌ 数字を入力してください", Colors.RED)

    # カスタムプロンプト（オプション）
    print_colored("\n✨ ステップ4: カスタムプロンプト（オプション）", Colors.CYAN)
    print_colored("例: 'XSS脆弱性を重点的にチェック', 'メモリ使用量を最適化'", Colors.WHITE)
    custom_prompt = input("カスタムプロンプト (Enter=なし): ").strip()

    # 質問（askコマンドの場合）
    question = ""
    if selected_command == "ask":
        print_colored("\n❓ ステップ5: 質問を入力してください", Colors.CYAN)
        question = input("質問: ").strip()
        if not question:
            print_colored("❌ askコマンドには質問が必要です", Colors.RED)
            sys.exit(1)

    # 確認
    print_colored("\n📋 設定確認", Colors.YELLOW)
    print_colored("=" * 30, Colors.YELLOW)
    print_colored(f"PR URL:     {pr_url}", Colors.WHITE)
    print_colored(f"設定:       {selected_config or 'デフォルト設定'}", Colors.WHITE)
    print_colored(f"コマンド:   {selected_command}", Colors.WHITE)
    if custom_prompt:
        print_colored(f"プロンプト: {custom_prompt}", Colors.WHITE)
    if question:
        print_colored(f"質問:       {question}", Colors.WHITE)

    confirm = input("\n実行しますか？ (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print_colored("❌ キャンセルされました", Colors.RED)
        sys.exit(0)

    # 引数リストを構築
    args = ["-u", pr_url, "--command", selected_command]

    # 設定ファイルが選択された場合のみ追加
    if selected_config:
        args.extend(["-c", selected_config])

    if custom_prompt:
        args.extend(["--prompt", custom_prompt])

    if question:
        args.extend(["--question", question])

    return args

def main():
    # tools/pr_agent_runner.py を呼び出し
    runner_path = Path(__file__).parent / "tools" / "pr_agent_runner.py"

    if not runner_path.exists():
        print_colored("❌ pr_agent_runner.py が見つかりません", Colors.RED)
        sys.exit(1)

    # 引数がない場合は対話型モード
    if len(sys.argv) == 1:
        try:
            print_colored("🔄 対話型モードを開始します...\n", Colors.GREEN)
            interactive_args = interactive_mode()
            cmd = [sys.executable, str(runner_path)] + interactive_args
        except KeyboardInterrupt:
            print_colored("\n⚠️  キャンセルされました", Colors.YELLOW)
            sys.exit(0)
    else:
        # 通常の引数渡し
        cmd = [sys.executable, str(runner_path)] + sys.argv[1:]

    try:
        # 実行
        print_colored("\n🚀 PR-Agentを実行しています...", Colors.GREEN)
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print_colored("\n⚠️  実行がキャンセルされました", Colors.YELLOW)
        sys.exit(1)

if __name__ == "__main__":
    main()