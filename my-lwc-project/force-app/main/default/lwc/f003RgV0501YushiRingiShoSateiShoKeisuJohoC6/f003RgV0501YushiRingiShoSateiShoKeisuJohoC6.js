import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC6 extends LightningElement {
  activeSections = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r"];

  reviewNumber = makeTestData("numeric", 4);
  amountUnit = "〇〇〇";
  groupNumber = makeTestData("numeric", 1);
  date = "2025/3/31";

  correctionReason = makeTestData("mixedChar", 105);
  poolCategory = makeTestData("numeric", 2);
  protectionRate = "999.99";
  limitGeneral = makeTestData("numeric", 7);
  marketInclusion = makeTestData("numeric", 5);
  regulatoryCollateral = makeTestData("numeric", 7);

  @api
  applySavedHighlight() {
    // C6 has no editable table number fields
  }
}
