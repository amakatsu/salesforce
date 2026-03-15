/**
 * 与信・保全ツリーデータ定義
 *
 * 与信テーブル(creditTreeData)と保全テーブル(collateralTreeData)の
 * ツリー構造データをサンプル値付きで定義する。
 * 各ノードは表示ラベル・サンプル数値・編集可否フィールドを持つ。
 *
 * ■ ツリー構造:
 *   各ノードは { id, label, 数値フィールド群, editableFields, children } を持つ。
 *   children配列で親子関係を表現し、main.jsの折りたたみ制御で展開/非表示を切り替える。
 *
 * ■ 編集可否マップ(editableFields):
 *   各フィールドのtrue/falseで編集可否を制御する。
 *   プリセット(CREDIT_FULLY_EDITABLE等)を組み合わせて各ノードに適用する。
 *
 * state.jsがこのデータを読み込み、3世代管理の初期値として使用する。
 */

// =====================================================================
// 定数: デフォルト値・上限値
// =====================================================================

const MAX_CREDIT_VALUE = 9999999;
const MAX_COLLATERAL_VALUE = 9999999;

const CREDIT_DEFAULTS = {
  dueDateMonth: "", dueDateDay: "", rate: "",
  balance99: MAX_CREDIT_VALUE, principal: MAX_CREDIT_VALUE,
  change: MAX_CREDIT_VALUE, postBalance: MAX_CREDIT_VALUE,
  actualBalance: MAX_CREDIT_VALUE, correction: MAX_CREDIT_VALUE
};

const COLLATERAL_DEFAULTS = {
  regValue: MAX_COLLATERAL_VALUE,
  marketValue: MAX_COLLATERAL_VALUE
};

// =====================================================================
// 定数: 編集可否フィールドマップ
// =====================================================================

/** 与信の全フィールドを読み取り専用にしたベースマップ */
const CREDIT_ALL_READONLY = {
  label: false, dueDateMonth: false, dueDateDay: false,
  rate: false, balance99: false, mark: false,
  principal: false, change: false, postBalance: false,
  actualBalance: false, correction: false
};

/** 保全の全フィールドを読み取り専用にしたベースマップ */
const COLLATERAL_ALL_READONLY = {
  regValue: false, marketValue: false
};

/** 指定フィールドだけをtrueにした与信用編集可否マップを返す */
const enableCreditFields = (fields) =>
  fields.reduce((accumulator, field) => ({ ...accumulator, [field]: true }), { ...CREDIT_ALL_READONLY });

/** 指定フィールドだけをtrueにした保全用編集可否マップを返す */
const enableCollateralFields = (fields) =>
  fields.reduce((accumulator, field) => ({ ...accumulator, [field]: true }), { ...COLLATERAL_ALL_READONLY });

// =====================================================================
// 定数: 編集可否プリセット
// =====================================================================

const CREDIT_FULLY_EDITABLE = enableCreditFields([
  "label", "rate", "balance99", "mark", "principal",
  "change", "postBalance", "actualBalance", "correction"
]);
const CREDIT_CORRECTION_ONLY = enableCreditFields(["correction"]);
const CREDIT_NUMBERS_EDITABLE = enableCreditFields([
  "rate", "balance99", "principal", "change",
  "postBalance", "actualBalance", "correction"
]);
const CREDIT_NUMBERS_AND_MARK = enableCreditFields([
  "rate", "balance99", "mark", "principal", "change",
  "postBalance", "actualBalance", "correction"
]);
const COLLATERAL_FULLY_EDITABLE = enableCollateralFields(["regValue", "marketValue"]);

// =====================================================================
// ノードファクトリ関数
// =====================================================================

/** 与信ノードを生成する。デフォルト値にoverridesをマージし、編集可否マップを付与。 */
const createCreditNode = ({ id, label, overrides = {}, editable, children = [] }) => ({
  ...CREDIT_DEFAULTS, id, label, ...overrides, editableFields: editable, children
});

/** 保全ノードを生成する。デフォルト値に編集可否マップを付与。 */
const createCollateralNode = ({ id, collateralType, editable = COLLATERAL_FULLY_EDITABLE, children = [] }) => ({
  ...COLLATERAL_DEFAULTS, id, collateralType, editableFields: editable, children
});

/** 期日+利率付き与信明細ノードを生成する(子ノードの共通パターン) */
const createCreditDetailNode = (id, label, month, editable = CREDIT_FULLY_EDITABLE, extraOverrides = {}) =>
  createCreditNode({
    id, label, editable,
    overrides: { dueDateMonth: month, dueDateDay: "01", rate: "99.999", ...extraOverrides }
  });

// =====================================================================
// 与信ツリーデータ
// =====================================================================

