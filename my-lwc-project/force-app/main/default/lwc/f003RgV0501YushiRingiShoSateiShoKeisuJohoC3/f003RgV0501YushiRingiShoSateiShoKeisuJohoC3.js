import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

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

const BANK_COLUMNS = [
  { label: "銀行名", fieldName: "bankName", type: "text" },
  { label: "２年前", fieldName: "twoYearsAgo", type: "text" },
  { label: "１年前", fieldName: "oneYearAgo", type: "text" },
  { label: "直近月末", fieldName: "recentEnd", type: "text" },
  { label: "外為シェア", fieldName: "foreignCurrency", type: "text" }
];

const INDICATOR_COLUMNS = [
  { label: "決算期(年/月)", fieldName: "period" },
  { label: "純売上高", fieldName: "sales" },
  { label: "月商", fieldName: "operatingProfit" },
  { label: "経常利益", fieldName: "currentProfit" },
  { label: "経常利益率(％)", fieldName: "currentProfitRate" },
  { label: "当期利益", fieldName: "netProfit" },
  { label: "当期利益率(％)", fieldName: "netProfitRate" },
  { label: "減価償却", fieldName: "depreciation" },
  { label: "簡易CF", fieldName: "commercialCF" },
  { label: "配当率(％)", fieldName: "distributionRate" },
  { label: "自己資本", fieldName: "ownCapital" },
  { label: "借入金回転期間(月)", fieldName: "borrowingPeriod" },
  { label: "純金利負担率(％)", fieldName: "netInterestBurdenRate" },
  { label: "自己資本比率(％)", fieldName: "ownCapitalRatio" },
  { label: "経常収支比率(％)", fieldName: "currentBalanceRatio" }
];

const ACTIVE_SECTIONS = "abcdefghijklmnopqr".split("");

const MAX_AMOUNT_5 = makeTestData("numeric", 5);
const MAX_AMOUNT_9 = makeTestData("numeric", 9);
const MAX_AMOUNT_6 = makeTestData("numeric", 6);
const MAX_DISTRIBUTION_RATE = makeTestData("numeric", 3);

const ASSESSMENT_LABELS = {
  nonClassifiedAmount: "非分類額",
  firstClassifiedAmount: "第I分類額",
  secondClassifiedAmount: "第II分類額",
  thirdClassifiedAmount: "第III分類額",
  fourthClassifiedAmount: "第IV分類額",
  totalAmount: "合計",
  managedPreferredDebt: "内要管理債権"
};
const ASSESSMENT_KEYS = [...Object.keys(ASSESSMENT_LABELS), "creditRelatedCosts"];

const OTHER_TRANSACTION_KEYS = [
  "agencyFee", "privateBond", "principal", "guarantor",
  "largeRemaining", "extreme", "specialContract"
];

const STOCK_LABELS = {
  stockName: "株数(株)",
  stockQuantity: "簿価(円)",
  acquisitionPrice: "取得価格(円)",
  stockPrice: "時価(円)",
  acquisitionDate: "取引先保有株数(株)",
  currentPrice: "取引先保有時価(円)",
  valuationProfitLoss: "採算(％)"
};
const STOCK_KEYS = Object.keys(STOCK_LABELS);

const BANK_FIELDS = ["twoYearsAgo", "oneYearAgo", "recentEnd", "foreignCurrency"];
const BANK_DEFAULTS = Object.fromEntries(BANK_FIELDS.map(field => [field, MAX_AMOUNT_5]));
const BANK_DISABLE_DEFAULTS = { twoYearsAgo: true, oneYearAgo: true, recentEnd: true, foreignCurrency: false };

const INDICATOR_DEFAULTS = {
  type: "", fiscalYear: "9999", fiscalMonth: "99",
  sales: MAX_AMOUNT_9, operatingProfit: MAX_AMOUNT_9,
  currentProfit: MAX_AMOUNT_6, currentProfitRate: "99.99",
  netProfit: MAX_AMOUNT_6, netProfitRate: "99.99",
  depreciation: MAX_AMOUNT_6, commercialCF: MAX_AMOUNT_6,
  distributionRate: MAX_DISTRIBUTION_RATE, ownCapital: MAX_AMOUNT_6,
  borrowingPeriod: "99.9", netInterestBurdenRate: "99.9",
  ownCapitalRatio: "99.9", currentBalanceRatio: "999.9"
};
const INDICATOR_FIELDS = Object.keys(INDICATOR_DEFAULTS).filter(key => key !== "type");
const INDICATOR_DISABLE_DEFAULTS = Object.fromEntries(INDICATOR_FIELDS.map(field => [field, true]));

const disableOnly = (keysToDisable = []) =>
  Object.fromEntries(INDICATOR_FIELDS.map(field => [field, keysToDisable.includes(field)]));

const valueField = (value, disabled = true) => ({ value, disabled });
const fillValueMap = (keys, value, disabled = true) =>
  Object.fromEntries(keys.map(key => [key, valueField(value, disabled)]));

const bankRow = ({ id, bankName, values = {}, disable = {} }) => ({
  id, bankName, ...BANK_DEFAULTS, ...values,
  disable: { ...BANK_DISABLE_DEFAULTS, ...disable }
});
const indicatorRow = ({ id, overrides = {}, disable = {} }) => ({
  id, ...INDICATOR_DEFAULTS, ...overrides,
  disable: { ...INDICATOR_DISABLE_DEFAULTS, ...disable }
});

