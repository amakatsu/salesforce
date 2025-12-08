import { LightningElement, api, track } from "lwc";
import LightningConfirm from "lightning/confirm";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

// ========================================
// 定数定義: ブランク行テンプレート
// ========================================

/**
 * 担保条件２の空白テンプレート
 */
const BLANK_COLLATERAL_DETAIL_ROW = {
  condition: "",
  timing: "",
  dueDate: ""
};

// ========================================
// 定数定義: サンプルテキスト
// ========================================

/**
 * conditionDetails で利用しているパターン付きサンプル文字列生成ロジックを転用
 * @param {string} pattern - mixedByte / mixedChar / half / numeric
 * @param {number} length - 生成する文字（またはバイト）長
 * @returns {string} パターン化されたサンプル文字列
 */
const generateData = (pattern, length) => {
  if (!Number.isInteger(length) || length <= 0) {
    throw new Error("length は 1 以上の整数を指定してください。");
  }

  const FULL = "〇";
  const MARK = "●";
  const HALF = "W";
  const DIGIT = "9";

  const twoDigitLabel = (n) => String(n).slice(-2);

  const generateLabeledByChars = (n, baseChar, markChar) => {
    let result = "";

    for (let pos = 1; pos <= n; pos++) {
      const indexInBlock = ((pos - 1) % 10) + 1;
      const blockNumber = Math.floor((pos - 1) / 10) + 1;

      let ch = baseChar;

      if (markChar && indexInBlock === 5) {
        ch = markChar;
      }

      if (indexInBlock === 9 || indexInBlock === 10) {
        const label = twoDigitLabel(blockNumber * 10);
        const digitIndex = indexInBlock - 9;
        ch = label[digitIndex];
      }

      result += ch;
    }

    return result;
  };

  if (pattern === "half") {
    return generateLabeledByChars(length, HALF, null);
  }
  if (pattern === "numeric") {
    return DIGIT.repeat(length);
  }
  if (pattern === "mixedChar") {
    return generateLabeledByChars(length, FULL, MARK);
  }
  if (pattern === "mixedByte") {
    const tokenForBlock = (block) => {
      if (block % 10 === 0) return twoDigitLabel(block);
      if (block % 5 === 0) return MARK;
      return FULL;
    };

    let result = "";
    let usedBytes = 0;
    let block = 1;

    while (length - usedBytes >= 2) {
      result += tokenForBlock(block++);
      usedBytes += 2;
    }

    if (usedBytes < length) {
      result += HALF;
    }

    return result;
  }

  throw new Error(
    'pattern は "mixedByte" / "mixedChar" / "half" / "numeric" のいずれかを指定してください。'
  );
};

/** 28文字相当のサンプルテキスト */
const SAMPLE_TEXT_28 = generateData("mixedByte", 28);

/** 280文字相当のサンプルテキスト */
const SAMPLE_TEXT_280 = generateData("mixedByte", 280);

/** 400バイト相当のサンプルテキスト */
const SAMPLE_TEXT_400 = generateData("mixedByte", 400);

// ========================================
// 定数定義: 選択肢オプション（統合版）
// ========================================

/**
 * 共通の選択肢を生成するヘルパー関数
 * @param {Array} items - ラベルと値のペアの配列
 * @returns {Array} オプションリスト
 */
const createOptions = (items) =>
  items.map(([label, value]) => ({ label, value }));

/**
 * すべての選択肢を一元管理するオブジェクト
 */
