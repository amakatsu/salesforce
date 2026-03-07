import { LightningElement, track } from "lwc";
import { switchingTabs } from "c/f003GsV0000SwitchingTabs";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJoho extends LightningElement {
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
  activeSectionsMessage = "";
  isAllVisible = true;

  @track showCalculationAndRegisterButtons = true;
  @track isModalOpen = false;
  @track editRow = {};
  @track treeGridData1 = [];

  /* ───────────────── 行アクション (補正値編集) ───────────────── */
  handleRowAction(event) {
    const { action, row } = event.detail;
    if (action.name === "editCorrection") {
      this.editRow = { ...row };
      this.isModalOpen = true;
    }
  }

  handleCorrectionInput(event) {
    this.editRow.correction = Number(event.target.value);
  }

  closeModal() {
    this.isModalOpen = false;
  }

  saveCorrection() {
    // 再帰的更新関数
    const update = (rows, id, value) => {
      for (const r of rows) {
        if (r.id === id) {
          r.correction = value;
          return true;
        }
        if (r._children && update(r._children, id, value)) {
          // 親合計も再計算
          r.correction = r._children.reduce((acc, c) => acc + c.correction, 0);
          return true;
        }
      }
      return false;
    };
    update(this.treeGridData1, this.editRow.id, this.editRow.correction);
    // 強制再描画
    this.treeGridData1 = [...this.treeGridData1];
    this.isModalOpen = false;
  }

  /* ───────────────── 操作ボタン (ダミー) ───────────────── */
  handleFetchCalculation() {
    console.log("計数再取得");
  }

  handleCalculate() {
    console.log("計算");
  }

  handleRegisterCorrection() {
    console.log("補正値登録");
  }

  handleRegister() {
    console.log("登録");
  }

  handleFileExport() {
    console.log("ファイル作成");
  }

  handleExcelExport() {
    console.log("Excel出力");
  }

  handleRecentInquiry() {
    console.log("直近計数照会");
  }

  handlePastReview() {
    console.log("過去審査");
  }

  handleDepositDetail() {
    console.log("預金担保明細");
  }

  handleBillBalance() {
    console.log("手形電債残高");
  }

  handleSecuritiesDetail() {
    console.log("有価証券明細");
  }

  handleAssociationGuarantee() {
    console.log("協会保証明細");
  }

  handleRealEstateDetail() {
    console.log("不動産担保明細");
  }

  /**
   * 親タブ切替処理
   *
   * @param {Event} event クリックイベント
   */
  handleSwitchingParentTabs(event) {
    // タブ要素を取得、設定
    const clickedTab = event.target;
    const clickedTabId = clickedTab.getAttribute("data-tab-content");
    const tabPosition = "parent";

    // タブの切替処理を実行
    switchingTabs.bind(this)(clickedTab, clickedTabId, tabPosition);
  }

  /**
   * 子タブ切替処理
   *
   * @param {Event} event クリックイベント
   */
  handleSwitchingChildTabs(event) {
    // タブ要素を取得、設定
    const clickedTab = event.target;
    const clickedTabId = clickedTab.getAttribute("data-tab-content");
    const tabPosition = "child";

    // タブの切替処理を実行
    switchingTabs.bind(this)(clickedTab, clickedTabId, tabPosition);
  }
}
