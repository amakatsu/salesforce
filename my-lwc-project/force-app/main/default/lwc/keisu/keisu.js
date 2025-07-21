import { LightningElement, track } from "lwc";
import { stateService } from './keisuState';

/**
 * 係数情報管理コンポーネント
 * 与信状況と他行動向の情報を管理するコンポーネント
 */
export default class KeisuComponent extends LightningElement {
  // 表示用データ
  @track creditRows = [];
  @track otherBankRows = [];
  
  // 表示状態管理
  highlightOn = false;
  
  // アコーディオンのアクティブセクション
  activeSections = ["d", "e"];

  // 下書き状態の取得
  get draft() {
    return stateService.getState().draft;
  }

  // コンポーネント初期化
  connectedCallback() {
    this.initializeData();
  }
  
  // データ初期化
  initializeData() {
    stateService.initializeState();
    const state = stateService.getState();
    this.creditRows = this.flattenTreeData(state.creditSource, false);
    this.otherBankRows = this.prepareOtherBankRows(state.otherBankSource, false);
  }

  /**
   * 保存処理
   * 下書きデータをクリアし、変更ハイライトを有効化
   */
  handleSave() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this.refreshDisplayData(true);
  }
  
  /**
   * リセット処理
   * 状態を初期化し、変更ハイライトを無効化
   */
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this.refreshDisplayData(false);
  }
  
  /**
   * 表示データの更新
   * @param {boolean} highlight - 変更ハイライトを有効化するか
   */
  refreshDisplayData(highlight) {
    const state = stateService.getState();
    this.creditRows = this.flattenTreeData(state.creditSource, highlight);
    this.otherBankRows = this.prepareOtherBankRows(state.otherBankSource, highlight);
  }

  /**
   * ツリーノードの展開/折りたたみ処理
   * @param {Event} event - クリックイベント
   */
  handleTreeToggle(event) {
    const { creditSource, otherBankSource, expanded } = stateService.getState();
    const nodeId = event.currentTarget.dataset.id;
    
    // 展開状態の切り替え
    if (expanded.has(nodeId)) {
      expanded.delete(nodeId);
    } else {
      expanded.add(nodeId);
    }
    
    // 表示データの更新
    this.creditRows = this.flattenTreeData(creditSource, this.highlightOn);
    this.otherBankRows = this.prepareOtherBankRows(otherBankSource, this.highlightOn);
  }

  /**
   * フィールド編集処理
   * @param {Event} event - 入力イベント
   */
  handleFieldEdit(event) {
    const nodeId = event.target.dataset.id;
    const fieldName = event.target.dataset.field;
    const newValue = event.target.value;

    // データ更新
    this.updateFieldValue(nodeId, fieldName, newValue);
    
    // 表示データの更新
    this.refreshDisplayData(this.highlightOn);
  }
  
  
  /**
   * フィールド値の更新
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   */
  updateFieldValue(nodeId, fieldName, newValue) {
    const { creditSource, otherBankSource, draft } = stateService.getState();
    
    // データソースの更新
    const updated = this.updateNodeInTree(creditSource, nodeId, fieldName, newValue) ||
                   this.updateNodeInTree(otherBankSource, nodeId, fieldName, newValue) ||
                   this.updateSubRowInBanks(otherBankSource, nodeId, fieldName, newValue);

    if (updated) {
      // 下書きデータの更新
      const previousDraft = draft.get(nodeId) || {};
      draft.set(nodeId, { ...previousDraft, [fieldName]: newValue });
    }
  }

  /**
   * ツリー構造をフラット配列に変換
   * @param {Array} tree - ツリーデータ
   * @param {boolean} shouldHighlight - 変更ハイライトを有効化するか
   * @param {number} level - ネストレベル
   * @param {Array} output - 出力配列
   * @returns {Array} フラット化されたデータ
   */
  flattenTreeData(tree, shouldHighlight, level = 0, output = []) {
    const { expanded, originalCreditSource, draft } = stateService.getState();

    tree.forEach((node) => {
      const originalNode = this.findNodeInTree(originalCreditSource, node.id);
      const flatNode = this.createFlatNode(node, originalNode, shouldHighlight, level, expanded, draft);
      output.push(flatNode);

      // 子ノードの処理
      if (expanded.has(node.id) && node.children) {
        this.flattenTreeData(node.children, shouldHighlight, level + 1, output);
      }
    });
    
    return output;
  }
  
  
  /**
   * フラット表示用ノードを作成
   * @param {Object} node - ノードデータ
   * @param {Object} originalNode - 元のノードデータ
   * @param {boolean} shouldHighlight - ハイライトを有効化するか
   * @param {number} level - ネストレベル
   * @param {Set} expanded - 展開状態
   * @param {Map} draft - 下書きデータ
   * @returns {Object} フラットノード
   */
  createFlatNode(node, originalNode, shouldHighlight, level, expanded, draft) {
    const indentClass = level === 0 ? 'indent-0' : 
                       level === 1 ? 'indent-1' :
                       level === 2 ? 'indent-2' : 'indent-3';
    const editableFlags = node.editable;
    
    return {
      ...node,
      level,
      hasChildren: node.children?.length > 0,
      icon: this.getNodeIcon(node, expanded),
      
      // CSS クラス
      labelClass: `${indentClass} ${this.getChangeClass("label", node, originalNode, shouldHighlight, draft)}`.trim(),
      currentBalanceClass: `${indentClass} ${this.getChangeClass("currentBalance", node, originalNode, shouldHighlight, draft)}`.trim(),
      principalClass: `${indentClass} ${this.getChangeClass("principal", node, originalNode, shouldHighlight, draft)}`.trim(),
      currentRateClass: `${indentClass} ${this.getChangeClass("currentRate", node, originalNode, shouldHighlight, draft)}`.trim(),
      postRateClass: `${indentClass} ${this.getChangeClass("postRate", node, originalNode, shouldHighlight, draft)}`.trim(),
      applyDateClass: `${indentClass} ${this.getChangeClass("applyDate", node, originalNode, shouldHighlight, draft)}`.trim(),
      applyDateTypeClass: `${indentClass} ${this.getChangeClass("applyDateType", node, originalNode, shouldHighlight, draft)}`.trim(),
      
      // 無効化フラグ
      currentBalanceDisabled: !editableFlags.currentBalance,
      principalDisabled: !editableFlags.principal,
      currentRateDisabled: !editableFlags.currentRate,
      postRateDisabled: !editableFlags.postRate,
      applyDateDisabled: !editableFlags.applyDate
    };
  }
  
  /**
   * ノードのアイコンを取得
   * @param {Object} node - ノードデータ
   * @param {Set} expanded - 展開状態
   * @returns {string} アイコン名
   */
  getNodeIcon(node, expanded) {
    if (!node.children || node.children.length === 0) {
      return "";
    }
    return expanded.has(node.id) ? "utility:chevrondown" : "utility:chevronright";
  }
  
  /**
   * 変更ハイライト用のCSSクラスを取得
   * @param {string} fieldName - フィールド名
   * @param {Object} node - 現在のノード
   * @param {Object} originalNode - 元のノード
   * @param {boolean} shouldHighlight - ハイライトを有効化するか
   * @param {Map} draft - 下書きデータ
   * @returns {string} CSSクラス名
   */
  getChangeClass(fieldName, node, originalNode, shouldHighlight, draft) {
    const hasChanged = shouldHighlight && 
                      !draft.has(node.id) && 
                      originalNode && 
                      originalNode[fieldName] !== node[fieldName];
    return hasChanged ? "changed-cell" : "";
  }

  /**
   * ツリー内のノードを更新
   * @param {Array} tree - ツリーデータ
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @returns {boolean} 更新成功したか
   */
  updateNodeInTree(tree, nodeId, fieldName, newValue) {
    for (const node of tree) {
      if (node.id === nodeId) {
        node[fieldName] = newValue;
        return true;
      }
      if (node.children && this.updateNodeInTree(node.children, nodeId, fieldName, newValue)) {
        return true;
      }
    }
    return false;
  }

  /**
   * ツリー内のノードを検索
   * @param {Array} tree - ツリーデータ
   * @param {string} nodeId - ノードID
   * @returns {Object|null} 検索結果またはnull
   */
  findNodeInTree(tree, nodeId) {
    for (const node of tree) {
      if (node.id === nodeId) {
        return node;
      }
      if (node.children) {
        const foundNode = this.findNodeInTree(node.children, nodeId);
        if (foundNode) {
          return foundNode;
        }
      }
    }
    return null;
  }
  
  /**
   * 他行動向データの準備
   * @param {Array} otherBankSource - 他行動向データソース
   * @param {boolean} shouldHighlight - ハイライトを有効化するか
   * @returns {Array} 表示用の他行動向データ
   */
  prepareOtherBankRows(otherBankSource, shouldHighlight) {
    const { draft } = stateService.getState();
    
    return otherBankSource.map(bank => ({
      ...bank,
      currentBalanceClass: this.getChangeClass("currentBalance", bank, null, shouldHighlight, draft),
      subRows: bank.subRows.map((subRow, index) => ({
        ...subRow,
        isFirst: index === 0,
        principalClass: this.getChangeClass("principal", subRow, null, shouldHighlight, draft),
        currentRateClass: this.getChangeClass("currentRate", subRow, null, shouldHighlight, draft),
        postRateClass: this.getChangeClass("postRate", subRow, null, shouldHighlight, draft),
        applyDateClass: this.getChangeClass("applyDate", subRow, null, shouldHighlight, draft)
      }))
    }));
  }

  /**
   * 銀行のサブ行データを更新
   * @param {Array} banks - 銀行データ配列
   * @param {string} nodeId - ノードID
   * @param {string} fieldName - フィールド名
   * @param {*} newValue - 新しい値
   * @returns {boolean} 更新成功したか
   */
  updateSubRowInBanks(banks, nodeId, fieldName, newValue) {
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

  /**
   * 数値入力エラーハンドラー
   * @param {Event} event - エラーイベント
   */
  numberErrorHandler(event) {
    const errorMessage = event.detail.message;
    const fieldName = event.detail.field;
    console.error(`数値入力エラー: ${fieldName} - ${errorMessage}`);
    
    // 必要に応じてユーザーへの通知処理を追加
    // this.showToast('エラー', errorMessage, 'error');
  }
}