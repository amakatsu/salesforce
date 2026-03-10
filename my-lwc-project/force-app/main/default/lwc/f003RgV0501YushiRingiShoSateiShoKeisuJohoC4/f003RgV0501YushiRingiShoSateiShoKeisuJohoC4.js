import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

const MAX_AMOUNT_7 = makeTestData("numeric", 7);
const MAX_AMOUNT_5 = makeTestData("numeric", 5);
const SAVED_HIGHLIGHT_CLASSES = "changed-cell cell-changed-saved";
const deepClone = (obj) => JSON.parse(JSON.stringify(obj));

const addEmptyHighlightClasses = (data, fields) =>
  data.map((item) => ({
    ...item,
    ...Object.fromEntries(fields.map((f) => [`${f}Class`, ""]))
  }));

const applyHighlight = (current, original, fields) =>
  current.map((row) => {
    const origRow = original.find((item) => item.id === row.id) || {};
    return {
      ...row,
      ...Object.fromEntries(
        fields.map((f) => [
          `${f}Class`,
          origRow[f] !== row[f] ? SAVED_HIGHLIGHT_CLASSES : ""
        ])
      )
    };
  });

/* Credit: header columns for template */
const CREDIT_HEADER_COLUMNS = [
  { key: "creditType1", label: "与信種類(科目)", w: "col-w95" },
  { key: "creditType2", label: "ワーニング情報", w: "col-w45" },
  { key: "grossNet", label: "グロス／ネット", w: "col-w35" },
  { key: "dueDate", label: "期日(年/月)", w: "col-w60" },
  { key: "margin", label: "マージン", w: "col-w37" },
  { key: "endOfMonthBalance", label: "99月末残高", w: "col-w37" },
  { key: "endOfMonthLimit", label: "99月末極度", w: "col-w40" },
  { key: "currentMonthChange", label: "当月増減", w: "col-w37" },
  { key: "postTransactionCreditAmount", label: "本件後与信額", w: "col-w37" },
  { key: "marketValueBalanceCEPE", label: "実勢現在残 C／E+P／E", w: "col-w40" },
  { key: "marketValueBalanceCEPEReference", label: "C／E+P／E(参考値)", w: "col-w40" },
  { key: "marketValueBalanceCE", label: "実勢現在残 C／E", w: "col-w40" },
  { key: "marketValueBalanceCEReference", label: "C／E(参考値)", w: "col-w40" },
  { key: "assumedPrincipalApprovalAmount", label: "想定元本承認額", w: "col-w40" },
  { key: "assumedPrincipalMarketValueBalance", label: "想定元本実勢現在残", w: "col-w40" }
];

/* Credit: field definitions for tbody iteration */
const CREDIT_TEXT_FIELDS = ["creditType2", "grossNet"];
const CREDIT_DUE_DATE_FIELDS = ["dueDateYear", "dueDateMonth"];
const CREDIT_NUM_FIELDS = [
  ...["endOfMonthBalance", "endOfMonthLimit", "currentMonthChange",
    "postTransactionCreditAmount", "marketValueBalanceCEPE", "marketValueBalanceCEPEReference",
    "marketValueBalanceCE", "marketValueBalanceCEReference",
    "assumedPrincipalApprovalAmount", "assumedPrincipalMarketValueBalance"
  ].map((f) => ({ field: f, disableable: true }))
];
const CREDIT_HIGHLIGHT_FIELDS = [
  ...CREDIT_TEXT_FIELDS,
  ...CREDIT_DUE_DATE_FIELDS,
  "margin",
  ...CREDIT_NUM_FIELDS.map((col) => col.field)
];

