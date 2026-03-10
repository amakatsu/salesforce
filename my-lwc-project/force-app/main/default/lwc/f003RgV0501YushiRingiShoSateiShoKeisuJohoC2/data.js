const MAX_CREDIT_VALUE = 9999999;
const MAX_COLLATERAL_VALUE = 9999999;

const CREDIT_DEFAULTS = {
  dueDateMonth: "",
  dueDateDay: "",
  rate: "",
  balance99: MAX_CREDIT_VALUE,
  principal: MAX_CREDIT_VALUE,
  change: MAX_CREDIT_VALUE,
  postBalance: MAX_CREDIT_VALUE,
  actualBalance: MAX_CREDIT_VALUE,
  correction: MAX_CREDIT_VALUE
};

const COLLATERAL_DEFAULTS = {
  regValue: MAX_COLLATERAL_VALUE,
  marketValue: MAX_COLLATERAL_VALUE
};

const baseCreditEditable = {
  label: false,
  dueDateMonth: false,
  dueDateDay: false,
  rate: false,
  balance99: false,
  mark: false,
  principal: false,
  change: false,
  postBalance: false,
  actualBalance: false,
  correction: false
};

const baseCollateralEditable = {
  regValue: false,
  marketValue: false
};

const creditEditable = (fields) =>
  fields.reduce((acc, field) => ({ ...acc, [field]: true }), {
    ...baseCreditEditable
  });

const collateralEditable = (fields) =>
  fields.reduce((acc, field) => ({ ...acc, [field]: true }), {
    ...baseCollateralEditable
  });

const creditNode = ({
  id,
  label,
  overrides = {},
  editableFields,
  children = []
}) => ({
  ...CREDIT_DEFAULTS,
  id,
  label,
  ...overrides,
  editableFields,
  children
});

const collateralNode = ({
  id,
  collateralType,
  overrides = {},
  editableFields,
  children = []
}) => ({
  ...COLLATERAL_DEFAULTS,
  id,
  collateralType,
  ...overrides,
  editableFields,
  children
});

