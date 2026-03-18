/**
 * 市場性与信テーブル コンポーネント (C4)
 *
 * テーブル①: 市場性与信状況(15列) - 与信種類ごとの残高・極度額等を表示
 * テーブル②: 為替予約残高推移(9列) - 予約平残・ピーク等の推移を表示
 *
 * ■ データ保持の仕組み(3世代管理):
 *   - _initial: 初回ロード時の状態(リセットでここに戻す)
 *   - _saved:   最後の保存時の状態(変更箇所の色付けの比較基準)
 *   - _current: ユーザーが編集中のデータ(セルを編集すると更新される)
 */
import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

// =====================================================================
// 定数
// =====================================================================

const MAX_AMOUNT_7 = makeTestData("numeric", 7);
const MAX_AMOUNT_5 = makeTestData("numeric", 5);

/** 変更されたセルに付ける色付けクラス名 */
const HIGHLIGHT_CLASS = "changed-cell";

// =====================================================================
// ユーティリティ
// =====================================================================

const deepClone = (obj) => JSON.parse(JSON.stringify(obj));

/** 全フィールドに空の色付けクラスを初期設定する */
const initHighlightClasses = (data, fields) =>
  data.map((item) => ({
    ...item,
    ...Object.fromEntries(fields.map((f) => [`${f}Class`, ""]))
  }));

/** 保存時の値と比較し、変わったフィールドに色付けクラスを付ける */
const applyHighlight = (current, saved, fields) =>
  current.map((row) => {
    const savedRow = saved.find((item) => item.id === row.id) || {};
    return {
      ...row,
      ...Object.fromEntries(
        fields.map((f) => [
          `${f}Class`,
          savedRow[f] !== row[f] ? HIGHLIGHT_CLASS : ""
        ])
      )
    };
  });

// =====================================================================
// 市場性与信テーブル定義
// =====================================================================

