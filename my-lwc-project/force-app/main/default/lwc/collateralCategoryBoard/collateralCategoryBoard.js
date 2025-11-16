import { LightningElement, api, track } from 'lwc';

// ========================================
// 定数定義: 選択肢オプション
// ========================================

/**
 * 科目の選択肢
 */
const SUBJECT_OPTIONS = [
  { label: '輸入L/C', value: '輸入L/C' },
  { label: '輸出手形', value: '輸出手形' },
  { label: '保証枠', value: '保証枠' },
  { label: '協会保証', value: '協会保証' },
  { label: '動産担保', value: '動産担保' },
  { label: 'その他', value: 'その他' }
];

/**
 * 大分類カテゴリ設定
 * 各大分類に対応する小分類の選択肢を定義
 */
const MAJOR_CATEGORY_CONFIG = {
  importCollateral: {
    label: '担保種類：商工・電保（輸入）',
    minors: [
      { label: '輸入信用状開設', value: 'import-lc' },
      { label: '輸入送金保証', value: 'import-wire' },
      { label: '船積書類精査', value: 'import-doc' }
    ]
  },
  exportCollateral: {
    label: '担保種類：輸出信用',
    minors: [
      { label: '輸出信用状確認', value: 'export-lc' },
      { label: '輸出保険付保', value: 'export-ins' },
      { label: '為替予約', value: 'export-fx' }
    ]
  },
  assetCollateral: {
    label: '担保種類：動産・不動産',
    minors: [
      { label: '本社ビル', value: 'asset-hq' },
      { label: '物流倉庫', value: 'asset-warehouse' },
      { label: '製造設備', value: 'asset-factory' }
    ]
  },
  guaranteeCollateral: {
    label: '担保種類：保証',
    minors: [
      { label: '親会社保証', value: 'guarantee-parent' },
      { label: 'オーナー保証', value: 'guarantee-owner' }
    ]
  },
  associationCollateral: {
    label: '担保種類：協会保証',
    minors: [
      { label: '普通保証', value: 'association-basic' },
      { label: '流動資産対応', value: 'association-flow' }
    ]
  }
};

/**
 * 大分類の選択肢
 * MAJOR_CATEGORY_CONFIGから生成
 */
const MAJOR_OPTIONS = Object.entries(MAJOR_CATEGORY_CONFIG).map(([value, config]) => ({
  label: config.label,
  value
}));

/**
 * 共通の選択肢を生成するヘルパー関数
 * @param {Array} items - ラベルと値のペアの配列
 * @returns {Array} オプションリスト
 */
const createOptions = items => items.map(([label, value]) => ({ label, value }));

/** 新規・既存の選択肢 */
const DEAL_TYPE_OPTIONS = createOptions([
  ['新規', 'new'],
  ['既存', 'existing']
]);

/** 設定区分の選択肢 */
const SETUP_CATEGORY_OPTIONS = createOptions([
  ['包括枠', 'package'],
  ['個別設定', 'single']
]);

/** 種類区分の選択肢 */
const COLLATERAL_CLASS_OPTIONS = createOptions([
  ['商工', 'commerce'],
  ['電保', 'electric'],
  ['その他', 'other']
]);

/** 取分の選択肢 */
const SHARE_OPTIONS = createOptions([
  ['100%', 'share100'],
  ['90%', 'share90'],
  ['80%', 'share80'],
  ['70%', 'share70']
]);

/** 消火方法の選択肢 */
const EXTINGUISH_OPTIONS = createOptions([
  ['期日一括', 'bullet'],
  ['分割返済', 'installment'],
  ['随時', 'as-needed']
]);

/** 根担保紐付けの選択肢 */
const ROOT_LINK_OPTIONS = createOptions([
  ['根担保に紐づく', 'link'],
  ['独立設定', 'independent']
]);

/** 保証種別の選択肢 */
const GUARANTEE_TYPE_OPTIONS = createOptions([
  ['親会社', 'parent'],
  ['オーナー', 'owner'],
  ['その他', 'other']
]);

/** 個人・法人の共通選択肢 */
const INDIVIDUAL_CORPORATE_OPTIONS = createOptions([
  ['個人', 'individual'],
  ['法人', 'corporate']
]);

