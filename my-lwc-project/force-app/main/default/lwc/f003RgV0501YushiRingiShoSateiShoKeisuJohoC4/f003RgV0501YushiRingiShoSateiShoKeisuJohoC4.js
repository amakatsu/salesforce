import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

// =========================
// C4: 与信（Credit）テーブル
// =========================

const CREDIT_COLUMNS = [
  { label: "与信種類(科目)", fieldName: "creditType1", type: "text" },
  { label: "ワーニング情報", fieldName: "creditType2", type: "text" },
  { label: "グロス／ネット", fieldName: "grossNet", type: "text" },
  { label: "期 日", fieldName: "dueDate", type: "text" },
  { label: "マージン", fieldName: "margin", type: "text" },
  { label: "99月末残高", fieldName: "endOfMonthBalance", type: "text" },
  { label: "99月末極度", fieldName: "endOfMonthLimit", type: "text" },
  { label: "当月増減", fieldName: "currentMonthChange", type: "text" },
  {
    label: "本件後与信額",
    fieldName: "postTransactionCreditAmount",
    type: "text"
  },
  {
    label: "実勢現在残高 Ｃ／Ｅ＋Ｐ／Ｅ",
    fieldName: "marketValueBalanceCEPE",
    type: "text"
  },
  {
    label: "実勢現在残高 Ｃ／Ｅ＋Ｐ／Ｅ（参考値）",
    fieldName: "marketValueBalanceCEPEReference",
    type: "text"
  },
  {
    label: "実勢現在残高 Ｃ／Ｅ",
    fieldName: "marketValueBalanceCE",
    type: "text"
  },
  {
    label: "実勢現在残高 Ｃ／Ｅ（参考値）",
    fieldName: "marketValueBalanceCEReference",
    type: "text"
  },
  {
    label: "想定元本承認額",
    fieldName: "assumedPrincipalApprovalAmount",
    type: "text"
  },
  {
    label: "想定元本実勢現在残",
    fieldName: "assumedPrincipalMarketValueBalance",
    type: "text"
  }
];

const MAX_NUM_7 = makeTestData("numeric", 7); // 9,999,999
const MAX_NUM_5 = makeTestData("numeric", 5); // 99,999

const CREDIT_DEFAULTS = {
  creditType2: "",
  grossNet: "",
  dueDate: "99/99",
  margin: MAX_NUM_7,
  endOfMonthBalance: MAX_NUM_5,
  endOfMonthLimit: MAX_NUM_5,
  currentMonthChange: MAX_NUM_5,
  postTransactionCreditAmount: MAX_NUM_5,
  marketValueBalanceCEPE: MAX_NUM_5,
  marketValueBalanceCEPEReference: `-${MAX_NUM_5}`,
  marketValueBalanceCE: MAX_NUM_5,
  marketValueBalanceCEReference: `-${MAX_NUM_5}`,
  assumedPrincipalApprovalAmount: MAX_NUM_7,
  assumedPrincipalMarketValueBalance: MAX_NUM_7,
  disabled: false
};

const DASH_FIELDS = {
  margin: "-",
  endOfMonthBalance: "-",
  endOfMonthLimit: "-",
  currentMonthChange: "-",
  postTransactionCreditAmount: "-",
  marketValueBalanceCEPE: "-",
  marketValueBalanceCEPEReference: "-",
  marketValueBalanceCE: "-",
  marketValueBalanceCEReference: "-"
};

const EMPTY_FIELDS = {
  endOfMonthBalance: "",
  endOfMonthLimit: "",
  currentMonthChange: "",
  postTransactionCreditAmount: "",
  marketValueBalanceCEPE: "",
  marketValueBalanceCEPEReference: "",
  marketValueBalanceCE: "",
  marketValueBalanceCEReference: ""
};

