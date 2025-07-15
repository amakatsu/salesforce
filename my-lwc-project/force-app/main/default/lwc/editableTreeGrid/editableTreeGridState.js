/* =========================================
 * editableTreeGrid用状態管理サービス
 * 
 * 機能:
 * - ツリーデータの初期化と管理
 * - 展開状態の管理
 * - ドラフト変更の追跡
 * - データのリセット機能
 * ========================================= */
let isInitialized = false;
let source = [];
let initialSource = [];
let originalSource = [];
let expanded = new Set();
let draft = new Map();

/* ---------- 生データ（editable なし） ---------- */
const rawComponentSource = [
  {
    id: "100",
    name: "開発部",
    status: "Active",
    joinDate: "2018-04-01",
    active: true,
    role: "Dept Head",
    children: [
      {
        id: "110",
        name: "佐藤 太郎",
        status: "Active",
        joinDate: "2020-06-15",
        active: true,
        role: "Backend Eng"
      },
      {
        id: "120",
        name: "田中 花子",
        status: "Inactive",
        joinDate: "2019-09-01",
        active: false,
        role: "QA Lead"
      },
      {
        id: "130",
        name: "鈴木 一郎",
        status: "Active",
        joinDate: "2021-02-01",
        active: true,
        role: "Frontend Eng"
      }
    ]
  },
  {
    id: "200",
    name: "営業部",
    status: "Active",
    joinDate: "2017-04-01",
    active: true,
    role: "Dept Head",
    children: [
      {
        id: "210",
        name: "高橋 彩",
        status: "Active",
        joinDate: "2022-01-10",
        active: true,
        role: "Sales Rep"
      },
      {
        id: "220",
        name: "伊藤 拓",
        status: "Active",
        joinDate: "2023-07-20",
        active: true,
        role: "Sales Rep"
      }
    ]
  },
  {
    id: "300",
    name: "管理部",
    status: "Inactive",
    joinDate: "2016-10-01",
    active: false,
    role: "Dept Head",
    children: [
      {
        id: "310",
        name: "小林 真",
        status: "Inactive",
        joinDate: "2015-12-05",
        active: false,
        role: "HR"
      },
      {
        id: "320",
        name: "山本 恵",
        status: "Active",
        joinDate: "2018-08-18",
        active: true,
        role: "Accountant"
      }
    ]
  }
];

/* ---------- editable フラグを付与 ---------- */
function attachEditableFlags(tree) {
  return tree.map((n) => {
    const isDept = n.children?.length;

    // ルール例（自由に変更可）
    const editable = {
      name: !isDept, // 部門行は名前編集不可
      status: n.role !== "Dept Head", // Dept Head 行はステータス不可
      joinDate: n.active, // inactive 行は日付編集不可
      active: true, // いつでも可
      role: !n.id.startsWith("200") // 営業部 (id 200xx) はロール不可
    };

    return {
      ...n,
      editable,
      children: n.children ? attachEditableFlags(n.children) : undefined
    };
  });
}

/* ---------- public ---------- */
const initializeState = () => {
  if (!isInitialized) {
    const withFlags = attachEditableFlags(rawComponentSource);
    source = deepCopy(withFlags);
    initialSource = deepCopy(withFlags);
    originalSource = deepCopy(withFlags);
    isInitialized = true;
  }
};
/* resetState, getState, setState は変更なし */

const resetState = () => {
  source = deepCopy(initialSource);
  originalSource = deepCopy(initialSource);
  draft.clear();
};
const getState = () => ({
  isInitialized,
  source,
  initialSource,
  originalSource,
  expanded,
  draft
});
const setState = (s) => {
  if (s.source) source = s.source;
  if (s.originalSource) originalSource = s.originalSource;
};
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

export const stateService = { initializeState, resetState, getState, setState };
