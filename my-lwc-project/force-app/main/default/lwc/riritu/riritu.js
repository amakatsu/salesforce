import { LightningElement, track } from "lwc";
import { stateService } from "./state";

// ラベル定義（共通化）  
const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY_NUMBER: '科目・摘要・稟査番号',
    DUE_DATE: '期日',
    RATE: '利率（%）',
    BALANCE_99: '99月末残高',
    MARK: '合算',
    PRINCIPAL: '極度額',
    CHANGE: '当月増減',
    POST_BALANCE: '本件後残高',
    ACTUAL_BALANCE: '実勢現在残',
    CORRECTION: '補正値'
  },
  COLLATERAL: {
    COLLATERAL_TYPE: '担保種類',
    REG_VALUE: '規定値',
    MARKET_VALUE: '時価ベース'
  },
  GUARANTOR: {
    GUARANTOR: '保証人'
  }
};

const ACCORDION_LABELS = {
  CREDIT_STATUS: '与信状況',
  COLLATERAL: '本件保全状況',
  GUARANTOR: '保証人'
};

const BUTTON_LABELS = {
  SAVE: '保存',
  RESET: 'リセット'
};

const MESSAGE_LABELS = {
  SAVE_SUCCESS: '保存が完了しました',
  RESET_SUCCESS: 'リセットが完了しました',
  NAKED_CREDIT_INFO: '裸与信は信用限度不参集与信を考慮した権限判定上の裸与信を表示'
};

const ARIA_LABELS = {
  EXPAND_COLLAPSE: '展開/折りたたみ',
  EDIT_FIELD: 'フィールドを編集'
};

// 入力フィールドラベル
const FIELD_LABELS = {
  RATE: '利率',
  BALANCE_99: '99月末残高',
  PRINCIPAL: '極度額',
  CHANGE: '当月増減',
  POST_BALANCE: '本件後残高',
  ACTUAL_BALANCE: '実勢現在残',
  CORRECTION: '補正値',
  REG_VALUE: '規定値',
  MARKET_VALUE: '時価ベース'
};

// 入力フィールド設定
const FIELD_CONFIG = {
  DECIMAL_STEP: '0.01'
};

// フィールド定義
const FIELD_DEFINITIONS = {
  CREDIT: [
    "label", "dueDate", "rate", "balance99", "mark"
  ],
  COLLATERAL: [
    "collateralType", "principal", "change", "postBalance", 
    "actualBalance", "regValue", "marketValue", "correction"
  ]
};

/**
 * 利率情報管理コンポーネント
 * 与信状況と本件保全の情報を管理
 */
export default class RirituComponent extends LightningElement {
  @track creditRows = [];
  @track collateralRows = [];
  @track guarantorData = generateGuarantorData();
  
  highlightOn = false;
  activeSections = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", 
    "k", "l", "m", "n", "o", "p", "q", "r"
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
    
    return (creditRow && creditRow[`${fieldName}Disabled`]) ||
           (collateralRow && collateralRow[`${fieldName}Disabled`]);
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
   * @param {Array} result - 結果配列
   * @returns {Array} フラット化された配列
   * @private
   */
  _flattenTree(tree, shouldHighlight, level = 0, result = []) {
    const { expanded, originalCreditSource, originalCollateralSource, draft } = 
      stateService.getState();

    tree.forEach(node => {
      const originalNode = 
        this._findNodeInTree(originalCreditSource, node.id) ||
        this._findNodeInTree(originalCollateralSource, node.id);

      const flatNode = this._createFlatNode(
        node, originalNode, shouldHighlight, level, expanded, draft
      );
      result.push(flatNode);

      // 子ノードの処理
      if (expanded.has(node.id) && node.children?.length) {
        this._flattenTree(node.children, shouldHighlight, level + 1, result);
      }
    });

    return result;
  }

  /**
   * フラット表示用ノード作成
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {number} level - ネストレベル
   * @param {Set} expanded - 展開状態
   * @param {Map} draft - 下書きデータ
   * @returns {Object} フラット表示用ノード
   * @private
   */
  _createFlatNode(node, originalNode, shouldHighlight, level, expanded, draft) {
    const indentClass = `indent-${Math.min(level, 3)}`;
    const hasChildren = node.children?.length > 0;
    const isExpanded = expanded.has(node.id);

    return {
      ...node,
      level,
      hasChildren,
      icon: hasChildren ? 
        (isExpanded ? "utility:chevrondown" : "utility:chevronright") : "",

      // 全フィールドのクラス生成を統一
      ...this._generateFieldClasses(node, originalNode, shouldHighlight, draft, indentClass),
      
      // 無効化フラグ生成を統一
      ...this._generateDisabledFlags(node)
    };
  }

  /**
   * フィールドクラス生成（統一化）
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {Map} draft - 下書きデータ
   * @param {string} indentClass - インデントクラス
   * @returns {Object} CSSクラス名のオブジェクト
   * @private
   */
  _generateFieldClasses(node, originalNode, shouldHighlight, draft, indentClass) {
    const allFields = [...FIELD_DEFINITIONS.CREDIT, ...FIELD_DEFINITIONS.COLLATERAL];
    const classes = {};

    allFields.forEach(field => {
      const changeClass = this._getChangeClass(
        field, node, originalNode, shouldHighlight, draft
      );
      classes[`${field}Class`] = `${indentClass} ${changeClass}`.trim();
    });

    return classes;
  }

  /**
   * 無効化フラグ生成（統一化）
   * @param {Object} node - ノードデータ
   * @returns {Object} 無効化フラグのオブジェクト
   * @private
   */
  _generateDisabledFlags(node) {
    const allFields = [...FIELD_DEFINITIONS.CREDIT, ...FIELD_DEFINITIONS.COLLATERAL];
    const flags = {};
    const editable = node.editable || {};

    allFields.forEach(field => {
      flags[`${field}Disabled`] = !editable[field];
    });

    return flags;
  }

  /**
   * 変更クラス取得
   * @param {string} fieldName - フィールド名
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {Map} draft - 下書きデータ
   * @returns {string} CSSクラス名
   * @private
   */
  _getChangeClass(fieldName, node, originalNode, shouldHighlight, draft) {
    const hasChanged = shouldHighlight && 
                      !draft.has(node.id) && 
                      originalNode && 
                      originalNode[fieldName] !== node[fieldName];
    return hasChanged ? "changed-cell" : "";
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

/**
 * 保証人データ生成
 * @returns {Array} 保証人データ配列
 */
function generateGuarantorData() {
  return Array.from({ length: 5 }, (_, index) => ({
    id: `guarantor_${index + 1}`,
    name: `保証人${index + 1}`
  }));
}