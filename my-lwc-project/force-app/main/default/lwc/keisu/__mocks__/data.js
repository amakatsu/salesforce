/**
 * data.js Mock - テスト用データ管理
 * 
 * 実際のデータファイルをモック化し、予測可能なテストデータを提供
 */

// モック用の与信データ
export const rawCreditSource = [
  {
    id: 'credit_1',
    label: 'テスト与信1',
    rate: 1.5,
    balance99: 1000000,
    principal: 5000000,
    editable: {
      rate: true,
      balance99: true,
      principal: false
    },
    children: [
      {
        id: 'credit_1_1',
        label: 'サブ与信1-1',
        rate: 1.2,
        balance99: 500000,
        editable: { rate: true }
      }
    ]
  },
  {
    id: 'credit_2',
    label: 'テスト与信2',
    rate: 2.0,
    balance99: 2000000,
    principal: 10000000,
    editable: {
      rate: true,
      balance99: true,
      principal: true
    }
  }
];

// モック用の担保データ
export const rawCollateralSource = [
  {
    id: 'collateral_1',
    collateralType: '不動産担保',
    regValue: 50000000,
    marketValue: 45000000,
    editable: {
      regValue: true,
      marketValue: true
    }
  },
  {
    id: 'collateral_2',
    collateralType: '預金担保',
    regValue: 10000000,
    marketValue: 10000000,
    editable: {
      regValue: false,
      marketValue: false
    }
  }
];

/**
 * 編集可能フラグを付与する関数のモック
 */
export const attachEditableFlags = jest.fn((data) => {
  // 実際の処理をシンプルにモック化
  return data.map(item => ({
    ...item,
    editable: item.editable || {
      // デフォルトで全フィールド編集可能
      rate: true,
      balance99: true,
      principal: true,
      regValue: true,
      marketValue: true
    }
  }));
});

/**
 * ディープコピー関数のモック
 */
export const deepCopy = jest.fn((obj) => {
  // JSON方式のシンプルなディープコピー
  return JSON.parse(JSON.stringify(obj));
});

// テスト用ヘルパー
export const __testHelpers__ = {
  // カスタムテストデータを作成
  createTestCreditData: (overrides = {}) => ([{
    id: 'test_credit',
    label: 'テスト用与信',
    rate: 1.0,
    balance99: 1000000,
    principal: 5000000,
    editable: { rate: true, balance99: true, principal: true },
    ...overrides
  }]),

  createTestCollateralData: (overrides = {}) => ([{
    id: 'test_collateral',
    collateralType: 'テスト担保',
    regValue: 10000000,
    marketValue: 9000000,
    editable: { regValue: true, marketValue: true },
    ...overrides
  }]),

  // 階層データの作成
  createNestedData: (parentId, childCount = 2) => ({
    id: parentId,
    label: `Parent ${parentId}`,
    children: Array.from({ length: childCount }, (_, i) => ({
      id: `${parentId}_child_${i + 1}`,
      label: `Child ${i + 1}`,
      rate: 1.0 + i * 0.1
    }))
  })
};