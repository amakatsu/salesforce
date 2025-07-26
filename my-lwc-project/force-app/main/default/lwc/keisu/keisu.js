import { LightningElement, track } from "lwc";
import { stateService } from "./state";

// ラベル定義（共通化）
const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY: '科目・概要',
    CURRENT_BALANCE: '現状残高',
    PRINCIPAL: '極度額',
    CURRENT_RATE: '現状利率（%）',
    POST_RATE: '本件後利率（%）',
    APPLY_DATE: '適用日',
    APPLY_DATE_TYPE: '適用日区分'
  },
  OTHER_BANK: {
    BANK_NAME: '銀行名',
    RAISE_LOWER_MONTH: '引上下月(月)',
    LONG_TERM_RATIO: '長期比率(%)',
    SUBJECT: '科目',
    CURRENT_STATUS: '現状(%)',
    POST_CASE: '本件後(%)'
  }
};

const ACCORDION_LABELS = {
  CREDIT_STATUS: '与信状況',
  OTHER_BANK_TREND: '他行動向'
};

const BUTTON_LABELS = {
  SAVE: '保存',
  RESET: 'リセット'
};

const MESSAGE_LABELS = {
  SAVE_SUCCESS: '保存が完了しました',
  RESET_SUCCESS: 'リセットが完了しました'
};

const ARIA_LABELS = {
  EXPAND_COLLAPSE: '展開/折りたたみ',
  EDIT_FIELD: 'フィールドを編集'
};

// 入力フィールドラベル
const FIELD_LABELS = {
  CURRENT_BALANCE: '現状残高',
  PRINCIPAL: '極度額', 
  CURRENT_RATE: '現状利率',
  POST_RATE: '本件後利率',
  LONG_TERM_RATIO: '長期比率(%)',
  CURRENT_STATUS: '現状(%)',
  POST_CASE: '本件後(%)'
};

// 入力フィールド設定
const FIELD_CONFIG = {
  DECIMAL_STEP: '0.01'
};

// フィールド定義
const FIELD_DEFINITIONS = {
  CREDIT: [
    "label", "currentBalance", "principal", "currentRate", 
    "postRate", "applyDate", "applyDateType"
  ],
  OTHER_BANK: [
    "label", "currentBalance", "principal", "currentRate", 
    "postRate", "applyDate"
  ]
};

/**
 * 係数情報管理コンポーネント
 * 与信状況と他行動向の情報を管理
 */
export default class KeisuComponent extends LightningElement {
  @track creditRows = [];
  @track otherBankRows = [];
  
  highlightOn = false;
  activeSections = ["d", "e"];

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
  handleTreeToggle(event) {
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
    const newValue = event.target.value;

    this._updateNodeData(nodeId, fieldName, newValue);
    this._updateDraft(nodeId, fieldName, newValue);
    this._refreshData();
  }

  /**
   * 数値入力エラーハンドラー - HTMLから呼び出し
   * @param {Event} event - エラーイベント
   * @public
   */
  numberErrorHandler(event) {
    const { message, field } = event.detail;
    console.error(`数値入力エラー: ${field} - ${message}`);
    
    // TODO: ユーザー通知の実装
    // this.showToast('エラー', message, 'error');
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
    const { creditSource, otherBankSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, false);
    this.otherBankRows = this._prepareOtherBankData(otherBankSource, false);
  }

  /**
   * データ更新
   * @private
   */
  _refreshData() {
    const { creditSource, otherBankSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, this.highlightOn);
    this.otherBankRows = this._prepareOtherBankData(otherBankSource, this.highlightOn);
  }

  /**
   * ノードデータ更新
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @private
   */
  _updateNodeData(nodeId, fieldName, newValue) {
    const { creditSource, otherBankSource } = stateService.getState();
    
    const updated = 
      this._updateNodeInTree(creditSource, nodeId, fieldName, newValue) ||
      this._updateNodeInTree(otherBankSource, nodeId, fieldName, newValue) ||
      this._updateSubRowInBanks(otherBankSource, nodeId, fieldName, newValue);

    return updated;
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
    const originalNode = this._findNodeInTree(state.originalCreditSource, node.id);

    return {
      ...node,
      level,
      hasChildren,
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

    FIELD_DEFINITIONS.CREDIT.forEach(field => {
      const hasChanged = this._hasFieldChanged(node, originalNode, field, shouldHighlight, draft);
      result[`${field}Class`] = `${indentClass} ${hasChanged ? 'changed-cell' : ''}`.trim();
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
    return shouldHighlight && 
           !draft.has(node.id) && 
           originalNode && 
           originalNode[field] !== node[field];
  }


  /**
   * 他行動向データの準備
   * @param {Array} otherBankSource - 他行動向データソース
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @returns {Array} 表示用の他行動向データ
   * @private
   */
  _prepareOtherBankData(otherBankSource, shouldHighlight) {
    const { draft } = stateService.getState();

    return otherBankSource.map(bank => ({
      ...bank,
      currentBalanceClass: this._hasFieldChanged(bank, null, "currentBalance", shouldHighlight, draft) ? 'changed-cell' : '',
      subRows: bank.subRows.map((subRow, index) => ({
        ...subRow,
        isFirst: index === 0,
        ...this._generateSubRowClasses(subRow, shouldHighlight, draft)
      }))
    }));
  }

  /**
   * サブ行のクラス生成
   * @param {Object} subRow - サブ行データ
   * @param {boolean} shouldHighlight - ハイライト表示するか
   * @param {Map} draft - 下書きデータ
   * @returns {Object} CSSクラス名のオブジェクト
   * @private
   */
  _generateSubRowClasses(subRow, shouldHighlight, draft) {
    const classes = {};
    const subRowFields = ["principal", "currentRate", "postRate", "applyDate"];

    subRowFields.forEach(field => {
      classes[`${field}Class`] = this._hasFieldChanged(subRow, null, field, shouldHighlight, draft) ? 'changed-cell' : '';
    });

    return classes;
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

  /**
   * 銀行のサブ行データ更新
   * @param {Array} banks - 銀行データ配列
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @returns {boolean} 更新成功したか
   * @private
   */
  _updateSubRowInBanks(banks, nodeId, fieldName, newValue) {
    for (const bank of banks) {
      if (bank.subRows) {
        const subRow = bank.subRows.find(row => row.id === nodeId);
        if (subRow) {
          subRow[fieldName] = newValue;
          return true;
        }
      }
    }
    return false;
  }

}