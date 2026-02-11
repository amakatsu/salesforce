#!/bin/bash
# SearchTool - セットアップ検証スクリプト
# このスクリプトは、必要な依存関係がすべてインストールされているかを確認します

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SearchTool - セットアップ検証"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ERRORS=0
WARNINGS=0

# ヘルパー関数
check_command() {
    local cmd=$1
    local name=$2
    local required=$3

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -1)
        echo "✅ $name: インストール済み ($version)"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ $name: 見つかりません（必須）"
            ((ERRORS++))
        else
            echo "⚠️  $name: 見つかりません（オプション）"
            ((WARNINGS++))
        fi
        return 1
    fi
}

check_file() {
    local file=$1
    local name=$2
    local required=$3

    if [ -f "$file" ]; then
        echo "✅ $name: 存在します"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ $name: 見つかりません（必須）"
            ((ERRORS++))
        else
            echo "⚠️  $name: 見つかりません（オプション）"
            ((WARNINGS++))
        fi
        return 1
    fi
}

check_dir() {
    local dir=$1
    local name=$2
    local required=$3

    if [ -d "$dir" ]; then
        echo "✅ $name: 存在します"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo "❌ $name: 見つかりません（必須）"
            ((ERRORS++))
        else
            echo "⚠️  $name: 見つかりません（オプション）"
            ((WARNINGS++))
        fi
        return 1
    fi
}

echo "【1】必須コマンドの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_command node "Node.js" true
check_command npm "npm" true
check_command rg "ripgrep" true

echo ""
echo "【2】オプションコマンドの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_command rga "ripgrep-all (PDF/Office対応)" false

echo ""
echo "【3】プロジェクトファイルの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

check_file "$PROJECT_ROOT/app/package.json" "package.json" true
check_dir "$PROJECT_ROOT/app/node_modules" "node_modules" true
check_file "$PROJECT_ROOT/app/node_modules/.bin/electron" "Electron" true
check_file "$PROJECT_ROOT/app/node_modules/.bin/vite" "Vite" true

echo ""
echo "【4】環境変数の確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✅ .env ファイル: 存在します"

    if grep -q "OPENAI_API_KEY=" "$PROJECT_ROOT/.env" 2>/dev/null; then
        if grep -q "OPENAI_API_KEY=sk-" "$PROJECT_ROOT/.env" 2>/dev/null; then
            echo "✅ OPENAI_API_KEY: 設定されています"
        else
            echo "⚠️  OPENAI_API_KEY: 設定されていますが、値が空または無効です"
            ((WARNINGS++))
        fi
    else
        echo "⚠️  OPENAI_API_KEY: 設定されていません（AI要約機能は無効）"
        ((WARNINGS++))
    fi
else
    echo "⚠️  .env ファイル: 見つかりません"
    echo "   ℹ️  .env.example をコピーして .env を作成してください"
    ((WARNINGS++))
fi

echo ""
echo "【5】Playwright ブラウザの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_dir "$HOME/.cache/ms-playwright/chromium-*" "Chromium ブラウザ" false; then
    :
else
    echo "   ℹ️  インストール: npx playwright install chromium"
fi

echo ""
echo "【6】ビルド成果物の確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "$PROJECT_ROOT/app/dist" "dist (Viteビルド)" false
check_dir "$PROJECT_ROOT/app/dist-electron" "dist-electron (Electronビルド)" false
check_file "$PROJECT_ROOT/app/release/1.0.0/SearchTool-Linux-1.0.0.AppImage" "AppImage" false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  検証結果サマリー"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 すべての検証に合格しました！"
    echo ""
    echo "次のステップ:"
    echo "  cd app && npm run dev"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  警告: $WARNINGS 件"
    echo ""
    echo "次のステップ:"
    echo "  cd app && npm run dev"
    echo ""
    echo "注意: 警告があっても基本機能は動作する可能性があります"
    exit 0
else
    echo "❌ エラー: $ERRORS 件"
    echo "⚠️  警告: $WARNINGS 件"
    echo ""
    echo "エラーを解決してから再度実行してください"
    echo ""
    echo "インストール手順:"
    echo "  # Node.js / npm"
    echo "  https://nodejs.org/"
    echo ""
    echo "  # ripgrep"
    echo "  sudo apt install ripgrep  # Ubuntu/Debian"
    echo "  brew install ripgrep      # macOS"
    echo ""
    echo "  # npm パッケージ"
    echo "  cd app && npm install"
    echo ""
    exit 1
fi