const creditTreeData = [
  createCreditNode({ id: "root1", label: "限度算入与信合計", overrides: { correction: "" }, editable: enableCreditFields([]) }),

  createCreditNode({ id: "root2", label: "貸付金・割引合計", editable: CREDIT_CORRECTION_ONLY, children: [
    createCreditDetailNode("l21", "貸付金・割引明細１", "03", enableCreditFields(["label", "rate", "balance99", "principal", "change", "postBalance", "actualBalance", "correction"]), { change: -9999999 }),
    createCreditDetailNode("l22", "貸付金・割引明細２", "04"),
    createCreditDetailNode("l23", "貸付金・割引明細３", "05")
  ]}),

  createCreditNode({ id: "root3", label: "内円貨", editable: CREDIT_CORRECTION_ONLY }),

  createCreditNode({ id: "root4", label: "外為与信合計", editable: CREDIT_CORRECTION_ONLY, children: [
    createCreditDetailNode("e43", "指定外Ｌ／Ｃ", "09"),
    createCreditDetailNode("e44", "Ｄ／Ｐ・Ｄ／Ａ・輸出ＯＡ", "10"),
    createCreditDetailNode("e45", "外貨小切手", "11"),
    createCreditDetailNode("e46", "輸出(小計)", "12"),
    createCreditDetailNode("e47", "貸出(輸出)", "01"),
    createCreditDetailNode("e48", "輸入Ｌ／Ｃ", "02"),
    createCreditDetailNode("e49", "ユーザンス", "03"),
    createCreditDetailNode("e410", "Ｌ／Ｇ", "04"),
    createCreditDetailNode("e411", "輸入(小計)", "05"),
    createCreditDetailNode("e412", "貸出(輸入)", "06"),
    createCreditDetailNode("e413", "故障指定Ｌ／Ｃ", "07"),
    createCreditDetailNode("e414", "ユーザンスシフト外貨", "08")
  ]}),

  createCreditNode({ id: "root5", label: "支払承諾合計", editable: CREDIT_CORRECTION_ONLY, children: [
    createCreditDetailNode("s51", "支払承諾合計 子１", "10", enableCreditFields(["label", "mark", "principal", "change", "postBalance", "correction"]), { change: -9999999 }),
    createCreditDetailNode("s52", "支払承諾合計 子２", "11", enableCreditFields(["rate", "balance99", "mark", "actualBalance", "correction"])),
    createCreditDetailNode("s53", "支払承諾・支承・一般", "12"),
    createCreditDetailNode("s54", "支払承諾・支承・一般外為", "01"),
    createCreditDetailNode("s55", "支払承諾・内他行保証支払承諾", "02"),
    createCreditDetailNode("s56", "支払承諾・代理貸付", "03")
  ]}),

  createCreditNode({ id: "root6", label: "私募債", editable: CREDIT_NUMBERS_EDITABLE }),
  createCreditNode({ id: "root16", label: "協保債", editable: CREDIT_NUMBERS_EDITABLE }),
  createCreditNode({ id: "root7", label: "その他一般与信", editable: CREDIT_NUMBERS_EDITABLE }),
  createCreditNode({ id: "root8", label: "限度算入ローン合計", editable: CREDIT_CORRECTION_ONLY }),
  createCreditNode({ id: "root9", label: "内ＨＬ信用分算入", editable: CREDIT_NUMBERS_AND_MARK }),
  createCreditNode({ id: "root10", label: "オンバランス合計", editable: CREDIT_CORRECTION_ONLY }),
  createCreditNode({ id: "root11", label: "オフバランス合計", editable: CREDIT_CORRECTION_ONLY }),

  createCreditNode({ id: "root12", label: "限度不算入与信合計", editable: CREDIT_CORRECTION_ONLY, children: [
    createCreditDetailNode("l121", "限度不算入 子１", "08", enableCreditFields(["balance99", "mark", "principal", "postBalance", "correction"])),
    createCreditDetailNode("l122", "限度不算入 子２", "09", enableCreditFields(["label", "rate", "mark", "change", "actualBalance", "correction"]))
  ]}),

  createCreditNode({ id: "root13", label: "一般与信合計", editable: CREDIT_CORRECTION_ONLY }),

  createCreditNode({ id: "root14", label: "特定与信合計", editable: CREDIT_CORRECTION_ONLY, children: [
    createCreditDetailNode("l141", "特定与信合計 子１", "12", enableCreditFields(["label", "rate", "mark", "principal", "change", "actualBalance", "correction"])),
    createCreditNode({
      id: "l142", label: "特定与信合計 子２",
      overrides: { dueDateMonth: "", dueDateDay: "", rate: "", balance99: "", principal: "", change: "", postBalance: "", actualBalance: "", correction: "" },
      editable: enableCreditFields(["label", "dueDateMonth", "dueDateDay", "rate", "balance99", "mark", "principal", "change", "postBalance", "actualBalance", "correction"])
    })
  ]})
];

