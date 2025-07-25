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
    children: []
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
        correction: 10000
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
        correction: 20000
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
    children: []
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
        correction: 20000
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
        correction: 30000
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
        correction: 30000
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
        correction: 50000
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
    children: []
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
    children: []
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
    children: []
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
    children: []
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
    children: []
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
    children: []
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
    children: []
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
        correction: 50000
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
        correction: 50000
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
    children: []
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
        correction: 50000
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
        correction: ""
      }
    ]
  }
];

// 担保データ生成関数
function generateCollateral(id, collateralType, regValue, prefix, count, hasChildren) {
  const children = hasChildren
    ? Array.from({ length: count }, (_, i) => ({
        id: `${prefix}${i + 1}`,
        collateralType: `${collateralType} 子${i + 1}`,
        regValue: regValue / count,
        marketValue: (regValue / count) * 1.2
      }))
    : [];

  return {
    id,
    collateralType,
    regValue,
    marketValue: regValue * 1.2,
    children
  };
}

// 担保データ
const rawCollateralSource = [
  generateCollateral("collGeneral", "規定担保合計", 8000000, "cg", 1, false),
  generateCollateral("collGeneral2", "裸与信", 8000000, "cg2", 1, false),
  generateCollateral("collGeneral3", "補正値", 8000000, "cg3", 1, false),
  generateCollateral("collGeneral4", "規定・優良小計", 8000000, "cg4", 20, true),
  generateCollateral("collGenera21", "規定・一般小計", 5000000, "co", 20, true),
  generateCollateral("collGenera22", "規定・その他小計", 5000000, "co", 20, true),
  generateCollateral("collGenera23", "規定・一般小計", 5000000, "co", 20, true),
  generateCollateral("collGenera22", "規定外合計", 5000000, "co", 20, false),
  generateCollateral("collGenera23", "規定外・優良小計", 5000000, "co", 20, true),
  generateCollateral("collGenera24", "規定外・一般小計", 5000000, "co", 20, true),
  generateCollateral("collGenera25", "規定外合計", 5000000, "co", 20, true),
  generateCollateral("collGenera26", "規定外・その他", 5000000, "co2", 20, false)
];

// 編集可能フラグの設定
function getEditableFlags(node) {
  const isDept = node.children?.length;

  return {
    label: !isDept,
    dueDate: node.rate !== "Dept Head",
    rate: node.balance99 > 0,
    balance99: true,
    mark: true,
    principal: !node.id.startsWith("200"),
    change: true,
    postBalance: true,
    actualBalance: true,
    correction: true,
    collateralType: true,
    regValue: true,
    marketValue: true
  };
}

// 編集可能フラグを各ノードに付与
function attachEditableFlags(tree) {
  return tree.map((node) => ({
    ...node,
    editable: getEditableFlags(node),
    children: node.children ? attachEditableFlags(node.children) : undefined
  }));
}

// ディープコピー関数
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

// データを外部から使用可能にするためのエクスポート
export {
  rawCreditSource,
  rawCollateralSource,
  generateCollateral,
  attachEditableFlags,
  deepCopy
};