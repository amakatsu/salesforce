// 利率コンポーネント用の状態管理サービス
import {
  rawCreditSource,
  rawCollateralSource,
  attachEditableFlags,
  deepCopy
} from "./data";

let isInitialized = false;
let creditSource = [];
let initialCreditSource = [];
let originalCreditSource = [];
let collateralSource = [];
let initialCollateralSource = [];
let originalCollateralSource = [];
let expanded = new Set();
let draft = new Map();

// 状態管理サービス
const initializeState = () => {
  if (!isInitialized) {
    const withCreditFlags = attachEditableFlags(rawCreditSource);
    const withCollateralFlags = attachEditableFlags(rawCollateralSource);

    creditSource = deepCopy(withCreditFlags);
    initialCreditSource = deepCopy(withCreditFlags);
    originalCreditSource = deepCopy(withCreditFlags);
    collateralSource = deepCopy(withCollateralFlags);
    initialCollateralSource = deepCopy(withCollateralFlags);
    originalCollateralSource = deepCopy(withCollateralFlags);
    isInitialized = true;
  }
};

const resetState = () => {
  creditSource = deepCopy(initialCreditSource);
  originalCreditSource = deepCopy(initialCreditSource);
  collateralSource = deepCopy(initialCollateralSource);
  originalCollateralSource = deepCopy(initialCollateralSource);
  draft.clear();
};

const getState = () => ({
  isInitialized,
  creditSource,
  initialCreditSource,
  originalCreditSource,
  collateralSource,
  initialCollateralSource,
  originalCollateralSource,
  expanded,
  draft
});

const setState = (s) => {
  if (s.creditSource) creditSource = s.creditSource;
  if (s.originalCreditSource) originalCreditSource = s.originalCreditSource;
  if (s.collateralSource) collateralSource = s.collateralSource;
  if (s.originalCollateralSource)
    originalCollateralSource = s.originalCollateralSource;
};

export const stateService = { initializeState, resetState, getState, setState };
