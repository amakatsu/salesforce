import { LightningElement, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

/* ────────────── ピックリスト選択肢 ────────────── */
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

/* ────────────── 選択候補データ ────────────── */
const SELECTION_OPTIONS = [
  { label: "優先度A", value: "priority_a", description: "最高優先で処理" },
  { label: "優先度B", value: "priority_b", description: "通常優先で処理" },
  { label: "優先度C", value: "priority_c", description: "低優先で処理" }
];

/* ────────────── モックデータ生成 ────────────── */
function generateMockData(count = 100) {
  return Array.from({ length: count }, (_, i) => ({
    Id: `${i + 1}`.padStart(3, "0"),
    isSelected: false,
    Branch: "本店",
    Workplace: `部署 ${i + 1}`,
    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    Authorization: i % 2 === 0,
    UsageType: USAGE_TYPE_OPTIONS[i % USAGE_TYPE_OPTIONS.length].value,
    Inclusive: i % 4 === 0,
    AssessmentA: i % 2 === 0,
    AssessmentB: i % 3 === 0,
    BulkTransition: i % 5 === 0,
    PartnerDeadline: new Date(2025, 6, 1 + i).toISOString().split("T")[0],
    ApprovalDate: new Date(2025, 6, 10 + i).toISOString().split("T")[0],
    Description: `備考内容 ${i + 1}`,
    liked: i % 2 === 1,
    radioGroupName: `selection_${i + 1}`, // 行ごとに独立したラジオグループ
    selectedOption: null // 初期状態は未選択
  }));
}

/* ────────────── LWC クラス ────────────── */
export default class CustomTableWithTh extends LightningElement {
  /* 行データ */
  @track accounts = generateMockData(100);

  /* ---------- テンプレート描画用 ---------- */
  get processedAccounts() {
    return this.accounts.map((acc) => {
      /* バッジ色設定 */
      let badgeClass = "slds-badge";
      if (["合格", "一時承認", "条件付き合格"].includes(acc.ReviewResult)) {
        badgeClass = "slds-badge slds-badge_success";
      } else if (["否認", "一部否認"].includes(acc.ReviewResult)) {
        badgeClass = "slds-badge slds-badge_error";
      } else if (["保留", "再審査"].includes(acc.ReviewResult)) {
        badgeClass = "slds-badge slds-badge_warning";
      }

      return {
        ...acc,
        badge: { class: badgeClass, label: acc.ReviewResult }
        // icon-class は使わずアイコン形状だけ切替
      };
    });
  }

  handleLikeButtonClick(event) {
    const { id } = event.currentTarget.dataset; // 行 ID 取得
    this.accounts = this.accounts.map(
      (a) => (a.Id === id ? { ...a, liked: !a.liked } : a) // その行だけ反転
    );
  }

  /* ---------- 行一括チェック ---------- */
  get allRowsSelected() {
    return this.accounts.every((a) => a.isSelected);
  }

  handleSelectAll(e) {
    const chk = e.target.checked;
    this.accounts = this.accounts.map((a) => ({ ...a, isSelected: chk }));
  }

  handleRowSelection(e) {
    const { id } = e.currentTarget.dataset;
    const chk = e.target.checked;
    this.accounts = this.accounts.map((a) =>
      a.Id === id ? { ...a, isSelected: chk } : a
    );
  }

  /* ---------- 入力変更 ---------- */
  handleInputChange(e) {
    const { id, field } = e.currentTarget.dataset;
    const val =
      e.target.type === "checkbox" ? e.detail.checked : e.detail.value;
    this.accounts = this.accounts.map((a) =>
      a.Id === id ? { ...a, [field]: val } : a
    );
  }

  /* ---------- ラジオボタン選択 ---------- */
  handleRadioSelection(e) {
    const { id, option } = e.currentTarget.dataset;
    const selectedValue = e.detail.value;

    this.accounts = this.accounts.map((a) =>
      a.Id === id ? { ...a, selectedOption: selectedValue } : a
    );
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
  usageTypeOptions = USAGE_TYPE_OPTIONS;
  selectionOptions = SELECTION_OPTIONS;
}