const CREDIT_ITEMS = [
  {
    id: "1",
    creditType1: "限度算入与信合計",
    indent: 0,
    overrides: {
      dueDate: "",
      margin: "",
      endOfMonthBalance: MAX_NUM_5,
      endOfMonthLimit: MAX_NUM_5,
      currentMonthChange: "-",
      postTransactionCreditAmount: MAX_NUM_5,
      marketValueBalanceCEPE: MAX_NUM_5,
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: MAX_NUM_5,
      marketValueBalanceCEReference: "-"
    },
    disabled: true
  },
  {
    id: "2",
    creditType1: makeTestData("mixedChar", 40),
    indent: 1,
    overrides: {
      creditType2: "ワーニング",
      grossNet: "グロス"
    }
  },
  {
    id: "3",
    creditType1: makeTestData("mixedChar", 40),
    indent: 1,
    overrides: {
      creditType2: "ワーニン",
      grossNet: "ネット",
      currentMonthChange: "-99999"
    }
  },
  {
    id: "4",
    creditType1: makeTestData("mixedChar", 40),
    indent: 1,
    overrides: {
      creditType2: "ワーニン",
      grossNet: "グロス"
    }
  },
  {
    id: "5",
    creditType1: "限度不算入与信為替取引",
    indent: 1,
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "6",
    creditType1: "スワップ／オプション取引",
    indent: 1,
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "7",
    creditType1: "その他",
    indent: 1,
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "8",
    creditType1: "限度不算入与信合計",
    indent: 0,
    overrides: {
      dueDate: "",
      margin: "-",
      ...EMPTY_FIELDS
    },
    disabled: true
  },
  {
    id: "9",
    creditType1: "市場性与信合計",
    indent: 0,
    overrides: {
      dueDate: "",
      margin: "",
      endOfMonthBalance: MAX_NUM_5,
      endOfMonthLimit: MAX_NUM_5,
      currentMonthChange: "-",
      postTransactionCreditAmount: MAX_NUM_5,
      marketValueBalanceCEPE: MAX_NUM_5,
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: MAX_NUM_5,
      marketValueBalanceCEReference: "-"
    },
    disabled: false
  }
];

const creditRow = ({ id, creditType1, indent = 0, overrides = {}, disabled }) => ({
  id,
  creditType1,
  creditType1Class: `indent-${indent}`,
  ...CREDIT_DEFAULTS,
  ...overrides,
  ...(disabled !== undefined ? { disabled } : {})
});

function generateCreditData() {
  return CREDIT_ITEMS.map((item) => creditRow(item));
}

// =========================
// C5: 為替予約・担保・参考
// =========================

const EXCHANGE_RESERVATION_COLUMNS = [
  { label: "(注)除く限度不算入取引", fieldName: "type" },
  { label: "前々期平均", fieldName: "previousTermAverage" },
  { label: "前期平均", fieldName: "lastTermAverage" },
  { label: "99月", fieldName: "september99" },
  { label: "99月", fieldName: "dueDate1" },
  { label: "99月", fieldName: "dueDate2" },
  { label: "99月", fieldName: "dueDate3" },
  { label: "99月", fieldName: "dueDate4" },
  { label: "99月", fieldName: "dueDate5" }
];

const REGULAR_COLLATERAL_COLUMNS = [
  { label: "担保種類", fieldName: "collateralType" },
  { label: "規定値", fieldName: "expectedShare" },
  { label: "時価ベース", fieldName: "marketValue" }
];

const NON_REGULAR_COLLATERAL_COLUMNS = [
  { label: "担保種類", fieldName: "collateralType" },
  { label: "見込取分", fieldName: "expectedShare" },
  { label: "時価ベース", fieldName: "marketValue" }
];

const REFERENCE_COLUMNS = [
  { label: "市場性与信種類", fieldName: "category" },
  { label: "Ｃ／Ｅ＋Ｐ／Ｅ", fieldName: "cePe" },
  { label: "Ｃ／Ｅ", fieldName: "ce" }
];

const CHANGED_CELL_CLASS = "changed-cell";

const EXCHANGE_DEFAULTS = {
  previousTermAverage: "9999999",
  lastTermAverage: "9999999",
  september99: "9999999",
  dueDate1: "9999999",
  dueDate2: "9999999",
  dueDate3: "9999999",
  dueDate4: "9999999",
  dueDate5: "9999999"
};

const COLLATERAL_DEFAULTS = {
  expectedShare: "99.99",
  marketValue: "99.99"
};

const REFERENCE_DEFAULTS = {
  cePe: makeTestData("numeric", 5),
  ce: makeTestData("numeric", 5),
  disabled: false
};

const exchangeRow = ({ id, type, overrides = {} }) => ({
  id,
  type,
  ...EXCHANGE_DEFAULTS,
  ...overrides
});

const collateralRow = ({
  id,
  collateralType,
  overrides = {},
  disabled = false
}) => ({
  id,
  collateralType,
  ...COLLATERAL_DEFAULTS,
  ...overrides,
  ...(disabled ? { disabled: true } : {})
});

const referenceRow = ({ id, category, overrides = {}, disabled = false }) => ({
  id,
  category,
  ...REFERENCE_DEFAULTS,
  ...overrides,
  ...(disabled ? { disabled: true } : {})
});

