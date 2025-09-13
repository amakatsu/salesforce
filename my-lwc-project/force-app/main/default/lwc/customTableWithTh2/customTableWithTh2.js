import { LightningElement, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

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
function generateMockData(count = 2) {
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
 * LWCコンポーネントクラス
 * ========================================= */
export default class CustomTableWithTh extends LightningElement {
  /* 行データ */
  @track accounts = generateMockData(2);

  /* ---------- テンプレート描画用 ---------- */
  get processedAccounts() {
    return this.accounts;
  }

  handleRecordValueChange(event) {
    this.record[event.target.dataset.id] = event.target.value;
    const inputElement = event.target;
    const childDataList = [inputElement];
    validateElement(childDataList);
  }

  handleRecordCheckedChange(event) {
    this.record[event.target.dataset.id] = event.target.checked;
  }

  handleComboboxChange(event) {
    const { id } = event.target.dataset;
    this.record[id] = event.target.value;
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

  /* ---------- ピックリスト ---------- */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;
}
