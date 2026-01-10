import { LightningElement, track } from "lwc";
const BANK_COLUMNS = [
  {
    label: "銀行名",
    fieldName: "bankName",
    type: "text"
  },
  {
    label: "2年前",
    fieldName: "twoYearsAgo",
    type: "text"
  },
  {
    label: "1年前",
    fieldName: "oneYearAgo",
    type: "text"
  },
  {
    label: "直近月末",
    fieldName: "recentEnd",
    type: "text"
  },
  {
    label: "外為シェア",
    fieldName: "foreignCurrency",
    type: "text"
  }
];
const INDICATOR_COLUMNS = [
  {
    label: "決算期",
    fieldName: "period",
    type: "text",
    className: "table-sticky__title table-sticky3__title01 width-100"
  },
  {
    label: "純売上高",
    fieldName: "sales",
    type: "text",
    className: "table-sticky__title table-sticky3__title02 width-100"
  },
  {
    label: "月商",
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
    label: "経常利益率（%）",
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
    label: "当期利益率（%）",
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
    label: "簡易CF",
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
  const data = [
    {
      id: "1",
      bankName: "当行",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: false
      }
    },
    {
      id: "2",
      bankName: "シェア(%)",
      twoYearsAgo: "99.999",
      oneYearAgo: "99.999",
      recentEnd: "99.999",
      foreignCurrency: "-",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: true
      }
    },
    {
      id: "3",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: false
      }
    },
    {
      id: "4",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: false
      }
    },
    {
      id: "5",
      bankName: "○○○○○",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: false
      }
    },
    {
      id: "6",
      bankName: "総借入",
      twoYearsAgo: "99999",
      oneYearAgo: "99999",
      recentEnd: "99999",
      foreignCurrency: "99999",
      disable: {
        twoYearsAgo: true,
        oneYearAgo: true,
        recentEnd: true,
        foreignCurrency: false
      }
    }
  ];
  return data;
}

function generateIndicatorData() {
  const data = [
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
      disable: {
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
      }
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
      disable: {
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
      }
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
      disable: {
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
      }
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
    }
  ];
  return data;
}
export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC3 extends LightningElement {
  @track amountUnit = "〇〇〇";
  @track groupNumber = "9";
  activeSections = ACTIVE_SECTIONS;
  @track bankData = generateBankData();
  bankColumns = BANK_COLUMNS;
  @track indicatorData = generateIndicatorData();
  indicatorColumns = INDICATOR_COLUMNS;

  // 自己査定結果データ
  @track assessmentData = {
    nonClassifiedAmount: { value: "99999", editable: true },
    firstClassifiedAmount: { value: "99999", editable: true },
    secondClassifiedAmount: { value: "99999", editable: true },
    thirdClassifiedAmount: { value: "99999", editable: true },
    fourthClassifiedAmount: { value: "99999", editable: true },
    totalAmount: { value: "99999", editable: true },
    managedPreferredDebt: { value: "99999", editable: true },
    creditRelatedCosts: { value: "99999", editable: true }
  };

  // その他取引状況データ
  @track otherTransactionData = {
    agencyFee: { value: "99999", editable: true },
    privateBond: { value: "99999", editable: true },
    principal: { value: "99999", editable: true },
    guarantor: { value: "99999", editable: true },
    largeRemaining: { value: "99999", editable: true },
    extreme: { value: "99999", editable: true },
    specialContract: { value: "99999", editable: true }
  };

  // 政策投資株式データ
  @track stockData = {
    stockName: { value: "99999", editable: true },
    stockQuantity: { value: "99999", editable: true },
    acquisitionPrice: { value: "99999", editable: true },
    stockPrice: { value: "99999", editable: true },
    acquisitionDate: { value: "99999", editable: true },
    currentPrice: { value: "99999", editable: true },
    valuationProfitLoss: { value: "99999", editable: true }
  };

  // その他単体データ
  @track memo = { value: "メモ内容", editable: false };
  @track total = { value: "99.9999", editable: true };

  // ゲッター：データ値を簡単にアクセスできるように
  get nonClassifiedAmount() {
    return this.assessmentData.nonClassifiedAmount.value;
  }

  get firstClassifiedAmount() {
    return this.assessmentData.firstClassifiedAmount.value;
  }

  get secondClassifiedAmount() {
    return this.assessmentData.secondClassifiedAmount.value;
  }

  get thirdClassifiedAmount() {
    return this.assessmentData.thirdClassifiedAmount.value;
  }

  get fourthClassifiedAmount() {
    return this.assessmentData.fourthClassifiedAmount.value;
  }

  get totalAmount() {
    return this.assessmentData.totalAmount.value;
  }

  get managedPreferredDebt() {
    return this.assessmentData.managedPreferredDebt.value;
  }

  get creditRelatedCosts() {
    return this.assessmentData.creditRelatedCosts.value;
  }

  get agencyFee() {
    return this.otherTransactionData.agencyFee.value;
  }

  get privateBond() {
    return this.otherTransactionData.privateBond.value;
  }

  get principal() {
    return this.otherTransactionData.principal.value;
  }

  get guarantor() {
    return this.otherTransactionData.guarantor.value;
  }

  get largeRemaining() {
    return this.otherTransactionData.largeRemaining.value;
  }

  get extreme() {
    return this.otherTransactionData.extreme.value;
  }

  get specialContract() {
    return this.otherTransactionData.specialContract.value;
  }

  get stockName() {
    return this.stockData.stockName.value;
  }

  get stockQuantity() {
    return this.stockData.stockQuantity.value;
  }

  get acquisitionPrice() {
    return this.stockData.acquisitionPrice.value;
  }

  get stockPrice() {
    return this.stockData.stockPrice.value;
  }

  get acquisitionDate() {
    return this.stockData.acquisitionDate.value;
  }

  get currentPrice() {
    return this.stockData.currentPrice.value;
  }

  get valuationProfitLoss() {
    return this.stockData.valuationProfitLoss.value;
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
}
