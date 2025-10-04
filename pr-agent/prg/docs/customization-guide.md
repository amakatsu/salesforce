# 🔧 PR-Agent カスタマイズ完全ガイド

## 📋 カスタマイズ用途別整理

### **🎯 用途1: 設定ファイルでのカスタマイズ**
> **コードを変更せずに動作をカスタマイズ**

#### **対象ファイル**
- `.pr_agent.toml` (リポジトリ固有設定)
- `~/.pr_agent/configuration.toml` (ユーザー設定)
- `configuration-example.toml` (設定テンプレート)

#### **カスタマイズ可能項目**

**基本動作**
```toml
[config]
model = "gpt-4"                    # AIモデル変更
response_language = "ja-JP"        # 日本語出力
temperature = 0.1                  # 応答の保守性
verbosity_level = 2                # ログ詳細度
```

**レビュー動作**
```toml
[pr_reviewer]
require_tests_review = true        # テストレビュー必須
require_score_review = true        # スコア評価必須
extra_instructions = "セキュリティ重視でレビューしてください"
num_code_suggestions = 5           # 提案数変更
```

**無視設定**
```toml
[config]
ignore_pr_authors = ["bot"]        # 特定作成者を無視
ignore_pr_labels = ["no-review"]   # 特定ラベルを無視
ignore_repositories = ["test-.*"]  # テストリポジトリ無視
```

#### **適用場面**
- ✅ プロジェクト固有のレビュー方針
- ✅ 言語・地域のローカライゼーション
- ✅ チーム・組織のガイドライン適用
- ✅ CI/CD パイプライン設定

---

### **🔧 用途2: コマンドごとのファイル修正**
> **既存コマンドの動作をカスタマイズ**

#### **対象ファイル**
- `tools/pr_reviewer.py` - レビュー機能
- `tools/pr_description.py` - 説明生成機能
- `tools/pr_code_suggestions.py` - コード提案機能
- `settings/*_prompts.toml` - プロンプトファイル

#### **修正例**

**レビュー機能カスタマイズ**
```python
# tools/pr_reviewer.py
def _get_system_prompt(self):
    base_prompt = get_settings().pr_review_prompt.system

    # 言語固有の追加指示
    if self.main_language == "python":
        base_prompt += "\nPEP8準拠とtype hintsを確認してください。"
    elif self.main_language == "javascript":
        base_prompt += "\nセキュリティ（XSS等）を重視してください。"

    return base_prompt
```

**プロンプトカスタマイズ**
```toml
# settings/pr_reviewer_prompts.toml
[pr_review_prompt]
system = """
あなたは経験豊富な日本人シニアエンジニアです。
以下の観点でレビューしてください：
- セキュリティ脆弱性
- パフォーマンス影響
- コード品質
"""
```

#### **適用場面**
- ✅ 既存機能の微調整
- ✅ 言語固有のレビュー観点追加
- ✅ プロンプトの日本語化
- ✅ 業界固有の要件対応

---

### **🚀 用途3: 独自コマンドの追加**
> **新しい機能・コマンドを追加**

#### **対象ファイル**
- `tools/pr_custom_tool.py` (新規作成)
- `agent/pr_agent.py` (コマンド登録)
- `settings/pr_custom_prompts.toml` (新規作成)
- `cli.py` (ヘルプ更新)

#### **実装例**

**1. カスタムツール作成**
```python
# tools/pr_security_check.py
class PRSecurityCheck:
    def __init__(self, pr_url: str, ai_handler=LiteLLMAIHandler, args=None):
        self.pr_url = pr_url
        self.ai_handler = ai_handler

    async def run(self):
        # セキュリティチェック特化の実装
        system_prompt = get_settings().pr_security_check.system_prompt
        # ...カスタム処理
        return result
```

**2. コマンド登録**
```python
# agent/pr_agent.py
from pr_agent.tools.pr_security_check import PRSecurityCheck

command2class = {
    # 既存コマンド...
    "security_check": PRSecurityCheck,  # 新規追加
    "sec": PRSecurityCheck,            # エイリアス
}
```

**3. 専用プロンプト**
```toml
# settings/pr_security_check.toml
[pr_security_check]
system_prompt = """
セキュリティエキスパートとして、OWASP Top 10に基づいて
コードの脆弱性を詳細に分析してください。
"""
```

**4. 使用方法**
```bash
pr-agent --pr_url="..." security_check
pr-agent --pr_url="..." sec  # エイリアス
```

#### **適用場面**
- ✅ 組織固有の分析機能
- ✅ 業界特化の検査機能
- ✅ 独自のワークフロー対応
- ✅ 専門的な分析ツール

---

## 🔄 カスタマイズフロー

### **段階1: 設定ファイル調整**
```bash
# 1. 設定テンプレートをコピー
cp configuration-example.toml .pr_agent.toml

# 2. プロジェクトに合わせて編集
# モデル、言語、レビュー観点等を調整

# 3. テスト実行
pr-agent --pr_url="test-pr" review
```

