import { LightningElement } from "lwc";
import { switchingTabs } from "c/f003GsV0000SwitchingTabs";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJoho extends LightningElement {
  isAllVisible = true;
  showCalculationAndRegisterButtons = true;

  /**
   * 親タブ切替処理
   *
   * @param {Event} event クリックイベント
   */
  handleSwitchingParentTabs(event) {
    const clickedTab = event.target;
    const clickedTabId = clickedTab.getAttribute("data-tab-content");
    switchingTabs.bind(this)(clickedTab, clickedTabId, "parent");
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

  /**
   * 子タブ切替処理
   *
   * @param {Event} event クリックイベント
   */
  handleSwitchingChildTabs(event) {
    const clickedTab = event.target;
    const clickedTabId = clickedTab.getAttribute("data-tab-content");
    switchingTabs.bind(this)(clickedTab, clickedTabId, "child");
  }
}