/** 保証人区分の選択肢（個人・法人と同じ） */
const GUARANTOR_CATEGORY_OPTIONS = INDIVIDUAL_CORPORATE_OPTIONS;

/** 債務者との関係の選択肢（個人・法人と同じ） */
const DEBTOR_RELATIONSHIP_OPTIONS = INDIVIDUAL_CORPORATE_OPTIONS;

/** 規定区分の選択肢 */
const CORPORATE_GUARANTEE_CATEGORY_OPTIONS = createOptions([
  ['経営者保証', 'management-guarantee'],
  ['第三者保証', 'third-party-guarantee']
]);

/** 保証期間の選択肢 */
const GUARANTEE_PERIOD_OPTIONS = createOptions([
  ['有期', 'fixed-term'],
  ['無期', 'indefinite']
]);

/** 協会保証種別の選択肢 */
const ASSOCIATION_TYPE_OPTIONS = createOptions([
  ['普通保証', 'basic'],
  ['超短期', 'short']
]);

/** 既存保証条件の選択肢 */
const ASSOCIATION_EXISTING_CONDITION_OPTIONS = createOptions([
  ['既存保証料立替', 'existing-fee-advance'],
  ['その他', 'other']
]);

/** 承諾条件の選択肢 */
const ASSOCIATION_APPROVAL_CONDITION_OPTIONS = createOptions([
  ['承諾条件：財務維持', 'financial-maintenance'],
  ['その他', 'other']
]);

const COLUMN_TEMPLATES = {
  pattern1: [
    {
      id: 'col-import',
      subject: '01',
      majorValue: 'importCollateral',
      minorValue: 'import-lc',
      dealType: 'new',
      setupCategory: 'package',
      collateralCategory: 'commerce',
      amount: '1234567',
      share: 'share80',
      extinguish: 'bullet',
      rootLink: 'link',
      dueDate: '2025-12-31'
    },
    {
      id: 'col-export',
      subject: '02',
      majorValue: 'exportCollateral',
      minorValue: 'export-lc',
      dealType: 'existing',
      setupCategory: 'single',
      collateralCategory: 'commerce',
      amount: '2500000',
      share: 'share90',
      extinguish: 'installment',
      rootLink: 'independent',
      dueDate: '2026-03-31'
    },
    {
      id: 'col-guarantee',
      subject: '03',
      majorValue: 'guaranteeCollateral',
      minorValue: 'guarantee-parent',
      dealType: 'new',
      setupCategory: 'single',
      collateralCategory: 'commerce',
      amount: '10000000',
      share: 'share100',
      extinguish: 'as-needed',
      rootLink: 'independent',
      dueDate: '無期限',
      guaranteeType: 'parent',
      guarantorName: '○○',
      guarantorCategory: 'corporate',
      corporateGuaranteeCategory: 'management-guarantee',
      debtorRelationship: 'corporate',
      guaranteePeriod: 'fixed-term',
      guaranteePeriodYears: '3',
      guaranteePeriodMonths: '0',
      guaranteeDeadline: '2027-03-31'
    },
    {
      id: 'col-association',
      subject: '04',
      majorValue: 'associationCollateral',
      minorValue: 'association-basic',
      dealType: 'new',
      setupCategory: 'single',
      collateralCategory: 'electric',
      amount: '2000000',
      share: 'share100',
      extinguish: 'installment',
      rootLink: 'independent',
      dueDate: '2026-05-31',
      associationGuaranteeNumber: '12345',
      associationExistingCondition: 'existing-fee-advance',
      associationApprovalCondition: 'financial-maintenance',
      associationGuaranteePeriod: 'fixed-term',
      associationPeriodYears: '2',
      associationPeriodMonths: '0',
      associationDeadline: '2026-05-01'
    }
  ],
  pattern2: [
    {
      id: 'col-import',
      subject: '01',
      majorValue: 'importCollateral',
      minorValue: 'import-lc',
      dealType: 'new',
      setupCategory: 'package',
      collateralCategory: 'commerce',
      amount: '1234567',
      share: 'share80',
      extinguish: 'bullet',
      rootLink: 'link',
      dueDate: '2025-12-31'
    },
    {
      id: 'col-export',
      subject: '02',
      majorValue: 'exportCollateral',
      minorValue: 'export-lc',
      dealType: 'existing',
      setupCategory: 'single',
      collateralCategory: 'commerce',
      amount: '2500000',
      share: 'share90',
      extinguish: 'installment',
      rootLink: 'independent',
      dueDate: '2026-03-31'
    },
    {
      id: 'col-guarantee',
      subject: '03',
      majorValue: 'guaranteeCollateral',
      minorValue: 'guarantee-parent',
      dealType: 'new',
      setupCategory: 'single',
      collateralCategory: 'commerce',
      amount: '10000000',
      share: 'share100',
      extinguish: 'as-needed',
      rootLink: 'independent',
      dueDate: '無期限',
      guaranteeType: 'parent',
      guarantorName: '○○',
      guarantorCategory: 'corporate',
      corporateGuaranteeCategory: 'management-guarantee',
      debtorRelationship: 'corporate',
      guaranteePeriod: 'fixed-term',
      guaranteePeriodYears: '3',
      guaranteePeriodMonths: '0',
      guaranteeDeadline: '2027-03-31'
    },
    {
      id: 'col-association',
      subject: '04',
      majorValue: 'associationCollateral',
      minorValue: 'association-basic',
      dealType: 'new',
      setupCategory: 'single',
      collateralCategory: 'electric',
      amount: '2000000',
      share: 'share100',
      extinguish: 'installment',
      rootLink: 'independent',
      dueDate: '2026-05-31',
      associationGuaranteeNumber: '12345',
      associationExistingCondition: 'existing-fee-advance',
      associationApprovalCondition: 'financial-maintenance',
      associationGuaranteePeriod: 'fixed-term',
      associationPeriodYears: '2',
      associationPeriodMonths: '0',
      associationDeadline: '2026-05-01'
    }
  ],
  pattern3: [
    {
      id: 'col-single',
      subject: '01',
      majorValue: 'assetCollateral',
      minorValue: 'asset-hq',
      dealType: 'existing',
      setupCategory: 'package',
      collateralCategory: 'other',
      amount: '3000000',
      share: 'share70',
      extinguish: 'bullet',
      rootLink: 'link',
      dueDate: '2026-09-30'
    }
  ]
};