const OPTIONS = {
  // 科目の選択肢
  subject: [
    { label: "01", value: "01" },
    { label: "02", value: "02" },
    { label: "03", value: "03" },
    { label: "04", value: "04" },
    { label: "動産担保", value: "動産担保" },
    { label: "その他", value: "その他" }
  ],

  // 新規・既存の選択肢
  dealType: createOptions([
    ["新規・協会優先", "new"],
    ["新規・協会優先", "existing"]
  ]),

  // 設定区分の選択肢
  setupCategory: createOptions([
    ["緊急措置", "package"],
    ["緊急措置", "single"]
  ]),

  // 担保種類区分の選択肢（パターン別）
  collateralClass: {
    normal: createOptions([
      ["特定債務保証", "parent"],
      ["オーナー", "owner"],
      ["その他", "other"]
    ]),
    association: createOptions([
      ["貸付個別保証", "loan-individual-guarantee"],
      ["貸付根保証", "loan-root-guarantee"],
      ["手割個別保証", "bill-discount-individual"],
      ["手割根保証", "bill-discount-root"],
      ["その他", "other"]
    ])
  },

  // 取分の選択肢
  share: createOptions([
    ["100%", "100"],
    ["90%", "90"],
    ["80%", "80"],
    ["70%", "70"]
  ]),

  // 消火方法の選択肢
  extinguish: createOptions([
    ["その他", "bullet"],
    ["その他", "installment"],
    ["その他", "as-needed"]
  ]),

  // 根担保紐付けの選択肢
  rootLink: createOptions([
    ["極度", "link"],
    ["極度", "independent"]
  ]),

  // 保証種別の選択肢（パターン別）
  guaranteeType: {
    normal: createOptions([
      ["包括根", "comprehensive-root"],
      ["包括根（極度付）", "comprehensive-root-limit"],
      ["包括根（期限付き）", "comprehensive-root-term"],
      ["極度期限付", "limit-term"],
      ["特定債務", "specific-debt"],
      ["得手根", "tokune"]
    ]),
    tkk: createOptions([
      ["貸付個別", "loan-individual"],
      ["貸付根", "loan-root"],
      ["手割", "bill-discount"],
      ["その他", "other"]
    ]),
    dhc: createOptions([
      ["極度期限付", "limit-term"],
      ["貸付個別", "loan-individual"],
      ["その他", "other"]
    ])
  },

  // 個人・法人の選択肢
  individualCorporate: createOptions([
    ["個人", "individual"],
    ["法人（上場）", "corporate"]
  ]),

  // 規定区分の選択肢
  corporateGuaranteeCategory: createOptions([
    ["規定外・優良", "management-guarantee"],
    ["第三者保証", "third-party-guarantee"]
  ]),

  // 保証期間の選択肢
  guaranteePeriod: createOptions([
    ["期間", "period"],
    ["日付", "date"]
  ]),

  // 協会保証種別の選択肢
  associationType: createOptions([
    ["普通保証", "basic"],
    ["超短期", "short"]
  ]),

  // 既存保証条件の選択肢
  associationExistingCondition: createOptions([
    ["無", "existing-fee-advance"],
    ["その他", "other"]
  ]),

  // 承諾条件の選択肢
  associationApprovalCondition: createOptions([
    ["優先充当", "financial-maintenance"],
    ["その他", "other"]
  ]),

  // 履行タイミングの選択肢
  timing: createOptions([
    ["取引開始前/同時", "取引開始前/同時"],
    ["四半期末", "四半期末"],
    ["半期末", "半期末"],
    ["契約更新時", "契約更新時"],
    ["その他", "その他"]
  ])
};

// 後方互換性のための旧定数名
const SUBJECT_OPTIONS = OPTIONS.subject;

/**
 * 大分類カテゴリ設定
 * 各大分類に対応する小分類の選択肢を定義
 */
