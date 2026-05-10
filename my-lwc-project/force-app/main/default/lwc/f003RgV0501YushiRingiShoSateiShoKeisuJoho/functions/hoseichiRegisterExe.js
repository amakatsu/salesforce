/*************************************************************************************************************
 * イベント名   ：  補正値登録
 * イベント概要 ：  与信禀査書査定書計数情報画面の補正値登録処理
 ************************************************************************************************************/
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { RG_DISP_LIST, SUBSYSTEM_ID_RG, RG_CONNECT } from "c/f003RgV0000Const";
import { postRequest } from "c/f003GsV0000CallApi";
import { paddingZero } from "c/f003GsV0000Utils";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { OPERATION, ENDPOINT } from "../f003RgV0501YushiRingiShoSateiShoKeisuJohoConst";
import ConfirmInfo from "c/f003GsV0000ConfirmInfo";
import { YUSRG0501C_I, YUSRG0502C_I } from "c/f003RgV0000MsgConst";
import { RgV0501HoseichiRegisterRequest } from "c/f003RgV0000OpenApiModel";

/**
 * 補正値登録ボタン押下イベント
 */
export async function hoseichiRegisterExe() {
  try {
    // 確認モーダル表示中に画面側で入力チェックエラーが表示されぬよう、
    // ここでは validateElement を含まないメソッドを使う
    const [b1GetItemList] = this.template
      .querySelector("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1")
      .getHoseichiNoCheckList();

    let confirmCheck = false;
    const metaInfo = new RequestMetadataDto();
    metaInfo.setSubSystemId(SUBSYSTEM_ID_RG);
    metaInfo.setDisplayId(RG_DISP_LIST.RgV0501.ID);
    metaInfo.setDisplayName(RG_DISP_LIST.RgV0501.NAME);
    metaInfo.setBranchNo(paddingZero(this.records.hdnBrNo, 7));
    metaInfo.setCustomerNo(this.records.hdnCmNo);
    metaInfo.setLcNo(this.records.hdnRefNo);
    metaInfo.setLcSeqNo("");

    confirmCheck = await ConfirmInfo.open({
      size: "small",
      message: YUSRG0501C_I,
      code: "YUSRG0501C-I"
    });

    if (!confirmCheck) {
      return;
    }

    if (confirmCheck) {
      this.isSpinnerVisible = true;
      this.isServerErrorVisible = false;

      const [b1GetItemList, b1Valid] = this.template
        .querySelector("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1")
        .getHoseichiList();

      const [c2GetItemList, c2Valid] = this.template
        .querySelector("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c2")
        .getHoseichiList();

      const [c6List, c6Valid] = this.template
        .querySelector("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c6")
        .getHoseiriyuList();

      if (b1Valid > 0 || c2Valid > 0 || c6Valid > 0) {
        this.validateErrorHandler();
        return;
      }

      metaInfo.setOperationName(OPERATION.HOSEICHI_REGISTER);

      const reqParam = {
        brNo: this.records.hdnBrNo,
        cmNo: this.records.hdnCmNo,
        loanDiscTotalCorrectionValue: c2GetItemList.loanDiscTotalCorrectionValue,
        internalJpyCorrectionValue: c2GetItemList.internalJpyCorrectionValue,
        forexCreditTotalCorrectionValue: c2GetItemList.forexCreditTotalCorrectionValue,
        shiShoTotalCorrectionValue: c2GetItemList.shiShoTotalCorrectionValue,
        regulationTanpoCorrectionValueRegulationValue:
          b1GetItemList.regulationTanpoCorrectionValueRegulationValue,
        regulationTanpoCorrectionValueJikaBase:
          b1GetItemList.regulationTanpoCorrectionValueJikaBase,
        correctionReason: c6List.correctionReason,
        lockInfo: {
          exclusiveKey:
            this.apiRecordsList.exclusiveKey ?? this.records.hdnRefNo,
          exclusiveCount: this.apiRecordsList.hdnExclusiveCount
        }
      };

      const reqParamsDto = RgV0501HoseichiRegisterRequest.constructFromObject(reqParam);
      const responseResult = await postRequest(metaInfo, ENDPOINT.HOSEICHI_REGISTER, RG_CONNECT, reqParamsDto);

      if (Object.hasOwn(responseResult, "errors")) {
        this.serverErrorHandler(responseResult);
        return;
      }

      this.initialize();
      this.handleRegister();

      const successEvent = new ShowToastEvent({
        title: "Success",
        message: YUSRG0502C_I,
        variant: "success"
      });
      this.dispatchEvent(successEvent);
      this.isSpinnerVisible = false;
    }
  } catch (error) {
    this.systemErrorHandler(error, OPERATION.HOSEICHI_REGISTER);
  }
}
