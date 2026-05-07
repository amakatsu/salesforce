import { LightningElement, api } from "lwc";
import registCorrectValue from "@salesforce/apex/RinsashoCntInfoApex.registCorrectValue";

const EVENT_REGISTER_SUCCESS = "registersuccess";
const EVENT_REGISTER_ERROR = "registererror";

// 必須項目不足時のクライアント側エラーメッセージ。マジックストリング回避のため定数化。
const MSG_REQUIRED_FIELDS_MISSING =
  "必須項目（店番・取引先番号・排他ロック情報）が不足しております。";

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 extends LightningElement {
  @api showCalculationAndRegisterButtons;

  @api brNo;
  @api cmNo;
  @api correctionValues;
  @api correctionReason;
  @api lockInfo;

  isLoading = false;

  /** プレースホルダー: 実装接続時に個別ハンドラに置き換え */
  handleAction() {
    // TODO: 実装接続時にdata-action属性等で分岐
  }

  handleCalculate() {
    this.dispatchEvent(new CustomEvent("calculate"));
  }

  /**
   * 補正値登録ボタン押下時の処理。
   * 必須項目チェック → ペイロード組立 → Apex 呼出を順に行い、結果を CustomEvent で親へ通知する。
   * @fires registersuccess
   * @fires registererror
   */
  async handleRegister() {
    if (!this.hasRequiredFields()) {
      this.notifyError(MSG_REQUIRED_FIELDS_MISSING);
      return;
    }

    this.isLoading = true;
    try {
      const payload = this.buildRequestPayload();
      const response = await registCorrectValue({ request: payload });
      this.notifySuccess(response);
    } catch (error) {
      // Apex 例外は error.body.message にメッセージが入る慣例。通信例外等で body が無い場合は文字列化でフォールバック。
      const message = error?.body?.message ?? String(error);
      this.notifyError(message);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * 必須 3 項目（brNo / cmNo / lockInfo）が揃っているか判定する。
   * @returns {boolean} 必須項目がすべて存在する場合 true
   */
  hasRequiredFields() {
    return Boolean(this.brNo) && Boolean(this.cmNo) && Boolean(this.lockInfo);
  }

  /**
   * Apex `registCorrectValue` に渡すリクエスト Body を組み立てる。
   * `correctionValues` の 6 補正値項目はサーバ側 DTO がフラット構造のためフラット展開する。
   * @returns {object} Apex リクエスト Body
   */
  buildRequestPayload() {
    const cv = this.correctionValues ?? {};
    return {
      brNo: this.brNo,
      cmNo: this.cmNo,
      loanDiscTotalCorrectionValue: cv.loanDiscTotalCorrectionValue ?? null,
      internalJpyCorrectionValue: cv.internalJpyCorrectionValue ?? null,
      forexCreditTotalCorrectionValue: cv.forexCreditTotalCorrectionValue ?? null,
      shiShoTotalCorrectionValue: cv.shiShoTotalCorrectionValue ?? null,
      regulationTanpoCorrectionValueRegulationValue:
        cv.regulationTanpoCorrectionValueRegulationValue ?? null,
      regulationTanpoCorrectionValueJikaBase:
        cv.regulationTanpoCorrectionValueJikaBase ?? null,
      correctionReason: this.correctionReason ?? null,
      lockInfo: this.lockInfo
    };
  }

  /**
   * 登録成功通知をディスパッチする。
   * @param {object} response Apex の戻り値（更新後 lockInfo を含む）
   * @fires registersuccess
   */
  notifySuccess(response) {
    this.dispatchEvent(
      new CustomEvent(EVENT_REGISTER_SUCCESS, {
        detail: { lockInfo: response?.lockInfo ?? null }
      })
    );
  }

  /**
   * 登録失敗通知をディスパッチする。
   * @param {string} message エラーメッセージ
   * @fires registererror
   */
  notifyError(message) {
    this.dispatchEvent(
      new CustomEvent(EVENT_REGISTER_ERROR, {
        detail: { message }
      })
    );
  }
}
