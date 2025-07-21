import { LightningElement, api } from "lwc";

export default class DatatableBadgeCell extends LightningElement {
  @api value;

  get badgeClass() {
    if (this.value === "true" || this.value === true) {
      return "slds-badge slds-theme_success";
    } else if (this.value === "false" || this.value === false) {
      return "slds-badge slds-theme_error";
    }
    return "slds-badge";
  }
}