const MAJOR_CATEGORY_CONFIG = {
  importCollateral: {
    label: "預金",
    minors: [
      { label: "なし", value: "import-lc" },
      { label: "なし", value: "import-wire" },
      { label: "なし", value: "import-doc" }
    ]
  },
  exportCollateral: {
    label: "有価証券・債権",
    minors: [
      { label: "なし", value: "export-lc" },
      { label: "なし", value: "export-ins" },
      { label: "なし", value: "export-fx" }
    ]
  },
  assetCollateral: {
    label: "動産・不動産",
    minors: [
      { label: "なし", value: "asset-hq" },
      { label: "なし", value: "asset-warehouse" },
      { label: "なし", value: "asset-factory" }
    ]
  },
  guaranteeCollateral: {
    label: "保証",
    minors: [
      { label: "通常保証", value: "guarantee-normal" },
      { label: "TKK", value: "guarantee-tkk" },
      { label: "全石協", value: "guarantee-zenseki" },
      { label: "DHC", value: "guarantee-dhc" }
    ]
  },
  associationCollateral: {
    label: "協会保証",
    minors: [
      { label: "なし", value: "association-basic" },
      { label: "なし", value: "association-flow" }
    ]
  }
};

/**
 * 大分類の選択肢
 * MAJOR_CATEGORY_CONFIGから生成
 */
const MAJOR_OPTIONS = Object.entries(MAJOR_CATEGORY_CONFIG).map(
  ([value, config]) => ({
    label: config.label,
    value
  })
);

// 後方互換性のための旧定数名（継続使用）
const DEAL_TYPE_OPTIONS = OPTIONS.dealType;
const SETUP_CATEGORY_OPTIONS = OPTIONS.setupCategory;
const COLLATERAL_CLASS_OPTIONS = OPTIONS.collateralClass.normal;
const EXTINGUISH_OPTIONS = OPTIONS.extinguish;
const ROOT_LINK_OPTIONS = OPTIONS.rootLink;
const GUARANTEE_TYPE_OPTIONS = OPTIONS.guaranteeType.normal;
const GUARANTOR_CATEGORY_OPTIONS = OPTIONS.individualCorporate;
const DEBTOR_RELATIONSHIP_OPTIONS = OPTIONS.individualCorporate;
const CORPORATE_GUARANTEE_CATEGORY_OPTIONS = OPTIONS.corporateGuaranteeCategory;
const GUARANTEE_PERIOD_OPTIONS = OPTIONS.guaranteePeriod;
const ASSOCIATION_TYPE_OPTIONS = OPTIONS.associationType;
const ASSOCIATION_EXISTING_CONDITION_OPTIONS = OPTIONS.associationExistingCondition;
const ASSOCIATION_APPROVAL_CONDITION_OPTIONS = OPTIONS.associationApprovalCondition;
const TIMING_OPTIONS = OPTIONS.timing;

// ========================================
// 定数定義: 動的選択肢の連動ルール
// ========================================

/**
 * 動的選択肢の連動ルール設定
 * 小分類や大分類に応じて選択肢を切り替えるロジックを定義
 */
const DYNAMIC_OPTIONS_CONFIG = {
  // 担保種類区分の連動ルール
  collateralClass: {
    // 常に適用
    shouldApply: () => true,
    // 大分類の値に応じたパターンのマッピング
    getPattern: (column) => {
      return column.majorValue === "associationCollateral" ? "association" : "normal";
    }
  },

  // 保証種別の連動ルール
  guaranteeType: {
    // 保証の場合のみ連動
    shouldApply: (column) => column.majorValue === "guaranteeCollateral",
    // 小分類の値に応じたパターンのマッピング
    getPattern: (column) => {
      const minorValue = column.minorValue;
      if (minorValue === "guarantee-tkk" || minorValue === "guarantee-zenseki") {
        return "tkk";
      } else if (minorValue === "guarantee-dhc") {
        return "dhc";
      }
      return "normal";
    }
  }
};

// ========================================
// 定数定義: サンプルデータ
// ========================================

/**
 * 担保条件２のサンプルデータ
 */
const SAMPLE_COLLATERAL_DETAIL_ROWS = [
  {
    condition: SAMPLE_TEXT_400,
    timing: "取引開始前/同時",
    dueDate: "2025-06-30"
  },
  {
    condition: SAMPLE_TEXT_400,
    timing: "四半期末",
    dueDate: "2025-09-30"
  },
  {
    condition: SAMPLE_TEXT_400,
    timing: "契約更新時",
    dueDate: "2026-03-31"
  },
  {
    condition: SAMPLE_TEXT_400,
    timing: "半期末",
    dueDate: "2025-12-31"
  },
  {
    condition: SAMPLE_TEXT_400,
    timing: "その他",
    dueDate: "2026-02-28"
  }
];

