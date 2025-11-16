import { LightningElement } from "lwc";

/**
 * 親コンポーネント。
 * 本件条件(ConditionDetails)と担保情報(CollateralDetailsTable)を同じ画面にまとめて表示する。
 */
const PATTERN_CARDS = [
  {
    id: "patternImport",
    label: "パターン",
    description: "案件: 本件条件①/②・備考・照会をすべて表示。上限6件。",
    screenType: "patternImport"
  },
  {
    id: "patternExport",
    label: "輸出輸入パターン",
    description: "輸出輸入案件: 全入力欄表示。上限12件。",
    screenType: "patternExport"
  },
  {
    id: "patternAbcp",
    label: "ABCPパターン",
    description: "ABCP: 詳細入力欄②と備考のみ表示。",
    screenType: "patternAbcp"
  }
];

export default class ConditionCollateralDashboard extends LightningElement {
  borrowerName = "株式会社アズール商事";
  creditNumber = "CN-2025-00018";
  creditLimit = "5,000,000,000";
  reviewStatus = "精査中";
  ownerName = "与信 太郎";
  lastUpdated = "2025/02/15";
  patternCards = PATTERN_CARDS;

  get statusClass() {
    const themeClass =
      this.reviewStatus === "承認済"
        ? "slds-theme_success"
        : "slds-theme_warning";
    return `status-badge ${themeClass}`;
  }
}
