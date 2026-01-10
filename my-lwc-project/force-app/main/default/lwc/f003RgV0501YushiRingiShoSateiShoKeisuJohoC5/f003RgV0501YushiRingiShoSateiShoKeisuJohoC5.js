import { LightningElement, track } from "lwc";
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
  { label: "C/E+P/E", fieldName: "cePe" },
  { label: "C/E", fieldName: "ce" }
];
const CHANGED_CELL_CLASS = "changed-cell";

const EXCHANGE_DEFAULTS = {
  previousTermAverage: "99.99",
  lastTermAverage: "99.99",
  september99: "99.99",
  dueDate1: "99.99",
  dueDate2: "99.99",
  dueDate3: "99.99",
  dueDate4: "99.99",
  dueDate5: "99.99"
};
const exchangeRow = ({ id, type, overrides = {} }) => ({
  id,
  type,
  ...EXCHANGE_DEFAULTS,
  ...overrides
});

const COLLATERAL_DEFAULTS = {
  expectedShare: "99.99",
  marketValue: "99.99"
};
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

const REFERENCE_DEFAULTS = {
  cePe: "99999",
  ce: "99999",
  disabled: false
};
const referenceRow = ({ id, category, overrides = {}, disabled = false }) => ({
  id,
  category,
  ...REFERENCE_DEFAULTS,
  ...overrides,
  ...(disabled ? { disabled: true } : {})
});