/* Credit: defaults and shared overrides */
const CREDIT_DEFAULTS = {
  creditType2: "", grossNet: "", dueDateYear: "9999", dueDateMonth: "99", margin: MAX_AMOUNT_7,
  endOfMonthBalance: MAX_AMOUNT_5, endOfMonthLimit: MAX_AMOUNT_5,
  currentMonthChange: MAX_AMOUNT_5,
  postTransactionCreditAmount: MAX_AMOUNT_5, marketValueBalanceCEPE: MAX_AMOUNT_5,
  marketValueBalanceCEPEReference: `-${MAX_AMOUNT_5}`, marketValueBalanceCE: MAX_AMOUNT_5,
  marketValueBalanceCEReference: `-${MAX_AMOUNT_5}`,
  assumedPrincipalApprovalAmount: MAX_AMOUNT_7,
  assumedPrincipalMarketValueBalance: MAX_AMOUNT_7,
  disabled: false
};
const DASH_OVERRIDES = Object.fromEntries(
  ["endOfMonthBalance", "endOfMonthLimit", "currentMonthChange",
    "postTransactionCreditAmount", "marketValueBalanceCEPE", "marketValueBalanceCEPEReference",
    "marketValueBalanceCE", "marketValueBalanceCEReference"].map((f) => [f, "-"])
);
const EMPTY_OVERRIDES = Object.fromEntries(
  ["endOfMonthBalance", "endOfMonthLimit", "currentMonthChange", "postTransactionCreditAmount",
    "marketValueBalanceCEPE", "marketValueBalanceCEPEReference",
    "marketValueBalanceCE", "marketValueBalanceCEReference"].map((f) => [f, ""])
);
const SUMMARY_OVERRIDES = {
  dueDateYear: "", dueDateMonth: "", margin: "",
  endOfMonthBalance: MAX_AMOUNT_5, endOfMonthLimit: MAX_AMOUNT_5, currentMonthChange: "-",
  postTransactionCreditAmount: MAX_AMOUNT_5, marketValueBalanceCEPE: MAX_AMOUNT_5,
  marketValueBalanceCEPEReference: "-", marketValueBalanceCE: MAX_AMOUNT_5,
  marketValueBalanceCEReference: "-"
};

const creditRow = ({ id, creditType1, indent = 0, overrides = {}, disabled }) => ({
  id, creditType1, creditType1Class: `indent-${indent}`,
  ...CREDIT_DEFAULTS, ...overrides, ...(disabled !== undefined ? { disabled } : {})
});

