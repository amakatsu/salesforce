/**
 * 計数サマリー・補正理由等コンポーネント (C6)
 *
 * 禀査番号・基準日・計数サマリー(限度算入/規定担保/保全率)・プール区分・補正理由を表示する。
 * 編集可能なテーブル数値セルを持たないため、applySavedHighlight は空実装。
 */
import { LightningElement, api, track } from "lwc";
import { makeTestData } from "c/testDataGenerator";
import { validateElement } from "c/f003GsV0000DataValidation";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";

/* ── 定数 ── */

const ACTIVE_SECTIONS = "abcdefghijklmnopqr".split("");

/* ── C6 補正値登録：取得対象キー / 必須キー（sample の C1_CHANGE_LIST 等と同構造） ── */
/* correctionReason は設計書 03_request_response.md にて required:– / ByteLength 0-100。
   バイト長制限は HTML 側 max-length="100" で担保。NotNull バリデーション不要ゆえ REQ_LIST は空 */

const C6_CHANGE_LIST = ["correctionReason"];
const C6_CHANGE_REQ_LIST = [];
const C6_ADD_LIST = ["correctionReason"];
const C6_ADD_REQ_LIST = [];

/* ── コンポーネント ── */

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC6 extends LightningElement {

  /* ── アコーディオン設定 ── */

  activeSections = ACTIVE_SECTIONS;

  /* ── ヘッダ情報 ── */

  reviewNumber = makeTestData("numeric", 4);
  referenceDate = "2025/3/31";

  /* ── 計数サマリー ── */

  generalCreditLimit = makeTestData("numeric", 7);
  marketCreditInclusion = makeTestData("numeric", 5);
  regulatoryCollateral = makeTestData("numeric", 7);
  protectionRate = "999.99";

  /* ── プール区分 ── */

  poolCategory = makeTestData("numeric", 2);

  /* ── 入力record（補正理由 correctionReason を保持。親は @api getChangeList / getAddList で取得） ── */

  @track record = {};

  /* ── 公開API ── */

  @api
  applySavedHighlight() {
    // C6は編集可能なテーブル数値セルを持たないため空実装
  }

  /**
   * 変更処理：子コンポーネントデータ取得
   */
  @api
  getChangeList() {
    let valid = 0;
    const data = this.template.querySelectorAll("[data-id]");
    const [itemList, dataList] = getComponentDataList(data, C6_CHANGE_LIST);
    valid = validateElement(dataList, C6_CHANGE_REQ_LIST, data);
    return [itemList, valid];
  }

  /**
   * 変更処理：子コンポーネントデータ取得＿バリデーションチェックなし
   */
  @api
  getChangeNoCheckList() {
    const data = this.template.querySelectorAll("[data-id]");
    const [itemList] = getComponentDataList(data, C6_CHANGE_LIST);
    return [itemList];
  }

  /**
   * 追加登録処理：子コンポーネントデータ取得
   */
  @api
  getAddList() {
    let valid = 0;
    const data = this.template.querySelectorAll("[data-id]");
    const [itemList, dataList] = getComponentDataList(data, C6_ADD_LIST);
    valid = validateElement(dataList, C6_ADD_REQ_LIST, data);
    return [itemList, valid];
  }

  /**
   * 追加登録処理：子コンポーネントデータ取得＿バリデーションチェックなし
   */
  @api
  getAddNoCheckList() {
    const data = this.template.querySelectorAll("[data-id]");
    const [itemList] = getComponentDataList(data, C6_ADD_LIST);
    return [itemList];
  }

  /**
   * 補正理由取得処理：子コンポーネントデータ取得
   * バリデーションは validateElement が担い、valid > 0 で親側 validateErrorHandler が発火する
   */
  @api
  getHoseiriyuList() {
    let valid = 0;
    const data = this.template.querySelectorAll("[data-id]");
    const [itemList, dataList] = getComponentDataList(data, C6_CHANGE_LIST);
    valid = validateElement(dataList, C6_CHANGE_REQ_LIST, data);
    return [itemList, valid];
  }

  /**
   * 入力項目値変更イベント
   */
  handleRecordValueChange(event) {
    // データレコードの更新
    this.record[event.target.dataset.id] = event.target.value;

    // バリデーションチェック実施
    const inputElement = event.target;
    const childDataList = [inputElement];
    validateElement(childDataList);
  }
}
