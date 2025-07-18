import { LightningElement, track } from "lwc";

let isInitialized = false;
let creditSource = [];
let initialCreditSource = [];
let originalCreditSource = [];
let otherBankSource = [];
let initialOtherBankSource = [];
let originalOtherBankSource = [];
let expanded = new Set();
let draft = new Map();

/* ---------- 生データ（editable なし） ---------- */
const rawCreditSource = [
  {
    id: "root1",
    label: "限度算入与信合計",
    currentBalance: 1000000,
    principal: 5000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root2",
    label: "貸付金・割合合計",
    currentBalance: 200000,
    principal: 1000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: [
      {
        id: "l21",
        label: "貸付金・割合合計 子1",
        currentBalance: 300000,
        principal: 1500000,
        currentRate: "1.3",
        postRate: "1.5",
        applyDate: "2023-03-01",
        applyDateType: "〇〇"
      },
      {
        id: "l22",
        label: "貸付金・割合合計 子2",
        currentBalance: 400000,
        principal: 2000000,
        currentRate: "1.4",
        postRate: "1.6",
        applyDate: "2023-04-01",
        applyDateType: "〇〇"
      }
    ]
  },
  {
    id: "root3",
    label: " (内円貸)",
    currentBalance: 500000,
    principal: 2500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root4",
    label: "外為与信合計",
    currentBalance: 600000,
    principal: 3000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: [
      {
        id: "e41",
        label: "外為与信合計 子1",
        currentBalance: 700000,
        principal: 3500000,
        currentRate: "1.7",
        postRate: "1.9",
        applyDate: "2023-07-01",
        applyDateType: "〇〇"
      },
      {
        id: "e42",
        label: "外為与信合計 子2",
        currentBalance: 800000,
        principal: 4000000,
        currentRate: "1.8",
        postRate: "2.0",
        applyDate: "2023-08-01",
        applyDateType: "〇〇"
      }
    ]
  },
  {
    id: "root5",
    label: "支払承諾合計",
    currentBalance: 900000,
    principal: 4500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: [
      {
        id: "s51",
        label: "支払承諾合計 子1",
        currentBalance: 1000000,
        principal: 5000000,
        currentRate: "2.0",
        postRate: "2.2",
        applyDate: "2023-10-01",
        applyDateType: "〇〇"
      },
      {
        id: "s52",
        label: "支払承諾合計 子2",
        currentBalance: 1100000,
        principal: 5500000,
        currentRate: "2.1",
        postRate: "2.3",
        applyDate: "2023-11-01",
        applyDateType: "〇〇"
      }
    ]
  },
  {
    id: "root6",
    label: "私募債",
    currentBalance: 1200000,
    principal: 6000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root16",
    label: "協保債",
    currentBalance: 1300000,
    principal: 6500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root8",
    label: "限度算入ローン合計",
    currentBalance: 1500000,
    principal: 7500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root10",
    label: "オンバランス合計",
    currentBalance: 1700000,
    principal: 8500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root11",
    label: "オフバランス合計",
    currentBalance: 1800000,
    principal: 9000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  },
  {
    id: "root12",
    label: "限度不算入",
    currentBalance: 1900000,
    principal: 9500000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: [
      {
        id: "l121",
        label: "限度不算入 子1",
        currentBalance: 2000000,
        principal: 10000000,
        currentRate: "3.0",
        postRate: "3.2",
        applyDate: "2024-08-01",
        applyDateType: "〇〇"
      },
      {
        id: "l122",
        label: "限度不算入 子2",
        currentBalance: 2100000,
        principal: 10500000,
        currentRate: "3.1",
        postRate: "3.3",
        applyDate: "2024-09-01",
        applyDateType: "〇〇"
      }
    ]
  },
  {
    id: "root13",
    label: "一般与信合計",
    currentBalance: 2200000,
    principal: 11000000,
    currentRate: "",
    postRate: "",
    applyDate: "",
    applyDateType: "",
    children: []
  }
];

const rawOtherBankSource = [
  {
    id: "bank1-1",
    label: "銀行A",
    currentBalance: "11",
    principal: 1.3,
    currentRate: "科目1-1",
    postRate: "1.1",
    applyDate: "1.3"
  },
  {
    id: "bank1-2",
    label: "銀行B",
    currentBalance: "11",
    principal: 1.3,
    currentRate: "科目1-2",
    postRate: "1.2",
    applyDate: "1.4"
  },
  {
    id: "bank1-3",
    label: "銀行C",
    currentBalance: "11",
    principal: 1.3,
    currentRate: "科目1-3",
    postRate: "1.3",
    applyDate: "1.5"
  },
  {
    id: "bank2-1",
    label: "銀行D",
    currentBalance: "11",
    principal: 1.3,
    currentRate: "科目2-1",
    postRate: "1.4",
    applyDate: "1.6"
  },
  {
    id: "bank2-2",
    label: "銀行E",
    currentBalance: "11",
    principal: 1.3,
    currentRate: "科目2-2",
    postRate: "1.5",
    applyDate: "1.7"
  }
];

/* ---------- editable フラグを付与 ---------- */
function getEditableFlags(node) {
  return {
    label: true,
    currentBalance: true,
    principal: true,
    currentRate: true,
    postRate: true,
    applyDate: true
  };
}

function attachEditableFlags(tree) {
  return tree.map((node) => ({
    ...node,
    editable: getEditableFlags(node),
    children: node.children ? attachEditableFlags(node.children) : undefined
  }));
}

