---
name: lwc-analyzer
description: LWCコンポーネントの構造・依存関係・データフローを自動分析してレポート生成。「LWCを分析して」「コンポーネントの構造を教えて」と言われたら自動実行。
disable-model-invocation: true
argument-hint: "[component-path]"
---

# LWC Analyzer - LWCコンポーネント構造分析

## 概要
LWCコンポーネントの構造・依存関係・データフローを分析し、レポートを生成する。

## 手順

### 1. 対象の特定
- $ARGUMENTS で指定されたパスのコンポーネントを対象
- 子コンポーネントも自動検出（同名プレフィックスで検索）

### 2. ファイル構成の分析
- 各コンポーネントのファイル一覧（HTML, JS, CSS, meta.xml）
- 欠落ファイルの検出（特に .js-meta.xml）

### 3. HTML構造の分析
- 使用しているlightning-*コンポーネント
- カスタムコンポーネント（c-*）の依存関係
- テンプレートディレクティブ（if:true, for:each等）の使用状況
- イベントハンドラのバインディング

### 4. JS構造の分析
- @api, @track, @wire デコレータの使用状況
- Apex呼び出し（import from '@salesforce/apex/*'）
- カスタムイベント（CustomEvent）の発火
- ライフサイクルフック（connectedCallback, renderedCallback等）
- import文の依存関係

### 5. データフローの分析
- 親→子のデータ伝達（@api プロパティ）
- 子→親のイベント伝達（CustomEvent）
- 状態管理パターン（state.js等）

### 6. 課題の検出
- 構文エラー（onclick記法不正等）
- 未定義プロパティ参照
- デッドコード
- パフォーマンス懸念（不要なリレンダリング等）

### 7. レポート出力
以下の形式で出力:
```
## コンポーネント分析レポート
### 概要
### ファイル構成
### 依存関係図
### データフロー
### 検出課題（重要度順）
### 改善提案
```
