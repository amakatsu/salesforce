import { LightningElement, api } from 'lwc';

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoB1 extends LightningElement {

        @api showCalculationAndRegisterButtons;

  /**
   * HTML で複数ボタンが onclick={handleAction} を共有するため、event.target.label で分岐する想定。
   */
  handleAction(event) {
    // TODO: event.target.label に応じた業務ロジック実装
    //   - 計数再取得 / ファイル出力 / Excel出力
    //   - 照会メニュー: 過去禀査 / 直近計数照会 / 預金担保明細 / 支払人別残高推移
    //                   / 電債担保残高 / 有価証券担保明細 / 協会保証明細 / 一般保証明細
    //                   / その他担保明細 / 不動産担保明細
  }

  /** 「計算」ボタン押下イベント */
  handleCalculate() {
    // TODO: 業務ロジック実装（補正前後の数値再計算 → 親側の表へ反映）
  }

  /**
   * HTML で「補正値登録」「登録」が onclick={handleRegister} を共有するため、label で分岐する。
   */
  async handleRegister(event) {
    const label = event?.target?.label;
    if (label === '補正値登録') {
      await this.handleHoseichiRegisterClick();
      return;
    }
    // TODO: 「登録」ボタン押下時の業務ロジック実装
  }

  /**   *  補正値登録ボタン押下イベント   */
  handleHoseichiRegisterClick() {
    const exe = new CustomEvent("hoseichiregister");

    this.dispatchEvent(exe);
  }
}
