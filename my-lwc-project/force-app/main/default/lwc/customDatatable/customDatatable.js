import { LightningElement, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

// ---------------------------
// ピックリスト選択肢
// ---------------------------
const REVIEW_RESULT_OPTIONS = [
  { label: "合格", value: "合格" },
  { label: "否認", value: "否認" },
  { label: "保留", value: "保留" },
  { label: "再審査", value: "再審査" },
  { label: "一時承認", value: "一時承認" }
];

const CREDIT_TYPE_OPTIONS = [
  { label: "新規", value: "新規" },
  { label: "更新", value: "更新" },
  { label: "延長", value: "延長" },
  { label: "追加", value: "追加" },
  { label: "削除", value: "削除" }
];

const SUBJECT_OPTIONS = [
  { label: "貸付金", value: "貸付金" },
  { label: "手形", value: "手形" },
  { label: "与信枠", value: "与信枠" },
  { label: "割引", value: "割引" },
  { label: "貸付金", value: "貸付金" },
  { label: "手形", value: "手形" },
  { label: "与信枠", value: "与信枠" },
  { label: "割引", value: "割引" },
  { label: "支払保証", value: "支払保証" }
];

const USAGE_TYPE_OPTIONS = [
  { label: "使用中", value: "使用中" },
  { label: "未使用", value: "未使用" },
  { label: "停止中", value: "停止中" },
  { label: "予定", value: "予定" }
];

// 稟議データを生成する関数
function generateMockData(count = 20) {
  return Array.from({ length: count }, (_, i) => ({
    Id: `${i + 1}`.padStart(3, "0"),
    Branch: "本店",
    Workplace: `部署 ${i + 1}`,

    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    CreditNo: `CR-${1000 + i}`,
    CreditType: CREDIT_TYPE_OPTIONS[i % CREDIT_TYPE_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    Authorization: i % 2 === 0,
    MonthEndSettlement: i % 3 === 0,
    UsageType: USAGE_TYPE_OPTIONS[i % USAGE_TYPE_OPTIONS.length].value,

    Inclusive: i % 4 === 0,
    AssessmentA: i % 2 === 0,
    AssessmentB: i % 3 === 0,
    BulkTransition: i % 5 === 0,

    PartnerDeadline: new Date(2025, 6, 1).toISOString().split("T")[0],
    ApprovalDate: new Date(2025, 6, 10).toISOString().split("T")[0],

    Description: `備考内容 ${i + 1}`,
    Confirmed: i % 2 === 1
  }));
}

export default class customDatatable extends LightningElement {
  // 稟議データ
  @track accounts = generateMockData(100);
  // ドラフト値
  @track draftValues = [];

  // 列定義
  columns = [
    { label: "選択", type: "checkbox" },
    { label: "支店", fieldName: "Branch", type: "text", editable: true },
    { label: "職場", fieldName: "Workplace", type: "text", editable: true },
    {
      label: "審査結果",
      fieldName: "ReviewResult",
      type: "picklistCell",
      editable: true,
      typeAttributes: { options: REVIEW_RESULT_OPTIONS }
    },
    { label: "与信番号", fieldName: "CreditNo", type: "text", editable: true },
    {
      label: "与信区分",
      fieldName: "CreditType",
      type: "picklistCell",
      editable: true,
      typeAttributes: { options: CREDIT_TYPE_OPTIONS }
    },
    {
      label: "科目",
      fieldName: "Subject",
      type: "picklistCell",
      editable: true,
      typeAttributes: { options: SUBJECT_OPTIONS }
    },
    {
      label: "実査権限",
      fieldName: "Authorization",
      type: "boolean",
      editable: true
    },
    {
      label: "月末与信決済",
      fieldName: "MonthEndSettlement",
      type: "boolean",
      editable: true
    },
    {
      label: "使用区分",
      fieldName: "UsageType",
      type: "picklistCell",
      editable: true,
      typeAttributes: { options: USAGE_TYPE_OPTIONS }
    },
    {
      label: "包括申請",
      fieldName: "Inclusive",
      type: "boolean",
      editable: true
    },
    {
      label: "A",
      fieldName: "AssessmentA",
      type: "boolean",
      editable: true
    },
    {
      label: "B",
      fieldName: "AssessmentB",
      type: "boolean",
      editable: true
    },
    {
      label: "一括推移",
      fieldName: "BulkTransition",
      type: "boolean",
      editable: true
    },
    {
      label: "取引先別期限",
      fieldName: "PartnerDeadline",
      type: "date",
      editable: true
    },
    {
      label: "審査承認日",
      fieldName: "ApprovalDate",
      type: "date",
      editable: true
    },
    { label: "備考", fieldName: "Description", type: "text", editable: true },
    {
      label: "確認",
      fieldName: "Confirmed",
      type: "boolean",
      editable: true
    }
  ];

  // 保存処理
  handleSave(event) {
    const updates = event.detail.draftValues;
    updates.forEach((d) => {
      const row = this.accounts.find((r) => r.Id === d.Id);
      if (row) Object.assign(row, d);
    });
    this.draftValues = [];
    this.dispatchEvent(
      new ShowToastEvent({
        title: "Saved (Mock)",
        message: `${updates.length} record(s) updated`,
        variant: "success"
      })
    );
  }
}
