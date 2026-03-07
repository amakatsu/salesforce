---
name: lwc-format
description: LWCコンポーネントのHTML/JS/CSSを一括フォーマット。Prettier実行後にLWC構文を検証・修復する。「LWCをフォーマットして」「コードを整形して」と言われたら自動実行。
disable-model-invocation: true
argument-hint: "[component-path]"
---

# LWC Format - LWCコンポーネント一括フォーマッタ

## 概要
LWCコンポーネントのHTML/JS/CSSをフォーマットし、LWC固有の構文を保護する。

## 手順

### 1. 対象の特定
- $ARGUMENTS で指定されたパスのコンポーネントを対象とする
- 指定がなければカレントディレクトリのLWCコンポーネントを対象

### 2. Prettier実行
```bash
cd [project-root] && npx prettier --write "$ARGUMENTS/**/*.{html,js,css}"
```

### 3. .prettierrc 確認
- プロジェクトの .prettierrc を確認
- `"parser": "html"` が指定されている場合、LWC構文を破壊するため警告
- 推奨: `"parser": "lwc"` または prettier-plugin-lwc の導入

### 4. LWC構文検証・修復（Prettier実行後に必須）
Prettierが破壊しやすいLWC構文を検証・修復する:

#### イベントハンドラ式
- ❌ `onclick="{ handler; }"` → ✅ `onclick={handler}`
- ❌ `onchange="{ handler; }"` → ✅ `onchange={handler}`
- 全てのon*属性を検証

#### テンプレートディレクティブ
- `if:true`, `if:false`, `for:each`, `for:item`, `iterator:*` が壊れていないか確認
- lwc:if, lwc:elseif, lwc:else の構文確認

#### データバインディング
- `{property}` 形式が維持されているか確認
- ネストされたプロパティ `{object.property}` の確認

### 5. 手動整形（Prettierで対応できない部分）
- HTML属性が1行に詰め込まれている場合、属性ごとに改行
- JSのメソッド間に適切な空行を挿入
- 不要な空行の削除

### 6. 最終確認
- Prettierを再実行して構文が壊れないことを確認
- 変更されたファイル一覧を報告
