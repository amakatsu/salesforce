import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

const FUND_USE_HEADERS = ["資金使途", "金額", "返済原資", "返済期間"];
const COLLATERAL_HEADERS = ["担保種類", "評価額", "設定額", "備考"];

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoC7 extends LightningElement {
  activeSections = ["a", "b"];

  fundUseRows = [
    { id: "fu1", use: makeTestData("mixedChar", 8), amount: makeTestData("numeric", 5), source: makeTestData("mixedChar", 6), period: makeTestData("mixedChar", 4) },
    { id: "fu2", use: makeTestData("mixedChar", 8), amount: makeTestData("numeric", 5), source: makeTestData("mixedChar", 6), period: makeTestData("mixedChar", 4) },
    { id: "fu3", use: makeTestData("mixedChar", 8), amount: makeTestData("numeric", 5), source: makeTestData("mixedChar", 6), period: makeTestData("mixedChar", 4) },
    { id: "fu4", use: makeTestData("mixedChar", 8), amount: makeTestData("numeric", 5), source: makeTestData("mixedChar", 6), period: makeTestData("mixedChar", 4) }
  ];

  collateralSummaryRows = [
    { id: "cs1", type: makeTestData("mixedChar", 6), valuation: makeTestData("numeric", 5), setting: makeTestData("numeric", 5), note: makeTestData("mixedChar", 6) },
    { id: "cs2", type: makeTestData("mixedChar", 6), valuation: makeTestData("numeric", 5), setting: makeTestData("numeric", 5), note: makeTestData("mixedChar", 6) },
    { id: "cs3", type: makeTestData("mixedChar", 6), valuation: makeTestData("numeric", 5), setting: makeTestData("numeric", 5), note: makeTestData("mixedChar", 6) }
  ];

  get fundUseHeaders() {
    return FUND_USE_HEADERS;
  }

  get collateralHeaders() {
    return COLLATERAL_HEADERS;
  }

  @api
  applySavedHighlight() {
    // C7 has no editable fields
  }
}
