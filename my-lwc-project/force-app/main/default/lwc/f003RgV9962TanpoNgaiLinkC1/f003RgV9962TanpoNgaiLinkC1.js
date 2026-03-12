import { LightningElement, track } from 'lwc';
 
// ========================================
// 定数定義: サンプルデータ
// ========================================
 
/** 32文字のサンプルテキスト */
const SAMPLE_TEXT_32 = 'w'.repeat(66);
 
/** 366文字のサンプルテキスト */
const SAMPLE_TEXT_366 = 'w'.repeat(366);
 
// ========================================
// 定数定義: 選択肢オプション
// ========================================
 
/**
* 担保詳細のコンボボックスオプション
*/
const DETAIL_OPTIONS = [
  { label: '一般法人保証（非上場）', value: '不動産担保' },
  { label: '動産担保', value: '動産担保' },
  { label: '債権担保', value: '債権担保' },
  { label: '保証人', value: '保証人' },
  { label: '連帯保証', value: '連帯保証' },
  { label: '根保証', value: '根保証' },
  { label: '質権', value: '質権' },
  { label: '抵当権', value: '抵当権' },
  { label: '譲渡担保', value: '譲渡担保' },
  { label: 'その他', value: 'その他' }
];
 
// ========================================
// コンポーネントクラス
// ========================================
 
/**
* 担保詳細フォームコンポーネント
* 担保/保証の詳細情報を入力するフォーム
*/
export default class f003RgV9962TanpoNgaiLinkC1 extends LightningElement {
  // フォームデータ
  @track collateralGuarantee = SAMPLE_TEXT_32;
  @track selectedDetail = '';
  @track jurisdiction = SAMPLE_TEXT_32;
  @track governingLaw = SAMPLE_TEXT_32;
  @track note = SAMPLE_TEXT_366;
 
  /**
   * 担保詳細のコンボボックスオプション
   * @returns {Array} オプションリスト
   */
  get detailOptions() {
    return DETAIL_OPTIONS;
  }
 
  // ========================================
  // イベントハンドラー
  // ========================================
 
  /**
   * Collateral/Guarantee入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleCollateralChange(event) {
    this.collateralGuarantee = event.target.value;
  }
 
  /**
   * 担保詳細コンボボックス変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleDetailChange(event) {
    this.selectedDetail = event.target.value;
  }
 
  /**
   * Jurisdiction入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleJurisdictionChange(event) {
    this.jurisdiction = event.target.value;
  }
 
  /**
   * Governing Law入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleGoverningLawChange(event) {
    this.governingLaw = event.target.value;
  }
 
  /**
   * Note変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleNoteChange(event) {
    this.note = event.target.value;
  }
}