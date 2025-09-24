import { LightningElement, api, track } from "lwc";
import {
  generateMockData,
  REVIEW_RESULT_OPTIONS,
  SUBJECT_OPTIONS
} from "./rowDynamicOPCMockData";
import { validateElement } from "c/f003GsV0000DataValidation";

// ========================================
// API連携用定数定義（ガイドライン準拠）
// ========================================

/** API連携（正常・連携1回）用項目リスト */
export const OPC_API_SUCCESS1_LIST = [
  'num1', 'num2', 'str1', 'str2',
  'dataCheck', 'ReviewResult', 'Subject', 'date1'
];

/** API連携（正常・連携1回）用必須項目リスト */
export const OPC_API_SUCCESS1_REQ_LIST = ['num1', 'str1'];

/* ========================================
 * メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicOPC extends LightningElement {

  // ========================================
  // プロパティ定義
  // ========================================

  /** 親コンポーネントから受領したデータ */
  @api tableData = [];

  /** 編集可能テーブルデータ（変更追跡用） */
  @track editableTableData = [];

  /** 選択された行のインデックス配列 */
  selectedRows = [];

  /** ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;

  // ========================================
  // ライフサイクルメソッド
  // ========================================

  /**
   * コンポーネント初期化
   * データ初期化：親からのデータがあれば使用、なければモックデータ
   */
  connectedCallback() {
    if (this.tableData && this.tableData.length > 0) {
      this.editableTableData = [...this.tableData];
    } else {
      this.editableTableData = generateMockData(40);
      this.tableData = [...this.editableTableData];
    }
  }

  // ========================================
  // テーブル操作イベントハンドラー
  // ========================================

  /**
   * 個別行選択処理
   * @param {Event} event チェックボックス変更イベント
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowIndex = parseInt(event.target.dataset.idx, 10);
    const isAlreadySelected = this.selectedRows.includes(rowIndex);

    // 選択状態の更新
    if (checked) {
      if (!isAlreadySelected) {
        this.selectedRows.push(rowIndex);
      }
    } else {
      this.selectedRows = this.selectedRows.filter((idx) => idx !== rowIndex);
    }

    // データ同期更新
    this.editableTableData = this.editableTableData.map((item, idx) =>
      idx === rowIndex ? { ...item, checked: checked } : item
    );
    this.tableData = [...this.editableTableData];
  }

  /**
   * 全行選択・全選択解除処理
   * @param {Event} event 全選択チェックボックス変更イベント
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked;

    // 選択行配列をリセット
    this.selectedRows = [];

    if (checked) {
      // 全データのインデックスを選択行配列に追加
      this.selectedRows = [...Array(this.editableTableData.length).keys()];
    }

    // 全データのcheckedフラグを更新
    this.editableTableData = this.editableTableData.map((item) => ({
      ...item,
      checked: checked
    }));
    this.tableData = [...this.editableTableData];
  }

  // ========================================
  // データ入力・編集処理
  // ========================================

  /**
   * テーブルセル内の入力値変更時の処理
   * @param {Event} event 変更イベント（input, combobox, checkbox等）
   */
  handleInputChange(event) {
    // データ識別用の属性取得
    // id = どのレコード(行)を更新するか (例: "rec001")
    // field = そのレコードのどのフィールド(列)を更新するか (例: "num1")
    const { id, field } = event.target.dataset;
    const value = event.target.type === "checkbox" ? event.target.checked : event.target.value;

    // データ更新（該当レコードの該当フィールドを更新）
    this.editableTableData = this.editableTableData.map((record) => {
      if (record.Id === id) {
        return { ...record, [field]: value };
      }
      return record;
    });

    // データ同期
    this.tableData = [...this.editableTableData];

    // 入力時バリデーション実行
    const inputElement = event.target;
    validateElement([inputElement], [], []);
  }

  // ========================================
  // 親コンポーネント向けAPIメソッド
  // ========================================

  /**
   * DOM要素取得API
   * 用途：親コンポーネントのhandleDataVerificationで使用
   * @param {string} recordId レコードID
   * @returns {NodeList} 指定IDの要素リスト
   */
  @api
  getElementsById(recordId) {
    return this.template.querySelectorAll(`[data-id="${recordId}"]`);
  }

  /**
   * データ取得・バリデーションAPI
   * 用途：親コンポーネントのhandleApiSaveで使用
   * @param {boolean} selectedOnly 選択データのみか全データか（デフォルト: true）
   * @param {Array} reqList 必須項目リスト（デフォルト: ['num1', 'str1']）
   * @returns {Array} [itemList, validationErrorCount]
   */
  @api
  getApiDataList(selectedOnly = true, reqList = OPC_API_SUCCESS1_REQ_LIST) {
    let validationErrorCount = 0;

    try {
      // 対象データを決定
      const targetData = selectedOnly
        ? this.editableTableData.filter((item) => item.checked)
        : this.editableTableData;

      // データが空の場合の処理
      if (targetData.length === 0) {
        return [{ tableData: [] }, selectedOnly ? 0 : 1];
      }

      // 各レコードのバリデーション処理
      targetData.forEach((record) => {
        const elements = this.getElementsById(record.Id);

        if (elements.length > 0) {
          // validateElement関数を呼び出し、バリデーション結果を取得
          const validationResult = validateElement(
            Array.from(elements),
            reqList,
            []
          );
          validationErrorCount += validationResult;
        }
      });

      // レスポンス用データオブジェクト生成
      const itemList = {
        tableData: targetData,
        [selectedOnly ? "selectedCount" : "totalCount"]: targetData.length,
        componentName: "rowDynamicOPC",
        apiType: selectedOnly ? "success" : "error"
      };

      return [itemList, validationErrorCount];
    } catch (error) {
      console.error("Error in getApiDataList:", error);
      throw error;
    }
  }
}
