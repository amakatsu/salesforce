import { LightningElement } from "lwc";
import { generateData } from "c/f003RgV0000CommonJs";

// ========================================
// 定数定義: 選択肢オプション
// ========================================

const DETAIL_OPTIONS = [
  { label: "一般法人保証（非上場）", value: "不動産担保" },
  { label: "動産担保", value: "動産担保" },
  { label: "債権担保", value: "債権担保" },
  { label: "保証人", value: "保証人" },
  { label: "連帯保証", value: "連帯保証" },
  { label: "根保証", value: "根保証" },
  { label: "質権", value: "質権" },
  { label: "抵当権", value: "抵当権" },
  { label: "譲渡担保", value: "譲渡担保" },
  { label: "その他", value: "その他" }
];

// ========================================
// 定数定義: サンプルデータ
// ========================================

const SAMPLE_TEXT_25 = generateData("half", 25);
const SAMPLE_TEXT_66 = generateData("half", 66);
const SAMPLE_TEXT_366 = generateData("half", 366);

// ========================================
// コンポーネントクラス
// ========================================

export default class f003RgV9962TanpoNgaiLinkC1 extends LightningElement {
  collateralGuarantee = SAMPLE_TEXT_25;
  selectedDetail = "";
  jurisdiction = SAMPLE_TEXT_66;
  governingLaw = SAMPLE_TEXT_66;
  note = SAMPLE_TEXT_366;
  detailOptions = DETAIL_OPTIONS;

  // ========================================
  // イベントハンドラー
  // ========================================

  handleDetailChange(event) {
    this.selectedDetail = event.target.value;
  }

  handleJurisdictionChange(event) {
    this.jurisdiction = event.target.value;
  }

  handleGoverningLawChange(event) {
    this.governingLaw = event.target.value;
  }

  handleNoteChange(event) {
    this.note = event.target.value;
  }
}
