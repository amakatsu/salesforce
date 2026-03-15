/**
 * 与信・保全テーブル コンポーネント (C2)
 *
 * 与信状況テーブル(左9列) + 保全状況テーブル(右3列) + 保証人テーブルを表示する。
 * ツリー構造の折りたたみ、セル編集、変更ハイライト、保存/リセットを提供する。
 *
 * ■ 折りたたみの仕組み:
 *   ツリーデータ(data.js)は親子関係を持つネスト配列。
 *   expandedセット(state.js)に含まれる親ノードだけ子を展開し、
 *   _treeToDisplayRows() でフラット行配列に変換してテンプレートに渡す。
 *   ▶/▼クリックでexpandedを切り替え、表示行を再構築する。
 *
 * ■ データ保持の仕組み(3世代管理):
 *   state.jsのStateServiceが current / initial / saved の3世代を保持。
 *   - current: ユーザー編集中のデータ(handleEditで更新)
 *   - initial: 初回ロード時の状態(リセットでここに戻す)
 *   - saved:   最後の保存時の状態(変更ハイライトの比較基準)
 *
 * ファイル構成:
 *   data.js  - 与信/保全のツリーデータ定義(サンプル値・編集可否)
 *   state.js - StateServiceクラス: ツリーの3世代管理(current/initial/saved)
 *   main.js  - 本ファイル: UI制御・表示行構築・ハイライト計算
 */
import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";
import { StateService } from "./state";

// =====================================================================
// 定数: テーブルヘッダ・ラベル
// =====================================================================

const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY_NUMBER: "科目・摘要・禀査番号",
    DUE_DATE: "期日(月/日)", RATE: "利率", BALANCE_99: "99月末残高",
    MARK: "合算", PRINCIPAL: "極度額", CHANGE: "当月増減",
    POST_BALANCE: "本件後残高", ACTUAL_BALANCE: "実勢現在残", CORRECTION: "補正値"
  },
  COLLATERAL: { COLLATERAL_TYPE: "担保種類", REG_VALUE: "規定値", MARKET_VALUE: "時価ベース" },
  GUARANTOR: { GUARANTOR: "保証人" }
};

const LABELS = {
  tableHeaders: TABLE_HEADERS,
  accordion: { CREDIT_STATUS: "与信状況", COLLATERAL: "保全状況(本件後)", GUARANTOR: "保証人" },
  message: {
    SAVE_SUCCESS: "保存が完了しました", RESET_SUCCESS: "リセットが完了しました",
    NAKED_CREDIT_INFO: "限度不算入与信を考慮した権限判定上の裸与信を表示"
  },
  field: {
    RATE: "利率", BALANCE_99: "99月末残高", PRINCIPAL: "極度額",
    CHANGE: "当月増減", POST_BALANCE: "本件後残高",
    ACTUAL_BALANCE: "実勢現在残", CORRECTION: "補正値",
    REG_VALUE: "規定値", MARKET_VALUE: "時価ベース"
  },
  config: { DECIMAL_STEP: "0.01" }
};

// =====================================================================
// 定数: 変更ハイライト
// =====================================================================

/** 変更セルに付与するCSSクラス */
const HIGHLIGHT_CLASS = "changed-cell";

/** インライン編集可能な特定ノードのID(特定与信合計 子２) */
const INLINE_EDITABLE_NODE_ID = "l142";

/** ハイライト対象フィールド一覧 */
const HIGHLIGHT_TARGET_FIELDS = [
  "label", "dueDate", "rate", "balance99", "mark", "collateralType",
  "principal", "change", "postBalance", "actualBalance",
  "regValue", "marketValue", "correction"
];

/** ラベル列・担保種類列はインデント付き表示 */
const INDENT_TARGET_FIELDS = new Set(["label", "collateralType"]);

// =====================================================================
// ツリー操作ユーティリティ
// =====================================================================

/** IDで深さ優先探索。親→子の順に再帰。 */
function findNodeById(tree, nodeId) {
  for (const node of tree) {
    if (node.id === nodeId) return node;
    if (node.children) {
      const found = findNodeById(node.children, nodeId);
      if (found) return found;
    }
  }
  return null;
}

