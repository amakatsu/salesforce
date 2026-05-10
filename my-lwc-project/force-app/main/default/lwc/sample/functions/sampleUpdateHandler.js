/************************************************************************************************************* * イベント名   ：  変更 * イベント概要 ：  関連禀査情報の変更処理 ************************************************************************************************************/ import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { CV_DISP_LIST } from "c/f003CvV0000Const";
import { CATEGORY_SELECTION } from "c/f003CvV0000CodeConst";
import { postRequest } from "c/f003GsV0000CallApi";
import { paddingZero } from "c/f003GsV0000Utils";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { OPERATION, ENDPOINT, BTN_PATTERN } from "../../f003CvV0103KanrenRinsaJohoMConst";
import ConfirmInfo from "c/f003GsV0000ConfirmInfo";
import { SUBSYSTEM_ID_COVENANTS, CV_CONNECT } from "c/f003GsV0000Const";
import { YUSGS5036C_I } from "c/f003GsV0000MsgConst";
import { YUSCV1702C_I } from "c/f003CvV0000MsgConst";
import { CvV0103UpdateRequest } from "c/f003CvV0000OpenApiModel";
/** *  変更ボタン押下イベント */ export async function changeExe() {
  try {
    // 行選択チェック
    let checkResult = "";

    checkResult = await this.template
      .querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1")
      .checkSelectedRows();

    // チェック問題なければ先進め
    // 行選択されている場合、checkResult=''
    if (checkResult !== "") {
      return;
    }

    // データ抽出(確認モーダル表示前なので、ここではvalidateElement処理がないメソッドを呼ぶ)
    // ここでvalidateElementが組まれてるメソッドを呼ぶと、確認モーダル表示中に画面で入力チェックエラーが表示されてしまう。
    const [child1GetItemList] = this.template
      .querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1")
      .getChangeNoCheckList();

    // 確認モーダル表示チェック用
    let confirmCheck = false;

    // リクエスト業務データDtoインスタンス化
    const metaInfo = new RequestMetadataDto();

    // ヘッダー情報セット
    metaInfo.setSubSystemId(SUBSYSTEM_ID_COVENANTS);

    metaInfo.setDisplayId(CV_DISP_LIST.CvV0103.ID);

    metaInfo.setDisplayName(CV_DISP_LIST.CvV0103.NAME);

    metaInfo.setBranchNo(paddingZero(this.records.hdnBrNo, 7));

    metaInfo.setCustomerNo(this.records.hdnCmNo);

    metaInfo.setLcNo(this.records.hdnRefNo);

    metaInfo.setLcSeqNo("");
    //ブランク
    if (child1GetItemList.categorySelect === CATEGORY_SELECTION.MAIN_CREDIT_APPROVAL) {
      // 区分選択＝「与信禀査（メイン）」の場合
      // 与信禀査（メイン）取得処理を呼ぶ。
      confirmCheck = await this.getCreditMainCount(metaInfo, BTN_PATTERN.UPDATE);
    } else {
      //区分選択＝「与信禀査（メイン）」以外の場合
      //確認モーダル表示
      confirmCheck = await ConfirmInfo.open({
        size: "small",

        message: YUSCV1702C_I,

        code: "YUSCV1702C-I"
      });
    }

    if (!confirmCheck) {
      //キャンセルの場合
      return;
    }

    //確認モーダルOK選択時、処理入る
    if (confirmCheck) {
      // 変数初期化
      this.isSpinnerVisible = true;

      this.isServerErrorVisible = false;

      // データ抽出、単項目チェック
      const [child1GetItemList, child1Valid] = this.template
        .querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1")
        .getChangeList();

      const childGetRowsList = this.template
        .querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1")
        .getSelectRecordList();

      if (child1Valid > 0) {
        // エラー時
        // 単項目チェックエラー表示共通処理に連携
        this.validateErrorHandler();

        return;
      }

      // 変更API呼び出し
      // ヘッダー情報セット（operationName以外は上記で設定しているため省略）
      metaInfo.setOperationName(OPERATION.UPDATE);

      // リクエストパラメータ初期化
      let reqHdnParam = {};
      // リクエストパラメータ設定
      if (this.records.hdnSourceDispId === CV_DISP_LIST.CvV0501.ID) {
        // 遷移元が「抵触・要管理シート」
        reqHdnParam = {
          hdnRefNo: this.records.hdnRefNo,

          hdnJokoId: this.records.hdnJokoId,

          seqNo: childGetRowsList[0].seqNo,

          hdnViolationFlg: true,

          hdnExclusiveCount: this.apiRecordsList.hdnExclusiveCount
        };
      } else {
        // 遷移元が「抵触・要管理シート」以外
        reqHdnParam = {
          hdnRefNo: this.records.hdnRefNo,

          seqNo: childGetRowsList[0].seqNo,

          hdnViolationFlg: false,

          hdnExclusiveCount: this.apiRecordsList.hdnExclusiveCount
        };
      }

      const reqParam = Object.assign(reqHdnParam, child1GetItemList);

      // リクエストDtoの生成
      const reqParamsDto = CvV0103UpdateRequest.constructFromObject(reqParam);

      // 外部API連携
      const responseResult = await postRequest(metaInfo, ENDPOINT.UPDATE, CV_CONNECT, reqParamsDto);

      // レスポンスデータ判定
      if (Object.hasOwn(responseResult, "errors")) {
        // エラー時
        // サーバーエラー表示共通処理に連携
        this.serverErrorHandler(responseResult);

        return;
      }

      // 初期表示API呼び出し
      this.initialize();

      // 一覧部の行選択情報をクリア
      this.template.querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1").clearSelectedRows();

      // 正常終了時
      // トーストメッセージ表示
      const successEvent = new ShowToastEvent({
        title: "Success",

        message: YUSGS5036C_I,

        variant: "success"
      });

      this.dispatchEvent(successEvent);

      // スピナーを非表示
      this.isSpinnerVisible = false;
    }
  } catch (error) {
    this.systemErrorHandler(error, OPERATION.UPDATE);
  }
}
