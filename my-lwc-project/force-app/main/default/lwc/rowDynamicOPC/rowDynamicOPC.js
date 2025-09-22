import { LightningElement, api, track } from "lwc";
import {
  generateMockData,
  REVIEW_RESULT_OPTIONS,
  SUBJECT_OPTIONS
} from "./rowDynamicOPCMockData";
import { validateElement } from "c/f003GsV0000DataValidation";

/* ========================================
 * メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicOPC extends LightningElement {
  /* ----------------------------------------
   * プロパティ定義
   * ---------------------------------------- */
  /* 親コンポーネントから受領したデータ */
  @api tableData = [];
  /* 編集可能テーブルデータ（変更追跡用） */
  @track editableTableData = [];
  /* 選択された行のインデックス配列 */
  selectedRows = [];

  /* ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;

  connectedCallback() {
    // データ初期化：親からのデータがあれば使用、なければモックデータ
    if (this.tableData && this.tableData.length > 0) {
      this.editableTableData = [...this.tableData];
    } else {
      this.editableTableData = generateMockData(40);
      this.tableData = [...this.editableTableData];
    }
  }

  /**
   * カスタマイズテーブル・行選択処理
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowIndex = parseInt(event.target.dataset.idx, 10);
    const isAlreadySelected = this.selectedRows.includes(rowIndex);

    // 事前チェックで条件分岐を簡潔に
    if (checked) {
      if (!isAlreadySelected) {
        this.selectedRows.push(rowIndex);
      }
    } else {
      this.selectedRows = this.selectedRows.filter((idx) => idx !== rowIndex);
    }

    // 内部データ更新
    this.editableTableData = this.editableTableData.map((item, idx) =>
      idx === rowIndex ? { ...item, checked: checked } : item
    );

    // tableDataも同期更新
    this.tableData = [...this.editableTableData];
  }

  /**
   * カスタマイズテーブル・全選択・全選択解除処理
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked;

    // 選択行配列をリセット
    this.selectedRows = [];

    if (checked) {
      // 全データのインデックスを選択行配列に追加
      this.selectedRows = [...Array(this.editableTableData.length).keys()];
    }

    // 全データの checked フラグを更新
    this.editableTableData = this.editableTableData.map((item) => ({
      ...item,
      checked: checked
    }));

    // tableDataも同期更新
    this.tableData = [...this.editableTableData];
  }

  /* ----------------------------------------
   * 直接編集にしたため、以下の保存用データ取得メソッドは不要（既存の固定テーブルの直接編集のテーブルもデータ変更時にvalidate()関数を読んでいるだけ）
   * ----------------------------------------
   * 保存ボタン押下時の処理<br>
   *
   * @return { Array.<Object, Array.<Element>> } APIに渡す用のリストと、単項目チェック用のリストを返却する。
   */
  // @api
  // getSavingDatas() {
  //   let itemList = {};
  //   let validationResult = 0;

  //   // 画面上の固定要素からデータを取得
  //   const nonTableElements = this.template.querySelectorAll(
  //     "[data-id]:not(tr *)"
  //   );
  //   const [fixedData, validationElements] = getComponentDataList(
  //     nonTableElements,
  //     SAVING_FIELD_LIST
  //   );

  //   // バリデーション実行
  //   validateElement(validationElements);

  //   // 結果をまとめる
  //   itemList = { ...fixedData };
  //   itemList.tableData = this.tableData;

  //   return [itemList, validationResult];
  // }

  /* ----------------------------------------
   * データ入力関連のメソッド（直接編集機能）
   * ---------------------------------------- */

  /**
   * テーブル内の入力項目変更処理
   */
  handleInputChange(event) {
    // id = どのレコード(行)を更新するか (例: "rec001")
    // field = そのレコードのどのフィールド(列)を更新するか (例: "num1")
    const { id, field } = event.target.dataset;
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;

    // データ更新（常に実行）
    this.editableTableData = this.editableTableData.map((record) => {
      if (record.Id === id) {
        return { ...record, [field]: value };
      }
      return record;
    });

    // tableDataも同期
    this.tableData = [...this.editableTableData];

    // validation実行
    const inputElement = event.target;
    validateElement([inputElement], [], []);
  }

  /**
   * 親コンポーネント用：指定IDの要素を取得
   * @param {string} recordId レコードID
   * @returns {NodeList} 要素のリスト
   */
  @api
  getElementsById(recordId) {
    return this.template.querySelectorAll(`[data-id="${recordId}"]`);
  }

}
