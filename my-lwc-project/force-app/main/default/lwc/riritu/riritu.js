import { LightningElement, track } from "lwc";
import { stateService } from "./state";
import { apiService } from "./apiService";

// ラベル定義（共通化）
const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY_NUMBER: "科目・摘要・稟査番号",
    DUE_DATE: "期日",
    RATE: "利率（%）",
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
  COLLATERAL: "保全状況",
  GUARANTOR: "保証人"
};

const BUTTON_LABELS = {
  SAVE: "保存",
  RESET: "リセット",
  ADD_ROW: "新規行追加",
  DELETE_ROW: "行削除",
  REFRESH: "データ再取得"
};

const MESSAGE_LABELS = {
  SAVE_SUCCESS: "保存が完了しました",
  RESET_SUCCESS: "リセットが完了しました",
  ADD_ROW_SUCCESS: "新規行が追加されました",
  DELETE_ROW_SUCCESS: "行が削除されました",
  REFRESH_SUCCESS: "データが再取得されました",
  DELETE_CONFIRM: "選択した行を削除しますか？",
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
  @track amountUnit = "〇〇〇";
  @track groupNumber = "9";
  @track creditRows = [];
  @track collateralRows = [];
  @track guarantorData = [
    { id: "guarantor_1", name: "保証人1" },
    { id: "guarantor_2", name: "保証人2" },
    { id: "guarantor_3", name: "保証人3" },
    { id: "guarantor_4", name: "保証人4" },
    { id: "guarantor_5", name: "保証人5" }
  ];
  @track selectedCreditRows = new Set();
  @track selectedCollateralRows = new Set();
  @track showToast = false;
  @track toastMessage = "";
  @track toastVariant = "success";

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

  // トースト関連のゲッター
  get toastClass() {
    const baseClass = "slds-notify slds-notify_toast slds-notify_toast-";
    return `${baseClass}${this.toastVariant} slds-theme_${this.toastVariant}`;
  }

  get isSuccessToast() {
    return this.toastVariant === "success";
  }

  get isWarningToast() {
    return this.toastVariant === "warning";
  }

  get isErrorToast() {
    return this.toastVariant === "error";
  }

  async connectedCallback() {
    await this._initializeData();
  }

  /**
   * 保存処理 - HTMLから呼び出し
   * @public
   */
  async handleSave() {
    try {
      const { draft } = stateService.getState();

      if (draft.size === 0) {
        this._showToast("保存する変更がありません", "warning");
        return;
      }

      // API保存処理
      await this._saveDataToAPI();

      stateService.getState().draft.clear();
      this.highlightOn = true;
      this._refreshData();
      this._showToast(MESSAGE_LABELS.SAVE_SUCCESS, "success");
    } catch (error) {
      console.error("保存エラー:", error);
      this._showToast("保存に失敗しました: " + error.message, "error");
    }
  }

  /**
   * リセット処理 - HTMLから呼び出し
   * @public
   */
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this._refreshData();
    this._showToast(MESSAGE_LABELS.RESET_SUCCESS, "success");
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

  /**
   * 新規行追加処理 - HTMLから呼び出し
   * @public
   */
  handleAddCreditRow() {
    const newId = `new_credit_${Date.now()}`;
    const newRow = {
      id: newId,
      label: "",
      dueDate: "",
      rate: "",
      balance99: "",
      principal: "",
      change: "",
      postBalance: "",
      actualBalance: "",
      correction: "",
      children: [],
      editableFields: {
        label: true,
        dueDate: true,
        rate: true,
        balance99: true,
        principal: true,
        change: true,
        postBalance: true,
        actualBalance: true,
        correction: true
      }
    };

    const { creditSource } = stateService.getState();
    creditSource.push(newRow);
    this._refreshData();
    this._showToast(MESSAGE_LABELS.ADD_ROW_SUCCESS, "success");
  }

  /**
   * 新規担保行追加処理 - HTMLから呼び出し
   * @public
   */
  handleAddCollateralRow() {
    const newId = `new_collateral_${Date.now()}`;
    const newRow = {
      id: newId,
      collateralType: "",
      regValue: "",
      marketValue: "",
      children: [],
      editableFields: {
        regValue: true,
        marketValue: true
      }
    };

    const { collateralSource } = stateService.getState();
    collateralSource.push(newRow);
    this._refreshData();
    this._showToast(MESSAGE_LABELS.ADD_ROW_SUCCESS, "success");
  }

  /**
   * 行選択処理 - HTMLから呼び出し
   * @param {Event} event - チェックボックスイベント
   * @public
   */
  handleRowSelection(event) {
    const rowId = event.target.dataset.id;
    const isCredit = event.target.dataset.type === "credit";
    const isChecked = event.target.checked;

    if (isCredit) {
      if (isChecked) {
        this.selectedCreditRows.add(rowId);
      } else {
        this.selectedCreditRows.delete(rowId);
      }
    } else {
      if (isChecked) {
        this.selectedCollateralRows.add(rowId);
      } else {
        this.selectedCollateralRows.delete(rowId);
      }
    }
  }

  /**
   * 選択行削除処理 - HTMLから呼び出し
   * @public
   */
  handleDeleteSelectedRows() {
    if (
      this.selectedCreditRows.size === 0 &&
      this.selectedCollateralRows.size === 0
    ) {
      this._showToast("削除する行を選択してください", "warning");
      return;
    }

    if (confirm(MESSAGE_LABELS.DELETE_CONFIRM)) {
      const { creditSource, collateralSource } = stateService.getState();

      // 与信行削除
      if (this.selectedCreditRows.size > 0) {
        this._deleteRowsFromTree(creditSource, this.selectedCreditRows);
        this.selectedCreditRows.clear();
      }

      // 担保行削除
      if (this.selectedCollateralRows.size > 0) {
        this._deleteRowsFromTree(collateralSource, this.selectedCollateralRows);
        this.selectedCollateralRows.clear();
      }

      this._refreshData();
      this._showToast(MESSAGE_LABELS.DELETE_ROW_SUCCESS, "success");
    }
  }

  /**
   * データ再取得処理 - HTMLから呼び出し
   * @public
   */
  async handleRefreshData() {
    try {
      stateService.resetState();
      this.highlightOn = false;
      this.selectedCreditRows.clear();
      this.selectedCollateralRows.clear();
      await this._initializeData();
      this._showToast(MESSAGE_LABELS.REFRESH_SUCCESS, "success");
    } catch (error) {
      console.error("データ再取得エラー:", error);
      this._showToast("データ再取得に失敗しました: " + error.message, "error");
    }
  }

  /**
   * 与信行全選択/全解除 - HTMLから呼び出し
   * @param {Event} event - チェックボックスイベント
   * @public
   */
  handleSelectAllCredit(event) {
    const isChecked = event.target.checked;
    const checkboxes = this.template.querySelectorAll(
      'lightning-input[data-type="credit"]'
    );

    checkboxes.forEach((checkbox) => {
      checkbox.checked = isChecked;
      const rowId = checkbox.dataset.id;
      if (isChecked) {
        this.selectedCreditRows.add(rowId);
      } else {
        this.selectedCreditRows.delete(rowId);
      }
    });
  }

  /**
   * 担保行全選択/全解除 - HTMLから呼び出し
   * @param {Event} event - チェックボックスイベント
   * @public
   */
  handleSelectAllCollateral(event) {
    const isChecked = event.target.checked;
    const checkboxes = this.template.querySelectorAll(
      'lightning-input[data-type="collateral"]'
    );

    checkboxes.forEach((checkbox) => {
      checkbox.checked = isChecked;
      const rowId = checkbox.dataset.id;
      if (isChecked) {
        this.selectedCollateralRows.add(rowId);
      } else {
        this.selectedCollateralRows.delete(rowId);
      }
    });
  }

  /**
   * トースト閉じる処理 - HTMLから呼び出し
   * @public
   */
  handleCloseToast() {
    this.showToast = false;
  }

  /* =========================================
   * PRIVATE METHODS - 内部処理専用
   * ======================================== */

  /**
   * データ初期化
   * @private
   */
  async _initializeData() {
    try {
      // APIからデータを取得
      const [creditData, collateralData] = await Promise.all([
        this._loadCreditDataFromAPI(),
        this._loadCollateralDataFromAPI()
      ]);

      // ステートサービスに設定
      if (creditData || collateralData) {
        stateService.initializeWithData(creditData, collateralData);
      } else {
        stateService.initializeState();
      }

      const { creditSource, collateralSource } = stateService.getState();
      this.creditRows = this._flattenTree(creditSource, false);
      this.collateralRows = this._flattenTree(collateralSource, false);
    } catch (error) {
      console.error("データ初期化エラー:", error);
      // エラー時はローカルデータで初期化
      stateService.initializeState();
      const { creditSource, collateralSource } = stateService.getState();
      this.creditRows = this._flattenTree(creditSource, false);
      this.collateralRows = this._flattenTree(collateralSource, false);
      this._showToast(
        "データの読み込みに失敗しました。ローカルデータを使用します。",
        "warning"
      );
    }
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
    const allFields = [
      ...FIELD_DEFINITIONS.CREDIT,
      ...FIELD_DEFINITIONS.COLLATERAL
    ];
    const result = {};

    allFields.forEach((field) => {
      const hasChanged = this._hasFieldChanged(
        node,
        originalNode,
        field,
        shouldHighlight,
        draft
      );
      result[`${field}Class`] = `${indentClass} ${
        hasChanged ? "changed-cell" : ""
      }`.trim();
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
   * トースト表示
   * @param {string} message - 表示メッセージ
   * @param {string} variant - バリアント (success, error, warning, info)
   * @private
   */
  _showToast(message, variant = "success") {
    this.toastMessage = message;
    this.toastVariant = variant;
    this.showToast = true;

    // 3秒後に自動で非表示
    setTimeout(() => {
      this.showToast = false;
    }, 3000);
  }

  /**
   * ツリーから行を削除
   * @param {Array} tree - ツリーデータ
   * @param {Set} idsToDelete - 削除するIDのセット
   * @private
   */
  _deleteRowsFromTree(tree, idsToDelete) {
    for (let i = tree.length - 1; i >= 0; i--) {
      const node = tree[i];
      if (idsToDelete.has(node.id)) {
        tree.splice(i, 1);
      } else if (node.children && node.children.length > 0) {
        this._deleteRowsFromTree(node.children, idsToDelete);
      }
    }
  }

  /* =========================================
   * API連携メソッド - 外部APIとの通信
   * ======================================== */

  /**
   * 与信データをAPIから読み込み
   * @returns {Array|null} 与信データまたはnull
   * @private
   */
  async _loadCreditDataFromAPI() {
    try {
      const response = await apiService.getCreditData();
      return response.success ? response.data : response;
    } catch (error) {
      console.error("与信データの読み込み失敗:", error);
      return null;
    }
  }

  /**
   * 担保データをAPIから読み込み
   * @returns {Array|null} 担保データまたはnull
   * @private
   */
  async _loadCollateralDataFromAPI() {
    try {
      const response = await apiService.getCollateralData();
      return response.success ? response.data : response;
    } catch (error) {
      console.error("担保データの読み込み失敗:", error);
      return null;
    }
  }

  /**
   * データをAPIに保存
   * @returns {Promise<void>}
   * @private
   */
  async _saveDataToAPI() {
    const { draft, creditSource, collateralSource } = stateService.getState();
    const creditUpdates = [];
    const collateralUpdates = [];

    // 下書きデータから更新対象を抽出
    for (const [nodeId, changes] of draft) {
      const creditNode = this._findNodeInTree(creditSource, nodeId);
      const collateralNode = this._findNodeInTree(collateralSource, nodeId);

      if (creditNode) {
        creditUpdates.push({ id: nodeId, ...creditNode, ...changes });
      } else if (collateralNode) {
        collateralUpdates.push({ id: nodeId, ...collateralNode, ...changes });
      }
    }

    // API保存実行
    const savePromises = [];

    if (creditUpdates.length > 0) {
      savePromises.push(apiService.updateAllCreditData(creditUpdates));
    }

    if (collateralUpdates.length > 0) {
      savePromises.push(apiService.updateAllCollateralData(collateralUpdates));
    }

    await Promise.all(savePromises);
  }

  /**
   * APIヘルスチェック
   * @returns {Promise<boolean>} API利用可能状態
   * @private
   */
  async _checkAPIHealth() {
    try {
      return await apiService.healthCheck();
    } catch (error) {
      console.error("APIヘルスチェック失敗:", error);
      return false;
    }
  }

  /**
   * 認証処理
   * @param {Object} credentials - 認証情報
   * @returns {Promise<Object>} 認証結果
   * @private
   */
  async _authenticateUser(credentials) {
    try {
      return await apiService.authenticate(credentials);
    } catch (error) {
      console.error("認証失敗:", error);
      throw error;
    }
  }

  /**
   * バッチ更新処理
   * @param {Object} batchData - バッチデータ
   * @returns {Promise<Object>} 更新結果
   * @private
   */
  async _performBatchUpdate(batchData) {
    try {
      return await apiService.batchUpdate(batchData);
    } catch (error) {
      console.error("バッチ更新失敗:", error);
      throw error;
    }
  }
}
