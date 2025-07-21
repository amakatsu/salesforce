import { LightningElement, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { stateService } from "./editableTreeGridState";

/**
 * 編集可能ツリーグリッドコンポーネント
 * 階層データの表示、展開/折りたたみ、インライン編集、変更追跡機能を提供します
 * 
 * 主要機能:
 * - 階層データのツリー表示
 * - 展開/折りたたみ機能
 * - インライン編集（フィールド別の編集可否制御）
 * - 変更追跡とハイライト表示
 * - ドラフト値の管理
 * - 保存/リセット機能
 */
export default class EditableTreeGrid extends LightningElement {
  /** 表示用のフラット化された行データ */
  @track rows = [];
  
  /** 変更ハイライトの表示フラグ */
  highlightOn = false;
  
  /** エラー状態の管理 */
  @track hasError = false;
  @track errorMessage = '';

  // 定数定義
  static FIELD_TYPES = {
    TEXT: 'text',
    DATE: 'date',
    CHECKBOX: 'checkbox'
  };

  static ICONS = {
    EXPANDED: 'utility:chevrondown',
    COLLAPSED: 'utility:chevronright'
  };

  static CSS_CLASSES = {
    CHANGED_CELL: 'changed-cell',
    INDENT_PREFIX: 'indent-'
  };

  /**
   * ドラフト変更のMapオブジェクトを取得
   * @returns {Map} ドラフト変更のMap
   */
  get draft() {
    try {
      return stateService.getState().draft;
    } catch (error) {
      this.handleError('ドラフトデータの取得に失敗しました', error);
      return new Map();
    }
  }

  /**
   * ドラフト変更があるかどうかを判定
   * @returns {boolean} ドラフト変更の有無
   */
  get hasDraft() {
    return this.draft.size > 0;
  }

  /**
   * ドラフト変更をJSON文字列として取得（デバッグ用）
   * @returns {string} JSON形式のドラフトデータ
   */
  get draftJson() {
    try {
      return JSON.stringify(Object.fromEntries(this.draft), null, 2);
    } catch (error) {
      this.handleError('ドラフトデータのシリアライゼーションに失敗しました', error);
      return '{}';
    }
  }

  /**
   * コンポーネント初期化時の処理
   */
  connectedCallback() {
    try {
      stateService.initializeState();
      this.refreshRows();
    } catch (error) {
      this.handleError('コンポーネントの初期化に失敗しました', error);
    }
  }

  /**
   * 行データを最新状態で更新
   */
  refreshRows() {
    try {
      const state = stateService.getState();
      this.rows = this.flattenTreeData(state.source, this.highlightOn);
    } catch (error) {
      this.handleError('行データの更新に失敗しました', error);
    }
  }

  /* ---------- 保存/リセット処理 ---------- */
  
  /**
   * 変更内容を保存する
   * ドラフト変更をクリアし、変更ハイライトを有効にする
   */
  handleSave() {
    try {
      const draftCount = this.draft.size;
      
      if (draftCount === 0) {
        this.showToast('情報', '保存する変更がありません', 'info');
        return;
      }

      // ドラフトをクリアして変更を確定
      stateService.getState().draft.clear();
      this.highlightOn = true;
      this.refreshRows();
      
      this.showToast('成功', `${draftCount}件の変更を保存しました`, 'success');
    } catch (error) {
      this.handleError('保存処理に失敗しました', error);
    }
  }

  /**
   * 変更内容をリセットして初期状態に戻す
   */
  handleReset() {
    try {
      const draftCount = this.draft.size;
      
      stateService.resetState();
      this.highlightOn = false;
      this.refreshRows();
      
      if (draftCount > 0) {
        this.showToast('情報', `${draftCount}件の変更をリセットしました`, 'info');
      }
    } catch (error) {
      this.handleError('リセット処理に失敗しました', error);
    }
  }

  /* ---------- ツリー展開/編集処理 ---------- */
  
  /**
   * ノードの展開/折りたたみを切り替える
   * @param {Event} e クリックイベント
   */
  handleToggle(e) {
    try {
      const { expanded } = stateService.getState();
      const id = e.currentTarget.dataset.id;
      
      if (!id) {
        throw new Error('ノードIDが見つかりません');
      }

      // 展開状態をトグル
      if (expanded.has(id)) {
        expanded.delete(id);
      } else {
        expanded.add(id);
      }
      
      this.refreshRows();
    } catch (error) {
      this.handleError('展開/折りたたみ処理に失敗しました', error);
    }
  }

  /**
   * セルの値を編集する
   * @param {Event} e 変更イベント
   */
  handleEdit(e) {
    try {
      const id = e.target.dataset.id;
      const field = e.target.dataset.field;
      
      if (!id || !field) {
        throw new Error('編集に必要なデータ属性が見つかりません');
      }

      // 値の取得（チェックボックスとその他で分岐）
      const value = field === "active" 
        ? e.target.checked 
        : e.target.value;

      // 編集可能性の確認
      const row = this.rows.find((r) => r.id === id);
      if (row && row[`${field}Disabled`]) {
        this.showToast('警告', 'このフィールドは編集できません', 'warning');
        return;
      }

      // データの更新
      this.updateNodeData(id, field, value);
      
    } catch (error) {
      this.handleError('編集処理に失敗しました', error);
    }
  }

  /**
   * ノードデータを更新する
   * @param {string} id ノードID
   * @param {string} field フィールド名
   * @param {any} value 新しい値
   */
  updateNodeData(id, field, value) {
    const { source, draft } = stateService.getState();
    
    // ソースデータを更新
    this.updateNodeInTree(source, id, field, value);

    // ドラフトに変更を記録
    const previousDraft = draft.get(id) || {};
    draft.set(id, { ...previousDraft, [field]: value });

    // 行データを再計算
    this.refreshRows();
  }

  /* ---------- ツリー→フラット変換処理 ---------- */
  
  /**
   * ツリー構造のデータをフラットな配列に変換する
   * @param {Array} tree ツリーデータ
   * @param {boolean} highlight 変更をハイライトするかどうか
   * @param {number} level 現在の階層レベル
   * @param {Array} result 結果配列（再帰用）
   * @returns {Array} フラット化された行データ
   */
  flattenTreeData(tree, highlight, level = 0, result = []) {
    if (!Array.isArray(tree)) {
      throw new Error('ツリーデータが配列ではありません');
    }

    const { expanded, originalSource, draft } = stateService.getState();

    tree.forEach((node) => {
      if (!node || !node.id) {
        console.warn('無効なノードデータがスキップされました:', node);
        return;
      }

      try {
        const isExpanded = expanded.has(node.id);
        const originalNode = this.findNodeInTree(originalSource, node.id);
        
        // 変更差分の検出関数
        const getCellClass = (fieldName) => {
          const baseClass = `${EditableTreeGrid.CSS_CLASSES.INDENT_PREFIX}${level}`;
          const changeClass = this.isFieldChanged(node, originalNode, fieldName, highlight, draft)
            ? EditableTreeGrid.CSS_CLASSES.CHANGED_CELL
            : '';
          return `${baseClass} ${changeClass}`.trim();
        };

        // アイコンの決定
        const icon = this.getNodeIcon(node, isExpanded);

        // 編集フラグの取得
        const editableFlags = this.getEditableFlags(node);

        // フラット化されたノードデータを作成
        const flatNode = {
          ...node,
          level,
          hasChildren: Boolean(node.children?.length),
          icon,
          
          // CSS クラス
          nameClass: getCellClass('name'),
          statusClass: getCellClass('status'),
          joinDateClass: getCellClass('joinDate'),
          activeClass: getCellClass('active'),
          roleClass: getCellClass('role'),
          
          // 編集可否フラグ
          ...editableFlags
        };

        result.push(flatNode);

        // 子ノードの処理（展開されている場合のみ）
        if (isExpanded && node.children && node.children.length > 0) {
          this.flattenTreeData(node.children, highlight, level + 1, result);
        }
      } catch (error) {
        console.error(`ノード ${node.id} の処理中にエラーが発生しました:`, error);
      }
    });

    return result;
  }

  /**
   * フィールドが変更されているかどうかを判定
   * @param {Object} currentNode 現在のノード
   * @param {Object} originalNode 元のノード
   * @param {string} fieldName フィールド名
   * @param {boolean} highlight ハイライト有効フラグ
   * @param {Map} draft ドラフト変更
   * @returns {boolean} 変更されている場合true
   */
  isFieldChanged(currentNode, originalNode, fieldName, highlight, draft) {
    return highlight && 
           !draft.has(currentNode.id) && 
           originalNode && 
           originalNode[fieldName] !== currentNode[fieldName];
  }

  /**
   * ノードのアイコンを取得
   * @param {Object} node ノード
   * @param {boolean} isExpanded 展開状態
   * @returns {string} アイコン名
   */
  getNodeIcon(node, isExpanded) {
    if (!node.children || node.children.length === 0) {
      return '';
    }
    return isExpanded 
      ? EditableTreeGrid.ICONS.EXPANDED 
      : EditableTreeGrid.ICONS.COLLAPSED;
  }

  /**
   * 編集可否フラグを取得
   * @param {Object} node ノード
   * @returns {Object} 編集可否フラグのオブジェクト
   */
  getEditableFlags(node) {
    const editable = node.editable || {};
    return {
      nameDisabled: !editable.name,
      statusDisabled: !editable.status,
      joinDateDisabled: !editable.joinDate,
      activeDisabled: !editable.active,
      roleDisabled: !editable.role
    };
  }

  /* ---------- ヘルパーメソッド ---------- */
  
  /**
   * ツリー内の指定されたノードを更新する
   * @param {Array} tree ツリーデータ
   * @param {string} id ノードID
   * @param {string} field フィールド名
   * @param {any} value 新しい値
   * @returns {boolean} 更新に成功した場合true
   */
  updateNodeInTree(tree, id, field, value) {
    if (!Array.isArray(tree)) {
      return false;
    }

    for (const node of tree) {
      if (node.id === id) {
        node[field] = value;
        return true;
      }
      if (node.children && this.updateNodeInTree(node.children, id, field, value)) {
        return true;
      }
    }
    return false;
  }

  /**
   * ツリー内から指定されたIDのノードを検索する
   * @param {Array} tree ツリーデータ
   * @param {string} id 検索するノードID
   * @returns {Object|null} 見つかったノード、見つからない場合はnull
   */
  findNodeInTree(tree, id) {
    if (!Array.isArray(tree)) {
      return null;
    }

    for (const node of tree) {
      if (node.id === id) {
        return node;
      }
      if (node.children) {
        const found = this.findNodeInTree(node.children, id);
        if (found) {
          return found;
        }
      }
    }
    return null;
  }

  /**
   * エラーハンドリング
   * @param {string} message エラーメッセージ
   * @param {Error} error エラーオブジェクト
   */
  handleError(message, error) {
    console.error(message, error);
    this.hasError = true;
    this.errorMessage = message;
    this.showToast('エラー', message, 'error');
  }

  /**
   * トースト通知を表示
   * @param {string} title タイトル
   * @param {string} message メッセージ
   * @param {string} variant バリアント（success, error, warning, info）
   */
  showToast(title, message, variant) {
    const event = new ShowToastEvent({
      title,
      message,
      variant
    });
    this.dispatchEvent(event);
  }
}