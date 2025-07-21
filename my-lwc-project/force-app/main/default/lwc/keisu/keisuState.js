// 係数コンポーネント用の状態管理サービス
import { rawCreditSource, rawOtherBankSource, attachEditableFlags, deepCopy } from './keisuData';

class KeisuStateService {
  constructor() {
    this.isInitialized = false;
    this.creditSource = [];
    this.initialCreditSource = [];
    this.originalCreditSource = [];
    this.otherBankSource = [];
    this.initialOtherBankSource = [];
    this.originalOtherBankSource = [];
    this.expanded = new Set();
    this.draft = new Map();
  }

  // 状態の初期化
  initializeState() {
    if (!this.isInitialized) {
      const withCreditFlags = attachEditableFlags(rawCreditSource);
      const withOtherBankFlags = attachEditableFlags(rawOtherBankSource);
      
      this.creditSource = deepCopy(withCreditFlags);
      this.initialCreditSource = deepCopy(withCreditFlags);
      this.originalCreditSource = deepCopy(withCreditFlags);
      this.otherBankSource = deepCopy(withOtherBankFlags);
      this.initialOtherBankSource = deepCopy(withOtherBankFlags);
      this.originalOtherBankSource = deepCopy(withOtherBankFlags);
      this.isInitialized = true;
    }
  }

  // 状態のリセット
  resetState() {
    this.creditSource = deepCopy(this.initialCreditSource);
    this.originalCreditSource = deepCopy(this.initialCreditSource);
    this.otherBankSource = deepCopy(this.initialOtherBankSource);
    this.originalOtherBankSource = deepCopy(this.initialOtherBankSource);
    this.draft.clear();
  }

  // 状態の取得
  getState() {
    return {
      isInitialized: this.isInitialized,
      creditSource: this.creditSource,
      initialCreditSource: this.initialCreditSource,
      originalCreditSource: this.originalCreditSource,
      otherBankSource: this.otherBankSource,
      initialOtherBankSource: this.initialOtherBankSource,
      originalOtherBankSource: this.originalOtherBankSource,
      expanded: this.expanded,
      draft: this.draft
    };
  }

  // 状態の設定
  setState(newState) {
    if (newState.creditSource) this.creditSource = newState.creditSource;
    if (newState.originalCreditSource) this.originalCreditSource = newState.originalCreditSource;
    if (newState.otherBankSource) this.otherBankSource = newState.otherBankSource;
    if (newState.originalOtherBankSource) this.originalOtherBankSource = newState.originalOtherBankSource;
  }
}

// シングルトンインスタンス
const stateService = new KeisuStateService();

export { stateService };