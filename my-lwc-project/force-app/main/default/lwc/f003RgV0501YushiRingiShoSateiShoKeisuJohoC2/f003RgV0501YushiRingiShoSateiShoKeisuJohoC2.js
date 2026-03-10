import { LightningElement, track, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";
import { stateService } from "./state";

const TABLE_HEADERS = {
  CREDIT: {
    SUBJECT_SUMMARY_NUMBER: "科目・摘要・禀査番号",
    DUE_DATE: "期日(月/日)",
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

const LABELS = {
  tableHeaders: TABLE_HEADERS,
  accordion: {
    CREDIT_STATUS: "与信状況",
    COLLATERAL: "保全状況(本件後)",
    GUARANTOR: "保証人"
  },
  message: {
    SAVE_SUCCESS: "保存が完了しました",
    RESET_SUCCESS: "リセットが完了しました",
    NAKED_CREDIT_INFO: "限度不算入与信を考慮した権限判定上の裸与信を表示"
  },
  field: {
    RATE: "利率",
    BALANCE_99: "99月末残高",
    PRINCIPAL: "極度額",
    CHANGE: "当月増減",
    POST_BALANCE: "本件後残高",
    ACTUAL_BALANCE: "実勢現在残",
    CORRECTION: "補正値",
    REG_VALUE: "規定値",
    MARKET_VALUE: "時価ベース"
  },
  config: {
    DECIMAL_STEP: "0.01"
  }
};

const EDITABLE_CREDIT_NODE_ID = "l142";
const STYLE_FIELDS = [
  "label", "dueDate", "rate", "balance99", "mark",
  "collateralType", "principal", "change", "postBalance",
  "actualBalance", "regValue", "marketValue", "correction"
];
const INDENT_FIELDS = new Set(["label", "collateralType"]);

/** ツリー内ノード検索（再帰） */
function findInTree(tree, nodeId) {
  for (const node of tree) {
    if (node.id === nodeId) return node;
    if (node.children) {
      const found = findInTree(node.children, nodeId);
      if (found) return found;
    }
  }
  return null;
}

/** ツリー内ノード更新（再帰・見つかったらtrue） */
function updateInTree(tree, nodeId, field, value) {
  for (const node of tree) {
    if (node.id === nodeId) { node[field] = value; return true; }
    if (node.children && updateInTree(node.children, nodeId, field, value)) return true;
  }
  return false;
}

export default class RirituComponent extends LightningElement {
  @track amountUnit = makeTestData("mixedChar", 3);
  @track groupNumber = makeTestData("numeric", 1);
  @track creditRows = [];
  @track collateralRows = [];
  @track guarantorData = Array.from({ length: 5 }, (_, i) => ({
    id: `guarantor_${i + 1}`, name: makeTestData("mixedChar", 10)
  }));

  isHighlightActive = false;
  _originalGuarantorData = null;
  activeSections = "abcdefghijklmnopqr".split("");

  // sticky高さ実測値キャッシュ（無限ループ防止）
  _lastTheadHeight = 0;
  _lastDataRowHeight = 0;

  get labels() { return LABELS; }
  get draft() { return stateService.getState().draft; }
  get hasDraft() { return this.draft.size > 0; }
  get draftJson() { return JSON.stringify(Object.fromEntries(this.draft), null, 2); }
  get collateralMarketValueHeader() { return TABLE_HEADERS.COLLATERAL.MARKET_VALUE; }

  connectedCallback() { this._initializeData(); }
  renderedCallback() { this._updateStickyHeights(); }

  /* DOM実測値でCSS変数を更新（マジックナンバー廃止） */
  _updateStickyHeights() {
    const queryTableElement = (selector) =>
      this.template.querySelector(`.table-container-collateral ${selector}`) ||
      this.template.querySelector(`.table-container-credit ${selector}`);
    const thead = queryTableElement("thead");
    const firstRow = queryTableElement("tbody tr");
    if (!thead?.offsetHeight || !firstRow?.offsetHeight) return;

    const theadHeight = thead.offsetHeight;
    const dataRowHeight = firstRow.offsetHeight;
    if (theadHeight === this._lastTheadHeight && dataRowHeight === this._lastDataRowHeight) return;

    this._lastTheadHeight = theadHeight;
    this._lastDataRowHeight = dataRowHeight;
    const hostStyle = this.template.host.style;
    hostStyle.setProperty("--c2-thead-height", `${theadHeight}px`);
    hostStyle.setProperty("--c2-data-row-height", `${dataRowHeight}px`);
  }


  handleSave() { this.applySavedHighlight(); }

  @api
  applySavedHighlight() {
    this.draft.clear();
    this.isHighlightActive = true;
    this._refreshData();
  }

  handleReset() {
    stateService.resetState();
    this.isHighlightActive = false;
    this._refreshData();
  }

  handleToggle(event) {
    const { expanded } = stateService.getState();
    const nodeId = event.currentTarget.dataset.id;
    expanded.has(nodeId) ? expanded.delete(nodeId) : expanded.add(nodeId);
    this._refreshData();
  }

  handleEdit(event) {
    const detail = event.detail || {};
    const nodeId = event.target.dataset.id || detail.id;
    const fieldName = event.target.dataset.field || detail.field;
    const newValue = fieldName === "active"
      ? event.target.checked
      : (detail.value !== undefined ? detail.value : event.target.value);
    if (this._isFieldDisabled(nodeId, fieldName)) return;
    this._updateNodeData(nodeId, fieldName, newValue);
    this._updateDraft(nodeId, fieldName, newValue);
    this._refreshData();
  }

  handleGuarantorInput(event) {
    const nodeId = event.target.dataset.id;
    const newValue = event.target.value;
    const guarantor = this.guarantorData.find((g) => g.id === nodeId);
    if (!guarantor) return;
    guarantor.name = newValue;
    const original = this._originalGuarantorData.find((g) => g.id === nodeId);
    const isChanged = original && original.name !== newValue;
    this.guarantorData = this.guarantorData.map((g) => {
      if (g.id !== nodeId) return { ...g, cellClass: g.cellClass || "slds-text-align_center" };
      return { ...g, cellClass: `slds-text-align_center${isChanged ? " changed-cell" : ""}` };
    });
  }

  numberErrorHandler(event) { console.log("数値入力エラー:", event.detail); }

  _initializeData() {
    stateService.initializeState();
    const { creditSource, collateralSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, false, 0, true);
    this.collateralRows = this._flattenTree(collateralSource, false, 0, false);
    this._originalGuarantorData = this.guarantorData.map((g) => ({ ...g }));
    this.guarantorData = this.guarantorData.map((g) => ({ ...g, cellClass: "slds-text-align_center" }));
  }

  _refreshData() {
    const { creditSource, collateralSource } = stateService.getState();
    this.creditRows = this._flattenTree(creditSource, this.isHighlightActive, 0, true);
    this.collateralRows = this._flattenTree(collateralSource, this.isHighlightActive, 0, false);
  }

  _isFieldDisabled(nodeId, fieldName) {
    const row = [...this.creditRows, ...this.collateralRows].find((r) => r.id === nodeId);
    return row?.[`${fieldName}Disabled`];
  }

  _updateNodeData(nodeId, fieldName, newValue) {
    const { creditSource, collateralSource } = stateService.getState();
    updateInTree(creditSource, nodeId, fieldName, newValue);
    updateInTree(collateralSource, nodeId, fieldName, newValue);
  }

  _updateDraft(nodeId, fieldName, newValue) {
    const { draft } = stateService.getState();
    const originalNode = this._findOriginalNode(nodeId);
    const existing = { ...(draft.get(nodeId) || {}) };
    if (originalNode && String(originalNode[fieldName] ?? "") === String(newValue ?? "")) {
      delete existing[fieldName];
      Object.keys(existing).length === 0 ? draft.delete(nodeId) : draft.set(nodeId, existing);
    } else {
      draft.set(nodeId, { ...existing, [fieldName]: newValue });
    }
  }

  _flattenTree(tree, shouldHighlight, level = 0, isCredit = true) {
    const { expanded } = stateService.getState();
    return tree.flatMap((node, indexInParent) => {
      const flat = this._createFlatNode(node, level, shouldHighlight, indexInParent, isCredit);
      const children = expanded.has(node.id) && node.children?.length
        ? this._flattenTree(node.children, shouldHighlight, level + 1, isCredit)
        : [];
      return [flat, ...children];
    });
  }

  _createFlatNode(node, level, shouldHighlight, indexInParent, isCredit) {
    const hasChildren = Boolean(node.children?.length);
    const isExpanded = stateService.getState().expanded.has(node.id);
    const isTargetCollateral = node.collateralType === "裸与信";
    const fieldStyles = this._generateFieldStyles(node, shouldHighlight, level);
    const editable = node.editable || {};
    const numberCellsBeforeMark = isCredit
      ? [
        this._buildNumberCell(node, fieldStyles, "rate", LABELS.field.RATE),
        this._buildNumberCell(node, fieldStyles, "balance99", LABELS.field.BALANCE_99)
      ]
      : [];
    const numberCellsAfterMark = isCredit
      ? [
        this._buildNumberCell(node, fieldStyles, "principal", LABELS.field.PRINCIPAL),
        this._buildNumberCell(node, fieldStyles, "change", LABELS.field.CHANGE),
        this._buildNumberCell(node, fieldStyles, "postBalance", LABELS.field.POST_BALANCE),
        this._buildNumberCell(node, fieldStyles, "actualBalance", LABELS.field.ACTUAL_BALANCE),
        this._buildNumberCell(node, fieldStyles, "correction", LABELS.field.CORRECTION)
      ]
      : [];
    const collateralNumberCells = !isCredit
      ? [
        this._buildNumberCell(node, fieldStyles, "regValue", LABELS.field.REG_VALUE),
        this._buildNumberCell(node, fieldStyles, "marketValue", LABELS.field.MARKET_VALUE)
      ]
      : [];

    return {
      ...node, level, hasChildren,
      isSpecificCredit: node.id === EDITABLE_CREDIT_NODE_ID,
      hideMark: level === 0,
      icon: hasChildren ? (isExpanded ? "utility:chevrondown" : "utility:chevronright") : "",
      showCollateralHelp: isTargetCollateral,
      ...fieldStyles,
      dueDateClass: this._computeDueDateClass(node, shouldHighlight),
      dueDateMonthDisabled: level === 0,
      dueDateDayDisabled: level === 0,
      showDueDateSeparator: Boolean(node.dueDateMonth || node.dueDateDay),
      numberCellsBeforeMark,
      numberCellsAfterMark,
      collateralNumberCells
    };
  }

  _findOriginalNode(nodeId) {
    const { originalCreditSource, originalCollateralSource } = stateService.getState();
    return findInTree(originalCreditSource, nodeId) || findInTree(originalCollateralSource, nodeId);
  }

  _computeDueDateClass(node, shouldHighlight) {
    const { draft } = stateService.getState();
    const nodeDraft = draft.get(node.id);
    const originalNode = this._findOriginalNode(node.id);
    const isSavedBase = shouldHighlight && !draft.has(node.id) && originalNode;
    const saved = isSavedBase && (
      originalNode.dueDateMonth !== node.dueDateMonth ||
      originalNode.dueDateDay !== node.dueDateDay
    );
    const drafted = nodeDraft && ("dueDateMonth" in nodeDraft || "dueDateDay" in nodeDraft);
    if (saved) return "changed-cell cell-changed-saved";
    if (drafted) return "changed-cell";
    return "";
  }

  _generateFieldStyles(node, shouldHighlight, level) {
    const { draft } = stateService.getState();
    const indentClass = `indent-${Math.min(level, 3)}`;
    const editable = node.editable || {};
    const nodeDraft = draft.get(node.id);
    const originalNode = this._findOriginalNode(node.id);
    const isSavedBase = shouldHighlight && !draft.has(node.id) && originalNode;
    const result = {};
    for (const field of STYLE_FIELDS) {
      const saved = isSavedBase && originalNode[field] !== node[field];
      const drafted = nodeDraft && field in nodeDraft;
      // 数値系はindentしない（開閉で列位置が動かない）
      const base = INDENT_FIELDS.has(field) ? indentClass : "";
      const highlightClass = saved ? "changed-cell cell-changed-saved" : drafted ? "changed-cell" : "";
      result[`${field}Class`] = `${base} ${highlightClass}`.trim();
      result[`${field}Disabled`] = !editable[field];
    }
    return result;
  }

  _buildNumberCell(node, fieldStyles, fieldName, label) {
    return {
      key: `${node.id}-${fieldName}`,
      field: fieldName,
      label,
      value: node[fieldName],
      disabled: fieldStyles[`${fieldName}Disabled`],
      cellClass: fieldStyles[`${fieldName}Class`]
    };
  }
}
