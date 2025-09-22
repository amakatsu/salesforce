import { LightningElement, api, track } from "lwc";
import {
  generateMockData,
  REVIEW_RESULT_OPTIONS,
  SUBJECT_OPTIONS,
  PRIORITY_OPTIONS,
  STATUS_OPTIONS
} from "./rowDynamicMultiHeaderMockData";
import { validateElement } from "c/f003GsV0000DataValidation";

/* ========================================
 * メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicMultiHeader extends LightningElement {
  /* ----------------------------------------
   * プロパティ定義
   * ---------------------------------------- */
  /* 親コンポーネントから受領したデータ */
  @api tableData = [];
  /* 編集可能テーブルデータ（変更追跡用） */
  @track editableTableData = [];
  /* 選択された行のインデックス配列*/
  selectedRows = [];

  /* ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;
  priorityOptions = PRIORITY_OPTIONS;
  statusOptions = STATUS_OPTIONS;

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
   * データ入力関連のメソッド（直接編集機能）
   * ---------------------------------------- */
  /**
   * テーブルセル内の入力値変更時の処理
   *
   * @param {Event} event - 変更イベント（input, combobox, checkbox等）
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
    // 固定テーブルでもvalidateElementを呼び出しているだけで結果をどうしているかは謎。（要確認）
    validateElement([inputElement], [], []);
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
  //   let valid = 0;

  //   // 可変のテーブルデータを除いたdata-idを持つ要素を取得する。
  //   const notTableData = this.template.querySelectorAll("[data-id]:not(tr *)");

  //   const [iList, dList] = getComponentDataList(notTableData, SAVING_BTN_LIST);
  //   validateElement(dList);
  //   itemList = { ...iList };
  //   itemList.dtoList = this.tableData;

  // 下については、画面に表示されているデータを直接取得し、個別に改めて単項目チェックを実施する必要があるケースにおいて利用する。

  // // 可変のテーブルデータ以外の要素を取得する。
  // const tableDataList = [];

  // // 1行内のtr毎にNodeListを取得し、それぞれ処理したのち内容をマージする。
  // // trそのものにカスタムデータ属性もしくはtrをそれぞれ特定できるクラス名を定義する。
  // // 行内にtrタブが1つだけの場合は、trの取得のみで問題なし。
  // const rowData1 = this.template.querySelectorAll('tr[data-id="1"]');
  // const rowData2 = this.template.querySelectorAll('tr[data-id="2"]');

  // rowData1.forEach((_, idx) => {
  //   const dataCell1 = rowData1[idx].querySelectorAll('[data-id]');
  //   const dataCell2 = rowData2[idx].querySelectorAll('[data-id]');

  //   const [rowItemList1, rowDataList1] = getDataList(dataCell1, SAVING_BTN_LIST);
  //   const [rowItemList2, rowDataList2] = getDataList(dataCell2, SAVING_BTN_LIST);

  //   valid = checkItem(rowDataList1);
  //   valid = checkItem(rowDataList2);

  //   const mergeItemList = Object.assign(rowItemList1, rowItemList2);
  //   tableDataList.push(mergeItemList);
  // });

  // itemList.dtoList = tableDataList;

  //   return [itemList, valid];
  // }

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
