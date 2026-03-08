import { LightningElement, track, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";
import { stateService } from "./state";

// ラベル定義（共通化）
const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY_NUMBER: "科目・摘要・禀査番号",
    DUE_DATE: "期日",
    RATE: "利率",
    BALANCE_99: "99月末残高",
    MARK: "合算",
    PRINCIPAL: "極度額",
    CHANGE: "当月増減",
    POST_BALANCE: "本件後残高",
    ACTUAL_BALANCE: "実勢現在残",
    CORRECTION: "補正値"
  },
  COLLATERAL: {
    COLLATERAL_TYPE: "担保種類",
    REG_VALUE: "規定値",
    MARKET_VALUE: "時価ベース"
  },
  GUARANTOR: {
    GUARANTOR: "保証人"
  }
};

const ACCORDION_LABELS = {
  CREDIT_STATUS: "与信状況",
  COLLATERAL: "保全状況(本件後)",
  GUARANTOR: "保証人"
};

const MESSAGE_LABELS = {
  SAVE_SUCCESS: "保存が完了しました",
  RESET_SUCCESS: "リセットが完了しました",
  NAKED_CREDIT_INFO: "限度不算入与信を考慮した権限判定上の裸与信を表示"
};

// 入力フィールドラベル
const FIELD_LABELS = {
  RATE: "利率",
  BALANCE_99: "99月末残高",
  PRINCIPAL: "極度額",
  CHANGE: "当月増減",
  POST_BALANCE: "本件後残高",
  ACTUAL_BALANCE: "実勢現在残",
  CORRECTION: "補正値",
  REG_VALUE: "規定値",
  MARKET_VALUE: "時価ベース"
};

// 入力フィールド設定
const FIELD_CONFIG = {
  DECIMAL_STEP: "0.01"
};

// ノードID定数
const EDITABLE_CREDIT_NODE_ID = "l142";
const MARK_HIDDEN_NODE_IDS = new Set(["root1", "root4"]);

// スタイル生成対象フィールド
const STYLE_FIELDS = [
  "label", "dueDate", "rate", "balance99", "mark",
  "collateralType", "principal", "change", "postBalance",
  "actualBalance", "regValue", "marketValue", "correction"
];

/**
 * 利率情報管理コンポーネント
 * 与信状況と本件保全の情報を管理
 */
export default class RirituComponent extends LightningElement {
  @track amountUnit = makeTestData("mixedChar", 3);
  @track groupNumber = makeTestData("numeric", 1);
  @track creditRows = [];
  @track collateralRows = [];
  @track guarantorData = [
    { id: "guarantor_1", name: makeTestData("mixedChar", 10) },
    { id: "guarantor_2", name: makeTestData("mixedChar", 10) },
    { id: "guarantor_3", name: makeTestData("mixedChar", 10) },
    { id: "guarantor_4", name: makeTestData("mixedChar", 10) },
    { id: "guarantor_5", name: makeTestData("mixedChar", 10) }
  ];

  highlightOn = false;
  _originalGuarantorData = null;

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

  /* =========================================
   * PUBLIC METHODS - HTMLから呼び出される
   * ======================================== */

  // ラベル定義をテンプレートで使用可能にする
  get labels() {
    return {
      tableHeaders: TABLE_HEADERS,
      accordion: ACCORDION_LABELS,
      message: MESSAGE_LABELS,
      field: FIELD_LABELS,
      config: FIELD_CONFIG
    };
  }

  // 下書き状態の取得
  get draft() {
    return stateService.getState().draft;
  }

  get hasDraft() {
    return this.draft.size > 0;
  }

  get draftJson() {
    return JSON.stringify(Object.fromEntries(this.draft), null, 2);
  }

  // sticky高さ実測値キャッシュ（無限ループ防止）
  _lastTheadHeight = 0;
  _lastDataRowHeight = 0;

  connectedCallback() {
    this._initializeData();
  }

  renderedCallback() {
    this._updateStickyHeights();
  }

  /**
   * DOM実測値でCSS変数を更新（マジックナンバー廃止）
   * @private
   */
  _updateStickyHeights() {
    const collateralThead = this.template.querySelector(
      ".table-container-collateral thead"
    );
    const creditThead = this.template.querySelector(
      ".table-container-credit thead"
    );
    const thead = collateralThead || creditThead;
    if (!thead || thead.offsetHeight === 0) return;

    const collateralFirstRow = this.template.querySelector(
      ".table-container-collateral tbody tr"
    );
    const creditFirstRow = this.template.querySelector(
      ".table-container-credit tbody tr"
    );
    const firstRow = collateralFirstRow || creditFirstRow;
    if (!firstRow || firstRow.offsetHeight === 0) return;

    const theadHeight = thead.offsetHeight;
    const dataRowHeight = firstRow.offsetHeight;

    if (
      theadHeight === this._lastTheadHeight &&
      dataRowHeight === this._lastDataRowHeight
    ) {
      return;
    }

    this._lastTheadHeight = theadHeight;
    this._lastDataRowHeight = dataRowHeight;

    const hostStyle = this.template.host.style;
    hostStyle.setProperty("--c2-thead-height", theadHeight + "px");
    hostStyle.setProperty("--c2-data-row-height", dataRowHeight + "px");
  }