const EXCHANGE_RESERVATION_ITEMS = [
  { id: "1", type: "予約平残" },
  { id: "2", type: "予約ピーク" },
  { id: "3", type: "当月締結累計額" },
  {
    id: "4",
    type: "平均回転期間",
    overrides: {
      previousTermAverage: "99.99",
      lastTermAverage: "99.99",
      september99: "99.99",
      dueDate1: "99.99",
      dueDate2: "99.99",
      dueDate3: "99.99",
      dueDate4: "99.99",
      dueDate5: "99.99"
    }
  }
];

const REGULAR_COLLATERAL_ITEMS = [
  { id: "11", collateralType: "預金" },
  { id: "12", collateralType: "電債担保" },
  { id: "13", collateralType: "有証" },
  { id: "14", collateralType: "保証" },
  { id: "15", collateralType: "不動産" },
  { id: "16", collateralType: "その他" },
  { id: "17", collateralType: "規定担保計", disabled: true },
  { id: "18", collateralType: "裸与信", disabled: true }
];

const NON_REGULAR_COLLATERAL_ITEMS = [
  { id: "111", collateralType: "電債担保" },
  { id: "115", collateralType: "不動産" },
  { id: "116", collateralType: "入居保証金" },
  { id: "117", collateralType: "債権" },
  { id: "118", collateralType: "その他" },
  { id: "119", collateralType: "規定外担保計", disabled: true }
];

const REFERENCE_ITEMS = [
  { id: "1111", category: "為替取引", disabled: true },
  { id: "1112", category: "スワップオプション取引", disabled: true },
  { id: "1113", category: "マークトリスク内在型取引", disabled: true },
  { id: "1114", category: "先物取引" },
  { id: "1115", category: "その他市場性与信" },
  { id: "1116", category: "全体", disabled: true }
];

function generateExchangeReservationData() {
  return EXCHANGE_RESERVATION_ITEMS.map((item) => exchangeRow(item));
}

function generateRegularCollateralData() {
  return REGULAR_COLLATERAL_ITEMS.map((item) => collateralRow(item));
}

function generateNonRegularCollateralData() {
  return NON_REGULAR_COLLATERAL_ITEMS.map((item) => collateralRow(item));
}

function generateReferenceData() {
  return REFERENCE_ITEMS.map((item) => referenceRow(item));
}

// =========================
// 差分ハイライト
// =========================

const EXCHANGE_DIFF_FIELDS = [
  "previousTermAverage",
  "lastTermAverage",
  "september99",
  "dueDate1",
  "dueDate2",
  "dueDate3",
  "dueDate4",
  "dueDate5"
];
const CREDIT_DIFF_FIELDS = [
  "creditType2",
  "grossNet",
  "dueDate",
  "margin",
  "endOfMonthBalance",
  "endOfMonthLimit",
  "currentMonthChange",
  "postTransactionCreditAmount",
  "marketValueBalanceCEPE",
  "marketValueBalanceCEPEReference",
  "marketValueBalanceCE",
  "marketValueBalanceCEReference",
  "assumedPrincipalApprovalAmount",
  "assumedPrincipalMarketValueBalance"
];
const COLLATERAL_DIFF_FIELDS = ["expectedShare", "marketValue"];
const REFERENCE_DIFF_FIELDS = ["cePe", "ce"];

function deepClone(data) {
  return JSON.parse(JSON.stringify(data));
}

function initializeClassFields(data, fields) {
  return data.map((item) => {
    const classFields = {};
    for (const field of fields) {
      classFields[`${field}Class`] = "";
    }
    return { ...item, ...classFields };
  });
}

function highlightChangedCells(currentData, originalData, fields) {
  return currentData.map((record) => {
    const original =
      originalData.find((r) => r.id === record.id) || {};
    const classUpdates = {};
    for (const field of fields) {
      classUpdates[`${field}Class`] =
        original[field] !== record[field] ? `${CHANGED_CELL_CLASS} cell-changed-saved` : "";
    }
    return { ...record, ...classUpdates };
  });
}

