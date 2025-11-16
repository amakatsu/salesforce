const SUBJECT_OPTIONS = [
  { label: '輸入L/C', value: '輸入L/C' },
  { label: '輸出手形', value: '輸出手形' },
  { label: '保証枠', value: '保証枠' },
  { label: '協会保証', value: '協会保証' },
  { label: '動産担保', value: '動産担保' },
  { label: 'その他', value: 'その他' }
];

import { LightningElement, api, track } from 'lwc';

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

const MAJOR_OPTIONS = Object.entries(MAJOR_CATEGORY_CONFIG).map(([value, config]) => ({
  label: config.label,
  value
}));

const DEAL_TYPE_OPTIONS = [
  { label: '新規', value: 'new' },
  { label: '既存', value: 'existing' }
];
const SETUP_CATEGORY_OPTIONS = [
  { label: '包括枠', value: 'package' },
  { label: '個別設定', value: 'single' }
];
const COLLATERAL_CLASS_OPTIONS = [
  { label: '商工', value: 'commerce' },
  { label: '電保', value: 'electric' },
  { label: 'その他', value: 'other' }
];
const SHARE_OPTIONS = [
  { label: '100%', value: 'share100' },
  { label: '90%', value: 'share90' },
  { label: '80%', value: 'share80' },
  { label: '70%', value: 'share70' }
];
const EXTINGUISH_OPTIONS = [
  { label: '期日一括', value: 'bullet' },
  { label: '分割返済', value: 'installment' },
  { label: '随時', value: 'as-needed' }
];
const ROOT_LINK_OPTIONS = [
  { label: '根担保に紐づく', value: 'link' },
  { label: '独立設定', value: 'independent' }
];
const GUARANTEE_TYPE_OPTIONS = [
  { label: '親会社', value: 'parent' },
  { label: 'オーナー', value: 'owner' },
  { label: 'その他', value: 'other' }
];
const GUARANTOR_CATEGORY_OPTIONS = [
  { label: '個人', value: 'individual' },
  { label: '法人', value: 'corporate' }
];
const DEBTOR_RELATIONSHIP_OPTIONS = [
  { label: '個人', value: 'individual' },
  { label: '法人', value: 'corporate' }
];
const CORPORATE_GUARANTEE_CATEGORY_OPTIONS = [
  { label: '経営者保証', value: 'management-guarantee' },
  { label: '第三者保証', value: 'third-party-guarantee' }
];
const GUARANTEE_PERIOD_OPTIONS = [
  { label: '有期', value: 'fixed-term' },
  { label: '無期', value: 'indefinite' }
];
const ASSOCIATION_TYPE_OPTIONS = [
  { label: '普通保証', value: 'basic' },
  { label: '超短期', value: 'short' }
];
const ASSOCIATION_EXISTING_CONDITION_OPTIONS = [
  { label: '既存保証料立替', value: 'existing-fee-advance' },
  { label: 'その他', value: 'other' }
];
const ASSOCIATION_APPROVAL_CONDITION_OPTIONS = [
  { label: '承諾条件：財務維持', value: 'financial-maintenance' },
  { label: 'その他', value: 'other' }
];

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

const getMinorOptions = majorValue =>
  MAJOR_CATEGORY_CONFIG[majorValue]?.minors ?? [];

const decorateColumn = column => ({
  ...column,
  minorOptions: getMinorOptions(column.majorValue),
  isGuaranteeCategory: column.majorValue === 'guaranteeCollateral',
  isAssociationCategory: column.majorValue === 'associationCollateral',
  isCorporateGuarantor: column.guarantorCategory === 'corporate'
});

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

  @api
  get parentScreenType() {
    return this._parentScreenType;
  }

  set parentScreenType(value) {
    this._parentScreenType = value || 'pattern1';
    this.applyPattern(this._parentScreenType);
  }

  get showSubjectColumn() {
    return this.parentScreenType === 'pattern1';
  }

  applyPattern(screenType) {
    const templates = COLUMN_TEMPLATES[screenType] || COLUMN_TEMPLATES.pattern1;
    this.columns = templates.map(decorateColumn);
  }

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

  handleRemarkChange(event) {
    this.globalRemark = event.detail.value;
  }
}
