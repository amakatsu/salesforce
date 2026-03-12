import { LightningElement, api } from "lwc";
import LightningConfirm from "lightning/confirm";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
 
// ========================================
// 定数定義: ブランク行テンプレート
// ========================================
 
/**
* 明細行の空白テンプレート
*/
const BLANK_DETAIL_ROW = {
  condition: "",
  timing: "",
  dueDate: ""
};
 
/**
* トップ入力欄の空白テンプレート（条件補足を含む）
*/
const BLANK_TOP_ROW = {
  ...BLANK_DETAIL_ROW,
  conditionSupplement: ""
};
 
// ========================================
// 定数定義: サンプルテキスト
// ========================================
 
const generateData = (pattern, length) => {
  if (!Number.isInteger(length) || length <= 0) {
    throw new Error("length は 1 以上の整数を指定してください。");
  }
 
  const FULL = "〇";
  const MARK = "●"; // 5の位置用
  const HALF = "W";
  const DIGIT = "9";
 
  // 10,20,30,... → "10","20","30"...（3桁以上は末尾2桁だけ）
  const twoDigitLabel = (n) => String(n).slice(-2);
 
  // 10文字ブロックごとに「ベース文字＋末尾2桁ラベル」を作るパターン
  //   baseChar: 〇 / W
  //   markChar: mixedChar のときだけ ●（half のときは null）
  const generateLabeledByChars = (n, baseChar, markChar) => {
    let result = "";
 
    for (let pos = 1; pos <= n; pos++) {
      const indexInBlock = ((pos - 1) % 10) + 1; // 1〜10
      const blockNumber = Math.floor((pos - 1) / 10) + 1; // 1,2,3,...
 
      let ch = baseChar;
 
      // 5文字目は ●（mixedChar のみ）
      if (markChar && indexInBlock === 5) {
        ch = markChar;
      }
 
      // 9–10文字目は "10","20","30"... の末尾2桁
      if (indexInBlock === 9 || indexInBlock === 10) {
        const label = twoDigitLabel(blockNumber * 10); // 10→"10", 100→"00"
        const digitIndex = indexInBlock - 9; // 9→0, 10→1
        ch = label[digitIndex];
      }
 
      result += ch;
    }
 
    return result;
  };
 
  // --- half / numeric ---
  if (pattern === "half") {
    // ベースW＋各10文字ブロックの末尾2桁に "10","20"... を入れる
    return generateLabeledByChars(length, HALF, null);
  }
  if (pattern === "numeric") {
    return DIGIT.repeat(length);
  }
 
  // --- mixedChar（全角・文字数指定） ---
  if (pattern === "mixedChar") {
    // ベース〇＋5文字目●＋9,10文字目に "10","20"...（末尾2桁）
    return generateLabeledByChars(length, FULL, MARK);
  }
 
  // --- mixedByte（全角=2B / 半角=1B・バイト数指定） ---
  if (pattern === "mixedByte") {
    // ブロック番号ごとのトークン（どれも「2バイトぶん」として扱う）
    const tokenForBlock = (block) => {
      if (block % 10 === 0) return twoDigitLabel(block); // 10→"10", 20→"20", 100→"00"
      if (block % 5 === 0) return MARK; // 5,15,25,...ブロック
      return FULL; // それ以外は〇
    };
 
    let result = "";
    let usedBytes = 0;
    let block = 1;
 
    // 2バイト単位でトークンを詰める
    while (length - usedBytes >= 2) {
      result += tokenForBlock(block++);
      usedBytes += 2;
    }
 
    // 端数 1 バイトがあれば W で埋める
    if (usedBytes < length) {
      result += HALF;
    }
 
    return result;
  }
 
  throw new Error(
    'pattern は "mixedByte" / "mixedChar" / "half" / "numeric" のいずれかを指定してください。'
  );
};
 
/** 28文字のサンプルテキスト */
const SAMPLE_TEXT_28 = generateData("mixedByte", 28);
 
/** 280文字のサンプルテキスト */
const SAMPLE_TEXT_280 = generateData("mixedByte", 280);
 
const SAMPLE_TEXT_140 = generateData("mixedByte", 140);
 
// ========================================
// 定数定義: サンプルデータ
// ========================================
 