/** ヘッダ列定義 */
const CREDIT_COLUMNS = [
  { key: "creditType1", label: "与信種類(科目)", w: "col-w95" },
  { key: "creditType2", label: "ワーニング情報", w: "col-w45" },
  { key: "grossNet", label: "グロス／ネット", w: "col-w35" },
  { key: "dueDate", label: "期日(年/月)", w: "col-w45" },
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

/** 文字表示のフィールド(ワーニング情報、グロス/ネット) */
const CREDIT_TEXT_FIELDS = ["creditType2", "grossNet"];

/** 数値フィールド(行の編集可否に連動して入力/表示が切り替わる) */
const CREDIT_NUM_FIELDS = [
  "endOfMonthBalance", "endOfMonthLimit", "currentMonthChange",
  "postTransactionCreditAmount", "marketValueBalanceCEPE", "marketValueBalanceCEPEReference",
  "marketValueBalanceCE", "marketValueBalanceCEReference",
  "assumedPrincipalApprovalAmount", "assumedPrincipalMarketValueBalance"
].map((f) => ({ field: f, disableable: true }));

/** 色付け対象の全フィールド */
const CREDIT_HIGHLIGHT_FIELDS = [
  ...CREDIT_TEXT_FIELDS,
  "dueDateYear", "dueDateMonth", "margin",
  ...CREDIT_NUM_FIELDS.map((col) => col.field)
];

/** 各行のデフォルト値 */
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

/** 残高系フィールドをまとめて書き換えるための定数 */
const BALANCE_FIELDS = [
  "endOfMonthBalance", "endOfMonthLimit", "currentMonthChange",
  "postTransactionCreditAmount", "marketValueBalanceCEPE", "marketValueBalanceCEPEReference",
  "marketValueBalanceCE", "marketValueBalanceCEReference"
];
const DASH_OVERRIDES = Object.fromEntries(BALANCE_FIELDS.map((f) => [f, "-"]));
const EMPTY_OVERRIDES = Object.fromEntries(BALANCE_FIELDS.map((f) => [f, ""]));
const SUMMARY_OVERRIDES = {
  dueDateYear: "", dueDateMonth: "", margin: "",
  endOfMonthBalance: MAX_AMOUNT_5, endOfMonthLimit: MAX_AMOUNT_5, currentMonthChange: "-",
  postTransactionCreditAmount: MAX_AMOUNT_5, marketValueBalanceCEPE: MAX_AMOUNT_5,
  marketValueBalanceCEPEReference: "-", marketValueBalanceCE: MAX_AMOUNT_5,
  marketValueBalanceCEReference: "-"
};

/** 行データを組み立てる関数 */
const buildCreditRow = ({ id, creditType1, indent = 0, overrides = {}, disabled }) => ({
  id, creditType1, creditType1Class: indent === 0 ? "tree-indent-root" : "tree-indent-child",
  ...CREDIT_DEFAULTS, ...overrides, ...(disabled !== undefined ? { disabled } : {})
});

/** サンプル行データ */
const CREDIT_ITEMS = [
  { id: "1", creditType1: "限度算入与信合計", overrides: SUMMARY_OVERRIDES, disabled: true },
  { id: "2", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニング", grossNet: "グロス" } },
  { id: "3", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニン", grossNet: "ネット", currentMonthChange: "-99999" } },
  { id: "4", creditType1: makeTestData("mixedChar", 40), indent: 1, overrides: { creditType2: "ワーニン", grossNet: "グロス" } },
  { id: "8", creditType1: "限度不算入与信合計", overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...EMPTY_OVERRIDES }, disabled: true },
  { id: "5", creditType1: "限度不算入与信為替取引", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "6", creditType1: "スワップ／オプション取引", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "7", creditType1: "その他", indent: 1, overrides: { dueDateYear: "", dueDateMonth: "", margin: "", ...DASH_OVERRIDES }, disabled: true },
  { id: "9", creditType1: "市場性与信合計", overrides: SUMMARY_OVERRIDES, disabled: false }
];

// =====================================================================
// 為替予約テーブル定義
// =====================================================================

/** ヘッダ列定義 */
const EXCHANGE_COLUMNS = [
  { label: "(注)除く限度不算入取引", fieldName: "type" },
  { label: "前々期平均", fieldName: "previousTermAverage" },
  { label: "前期平均", fieldName: "lastTermAverage" },
  { label: "99月", fieldName: "september99" },
  { label: "99月", fieldName: "dueDate1" }, { label: "99月", fieldName: "dueDate2" },
  { label: "99月", fieldName: "dueDate3" }, { label: "99月", fieldName: "dueDate4" },
  { label: "99月", fieldName: "dueDate5" }
];

/** 色付け対象フィールド */
const EXCHANGE_HIGHLIGHT_FIELDS = [
  "previousTermAverage", "lastTermAverage", "september99",
  "dueDate1", "dueDate2", "dueDate3", "dueDate4", "dueDate5"
];

const EXCHANGE_DEFAULTS = Object.fromEntries(
  EXCHANGE_HIGHLIGHT_FIELDS.map((f) => [f, "9999999"])
);

/** 行データを組み立てる関数 */
const buildExchangeRow = ({ id, type, overrides = {} }) => ({
  id, type, ...EXCHANGE_DEFAULTS, ...overrides
});

/** サンプル行データ */
const EXCHANGE_ITEMS = [
  { id: "1", type: "予約平残" }, { id: "2", type: "予約ピーク" },
  { id: "3", type: "当月締結累計額" },
  { id: "4", type: "平均回転期間", overrides: Object.fromEntries(EXCHANGE_HIGHLIGHT_FIELDS.map((f) => [f, "99.99"])) }
];

// =====================================================================
// コンポーネントクラス
// =====================================================================

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoC4 extends LightningElement {

  // --- @api ---

  /** 親から呼ばれる: 保存して色付けを更新する */
  @api applySavedHighlight() { this._save(); }

  // --- プロパティ ---

  amountUnit = "〇〇〇";
  groupNumber = makeTestData("numeric", 1);
  creditColumns = CREDIT_COLUMNS;
  exchangeColumns = EXCHANGE_COLUMNS;

  _initialCreditData = CREDIT_ITEMS.map((item) => buildCreditRow(item));
  _initialExchangeData = EXCHANGE_ITEMS.map((item) => buildExchangeRow(item));
  _savedCreditData = [];
  _savedExchangeData = [];
  _creditData = [];
  _exchangeData = [];

  // --- ライフサイクル ---

  /** 初回表示時にデータを初期化する */
  connectedCallback() { this._reset(); }

  // --- テンプレート用getter ---

  /** 市場性与信テーブルの表示行を組み立てる */
  get creditRows() {
    return this._creditData.map((row) => {
      const yearClass = row.dueDateYearClass || "";
      const monthClass = row.dueDateMonthClass || "";
      const dueDateCellClass = yearClass || monthClass ? HIGHLIGHT_CLASS : "";
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

  /** 為替予約テーブルの表示行を組み立てる */
  get exchangeRows() {
    return this._exchangeData.map((row) => ({
      ...row,
      cells: EXCHANGE_HIGHLIGHT_FIELDS.map((f) => ({
        key: `${row.id}-${f}`, field: f, value: row[f],
        cellClass: row[`${f}Class`] || ""
      }))
    }));
  }

  // --- イベントハンドラ ---

  /** セルが編集されたらデータを更新し、変更箇所を色付けする */
  handleInputChange(event) {
    const { id, field } = event.currentTarget?.dataset || event.target?.dataset || {};
    const value = event.target.value;
    if (!id || !field) return;
    this._creditData = applyHighlight(
      this._updateRow(this._creditData, id, field, value),
      this._savedCreditData, CREDIT_HIGHLIGHT_FIELDS
    );
    this._exchangeData = this._updateRow(this._exchangeData, id, field, value);
  }

  /** 保存して色付けを更新する */
  handleSave() { this._save(); }

  /** 初期状態に戻す */
  handleReset() { this._reset(); }

  /** 数値入力部品のエラー処理 */
  numberErrorHandler(event) { console.error("数値入力エラー:", event.detail); }

  // --- プライベートメソッド ---

  /** 指定した行のフィールドを書き換えた新しい配列を返す */
  _updateRow(data, id, field, value) {
    return data.map((row) => (row.id === id ? { ...row, [field]: value } : row));
  }

  /** 初期データから復元し、色付けをリセットする */
  _reset() {
    const cloneAndInit = (data, fields) => [
      deepClone(data),
      initHighlightClasses(data, fields)
    ];
    [this._savedCreditData, this._creditData] =
      cloneAndInit(this._initialCreditData, CREDIT_HIGHLIGHT_FIELDS);
    [this._savedExchangeData, this._exchangeData] =
      cloneAndInit(this._initialExchangeData, EXCHANGE_HIGHLIGHT_FIELDS);
  }

  /** 変更箇所を色付けし、現在のデータを保存済みとして記録する */
  _save() {
    const highlightAndSnapshot = (current, saved, fields) => {
      const highlighted = applyHighlight(current, saved, fields);
      return [highlighted, deepClone(highlighted)];
    };
    [this._creditData, this._savedCreditData] =
      highlightAndSnapshot(this._creditData, this._savedCreditData, CREDIT_HIGHLIGHT_FIELDS);
    [this._exchangeData, this._savedExchangeData] =
      highlightAndSnapshot(this._exchangeData, this._savedExchangeData, EXCHANGE_HIGHLIGHT_FIELDS);
  }
}
