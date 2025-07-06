import LightningDatatable from "lightning/datatable";
import picklistView from "./picklistView.html";
import picklistEdit from "./picklistEdit.html";

// 拡張データテーブルコンポーネント
export default class EditableDataTableDatatable extends LightningDatatable {
  // カスタムデータタイプ定義
  static customTypes = {
    picklistCell: {
      template: picklistView, // 表示テンプレート
      editTemplate: picklistEdit, // 編集テンプレート
      typeAttributes: ["options"], // タイプ属性
      standardCellLayout: true, // 標準セルレイアウト
      editable: true // 編集可能
    }
  };
}
