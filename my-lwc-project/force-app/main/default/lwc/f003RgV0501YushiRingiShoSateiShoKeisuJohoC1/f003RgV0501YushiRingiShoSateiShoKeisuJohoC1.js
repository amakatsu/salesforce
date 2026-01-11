import { LightningElement, track, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC1 extends LightningElement {
  activeSections = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r"
  ];

  @api showCalculationAndRegisterButtons;

  @track branchNumber = makeTestData("numeric", 5);
  @track branchName = makeTestData("mixedChar", 20);
  @track customerName = makeTestData("mixedChar", 150);
  @track customerNumber = makeTestData("numeric", 7);
  @track debtorRating = "99-9";
  @track coreCompany = makeTestData("mixedChar", 12);

  @track reviewNumber = makeTestData("numeric", 4);
  @track amountUnit = "〇〇〇";
  @track groupNumber = makeTestData("numeric", 1);
  @track date = "2025/3/31";

  @track correctionReason = makeTestData("mixedChar", 100);
  @track poolCategory = makeTestData("numeric", 2);
  @track protectionRate = "999.99";
  @track limitGeneral = makeTestData("numeric", 7);
  @track marketInclusion = makeTestData("numeric", 5);
  @track regulatoryCollateral = makeTestData("numeric", 7);
}
