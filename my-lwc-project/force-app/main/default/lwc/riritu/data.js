// 利率コンポーネント用のデータ定義

const rawCreditSource = [
  {
    id: "root1",
    label: "限度算入与信合計",
    dueDate: "",
    rate: "",
    balance99: 1000000,
    principal: 5000000,
    change: 100000,
    postBalance: 1100000,
    actualBalance: 1050000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root2",
    label: "貸付金・割合合計",
    dueDate: "",
    rate: "",
    balance99: 200000,
    principal: 1000000,
    change: 50000,
    postBalance: 250000,
    actualBalance: 240000,
    correction: 10000,
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    },
    children: [
      {
        id: "l21",
        label: "貸付金・割合合計 子1",
        dueDate: "2023-03-01",
        rate: "1.3",
        balance99: 300000,
        principal: 1500000,
        change: -50000,
        postBalance: 250000,
        actualBalance: 240000,
        correction: 10000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: true,
          principal: true,
          change: true,
          postBalance: true,
          actualBalance: true,
          correction: true
        }
      },
      {
        id: "l22",
        label: "貸付金・割合合計 子2",
        dueDate: "2023-04-01",
        rate: "1.4",
        balance99: 400000,
        principal: 2000000,
        change: 100000,
        postBalance: 500000,
        actualBalance: 480000,
        correction: 20000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: true,
          mark: true,
          principal: true,
          change: true,
          postBalance: true,
          actualBalance: true,
          correction: true
        }
      }
    ]
  },
  {
    id: "root3",
    label: " (内円貸)",
    dueDate: "",
    rate: "",
    balance99: 500000,
    principal: 2500000,
    change: 150000,
    postBalance: 600000,
    actualBalance: 580000,
    correction: 20000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root4",
    label: "外為与信合計",
    dueDate: "",
    rate: "",
    balance99: 600000,
    principal: 3000000,
    change: 200000,
    postBalance: 750000,
    actualBalance: 720000,
    correction: 30000,
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    },
    children: [
      {
        id: "e41",
        label: "外為与信合計 子1",
        dueDate: "2023-07-01",
        rate: "1.7",
        balance99: 700000,
        principal: 3500000,
        change: -100000,
        postBalance: 650000,
        actualBalance: 630000,
        correction: 20000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: true,
          mark: true,
          principal: false,
          change: true,
          postBalance: false,
          actualBalance: true,
          correction: true
        }
      },
      {
        id: "e42",
        label: "外為与信合計 子2",
        dueDate: "2023-08-01",
        rate: "1.8",
        balance99: 800000,
        principal: 4000000,
        change: 100000,
        postBalance: 900000,
        actualBalance: 880000,
        correction: 30000,
        editableFields: {
          label: false,
          dueDate: false,
          rate: false,
          balance99: true,
          mark: true,
          principal: true,
          change: false,
          postBalance: true,
          actualBalance: false,
          correction: true
        }
      }
    ]
  },
  {
    id: "root5",
    label: "支払承諾合計",
    dueDate: "",
    rate: "",
    balance99: 900000,
    principal: 4500000,
    change: 200000,
    postBalance: 1000000,
    actualBalance: 950000,
    correction: 50000,
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    },
    children: [
      {
        id: "s51",
        label: "支払承諾合計 子1",
        dueDate: "2023-10-01",
        rate: "2.0",
        balance99: 1000000,
        principal: 5000000,
        change: -50000,
        postBalance: 950000,
        actualBalance: 920000,
        correction: 30000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: false,
          balance99: false,
          mark: true,
          principal: true,
          change: true,
          postBalance: true,
          actualBalance: false,
          correction: true
        }
      },
      {
        id: "s52",
        label: "支払承諾合計 子2",
        dueDate: "2023-11-01",
        rate: "2.1",
        balance99: 1100000,
        principal: 5500000,
        change: 100000,
        postBalance: 1200000,
        actualBalance: 1150000,
        correction: 50000,
        editableFields: {
          label: false,
          dueDate: false,
          rate: true,
          balance99: true,
          mark: true,
          principal: false,
          change: false,
          postBalance: false,
          actualBalance: true,
          correction: true
        }
      }
    ]
  },
  {
    id: "root6",
    label: "私募債",
    dueDate: "",
    rate: "",
    balance99: 1200000,
    principal: 6000000,
    change: 150000,
    postBalance: 1350000,
    actualBalance: 1300000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: true,
      balance99: true,
      principal: true,
      change: true,
      postBalance: true,
      actualBalance: true,
      correction: true
    }
  },
  {
    id: "root16",
    label: "協保債",
    dueDate: "",
    rate: "",
    balance99: 1300000,
    principal: 6500000,
    change: 200000,
    postBalance: 1500000,
    actualBalance: 1450000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: true,
      balance99: true,
      principal: true,
      change: true,
      postBalance: true,
      actualBalance: true,
      correction: true
    }
  },
  {
    id: "root7",
    label: "その他一般融資",
    dueDate: "",
    rate: "",
    balance99: 1400000,
    principal: 7000000,
    change: 250000,
    postBalance: 1650000,
    actualBalance: 1600000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: true,
      balance99: true,
      principal: true,
      change: true,
      postBalance: true,
      actualBalance: true,
      correction: true
    }
  },
  {
    id: "root8",
    label: "限度算入ローン合計",
    dueDate: "",
    rate: "",
    balance99: 1500000,
    principal: 7500000,
    change: 300000,
    postBalance: 1800000,
    actualBalance: 1750000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root9",
    label: " 内HL信用不算入",
    dueDate: "",
    rate: "",
    balance99: 1600000,
    principal: 8000000,
    change: 350000,
    postBalance: 1950000,
    actualBalance: 1900000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: true,
      balance99: true,
      mark: true,
      principal: true,
      change: true,
      postBalance: true,
      actualBalance: true,
      correction: true
    }
  },
  {
    id: "root10",
    label: "オンバランス合計",
    dueDate: "",
    rate: "",
    balance99: 1700000,
    principal: 8500000,
    change: 400000,
    postBalance: 2100000,
    actualBalance: 2050000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root11",
    label: "オフバランス合計",
    dueDate: "",
    rate: "",
    balance99: 1800000,
    principal: 9000000,
    change: 450000,
    postBalance: 2250000,
    actualBalance: 2200000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      mark: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root12",
    label: "限度不算入",
    dueDate: "",
    rate: "",
    balance99: 1900000,
    principal: 9500000,
    change: 500000,
    postBalance: 2400000,
    actualBalance: 2350000,
    correction: 50000,
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    },
    children: [
      {
        id: "l121",
        label: "限度不算入 子1",
        dueDate: "2024-08-01",
        rate: "3.0",
        balance99: 2000000,
        principal: 10000000,
        change: 550000,
        postBalance: 2550000,
        actualBalance: 2500000,
        correction: 50000,
        editableFields: {
          label: false,
          dueDate: false,
          rate: false,
          balance99: true,
          mark: true,
          principal: true,
          change: false,
          postBalance: true,
          actualBalance: false,
          correction: true
        }
      },
      {
        id: "l122",
        label: "限度不算入 子2",
        dueDate: "2024-09-01",
        rate: "3.1",
        balance99: 2100000,
        principal: 10500000,
        change: 600000,
        postBalance: 2700000,
        actualBalance: 2650000,
        correction: 50000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: false,
          mark: true,
          principal: false,
          change: true,
          postBalance: false,
          actualBalance: true,
          correction: true
        }
      }
    ]
  },
  {
    id: "root13",
    label: "一般与信合計",
    dueDate: "",
    rate: "",
    balance99: 2200000,
    principal: 11000000,
    change: 650000,
    postBalance: 2850000,
    actualBalance: 2800000,
    correction: 50000,
    children: [],
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    }
  },
  {
    id: "root14",
    label: "特定与信合計",
    dueDate: "",
    rate: "",
    balance99: 2300000,
    principal: 11500000,
    change: 700000,
    postBalance: 3000000,
    actualBalance: 2950000,
    correction: 50000,
    editableFields: {
      label: false,
      dueDate: false,
      rate: false,
      balance99: false,
      principal: false,
      change: false,
      postBalance: false,
      actualBalance: false,
      correction: true
    },
    children: [
      {
        id: "l141",
        label: "特定与信合計 子1",
        dueDate: "2024-12-01",
        rate: "3.4",
        balance99: 2400000,
        principal: 12000000,
        change: 750000,
        postBalance: 3150000,
        actualBalance: 3100000,
        correction: 50000,
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: false,
          mark: true,
          principal: true,
          change: true,
          postBalance: false,
          actualBalance: true,
          correction: true
        }
      },
      {
        id: "l142",
        label: "",
        dueDate: "",
        rate: "",
        balance99: "",
        principal: "",
        change: "",
        postBalance: "",
        actualBalance: "",
        correction: "",
        editableFields: {
          label: true,
          dueDate: false,
          rate: true,
          balance99: true,
          mark: true,
          principal: true,
          change: true,
          postBalance: true,
          actualBalance: true,
          correction: true
        }
      }
    ]
  }
];

