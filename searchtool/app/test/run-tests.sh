#!/bin/bash
# SearchTool - テスト実行スクリプト

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SearchTool - テスト実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")/.."

# 1. TypeScript型チェック
echo "【1】TypeScript 型チェック"
echo "────────────────────────────────────────"
npm run typecheck
echo "✅ 型チェック完了"
echo ""

# 2. 設定スキーマテスト
echo "【2】設定スキーマテスト"
echo "────────────────────────────────────────"
npx tsx test/settings.test.ts
echo ""

# 3. UIモックの生成
echo "【3】UIモックの生成"
echo "────────────────────────────────────────"
if [ -f "test/ui-mock.html" ]; then
    echo "✅ UIモックが生成されました"
    echo "   ファイル: test/ui-mock.html"
    echo "   開き方: ブラウザで直接開いてください"
    echo ""
else
    echo "⚠️  UIモックファイルが見つかりません"
    echo ""
fi

# 4. サンプル設定の生成
echo "【4】サンプル設定の生成"
echo "────────────────────────────────────────"
cat > test/sample-settings.json <<'EOF'
{
  "keyword": "API 認証",
  "ai": {
    "apiKey": "sk-proj-example-xxxxxxxxxxxxxxxxxxxxx",
    "modelId": "openai/gpt-4o-mini"
  },
  "local": {
    "root": [
      "/home/user/projects",
      "/home/user/documents"
    ]
  },
  "redmine": {
    "urls": [
      "https://redmine.example.com"
    ]
  },
  "sharepoint": {
    "urls": [
      "https://company.sharepoint.com/sites/docs"
    ]
  },
  "teams": {
    "urls": [
      "https://teams.microsoft.com/_#/discover"
    ]
  },
  "internalDocs": {
    "baseUrl": "https://docs.internal.example.com"
  },
  "browser": {
    "userDataDir": "/home/user/.config/chromium"
  },
  "excludeGlobs": [
    ".git",
    "node_modules",
    ".venv",
    "target",
    "dist"
  ],
  "limits": {
    "localMaxResults": 200,
    "redmineMaxResults": 50,
    "timeoutSeconds": 30,
    "scrollSteps": 5
  }
}
EOF

echo "✅ サンプル設定を生成しました"
echo "   ファイル: test/sample-settings.json"
echo ""
cat test/sample-settings.json
echo ""

# 5. 結果サマリー
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  テスト完了！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "生成されたファイル:"
echo "  - test/ui-mock.html         (UIプレビュー)"
echo "  - test/sample-settings.json (サンプル設定)"
echo ""
echo "次のステップ:"
echo "  1. test/ui-mock.html をブラウザで開く"
echo "  2. test/sample-settings.json を確認"
echo "  3. 実際のアプリで設定を試す"
echo ""