/* ---------- public ---------- */
const initializeState = () => {
  if (!isInitialized) {
    const withCreditFlags = attachEditableFlags(rawCreditSource);
    const withOtherBankFlags = attachEditableFlags(rawOtherBankSource);
    creditSource = deepCopy(withCreditFlags);
    initialCreditSource = deepCopy(withCreditFlags);
    originalCreditSource = deepCopy(withCreditFlags);
    otherBankSource = deepCopy(withOtherBankFlags);
    initialOtherBankSource = deepCopy(withOtherBankFlags);
    originalOtherBankSource = deepCopy(withOtherBankFlags);
    isInitialized = true;
  }
};

const resetState = () => {
  creditSource = deepCopy(initialCreditSource);
  originalCreditSource = deepCopy(initialCreditSource);
  otherBankSource = deepCopy(initialOtherBankSource);
  originalOtherBankSource = deepCopy(initialOtherBankSource);
  draft.clear();
};

const getState = () => ({
  isInitialized,
  creditSource,
  initialCreditSource,
  originalCreditSource,
  otherBankSource,
  initialOtherBankSource,
  originalOtherBankSource,
  expanded,
  draft
});

const setState = (s) => {
  if (s.creditSource) creditSource = s.creditSource;
  if (s.originalCreditSource) originalCreditSource = s.originalCreditSource;
  if (s.otherBankSource) otherBankSource = s.otherBankSource;
  if (s.originalOtherBankSource)
    originalOtherBankSource = s.originalOtherBankSource;
};

const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

export const stateService = { initializeState, resetState, getState, setState };

export default class f003RgV0502RiritsuHenkoRingiShoSateiShoKeisuJohoC1 extends LightningElement {
  @track creditRows = [];
  @track otherBankRows = [];
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
    stateService.initializeState();
    this.creditRows = this.flatten(stateService.getState().creditSource, false);
    this.otherBankRows = this.flatten(
      stateService.getState().otherBankSource,
      false
    );
  }

  /* ---------- SAVE / RESET ---------- */
  handleSave() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this.creditRows = this.flatten(stateService.getState().creditSource, true);
    this.otherBankRows = this.flatten(
      stateService.getState().otherBankSource,
      true
    );
  }
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this.creditRows = this.flatten(stateService.getState().creditSource, false);
    this.otherBankRows = this.flatten(
      stateService.getState().otherBankSource,
      false
    );
  }

  /* ---------- TOGGLE / EDIT ---------- */
  handleToggle(e) {
    const { creditSource, otherBankSource, expanded } = stateService.getState();
    const id = e.currentTarget.dataset.id;
    expanded.has(id) ? expanded.delete(id) : expanded.add(id);
    this.creditRows = this.flatten(creditSource, this.highlightOn);
    this.otherBankRows = this.flatten(otherBankSource, this.highlightOn);
  }

  handleEdit(e) {
    const id = e.target.dataset.id;
    const field = e.target.dataset.field;
    const value = field === "active" ? e.target.checked : e.target.value;

    const creditRow = this.creditRows.find((r) => r.id === id);
    const otherBankRow = this.otherBankRows.find((r) => r.id === id);
    if (creditRow && creditRow[`${field}Disabled`]) return; // 編集不可なら無視
    if (otherBankRow && otherBankRow[`${field}Disabled`]) return; // 編集不可なら無視

    const { creditSource, otherBankSource, draft } = stateService.getState();
    this.updateNode(creditSource, id, field, value); // ソース更新
    this.updateNode(otherBankSource, id, field, value); // ソース更新

    const prev = draft.get(id) || {};
    draft.set(id, { ...prev, [field]: value }); // draft へ

    this.creditRows = this.flatten(creditSource, this.highlightOn);
    this.otherBankRows = this.flatten(otherBankSource, this.highlightOn);
  }

  /* ---------- tree -> flat ---------- */
  flatten(tree, highlight, level = 0, out = []) {
    const { expanded, originalCreditSource, originalOtherBankSource, draft } =
      stateService.getState();

    tree.forEach((node) => {
      const base =
        this.findNode(originalCreditSource, node.id) ||
        this.findNode(originalOtherBankSource, node.id);

      const diff = (k) =>
        highlight && !draft.has(node.id) && base && base[k] !== node[k]
          ? "changed-cell"
          : "";

      const indent = `indent-${level}`;
      const ed = node.editable; // shorthand

      out.push({
        ...node,
        level,
        hasChildren: node.children?.length,
        icon: node.children
          ? expanded.has(node.id)
            ? "utility:chevrondown"
            : "utility:chevronright"
          : "",

        labelClass: `${indent} ${diff("label")}`.trim(),
        currentBalanceClass: `${indent} ${diff("currentBalance")}`.trim(),
        principalClass: `${indent} ${diff("principal")}`.trim(),
        currentRateClass: `${indent} ${diff("currentRate")}`.trim(),
        postRateClass: `${indent} ${diff("postRate")}`.trim(),
        applyDateClass: `${indent} ${diff("applyDate")}`.trim(),

        /* disabled フラグを生成 */
        labelDisabled: !ed.label,
        currentBalanceDisabled: !ed.currentBalance,
        principalDisabled: !ed.principal,
        currentRateDisabled: !ed.currentRate,
        postRateDisabled: !ed.postRate,
        applyDateDisabled: !ed.applyDate
      });

      if (expanded.has(node.id) && node.children)
        this.flatten(node.children, highlight, level + 1, out);
    });
    return out;
  }

  /* ---------- helpers ---------- */
  updateNode(tree, id, field, value) {
    for (const n of tree) {
      if (n.id === id) {
        n[field] = value;
        return;
      }
      if (n.children) this.updateNode(n.children, id, field, value);
    }
  }

  findNode(tree, id) {
    for (const n of tree) {
      if (n.id === id) return n;
      if (n.children) {
        const f = this.findNode(n.children, id);
        if (f) return f;
      }
    }
    return null;
  }
}
