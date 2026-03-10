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

  get organizationFields() {
    return [
      { key: "orgBranch", label: "組織店番", value: this.branchNumber, size: "2" },
      { key: "orgName", label: "組織店名", value: this.branchName, size: "4" }
    ];
  }

  get customerFields() {
    return [
      { key: "custBranch", label: "店番", value: this.branchNumber, size: "2" },
      { key: "custNumber", label: "取引先番号", value: this.customerNumber, size: "2" },
      { key: "custName", label: "取引先名", value: this.customerName, size: "4" },
      { key: "custRating", label: "債務者格付", value: this.debtorRating, size: "2" },
      { key: "custCore", label: "コア企業", value: this.coreCompany, size: "2" }
    ];
  }
}