  /**
   * 保存処理 - HTMLから呼び出し
   * @public
   */
  handleSave() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this._refreshData();
  }

  /**
   * 登録後ハイライト適用 - 親から@api経由で呼び出し
   * @api
   */
  @api
  applySavedHighlight() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this._refreshData();
  }

  /**
   * リセット処理 - HTMLから呼び出し
   * @public
   */
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this._refreshData();
  }

  /**
   * ツリー展開/折りたたみ - HTMLから呼び出し
   * @param {Event} event - クリックイベント
   * @public
   */
  handleToggle(event) {
    const { expanded } = stateService.getState();
    const nodeId = event.currentTarget.dataset.id;
    expanded.has(nodeId) ? expanded.delete(nodeId) : expanded.add(nodeId);
    this._refreshData();
  }

  /**
   * 編集処理 - HTMLから呼び出し
   * @param {Event} event - 入力イベント
   * @public
   */
  handleEdit(event) {
    const nodeId = event.target.dataset.id;
    const fieldName = event.target.dataset.field;
    const newValue =
      fieldName === "active" ? event.target.checked : event.target.value;

    // 編集可能性チェック
    if (this._isFieldDisabled(nodeId, fieldName)) return;

    this._updateNodeData(nodeId, fieldName, newValue);
    this._updateDraft(nodeId, fieldName, newValue);
    this._refreshData();
  }

  /* =========================================
   * PRIVATE METHODS - 内部処理専用
   * ======================================== */

  /**
   * データ初期化
   * @private
   */
  _initializeData() {
    stateService.initializeState();
    const { creditSource, collateralSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, false);
    this.collateralRows = this._flattenTree(collateralSource, false);
    this._originalGuarantorData = this.guarantorData.map((g) => ({ ...g }));
    this.guarantorData = this.guarantorData.map((g) => ({
      ...g,
      cellClass: "slds-text-align_center"
    }));
  }

  /**
   * データ更新
   * @private
   */
  _refreshData() {
    const { creditSource, collateralSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, this.highlightOn);
    this.collateralRows = this._flattenTree(collateralSource, this.highlightOn);
  }

  /**
   * フィールドが無効化されているかチェック
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @returns {boolean} 無効化されているか
   * @private
   */
  _isFieldDisabled(nodeId, fieldName) {
    const creditRow = this.creditRows.find((row) => row.id === nodeId);
    const collateralRow = this.collateralRows.find((row) => row.id === nodeId);
    return (
      (creditRow && creditRow[`${fieldName}Disabled`]) ||
      (collateralRow && collateralRow[`${fieldName}Disabled`])
    );
  }

  /**
   * ノードデータ更新
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @private
   */
  _updateNodeData(nodeId, fieldName, newValue) {
    const { creditSource, collateralSource } = stateService.getState();
    this._updateNodeInTree(creditSource, nodeId, fieldName, newValue);
    this._updateNodeInTree(collateralSource, nodeId, fieldName, newValue);
  }

  /**
   * 下書きデータ更新
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @private
   */
  _updateDraft(nodeId, fieldName, newValue) {
    const { draft } = stateService.getState();
    const originalNode = this._findOriginalNode(nodeId);
    const existingDraft = { ...(draft.get(nodeId) || {}) };

    if (
      originalNode &&
      String(originalNode[fieldName] ?? "") === String(newValue ?? "")
    ) {
      delete existingDraft[fieldName];
      if (Object.keys(existingDraft).length === 0) {
        draft.delete(nodeId);
      } else {
        draft.set(nodeId, existingDraft);
      }
    } else {
      draft.set(nodeId, { ...existingDraft, [fieldName]: newValue });
    }
  }

  /**
   * ツリーをフラット配列に変換
   * @param {Array} tree - ツリーデータ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {number} level - ネストレベル
   * @returns {Array} フラット化された配列
   * @private
   */
  _flattenTree(tree, shouldHighlight, level = 0) {
    return tree.flatMap((node) => {
      const flatNode = this._createFlatNode(node, level, shouldHighlight);
      const children = this._shouldShowChildren(node)
        ? this._flattenTree(node.children, shouldHighlight, level + 1)
        : [];
      return [flatNode, ...children];
    });
  }

  /**
   * フラット表示用ノード作成
   * @param {Object} node - ノードデータ
   * @param {number} level - ネストレベル
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @returns {Object} フラット表示用ノード
   * @private
   */
  _createFlatNode(node, level, shouldHighlight) {
    const state = stateService.getState();
    const hasChildren = Boolean(node.children?.length);
    const isExpanded = state.expanded.has(node.id);
    const originalNode = this._findOriginalNode(node.id);
    const isSpecificCredit = node.id === EDITABLE_CREDIT_NODE_ID;
    const hideMark = MARK_HIDDEN_NODE_IDS.has(node.id);

    return {
      ...node,
      level,
      hasChildren,
      isSpecificCredit,
      hideMark,
      icon: this._getNodeIcon(hasChildren, isExpanded),
      ...this._generateFieldStyles(node, originalNode, shouldHighlight, level)
    };
  }

  /**
   * 子ノードを表示すべきかチェック
   * @param {Object} node - ノードデータ
   * @returns {boolean} 子ノードを表示するか
   * @private
   */
  _shouldShowChildren(node) {
    const { expanded } = stateService.getState();
    return expanded.has(node.id) && node.children?.length > 0;
  }

  /**
   * ノードアイコン取得
   * @param {boolean} hasChildren - 子ノードを持つか
   * @param {boolean} isExpanded - 展開されているか
   * @returns {string} アイコン名
   * @private
   */
  _getNodeIcon(hasChildren, isExpanded) {
    if (!hasChildren) return "";
    return isExpanded ? "utility:chevrondown" : "utility:chevronright";
  }

  /**
   * 元のノードを検索
   * @param {string} nodeId - ノードID
   * @returns {Object|null} 元のノード
   * @private
   */
  _findOriginalNode(nodeId) {
    const { originalCreditSource, originalCollateralSource } =
      stateService.getState();
    return (
      this._findNodeInTree(originalCreditSource, nodeId) ||
      this._findNodeInTree(originalCollateralSource, nodeId)
    );
  }

  /**
   * フィールドスタイル生成
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {number} level - ネストレベル
   * @returns {Object} スタイルとフラグのオブジェクト
   * @private
   */
  _generateFieldStyles(node, originalNode, shouldHighlight, level) {
    const { draft } = stateService.getState();
    const indentClass = `indent-${Math.min(level, 3)}`;
    const editable = node.editable || {};
    const result = {};
    const indentFields = new Set(["label", "collateralType"]);

    const nodeDraft = draft.get(node.id);

    STYLE_FIELDS.forEach((field) => {
      const isSavedChange = this._hasFieldChanged(
        node,
        originalNode,
        field,
        shouldHighlight,
        draft
      );
      const isDraftChange = nodeDraft && field in nodeDraft;

      // 数値系はindentしない（＞開閉で列位置が動かない）
      const baseClass = indentFields.has(field) ? indentClass : "";

      let highlightClass = "";
      if (isSavedChange) {
        highlightClass = "changed-cell cell-changed-saved";
      } else if (isDraftChange) {
        highlightClass = "changed-cell";
      }

      result[`${field}Class`] = `${baseClass} ${highlightClass}`.trim();
      result[`${field}Disabled`] = !editable[field];
    });

    return result;
  }

  /**
   * フィールドが変更されているかチェック
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {string} field - フィールド名
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {Map} draft - 下書きデータ
   * @returns {boolean} 変更されているか
   * @private
   */
  _hasFieldChanged(node, originalNode, field, shouldHighlight, draft) {
    return (
      shouldHighlight &&
      !draft.has(node.id) &&
      originalNode &&
      originalNode[field] !== node[field]
    );
  }

  /**
   * ツリー内ノード更新
   * @param {Array} tree - ツリーデータ
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @returns {boolean} 更新成功したか
   * @private
   */
  _updateNodeInTree(tree, nodeId, fieldName, newValue) {
    for (const node of tree) {
      if (node.id === nodeId) {
        node[fieldName] = newValue;
        return true;
      }
      if (
        node.children &&
        this._updateNodeInTree(node.children, nodeId, fieldName, newValue)
      ) {
        return true;
      }
    }
    return false;
  }

  /**
   * ツリー内ノード検索
   * @param {Array} tree - ツリーデータ
   * @param {string} nodeId - ノードID
   * @returns {Object|null} 見つかったノードまたはnull
   * @private
   */
  _findNodeInTree(tree, nodeId) {
    for (const node of tree) {
      if (node.id === nodeId) return node;
      if (node.children) {
        const found = this._findNodeInTree(node.children, nodeId);
        if (found) return found;
      }
    }
    return null;
  }

  /**
   * 数値入力エラーハンドラ
   * @param {Event} event - エラーイベント
   * @public
   */
  numberErrorHandler(event) {
    console.log("数値入力エラー:", event.detail);
  }

  /**
   * 保証人テーブル入力変更ハンドラ
   * @param {Event} event - 変更イベント
   * @public
   */
  handleInputChange(event) {
    const nodeId = event.target.dataset.id;
    const newValue = event.target.value;
    const guarantor = this.guarantorData.find((g) => g.id === nodeId);
    if (guarantor) {
      guarantor.name = newValue;
      const original = this._originalGuarantorData.find((g) => g.id === nodeId);
      const isChanged = original && original.name !== newValue;
      this.guarantorData = this.guarantorData.map((g) => ({
        ...g,
        cellClass:
          g.id === nodeId
            ? `slds-text-align_center${isChanged ? " changed-cell" : ""}`
            : g.cellClass || "slds-text-align_center"
      }));
    }
  }

  get collateralMarketValueHeader() {
    return TABLE_HEADERS.COLLATERAL.MARKET_VALUE;
  }
}
