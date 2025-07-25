# カスタム編集可能データテーブル

このコンポーネントは、モックデータを使用したカスタム編集可能データテーブルのデモンストレーションです。

## 目的

- 編集可能で、カスタムセルタイプ（picklistCell）を使用する`lightning-datatable`の例を提供します。
- ドラフト値の保存を処理する方法を示します。

## 使い方

1.  **`customDatatable.js`**:

    - デモンストレーション用に 100 行のモックデータを生成します。
    - `picklistCell`などのカスタムタイプを含む、データテーブルの列を定義します。
    - `handleSave`関数は、ユーザーがデータテーブルの保存ボタンをクリックしたときに呼び出されます。ローカルデータをドラフト値で更新し、トースト通知を表示します。

2.  **`customDatatable.html`**:
    - `c-editable-data-table-datatable`コンポーネントを使用してデータを表示します。
    - `key-field`、`data`、`columns`、および`draft-values`属性がデータテーブルに渡されます。
    - `onsave`イベントは`handleSave`関数によって処理されます。

## 主要な概念

- **`lightning-datatable`**: 表形式のデータを表示するための標準 LWC コンポーネント。
- **インライン編集**: 列定義の`editable`プロパティにより、ユーザーはテーブル内で直接セル値を編集できます。
- **ドラフト値**: ユーザーがセルを編集すると、変更は明示的に保存されるまで「ドラフト値」として保存されます。
- **カスタムセルタイプ**: データテーブルは、ピクリストなどのよりリッチな編集体験を提供するために、カスタムセルタイプで拡張できます。
