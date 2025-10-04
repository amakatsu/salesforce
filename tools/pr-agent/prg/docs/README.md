# 📚 PR-Agent カスタマイズ ドキュメント

このディレクトリには、PR-Agentのカスタマイズ・運用に関する詳細ドキュメントが含まれています。

## 📋 ドキュメント一覧

### ⚡ **クイックスタート**
- **[quick-reference.md](./quick-reference.md)** - クイックリファレンス
  - 基本コマンド集
  - 設定一覧
  - よくあるパターン

### 🚀 **基本ガイド**
- **[usage-examples.md](./usage-examples.md)** - 実用的な使用例集
  - コマンド別使用例
  - シナリオ別パターン
  - トラブルシューティング


### 🔧 **カスタマイズガイド**
- **[customization-guide.md](./customization-guide.md)** - カスタマイズ完全ガイド
  - 設定ファイルカスタマイズ
  - 既存コマンド修正
  - 独自コマンド追加
  - プロンプト切り替えシステム
  - 動的プロンプト選択

### 📊 **品質向上ガイド**
- **[precision-enhancement-guide.md](./precision-enhancement-guide.md)** - レビュー精度向上
  - 精度向上の要素分析
  - 段階的改善プロセス
  - 言語・フレームワーク別最適化

### 🏗️ **技術詳細**
- **[PR-Agent-Structure.md](./PR-Agent-Structure.md)** - PR-Agent内部構造
  - パッケージ構成詳細
  - カスタムハンドラー作成
  - 新機能追加方法

## 🎯 読む順番（推奨）

### **初回セットアップ時**
1. **クイックスタート** → [quick-reference.md](./quick-reference.md)
2. **基本的な使い方** → [usage-examples.md](./usage-examples.md)
3. **必要に応じてカスタマイズ** → [customization-guide.md](./customization-guide.md)

### **運用・改善時**
1. **レビュー品質向上** → [precision-enhancement-guide.md](./precision-enhancement-guide.md)
2. **高度なカスタマイズ** → [customization-guide.md](./customization-guide.md)
3. **PR-Agent内部構造理解** → [PR-Agent-Structure.md](./PR-Agent-Structure.md)

## 🔍 クイックリファレンス

### **よく使うコマンド**
```bash
# 基本実行
python pr_agent.py -u "<PR_URL>" -c security-focused

# 設定切り替え
python tools/switch_config.py performance-focused

# 設定一覧確認
python tools/switch_config.py --list
```

### **設定ファイル場所**
```
configs/
├── templates/     # 基本テンプレート
├── presets/       # 用途別プリセット
└── language-specific/  # 言語固有設定
```

### **主要設定**
- **セキュリティ特化**: `security-focused`
- **パフォーマンス特化**: `performance-focused`
- **教育用**: `educational`
- **高精度**: `high-precision-config`

## 📞 サポート・質問

### **ドキュメント内検索**
各ドキュメントは詳細な目次と検索可能な構造になっています。
Ctrl+F（Cmd+F）でキーワード検索を活用してください。

### **よくある質問**
- **設定が反映されない** → [usage-examples.md](./usage-examples.md) のトラブルシューティング参照
- **カスタムプロンプト作成** → [customization-guide.md](./customization-guide.md) 参照
- **レビュー品質改善** → [precision-enhancement-guide.md](./precision-enhancement-guide.md) 参照

### **コミュニティ・リソース**
- [PR-Agent 公式ドキュメント](https://qodo-merge-docs.qodo.ai/)
- [GitHub Issues](https://github.com/Codium-ai/pr-agent/issues)
- [Discord コミュニティ](https://discord.gg/SgSxuQ65GF)

---

*このドキュメントは PR-Agent v0.3.0 対応版です*