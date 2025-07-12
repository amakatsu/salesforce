/* =========================================
 * 状態管理サービス
 * ========================================= */
let isInitialized = false;
let source = [];
let initialSource = [];
let originalSource = [];
let expanded = new Set();
let draft = new Map();

/* ---------- サンプル初期データ ---------- */
const componentSource = [
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
  },
  {
    id: "400",
    name: "サポート部",
    status: "Active",
    joinDate: "2019-01-01",
    active: true,
    role: "Dept Head",
    children: [
      {
        id: "410",
        name: "石井 智",
        status: "Active",
        joinDate: "2019-05-01",
        active: true,
        role: "Support L1"
      }
    ]
  },
  {
    id: "500",
    name: "研究部",
    status: "Active",
    joinDate: "2022-04-01",
    active: true,
    role: "Dept Head"
  },
  {
    id: "600",
    name: "マーケティング部",
    status: "Inactive",
    joinDate: "2021-07-01",
    active: false,
    role: "Dept Head"
  }
];

/* ---------- public functions ---------- */
const initializeState = () => {
  if (!isInitialized) {
    source = deepCopy(componentSource);
    initialSource = deepCopy(componentSource);
    originalSource = deepCopy(componentSource);
    isInitialized = true;
  }
};

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

const setState = (newState) => {
  if (newState.source) source = newState.source;
  if (newState.originalSource) originalSource = newState.originalSource;
};

/* ---------- util ---------- */
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

/* ---------- export ---------- */
export const stateService = {
  initializeState,
  resetState,
  getState,
  setState
};