// =========================
// 統合コンポーネント
// =========================

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC45 extends LightningElement {
  activeSections = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r"
  ];

  amountUnit = "〇〇〇";
  groupNumber = makeTestData("numeric", 1);

  // C4
  creditColumns = CREDIT_COLUMNS;
  creditData = generateCreditData();
  initialCreditData = [];
  originalCreditData = [];

  // C5
  exchangeReservationColumns = EXCHANGE_RESERVATION_COLUMNS;
  regularCollateralColumns = REGULAR_COLLATERAL_COLUMNS;
  nonRegularCollateralColumns = NON_REGULAR_COLLATERAL_COLUMNS;
  referenceColumns = REFERENCE_COLUMNS;

  initialExchangeReservationData = generateExchangeReservationData();
  initialRegularCollateralData = generateRegularCollateralData();
  initialNonRegularCollateralData = generateNonRegularCollateralData();
  initialReferenceData = generateReferenceData();

  originalExchangeReservationData = [];
  originalRegularCollateralData = [];
  originalNonRegularCollateralData = [];
  originalReferenceData = [];

  exchangeReservationData = [];
  regularCollateralData = [];
  nonRegularCollateralData = [];
  referenceData = [];

  connectedCallback() {
    this.resetData();
  }

  resetData() {
    this.originalExchangeReservationData = deepClone(
      this.initialExchangeReservationData
    );
    this.originalRegularCollateralData = deepClone(
      this.initialRegularCollateralData
    );
    this.originalNonRegularCollateralData = deepClone(
      this.initialNonRegularCollateralData
    );
    this.originalReferenceData = deepClone(this.initialReferenceData);

    this.exchangeReservationData = initializeClassFields(
      this.initialExchangeReservationData,
      EXCHANGE_DIFF_FIELDS
    );
    this.regularCollateralData = initializeClassFields(
      this.initialRegularCollateralData,
      COLLATERAL_DIFF_FIELDS
    );
    this.nonRegularCollateralData = initializeClassFields(
      this.initialNonRegularCollateralData,
      COLLATERAL_DIFF_FIELDS
    );
    this.referenceData = initializeClassFields(
      this.initialReferenceData,
      REFERENCE_DIFF_FIELDS
    );

    this.initialCreditData = generateCreditData();
    this.originalCreditData = deepClone(this.initialCreditData);
    this.creditData = initializeClassFields(
      this.initialCreditData,
      CREDIT_DIFF_FIELDS
    );
  }

  handleInputChange(event) {
    const { id, field } =
      event.currentTarget?.dataset || event.target?.dataset || {};
    const value = event.target.value;

    if (!id || !field) return;

    this.creditData = this.updateDataImmutable(
      this.creditData,
      id,
      field,
      value
    );
    this.creditData = highlightChangedCells(
      this.creditData,
      this.originalCreditData,
      CREDIT_DIFF_FIELDS
    );
    this.exchangeReservationData = this.updateDataImmutable(
      this.exchangeReservationData,
      id,
      field,
      value
    );
    this.regularCollateralData = this.updateDataImmutable(
      this.regularCollateralData,
      id,
      field,
      value
    );
    this.nonRegularCollateralData = this.updateDataImmutable(
      this.nonRegularCollateralData,
      id,
      field,
      value
    );
    this.referenceData = this.updateDataImmutable(
      this.referenceData,
      id,
      field,
      value
    );
  }

  updateDataImmutable(data, id, field, value) {
    return data.map((row) =>
      row.id === id ? { ...row, [field]: value } : row
    );
  }

  @api
  applySavedHighlight() {
    this.handleSave();
  }

  handleSave() {
    this.creditData = highlightChangedCells(
      this.creditData,
      this.originalCreditData,
      CREDIT_DIFF_FIELDS
    );
    this.originalCreditData = deepClone(this.creditData);

    this.exchangeReservationData = highlightChangedCells(
      this.exchangeReservationData,
      this.originalExchangeReservationData,
      EXCHANGE_DIFF_FIELDS
    );
    this.regularCollateralData = highlightChangedCells(
      this.regularCollateralData,
      this.originalRegularCollateralData,
      COLLATERAL_DIFF_FIELDS
    );
    this.nonRegularCollateralData = highlightChangedCells(
      this.nonRegularCollateralData,
      this.originalNonRegularCollateralData,
      COLLATERAL_DIFF_FIELDS
    );
    this.referenceData = highlightChangedCells(
      this.referenceData,
      this.originalReferenceData,
      REFERENCE_DIFF_FIELDS
    );

    this.originalExchangeReservationData = deepClone(
      this.exchangeReservationData
    );
    this.originalRegularCollateralData = deepClone(
      this.regularCollateralData
    );
    this.originalNonRegularCollateralData = deepClone(
      this.nonRegularCollateralData
    );
    this.originalReferenceData = deepClone(this.referenceData);
  }

  handleReset() {
    this.resetData();
  }
}
