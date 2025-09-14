import { LightningElement, api, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { validateElement } from "c/f003GsV0000DataValidation";

/* =========================================
 * ピックリスト選択肢定義
 * ========================================= */
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

/* =========================================
 * モックデータ生成関数
 * ========================================= */
function generateMockData(count = 3) {
  return Array.from({ length: count }, (_, i) => ({
    Id: `${i + 1}`.padStart(3, "0"),
    label: `横ラベル${i + 1}`,
    num1: 7777777 + i * 1111111,
    num2: -7777777 - i * 1111111,
    str1: `サンプル参照テキスト${i + 1}`,
    str2: `サンプル入力テキスト${i + 1}`,
    checked: i % 2 === 0,
    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    date1: new Date(2023, 8, 15 + i).toISOString().split("T")[0],
    date2: new Date(2023, 9, 15 + i).toISOString().split("T")[0]
  }));
}

/* =========================================
 * 保存対象のフィールド定義
 * ========================================= */
const SAVING_BTN_LIST = [
  "Id",
  "label",
  "num1",
  "num2",
  "str1",
  "str2",
  "checked",
  "ReviewResult",
  "Subject",
  "date1",
  "date2"
];

/* =========================================
 * LWCコンポーネントクラス
 * ========================================= */
export default class RowDynamicOPC extends LightningElement {
  initialize = false;
  selectedRows = [];
  /* 行データ - structuredCloneで深いコピーを作成し可変データにする */
  @track tableData = [...structuredClone(generateMockData(50))];

  /**
   * カスタマイズテーブル・行選択処理
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowidx = parseInt(event.target.dataset.idx, 10);
    const havingFlg = this.selectedRows.includes(rowidx);
    if (checked) {
      if (havingFlg) {
        this.selectedRows = this.selectedRows.filter(function (selectRow) {
          return selectRow !== rowidx;
        });
      } else {
        this.selectedRows.push(rowidx);
      }
    } else {
      this.selectedRows = this.selectedRows.filter(function (selectRow) {
        return selectRow !== rowidx;
      });
    }
    this.tableData = this.tableData.map((item, idx) =>
      idx === rowidx ? { ...item, checked: checked } : item
    );
  }

  /**
   * カスタマイズテーブル・全選択・全選択解除処理
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked; // 選択行の初期化
    this.selectedRows = [];
    if (checked) {
      // 取得した件数分のインデックス番号があればいい。
      this.selectedRows = [...Array(this.tableData.length).keys()];
    }
    this.tableData = this.tableData.map((item) => ({
      ...item,
      checked: checked
    }));
  }

  /**
   * レコード更新処理
   */
  updateRecord(updatedRecord) {
    // 行番号が一致しているテーブルデータを更新
    this.tableData = this.tableData.map((item) => {
      if (item.Id === updatedRecord.Id) {
        return { ...item, ...updatedRecord };
      }
      return item;
    });
  }

  /**
   * 保存ボタン押下時の処理<br>
   *
   * @return { Array.<Object, Array.<Element>> } APIに渡す用のリストと、単項目チェック用のリストを返却する。
   */
  @api
  getSavingDatas() {
    let itemList = {};
    let valid = 0; // 可変のテーブルデータを除いたdata-idを持つ要素を取得する。
    const notTableData = this.template.querySelectorAll("[data-id]:not(tr *)");
    const [iList, dList] = getComponentDataList(notTableData, SAVING_BTN_LIST);
    validateElement(dList);
    itemList = { ...iList };
    itemList.tableData = this.tableData; // 下については、画面に表示されているデータを直接取得し、個別に改めて単項目チェックを実施する必要があるケースにおいて利用する。     return [itemList, valid];
  }

  /* ---------- ピックリスト ---------- */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;

  /* ==========================================
   * rowDynamicOPC固有のメソッド（テスト用など）
   * ========================================== */

  /* ---------- POC固有の入力処理メソッド ---------- */

  /**
   * テーブル内の各行データ（tableData配列）への入力値反映処理
   * 必要な理由: POCのHTMLテンプレートがdata-id, data-fieldパターンを使用しているため
   * Sample1とは異なるデータバインディング方式に対応
   */
  handleInputChange(event) {
    const { id, field } = event.target.dataset;
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;

    this.tableData = this.tableData.map((account) => {
      if (account.Id === id) {
        return { ...account, [field]: value };
      }
      return account;
    });
  }

  /* ---------- テスト用メソッド ---------- */

  /**
   * 選択されたデータの詳細表示テスト
   * 検証対象: handleRowSelection()による selectedRows の管理と tableData の checked 状態
   */
  handleTestSelectedData() {
    const selectedAccounts = this.tableData.filter((_, idx) =>
      this.selectedRows.includes(idx)
    );

    // ポップアップで詳細なデータ表示
    let alertMessage = `【選択されたデータ詳細】\n選択された行数: ${selectedAccounts.length}件\n\n`;
    selectedAccounts.forEach((account, i) => {
      alertMessage += `[${i + 1}] ID:${account.Id} ラベル:${account.label}\n`;
      alertMessage += `   数値1:${account.num1} 数値2:${account.num2}\n`;
      alertMessage += `   文字列1:${account.str1} 文字列2:${account.str2}\n`;
      alertMessage += `   審査結果:${account.ReviewResult} 科目:${account.Subject}\n`;
      alertMessage += `   チェック:${account.checked} 日付1:${account.date1} 日付2:${account.date2}\n\n`;
    });

    alert(alertMessage);
  }

  /**
   * 全データと選択状態の詳細表示テスト
   * 検証対象: tableData 配列の構造、selectedRows との整合性、データの入力反映状況
   */
  handleTestAllData() {
    // 選択状態の確認
    const checkedCount = this.tableData.filter((acc) => acc.checked).length;
    const selectedCount = this.selectedRows.length;

    // ポップアップで全データ表示
    let alertMessage = `【全データ表示】\n全データ数: ${this.tableData.length}件\nチェック状態: ${checkedCount}件\n選択行配列: ${selectedCount}件\n\n`;

    this.tableData.forEach((account, i) => {
      const isSelected = this.selectedRows.includes(i) ? "★" : "　";
      alertMessage += `${isSelected}[${i + 1}] ID:${account.Id} ${
        account.label
      }\n`;
      alertMessage += `   数値1:${account.num1} 数値2:${account.num2}\n`;
      alertMessage += `   文字列1:${account.str1} 文字列2:${account.str2}\n`;
      alertMessage += `   審査結果:${account.ReviewResult} 科目:${account.Subject}\n`;
      alertMessage += `   チェック:${account.checked} 日付1:${account.date1} 日付2:${account.date2}\n\n`;
    });

    alert(alertMessage);
  }

  /**
   * 全選択機能のテスト
   * 検証対象: handleSelectFullCheck(checked: true) の動作
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
   * 全解除機能のテスト
   * 検証対象: handleSelectFullCheck(checked: false) の動作
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
   * 保存データ取得機能のテスト
   * 検証対象: getSavingDatas() の動作、バリデーション処理、データ構造の確認
   */
  handleTestSavingData() {
    try {
      const [itemList, valid] = this.getSavingDatas();

      let alertMessage = `【保存データ取得テスト】\nテーブルデータ数: ${itemList.tableData.length}件\nバリデーション結果: ${valid}\n\n`;

      itemList.tableData.forEach((account, i) => {
        alertMessage += `[${i + 1}] ID:${account.Id} ${account.label}\n`;
        alertMessage += `   数値1:${account.num1} 文字列1:${account.str1}\n`;
        alertMessage += `   審査結果:${account.ReviewResult} チェック:${account.checked}\n\n`;
      });

      alert(alertMessage);
    } catch (error) {
      alert(
        `【エラー】\n保存データ取得に失敗しました\nエラー内容: ${error.message}`
      );
    }
  }

  /* ---------- 保存（モック） ---------- */
  handleSave() {
    this.dispatchEvent(
      new ShowToastEvent({
        title: "Success",
        message: "Records updated successfully (mock).",
        variant: "success"
      })
    );
  }
}