/**
* トップ入力欄のサンプルデータ
*/
const SAMPLE_TOP_ROWS = [
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-03-15"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-06-30"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-04-10"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-07-15"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-09-30"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-12-15"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2026-03-31"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-10-01"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-12-31"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2026-01-31"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2025-11-30"
  },
  {
    condition: "極度内運用○○○○○○○○○○○○○",
    conditionSupplement: SAMPLE_TEXT_28,
    timing: "取引開始前/同時",
    dueDate: "2026-02-28"
  }
];
 
/**
* 明細入力欄のサンプルデータ
*/
const SAMPLE_DETAIL_ROWS = [
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-07-31"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-08-15"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-04-10"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-06-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-09-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-12-15"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-04-10"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-06-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-09-30"
  }
];
 
// ========================================
// 定数定義: 画面オプション
// ========================================
 
/**
* 画面タイプ別のオプションセット
* 各画面タイプに応じた条件とタイミングの選択肢を定義
*/
const SCREEN_OPTION_SETS = {
  default: {
    condition: [
      { label: "極度内運用○○○○○○○○○○○○○", value: "極度内運用○○○○○○○○○○○○○" },
      { label: "他与信圧縮", value: "他与信圧縮" },
      { label: "最終残高法", value: "最終残高法" },
      { label: "電債担保１年超を含む", value: "電債担保１年超を含む" },
      { label: "なし", value: "なし" }
    ],
    timing: [
      { label: "取引開始前/同時", value: "取引開始前/同時" },
      { label: "取引都度", value: "取引都度" },
      { label: "取引開始後", value: "取引開始後" }
    ]
  },
  patternInExport: {
    condition: [
      { label: "極度内運用○○○○○○○○○○○○○", value: "極度内運用○○○○○○○○○○○○○" },
      { label: "他与信圧縮", value: "他与信圧縮" },
      { label: "その他", value: "その他" }
    ],
    timing: [
      { label: "取引開始前/同時", value: "取引開始前/同時" },
      { label: "取引都度", value: "取引都度" },
      { label: "取引開始後", value: "取引開始後" }
    ]
 
  },
  patternAbcp: {
    condition: [
      { label: "極度内運用○○○○○○○○○○○○○", value: "極度内運用○○○○○○○○○○○○○" },
      { label: "他与信圧縮", value: "他与信圧縮" },
      { label: "その他", value: "その他" }
    ],
    timing: [
      { label: "取引開始前/同時", value: "取引開始前/同時" },
      { label: "取引都度", value: "取引都度" },
      { label: "取引開始後", value: "取引開始後" }
    ]
  }
};
 
// ========================================
// 定数定義: 画面動作設定
// ========================================
 
/** サポートされている親画面タイプ */
const SUPPORTED_PARENT_SCREENS = [
  "default",
  "patternInExport",
  "patternAbcp"
];
 
/** デフォルトのセクション表示設定 */
const DEFAULT_SECTIONS = {
  topInput: true,
  detailInput: true,
  remarks: true,
  inquiry: true
};
 
/**
* 画面タイプ別の動作設定
* デフォルト値からの差分のみを定義
*/
const SCREEN_BEHAVIOR_BY_PARENT = {
  default: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 6
  },
  patternInExport: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 12
  },
  patternAbcp: {
    sections: {
      ...DEFAULT_SECTIONS,
      topInput: false,
      inquiry: false
    },
    topInputLimit: 0
  }
};
 
/** 明細行の最大追加可能件数 */
const MAX_DETAIL_ROWS = 9;
 
// ========================================
// ユーティリティ関数
// ========================================
 
/**
* 行データにIDと空白テンプレートを適用してビルドする
* @param {Array} rows - 元の行データ
* @param {string} prefix - ID のプレフィックス
* @param {Object} blankRow - 空白行のテンプレート
* @returns {Array} IDを付与された行データ
*/
const buildRows = (rows, prefix, blankRow) =>
  rows.map((row, index) => ({
    id: `${prefix}-${index + 1}`,
    ...blankRow,
    ...row
  }));
 
// ========================================
// コンポーネントクラス
// ========================================
 
/**
* 本件条件コンポーネント
* 親画面タイプに応じて条件入力欄の表示内容を切り替える
*/
export default class f003RgV9951HonkenJokenBasicC1 extends LightningElement {
  topRows = buildRows(SAMPLE_TOP_ROWS, "top", BLANK_TOP_ROW);
  conditionRows = buildRows(SAMPLE_DETAIL_ROWS, "detail", BLANK_DETAIL_ROW);
 
