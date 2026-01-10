// 利率コンポーネント用の状態管理サービス
import {
  rawCreditSource,
  rawCollateralSource,
  attachEditableFlags,
  deepCopy
} from "./data";
import { apiService } from "./apiService";

let isInitialized = false;
let creditSource = [];
let initialCreditSource = [];
let originalCreditSource = [];
let collateralSource = [];
let initialCollateralSource = [];
let originalCollateralSource = [];
let expanded = new Set();
let draft = new Map();
let useApi = false; // APIを使用するかどうかのフラグ

// 外部データで初期化する関数
const initializeWithData = (creditData, collateralData) => {
  if (creditData) {
    creditSource = attachEditableFlags(creditData);
    initialCreditSource = deepCopy(creditSource);
    originalCreditSource = deepCopy(creditSource);
  } else {
    creditSource = attachEditableFlags(rawCreditSource);
    initialCreditSource = deepCopy(creditSource);
    originalCreditSource = deepCopy(creditSource);
  }

  if (collateralData) {
    collateralSource = attachEditableFlags(collateralData);
    initialCollateralSource = deepCopy(collateralSource);
    originalCollateralSource = deepCopy(collateralSource);
  } else {
    collateralSource = attachEditableFlags(rawCollateralSource);
    initialCollateralSource = deepCopy(collateralSource);
    originalCollateralSource = deepCopy(collateralSource);
  }

  isInitialized = true;
};

// 状態管理サービス
const initializeState = async () => {
  if (!isInitialized) {
    // APIが利用可能かチェック
    const apiAvailable = await apiService.healthCheck();
    useApi = apiAvailable;

    if (useApi) {
      try {
        // APIからデータを取得
        const apiCreditData = await apiService.getCreditData();
        const apiCollateralData = await apiService.getCollateralData();

        // APIデータを階層構造に変換
        const convertedCreditData = convertFlatToHierarchy(apiCreditData);
        const convertedCollateralData =
          convertFlatToHierarchy(apiCollateralData);

        creditSource = attachEditableFlags(convertedCreditData);
        collateralSource = attachEditableFlags(convertedCollateralData);
      } catch (error) {
        console.warn("API data fetch failed, using local data:", error);
        useApi = false;
      }
    }

    if (!useApi) {
      // ローカルデータを使用
      const withCreditFlags = attachEditableFlags(rawCreditSource);
      const withCollateralFlags = attachEditableFlags(rawCollateralSource);

      creditSource = deepCopy(withCreditFlags);
      collateralSource = deepCopy(withCollateralFlags);
    }

    initialCreditSource = deepCopy(creditSource);
    originalCreditSource = deepCopy(creditSource);
    initialCollateralSource = deepCopy(collateralSource);
    originalCollateralSource = deepCopy(collateralSource);
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

// APIデータをローカル階層構造に変換するヘルパー関数
const convertFlatToHierarchy = (flatData) => {
  if (!flatData || !Array.isArray(flatData)) {
    return [];
  }

  // 実際の変換ロジックはデータ構造に依存
  // ここではサンプル実装
  return flatData.map((item) => ({
    ...item,
    children: item.children || []
  }));
};

export const stateService = {
  initializeState,
  initializeWithData,
  resetState,
  getState,
  setState
};
