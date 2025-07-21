import LightningDatatable from "lightning/datatable";
import picklistView from "./picklistView.html";
import picklistEdit from "./picklistEdit.html";

/**
 * 拡張データテーブルコンポーネント
 * Lightning Datatableを継承し、カスタムセルタイプを提供します
 * 
 * 機能:
 * - picklistCellタイプによる選択リストの表示・編集
 * - 標準のDatatableの全機能を継承
 * - エラーハンドリングとアクセシビリティの向上
 */
export default class EditableDataTableDatatable extends LightningDatatable {
  /**
   * カスタムデータタイプ定義
   * 新しいセルタイプを追加する場合は、ここに定義を追加してください
   */
  static customTypes = {
    // 選択リスト（ピックリスト）セルタイプ
    picklistCell: {
      template: picklistView,        // 表示用テンプレート
      editTemplate: picklistEdit,    // 編集用テンプレート
      typeAttributes: ["options"],   // 必要な属性（選択肢のリスト）
      standardCellLayout: true,      // 標準セルレイアウトを使用
      editable: true                 // 編集可能フラグ
    }
    // 将来的に他のカスタムタイプを追加する場合は、ここに定義を追加
    // 例: datePickerCell, currencyCell, etc.
  };

  /**
   * コンポーネント初期化時の処理
   * 必要に応じてカスタム初期化ロジックを追加できます
   */
  connectedCallback() {
    super.connectedCallback();
    // カスタム初期化ロジックをここに追加可能
  }

  /**
   * エラーハンドリング用メソッド
   * セルの編集中にエラーが発生した場合の処理
   */
  handleCellError(error, cellInfo) {
    console.error('データテーブルセルでエラーが発生しました:', error);
    console.error('セル情報:', cellInfo);
    // 必要に応じてカスタムエラー処理を実装
  }
}