const CREDIT_ITEMS = [
  { id: "1", creditType1: "限度算入与信合計", overrides: SUMMARY_OVERRIDES, disabled: true },
  { id: "2", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニング", grossNet: "グロス" } },
  { id: "3", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニン", grossNet: "ネット", currentMonthChange: "-99999" } },
  { id: "4", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニン", grossNet: "グロス" } },
  { id: "5", creditType1: "限度不算入与信為替取引", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "6", creditType1: "スワップ／オプション取引", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "7", creditType1: "その他", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "8", creditType1: "限度不算入与信合計", overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...EMPTY_OVERRIDES }, disabled: true },
  { id: "9", creditType1: "市場性与信合計", overrides: SUMMARY_OVERRIDES, disabled: false }
];

/* Exchange reservation */
const EXCHANGE_RESERVATION_COLUMNS = [
  { label: "(注)除く限度不算入取引", fieldName: "type" },
  { label: "前々期平均", fieldName: "previousTermAverage" },
  { label: "前期平均", fieldName: "lastTermAverage" },
  { label: "99月", fieldName: "september99" },
  { label: "99月", fieldName: "dueDate1" }, { label: "99月", fieldName: "dueDate2" },
  { label: "99月", fieldName: "dueDate3" }, { label: "99月", fieldName: "dueDate4" },
  { label: "99月", fieldName: "dueDate5" }
];
const EXCHANGE_HIGHLIGHT_FIELDS = [
  "previousTermAverage", "lastTermAverage", "september99",
  "dueDate1", "dueDate2", "dueDate3", "dueDate4", "dueDate5"
];
const EXCHANGE_DEFAULTS = Object.fromEntries(
  EXCHANGE_HIGHLIGHT_FIELDS.map((f) => [f, "9999999"])
);
const exchangeRow = ({ id, type, overrides = {} }) => ({
  id, type, ...EXCHANGE_DEFAULTS, ...overrides
});
const EXCHANGE_ITEMS = [
  { id: "1", type: "予約平残" }, { id: "2", type: "予約ピーク" },
  { id: "3", type: "当月締結累計額" },
  { id: "4", type: "平均回転期間", overrides: Object.fromEntries(EXCHANGE_HIGHLIGHT_FIELDS.map((f) => [f, "99.99"])) }
];

/* Collateral */
const COLLATERAL_DEFAULTS = { expectedShare: "99.99", marketValue: "99.99" };
const COLLATERAL_HIGHLIGHT_FIELDS = ["expectedShare", "marketValue"];
const collateralRow = ({ id, collateralType, overrides = {}, disabled = false }) => ({
  id, collateralType, ...COLLATERAL_DEFAULTS, ...overrides,
  ...(disabled ? { disabled: true } : {})
});
const REGULAR_COLLATERAL_ITEMS = [
  { id: "11", collateralType: "預金" }, { id: "12", collateralType: "電債担保" },
  { id: "13", collateralType: "有証" }, { id: "14", collateralType: "保証" },
  { id: "15", collateralType: "不動産" }, { id: "16", collateralType: "その他" },
  { id: "17", collateralType: "規定担保計", disabled: true },
  { id: "18", collateralType: "裸与信", disabled: true }
];
const NON_REGULAR_COLLATERAL_ITEMS = [
  { id: "111", collateralType: "電債担保" }, { id: "115", collateralType: "不動産" },
  { id: "116", collateralType: "入居保証金" }, { id: "117", collateralType: "債権" },
  { id: "118", collateralType: "その他" },
  { id: "119", collateralType: "規定外担保計", disabled: true }
];

/* Reference */
const REFERENCE_DEFAULTS = { cePe: MAX_AMOUNT_5, ce: MAX_AMOUNT_5, disabled: false };
const REFERENCE_HIGHLIGHT_FIELDS = ["cePe", "ce"];
const referenceRow = ({ id, category, overrides = {}, disabled = false }) => ({
  id, category, ...REFERENCE_DEFAULTS, ...overrides,
  ...(disabled ? { disabled: true } : {})
});
const REFERENCE_ITEMS = [
  { id: "1111", category: "為替取引", disabled: true },
  { id: "1112", category: "スワップオプション取引", disabled: true },
  { id: "1113", category: "マークトリスク内在型取引", disabled: true },
  { id: "1114", category: "先物取引" }, { id: "1115", category: "その他市場性与信" },
  { id: "1116", category: "全体", disabled: true }
];

/* Component */
export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC45 extends LightningElement {
  activeSections = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r"];
  amountUnit = "〇〇〇";
  groupNumber = makeTestData("numeric", 1);

  creditHeaderColumns = CREDIT_HEADER_COLUMNS;
  exchangeReservationColumns = EXCHANGE_RESERVATION_COLUMNS;

  initialCreditData = CREDIT_ITEMS.map((item) => creditRow(item));
  initialExchangeReservationData = EXCHANGE_ITEMS.map((item) => exchangeRow(item));
  initialRegularCollateralData = REGULAR_COLLATERAL_ITEMS.map((item) => collateralRow(item));
  initialNonRegularCollateralData = NON_REGULAR_COLLATERAL_ITEMS.map((item) => collateralRow(item));
  initialReferenceData = REFERENCE_ITEMS.map((item) => referenceRow(item));

  originalCreditData = [];
  originalExchangeReservationData = [];
  originalRegularCollateralData = [];
  originalNonRegularCollateralData = [];
  originalReferenceData = [];

  creditData = [];
  exchangeReservationData = [];
  regularCollateralData = [];
  nonRegularCollateralData = [];
  referenceData = [];

  connectedCallback() { this.resetData(); }

  get creditRows() {
    return this.creditData.map((row) => {
      const yearClass = row.dueDateYearClass || "";
      const monthClass = row.dueDateMonthClass || "";
      const dueDateCellClass = yearClass || monthClass ? SAVED_HIGHLIGHT_CLASSES : "";
      const dueDateValue = row.dueDateYear || row.dueDateMonth
        ? `${row.dueDateYear}/${row.dueDateMonth}`
        : "";
      return {
        ...row,
        textCells: [
          ...CREDIT_TEXT_FIELDS.map((f) => ({
            key: `${row.id}-${f}`, field: f, value: row[f],
            cellClass: row[`${f}Class`] || ""
          })),
          {
            key: `${row.id}-dueDate`, field: "dueDate", value: dueDateValue,
            cellClass: dueDateCellClass
          },
          {
            key: `${row.id}-margin`, field: "margin", value: row.margin,
            cellClass: row.marginClass || ""
          }
        ],
        numberCells: CREDIT_NUM_FIELDS.map(({ field: f, disableable }) => ({
          key: `${row.id}-${f}`, field: f, value: row[f],
          cellClass: row[`${f}Class`] || "",
          disabled: disableable ? row.disabled : false,
          renderAsFormatted: disableable ? !!row.disabled : false
        }))
      };
    });
  }

  get exchangeRows() {
    return this.exchangeReservationData.map((row) => ({
      ...row,
      cells: EXCHANGE_HIGHLIGHT_FIELDS.map((f) => ({
        key: `${row.id}-${f}`, field: f, value: row[f],
        cellClass: row[`${f}Class`] || ""
      }))
    }));
  }

  resetData() {
    const cloneAndInit = (data, fields) => [
      deepClone(data),
      addEmptyHighlightClasses(data, fields)
    ];
    [this.originalCreditData, this.creditData] =
      cloneAndInit(this.initialCreditData, CREDIT_HIGHLIGHT_FIELDS);
    [this.originalExchangeReservationData, this.exchangeReservationData] =
      cloneAndInit(this.initialExchangeReservationData, EXCHANGE_HIGHLIGHT_FIELDS);
    [this.originalRegularCollateralData, this.regularCollateralData] =
      cloneAndInit(this.initialRegularCollateralData, COLLATERAL_HIGHLIGHT_FIELDS);
    [this.originalNonRegularCollateralData, this.nonRegularCollateralData] =
      cloneAndInit(this.initialNonRegularCollateralData, COLLATERAL_HIGHLIGHT_FIELDS);
    [this.originalReferenceData, this.referenceData] =
      cloneAndInit(this.initialReferenceData, REFERENCE_HIGHLIGHT_FIELDS);
  }

  handleInputChange(event) {
    const { id, field } = event.currentTarget?.dataset || event.target?.dataset || {};
    const value = event.target.value;
    if (!id || !field) return;
    const updateRows = (data) => this.updateDataImmutable(data, id, field, value);
    this.creditData = applyHighlight(
      updateRows(this.creditData), this.originalCreditData, CREDIT_HIGHLIGHT_FIELDS
    );
    this.exchangeReservationData = updateRows(this.exchangeReservationData);
    this.regularCollateralData = updateRows(this.regularCollateralData);
    this.nonRegularCollateralData = updateRows(this.nonRegularCollateralData);
    this.referenceData = updateRows(this.referenceData);
  }

  updateDataImmutable(data, id, field, value) {
    return data.map((row) => (row.id === id ? { ...row, [field]: value } : row));
  }

  @api applySavedHighlight() { this.handleSave(); }

  handleSave() {
    const highlightAndSnapshot = (current, original, fields) => {
      const highlighted = applyHighlight(current, original, fields);
      return [highlighted, deepClone(highlighted)];
    };
    [this.creditData, this.originalCreditData] =
      highlightAndSnapshot(this.creditData, this.originalCreditData, CREDIT_HIGHLIGHT_FIELDS);
    [this.exchangeReservationData, this.originalExchangeReservationData] =
      highlightAndSnapshot(this.exchangeReservationData, this.originalExchangeReservationData, EXCHANGE_HIGHLIGHT_FIELDS);
    [this.regularCollateralData, this.originalRegularCollateralData] =
      highlightAndSnapshot(this.regularCollateralData, this.originalRegularCollateralData, COLLATERAL_HIGHLIGHT_FIELDS);
    [this.nonRegularCollateralData, this.originalNonRegularCollateralData] =
      highlightAndSnapshot(this.nonRegularCollateralData, this.originalNonRegularCollateralData, COLLATERAL_HIGHLIGHT_FIELDS);
    [this.referenceData, this.originalReferenceData] =
      highlightAndSnapshot(this.referenceData, this.originalReferenceData, REFERENCE_HIGHLIGHT_FIELDS);
  }

  handleReset() { this.resetData(); }
}