/** ノードのフィールド値をin-place更新。見つかったらtrue。 */
function updateNodeField(tree, nodeId, field, value) {
  for (const node of tree) {
    if (node.id === nodeId) { node[field] = value; return true; }
    if (node.children && updateNodeField(node.children, nodeId, field, value)) return true;
  }
  return false;
}

// =====================================================================
// コンポーネントクラス
// =====================================================================

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoC2 extends LightningElement {

  // --- @api ---

  /** 親から呼ばれる: 保存後ハイライト適用 */
  @api applySavedHighlight() {
    this._rebuildDisplayRows();
    this._state.saveSnapshot();
    this._snapshotGuarantor();
  }

  // --- プロパティ ---

  _state = new StateService();
  labels = LABELS;
  collateralMarketValueHeader = TABLE_HEADERS.COLLATERAL.MARKET_VALUE;
  activeSections = "abcdefghijklmnopqr".split("");
  amountUnit = makeTestData("mixedChar", 3);
  groupNumber = makeTestData("numeric", 1);

  creditRows = [];
  collateralRows = [];
  guarantorData = Array.from({ length: 5 }, (_, index) => ({
    id: `guarantor_${index + 1}`, name: makeTestData("mixedChar", 10)
  }));

  _savedGuarantorData = null;
  _lastTheadHeight = 0;
  _lastDataRowHeight = 0;

  // --- ライフサイクル ---

  /** 初回: StateService初期化 → 表示行構築 → 保証人スナップショット */
  connectedCallback() {
    this._state.initialize();
    this._rebuildDisplayRows();
    this._snapshotGuarantor();
    this.guarantorData = this.guarantorData.map((guarantor) => ({
      ...guarantor, cellClass: "slds-text-align_center"
    }));
  }

  /** 毎描画後: stickyヘッダ高さをCSS変数に同期 */
  renderedCallback() { this._syncStickyHeights(); }

  // --- イベントハンドラー ---

  /** 保存ボタン → saved更新+ハイライト適用 */
  handleSave() { this.applySavedHighlight(); }

  /** リセットボタン → initial復元+ハイライト解除 */
  handleReset() {
    this._state.reset();
    this._rebuildDisplayRows();
    this._snapshotGuarantor();
    this.guarantorData = this.guarantorData.map((guarantor) => ({
      ...guarantor, cellClass: "slds-text-align_center"
    }));
  }

  /** ▶/▼クリック → expanded切替 → 表示行再構築(子行の表示/非表示が変わる) */
  handleToggle(event) {
    const { expanded } = this._state.getState();
    const nodeId = event.currentTarget.dataset.id;
    expanded.has(nodeId) ? expanded.delete(nodeId) : expanded.add(nodeId);
    this._rebuildDisplayRows();
  }

  /** セル編集 → currentツリー更新 → 表示行再構築(ハイライト再計算) */
  handleEdit(event) {
    const detail = event.detail || {};
    const nodeId = event.target.dataset.id || detail.id;
    const fieldName = event.target.dataset.field || detail.field;
    const newValue = fieldName === "active"
      ? event.target.checked
      : (detail.value !== undefined ? detail.value : event.target.value);
    if (this._isReadOnly(nodeId, fieldName)) return;
    this._applyFieldChange(nodeId, fieldName, newValue);
    this._rebuildDisplayRows();
  }

  /**
   * 保証人セル編集ハンドラ
   * saved時点の値と比較し、変更があればハイライトCSSクラスを付与する。
   * 配列置換でLWCのリアクティブ更新を発火させる(ミューテーション回避)。
   */
  handleGuarantorInput(event) {
    const nodeId = event.target.dataset.id;
    const newValue = event.target.value;
    const savedGuarantor = this._savedGuarantorData.find((guarantor) => guarantor.id === nodeId);
    if (!savedGuarantor) return;
    const isChanged = savedGuarantor.name !== newValue;
    this.guarantorData = this.guarantorData.map((guarantor) => {
      if (guarantor.id !== nodeId) return guarantor;
      return {
        ...guarantor,
        name: newValue,
        cellClass: `slds-text-align_center${isChanged ? ` ${HIGHLIGHT_CLASS}` : ""}`
      };
    });
  }

  /** 数値入力コンポーネントのエラーハンドラ */
  handleNumberInputError(event) { console.log("数値入力エラー:", event.detail); }

  // --- 折りたたみ制御: ツリー→表示行変換 ---

  /**
   * currentツリーから表示行を再構築する。
   * 全ての編集/トグル/保存/リセット操作の最後に呼ばれ、
   * creditRows/collateralRowsを更新してテンプレートを再描画する。
   */
  _rebuildDisplayRows() {
    const { creditSource, collateralSource } = this._state.getState();
    this.creditRows = this._treeToDisplayRows(creditSource, 0, true);
    this.collateralRows = this._treeToDisplayRows(collateralSource, 0, false);
  }

  /**
   * ツリーを再帰走査し、expandedセットに含まれるノードの子だけを展開した
   * フラット行配列を生成する。折りたたまれた子ノードは配列に含まれない。
   */
  _treeToDisplayRows(tree, level = 0, isCredit = true) {
    const { expanded } = this._state.getState();
    return tree.flatMap((node) => {
      const row = this._buildDisplayRow(node, level, isCredit);
      const childRows = expanded.has(node.id) && node.children?.length
        ? this._treeToDisplayRows(node.children, level + 1, isCredit)
        : [];
      return [row, ...childRows];
    });
  }

  /** 1ノード → テンプレート用フラット行に変換 */
  _buildDisplayRow(node, level, isCredit) {
    const hasChildren = Boolean(node.children?.length);
    const isExpanded = this._state.getState().expanded.has(node.id);
    const fieldStyles = this._computeFieldStyles(node, level);

    return {
      ...node, level, hasChildren,
      isSpecificCredit: node.id === INLINE_EDITABLE_NODE_ID,
      hideMark: level === 0,
      icon: hasChildren ? (isExpanded ? "utility:chevrondown" : "utility:chevronright") : "",
      showCollateralHelp: node.collateralType === "裸与信",
      ...fieldStyles,
      dueDateClass: this._getDueDateHighlight(node),
      dueDateMonthDisabled: level === 0,
      dueDateDayDisabled: level === 0,
      showDueDateSeparator: Boolean(node.dueDateMonth || node.dueDateDay),
      ...this._buildNumberCells(node, fieldStyles, isCredit)
    };
  }

  // --- 変更ハイライト計算 ---

  /**
   * saved vs current を比較し、各フィールドのCSSクラスと編集可否を算出する。
   * 変更があったフィールドにはHIGHLIGHT_CLASSを付与し、視覚的に差分を示す。
   */
  _computeFieldStyles(node, level) {
    const indentClass = level === 0 ? 'tree-indent-root' : 'slds-p-left_small';
    const editable = node.editable || {};
    const savedNode = this._findSavedNode(node.id);
    const result = {};
    for (const field of HIGHLIGHT_TARGET_FIELDS) {
      const changed = savedNode && savedNode[field] !== node[field];
      const base = INDENT_TARGET_FIELDS.has(field) ? indentClass : "";
      const highlight = changed ? HIGHLIGHT_CLASS : "";
      result[`${field}Class`] = `${base} ${highlight}`.trim();
      result[`${field}Disabled`] = !editable[field];
    }
    return result;
  }

  /** 保存済みツリーからノードを検索(与信→保全の順に探索) */
  _findSavedNode(nodeId) {
    const { savedCreditSource, savedCollateralSource } = this._state.getState();
    return findNodeById(savedCreditSource, nodeId) || findNodeById(savedCollateralSource, nodeId);
  }

  /** 期日(月/日)の変更ハイライトを判定 */
  _getDueDateHighlight(node) {
    const savedNode = this._findSavedNode(node.id);
    if (savedNode && (savedNode.dueDateMonth !== node.dueDateMonth || savedNode.dueDateDay !== node.dueDateDay)) {
      return HIGHLIGHT_CLASS;
    }
    return "";
  }

  // --- 数値セル構築 ---

  /** 与信/保全に応じた数値セル配列を構築 */
  _buildNumberCells(node, fieldStyles, isCredit) {
    if (isCredit) {
      return {
        numberCellsBeforeMark: [
          this._buildNumberCell(node, fieldStyles, "rate", LABELS.field.RATE),
          this._buildNumberCell(node, fieldStyles, "balance99", LABELS.field.BALANCE_99)
        ],
        numberCellsAfterMark: [
          this._buildNumberCell(node, fieldStyles, "principal", LABELS.field.PRINCIPAL),
          this._buildNumberCell(node, fieldStyles, "change", LABELS.field.CHANGE),
          this._buildNumberCell(node, fieldStyles, "postBalance", LABELS.field.POST_BALANCE),
          this._buildNumberCell(node, fieldStyles, "actualBalance", LABELS.field.ACTUAL_BALANCE),
          this._buildNumberCell(node, fieldStyles, "correction", LABELS.field.CORRECTION)
        ],
        collateralNumberCells: []
      };
    }
    return {
      numberCellsBeforeMark: [],
      numberCellsAfterMark: [],
      collateralNumberCells: [
        this._buildNumberCell(node, fieldStyles, "regValue", LABELS.field.REG_VALUE),
        this._buildNumberCell(node, fieldStyles, "marketValue", LABELS.field.MARKET_VALUE)
      ]
    };
  }

  /** 1つの数値セルのテンプレートバインディング用オブジェクトを生成 */
  _buildNumberCell(node, fieldStyles, fieldName, label) {
    return {
      key: `${node.id}-${fieldName}`, field: fieldName, label,
      value: node[fieldName],
      disabled: fieldStyles[`${fieldName}Disabled`],
      cellClass: fieldStyles[`${fieldName}Class`]
    };
  }

  // --- データ更新ヘルパー ---

  /** 表示行から編集可否を判定 */
  _isReadOnly(nodeId, fieldName) {
    const row = this.creditRows.find((creditRow) => creditRow.id === nodeId)
      || this.collateralRows.find((collateralRow) => collateralRow.id === nodeId);
    return row?.[`${fieldName}Disabled`];
  }

  /** 与信ツリーで見つかれば保全ツリーの探索をスキップ */
  _applyFieldChange(nodeId, fieldName, newValue) {
    const { creditSource, collateralSource } = this._state.getState();
    if (updateNodeField(creditSource, nodeId, fieldName, newValue)) return;
    updateNodeField(collateralSource, nodeId, fieldName, newValue);
  }

  /** 保証人データのスナップショットを保存(変更ハイライトの比較基準) */
  _snapshotGuarantor() {
    this._savedGuarantorData = this.guarantorData.map((guarantor) => ({ ...guarantor }));
  }

  // --- Stickyヘッダ高さ同期 ---

  /**
   * DOM実測値でCSS変数を更新する。
   * theadとデータ行の高さが変わらなければスキップし、
   * renderedCallbackでの無限ループを防止する。
   */
  _syncStickyHeights() {
    const findStickyElement = (selector) =>
      this.template.querySelector(`.table-container-collateral ${selector}`) ||
      this.template.querySelector(`.table-container-credit ${selector}`);
    const thead = findStickyElement("thead");
    const firstDataRow = findStickyElement("tbody tr");
    if (!thead?.offsetHeight || !firstDataRow?.offsetHeight) return;

    const theadHeight = thead.offsetHeight;
    const dataRowHeight = firstDataRow.offsetHeight;
    if (theadHeight === this._lastTheadHeight && dataRowHeight === this._lastDataRowHeight) return;

    this._lastTheadHeight = theadHeight;
    this._lastDataRowHeight = dataRowHeight;
    const hostStyle = this.template.host.style;
    hostStyle.setProperty("--c2-thead-height", `${theadHeight}px`);
    hostStyle.setProperty("--c2-data-row-height", `${dataRowHeight}px`);
  }

}
