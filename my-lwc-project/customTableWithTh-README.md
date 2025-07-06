# カスタムテーブル（TH 付き）

このコンポーネントは、`<th>`要素を持つカスタムテーブルのデモンストレーションです。

## 目的

- `lightning-datatable`を使用せずに、標準の HTML `<table>`要素と SLDS クラスを使用して編集可能なテーブルを作成する方法を示します。
- 各行にチェックボックスがあり、すべての行を選択/選択解除する機能を提供します。

## 使い方

1.  **`customTableWithTh.js`**:

    - デモンストレーション用に 100 行のモックデータを生成します。
    - `handleSelectAll`関数は、ヘッダーのチェックボックスがクリックされたときにすべての行を選択または選択解除します。
    - `handleRowSelection`関数は、個々の行のチェックボックスの状態を処理します。
    - `handleInputChange`関数は、テーブル内の入力フィールド（テキスト、チェックボックス、コンボボックス）の変更を処理します。
    - `handleSave`関数は、変更を保存するためのプレースホルダーです（現在はモックのトースト通知のみ）。

2.  **`customTableWithTh.html`**:
    - SLDS クラスを使用してスタイル設定された標準の HTML `<table>`を使用します。
    - テーブルヘッダー（`<thead>`）は手動で定義されます。
    - テーブルボディ（`<tbody>`）は、`accounts`データの各行をループ処理して生成されます。
    - 各セルには、`lightning-input`または`lightning-combobox`が含まれており、インライン編集が可能です。

## 主要な概念

- **SLDS（Salesforce Lightning Design System）**: `lightning-datatable`を使用せずに、標準の HTML 要素で Salesforce の外観と一致するテーブルを作成するために使用されます。
- **手動でのテーブル作成**: `lightning-datatable`の代わりに`<table>`、`<thead>`、`<tbody>`、`<tr>`、`<th>`、および`<td>`要素を直接使用します。これにより、テーブルの構造とスタイルをより細かく制御できます。
- **双方向データバインディング（手動）**: `onchange`イベントハンドラを使用して、入力の変更を JavaScript プロパティに手動で反映させます。