// ========================================
// ユーティリティ関数
// ========================================

/**
 * 大分類の値から小分類の選択肢を取得
 * @param {string} majorValue - 大分類の値
 * @returns {Array} 小分類の選択肢リスト
 */
const getMinorOptions = majorValue =>
  MAJOR_CATEGORY_CONFIG[majorValue]?.minors ?? [];

/**
 * 列データに表示用のプロパティを追加
 * @param {Object} column - 元の列データ
 * @returns {Object} デコレートされた列データ
 */
const decorateColumn = column => ({
  ...column,
  minorOptions: getMinorOptions(column.majorValue),
  isGuaranteeCategory: column.majorValue === 'guaranteeCollateral',
  isAssociationCategory: column.majorValue === 'associationCollateral',
  isCorporateGuarantor: column.guarantorCategory === 'corporate'
});

// ========================================
// コンポーネントクラス
// ========================================

/**
 * 担保カテゴリボードコンポーネント
 * 親画面タイプに応じて列データのテンプレートを切り替える
 */
export default class CollateralCategoryBoard extends LightningElement {
  _parentScreenType = 'pattern1';
  subjectOptions = SUBJECT_OPTIONS;
  majorOptions = MAJOR_OPTIONS;
  globalRemark = '○○';
  dealTypeOptions = DEAL_TYPE_OPTIONS;
  setupCategoryOptions = SETUP_CATEGORY_OPTIONS;
  collateralClassOptions = COLLATERAL_CLASS_OPTIONS;
  shareOptions = SHARE_OPTIONS;
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

  @track columns = COLUMN_TEMPLATES.pattern1.map(decorateColumn);

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
    this._parentScreenType = value || 'pattern1';
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
    return this.parentScreenType === 'pattern1';
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

    this.columns = this.columns.map(column =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            majorValue: nextValue,
            minorValue: minorOptions[0]?.value || ''
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

    this.columns = this.columns.map(column =>
      column.id === columnId
        ? {
            ...column,
            [field]: value
          }
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

    this.columns = this.columns.map(column =>
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
}
