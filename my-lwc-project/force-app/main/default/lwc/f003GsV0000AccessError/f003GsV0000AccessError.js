import { LightningElement, api } from "lwc";

export default class F003GsV0000AccessError extends LightningElement {
  @api records = [];

  get hasErrors() {
    return this.records && this.records.length > 0;
  }
}