/** 担保条件２の最大追加可能件数 */
const MAX_COLLATERAL_DETAIL_ROWS = 9;

const COLUMN_TEMPLATES = {
  pattern1: [
    {
      id: "col-import",
      subject: "01",
      majorValue: "importCollateral",
      minorValue: "import-lc",
      dealType: "new",
      setupCategory: "package",
      collateralCategory: "commerce",
      amount: "1234567",
      share: "80",
      extinguish: "bullet",
      rootLink: "link",
      timing: "取引開始前/同時",
      dueDate: "2025-12-31",
      remark: SAMPLE_TEXT_28
    },
    {
      id: "col-export",
      subject: "02",
      majorValue: "exportCollateral",
      minorValue: "export-lc",
      dealType: "existing",
      setupCategory: "single",
      collateralCategory: "commerce",
      amount: "2500000",
      share: "90",
      extinguish: "installment",
      rootLink: "independent",
      timing: "四半期末",
      dueDate: "2026-03-31",
      remark: SAMPLE_TEXT_28
    },
    {
      id: "col-guarantee",
      subject: "03",
      majorValue: "guaranteeCollateral",
      minorValue: "guarantee-parent",
      dealType: "new",
      setupCategory: "single",
      collateralCategory: "commerce",
      amount: "10000000",
      share: "100",
      extinguish: "as-needed",
      rootLink: "independent",
      timing: "契約更新時",
      dueDate: "2027-03-31",
      remark: SAMPLE_TEXT_28,
      guaranteeType: "parent",
      guarantorName: SAMPLE_TEXT_28,
      guarantorCategory: "corporate",
      corporateGuaranteeCategory: "management-guarantee",
      debtorRelationship: "corporate",
      guaranteePeriod: "period",
      guaranteePeriodYears: "3",
      guaranteePeriodMonths: "0",
      guaranteeDeadline: "2027-03-31"
    },
    {
      id: "col-association",
      subject: "04",
      majorValue: "associationCollateral",
      minorValue: "association-basic",
      dealType: "new",
      setupCategory: "single",
      collateralCategory: "electric",
      amount: "2000000",
      share: "100",
      extinguish: "installment",
      rootLink: "independent",
      timing: "半期末",
      dueDate: "2026-05-31",
      remark: SAMPLE_TEXT_28,
      associationType: "basic",
      associationGuaranteeNumber: "12345",
      associationExistingCondition: "existing-fee-advance",
      associationApprovalCondition: "financial-maintenance",
      associationGuaranteePeriod: "period",
      associationPeriodYears: "2",
      associationPeriodMonths: "0",
      associationDeadline: "2026-05-01"
    }
  ],
  pattern2: [
    {
      id: "col-import",
      subject: "01",
      majorValue: "importCollateral",
      minorValue: "import-lc",
      dealType: "new",
      setupCategory: "package",
      collateralCategory: "commerce",
      amount: "1234567",
      share: "80",
      extinguish: "bullet",
      rootLink: "link",
      timing: "取引開始前/同時",
      dueDate: "2025-12-31",
      remark: SAMPLE_TEXT_28
    },
    {
      id: "col-export",
      subject: "02",
      majorValue: "exportCollateral",
      minorValue: "export-lc",
      dealType: "existing",
      setupCategory: "single",
      collateralCategory: "commerce",
      amount: "2500000",
      share: "90",
      extinguish: "installment",
      rootLink: "independent",
      timing: "四半期末",
      dueDate: "2026-03-31",
      remark: SAMPLE_TEXT_28
    },
    {
      id: "col-guarantee",
      subject: "03",
      majorValue: "guaranteeCollateral",
      minorValue: "guarantee-parent",
      dealType: "new",
      setupCategory: "single",
      collateralCategory: "commerce",
      amount: "10000000",
      share: "100",
      extinguish: "as-needed",
      rootLink: "independent",
      timing: "契約更新時",
      dueDate: "2027-03-31",
      remark: SAMPLE_TEXT_28,
      guaranteeType: "parent",
      guarantorName: SAMPLE_TEXT_28,
      guarantorCategory: "corporate",
      corporateGuaranteeCategory: "management-guarantee",
      debtorRelationship: "corporate",
      guaranteePeriod: "period",
      guaranteePeriodYears: "3",
      guaranteePeriodMonths: "0",
      guaranteeDeadline: "2027-03-31"
    },
    {
      id: "col-association",
      subject: "04",
      majorValue: "associationCollateral",
      minorValue: "association-basic",
      dealType: "new",
      setupCategory: "single",
      collateralCategory: "electric",
      amount: "2000000",
      share: "100",
      extinguish: "installment",
      rootLink: "independent",
      timing: "半期末",
      dueDate: "2026-05-31",
      remark: SAMPLE_TEXT_28,
      associationType: "basic",
      associationGuaranteeNumber: "12345",
      associationExistingCondition: "existing-fee-advance",
      associationApprovalCondition: "financial-maintenance",
      associationGuaranteePeriod: "period",
      associationPeriodYears: "2",
      associationPeriodMonths: "0",
      associationDeadline: "2026-05-01"
    }
  ],
  pattern3: [
    {
      id: "col-single",
      subject: "01",
      majorValue: "assetCollateral",
      minorValue: "asset-hq",
      dealType: "existing",
      setupCategory: "package",
      collateralCategory: "other",
      amount: "3000000",
      share: "70",
      extinguish: "bullet",
      rootLink: "link",
      timing: "その他",
      dueDate: "2026-09-30",
      remark: SAMPLE_TEXT_28
    }
  ]
};

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

