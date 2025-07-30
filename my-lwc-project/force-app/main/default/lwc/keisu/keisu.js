import { LightningElement, track } from "lwc";

const BANK_COLUMNS = [
  { label: "銀行名", fieldName: "bankName", type: "text" },
  { label: "2年前", fieldName: "twoYearsAgo", type: "text" },
  { label: "1年前", fieldName: "oneYearAgo", type: "text" },
  { label: "直近月末", fieldName: "recentEnd", type: "text" },
  { label: "外為シェア", fieldName: "foreignCurrency", type: "text" }
];

const INDICATOR_COLUMNS = [
  {
    label: "",
    fieldName: "type",
    type: "text",
    className: "table-sticky__title table-sticky3__title01 width-15"
  },
  {
    label: "決算期",
    fieldName: "period",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "純売上高",
    fieldName: "sales",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "純売上高（月商）",
    fieldName: "operatingProfit",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "経常利益",
    fieldName: "currentProfit",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "経常利益（同率）（％）",
    fieldName: "currentProfitRate",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "当期利益",
    fieldName: "netProfit",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "当期利益（同率）（％）",
    fieldName: "netProfitRate",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "減価償却",
    fieldName: "depreciation",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "商業CF",
    fieldName: "commercialCF",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "配当率（％）",
    fieldName: "distributionRate",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "自己資本",
    fieldName: "ownCapital",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "借入金回転期間（月）",
    fieldName: "borrowingPeriod",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "純金利負担率（％）",
    fieldName: "netInterestBurdenRate",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "自己資本比率（％）",
    fieldName: "ownCapitalRatio",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-120"
  },
  {
    label: "経常収支比率（％）",
    fieldName: "currentBalanceRatio",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  }
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

function generateBankData() {
  return [
    {
      id: "1",
      bankName: "当行",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      editable: false
    },
    {
      id: "2",
      bankName: "シェア(%)",
      twoYearsAgo: "99.999",
      oneYearAgo: "99.999",
      recentEnd: "99.999",
      foreignCurrency: "-",
      editable: true
    },
    {
      id: "3",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      editable: false
    },
    {
      id: "4",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      editable: false
    },
    {
      id: "5",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      editable: false
    },
    {
      id: "6",
      bankName: "総借入",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      editable: false
    }
  ];
}

function generateIndicatorData() {
  return [
    {
      id: "1",
      type: "",
      period: "99.99",
      sales: "99999",
      operatingProfit: "99999",
      currentProfit: "99999",
      netProfit: "99999",
      depreciation: "99999",
      commercialCF: "99999",
      distributionRate: "99.99",
      ownCapital: "99999",
      borrowingPeriod: "99.99",
      netInterestBurdenRate: "99.99",
      ownCapitalRatio: "99.99",
      currentBalanceRatio: "99.99",
      editable: true
    },
    {
      id: "2",
      type: "",
      period: "99.99",
      sales: "99999",
      operatingProfit: "99999",
      currentProfit: "99999",
      netProfit: "99999",
      depreciation: "99999",
      commercialCF: "99999",
      distributionRate: "99.99",
      ownCapital: "99999",
      borrowingPeriod: "99.99",
      netInterestBurdenRate: "99.99",
      ownCapitalRatio: "99.99",
      currentBalanceRatio: "99.99",
      editable: true
    },
    {
      id: "3",
      type: "",
      period: "99.99",
      sales: "99999",
      operatingProfit: "99999",
      currentProfit: "99999",
      netProfit: "99999",
      depreciation: "99999",
      commercialCF: "99999",
      distributionRate: "99.99",
      ownCapital: "99999",
      borrowingPeriod: "99.99",
      netInterestBurdenRate: "99.99",
      ownCapitalRatio: "99.99",
      currentBalanceRatio: "99.99",
      editable: true
    },
    {
      id: "4",
      type: "中間",
      period: "99.99",
      sales: "99999",
      operatingProfit: "99999",
      currentProfit: "99999",
      netProfit: "99999",
      depreciation: "99999",
      commercialCF: "99999",
      distributionRate: "99.99",
      ownCapital: "99999",
      borrowingPeriod: "99.99",
      netInterestBurdenRate: "99.99",
      ownCapitalRatio: "99.99",
      currentBalanceRatio: "",
      editable: false
    },
    {
      id: "5",
      type: "予想",
      period: "99.99",
      sales: "99999",
      operatingProfit: "99999",
      currentProfit: "99999",
      netProfit: "99999",
      depreciation: "99999",
      commercialCF: "99999",
      distributionRate: "99.99",
      ownCapital: "99999",
      borrowingPeriod: "99.99",
      netInterestBurdenRate: "",
      ownCapitalRatio: "",
      currentBalanceRatio: "",
      editable: false
    }
  ];
}

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC3 extends LightningElement {
  @track amountUnit = "〇〇〇";
  @track groupNumber = "9";
  activeSections = ACTIVE_SECTIONS;

  @track bankData = generateBankData();
  bankColumns = BANK_COLUMNS;

  @track indicatorData = generateIndicatorData();
  indicatorColumns = INDICATOR_COLUMNS;

  @track total = "99.9999";

  @track nonClassifiedAmount = "99999";
  @track firstClassifiedAmount = "99999";
  @track secondClassifiedAmount = "99999";
  @track thirdClassifiedAmount = "99999";
  @track fourthClassifiedAmount = "99999";
  @track totalAmount = "99999";
  @track managedPreferredDebt = "99999";
  @track creditRelatedCosts = "99999";

  @track agencyFee = "99999";
  @track principal = "99999";
  @track guarantor = "99999";
  @track largeRemaining = "99999";
  @track extreme = "99999";
  @track specialContract = "99999";

  @track stockName = "99999";
  @track stockQuantity = "99999";
  @track acquisitionPrice = "99999";
  @track stockPrice = "99999";
  @track acquisitionDate = "99999";
  @track currentPrice = "99999";
  @track valuationProfitLoss = "99999";

  @track memo = "メモ内容";

  handleInputChange(event) {
    const { id, field } = event.currentTarget.dataset;
    const value = event.target.value;
    this.updateData(this.bankData, id, field, value);
    this.updateData(this.indicatorData, id, field, value);
  }

  updateData(data, id, field, value) {
    const item = data.find((row) => row.id === id);
    if (item) {
      item[field] = value;
    }
  }
}