  @api parentScreenType;
  nextDetailId = this.conditionRows.length + 1;
  relatedInquiryNumber = SAMPLE_TEXT_28;
  remarks = SAMPLE_TEXT_280;
  activeTopSections = ["section1"];
  activeDetailSections = ["section2"];
 
  // ========================================
  // イベントハンドラー
  // ========================================
 
  /**
   * 行変更ハンドラー（トップ入力欄用）
   * @param {Event} event - 変更イベント
   */
  handleTopRowChange(event) {
    this.topRows = this.updateRows(this.topRows, event);
  }
 
  /**
   * 行変更ハンドラー（明細入力欄用）
   * @param {Event} event - 変更イベント
   */
  handleRowChange(event) {
    this.conditionRows = this.updateRows(this.conditionRows, event);
  }
 
  /**
   * 明細行追加ハンドラー
   * 最大件数に達している場合は警告を表示
   */
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
 
  /**
   * 明細行削除ハンドラー
   * 削除前に確認ダイアログを表示
   * @param {Event} event - クリックイベント
   */
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
 
  /**
   * 関連照会番号変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleRelatedInquiryNumberChange(event) {
    this.relatedInquiryNumber = event.target.value;
  }
 
  /**
   * 備考変更ハンドラー
   * @param {Event} event - 変更イベント
   */
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
 
  /**
   * トップアコーディオン開閉ハンドラー
   * @param {Event} event - トグルイベント
   */
  handleTopAccordionToggle(event) {
    this.activeTopSections = event.detail.openSections;
  }
 
  /**
   * 明細アコーディオン開閉ハンドラー
   * @param {Event} event - トグルイベント
   */
  handleDetailAccordionToggle(event) {
    this.activeDetailSections = event.detail.openSections;
  }
 
  // ========================================
  // ヘルパーメソッド
  // ========================================
 
  /**
   * 行データを更新する
   * @param {Array} rows - 更新対象の行データ
   * @param {Event} event - 変更イベント
   * @returns {Array} 更新された行データ
   */
  updateRows(rows, event) {
    const { id, field } = event.target.dataset;
    const { value } = event.target;
    return rows.map((row) =>
      row.id === id ? { ...row, [field]: value } : row
    );
  }
 
  // ========================================
  // ゲッタープロパティ
  // ========================================
 
  /**
   * 現在の画面タイプに応じた動作設定を取得
   * @returns {Object} 画面動作設定オブジェクト
   */
  get screenBehavior() {
    return (
      SCREEN_BEHAVIOR_BY_PARENT[this.parentScreenType] ||
      SCREEN_BEHAVIOR_BY_PARENT.default
    );
  }
 
  /**
   * 条件の選択肢を取得
   * @returns {Array} 条件オプションリスト
   */
  get conditionOptions() {
    return (
      SCREEN_OPTION_SETS[this.parentScreenType] || SCREEN_OPTION_SETS.default
    ).condition;
  }
 
  /**
   * タイミングの選択肢を取得
   * @returns {Array} タイミングオプションリスト
   */
  get timingOptions() {
    return (
      SCREEN_OPTION_SETS[this.parentScreenType] || SCREEN_OPTION_SETS.default
    ).timing;
  }
 
  /**
   * トップ入力欄セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showTopInputSection() {
    return this.screenBehavior.sections.topInput;
  }
 
  /**
   * 明細入力欄セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showDetailInputSection() {
    return this.screenBehavior.sections.detailInput;
  }
 
  /**
   * 備考セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showRemarksSection() {
    return this.screenBehavior.sections.remarks;
  }
 
  /**
   * 関連照会セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showInquirySection() {
    return this.screenBehavior.sections.inquiry;
  }
 
  /**
   * トップ入力欄の上限件数を取得
   * @returns {number} 上限件数
   */
  get topInputLimit() {
    return this.screenBehavior.topInputLimit;
  }
 
  /**
   * 表示用のトップ行データ（上限件数まで）を取得
   * @returns {Array} 表示用行データ
   */
  get topRowsForDisplay() {
    return this.topRows.slice(0, this.topInputLimit);
  }
 
  /**
   * トップ行が上限件数を超過しているかチェック
   * @returns {boolean} 超過している場合true
   */
  get isTopRowLimitExceeded() {
    return this.topRows.length > this.topInputLimit;
  }
 
  /**
   * コンポーネント全体の表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get isVisible() {
    return (
      !this.parentScreenType ||
      SUPPORTED_PARENT_SCREENS.includes(this.parentScreenType)
    );
  }
}