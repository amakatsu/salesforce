// 係数コンポーネント用のデータ定義

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
    id: "bank1",
    label: "銀行A",
    currentBalance: "11",
    // 銀行ごとに3つのサブローを持つ構造
    subRows: [
      {
        id: "bank1-1",
        principal: 1.3,
        currentRate: "科目1-1",
        postRate: "1.1",
        applyDate: "1.3"
      },
      {
        id: "bank1-2",
        principal: 1.4,
        currentRate: "科目1-2",
        postRate: "1.2",
        applyDate: "1.4"
      },
      {
        id: "bank1-3",
        principal: 1.5,
        currentRate: "科目1-3",
        postRate: "1.3",
        applyDate: "1.5"
      }
    ]
  },
  {
    id: "bank2",
    label: "銀行B",
    currentBalance: "12",
    subRows: [
      {
        id: "bank2-1",
        principal: 1.6,
        currentRate: "科目2-1",
        postRate: "1.4",
        applyDate: "1.6"
      },
      {
        id: "bank2-2",
        principal: 1.7,
        currentRate: "科目2-2",
        postRate: "1.5",
        applyDate: "1.7"
      },
      {
        id: "bank2-3",
        principal: 1.8,
        currentRate: "科目2-3",
        postRate: "1.6",
        applyDate: "1.8"
      }
    ]
  },
  {
    id: "bank3",
    label: "銀行C",
    currentBalance: "13",
    subRows: [
      {
        id: "bank3-1",
        principal: 1.9,
        currentRate: "科目3-1",
        postRate: "1.7",
        applyDate: "1.9"
      },
      {
        id: "bank3-2",
        principal: 2.0,
        currentRate: "科目3-2",
        postRate: "1.8",
        applyDate: "2.0"
      },
      {
        id: "bank3-3",
        principal: 2.1,
        currentRate: "科目3-3",
        postRate: "1.9",
        applyDate: "2.1"
      }
    ]
  },
  {
    id: "bank4",
    label: "銀行D",
    currentBalance: "14",
    subRows: [
      {
        id: "bank4-1",
        principal: 2.2,
        currentRate: "科目4-1",
        postRate: "2.0",
        applyDate: "2.2"
      },
      {
        id: "bank4-2",
        principal: 2.3,
        currentRate: "科目4-2",
        postRate: "2.1",
        applyDate: "2.3"
      },
      {
        id: "bank4-3",
        principal: 2.4,
        currentRate: "科目4-3",
        postRate: "2.2",
        applyDate: "2.4"
      }
    ]
  },
  {
    id: "bank5",
    label: "銀行E",
    currentBalance: "15",
    subRows: [
      {
        id: "bank5-1",
        principal: 2.5,
        currentRate: "科目5-1",
        postRate: "2.3",
        applyDate: "2.5"
      },
      {
        id: "bank5-2",
        principal: 2.6,
        currentRate: "科目5-2",
        postRate: "2.4",
        applyDate: "2.6"
      },
      {
        id: "bank5-3",
        principal: 2.7,
        currentRate: "科目5-3",
        postRate: "2.5",
        applyDate: "2.7"
      }
    ]
  }
];

// 編集可能フラグの設定
function getEditableFlags() {
  return {
    label: true,
    currentBalance: true,
    principal: true,
    currentRate: true,
    postRate: true,
    applyDate: true
  };
}

// 編集可能フラグを各ノードに付与
function attachEditableFlags(tree) {
  return tree.map((node) => ({
    ...node,
    editable: getEditableFlags(),
    children: node.children ? attachEditableFlags(node.children) : undefined
  }));
}

// ディープコピー関数
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

// データを外部から使用可能にするためのエクスポート
export {
  rawCreditSource,
  rawOtherBankSource,
  attachEditableFlags,
  deepCopy
};