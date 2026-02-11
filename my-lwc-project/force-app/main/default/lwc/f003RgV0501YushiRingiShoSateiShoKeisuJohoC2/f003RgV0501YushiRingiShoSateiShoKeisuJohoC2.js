const MAX_CREDIT_VALUE = 9999999;
const MAX_COLLATERAL_VALUE = 9999999;

const CREDIT_DEFAULTS = {
  dueDate: "",
  rate: "",
  balance99: MAX_CREDIT_VALUE,
  principal: MAX_CREDIT_VALUE,
  change: MAX_CREDIT_VALUE,
  postBalance: MAX_CREDIT_VALUE,
  actualBalance: MAX_CREDIT_VALUE,
  correction: MAX_CREDIT_VALUE
};

const COLLATERAL_DEFAULTS = {
  regValue: MAX_COLLATERAL_VALUE,
  marketValue: MAX_COLLATERAL_VALUE
};

const baseCreditEditable = {
  label: false,
  dueDate: false,
  rate: false,
  balance99: false,
  mark: false,
  principal: false,
  change: false,
  postBalance: false,
  actualBalance: false,
  correction: false
};

const baseCollateralEditable = {
  regValue: false,
  marketValue: false
};

const creditEditable = fields =>
  fields.reduce(
    (acc, field) => ({ ...acc, [field]: true }),
    { ...baseCreditEditable }
  );
const collateralEditable = fields =>
  fields.reduce(
    (acc, field) => ({ ...acc, [field]: true }),
    { ...baseCollateralEditable }
  );

const creditNode = ({ id, label, overrides = {}, editableFields, children = [] }) => ({
  ...CREDIT_DEFAULTS,
  id,
  label,
  ...overrides,
  editableFields,
  children
});

const collateralNode = ({
  id,
  collateralType,
  overrides = {},
  editableFields,
  children = []
}) => ({
  ...COLLATERAL_DEFAULTS,
  id,
  collateralType,
  ...overrides,
  editableFields,
  children
});

