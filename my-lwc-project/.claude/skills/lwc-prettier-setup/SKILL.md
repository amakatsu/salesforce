---
name: lwc-prettier-setup
description: LWCプロジェクトのPrettier設定を自動検証・修正。「Prettier設定を確認して」「フォーマッタの設定を直して」と言われたら自動実行。
disable-model-invocation: true
---

# LWC Prettier Setup - Prettier設定検証・修正

## 概要
LWCプロジェクトのPrettier設定を検証し、LWC構文を破壊しない設定に修正する。

## 手順

### 1. 現状確認
- .prettierrc / .prettierrc.json / .prettierrc.yaml / .prettierrc.js の存在確認
- .prettierignore の存在確認
- package.json の prettier 設定確認

### 2. 問題検出
#### parser設定
- ❌ `"parser": "html"` → LWC構文を破壊する
- ✅ `"parser": "lwc"` またはオーバーライド設定

#### prettier-plugin-lwc
- インストール状況確認: `npm ls prettier-plugin-lwc`
- 未インストールなら推奨: `npm install --save-dev prettier-plugin-lwc`

#### overrides設定（推奨）
```json
{
  "overrides": [
    {
      "files": "*.html",
      "options": {
        "parser": "lwc"
      }
    }
  ]
}
```

### 3. 修正実行
- .prettierrc を LWC互換設定に更新
- prettier-plugin-lwc をインストール（必要なら）
- .prettierignore に不要なパスを追加

### 4. 検証
- サンプルLWC HTMLファイルにPrettierを実行して構文が壊れないことを確認
- 結果を報告