const rawCreditSource = [
  creditNode({
    id: "root1",
    label: "限度算入与信合計",
    overrides: { correction: "" },
    editableFields: creditEditable([])
  }),
  creditNode({
    id: "root2",
    label: "貸付金・割引合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l21",
        label: "貸付金・割引明細１",
        overrides: { dueDateMonth: "03", dueDateDay: "01", rate: "99.999", change: -9999999 },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l22",
        label: "貸付金・割引明細２",
        overrides: { dueDateMonth: "04", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l23",
        label: "貸付金・割引明細３",
        overrides: { dueDateMonth: "05", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root3",
    label: "内円貨",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root4",
    label: "外為与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "e43",
        label: "指定外Ｌ／Ｃ",
        overrides: { dueDateMonth: "09", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e44",
        label: "Ｄ／Ｐ・Ｄ／Ａ・輸出ＯＡ",
        overrides: { dueDateMonth: "10", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e45",
        label: "外貨小切手",
        overrides: { dueDateMonth: "11", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e46",
        label: "輸出(小計)",
        overrides: { dueDateMonth: "12", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e47",
        label: "貸出(輸出)",
        overrides: { dueDateMonth: "01", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e48",
        label: "輸入Ｌ／Ｃ",
        overrides: { dueDateMonth: "02", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e49",
        label: "ユーザンス",
        overrides: { dueDateMonth: "03", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e410",
        label: "Ｌ／Ｇ",
        overrides: { dueDateMonth: "04", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e411",
        label: "輸入(小計)",
        overrides: { dueDateMonth: "05", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e412",
        label: "貸出(輸入)",
        overrides: { dueDateMonth: "06", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e413",
        label: "故障指定Ｌ／Ｃ",
        overrides: { dueDateMonth: "07", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "e414",
        label: "ユーザンスシフト外貨",
        overrides: { dueDateMonth: "08", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root5",
    label: "支払承諾合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "s51",
        label: "支払承諾合計 子１",
        overrides: { dueDateMonth: "10", dueDateDay: "01", rate: "99.999", change: -9999999 },
        editableFields: creditEditable([
          "label",
          "mark",
          "principal",
          "change",
          "postBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s52",
        label: "支払承諾合計 子２",
        overrides: { dueDateMonth: "11", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "rate",
          "balance99",
          "mark",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s53",
        label: "支払承諾・支承・一般",
        overrides: { dueDateMonth: "12", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s54",
        label: "支払承諾・支承・一般外為",
        overrides: { dueDateMonth: "01", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s55",
        label: "支払承諾・内他行保証支払承諾",
        overrides: { dueDateMonth: "02", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "s56",
        label: "支払承諾・代理貸付",
        overrides: { dueDateMonth: "03", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root6",
    label: "私募債",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root16",
    label: "協保債",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root7",
    label: "その他一般与信",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root8",
    label: "限度算入ローン合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root9",
    label: "内ＨＬ信用分算入",
    editableFields: creditEditable([
      "rate",
      "balance99",
      "mark",
      "principal",
      "change",
      "postBalance",
      "actualBalance",
      "correction"
    ])
  }),
  creditNode({
    id: "root10",
    label: "オンバランス合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root11",
    label: "オフバランス合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root12",
    label: "限度不算入与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l121",
        label: "限度不算入 子１",
        overrides: { dueDateMonth: "08", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "balance99",
          "mark",
          "principal",
          "postBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l122",
        label: "限度不算入 子２",
        overrides: { dueDateMonth: "09", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "mark",
          "change",
          "actualBalance",
          "correction"
        ])
      })
    ]
  }),
  creditNode({
    id: "root13",
    label: "一般与信合計",
    editableFields: creditEditable(["correction"])
  }),
  creditNode({
    id: "root14",
    label: "特定与信合計",
    editableFields: creditEditable(["correction"]),
    children: [
      creditNode({
        id: "l141",
        label: "特定与信合計 子１",
        overrides: { dueDateMonth: "12", dueDateDay: "01", rate: "99.999" },
        editableFields: creditEditable([
          "label",
          "rate",
          "mark",
          "principal",
          "change",
          "actualBalance",
          "correction"
        ])
      }),
      creditNode({
        id: "l142",
        label: "特定与信合計 子２",
        overrides: {
          dueDateMonth: "",
          dueDateDay: "",
          rate: "",
          balance99: "",
          principal: "",
          change: "",
          postBalance: "",
          actualBalance: "",
          correction: ""
        },
        editableFields: creditEditable([
          "label",
          "dueDateMonth",
          "dueDateDay",
          "rate",
          "balance99",
          "mark",
          "principal",
          "change",
          "postBalance",
          "actualBalance",
          "correction"
        ])
      })
    ]
  })
];

const rawCollateralSource = [
  collateralNode({
    id: "collGeneral",
    collateralType: "規定担保合計",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral2",
    collateralType: "裸与信",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral3",
    collateralType: "補正値",
    editableFields: collateralEditable(["regValue", "marketValue"])
  }),
  collateralNode({
    id: "collGeneral4",
    collateralType: "規定・優良小計",
    editableFields: collateralEditable(["regValue", "marketValue"]),
    children: [
      collateralNode({
        id: "cg4_1",
        collateralType: "規定・優良担保小計",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_2",
        collateralType: "預金",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_3",
        collateralType: "電債割引",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_4",
        collateralType: "電債担保",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_5",
        collateralType: "有証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_6",
        collateralType: "協会保証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_7",
        collateralType: "保証(除協会)",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_8",
        collateralType: "一般Ｌ／Ｃ",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_9",
        collateralType: "手形保険",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg4_11",
        collateralType: "その他",
        editableFields: collateralEditable(["regValue", "marketValue"])
      })
    ]
  }),
  collateralNode({
    id: "collGenera21",
    collateralType: "規定・一般小計",
    editableFields: collateralEditable(["regValue", "marketValue"]),
    children: [
      collateralNode({
        id: "cg21_1",
        collateralType: "有証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_2",
        collateralType: "保証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_3",
        collateralType: "不動産(抵)",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_4",
        collateralType: "内ＨＬ(抵)",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_5",
        collateralType: "不動産(根)",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_6",
        collateralType: "Ｄ／Ｆ保証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg21_7",
        collateralType: "その他",
        editableFields: collateralEditable(["regValue", "marketValue"])
      })
    ]
  }),
  collateralNode({
    id: "collGenera22",
    collateralType: "規定・その他担保小計",
    editableFields: collateralEditable(["regValue", "marketValue"]),
    children: [
      collateralNode({
        id: "cg22_1",
        collateralType: "有証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg22_2",
        collateralType: "保証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg22_3",
        collateralType: "ローン保証",
        editableFields: collateralEditable(["regValue", "marketValue"])
      }),
      collateralNode({
        id: "cg22_4",
        collateralType: "その他",
        editableFields: collateralEditable(["regValue", "marketValue"])
      })
    ]
  }),
  collateralNode({
    id: "collGenera23",
    collateralType: "規定外担保合計",
    editableFields: collateralEditable(["regValue", "marketValue"]),
    children: [
      collateralNode({
        id: "cg23_1",
        collateralType: "規定外・優良小計",
        editableFields: collateralEditable(["regValue", "marketValue"]),
        children: [
          collateralNode({
            id: "cg23_1_1",
            collateralType: "預金",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_1_2",
            collateralType: "有証",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_1_3",
            collateralType: "保証",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_1_4",
            collateralType: "その他",
            editableFields: collateralEditable(["regValue", "marketValue"])
          })
        ]
      }),
      collateralNode({
        id: "cg23_2",
        collateralType: "規定外・一般小計",
        editableFields: collateralEditable(["regValue", "marketValue"]),
        children: [
          collateralNode({
            id: "cg23_2_1",
            collateralType: "有証",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_2",
            collateralType: "保証",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_3",
            collateralType: "不動産(抵)",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_4",
            collateralType: "不動産(根)",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_5",
            collateralType: "入居保証金",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_6",
            collateralType: "債権",
            editableFields: collateralEditable(["regValue", "marketValue"])
          }),
          collateralNode({
            id: "cg23_2_7",
            collateralType: "その他",
            editableFields: collateralEditable(["regValue", "marketValue"])
          })
        ]
      }),
      collateralNode({
        id: "cg23_3",
        collateralType: "規定外・その他",
        editableFields: collateralEditable(["regValue", "marketValue"])
      })
    ]
  })
];

// 編集可能フラグを各ノードに付与(簡素化)
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
