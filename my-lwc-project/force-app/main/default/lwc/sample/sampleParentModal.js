/************************************************************************************************************* * 画面名   ：  関連禀査情報 * 画面概要 ：  関連禀査情報画面の親コンポーネント ************************************************************************************************************/ import {
  api,
  track
} from "lwc";
import LightningModal from "lightning/modal";
import { getRequest } from "c/f003GsV0000CallApi";
import { paddingZero } from "c/f003GsV0000Utils";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { handleSystemError, showToastError } from "c/f003GsV0000ErrorHandler";
import { CV_DISP_LIST } from "c/f003CvV0000Const";
import { OPERATION, ENDPOINT, BTN_PATTERN } from "./f003CvV0103KanrenRinsaJohoMConst";
import ConfirmInfo from "c/f003GsV0000ConfirmInfo";
import { SUBSYSTEM_ID_COVENANTS, CV_CONNECT } from "c/f003GsV0000Const";
import { YUSCV1701C_I, YUSCV1702C_I, YUSCV1715C_I } from "c/f003CvV0000MsgConst";
import { addExe } from "./functions/sampleAddHandler";
import { changeExe } from "./functions/sampleUpdateHandler";
import { deleteExe } from "./functions/sampleDeleteHandler";
import { CvV0103GetResponse, CvV0103GetCreditApprovalResponse } from "c/f003CvV0000OpenApiModel";
export default class F003CvV0103KanrenRinsaJohoM extends LightningModal {
  // スピナー表示フラグ
  isSpinnerVisible = false;

  // 画面表示フラグ
  isAllVisible = false;

  // 相関エラー表示フラグ
  isServerErrorVisible = false;

  // アクセスエラー表示フラグ
  isAccessErrorVisible = false;

  // 子コンポーネント連携用レコードリスト
  @track apiRecordsList = [];

  parameterList = {};

  // リクエスト業務データ生成用項目
  hdnBrNo = "";
  // 店番
  hdnCmNo = "";
  // 取引先番号
  hdnRefNo = "";
  // 案件番号
  /**   * 親コンポーネントからのレコードデータのgetter   *   * @returns {Object} レコードデータ   */
  @api
  get records() {
    return this._records;
  }

  /**   * 親コンポーネントからのレコードデータのsetter   *   * @param {Object} value レコードデータ   */
  set records(value) {
    this._records = value;

    this.initialize();
  }

  /**   * 初期表示処理   */
  async initialize() {
    try {
      // 各フラグ・変数の初期化
      this.errors = "";

      this.isSpinnerVisible = true;

      this.isServerErrorVisible = false;

      this.isAccessErrorVisible = false;

      // リクエスト業務データ生成用データの設定
      this.hdnBrNo = paddingZero(this.records.hdnBrNo, 7);
      // 店番設定
      this.hdnCmNo = this.records.hdnCmNo;
      // 取引先番号設定
      this.hdnRefNo = this.records.hdnRefNo;
      // 案件番号設定
      // 画面表示用データ取得
      const responseResult = await this.loadInitData(this.records);

      // レスポンスデータ判定
      if (Object.hasOwn(responseResult, "errors")) {
        // エラー時
        // エラー情報の抽出
        this.errors = responseResult.errors;

        // アクセスエラー表示フラグをオン
        this.isAccessErrorVisible = true;

        // スピナーを非表示
        this.isSpinnerVisible = false;

        return;
      }

      // レスポンスDtoの宣言
      const responseTmpDto = {
        ...CvV0103GetResponse.constructFromObject(responseResult)
      };
      const responseDto = {
        ...responseTmpDto
      };
      // 正常終了時
      // レスポンス値格納
      this.apiRecordsList = responseDto;
      // リクエスト業務データ生成用データの設定
      // 遷移元画面の引継ぎ情報を追加
      this.apiRecordsList.parameterList = Object.assign({}, this.records);

      // 画面表示
      this.isAllVisible = true;

      // スピナーを非表示にする。
      this.isSpinnerVisible = false;
    } catch (error) {
      this.systemErrorHandler(error, OPERATION.INIT);
    }
  }

