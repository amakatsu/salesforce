/**
 * 与信・保全テーブル (C2)
 *
 * 左に与信状況テーブル(9列)、右に保全状況テーブル(3列) + 保証人テーブルを並べる。
 * ツリーの折りたたみ、セル編集、変更ハイライト、保存/リセットができる。
 *
 * ■ 折りたたみ（▶/▼ボタン）:
 *   HTMLのfor:eachで表示行リスト(displayRows)をループして画面に表示している。
 *   ▶クリック → その親行の子データを表示行リストに追加 → 画面に子行が現れる
 *   ▼クリック → その親行の子データを表示行リストから除去 → 画面から子行が消える
 *   つまり、表示行リストの中身を入れ替えることで開閉を実現している。
 *
 * ■ 3世代データ管理(state.js の StateService):
 *   - current: 今のユーザー編集データ
 *   - initial: 初回ロード時のデータ(リセットで戻る先)
 *   - saved:   最後に保存したデータ(ハイライトの比較基準)
 *
 * ファイル構成:
 *   data.js  - ツリーデータ定義(サンプル値・編集可否)
 *   state.js - StateService: 3世代管理
 *   本ファイル - UI制御・表示行構築・ハイライト計算
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

/** 変更があったセルに付けるCSSクラス名 */
const HIGHLIGHT_CLASS = "changed-cell";

/** インライン編集可能な特定ノードのID(特定与信合計 子２) */
const INLINE_EDITABLE_NODE_ID = "l142";

/** ハイライト対象のフィールド名リスト */
const HIGHLIGHT_TARGET_FIELDS = [
  "label", "dueDate", "rate", "balance99", "mark", "collateralType",
  "principal", "change", "postBalance", "actualBalance",
  "regValue", "marketValue", "correction"
];

/** ツリー階層でインデントを付ける列 */
const INDENT_TARGET_FIELDS = new Set(["label", "collateralType"]);

// =====================================================================
// ツリー操作ユーティリティ
// =====================================================================

/** ツリーからIDが一致するノードを探す(深さ優先) */
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

/** ツリー内のノードを探してフィールド値を直接書き換える。見つかったらtrue */
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

  /** 親から呼ばれる: 保存してハイライトを更新する */
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

  /** 初回マウント: データ初期化 → 表示行を作る → 保証人の初期値を控える */
  connectedCallback() {
    this._state.initialize();
    this._rebuildDisplayRows();
    this._snapshotGuarantor();
    this.guarantorData = this.guarantorData.map((guarantor) => ({
      ...guarantor, cellClass: "slds-text-align_center"
    }));
  }

  /** 描画のたびにtheadの実測高さをCSS変数に反映する */
  renderedCallback() { this._syncStickyHeights(); }

  // --- イベントハンドラー ---

  /** 保存ボタン: 現在値をsavedに控えてハイライトを更新 */
  handleSave() { this.applySavedHighlight(); }

  /** リセットボタン: 初期値に戻してハイライトを消す */
  handleReset() {
    this._state.reset();
    this._rebuildDisplayRows();
    this._snapshotGuarantor();
    this.guarantorData = this.guarantorData.map((guarantor) => ({
      ...guarantor, cellClass: "slds-text-align_center"
    }));
  }

  /** ▶/▼クリック: ツリーの展開/折りたたみを切り替えて行を再構築 */
  handleToggle(event) {
    const { expanded } = this._state.getState();
    const nodeId = event.currentTarget.dataset.id;
    expanded.has(nodeId) ? expanded.delete(nodeId) : expanded.add(nodeId);
    this._rebuildDisplayRows();
  }

  /** セル編集: 値を更新して表示行を再構築(ハイライトも再計算される) */
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
   * 保証人セルの編集: 保存時の値と比べて変更があればハイライトする。
   * 配列を丸ごと置き換えてLWCに再描画させる(直接書き換えだと反映されない)。
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

  /** 数値入力でエラーが起きたときのログ出力 */
  handleNumberInputError(event) { console.log("数値入力エラー:", event.detail); }

  // --- 折りたたみ制御: ツリー→表示行変換 ---

  /**
   * ツリーから表示行を作り直す。
   * 編集・トグル・保存・リセットの最後に毎回呼ばれて画面を更新する。
   */
  _rebuildDisplayRows() {
    const { creditSource, collateralSource } = this._state.getState();
    this.creditRows = this._treeToDisplayRows(creditSource, 0, true);
    this.collateralRows = this._treeToDisplayRows(collateralSource, 0, false);
  }

  /**
   * ツリーを再帰的に辿り、展開中のノードの子だけを開いたフラット行配列を返す。
   * 折りたたまれた子はスキップする。
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

  /** 1つのノードをテンプレートに渡せるフラット行オブジェクトに変換する */
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
   * 保存時と今の値を比べて、変わっていたらハイライト用のCSSクラスを付ける。
   * 各フィールドのCSSクラス名と編集可否をまとめて返す。
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

  /** 保存時のツリーからノードを探す(与信→保全の順) */
  _findSavedNode(nodeId) {
    const { savedCreditSource, savedCollateralSource } = this._state.getState();
    return findNodeById(savedCreditSource, nodeId) || findNodeById(savedCollateralSource, nodeId);
  }

  /** 期日(月/日)が変わっていたらハイライトクラスを返す */
  _getDueDateHighlight(node) {
    const savedNode = this._findSavedNode(node.id);
    if (savedNode && (savedNode.dueDateMonth !== node.dueDateMonth || savedNode.dueDateDay !== node.dueDateDay)) {
      return HIGHLIGHT_CLASS;
    }
    return "";
  }

  // --- 数値セル構築 ---

  /** 与信/保全テーブルに合わせた数値セルの配列を作る */
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

  /** 1つの数値セル分のテンプレート用オブジェクトを作る */
  _buildNumberCell(node, fieldStyles, fieldName, label) {
    return {
      key: `${node.id}-${fieldName}`, field: fieldName, label,
      value: node[fieldName],
      disabled: fieldStyles[`${fieldName}Disabled`],
      cellClass: fieldStyles[`${fieldName}Class`]
    };
  }

  // --- データ更新ヘルパー ---

  /** そのセルが読み取り専用かどうか調べる */
  _isReadOnly(nodeId, fieldName) {
    const row = this.creditRows.find((creditRow) => creditRow.id === nodeId)
      || this.collateralRows.find((collateralRow) => collateralRow.id === nodeId);
    return row?.[`${fieldName}Disabled`];
  }

  /** 与信ツリーで見つかったら保全ツリーは探さない */
  _applyFieldChange(nodeId, fieldName, newValue) {
    const { creditSource, collateralSource } = this._state.getState();
    if (updateNodeField(creditSource, nodeId, fieldName, newValue)) return;
    updateNodeField(collateralSource, nodeId, fieldName, newValue);
  }

  /** 保証人データの今の値を控えておく(ハイライト比較に使う) */
  _snapshotGuarantor() {
    this._savedGuarantorData = this.guarantorData.map((guarantor) => ({ ...guarantor }));
  }

  // --- Stickyヘッダ高さ同期 ---

  /**
   * theadとデータ行の実際の高さを測ってCSS変数を更新する。
   * 高さが前回と同じならスキップする(そうしないとrenderedCallbackが無限ループする)。
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
