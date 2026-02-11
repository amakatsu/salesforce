import { LightningElement, track } from "lwc";
import { makeTestData } from "c/testDataGenerator";
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
    label: "実勢現在残高 C/E+P/E",
    fieldName: "marketValueBalanceCEPE",
    type: "text"
  },
  {
    label: "実勢現在残高 C/E+P/E（参考値）",
    fieldName: "marketValueBalanceCEPEReference",
    type: "text"
  },
  {
    label: "実勢現在残高 C/E",
    fieldName: "marketValueBalanceCE",
    type: "text"
  },
  {
    label: "実勢現在残高 C/E（参考値）",
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

const MAX_NUM_4 = makeTestData("numeric", 4);
const MAX_NUM_5 = makeTestData("numeric", 5);
const MAX_NUM_6 = makeTestData("numeric", 6);
const MAX_NUM_13 = makeTestData("numeric", 13);

const CREDIT_DEFAULTS = {
  creditType2: "",
  grossNet: "",
  dueDate: "99/99",
  margin: MAX_NUM_4,
  endOfMonthBalance: MAX_NUM_6,
  endOfMonthLimit: MAX_NUM_6,
  currentMonthChange: MAX_NUM_6,
  postTransactionCreditAmount: MAX_NUM_6,
  marketValueBalanceCEPE: MAX_NUM_6,
  marketValueBalanceCEPEReference: MAX_NUM_6,
  marketValueBalanceCE: MAX_NUM_6,
  marketValueBalanceCEReference: MAX_NUM_6,
  assumedPrincipalApprovalAmount: MAX_NUM_13,
  assumedPrincipalMarketValueBalance: MAX_NUM_13,
  disabled: false
};

const creditRow = ({ id, creditType1, overrides = {}, disabled }) => ({
  id,
  creditType1,
  ...CREDIT_DEFAULTS,
  ...overrides,
  ...(disabled !== undefined ? { disabled } : {})
});

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
    creditType1: "××××××××××××××××××××××××××××××××××××××××",
    overrides: {
      creditType2: "ワーニング",
      grossNet: "グロス"
    }
  },
  {
    id: "3",
    creditType1: `${makeTestData("mixedChar", 15)}与信科目`,
    overrides: {
      creditType2: "ワーニン",
      grossNet: "ネット",
      currentMonthChange: "-999999"
    }
  },
  {
    id: "4",
    creditType1: `${makeTestData("mixedChar", 16)}与信科目`,
    overrides: {
      creditType2: "ワーニン",
      grossNet: "グロス"
    }
  },
  {
    id: "5",
    creditType1: "限度不算入与信為替取引",
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "6",
    creditType1: "スワップ/オプション取引",
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "7",
    creditType1: "その他",
    overrides: {
      dueDate: "",
      ...DASH_FIELDS
    },
    disabled: true
  },
  {
    id: "8",
    creditType1: "限度不算入与信合計",
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

function generateCreditData() {
  return CREDIT_ITEMS.map(item => creditRow(item));
}
export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC4 extends LightningElement {
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
  @track amountUnit = "〇〇〇";
  @track groupNumber = makeTestData("numeric", 1);
  @track creditData = generateCreditData();
  creditColumns = CREDIT_COLUMNS;
  handleInputChange(event) {
    const { id, field } = event.currentTarget.dataset;
    const value = event.target.value;
    this.updateData(this.creditData, id, field, value);
  }
  updateData(data, id, field, value) {
    const item = data.find((row) => row.id === id);
    if (item) {
      item[field] = value;
    }
  }
}
