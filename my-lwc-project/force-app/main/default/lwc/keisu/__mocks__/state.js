/**
 * stateService Mock - 本格的開発用
 * 
 * 外部依存をモック化し、テスト対象のコンポーネント本体は
 * 実際のソースコードを使用するアプローチ
 */

// モック用の初期状態データ
const createMockState = (overrides = {}) => ({
  isInitialized: false,
  creditSource: [],
  initialCreditSource: [],
  originalCreditSource: [],
  collateralSource: [],
  initialCollateralSource: [],
  originalCollateralSource: [],
  expanded: new Set(),
  draft: new Map(),
  ...overrides
});

// モックされたstateService
export const stateService = {
  // 状態初期化のスパイ関数
  initializeState: jest.fn(() => {
    // 実際の初期化処理をモック化
    mockState.isInitialized = true;
    mockState.creditSource = mockState.initialCreditSource.slice();
    mockState.collateralSource = mockState.initialCollateralSource.slice();
  }),

  // 状態リセットのスパイ関数
  resetState: jest.fn(() => {
    // 実際のリセット処理をモック化
    mockState.creditSource = mockState.initialCreditSource.slice();
    mockState.collateralSource = mockState.initialCollateralSource.slice();
    mockState.draft.clear();
    mockState.expanded.clear();
  }),

  // 状態取得のモック関数
  getState: jest.fn(() => mockState),

  // 状態設定のモック関数（テスト用）
  setState: jest.fn((newState) => {
    Object.assign(mockState, newState);
  })
};

// テストで使用するモック状態
let mockState = createMockState();

// テスト用のヘルパー関数
export const __testHelpers__ = {
  // モック状態をリセット
  resetMockState: (initialState = {}) => {
    mockState = createMockState(initialState);
    jest.clearAllMocks();
  },

  // 現在のモック状態を取得
  getMockState: () => mockState,

  // 特定の状態を設定
  setMockState: (state) => {
    Object.assign(mockState, state);
  },

  // 下書きデータを追加
  addDraftData: (nodeId, data) => {
    mockState.draft.set(nodeId, data);
  },

  // 展開状態を設定
  setExpandedNodes: (nodeIds) => {
    mockState.expanded.clear();
    nodeIds.forEach(id => mockState.expanded.add(id));
  }
};