const rawCreditSource = [
  creditNode({
    id: "root1",
    label: "限度算入与信合計",
    overrides: { correction: "" },
    editableFields: creditEditable([])
  }),
  creditNode({
    id: "root2",
    label: "貸付金・割引合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l21",
        label: "貸付金・割引合計 子1",
        overrides: { dueDate: "03/01", rate: "99.999", change: -9999999 },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l22",
        label: "貸付金・割引合計 子2",
        overrides: { dueDate: "04/01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root3",
    label: " (内円貸)",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root4",
    label: "外為与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "e41",
        label: "外為与信合計 子1",
        overrides: { dueDate: "07/01", rate: "99.999", change: -9999999 },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "change",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e42",
        label: "外為与信合計 子2",
        overrides: { dueDate: "08/01", rate: "99.999" },
        editableFields: creditEditable([
          "balance99",
          "mark",
          "principal",
          "postBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root5",
    label: "支払承諾合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "s51",
        label: "支払承諾合計 子1",
        overrides: { dueDate: "10/01", rate: "99.999", change: -9999999 },
        editableFields: creditEditable([
          "label",
          "mark",
          "principal",
          "change",
          "postBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s52",
        label: "支払承諾合計 子2",
        overrides: { dueDate: "11/01", rate: "99.999" },
        editableFields: creditEditable([
          "rate",
          "balance99",
          "mark",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root6",
    label: "私募債",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root16",
    label: "協保債",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root7",
    label: "その他一般与信",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root8",
    label: "限度算入ローン合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root9",
    label: " 内HL信用不算入",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "mark",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root10",
    label: "オンバランス合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root11",
    label: "オフバランス合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root12",
    label: "限度不算入与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l121",
        label: "限度不算入 子1",
        overrides: { dueDate: "08/01", rate: "99.999" },
        editableFields: creditEditable([
          "balance99",
          "mark",
          "principal",
          "postBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l122",
        label: "限度不算入 子2",
        overrides: { dueDate: "09/01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "mark",
          "change",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root13",
    label: "一般与信合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root14",
    label: "特定与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l141",
        label: "特定与信合計 子1",
        overrides: { dueDate: "12/01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "mark",
          "principal",
          "change",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l142",
        label: "",
        overrides: {
          dueDate: "",
          rate: "",
          balance99: "",
          principal: "",
          change: "",
          postBalance: "",
          actualBalance: "",
          correction: ""
        },
        editableFields: creditEditable([
          "label",
          "dueDate",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  })
];

const rawCollateralSource = [
  collateralNode({
    id: "collGeneral",
    collateralType: "規定担保合計",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral2",
    collateralType: "裸与信",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral3",
    collateralType: "補正値",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral4",
    collateralType: "規定・優良小計",
    editableFields: collateralEditable(["regValue", "marketValue"]),
    children: [
      collateralNode({
        id: "cg4_1",
        collateralType: "規定・優良小計 子1",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_2",
        collateralType: "規定・優良小計 子2",
        editableFields: collateralEditable(["regValue", "marketValue"])
      })
    ]
  }),
  collateralNode({
    id: "collGenera21",
    collateralType: "規定・一般小計",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGenera26",
    collateralType: "規定外・その他",
    overrides: { regValue: 5000000, marketValue: 6000000 },
    editableFields: collateralEditable(["regValue", "marketValue"])
  })
];

// 編集可能フラグを各ノードに付与（簡素化）
function attachEditableFlags(tree) {
  return tree.map(node => ({
    ...node,
    editable: node.editableFields || {},
    children: node.children ? attachEditableFlags(node.children) : undefined
  }));
}

// ディープコピー関数
const deepCopy = obj => JSON.parse(JSON.stringify(obj));

// データを外部から使用可能にするためのエクスポート
export { rawCreditSource, rawCollateralSource, attachEditableFlags, deepCopy };

import { LightningElement, track } from "lwc";
import { makeTestData } from "c/testDataGenerator";
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
  COLLATERAL: "本件保全状況",
  GUARANTOR: "保証人"
};

const BUTTON_LABELS = {
  SAVE: "保存",
  RESET: "リセット"
};

const MESSAGE_LABELS = {
  SAVE_SUCCESS: "保存が完了しました",
  RESET_SUCCESS: "リセットが完了しました",
  NAKED_CREDIT_INFO:
    "裸与信は信用限度不参集与信を考慮した権限判定上の裸与信を表示"
};

const ARIA_LABELS = {
  EXPAND_COLLAPSE: "展開/折りたたみ",
  EDIT_FIELD: "フィールドを編集"
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

// フィールド定義
const FIELD_DEFINITIONS = {
  CREDIT: ["label", "dueDate", "rate", "balance99", "mark"],
  COLLATERAL: [
    "collateralType",
    "principal",
    "change",
    "postBalance",
    "actualBalance",
    "regValue",
    "marketValue",
    "correction"
  ]
};

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
      button: BUTTON_LABELS,
      message: MESSAGE_LABELS,
      aria: ARIA_LABELS,
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
  connectedCallback() {
    this._initializeData();
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
    const newValue = fieldName === "active" ? event.target.checked : event.target.value;
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
    const creditRow = this.creditRows.find(row => row.id === nodeId);
    const collateralRow = this.collateralRows.find(row => row.id === nodeId);
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
    const existingDraft = draft.get(nodeId) || {};
    draft.set(nodeId, { ...existingDraft, [fieldName]: newValue });
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
    return tree.flatMap(node => {
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
    const isSpecificCredit = node.id === "l142";
    return {
      ...node,
      level,
      hasChildren,
      isSpecificCredit,
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
    const { originalCreditSource, originalCollateralSource } = stateService.getState();
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
    const allFields = [...FIELD_DEFINITIONS.CREDIT, ...FIELD_DEFINITIONS.COLLATERAL];
    const result = {};
    allFields.forEach(field => {
      const hasChanged = this._hasFieldChanged(node, originalNode, field, shouldHighlight, draft);
      result[`${field}Class`] = `${indentClass} ${hasChanged ? "changed-cell" : ""}`.trim();
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
    return shouldHighlight && !draft.has(node.id) && originalNode && originalNode[field] !== node[field];
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
      if (node.children && this._updateNodeInTree(node.children, nodeId, fieldName, newValue)) {
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
}