  /**   * 画面表示用データ取得   *   * @param {Object} reqParam リクエストパラメータ   */
  async loadInitData(reqParam) {
    // リクエスト業務データDtoインスタンス化
    const metaInfo = new RequestMetadataDto();

    // リクエスト業務情報セット
    metaInfo.setSubSystemId(SUBSYSTEM_ID_COVENANTS);

    metaInfo.setDisplayId(CV_DISP_LIST.CvV0103.ID);

    metaInfo.setDisplayName(CV_DISP_LIST.CvV0103.NAME);

    metaInfo.setOperationName(OPERATION.INIT);

    metaInfo.setBranchNo(paddingZero(reqParam.hdnBrNo, 7));

    metaInfo.setCustomerNo(reqParam.hdnCmNo);

    metaInfo.setLcNo(reqParam.hdnRefNo);

    metaInfo.setLcSeqNo("");
    //ブランク
    // 画面間引継ぎ情報
    const reqInitParam = {
      hdnRefNo: reqParam.hdnRefNo
    };
    // 外部API連携
    const responseResult = await getRequest(metaInfo, ENDPOINT.INIT, CV_CONNECT, reqInitParam);

    return responseResult;
  }

  /**   * 単項目チェックエラー表示共通処理   */
  validateErrorHandler() {
    // 共通トーストエラー表示
    showToastError.bind(this)();

    // スピナーを非表示
    this.isSpinnerVisible = false;
  }

  /**   * サーバーエラー表示共通処理   */
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

  /**   * 子コンポーネントエラー共通処理   */
  childErrorHandler(event) {
    const error = event.detail.error;

    this.isAllVisible = false;

    this.systemErrorHandler(error, OPERATION.INIT);
  }

  /**   * システムエラー表示共通処理   */
  async systemErrorHandler(error, operationInfo) {
    // 業務情報格納
    // 共通タブ連携用レコードリスト生成
    const metaInfo = new RequestMetadataDto();
    // 業務情報セット
    metaInfo.setSubSystemId(SUBSYSTEM_ID_COVENANTS);

    metaInfo.setDisplayId(CV_DISP_LIST.CvV0103.ID);

    metaInfo.setDisplayName(CV_DISP_LIST.CvV0103.NAME);

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

  /**   *  変更ボタン押下イベント   */
  async handleChangeClick() {
    changeExe.bind(this)();
  }

  /**   *  追加登録ボタン押下イベント   */
  async handleAddClick() {
    addExe.bind(this)();
  }

  /**   *  削除ボタン押下イベント   */
  async handleDeleteClick() {
    deleteExe.bind(this)();
  }

  /**   * 与信禀査（メイン）取得共通処理   * @param {Object} metaInfo リクエストの業務情報を格納したクラス   * @param {string} btnPattern 変更or追加登録ボタン   */
  async getCreditMainCount(metaInfo, btnPattern) {
    // 「変更」or「追加」登録ボタンにより確認モーダルのメッセージ変更
    // 確認モーダル表示用変数
    let modalMsg = "";

    let modalCode = "";

    let confirmCheck = false;

    if (btnPattern === BTN_PATTERN.UPDATE) {
      // 変更ボタン押下時
      modalMsg = YUSCV1702C_I;

      modalCode = "YUSCV1702C-I";

      // ヘッダー情報セット（ここではoperationNameのみ）
      metaInfo.setOperationName(OPERATION.UPDATE);
    } else {
      // 追加登録ボタン押下時
      modalMsg = YUSCV1701C_I;

      modalCode = "YUSCV1701C-I";

      // ヘッダー情報セット（ここではoperationNameのみ）
      metaInfo.setOperationName(OPERATION.ADD);
    }

    const reqParam = {
      hdnRefNo: this.records.hdnRefNo
    };
    // 外部API連携
    const responseResult = await getRequest(
      metaInfo,
      ENDPOINT.GET_MAIN_CREDIT_APPROVAL,
      CV_CONNECT,
      reqParam
    );

    // レスポンスDtoの宣言
    const responseTmpDto = {
      ...CvV0103GetCreditApprovalResponse.constructFromObject(responseResult)
    };
    const responseDto = {
      ...responseTmpDto
    };
    if (responseDto.count > 0) {
      //与信禀査（メイン）取得APIのレスポンス値.件数＞０の場合
      //確認モーダル表示
      confirmCheck = await ConfirmInfo.open({
        size: "small",

        message: YUSCV1715C_I,

        code: "YUSCV1715C-I"
      });
    } else {
      //区分選択＝「与信禀査（メイン）」かつ、
      //与信禀査（メイン）取得APIのレスポンス値.件数=０の場合
      //確認モーダル表示
      confirmCheck = await ConfirmInfo.open({
        size: "small",

        message: modalMsg,

        code: modalCode
      });
    }

    return confirmCheck;
  }
}
