import { LightningElement, track } from "lwc";
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
function generateCreditData() {
  return [
    {
      id: "1",
      creditType1: "限度算入与信合計",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "",
      endOfMonthBalance: "99999",
      endOfMonthLimit: "99999",
      currentMonthChange: "-",
      postTransactionCreditAmount: "99999",
      marketValueBalanceCEPE: "99999",
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: "99999",
      marketValueBalanceCEReference: "-",
      assumedPrincipalApprovalAmount: "111000000",
      assumedPrincipalMarketValueBalance: "109500000",
      disabled: true
    },
    {
      id: "2",
      creditType1: "××××××××××××××××××××××××××××××××××××××××",
      creditType2: "ワーニング",
      grossNet: "グロス",
      dueDate: "99/99",
      margin: "9999",
      endOfMonthBalance: "999999",
      endOfMonthLimit: "999999",
      currentMonthChange: "999999",
      postTransactionCreditAmount: "999999",
      marketValueBalanceCEPE: "999999",
      marketValueBalanceCEPEReference: "999999",
      marketValueBalanceCE: "999999",
      marketValueBalanceCEReference: "999999",
      assumedPrincipalApprovalAmount: "13000000",
      assumedPrincipalMarketValueBalance: "12500000"
    },
    {
      id: "3",
      creditType1: "〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇与信科目",
      creditType2: "ワーニン",
      grossNet: "ネット",
      dueDate: "99/99",
      margin: "9999",
      endOfMonthBalance: "999999",
      endOfMonthLimit: "999999",
      currentMonthChange: "-999999",
      postTransactionCreditAmount: "999999",
      marketValueBalanceCEPE: "999999",
      marketValueBalanceCEPEReference: "999999",
      marketValueBalanceCE: "999999",
      marketValueBalanceCEReference: "999999",
      assumedPrincipalApprovalAmount: "21000000",
      assumedPrincipalMarketValueBalance: "20500000"
    },
    {
      id: "4",
      creditType1: "〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇与信科目",
      creditType2: "ワーニン",
      grossNet: "グロス",
      dueDate: "99/99",
      margin: "9999",
      endOfMonthBalance: "999999",
      endOfMonthLimit: "999999",
      currentMonthChange: "999999",
      postTransactionCreditAmount: "999999",
      marketValueBalanceCEPE: "999999",
      marketValueBalanceCEPEReference: "999999",
      marketValueBalanceCE: "999999",
      marketValueBalanceCEReference: "999999",
      assumedPrincipalApprovalAmount: "36000000",
      assumedPrincipalMarketValueBalance: "35500000"
    },
    {
      id: "5",
      creditType1: "限度不算入与信為替取引",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "-",
      endOfMonthBalance: "-",
      endOfMonthLimit: "-",
      currentMonthChange: "-",
      postTransactionCreditAmount: "-",
      marketValueBalanceCEPE: "-",
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: "-",
      marketValueBalanceCEReference: "-",
      assumedPrincipalApprovalAmount: "36000000",
      assumedPrincipalMarketValueBalance: "355,000,00",
      disabled: true
    },
    {
      id: "6",
      creditType1: "スワップ/オプション取引",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "-",
      endOfMonthBalance: "-",
      endOfMonthLimit: "-",
      currentMonthChange: "-",
      postTransactionCreditAmount: "-",
      marketValueBalanceCEPE: "-",
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: "-",
      marketValueBalanceCEReference: "-",
      assumedPrincipalApprovalAmount: "37000000",
      assumedPrincipalMarketValueBalance: "36500000",
      disabled: true
    },
    {
      id: "7",
      creditType1: "その他",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "-",
      endOfMonthBalance: "-",
      endOfMonthLimit: "-",
      currentMonthChange: "-",
      postTransactionCreditAmount: "-",
      marketValueBalanceCEPE: "-",
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: "-",
      marketValueBalanceCEReference: "-",
      assumedPrincipalApprovalAmount: "38000000",
      assumedPrincipalMarketValueBalance: "37500000",
      disabled: true
    },
    {
      id: "8",
      creditType1: "限度不算入与信合計",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "-",
      endOfMonthBalance: "",
      endOfMonthLimit: "",
      currentMonthChange: "",
      postTransactionCreditAmount: "",
      marketValueBalanceCEPE: "",
      marketValueBalanceCEPEReference: "",
      marketValueBalanceCE: "",
      marketValueBalanceCEReference: "",
      assumedPrincipalApprovalAmount: "1,11000000",
      assumedPrincipalMarketValueBalance: "109500000",
      disabled: true
    },
    {
      id: "9",
      creditType1: "市場性与信合計",
      creditType2: "",
      grossNet: "",
      dueDate: "",
      margin: "",
      endOfMonthBalance: "99999",
      endOfMonthLimit: "99999",
      currentMonthChange: "-",
      postTransactionCreditAmount: "99999",
      marketValueBalanceCEPE: "99999",
      marketValueBalanceCEPEReference: "-",
      marketValueBalanceCE: "99999",
      marketValueBalanceCEReference: "-",
      assumedPrincipalApprovalAmount: "1,11000000",
      assumedPrincipalMarketValueBalance: "109500000",
      disabled: false
    }
  ];
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
  @track groupNumber = "9";
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
