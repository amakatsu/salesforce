import { LightningElement } from "lwc";
import { switchingTabs } from "c/f003GsV0000SwitchingTabs";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJoho extends LightningElement {
  isAllVisible = true;
  showCalculationAndRegisterButtons = true;

  /**
   * タブ切替処理(親タブ・子タブ共通)
   * data-tab-type 属性で親/子を判別
   *
   * @param {Event} event クリックイベント
   */
  handleTabSwitch(event) {
    const clickedTab = event.target;
    const tabContentId = clickedTab.dataset.tabContent;
    const tabType = clickedTab.dataset.tabType;
    switchingTabs.bind(this)(clickedTab, tabContentId, tabType);
  }

  /**
   * 登録ボタン押下時の処理
   * B1からのregisterイベントを受けて各子コンポーネントのハイライトを適用
   */
  handleRegister() {
    const selectors = [
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c2",
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c3",
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c4",
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c6"
    ];
    selectors.forEach((selector) => {
      const component = this.template.querySelector(selector);
      if (component) {
        component.applySavedHighlight();
      }
    });
  }
}
