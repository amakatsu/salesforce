import { LightningElement, api } from "lwc";

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 extends LightningElement {
  @api showCalculationAndRegisterButtons;

  /** プレースホルダー: 実装接続時に個別ハンドラに置き換え */
  handleAction() {
    // TODO: 実装接続時にdata-action属性等で分岐
  }

  handleCalculate() {
    this.dispatchEvent(new CustomEvent("calculate"));
  }

  handleRegister() {
    this.dispatchEvent(new CustomEvent("register"));
  }
}
