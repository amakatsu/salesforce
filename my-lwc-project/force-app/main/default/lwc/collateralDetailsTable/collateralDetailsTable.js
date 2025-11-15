import { LightningElement, track } from 'lwc';

/**
 * 担保詳細フォームコンポーネント
 * 画像参照に基づいたフォームレイアウト
 */
export default class CollateralDetailsTable extends LightningElement {
  // フォームデータ（モックデータ）
  @track collateralGuarantee = '〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇';
  @track selectedDetail = '';
  @track jurisdiction = '〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇';
  @track governingLaw = '〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇';
  @track note = '〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇';

  /**
   * 担保詳細のコンボボックスオプション
   */
  detailOptions = [
    { label: '不動産担保', value: '不動産担保' },
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

  /**
   * Collateral/Guarantee入力変更ハンドラー
   */
  handleCollateralChange(event) {
    this.collateralGuarantee = event.target.value;
  }

  /**
   * 担保詳細コンボボックス変更ハンドラー
   */
  handleDetailChange(event) {
    this.selectedDetail = event.target.value;
  }

  /**
   * Jurisdiction入力変更ハンドラー
   */
  handleJurisdictionChange(event) {
    this.jurisdiction = event.target.value;
  }

  /**
   * Governing Law入力変更ハンドラー
   */
  handleGoverningLawChange(event) {
    this.governingLaw = event.target.value;
  }

  /**
   * Note変更ハンドラー
   */
  handleNoteChange(event) {
    this.note = event.target.value;
  }
}