### **段階2: 既存機能の微調整**
```bash
# 1. 対象ツールファイルを特定
# tools/pr_reviewer.py など

# 2. プロンプトファイルの調整
# settings/pr_reviewer_prompts.toml

# 3. 必要に応じてロジック修正
# 条件分岐やメッセージ処理
```

### **段階3: 独自機能追加**
```bash
# 1. 新しいツールクラス作成
# tools/pr_[custom_name].py

# 2. コマンド辞書に登録
# agent/pr_agent.py の command2class

# 3. 専用プロンプト作成
# settings/pr_[custom_name].toml

# 4. ヘルプ更新
# cli.py の usage
```

## 📁 ファイル構造とカスタマイズポイント

```
pr_agent/
├── agent/
│   └── pr_agent.py           # ← コマンド登録 (用途3)
├── tools/
│   ├── pr_reviewer.py        # ← レビュー機能修正 (用途2)
│   ├── pr_description.py     # ← 説明生成修正 (用途2)
│   └── pr_custom_tool.py     # ← 新規機能追加 (用途3)
├── settings/
│   ├── configuration.toml    # ← 基本設定 (用途1)
│   ├── pr_*_prompts.toml     # ← プロンプト修正 (用途2)
│   └── pr_custom.toml        # ← 新規プロンプト (用途3)
├── cli.py                    # ← ヘルプ更新 (用途3)
└── config_loader.py          # ← 設定読み込み (用途1)

# プロジェクトルート
├── .pr_agent.toml            # ← リポジトリ固有設定 (用途1)
└── configuration-example.toml # ← 設定テンプレート (用途1)
```

## 🎯 用途別推奨アプローチ

| 要件 | 推奨用途 | 難易度 | 影響範囲 |
|------|----------|--------|----------|
| 日本語化 | 用途1 | ⭐ | 全体 |
| レビュー観点変更 | 用途1+2 | ⭐⭐ | レビュー機能 |
| 新しい分析機能 | 用途3 | ⭐⭐⭐ | 独立機能 |
| チーム固有ルール | 用途1 | ⭐ | 全体 |
| 言語固有対応 | 用途2 | ⭐⭐ | 各ツール |
| 組織ガバナンス | 用途1+3 | ⭐⭐⭐ | 全体+新機能 |

## 💡 カスタマイズのベストプラクティス

### **1. 段階的アプローチ**
- 設定ファイル → 既存修正 → 新機能追加の順番
- 小さな変更から始めて徐々に拡張

### **2. バックアップ**
- 元ファイルのバックアップを必ず取る
- Git管理でカスタマイズを追跡

### **3. テスト**
- 小さなPRでテスト実行
- 段階的にカスタマイズを適用

### **4. ドキュメント化**
- カスタマイズ内容を文書化
- チーム内での共有

---

## 🔄 カスタムプロンプト切り替えシステム

### **プロンプト切り替え方法一覧**

| 方法 | 難易度 | 柔軟性 | 推奨用途 |
|------|--------|--------|----------|
| **設定ファイル切り替え** | ⭐ | ⭐⭐ | プロジェクト別 |
| **環境変数切り替え** | ⭐⭐ | ⭐⭐⭐ | CI/CD・自動化 |
| **CLI引数切り替え** | ⭐ | ⭐⭐⭐⭐ | 手動実行 |
| **動的プロンプト選択** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 条件自動切り替え |

### **設定ファイル切り替え実装**

```bash
# プロンプト切り替えコマンド
python tools/switch_config.py security-focused    # セキュリティ特化
python tools/switch_config.py performance-focused # パフォーマンス特化
python tools/switch_config.py educational         # 教育用
```

### **環境変数での動的切り替え**

```bash
# 環境変数でプロンプトを定義
export SECURITY_PROMPT="🔒 セキュリティ最優先でレビューしてください..."
export PERFORMANCE_PROMPT="⚡ パフォーマンス最優先でレビューしてください..."
export EDUCATION_PROMPT="👨‍🎓 教育的な丁寧なレビューをしてください..."

# 設定ファイルで環境変数参照
[pr_reviewer]
extra_instructions = "${REVIEW_PROMPT}"  # 環境変数から読み込み

# 使用方法
export REVIEW_PROMPT="$SECURITY_PROMPT"
python pr_agent.py -u "PR_URL" -c security-focused
```

### **CLI引数での柔軟な切り替え**

```bash
# 直接プロンプト指定
python pr_agent.py -u "PR_URL" -c security-focused --command review

# 複数コマンド組み合わせ
python pr_agent.py -u "PR_URL" -c educational --command describe
python pr_agent.py -u "PR_URL" -c performance-focused --command improve
```

### **シナリオ別切り替え例**

```bash
# プロジェクトフェーズ別
# 開発初期（教育重視）
python tools/switch_config.py educational

# セキュリティ監査フェーズ
python tools/switch_config.py security-focused

# パフォーマンス最適化フェーズ
python tools/switch_config.py performance-focused

# 本番リリース前（高精度）
python tools/switch_config.py high-precision-config
```

これにより、目的に応じた最適なカスタマイズアプローチが選択できます。