/**
 * 大分類の値から小分類の選択肢を取得
 * @param {string} majorValue - 大分類の値
 * @returns {Array} 小分類の選択肢リスト
 */
const getMinorOptions = (majorValue) =>
  MAJOR_CATEGORY_CONFIG[majorValue]?.minors ?? [];

/**
 * 小分類に応じた担保種類区分の選択肢を取得
 * @param {string} majorValue - 大分類の値
 * @param {string} minorValue - 小分類の値
 * @returns {Array} 担保種類区分の選択肢リスト
 */
const getCollateralClassOptions = (majorValue, minorValue) => {
  const config = DYNAMIC_OPTIONS_CONFIG.collateralClass;
  const column = { majorValue, minorValue };

  if (config.shouldApply(column)) {
    const pattern = config.getPattern(column);
    return OPTIONS.collateralClass[pattern];
  }
  return OPTIONS.collateralClass.normal;
};

/**
 * 小分類に応じた保証種別の選択肢を取得
 * @param {string} majorValue - 大分類の値
 * @param {string} minorValue - 小分類の値
 * @returns {Array} 保証種別の選択肢リスト
 */
const getGuaranteeTypeOptions = (majorValue, minorValue) => {
  const config = DYNAMIC_OPTIONS_CONFIG.guaranteeType;
  const column = { majorValue, minorValue };

  if (config.shouldApply(column)) {
    const pattern = config.getPattern(column);
    return OPTIONS.guaranteeType[pattern];
  }
  return OPTIONS.guaranteeType.normal;
};

/**
 * 列データに表示用のプロパティを追加
 * @param {Object} column - 元の列データ
 * @returns {Object} デコレートされた列データ
 */
