import { LightningElement, track, api } from "lwc";

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

  @track branchNumber = "99999";
  @track branchName = "○○○○●○○○○10○○○○●○○○○20";
  @track customerName =
    "○○○○●○○○○10○○○○●○○○○20○○○○●○○○○30○○○○●○○○○40○○○○●○○○○50○○○○●○○○○60○○○○●○○○○70○○○○●○○○○80○○○○●○○○○90○○○○●○○○○100○○○○●○○○○110○○○○●○○○○120○○○○●○○○○130○○○○●○○○○140○○○○●○○○○150";
  @track customerNumber = "9999999";
  @track debtorRating = "99-9";
  @track coreCompany = "○○○○●○○○○10○12";

  @track reviewNumber = "9999";
  @track amountUnit = "○○○○●○";
  @track groupNumber = "9";
  @track date = "2025/3/31";

  @track correctionReason =
    "○○○○●○○○○10○○○○●○○○○20○○○○●○○○○30○○○○●○○○○40○○○○●○○○○50○○○○●○○○○60○○○○●○○○○70○○○○●○○○○80○○○○●○○○○90○○○○●○○○○100";
  @track poolCategory = "99";
  @track protectionRate = "999.99";
  @track limitGeneral = "9,999,999";
  @track marketInclusion = "99,999";
  @track regulatoryCollateral = "9,999,999";
}
