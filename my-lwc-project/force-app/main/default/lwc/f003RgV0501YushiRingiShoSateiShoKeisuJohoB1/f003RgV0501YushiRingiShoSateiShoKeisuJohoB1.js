import { LightningElement, api } from "lwc";

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 extends LightningElement {
  @api showCalculationAndRegisterButtons;

  /** プレースホルダー: 実装時に個別ハンドラに置き換え */
  handleAction(event) {
    console.log(event.currentTarget.label);
  }

  handleCalculate() {
    console.log("計算");
    this.dispatchEvent(new CustomEvent("calculate"));
  }

  handleRegister() {
    console.log("登録");
    this.dispatchEvent(new CustomEvent("register"));
  }
}