function generateBankData() {
  return [
    bankRow({ id: "1", bankName: "当行" }),
    bankRow({
      id: "2", bankName: "シェア(％)",
      values: { twoYearsAgo: "99.999", oneYearAgo: "99.999", recentEnd: "99.999", foreignCurrency: "-" },
      disable: { foreignCurrency: true }
    }),
    bankRow({ id: "3", bankName: makeTestData("mixedChar", 10) }),
    bankRow({ id: "4", bankName: makeTestData("mixedChar", 10) }),
    bankRow({ id: "5", bankName: makeTestData("mixedChar", 10) }),
    bankRow({ id: "6", bankName: "総借入" })
  ];
}

function generateIndicatorData() {
  return [
    indicatorRow({ id: "1" }),
    indicatorRow({ id: "2" }),
    indicatorRow({ id: "3" }),
    indicatorRow({
      id: "4", overrides: { type: "中間", currentBalanceRatio: "" },
      disable: disableOnly(["currentBalanceRatio"])
    }),
    indicatorRow({
      id: "5",
      overrides: { type: "予想", netInterestBurdenRate: "", ownCapitalRatio: "", currentBalanceRatio: "" },
      disable: disableOnly(["netInterestBurdenRate", "ownCapitalRatio", "currentBalanceRatio"])
    })
  ];
}

function buildCells(row, columns) {
  return columns.map(col => ({
    fieldName: col.fieldName,
    value: row[col.fieldName],
    cellClass: row[col.fieldName + "Class"] || "",
    disabled: row.disable[col.fieldName],
    renderAsFormatted: !!row.disable[col.fieldName]
  }));
}

function buildDisplayRows(data, labels) {
  return Object.entries(labels).map(([key, label]) => ({
    key, label, value: data[key]
  }));
}

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC3 extends LightningElement {
  amountUnit = "〇〇〇";
  groupNumber = makeTestData("numeric", 1);
  activeSections = ACTIVE_SECTIONS;
  bankColumns = BANK_COLUMNS;
  indicatorColumns = INDICATOR_COLUMNS;
  assessmentData = Object.fromEntries(ASSESSMENT_KEYS.map(key => [key, MAX_AMOUNT_5]));
  otherTransactionData = fillValueMap(OTHER_TRANSACTION_KEYS, MAX_AMOUNT_5);
  stockData = Object.fromEntries(STOCK_KEYS.map(key => [key, MAX_AMOUNT_5]));
  memo = valueField(makeTestData("mixedChar", 214), false);
  total = valueField("99.9999", true);

  initialBankData = generateBankData();
  initialIndicatorData = generateIndicatorData();
  originalBankData = [];
  originalIndicatorData = [];
  bankData = [];
  indicatorData = [];

  connectedCallback() { this.resetData(); }

  get bankRows() {
    const cols = BANK_COLUMNS.slice(1);
    return this.bankData.map(row => ({ ...row, cells: buildCells(row, cols) }));
  }
  get indicatorRows() {
    const cols = INDICATOR_COLUMNS.slice(1);
    return this.indicatorData.map(row => ({
      ...row,
      periodDisabled: !!row.disable.fiscalYear,
      cells: buildCells(row, cols)
    }));
  }
  get assessmentRows() { return buildDisplayRows(this.assessmentData, ASSESSMENT_LABELS); }
  get stockRows() { return buildDisplayRows(this.stockData, STOCK_LABELS); }
  get memoValue() { return this.memo.value; }
  get totalValue() { return this.total.value; }

  resetData() {
    const cloneAndInit = (data, fields) => [
      deepClone(data),
      addEmptyHighlightClasses(data, fields)
    ];
    [this.originalBankData, this.bankData] =
      cloneAndInit(this.initialBankData, BANK_FIELDS);
    [this.originalIndicatorData, this.indicatorData] =
      cloneAndInit(this.initialIndicatorData, INDICATOR_FIELDS);
  }

  handleInputChange(event) {
    const detail = event.detail || {};
    const id = event.currentTarget?.dataset?.id || detail.id;
    const field = event.currentTarget?.dataset?.field || detail.field;
    const value = detail.value !== undefined ? detail.value : event.target.value;
    if (!id || !field) return;
    const updateRows = (data) => this.updateDataImmutable(data, id, field, value);
    this.bankData = applyHighlight(
      updateRows(this.bankData), this.originalBankData, BANK_FIELDS
    );
    this.indicatorData = applyHighlight(
      updateRows(this.indicatorData), this.originalIndicatorData, INDICATOR_FIELDS
    );
  }

  updateDataImmutable(data, id, field, value) {
    return data.map((row) => {
      if (row.id !== id) return row;
      if (row.disable && row.disable[field]) return row;
      return { ...row, [field]: value };
    });
  }

  @api applySavedHighlight() { this.handleSave(); }

  handleSave() {
    const highlightAndSnapshot = (current, original, fields) => {
      const highlighted = applyHighlight(current, original, fields);
      return [highlighted, deepClone(highlighted)];
    };
    [this.bankData, this.originalBankData] =
      highlightAndSnapshot(this.bankData, this.originalBankData, BANK_FIELDS);
    [this.indicatorData, this.originalIndicatorData] =
      highlightAndSnapshot(this.indicatorData, this.originalIndicatorData, INDICATOR_FIELDS);
  }

  handleReset() { this.resetData(); }
}