// 担保データ（直接定義で簡素化）
const rawCollateralSource = [
  {
    id: "collGeneral",
    collateralType: "規定担保合計",
    regValue: 8000000,
    marketValue: 9600000,
    children: [],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGeneral2",
    collateralType: "裸与信",
    regValue: 8000000,
    marketValue: 9600000,
    children: [],
    editableFields: { regValue: true, marketValue: true }
  },
  {
    id: "collGeneral3",
    collateralType: "補正値",
    regValue: 8000000,
    marketValue: 9600000,
    children: [],
    editableFields: { regValue: true, marketValue: true }
  },
  {
    id: "collGeneral4",
    collateralType: "規定・優良小計",
    regValue: 8000000,
    marketValue: 9600000,
    children: [
      {
        id: "cg4_1",
        collateralType: "規定・優良小計 子1",
        regValue: 4000000,
        marketValue: 4800000,
        editableFields: { regValue: true, marketValue: true }
      },
      {
        id: "cg4_2",
        collateralType: "規定・優良小計 子2",
        regValue: 4000000,
        marketValue: 4800000,
        editableFields: { regValue: true, marketValue: true }
      }
    ],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGenera21",
    collateralType: "規定・一般小計",
    regValue: 5000000,
    marketValue: 6000000,
    children: [
      {
        id: "co_1",
        collateralType: "規定・一般小計 子1",
        regValue: 2500000,
        marketValue: 3000000,
        editableFields: { regValue: true, marketValue: true }
      },
      {
        id: "co_2",
        collateralType: "規定・一般小計 子2",
        regValue: 2500000,
        marketValue: 3000000,
        editableFields: { regValue: true, marketValue: true }
      }
    ],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGenera22",
    collateralType: "規定・その他小計",
    regValue: 5000000,
    marketValue: 6000000,
    children: [],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGenera23",
    collateralType: "規定外合計",
    regValue: 5000000,
    marketValue: 6000000,
    children: [],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGenera24",
    collateralType: "規定外・優良小計",
    regValue: 5000000,
    marketValue: 6000000,
    children: [
      {
        id: "co24_1",
        collateralType: "規定外・優良小計 子1",
        regValue: 2500000,
        marketValue: 3000000,
        editableFields: { regValue: true, marketValue: true }
      },
      {
        id: "co24_2",
        collateralType: "規定外・優良小計 子2",
        regValue: 2500000,
        marketValue: 3000000,
        editableFields: { regValue: true, marketValue: true }
      }
    ],
    editableFields: { regValue: false, marketValue: false }
  },
  {
    id: "collGenera25",
    collateralType: "規定外・一般小計",
    regValue: 5000000,
    marketValue: 6000000,
    children: [],
    editableFields: { regValue: false, marketValue: true }
  },
  {
    id: "collGenera26",
    collateralType: "規定外・その他",
    regValue: 5000000,
    marketValue: 6000000,
    children: [],
    editableFields: { regValue: true, marketValue: false }
  }
];

// 編集可能フラグを各ノードに付与（簡素化）
function attachEditableFlags(tree) {
  return tree.map((node) => ({
    ...node,
    editable: node.editableFields || {},
    children: node.children ? attachEditableFlags(node.children) : undefined
  }));
}

// ディープコピー関数
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

// データを外部から使用可能にするためのエクスポート
export { rawCreditSource, rawCollateralSource, attachEditableFlags, deepCopy };