const decorateColumn = (column) => {
  const isGuarantee = column.majorValue === "guaranteeCollateral";
  const isAssociation = column.majorValue === "associationCollateral";
  const isGuaranteeOrAssociation = isGuarantee || isAssociation;

  return {
    ...column,
    minorOptions: getMinorOptions(column.majorValue),
    collateralClassOptions: getCollateralClassOptions(column.majorValue, column.minorValue),
    guaranteeTypeOptions: getGuaranteeTypeOptions(column.majorValue, column.minorValue),
    isGuaranteeCategory: isGuarantee,
    isAssociationCategory: isAssociation,
    isGuaranteeOrAssociation,
    isCorporateGuarantor: column.guarantorCategory === "corporate",
    // 保証種別の統一プロパティ
    guaranteeTypeValue: isAssociation ? column.associationType : column.guaranteeType,
    guaranteeTypeOptionsForDisplay: isAssociation ? OPTIONS.associationType : getGuaranteeTypeOptions(column.majorValue, column.minorValue),
    guaranteeTypeField: isAssociation ? "associationType" : "guaranteeType",
    guaranteeTypeHelp: isAssociation ? "協会保証の種類を選択してください。普通保証または超短期から選択できます。" : undefined,
    // 保証期間の入力制御
    isPeriodInputDisabled: column.guaranteePeriod === "date",
    isDateInputDisabled: column.guaranteePeriod === "period",
    // 協会保証期間の入力制御
    isAssociationPeriodInputDisabled: column.associationGuaranteePeriod === "date",
    isAssociationDateInputDisabled: column.associationGuaranteePeriod === "period"
  };
};

// ========================================
// コンポーネントクラス
// ========================================

/**
 * 担保カテゴリボードコンポーネント
 * 親画面タイプに応じて列データのテンプレートを切り替える
 */
export default class f003RgV9961TanpoBasicC1 extends LightningElement {
  _parentScreenType = "pattern1";
  subjectOptions = SUBJECT_OPTIONS;
  majorOptions = MAJOR_OPTIONS;
  globalRemark = SAMPLE_TEXT_280;
  dealTypeOptions = DEAL_TYPE_OPTIONS;
  setupCategoryOptions = SETUP_CATEGORY_OPTIONS;
  collateralClassOptions = COLLATERAL_CLASS_OPTIONS;
  extinguishOptions = EXTINGUISH_OPTIONS;
  rootLinkOptions = ROOT_LINK_OPTIONS;
  guaranteeTypeOptions = GUARANTEE_TYPE_OPTIONS;
  guarantorCategoryOptions = GUARANTOR_CATEGORY_OPTIONS;
  debtorRelationshipOptions = DEBTOR_RELATIONSHIP_OPTIONS;
  corporateGuaranteeCategoryOptions = CORPORATE_GUARANTEE_CATEGORY_OPTIONS;
  guaranteePeriodOptions = GUARANTEE_PERIOD_OPTIONS;
  associationTypeOptions = ASSOCIATION_TYPE_OPTIONS;
  associationExistingConditionOptions = ASSOCIATION_EXISTING_CONDITION_OPTIONS;
  associationApprovalConditionOptions = ASSOCIATION_APPROVAL_CONDITION_OPTIONS;
  timingOptions = TIMING_OPTIONS;

  @track columns = COLUMN_TEMPLATES.pattern1.map(decorateColumn);
  @track collateralDetailRows = buildRows(
    SAMPLE_COLLATERAL_DETAIL_ROWS,
    "collateral-detail",
    BLANK_COLLATERAL_DETAIL_ROW
  );
  nextCollateralDetailId = this.collateralDetailRows.length + 1;

  // ========================================
  // 公開プロパティ
  // ========================================

  /**
   * 親画面タイプを取得
   * @returns {string} 親画面タイプ
   */
  @api
  get parentScreenType() {
    return this._parentScreenType;
  }

  /**
   * 親画面タイプを設定し、対応するパターンを適用
   * @param {string} value - 親画面タイプ
   */
  set parentScreenType(value) {
    this._parentScreenType = value || "pattern1";
    this.applyPattern(this._parentScreenType);
  }

  // ========================================
  // ゲッタープロパティ
  // ========================================

