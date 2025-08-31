/**
 * Jest Setup for Production LWC Testing
 * 
 * LWCフレームワークの本格的なモック環境を構築
 */

// =============================================================================
// LWC Framework Mocks
// =============================================================================

/**
 * LightningElement base class mock
 * 実際のLWCライフサイクルとリアクティブプロパティを模擬
 */
class MockLightningElement {
  constructor() {
    this.template = new MockTemplate();
    this._connected = false;
    this._rendered = false;
    
    // リアクティブプロパティの追跡
    this._reactiveProps = new Set();
  }

  // ライフサイクルメソッド
  connectedCallback() {
    this._connected = true;
  }

  disconnectedCallback() {
    this._connected = false;
  }

  renderedCallback() {
    this._rendered = true;
  }

  errorCallback(error, stack) {
    console.error('Component error:', error, stack);
  }

  // DOM操作のモック
  querySelector(selector) {
    return this.template.querySelector(selector);
  }

  querySelectorAll(selector) {
    return this.template.querySelectorAll(selector);
  }
}

/**
 * Template mock for LWC
 */
class MockTemplate {
  constructor() {
    this._elements = new Map();
  }

  querySelector(selector) {
    return this._elements.get(selector) || null;
  }

  querySelectorAll(selector) {
    return Array.from(this._elements.values())
      .filter(el => el.matches && el.matches(selector));
  }
}

// LWCモジュールのモック
global.LightningElement = MockLightningElement;

/**
 * @track デコレータのモック
 * 実際にはBabelトランスフォームで処理されるが、テスト用に空実装
 */
global.track = (target, propertyKey, descriptor) => {
  // テスト環境では何もしない
  return descriptor;
};

/**
 * @api デコレータのモック
 */
global.api = (target, propertyKey, descriptor) => {
  return descriptor;
};

/**
 * @wire デコレータのモック
 */
global.wire = (wireAdapter, config) => {
  return (target, propertyName, descriptor) => {
    return descriptor;
  };
};

// =============================================================================
// DOM Environment Setup
// =============================================================================

/**
 * createElement のより高度なモック
 * LWCコンポーネントの作成をサポート
 */
const originalCreateElement = document.createElement;

global.createElement = (tagName, options) => {
  if (options && options.is) {
    // LWCコンポーネントの場合
    const element = new options.is();
    element.tagName = tagName.toUpperCase();
    
    // DOM要素としてのプロパティを追加
    element.style = {};
    element.dataset = {};
    element.classList = {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    };
    
    return element;
  }
  
  // 通常のDOM要素
  return originalCreateElement.call(document, tagName);
};

// =============================================================================
// Global Mocks and Utilities
// =============================================================================

/**
 * Lightning Design System のユーティリティクラス
 */
global.SLDS = {
  icons: {
    utility: {
      chevrondown: 'utility:chevrondown',
      chevronright: 'utility:chevronright'
    }
  }
};

/**
 * Test utilities for LWC components
 */
global.TestUtils = {
  /**
   * イベントオブジェクトを作成
   */
  createEvent: (type, detail = null, target = null) => ({
    type,
    detail,
    target: target || {
      value: '',
      checked: false,
      dataset: {}
    },
    currentTarget: target || {
      dataset: {}
    },
    preventDefault: jest.fn(),
    stopPropagation: jest.fn()
  }),

  /**
   * HTML要素のモック作成
   */
  createMockElement: (tagName = 'div', properties = {}) => ({
    tagName: tagName.toUpperCase(),
    style: {},
    dataset: {},
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn()
    },
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    ...properties
  }),

  /**
   * リアクティブプロパティの変更をシミュレート
   */
  triggerReactiveChange: (component, property, value) => {
    const oldValue = component[property];
    component[property] = value;
    
    // 変更通知のシミュレート（実際のLWCではフレームワークが行う）
    if (typeof component.renderedCallback === 'function') {
      component.renderedCallback();
    }
    
    return { oldValue, newValue: value };
  }
};

// =============================================================================
// Test Lifecycle Hooks
// =============================================================================

/**
 * 各テスト前の共通セットアップ
 */
beforeEach(() => {
  // モックの状態をリセット
  jest.clearAllMocks();
  
  // DOMのクリーンアップ
  document.body.innerHTML = '';
});

/**
 * 各テスト後の共通クリーンアップ
 */
afterEach(() => {
  // 非同期処理の完了を待つ
  return new Promise(resolve => setTimeout(resolve, 0));
});