// =====================================================================
// 保全ツリーデータ
// =====================================================================

const collateralTreeData = [
  createCollateralNode({ id: "collGeneral", collateralType: "規定担保合計" }),
  createCollateralNode({ id: "collGeneral2", collateralType: "裸与信" }),
  createCollateralNode({ id: "collGeneral3", collateralType: "補正値" }),

  createCollateralNode({ id: "collGeneral4", collateralType: "規定・優良小計", children: [
    createCollateralNode({ id: "cg4_1", collateralType: "規定・優良担保小計" }),
    createCollateralNode({ id: "cg4_2", collateralType: "預金" }),
    createCollateralNode({ id: "cg4_3", collateralType: "電債割引" }),
    createCollateralNode({ id: "cg4_4", collateralType: "電債担保" }),
    createCollateralNode({ id: "cg4_5", collateralType: "有証" }),
    createCollateralNode({ id: "cg4_6", collateralType: "協会保証" }),
    createCollateralNode({ id: "cg4_7", collateralType: "保証(除協会)" }),
    createCollateralNode({ id: "cg4_8", collateralType: "一般Ｌ／Ｃ" }),
    createCollateralNode({ id: "cg4_9", collateralType: "手形保険" }),
    createCollateralNode({ id: "cg4_11", collateralType: "その他" })
  ]}),

  createCollateralNode({ id: "collGenera21", collateralType: "規定・一般小計", children: [
    createCollateralNode({ id: "cg21_1", collateralType: "有証" }),
    createCollateralNode({ id: "cg21_2", collateralType: "保証" }),
    createCollateralNode({ id: "cg21_3", collateralType: "不動産(抵)" }),
    createCollateralNode({ id: "cg21_4", collateralType: "内ＨＬ(抵)" }),
    createCollateralNode({ id: "cg21_5", collateralType: "不動産(根)" }),
    createCollateralNode({ id: "cg21_6", collateralType: "Ｄ／Ｆ保証" }),
    createCollateralNode({ id: "cg21_7", collateralType: "その他" })
  ]}),

  createCollateralNode({ id: "collGenera22", collateralType: "規定・その他担保小計", children: [
    createCollateralNode({ id: "cg22_1", collateralType: "有証" }),
    createCollateralNode({ id: "cg22_2", collateralType: "保証" }),
    createCollateralNode({ id: "cg22_3", collateralType: "ローン保証" }),
    createCollateralNode({ id: "cg22_4", collateralType: "その他" })
  ]}),

  createCollateralNode({ id: "collGenera23", collateralType: "規定外担保合計", children: [] }),

  createCollateralNode({ id: "cg23_1", collateralType: "規定外・優良小計", children: [
    createCollateralNode({ id: "cg23_1_1", collateralType: "預金" }),
    createCollateralNode({ id: "cg23_1_2", collateralType: "有証" }),
    createCollateralNode({ id: "cg23_1_3", collateralType: "保証" }),
    createCollateralNode({ id: "cg23_1_4", collateralType: "その他" })
  ]}),

  createCollateralNode({ id: "cg23_2", collateralType: "規定外・一般小計", children: [
    createCollateralNode({ id: "cg23_2_1", collateralType: "有証" }),
    createCollateralNode({ id: "cg23_2_2", collateralType: "保証" }),
    createCollateralNode({ id: "cg23_2_3", collateralType: "不動産(抵)" }),
    createCollateralNode({ id: "cg23_2_4", collateralType: "不動産(根)" }),
    createCollateralNode({ id: "cg23_2_5", collateralType: "入居保証金" }),
    createCollateralNode({ id: "cg23_2_6", collateralType: "債権" }),
    createCollateralNode({ id: "cg23_2_7", collateralType: "その他" })
  ]}),

  createCollateralNode({ id: "cg23_3", collateralType: "規定外・その他" })
];

// =====================================================================
// ユーティリティ
// =====================================================================

/** ツリーの各ノードにeditableフラグを付与する(editableFields→editable) */
function applyEditableFlags(tree) {
  return tree.map((node) => ({
    ...node,
    editable: node.editableFields || {},
    children: node.children ? applyEditableFlags(node.children) : undefined
  }));
}

/** オブジェクトのディープコピー(JSON経由) */
const deepCopy = (source) => JSON.parse(JSON.stringify(source));

export { creditTreeData, collateralTreeData, applyEditableFlags, deepCopy };
