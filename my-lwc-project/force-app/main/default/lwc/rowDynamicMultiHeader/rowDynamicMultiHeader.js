/* ========================================
 * 2行ヘッダー・2行データの固定列テーブル（JavaScript）
 * ========================================
 *
 * このJavaScriptが管理すること:
 * 1. テーブルデータの管理（2行構造に対応）
 * 2. 行選択機能（checked と dataCheck を分離）
 * 3. データ入力の反映とバリデーション
 * 4. テスト・デバッグ機能
 */

import { LightningElement, api, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { validateElement } from "c/f003GsV0000DataValidation";

/* ========================================
 * 1. 設定値の一元管理（カスタマイズ時はここを変更）
 * ======================================== */

// モックデータの件数
const MOCK_DATA_COUNT = 3;

/* ピックリスト選択肢定義 */
const REVIEW_RESULT_OPTIONS = [
  { label: "合格", value: "合格" },
  { label: "否認", value: "否認" },
  { label: "保留", value: "保留" },
  { label: "再審査", value: "再審査" },
  { label: "一時承認", value: "一時承認" },
  { label: "条件付き合格", value: "条件付き合格" },
  { label: "一部否認", value: "一部否認" },
  { label: "キャンセル", value: "キャンセル" },
  { label: "取下げ", value: "取下げ" },
  { label: "差戻し", value: "差戻し" },
  { label: "審査中", value: "審査中" },
  { label: "未審査", value: "未審査" }
];

const SUBJECT_OPTIONS = [
  { label: "貸付金", value: "貸付金" },
  { label: "手形", value: "手形" },
  { label: "与信枠", value: "与信枠" },
  { label: "割引", value: "割引" },
  { label: "支払保証", value: "支払保証" },
  { label: "リース", value: "リース" },
  { label: "デリバティブ", value: "デリバティブ" },
  { label: "コミットメントライン", value: "コミットメントライン" },
  { label: "スタンドバイ・クレジット", value: "スタンドバイ・クレジット" },
  { label: "その他金融商品", value: "その他金融商品" }
];

const PRIORITY_OPTIONS = [
  { label: "高", value: "高" },
  { label: "中", value: "中" },
  { label: "低", value: "低" }
];

const STATUS_OPTIONS = [
  { label: "処理中", value: "処理中" },
  { label: "完了", value: "完了" },
  { label: "保留", value: "保留" }
];

/* 保存対象フィールド定義（2行構造対応） */
const SAVING_FIELD_LIST = [
  // 基本情報
  "Id",
  "label",

  // 1行目データ（上段）
  "num1",
  "num2",
  "str1",
  "str2",
  "str3",
  "dataCheck",
  "ReviewResult",
  "Subject",
  "date1",
  "date2",

  // 2行目データ（下段）
  "num3",
  "num4",
  "str4",
  "str5",
  "str6",
  "checked2",
  "Priority",
  "Status",
  "date3",
  "date4"
];

/* ========================================
 * 2. モックデータ生成関数
 * ======================================== */

/**
 * テスト用のモックデータを生成
 * @param {number} count 生成するデータ件数
 * @return {Array} モックデータ配列
 */
function generateMockData(count = MOCK_DATA_COUNT) {
  return Array.from({ length: count }, (_, i) => ({
    // 基本情報
    Id: `${i + 1}`.padStart(3, "0"),
    label: `横ラベル${i + 1}`,
    checked: false, // 行選択用（UI表示のみ）

    // 1行目データ（上段）
    num1: 1000000 + i * 100000,
    num2: -2000000 - i * 200000,
    str1: `入力文字列1-${i + 1}`,
    str2: `表示文字列2-${i + 1}`,
    str3: `入力文字列3-${i + 1}`,
    dataCheck: i % 3 === 0, // データ用チェックボックス
    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    date1: new Date(2024, 0, 15 + i).toISOString().split("T")[0],
    date2: new Date(2024, 1, 15 + i).toISOString().split("T")[0],

    // 2行目データ（下段）
    num3: 3000000 + i * 300000,
    num4: -4000000 - i * 400000,
    str4: `詳細情報${i + 1}`,
    str5: `備考・メモ欄\n複数行テキスト${i + 1}`,
    str6: `追加情報${i + 1}`,
    checked2: i % 4 === 0,
    Priority: PRIORITY_OPTIONS[i % PRIORITY_OPTIONS.length].value,
    Status: STATUS_OPTIONS[i % STATUS_OPTIONS.length].value,
    date3: new Date(2024, 2, 1 + i).toISOString().split("T")[0],
    date4: new Date(2024, 3, 1 + i).toISOString().split("T")[0]
  }));
}

/* ========================================
 * 3. メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicMultiHeader extends LightningElement {
  /* ----------------------------------------
   * プロパティ定義
   * ---------------------------------------- */
  initialize = false;
  selectedRows = []; // 選択された行のインデックス配列

  /* テーブルデータ（リアクティブ） */
  @track tableData = structuredClone(generateMockData());

  /* ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;
  priorityOptions = PRIORITY_OPTIONS;
  statusOptions = STATUS_OPTIONS;

  /* ----------------------------------------
   * 行選択関連のメソッド
   * ---------------------------------------- */

  /**
   * 個別行の選択/解除処理
   * 注意：data.checked（行選択）と data.dataCheck（データ項目）を分離
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowIndex = parseInt(event.target.dataset.idx, 10);

    // 選択行配列の更新
    if (checked) {
      if (!this.selectedRows.includes(rowIndex)) {
        this.selectedRows.push(rowIndex);
      }
    } else {
      this.selectedRows = this.selectedRows.filter((idx) => idx !== rowIndex);
    }

    // tableData の checked フラグを更新
    this.tableData = this.tableData.map((item, idx) =>
      idx === rowIndex ? { ...item, checked: checked } : item
    );
  }

  /**
   * 全選択/全解除処理
   * ヘッダーのチェックボックス操作時に実行
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked;

    // 選択行配列をリセット
    this.selectedRows = [];

    if (checked) {
      // 全データのインデックスを選択行配列に追加
      this.selectedRows = [...Array(this.tableData.length).keys()];
    }

    // 全データの checked フラグを更新
    this.tableData = this.tableData.map((item) => ({
      ...item,
      checked: checked
    }));
  }

  /* ----------------------------------------
   * データ入力関連のメソッド
   * ---------------------------------------- */

  /**
   * テーブル内の入力項目変更処理
   * data-id と data-field を使用してデータを特定・更新
   */
  handleInputChange(event) {
    const { id, field } = event.target.dataset;
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;

    // 該当レコードのフィールドを更新
    this.tableData = this.tableData.map((record) => {
      if (record.Id === id) {
        return { ...record, [field]: value };
      }
      return record;
    });
  }

  /**
   * レコード一括更新処理（外部API用）
   * @param {Object} updatedRecord 更新するレコードデータ
   */
  updateRecord(updatedRecord) {
    this.tableData = this.tableData.map((item) => {
      if (item.Id === updatedRecord.Id) {
        return { ...item, ...updatedRecord };
      }
      return item;
    });
  }

  /* ----------------------------------------
   * データ保存関連のメソッド
   * ---------------------------------------- */

  /**
   * 保存用データ取得（API呼び出し用）
   * @return {Array} [保存データオブジェクト, バリデーション結果]
   */
  @api
  getSavingDatas() {
    let itemList = {};
    let validationResult = 0;

    // 画面上の固定要素からデータを取得
    const nonTableElements = this.template.querySelectorAll(
      "[data-id]:not(tr *)"
    );
    const [fixedData, validationElements] = getComponentDataList(
      nonTableElements,
      SAVING_FIELD_LIST
    );

    // バリデーション実行
    validateElement(validationElements);

    // 結果をまとめる
    itemList = { ...fixedData };
    itemList.tableData = this.tableData;

    return [itemList, validationResult];
  }

  /* ----------------------------------------
   * テスト・デバッグ用メソッド
   * ---------------------------------------- */

  /**
   * 選択されたデータの詳細表示（開発・テスト用）
   * 選択機能が正常に動作しているかを確認
   */
  handleTestSelectedData() {
    const selectedData = this.tableData.filter((_, idx) =>
      this.selectedRows.includes(idx)
    );

    let message = `【選択データ詳細】\n選択件数: ${selectedData.length}件\n\n`;
    selectedData.forEach((data, i) => {
      message += `[${i + 1}] ID:${data.Id} ${data.label}\n`;
      message += `  上段: 数値1=${data.num1} 文字列1=${data.str1}\n`;
      message += `  下段: 数値3=${data.num3} 文字列4=${data.str4}\n`;
      message += `  チェック: データ=${data.dataCheck} 選択=${data.checked}\n\n`;
    });

    alert(message);
  }

  /**
   * 全データ構造の表示（開発・テスト用）
   * データ構造と選択状態の整合性を確認
   */
  handleTestAllData() {
    const checkedCount = this.tableData.filter((data) => data.checked).length;
    const selectedCount = this.selectedRows.length;

    let message = `【全データ構造】\n`;
    message += `総データ数: ${this.tableData.length}件\n`;
    message += `選択データ数: ${checkedCount}件\n`;
    message += `選択行配列: ${selectedCount}件\n\n`;

    this.tableData.slice(0, 3).forEach((data, i) => {
      const isSelected = this.selectedRows.includes(i) ? "★" : "　";
      message += `${isSelected}[${i + 1}] ${data.label}\n`;
      message += `  上段: ${data.str1} / 下段: ${data.str4}\n`;
      message += `  選択=${data.checked} データ=${data.dataCheck}\n\n`;
    });

    if (this.tableData.length > 3) {
      message += `...他 ${this.tableData.length - 3}件`;
    }

    alert(message);
  }

  /**
   * 全選択テスト（開発・テスト用）
   */
  handleSelectAllTest() {
    const event = { target: { checked: true } };
    this.handleSelectFullCheck(event);

    this.dispatchEvent(
      new ShowToastEvent({
        title: "全選択完了",
        message: `${this.tableData.length}件すべて選択されました`,
        variant: "success"
      })
    );
  }

  /**
   * 全解除テスト（開発・テスト用）
   */
  handleDeselectAllTest() {
    const event = { target: { checked: false } };
    this.handleSelectFullCheck(event);

    this.dispatchEvent(
      new ShowToastEvent({
        title: "全解除完了",
        message: "すべての選択が解除されました",
        variant: "info"
      })
    );
  }

  /**
   * 保存データ構造テスト（開発・テスト用）
   * getSavingDatas()の動作と返されるデータ構造を確認
   */
  handleTestSavingData() {
    try {
      const [itemList, validation] = this.getSavingDatas();

      let message = `【保存データ構造】\n`;
      message += `テーブルデータ数: ${itemList.tableData.length}件\n`;
      message += `バリデーション結果: ${validation}\n\n`;

      message += `サンプルデータ（最初の2件）:\n`;
      itemList.tableData.slice(0, 2).forEach((data, i) => {
        message += `[${i + 1}] ID:${data.Id} ${data.label}\n`;
        message += `  上段: 数値1=${data.num1} 文字列1=${data.str1}\n`;
        message += `  下段: 数値3=${data.num3} 詳細=${data.str4}\n`;
        message += `  選択=${data.checked} データチェック=${data.dataCheck}\n\n`;
      });

      alert(message);
    } catch (error) {
      alert(`【エラー】\n保存データ取得に失敗\nエラー: ${error.message}`);
    }
  }

  /**
   * 保存処理（モック実装）
   * 実際のAPIコール処理はここに実装
   */
  handleSave() {
    this.dispatchEvent(
      new ShowToastEvent({
        title: "保存完了",
        message: "データが正常に保存されました（モック）",
        variant: "success"
      })
    );
  }
}

/* ========================================
 * 補足説明
 * ========================================
 *
 * 【2行データ構造について】
 * 1レコードが上段・下段の2行で表示される構造。
 * - 上段: num1, str1-3, dataCheck, ReviewResult, Subject, date1-2
 * - 下段: num3-4, str4-6, checked2, Priority, Status, date3-4
 *
 * 【チェックボックスの分離】
 * - data.checked: 行選択用（UI制御のみ）
 * - data.dataCheck: データ項目（保存対象）
 * この分離により、行選択とデータ項目が独立して動作。
 *
 * 【選択機能の仕組み】
 * - selectedRows配列: 選択された行のインデックスを管理
 * - data.checked: UI表示用の選択状態
 * - 両方が同期して動作するように制御
 *
 * 【カスタマイズポイント】
 * - MOCK_DATA_COUNT: テストデータの件数
 * - ピックリストオプション: 各選択肢配列
 * - SAVING_FIELD_LIST: 保存対象フィールド
 */
