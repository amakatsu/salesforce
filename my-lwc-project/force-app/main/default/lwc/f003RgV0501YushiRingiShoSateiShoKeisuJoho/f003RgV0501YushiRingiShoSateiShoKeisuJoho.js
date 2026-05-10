import { LightningElement, api, track } from "lwc";
import { switchingTabs } from "c/f003GsV0000SwitchingTabs";
import { handleSystemError, showToastError } from "c/f003GsV0000ErrorHandler";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { SUBSYSTEM_ID_RG } from "c/f003GsV0000Const";
import { RG_DISP_LIST } from "c/f003RgV0000Const";
import { OPERATION } from "./f003RgV0501YushiRingiShoSateiShoKeisuJohoConst";
import { hoseichiRegisterExe } from "./functions/hoseichiRegisterExe";

export default class f003RgV0501YushiRingiShoSateiShoKeisuJoho extends LightningElement {
  // スピナー表示フラグ
  isSpinnerVisible = false;

  // 画面表示フラグ
  isAllVisible = true;

  // 相関エラー表示フラグ
  isServerErrorVisible = false;

  // アクセスエラー表示フラグ
  isAccessErrorVisible = false;

  // 計算・補正値登録ボタン表示フラグ
  showCalculationAndRegisterButtons = true;

  // 子コンポーネント連携用レコードリスト
  @track apiRecordsList = {};

  // リクエスト業務データ生成用項目
  hdnBrNo = "";
  // 店番
  hdnCmNo = "";
  // 取引先番号
  hdnRefNo = "";
  // 案件番号
  /**
   * 親コンポーネントからのレコードデータのgetter
   *
   * @returns {Object} レコードデータ
   */
  @api
  get records() {
    return this._records;
  }

  /**
   * 親コンポーネントからのレコードデータのsetter
   *
   * @param {Object} value レコードデータ
   */
  set records(value) {
    this._records = value;
  }

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
    for (const selector of selectors) {
      const component = this.template.querySelector(selector);
      if (component) {
        component.applySavedHighlight();
      }
    }
  }

  /**
   *  補正値登録ボタン押下イベント
   */
  async handleHoseichiRegister() {
    hoseichiRegisterExe.bind(this)();
  }

  /**
   * 単項目チェックエラー表示共通処理
   */
  validateErrorHandler() {
    // 共通トーストエラー表示
    showToastError.bind(this)();

    // スピナーを非表示
    this.isSpinnerVisible = false;
  }

  /**
   * サーバーエラー表示共通処理
   */
  serverErrorHandler(responseResult) {
    // エラー情報の抽出
    this.errors = responseResult.errors;

    // エラー対象フィールド取得処理（第4期では利用無しのため省略）
    // 相関エラー表示フラグをオン
    this.isServerErrorVisible = true;

    // 共通トーストエラー表示
    showToastError.bind(this)();

    // スピナーを非表示
    this.isSpinnerVisible = false;
  }

  /**
   * 子コンポーネントエラー共通処理
   */
  childErrorHandler(event) {
    const error = event.detail.error;

    this.isAllVisible = false;

    this.systemErrorHandler(error, OPERATION.INIT);
  }

  /**
   * システムエラー表示共通処理
   */
  async systemErrorHandler(error, operationInfo) {
    // 業務情報格納
    // 共通タブ連携用レコードリスト生成
    const metaInfo = new RequestMetadataDto();
    // 業務情報セット
    metaInfo.setSubSystemId(SUBSYSTEM_ID_RG);

    metaInfo.setDisplayId(RG_DISP_LIST.RgV0501.ID);

    metaInfo.setDisplayName(RG_DISP_LIST.RgV0501.NAME);

    metaInfo.setOperationName(operationInfo);

    metaInfo.setBranchNo(this.hdnBrNo);

    metaInfo.setCustomerNo(this.hdnCmNo);

    metaInfo.setLcNo(this.hdnRefNo);

    metaInfo.setLcSeqNo("");

    // 共通システムエラー処理に連携
    handleSystemError(error, metaInfo);

    // スピナーを非表示
    this.isSpinnerVisible = false;
  }
}