  /**
   * 科目列の表示フラグ
   * @returns {boolean} pattern1の場合のみtrue
   */
  get showSubjectColumn() {
    return this.parentScreenType === "pattern1";
  }

  // ========================================
  // メソッド
  // ========================================

  /**
   * パターンに応じた列データテンプレートを適用
   * @param {string} screenType - 画面タイプ
   */
  applyPattern(screenType) {
    const templates = COLUMN_TEMPLATES[screenType] || COLUMN_TEMPLATES.pattern1;
    this.columns = templates.map(decorateColumn);
  }

  /**
   * 大分類変更ハンドラー
   * 大分類が変更されたら小分類を最初の選択肢に設定
   * @param {Event} event - 変更イベント
   */
  handleMajorChange(event) {
    const { columnId } = event.target.dataset;
    const nextValue = event.detail.value;
    const minorOptions = getMinorOptions(nextValue);

    this.columns = this.columns.map((column) =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            majorValue: nextValue,
            minorValue: minorOptions[0]?.value || ""
          })
        : column
    );
  }

  /**
   * フィールド変更ハンドラー
   * 各フィールドの値を更新
   * @param {Event} event - 変更イベント
   */
  handleFieldChange(event) {
    const { columnId, field } = event.target.dataset;
    const value = event.detail.value;

    this.columns = this.columns.map((column) =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            [field]: value
          })
        : column
    );
  }

  /**
   * 数値入力ハンドラー
   * c-f003-gs-v0000-number からの変更を受けて列を更新
   * @param {CustomEvent} event - 数値変更イベント
   */
  handleNumberChange(event) {
    const { id, field, value } = event.detail;

    this.columns = this.columns.map((column) =>
      column.id === id
        ? decorateColumn({
            ...column,
            [field]: value
          })
        : column
    );
  }

  /**
   * 保証人区分変更ハンドラー
   * 保証人区分が変更されたら列データを再デコレート
   * @param {Event} event - 変更イベント
   */
  handleGuarantorCategoryChange(event) {
    const { columnId, field } = event.target.dataset;
    const value = event.detail.value;

    this.columns = this.columns.map((column) =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            [field]: value
          })
        : column
    );
  }

  /**
   * 備考変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleRemarkChange(event) {
    this.globalRemark = event.detail.value;
  }

  /**
   * 担保条件２の行変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleCollateralDetailRowChange(event) {
    const { id, field } = event.target.dataset;
    let value = event.target.value;

    if (typeof value === "undefined") {
      value = event.detail?.value;
    }

    this.collateralDetailRows = this.collateralDetailRows.map((row) =>
      row.id === id ? { ...row, [field]: value } : row
    );
  }

  /**
   * 担保条件２の行追加ハンドラー
   * 最大件数に達している場合は警告を表示
   */
  handleAddCollateralDetailRow() {
    if (this.collateralDetailRows.length >= MAX_COLLATERAL_DETAIL_ROWS) {
      this.dispatchEvent(
        new ShowToastEvent({
          title: "上限に達しました",
          message: `担保条件２は最大${MAX_COLLATERAL_DETAIL_ROWS}件まで追加できます`,
          variant: "warning"
        })
      );
      return;
    }

    const newRow = {
      id: `collateral-detail-${this.nextCollateralDetailId++}`,
      ...BLANK_COLLATERAL_DETAIL_ROW
    };
    this.collateralDetailRows = [...this.collateralDetailRows, newRow];
  }

  /**
   * 担保条件２の行削除ハンドラー
   * 削除前に確認ダイアログを表示
   * @param {Event} event - クリックイベント
   */
  async handleRemoveCollateralDetailRow(event) {
    const rowId = event.target.dataset.id;
    const confirmed = await LightningConfirm.open({
      label: "削除の確認",
      message: "選択した行を削除しますか？",
      theme: "warning"
    });

    if (!confirmed) {
      return;
    }

    this.collateralDetailRows = this.collateralDetailRows.filter(
      (row) => row.id !== rowId
    );
  }
}
