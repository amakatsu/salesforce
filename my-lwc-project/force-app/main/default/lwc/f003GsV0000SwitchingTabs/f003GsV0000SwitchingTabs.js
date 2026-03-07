/**
 * タブ切替ユーティリティ
 * 親/子タブのアクティブ状態を切り替える共通関数
 *
 * @param {HTMLElement} clickedTab - クリックされたタブ要素
 * @param {string} clickedTabId - タブコンテンツのdata-tab-content値
 * @param {string} tabPosition - "parent" または "child"
 */
const switchingTabs = function (clickedTab, clickedTabId, tabPosition) {
  const tabItems = this.template.querySelectorAll(`.${tabPosition}-tabs-item`);
  tabItems.forEach((item) => {
    item.classList.remove("slds-is-active");
    const link = item.querySelector("a");
    if (link) {
      link.setAttribute("tabindex", "-1");
      link.setAttribute("aria-selected", "false");
    }
  });

  const parentItem = clickedTab.closest(`.${tabPosition}-tabs-item`);
  if (parentItem) {
    parentItem.classList.add("slds-is-active");
    clickedTab.setAttribute("tabindex", "0");
    clickedTab.setAttribute("aria-selected", "true");
  }

  const tabContents = this.template.querySelectorAll(
    `.${tabPosition}-tabs-content`
  );
  tabContents.forEach((content) => {
    if (content.getAttribute("data-tab-content") === clickedTabId) {
      content.classList.remove("slds-hide");
      content.classList.add("slds-show");
    } else {
      content.classList.remove("slds-show");
      content.classList.add("slds-hide");
    }
  });
};

export { switchingTabs };
