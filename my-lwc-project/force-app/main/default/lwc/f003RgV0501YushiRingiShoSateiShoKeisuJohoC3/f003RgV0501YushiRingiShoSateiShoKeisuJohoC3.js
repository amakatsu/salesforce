import { LightningElement, track, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

const BANK_COLUMNS = [
  { label: "銀行名", fieldName: "bankName", type: "text" },
  { label: "２年前", fieldName: "twoYearsAgo", type: "text" },
  { label: "１年前", fieldName: "oneYearAgo", type: "text" },
  { label: "直近月末", fieldName: "recentEnd", type: "text" },
  { label: "外為シェア", fieldName: "foreignCurrency", type: "text" }
];

const INDICATOR_COLUMNS = [
  { label: "決算期", fieldName: "period" },
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

const ACTIVE_SECTIONS = [
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

const MAX_AMOUNT = makeTestData("numeric", 5);
const MAX_AMOUNT9 = makeTestData("numeric", 9);
const MAX_AMOUNT6 = makeTestData("numeric", 6);
const MAX_BALANCE_RATIO = "999.9";
const MAX_RATE = "99.99";
const MAX_SMALL_RATE = "99.9";
const MAX_DISTRIBUTION_RATE = makeTestData("numeric", 3);

const ASSESSMENT_KEYS = [
  "nonClassifiedAmount",
  "firstClassifiedAmount",
  "secondClassifiedAmount",
  "thirdClassifiedAmount",
  "fourthClassifiedAmount",
  "totalAmount",
  "managedPreferredDebt",
  "creditRelatedCosts"
];
const OTHER_TRANSACTION_KEYS = [
  "agencyFee",
  "privateBond",
  "principal",
  "guarantor",
  "largeRemaining",
  "extreme",
  "specialContract"
];
const STOCK_KEYS = [
  "stockName",
  "stockQuantity",
  "acquisitionPrice",
  "stockPrice",
  "acquisitionDate",
  "currentPrice",
  "valuationProfitLoss"
];

const BANK_DEFAULTS = {
  twoYearsAgo: MAX_AMOUNT,
  oneYearAgo: MAX_AMOUNT,
  recentEnd: MAX_AMOUNT,
  foreignCurrency: MAX_AMOUNT
};
const BANK_DISABLE_DEFAULTS = {
  twoYearsAgo: true,
  oneYearAgo: true,
  recentEnd: true,
  foreignCurrency: false
};

const INDICATOR_DEFAULTS = {
  type: "",
  period: "99.99",
  sales: MAX_AMOUNT9,
  operatingProfit: MAX_AMOUNT9,
  currentProfit: MAX_AMOUNT6,
  currentProfitRate: MAX_RATE,
  netProfit: MAX_AMOUNT6,
  netProfitRate: MAX_RATE,
  depreciation: MAX_AMOUNT6,
  commercialCF: MAX_AMOUNT6,
  distributionRate: MAX_DISTRIBUTION_RATE,
  ownCapital: MAX_AMOUNT6,
  borrowingPeriod: MAX_SMALL_RATE,
  netInterestBurdenRate: MAX_SMALL_RATE,
  ownCapitalRatio: MAX_SMALL_RATE,
  currentBalanceRatio: MAX_BALANCE_RATIO
};

const INDICATOR_DISABLE_DEFAULTS = {
  period: true,
  sales: true,
  operatingProfit: true,
  currentProfit: true,
  currentProfitRate: true,
  netProfit: true,
  netProfitRate: true,
  depreciation: true,
  commercialCF: true,
  distributionRate: true,
  ownCapital: true,
  borrowingPeriod: true,
  netInterestBurdenRate: true,
  ownCapitalRatio: true,
  currentBalanceRatio: true
};

const BANK_HIGHLIGHT_FIELDS = Object.keys(BANK_DEFAULTS);
const INDICATOR_HIGHLIGHT_FIELDS = Object.keys(INDICATOR_DEFAULTS).filter(
  (f) => f !== "type"
);

const valueField = (value, editable = true) => ({ value, editable });
const valueMap = (values, editable = true) =>
  Object.fromEntries(
    Object.entries(values).map(([key, value]) => [
      key,
      valueField(value, editable)
    ])
  );
const fillValueMap = (keys, value, editable = true) =>
  Object.fromEntries(keys.map((key) => [key, valueField(value, editable)]));

const bankRow = ({ id, bankName, values = {}, disable = {} }) => ({
  id,
  bankName,
  ...BANK_DEFAULTS,
  ...values,
  disable: { ...BANK_DISABLE_DEFAULTS, ...disable }
});

const indicatorRow = ({ id, overrides = {}, disable = {} }) => ({
  id,
  ...INDICATOR_DEFAULTS,
  ...overrides,
  disable: { ...INDICATOR_DISABLE_DEFAULTS, ...disable }
});

function generateBankData() {
  return [
    bankRow({ id: "1", bankName: "当行" }),
    bankRow({
      id: "2",
      bankName: "シェア(％)",
      values: {
        twoYearsAgo: "99.999",
        oneYearAgo: "99.999",
        recentEnd: "99.999",
        foreignCurrency: "-"
      },
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
      id: "4",
      overrides: { type: "中間", currentBalanceRatio: "" },
      disable: {
        period: false,
        sales: false,
        operatingProfit: false,
        currentProfit: false,
        currentProfitRate: false,
        netProfit: false,
        netProfitRate: false,
        depreciation: false,
        commercialCF: false,
        distributionRate: false,
        ownCapital: false,
        borrowingPeriod: false,
        netInterestBurdenRate: false,
        ownCapitalRatio: false,
        currentBalanceRatio: true
      }
    }),
    indicatorRow({
      id: "5",
      overrides: {
        type: "予想",
        netInterestBurdenRate: "",
        ownCapitalRatio: "",
        currentBalanceRatio: ""
      },
      disable: {
        period: false,
        sales: false,
        operatingProfit: false,
        currentProfit: false,
        currentProfitRate: false,
        netProfit: false,
        netProfitRate: false,
        depreciation: false,
        commercialCF: false,
        distributionRate: false,
        ownCapital: false,
        borrowingPeriod: false,
        netInterestBurdenRate: true,
        ownCapitalRatio: true,
        currentBalanceRatio: true
      }
    })
  ];
}

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC3 extends LightningElement {
  @track amountUnit = "〇〇〇";
  @track groupNumber = makeTestData("numeric", 1);
  activeSections = ACTIVE_SECTIONS;
  @track bankData = generateBankData();
  bankColumns = BANK_COLUMNS;
  @track indicatorData = generateIndicatorData();
  indicatorColumns = INDICATOR_COLUMNS;

  @track assessmentData = fillValueMap(ASSESSMENT_KEYS, MAX_AMOUNT);

  @track otherTransactionData = fillValueMap(
    OTHER_TRANSACTION_KEYS,
    MAX_AMOUNT
  );

  @track stockData = fillValueMap(STOCK_KEYS, MAX_AMOUNT);

  @track memo = valueField(makeTestData("mixedChar", 214), false);
  @track total = valueField("99.9999");

  _savedBankValues = new Map();
  _savedIndicatorValues = new Map();

  connectedCallback() {
    this._snapshotValues();
  }

  _getValue(group, key) {
    return this[group][key].value;
  }

  get nonClassifiedAmount() {
    return this._getValue("assessmentData", "nonClassifiedAmount");
  }

  get firstClassifiedAmount() {
    return this._getValue("assessmentData", "firstClassifiedAmount");
  }

  get secondClassifiedAmount() {
    return this._getValue("assessmentData", "secondClassifiedAmount");
  }

  get thirdClassifiedAmount() {
    return this._getValue("assessmentData", "thirdClassifiedAmount");
  }

  get fourthClassifiedAmount() {
    return this._getValue("assessmentData", "fourthClassifiedAmount");
  }

  get totalAmount() {
    return this._getValue("assessmentData", "totalAmount");
  }

  get managedPreferredDebt() {
    return this._getValue("assessmentData", "managedPreferredDebt");
  }

  get creditRelatedCosts() {
    return this._getValue("assessmentData", "creditRelatedCosts");
  }

  get agencyFee() {
    return this._getValue("otherTransactionData", "agencyFee");
  }

  get privateBond() {
    return this._getValue("otherTransactionData", "privateBond");
  }

  get principal() {
    return this._getValue("otherTransactionData", "principal");
  }

  get guarantor() {
    return this._getValue("otherTransactionData", "guarantor");
  }

  get largeRemaining() {
    return this._getValue("otherTransactionData", "largeRemaining");
  }

  get extreme() {
    return this._getValue("otherTransactionData", "extreme");
  }

  get specialContract() {
    return this._getValue("otherTransactionData", "specialContract");
  }

  get stockName() {
    return this._getValue("stockData", "stockName");
  }

  get stockQuantity() {
    return this._getValue("stockData", "stockQuantity");
  }

  get acquisitionPrice() {
    return this._getValue("stockData", "acquisitionPrice");
  }

  get stockPrice() {
    return this._getValue("stockData", "stockPrice");
  }

  get acquisitionDate() {
    return this._getValue("stockData", "acquisitionDate");
  }

  get currentPrice() {
    return this._getValue("stockData", "currentPrice");
  }

  get valuationProfitLoss() {
    return this._getValue("stockData", "valuationProfitLoss");
  }

  get memoValue() {
    return this.memo.value;
  }

  get totalValue() {
    return this.total.value;
  }

  handleInputChange(event) {
    const { id, field } = event.currentTarget.dataset;
    const value = event.target.value;
    this.updateData(this.bankData, id, field, value);
    this.updateData(this.indicatorData, id, field, value);
  }

  updateData(data, id, field, value) {
    const item = data.find((row) => row.id === id);

    if (item && !item.disable[field]) {
      item[field] = value;
    }
  }

  _snapshotValues() {
    this._savedBankValues = new Map();
    for (const row of this.bankData) {
      const snapshot = {};
      for (const field of BANK_HIGHLIGHT_FIELDS) {
        snapshot[field] = row[field];
      }
      this._savedBankValues.set(row.id, snapshot);
    }
    this._savedIndicatorValues = new Map();
    for (const row of this.indicatorData) {
      const snapshot = {};
      for (const field of INDICATOR_HIGHLIGHT_FIELDS) {
        snapshot[field] = row[field];
      }
      this._savedIndicatorValues.set(row.id, snapshot);
    }
  }

  @api
  applySavedHighlight() {
    const cls = "cell-changed-saved";

    this.bankData = this.bankData.map((row) => {
      const saved = this._savedBankValues.get(row.id) || {};
      const updated = { ...row };
      for (const field of BANK_HIGHLIGHT_FIELDS) {
        updated[field + "Class"] =
          String(updated[field]) !== String(saved[field]) ? cls : "";
      }
      return updated;
    });

    this.indicatorData = this.indicatorData.map((row) => {
      const saved = this._savedIndicatorValues.get(row.id) || {};
      const updated = { ...row };
      for (const field of INDICATOR_HIGHLIGHT_FIELDS) {
        updated[field + "Class"] =
          String(updated[field]) !== String(saved[field]) ? cls : "";
      }
      return updated;
    });

    this._snapshotValues();
  }
}