function generateExchangeReservationData() {
  return [
    exchangeRow({
      id: "1",
      type: "予約平残",
      overrides: { previousTermAverage: "99999.99" }
    }),
    exchangeRow({ id: "2", type: "予約ピーク" }),
    exchangeRow({ id: "3", type: "当月締結累計額" }),
    exchangeRow({ id: "4", type: "平均回転期間" })
  ];
}
function generateRegularCollateralData() {
  return [
    collateralRow({ id: "11", collateralType: "預金" }),
    collateralRow({ id: "12", collateralType: "担手・電担" }),
    collateralRow({ id: "13", collateralType: "有証" }),
    collateralRow({ id: "14", collateralType: "保証" }),
    collateralRow({ id: "15", collateralType: "不動産" }),
    collateralRow({ id: "16", collateralType: "その他" }),
    collateralRow({ id: "17", collateralType: "規定担保計", disabled: true }),
    collateralRow({ id: "18", collateralType: "裸与信", disabled: true })
  ];
}
function generateNonRegularCollateralData() {
  return [
    collateralRow({ id: "111", collateralType: "担手・電担" }),
    collateralRow({ id: "115", collateralType: "不動産" }),
    collateralRow({ id: "116", collateralType: "入居保証金" }),
    collateralRow({ id: "117", collateralType: "債権" }),
    collateralRow({ id: "118", collateralType: "その他" }),
    collateralRow({ id: "119", collateralType: "規定外担保計", disabled: true })
  ];
}
function generateReferenceData() {
  return [
    referenceRow({ id: "1111", category: "為替取引", disabled: true }),
    referenceRow({ id: "1112", category: "スワップオプション取引", disabled: true }),
    referenceRow({ id: "1113", category: "マークトリスク内在型取引", disabled: true }),
    referenceRow({ id: "1114", category: "先物取引" }),
    referenceRow({ id: "1115", category: "その他市場性与信" }),
    referenceRow({ id: "1116", category: "全体", disabled: true })
  ];
}
export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC5 extends LightningElement {
  @track amountUnit = "〇〇〇";
  @track groupNumber = "9";
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
  initialExchangeReservationData = generateExchangeReservationData();
  initialRegularCollateralData = generateRegularCollateralData();
  initialNonRegularCollateralData = generateNonRegularCollateralData();
  initialReferenceData = generateReferenceData();
  originalExchangeReservationData = [];
  originalRegularCollateralData = [];
  originalNonRegularCollateralData = [];
  originalReferenceData = [];
  @track exchangeReservationData = [];
  @track regularCollateralData = [];
  @track nonRegularCollateralData = [];
  @track referenceData = [];
  exchangeReservationColumns = EXCHANGE_RESERVATION_COLUMNS;
  regularCollateralColumns = REGULAR_COLLATERAL_COLUMNS;
  nonRegularCollateralColumns = NON_REGULAR_COLLATERAL_COLUMNS;
  referenceColumns = REFERENCE_COLUMNS;
  connectedCallback() {
    this.resetData();
  }
  resetData() {
    this.originalExchangeReservationData = JSON.parse(
      JSON.stringify(this.initialExchangeReservationData)
    );
    this.originalRegularCollateralData = JSON.parse(
      JSON.stringify(this.initialRegularCollateralData)
    );
    this.originalNonRegularCollateralData = JSON.parse(
      JSON.stringify(this.initialNonRegularCollateralData)
    );
    this.originalReferenceData = JSON.parse(
      JSON.stringify(this.initialReferenceData)
    );
    this.exchangeReservationData = this.initialExchangeReservationData.map(
      (item) => ({
        ...item,
        previousTermAverageClass: "",
        lastTermAverageClass: "",
        september99Class: "",
        dueDate1Class: "",
        dueDate2Class: "",
        dueDate3Class: "",
        dueDate4Class: "",
        dueDate5Class: ""
      })
    );
    this.regularCollateralData = this.initialRegularCollateralData.map(
      (item) => ({ ...item, expectedShareClass: "", marketValueClass: "" })
    );
    this.nonRegularCollateralData = this.initialNonRegularCollateralData.map(
      (item) => ({ ...item, expectedShareClass: "", marketValueClass: "" })
    );
    this.referenceData = this.initialReferenceData.map((item) => ({
      ...item,
      cePeClass: "",
      ceClass: ""
    }));
  }
  handleInputChange(event) {
    const { id, field } = event.target.dataset;
    const value = event.target.value;
    this.updateData(this.exchangeReservationData, id, field, value);
    this.updateData(this.regularCollateralData, id, field, value);
    this.updateData(this.nonRegularCollateralData, id, field, value);
    this.updateData(this.referenceData, id, field, value);
  }
  updateData(data, id, field, value) {
    const recordIndex = data.findIndex((row) => row.id === id);
    if (recordIndex !== -1) {
      data[recordIndex][field] = value;
    }
  }
  handleSave() {
    console.log("Saving data...");
    this.exchangeReservationData = this.exchangeReservationData.map(
      (record) => {
        const original = this.originalExchangeReservationData.find(
          (r) => r.id === record.id
        );
        return {
          ...record,
          previousTermAverageClass:
            original.previousTermAverage !== record.previousTermAverage
              ? CHANGED_CELL_CLASS
              : "",
          lastTermAverageClass:
            original.lastTermAverage !== record.lastTermAverage
              ? CHANGED_CELL_CLASS
              : "",
          september99Class:
            original.september99 !== record.september99
              ? CHANGED_CELL_CLASS
              : "",
          dueDate1Class:
            original.dueDate1 !== record.dueDate1 ? CHANGED_CELL_CLASS : "",
          dueDate2Class:
            original.dueDate2 !== record.dueDate2 ? CHANGED_CELL_CLASS : "",
          dueDate3Class:
            original.dueDate3 !== record.dueDate3 ? CHANGED_CELL_CLASS : "",
          dueDate4Class:
            original.dueDate4 !== record.dueDate4 ? CHANGED_CELL_CLASS : "",
          dueDate5Class:
            original.dueDate5 !== record.dueDate5 ? CHANGED_CELL_CLASS : ""
        };
      }
    );
    this.regularCollateralData = this.regularCollateralData.map((record) => {
      const original = this.originalRegularCollateralData.find(
        (r) => r.id === record.id
      );
      return {
        ...record,
        expectedShareClass:
          original.expectedShare !== record.expectedShare
            ? CHANGED_CELL_CLASS
            : "",
        marketValueClass:
          original.marketValue !== record.marketValue ? CHANGED_CELL_CLASS : ""
      };
    });
    this.nonRegularCollateralData = this.nonRegularCollateralData.map(
      (record) => {
        const original = this.originalNonRegularCollateralData.find(
          (r) => r.id === record.id
        );
        return {
          ...record,
          expectedShareClass:
            original.expectedShare !== record.expectedShare
              ? CHANGED_CELL_CLASS
              : "",
          marketValueClass:
            original.marketValue !== record.marketValue
              ? CHANGED_CELL_CLASS
              : ""
        };
      }
    );
    this.referenceData = this.referenceData.map((record) => {
      const original = this.originalReferenceData.find(
        (r) => r.id === record.id
      );
      return {
        ...record,
        cePeClass: original.cePe !== record.cePe ? CHANGED_CELL_CLASS : "",
        ceClass: original.ce !== record.ce ? CHANGED_CELL_CLASS : ""
      };
    });
    this.originalExchangeReservationData = JSON.parse(
      JSON.stringify(this.exchangeReservationData)
    );
    this.originalRegularCollateralData = JSON.parse(
      JSON.stringify(this.regularCollateralData)
    );
    this.originalNonRegularCollateralData = JSON.parse(
      JSON.stringify(this.nonRegularCollateralData)
    );
    this.originalReferenceData = JSON.parse(JSON.stringify(this.referenceData));
  }
  handleReset() {
    console.log("Resetting data...");
    this.resetData();
  }
}
