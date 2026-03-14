import { LightningElement, api } from "lwc";
import LightningConfirm from "lightning/confirm";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { generateData } from "c/f003RgV0000CommonJs";

// ========================================
// 定義: テンプレート・定数・設定値
// ========================================

const SAMPLE_TEXT_28 = generateData("mixedByte", 28);
const SAMPLE_TEXT_140 = generateData("mixedByte", 140);
const SAMPLE_TEXT_400 = generateData("mixedByte", 400);

const BLANK_DETAIL_ROW = {
  condition: "",
  timing: "",
  dueDate: ""
};

const BLANK_TOP_ROW = {
  ...BLANK_DETAIL_ROW,
  conditionSupplement: ""
};

/** 明細行の最大追加可能件数 */
const MAX_DETAIL_ROWS = 9;

/** デフォルトの画面タイプ */
const DEFAULT_SCREEN_TYPE = "patternYushi";

/** 全パターン共通の履行タイミング選択肢 */
const TIMING_OPTIONS = [
  { label: "取引開始前/同時", value: "取引開始前/同時" },
  { label: "取引都度", value: "取引都度" },
  { label: "取引開始後", value: "取引開始後" }
];

/** 輸出入・ABCP共通の本件条件選択肢 */
const CONDITION_OPTIONS_COMMON = [
  { label: "極度内運用○○○○○○○○○○○○○", value: "極度内運用○○○○○○○○○○○○○" },
  { label: "他与信圧縮", value: "他与信圧縮" },
  { label: "その他", value: "その他" }
];

/** 画面タイプ別の本件条件選択肢 */
const CONDITION_OPTIONS_BY_PARENT = {
  patternYushi: [
    { label: "極度内運用○○○○○○○○○○○○○", value: "極度内運用○○○○○○○○○○○○○" },
    { label: "他与信圧縮", value: "他与信圧縮" },
    { label: "最終残高法", value: "最終残高法" },
    { label: "電債担保１年超を含む", value: "電債担保１年超を含む" },
    { label: "なし", value: "なし" }
  ],
  patternYushutsuYunyu: CONDITION_OPTIONS_COMMON,
  patternAbcp: CONDITION_OPTIONS_COMMON
};

/** デフォルトのセクション表示設定 */
const DEFAULT_SECTIONS = {
  topInput: true,
  detailInput: true,
  remarks: true,
  inquiry: true
};

/** 画面タイプ別の動作設定 */
const SCREEN_BEHAVIOR_BY_PARENT = {
  patternYushi: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 6,
    remarksSize: "5"
  },
  patternYushutsuYunyu: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 12,
    remarksSize: "5"
  },
  patternAbcp: {
    sections: {
      ...DEFAULT_SECTIONS,
      topInput: false,
      detailInput: false,
      inquiry: false
    },
    topInputLimit: 0,
    remarksSize: "10"
  }
};


const SAMPLE_TOP_ROWS = [
  "2025-03-15", "2025-06-30", "2025-04-10", "2025-07-15",
  "2025-09-30", "2025-12-15", "2026-03-31", "2025-10-01",
  "2025-12-31", "2026-01-31", "2025-11-30", "2026-02-28"
].map((dueDate) => ({
  condition: "極度内運用○○○○○○○○○○○○○",
  conditionSupplement: SAMPLE_TEXT_28,
  timing: "取引開始前/同時",
  dueDate
}));

const SAMPLE_DETAIL_ROWS = [
  "2025-07-31", "2025-08-15", "2025-04-10", "2025-06-30",
  "2025-09-30", "2025-12-15", "2025-04-10", "2025-06-30",
  "2025-09-30"
].map((dueDate) => ({
  condition: SAMPLE_TEXT_140,
  timing: "取引開始前/同時",
  dueDate
}));

// ========================================
// コンポーネントクラス
// ========================================

const buildRows = (rows, prefix, blankRow) =>
  rows.map((row, index) => ({
    id: `${prefix}-${index + 1}`,
    ...blankRow,
    ...row
  }));

