import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC1 extends LightningElement {
  activeSections = ["a"];

  @api showCalculationAndRegisterButtons;

  branchNumber = makeTestData("numeric", 5);
  branchName = makeTestData("mixedChar", 20);
  customerName = makeTestData("mixedChar", 150);
  customerNumber = makeTestData("numeric", 7);
  debtorRating = "99-9";
  coreCompany = makeTestData("mixedChar", 12);
}
