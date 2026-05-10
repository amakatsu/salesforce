/************************************************************************************************************* * イベント名   ：  削除 * イベント概要 ：  関連禀査情報の削除処理 ************************************************************************************************************/ import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { CV_DISP_LIST } from "c/f003CvV0000Const";
import { CATEGORY_SELECTION } from "c/f003CvV0000CodeConst";
import { deleteRequest } from "c/f003GsV0000CallApi";
import { paddingZero } from "c/f003GsV0000Utils";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { OPERATION, ENDPOINT } from "../../f003CvV0103KanrenRinsaJohoMConst";
import ConfirmInfo from "c/f003GsV0000ConfirmInfo";
import { SUBSYSTEM_ID_COVENANTS, CV_CONNECT } from "c/f003GsV0000Const";
import { YUSGS5037C_I } from "c/f003GsV0000MsgConst";
import { YUSCV1704C_I, YUSCV1703C_I } from "c/f003CvV0000MsgConst";
/** *  削除ボタン押下イベント */ export async function deleteExe() {
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

    const childGetRowsList = this.template
      .querySelector("c-f003-cv-v0103-kanren-rinsa-joho-m-c1")
      .getSelectRecordList();

    // 確認モーダル表示チェック用
    let confirmCheck = false;

    if (childGetRowsList[0].creditRinsaValue === CATEGORY_SELECTION.MAIN_CREDIT_APPROVAL) {
      // 選択行＝「与信禀査（メイン）」の場合
      //確認モーダル表示
      confirmCheck = await ConfirmInfo.open({
        size: "small",

        message: YUSCV1704C_I,

        code: "YUSCV1704C-I"
      });
    } else {
      // 選択行＝「与信禀査（メイン）」以外の場合
      //確認モーダル表示
      confirmCheck = await ConfirmInfo.open({
        size: "small",

        message: YUSCV1703C_I,

        code: "YUSCV1703C-I"
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

      //削除API呼び出し
      // リクエスト業務データDtoインスタンス化
      const metaInfo = new RequestMetadataDto();

      // ヘッダー情報セット
      metaInfo.setSubSystemId(SUBSYSTEM_ID_COVENANTS);

      metaInfo.setDisplayId(CV_DISP_LIST.CvV0103.ID);

      metaInfo.setDisplayName(CV_DISP_LIST.CvV0103.NAME);

      metaInfo.setOperationName(OPERATION.DELETE);

      metaInfo.setBranchNo(paddingZero(this.records.hdnBrNo, 7));

      metaInfo.setCustomerNo(this.records.hdnCmNo);

      metaInfo.setLcNo(this.records.hdnRefNo);

      metaInfo.setLcSeqNo("");
      //ブランク
      // リクエストパラメータ初期化
      let reqParam = {};
      // リクエストパラメータ設定
      if (this.records.hdnSourceDispId === CV_DISP_LIST.CvV0501.ID) {
        // 遷移元が「抵触・要管理シート」
        reqParam = {
          hdnRefNo: this.records.hdnRefNo,

          hdnJokoId: this.records.hdnJokoId,

          seqNo: childGetRowsList[0].seqNo,

          hdnViolationFlg: true,

          hdnExclusiveCount: this.apiRecordsList.hdnExclusiveCount
        };
      } else {
        // 遷移元が「抵触・要管理シート」以外
        reqParam = {
          hdnRefNo: this.records.hdnRefNo,

          seqNo: childGetRowsList[0].seqNo,

          hdnViolationFlg: false,

          hdnExclusiveCount: this.apiRecordsList.hdnExclusiveCount
        };
      }

      // 外部API連携
      const responseResult = await deleteRequest(metaInfo, ENDPOINT.DELETE, CV_CONNECT, reqParam);

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

        message: YUSGS5037C_I,

        variant: "success"
      });

      this.dispatchEvent(successEvent);

      // スピナーを非表示
      this.isSpinnerVisible = false;
    }
  } catch (error) {
    this.systemErrorHandler(error, OPERATION.DELETE);
  }
}
