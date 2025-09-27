# 🚀 PR-Agent 実践的な使用例集

## 🎯 具体的な使用例

### **1. セキュリティ特化レビュー**
```bash
# セキュリティ脆弱性を重点的にチェック
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused

# GitLab MRのセキュリティレビュー
python pr_agent.py -u "https://gitlab.com/user/repo/-/merge_requests/45" -c security-focused
```

### **2. パフォーマンス特化レビュー**
```bash
# パフォーマンス改善に特化したレビュー
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c performance-focused

# コード改善提案を生成
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c performance-focused --command improve
```

### **3. 教育的レビュー（新人向け）**
```bash
# 学習効果を重視した丁寧なレビュー
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c educational

# PR説明も教育的に生成
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c educational --command describe
```

### **4. 高精度レビュー**
```bash
# 最高品質のレビュー（重要リリース前）
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c high-precision-config

# 高精度でのコード改善提案
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c high-precision-config --command improve
```

### **5. 言語固有設定**
```bash
# Python専用の高精度レビュー
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c python-high-precision
```

## 🔧 コマンド別使用例

### **review（デフォルト）**
```bash
# PR レビューの実行
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused --command review
```

### **describe**
```bash
# PR説明・タイトルの生成
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c educational --command describe
```

### **improve**
```bash
# コード改善提案の生成
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c performance-focused --command improve
```

### **ask**
```bash
# PRに関する質問
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c educational --command ask --question "このPRのセキュリティ影響は？"

python pr_agent.py -u "https://github.com/user/repo/pull/123" -c performance-focused --command ask --question "パフォーマンスへの影響を教えて"
```

### **generate_labels**
```bash
# 適切なラベルを自動生成
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c configuration-example --command generate_labels
```

### **add_docs**
```bash
# ドキュメント追加の提案
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c educational --command add_docs
```

## 🔍 管理・設定コマンド

### **利用可能な設定一覧**
```bash
python pr_agent.py --list
```

### **設定の復元**
```bash
python pr_agent.py --restore
```

### **Dry-run（設定適用のみ）**
```bash
# 設定ファイルを適用するが、PR-Agentは実行しない
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused --dry-run
```

## 🌐 対応プラットフォーム例

### **GitHub**
```bash
python pr_agent.py -u "https://github.com/microsoft/vscode/pull/12345" -c security-focused
python pr_agent.py -u "https://github.com/facebook/react/pull/6789" -c performance-focused
```

### **GitLab**
```bash
python pr_agent.py -u "https://gitlab.com/gitlab-org/gitlab/-/merge_requests/123" -c security-focused
python pr_agent.py -u "https://gitlab.company.com/team/project/-/merge_requests/45" -c educational
```

### **Bitbucket**
```bash
python pr_agent.py -u "https://bitbucket.org/user/repo/pull-requests/123" -c performance-focused
```

## 🎯 シナリオ別使用パターン

### **開発フェーズ別**

#### **開発初期**
```bash
# 学習重視の教育的レビュー
python pr_agent.py -u "<PR_URL>" -c educational
```

#### **機能開発中**
```bash
# バランス型のレビュー
python pr_agent.py -u "<PR_URL>" -c configuration-example
```

#### **セキュリティ監査**
```bash
# セキュリティ特化レビュー
python pr_agent.py -u "<PR_URL>" -c security-focused
```

#### **パフォーマンス最適化**
```bash
# パフォーマンス特化レビュー
python pr_agent.py -u "<PR_URL>" -c performance-focused --command improve
```

#### **リリース前**
```bash
# 最高精度レビュー
python pr_agent.py -u "<PR_URL>" -c high-precision-config
```

### **開発者レベル別**

#### **新人開発者**
```bash
# 教育的で丁寧なレビュー
python pr_agent.py -u "<PR_URL>" -c educational
```

#### **中級開発者**
```bash
# 標準的なレビュー
python pr_agent.py -u "<PR_URL>" -c configuration-example
```

#### **上級開発者**
```bash
# パフォーマンス重視のレビュー
python pr_agent.py -u "<PR_URL>" -c performance-focused
```

#### **セキュリティエンジニア**
```bash
# セキュリティ特化レビュー
python pr_agent.py -u "<PR_URL>" -c security-focused
```

## 🔗 他ツールとの連携

### **CI/CD パイプライン統合**
```bash
# GitHub Actions例
- name: Run PR-Agent Security Review
  run: |
    python pr_agent.py -u "${{ github.event.pull_request.html_url }}" -c security-focused

# GitLab CI例
script:
  - python pr_agent.py -u "$CI_MERGE_REQUEST_PROJECT_URL/-/merge_requests/$CI_MERGE_REQUEST_IID" -c security-focused
```

### **スクリプト例**
```bash
#!/bin/bash
# PR URL を引数で受け取り、条件に応じて設定を切り替え

PR_URL=$1

if [[ "$PR_URL" == *"security"* ]]; then
    CONFIG="security-focused"
elif [[ "$PR_URL" == *"performance"* ]]; then
    CONFIG="performance-focused"
else
    CONFIG="configuration-example"
fi

python pr_agent.py -u "$PR_URL" -c "$CONFIG"
```

## 🆘 トラブルシューティング

### **設定ファイルが見つからない**
```bash
# 利用可能な設定を確認
python pr_agent.py --list

# 部分マッチで検索
python pr_agent.py -u "<PR_URL>" -c security  # security-focused.toml を自動検出
```

### **PR URLの形式エラー**
```bash
# 正しい形式例
python pr_agent.py -u "https://github.com/user/repo/pull/123" -c security-focused

# 不正な形式（エラー）
python pr_agent.py -u "github.com/user/repo" -c security-focused
```

### **設定の復元**
```bash
# 前の設定に戻す
python pr_agent.py --restore
```

## 💡 効率的な使用のコツ

### **エイリアス設定**
```bash
# .bashrc または .zshrc に追加
alias pra-sec='python pr_agent.py -c security-focused -u'
alias pra-perf='python pr_agent.py -c performance-focused -u'
alias pra-edu='python pr_agent.py -c educational -u'

# 使用例
pra-sec "https://github.com/user/repo/pull/123"
pra-perf "https://github.com/user/repo/pull/123" --command improve
```

### **設定ファイルのカスタマイズ**
```bash
# 既存設定をコピーしてカスタマイズ
cp configs/templates/configuration-example.toml configs/presets/my-custom.toml

# カスタム設定を使用
python pr_agent.py -u "<PR_URL>" -c my-custom
```