export default class f003RgV9951HonkenJokenBasicC1 extends LightningElement {
  topRows = buildRows(SAMPLE_TOP_ROWS, "top", BLANK_TOP_ROW);
  conditionRows = buildRows(SAMPLE_DETAIL_ROWS, "detail", BLANK_DETAIL_ROW);

  @api parentScreenType;
  nextDetailId = this.conditionRows.length + 1;
  relatedInquiryNumber = SAMPLE_TEXT_28;
  remarks = SAMPLE_TEXT_400;
  activeTopSections = ["section1"];

  // --- イベントハンドラー ---

  handleTopRowChange(event) {
    this.topRows = this.updateRows(this.topRows, event);
  }

  handleRowChange(event) {
    this.conditionRows = this.updateRows(this.conditionRows, event);
  }

  handleAddRow() {
    if (this.conditionRows.length >= MAX_DETAIL_ROWS) {
      this.dispatchEvent(
        new ShowToastEvent({
          title: "上限に達しました",
          message: `明細は最大${MAX_DETAIL_ROWS}件まで追加できます`,
          variant: "warning"
        })
      );
      return;
    }

    const newRow = {
      id: `detail-${this.nextDetailId++}`,
      ...BLANK_DETAIL_ROW
    };
    this.conditionRows = [...this.conditionRows, newRow];
  }

  async handleRemoveRow(event) {
    const rowId = event.target.dataset.id;
    const confirmed = await LightningConfirm.open({
      label: "削除の確認",
      message: "選択した行を削除しますか？",
      theme: "warning"
    });

    if (!confirmed) {
      return;
    }

    this.conditionRows = this.conditionRows.filter((row) => row.id !== rowId);
  }

  handleRelatedInquiryNumberChange(event) {
    this.relatedInquiryNumber = event.target.value;
  }

  handleRemarksChange(event) {
    this.remarks = event.target.value;
  }

  /**
   * 関連照会ボタンクリックハンドラー
   * TODO: 実装接続時に差し替え予定のスタブ
   */
  handleRelatedInquiry() {
    // eslint-disable-next-line no-console
    console.log("関連厘差照会番号", this.relatedInquiryNumber);
  }

  handleTopAccordionToggle(event) {
    this.activeTopSections = event.detail.openSections;
  }

  // --- ヘルパーメソッド ---

  updateRows(rows, event) {
    const { id, field } = event.target.dataset;
    const { value } = event.target;
    return rows.map((row) =>
      row.id === id ? { ...row, [field]: value } : row
    );
  }

  // --- ゲッタープロパティ ---

  get screenBehavior() {
    return (
      SCREEN_BEHAVIOR_BY_PARENT[this.parentScreenType] ||
      SCREEN_BEHAVIOR_BY_PARENT[DEFAULT_SCREEN_TYPE]
    );
  }

  get conditionOptions() {
    return (
      CONDITION_OPTIONS_BY_PARENT[this.parentScreenType] ||
      CONDITION_OPTIONS_BY_PARENT[DEFAULT_SCREEN_TYPE]
    );
  }

  get timingOptions() {
    return TIMING_OPTIONS;
  }

  get showTopInputSection() {
    return this.screenBehavior.sections.topInput;
  }

  get showDetailInputSection() {
    return this.screenBehavior.sections.detailInput;
  }

  get showRemarksSection() {
    return this.screenBehavior.sections.remarks;
  }

  get showInquirySection() {
    return this.screenBehavior.sections.inquiry;
  }

  get remarksSize() {
    return this.screenBehavior.remarksSize;
  }

  get topInputLimit() {
    return this.screenBehavior.topInputLimit;
  }

  get topRowsForDisplay() {
    return this.topRows.slice(0, this.topInputLimit);
  }

  get isVisible() {
    return (
      !this.parentScreenType ||
      this.parentScreenType in SCREEN_BEHAVIOR_BY_PARENT
    );
  }
}
