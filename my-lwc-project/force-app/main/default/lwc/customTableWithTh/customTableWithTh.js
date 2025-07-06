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
  { label: "一時承認", value: "一時承認" },
  { label: "条件付き合格", value: "条件付き合格" },
  { label: "一部否認", value: "一部否認" },
  { label: "キャンセル", value: "キャンセル" },
  { label: "取下げ", value: "取下げ" },
  { label: "差戻し", value: "差戻し" },
  { label: "審査中", value: "審査中" },
  { label: "未審査", value: "未審査" }
];

const CREDIT_TYPE_OPTIONS = [
  { label: "新規", value: "新規" },
  { label: "更新", value: "更新" },
  { label: "延長", value: "延長" },
  { label: "追加", value: "追加" },
  { label: "削除", value: "削除" },
  { label: "変更", value: "変更" },
  { label: "見直し", value: "見直し" },
  { label: "臨時", value: "臨時" },
  { label: "定例", value: "定例" },
  { label: "緊急", value: "緊急" },
  { label: "その他", value: "その他" }
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

const USAGE_TYPE_OPTIONS = [
  { label: "使用中", value: "使用中" },
  { label: "未使用", value: "未使用" },
  { label: "停止中", value: "停止中" },
  { label: "予定", value: "予定" },
  { label: "一部使用", value: "一部使用" },
  { label: "予約済", value: "予約済" },
  { label: "期限切れ", value: "期限切れ" },
  { label: "解約済", value: "解約済" },
  { label: "凍結中", value: "凍結中" },
  { label: "調査中", value: "調査中" }
];

// 稟議データを生成する関数
function generateMockData(count = 100) {
  return Array.from({ length: count }, (_, i) => ({
    Id: `${i + 1}`.padStart(3, "0"),
    isSelected: false,
    Branch: "本店",
    Workplace: `部署 ${i + 1}`,
    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    CreditNo: `${1000 + i}`,
    CreditType: CREDIT_TYPE_OPTIONS[i % CREDIT_TYPE_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    Authorization: i % 2 === 0,
    MonthEndSettlement: i % 3 === 0,
    UsageType: USAGE_TYPE_OPTIONS[i % USAGE_TYPE_OPTIONS.length].value,
    Inclusive: i % 4 === 0,
    AssessmentA: i % 2 === 0,
    AssessmentB: i % 3 === 0,
    BulkTransition: i % 5 === 0,
    PartnerDeadline: new Date(2025, 6, 1 + i).toISOString().split("T")[0],
    ApprovalDate: new Date(2025, 6, 10 + i).toISOString().split("T")[0],
    Description: `備考内容 ${i + 1}`,
    Confirmed: i % 2 === 1
  }));
}

export default class customTableWithTh extends LightningElement {
  // 稟議データ
  @track accounts = generateMockData(100);

  get processedAccounts() {
    return this.accounts.map((account) => {
      const badge = {};
      switch (account.ReviewResult) {
        case "合格":
        case "一時承認":
        case "条件付き合格":
          badge.class = "slds-badge slds-badge_success";
          badge.label = account.ReviewResult;
          break;
        case "否認":
        case "一部否認":
          badge.class = "slds-badge slds-badge_error";
          badge.label = account.ReviewResult;
          break;
        case "保留":
        case "再審査":
          badge.class = "slds-badge slds-badge_warning";
          badge.label = account.ReviewResult;
          break;
        default:
          badge.class = "slds-badge";
          badge.label = account.ReviewResult;
      }
      return { ...account, badge };
    });
  }

  // テンプレートで利用する選択肢
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  creditTypeOptions = CREDIT_TYPE_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;
  usageTypeOptions = USAGE_TYPE_OPTIONS;

  get allRowsSelected() {
    return this.accounts.every((acc) => acc.isSelected);
  }

  handleSelectAll(event) {
    const isChecked = event.target.checked;
    this.accounts = this.accounts.map((acc) => ({
      ...acc,
      isSelected: isChecked
    }));
  }

  handleRowSelection(event) {
    const { id } = event.currentTarget.dataset;
    const isChecked = event.target.checked;

    const account = this.accounts.find((acc) => acc.Id === id);
    if (account) {
      account.isSelected = isChecked;
      this.accounts = [...this.accounts];
    }
  }

  // 入力変更時の処理
  handleInputChange(event) {
    const { id, field } = event.currentTarget.dataset;
    const value =
      event.target.type === "checkbox"
        ? event.detail.checked
        : event.detail.value;

    const account = this.accounts.find((acc) => acc.Id === id);
    if (account) {
      account[field] = value;
      this.accounts = [...this.accounts];
    }
  }

  // 保存処理
  handleSave() {
    // ここでApexを呼び出してサーバーにデータを保存するロジックを実装できます。
    // 今回はモックなので、Toastメッセージのみ表示します。
    this.dispatchEvent(
      new ShowToastEvent({
        title: "Success",
        message: "Records updated successfully (mock).",
        variant: "success"
      })
    );
  }
}
