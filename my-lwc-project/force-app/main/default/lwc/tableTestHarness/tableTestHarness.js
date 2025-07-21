import { LightningElement, track, api } from "lwc";

export default class TableTestHarness extends LightningElement {
  @api height = 800;
  @track selectedTestType = "simple-card";
  @track sampleInput = "";
  @track notes = "";


  testTypeOptions = [
    { label: "単純なカード内配置", value: "simple-card" },
    { label: "タブ内配置", value: "tab-test" },
    { label: "複数コンポーネント共存", value: "multi-component" },
    { label: "ネストしたレイアウト", value: "nested-layout" },
    { label: "スクロール競合テスト", value: "scroll-test" }
  ];

  dummyContent = [
    { id: 1, text: "ダミーコンテンツ行1: テーブルスクロールとの競合を確認" },
    { id: 2, text: "ダミーコンテンツ行2: ページ全体のスクロールが正常か確認" },
    { id: 3, text: "ダミーコンテンツ行3: z-indexの競合がないか確認" },
    { id: 4, text: "ダミーコンテンツ行4: レイアウト崩れがないか確認" },
    { id: 5, text: "ダミーコンテンツ行5: 最終確認項目" }
  ];

  get showSimpleCard() {
    return this.selectedTestType === "simple-card";
  }

  get showTabTest() {
    return this.selectedTestType === "tab-test";
  }

  get showMultiComponent() {
    return this.selectedTestType === "multi-component";
  }

  get showNestedLayout() {
    return this.selectedTestType === "nested-layout";
  }

  get showScrollTest() {
    return this.selectedTestType === "scroll-test";
  }



  handleTestTypeChange(event) {
    this.selectedTestType = event.detail.value;
  }

  handleSampleInputChange(event) {
    this.sampleInput = event.target.value;
  }

  handleNotesChange(event) {
    this.notes = event.target.value;
  }

  handleSampleButtonClick() {
    console.log("サンプルボタンがクリックされました");
    // テーブルとの相互作用テスト用
  }

}