import { LightningElement, api, track } from "lwc";

export default class F003GsV0000Number extends LightningElement {
  @api numValue;
  @api numLabel = "";
  @api isTable = false;
  @api disabled = false;
  @api step = "1";
  @api setId = "";

  get inputVariant() {
    return this.isTable ? "label-hidden" : "standard";
  }

  get inputClass() {
    const classes = [];
    if (this.isTable) {
      classes.push("table-number-input");
    }
    if (this.disabled) {
      classes.push("display-number-input");
    }
    return classes.join(" ");
  }

  get tableInputClass() {
    const classes = ["slds-input", "table-number-input"];
    if (this.disabled) {
      classes.push("display-number-input");
    }
    return classes.join(" ");
  }

  handleNumberChange(event) {
    const value = event.target.value;

    // 数値バリデーション
    if (value && isNaN(value)) {
      this.dispatchEvent(
        new CustomEvent("error", {
          detail: {
            message: "数値を入力してください",
            field: this.setId
          }
        })
      );
      return;
    }

    // 変更イベントを親コンポーネントに送信
    this.dispatchEvent(
      new CustomEvent("change", {
        detail: {
          value: value,
          field: this.setId,
          id: this.template.host.dataset.id
        }
      })
    );
  }
}
