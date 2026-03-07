import { LightningElement, track } from "lwc";
import { makeTestData } from "c/testDataGenerator";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC6 extends LightningElement {
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
