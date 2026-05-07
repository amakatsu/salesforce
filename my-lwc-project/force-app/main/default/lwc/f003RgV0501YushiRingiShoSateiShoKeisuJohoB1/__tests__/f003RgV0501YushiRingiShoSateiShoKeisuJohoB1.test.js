/**
 * f003RgV0501YushiRingiShoSateiShoKeisuJohoB1 LWC の Jest テスト。
 * t-wada 流: describe/it 構造、日本語仕様文 it 名、given/when/then、test.each パラメータ化、1 テスト 1 観点。
 *
 * 環境: @salesforce/sfdx-lwc-jest 公式パターン（jest.config.js で jestConfig を継承）。
 *      preset が createElement / lwc モジュール / @api decorators / @salesforce/apex / lightning-stubs を一括提供する。
 *
 * 呼出方式: ハンドラは @api ではないため外部から直接呼べない。
 *          shadowRoot.querySelector('lightning-button[label="..."]').click() でユーザ操作をシミュレートする。
 */

import { createElement } from "lwc";
import F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 from "c/f003RgV0501YushiRingiShoSateiShoKeisuJohoB1";
import registCorrectValue from "@salesforce/apex/RinsashoCntInfoApex.registCorrectValue";

jest.mock(
  "@salesforce/apex/RinsashoCntInfoApex.registCorrectValue",
  () => ({ default: jest.fn() }),
  { virtual: true }
);

// 標準的な flushPromises（jsdom 環境下のマイクロタスク完了待ち）
const flushPromises = () => Promise.resolve();

/**
 * 指定 label の lightning-button を取得する。未描画なら null。
 * lightning-stubs では @api プロパティは attribute に反射されないため、
 * querySelectorAll で全 lightning-button を取得し .label プロパティで find する。
 */
function findButtonByLabel(element, label) {
  const buttons = element.shadowRoot.querySelectorAll("lightning-button");
  return Array.from(buttons).find((b) => b.label === label) || null;
}

/** 指定 label の lightning-button を click する。未描画なら明示的にエラーを投げる。 */
function clickButton(element, label) {
  const btn = findButtonByLabel(element, label);
  if (!btn) {
    throw new Error(`lightning-button[label="${label}"] is not rendered`);
  }
  btn.click();
}

describe("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1", () => {
  let element;

  beforeEach(() => {
    jest.clearAllMocks();
    element = createElement(
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1",
      { is: F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 }
    );
  });

  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
  });

  // ==========================================================================
  // レンダリング（プロパティ駆動の表示分岐）
  // ==========================================================================

  describe("レンダリング", () => {
    it("初期状態（showCalculationAndRegisterButtons 未設定）では「補正値登録」ボタンが描画されない", () => {
      // given - beforeEach で element 生成のみ

      // when
      document.body.appendChild(element);

      // then
      const registerButton = findButtonByLabel(element, "補正値登録");
      expect(registerButton).toBeNull();
    });

    it("showCalculationAndRegisterButtons=true のとき、「補正値登録」ボタンが描画される", async () => {
      // given
      element.showCalculationAndRegisterButtons = true;

      // when
      document.body.appendChild(element);
      await flushPromises();

      // then
      const registerButton = findButtonByLabel(element, "補正値登録");
      expect(registerButton).not.toBeNull();
    });

    it("showCalculationAndRegisterButtons=false のとき、「補正値登録」ボタンは描画されない", async () => {
      // given
      element.showCalculationAndRegisterButtons = false;

      // when
      document.body.appendChild(element);
      await flushPromises();

      // then
      const registerButton = findButtonByLabel(element, "補正値登録");
      expect(registerButton).toBeNull();
    });
  });

  // ==========================================================================
  // handleCalculate（「計算」ボタン）
  // ==========================================================================

  describe("handleCalculate", () => {
    it("「計算」ボタン押下で calculate CustomEvent を 1 回 dispatch する", async () => {
      // given - 「計算」ボタンを描画させるため showCalculationAndRegisterButtons=true
      element.showCalculationAndRegisterButtons = true;
      document.body.appendChild(element);
      await flushPromises();
      const handler = jest.fn();
      element.addEventListener("calculate", handler);

      // when
      clickButton(element, "計算");

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.type).toBe("calculate");
    });
  });

  // ==========================================================================
  // handleRegister（「補正値登録」ボタン）
  // ==========================================================================

  describe("handleRegister", () => {
    const VALID_BR_NO = "010";
    const VALID_CM_NO = "9019149";
    const VALID_LOCK_INFO = {
      exclusiveKey: "rkANKEN111111111111",
      exclusiveCount: 1
    };
    const VALID_CORRECTION_VALUES = {
      loanDiscTotalCorrectionValue: 1000,
      internalJpyCorrectionValue: 2000,
      forexCreditTotalCorrectionValue: 3000,
      shiShoTotalCorrectionValue: 4000,
      regulationTanpoCorrectionValueRegulationValue: 5000,
      regulationTanpoCorrectionValueJikaBase: 6000
    };
    const VALID_REASON = "テスト補正理由";

    beforeEach(async () => {
      element.showCalculationAndRegisterButtons = true;
      element.brNo = VALID_BR_NO;
      element.cmNo = VALID_CM_NO;
      element.lockInfo = { ...VALID_LOCK_INFO };
      element.correctionValues = { ...VALID_CORRECTION_VALUES };
      element.correctionReason = VALID_REASON;
      document.body.appendChild(element);
      await flushPromises();
    });

    it("「補正値登録」押下で Apex registCorrectValue を { request: フラットペイロード } 形式で 1 回呼び出す", async () => {
      // given
      registCorrectValue.mockResolvedValue({
        lockInfo: { exclusiveKey: "KEY-OK", exclusiveCount: 2 }
      });

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(registCorrectValue).toHaveBeenCalledTimes(1);
      expect(registCorrectValue).toHaveBeenCalledWith({
        request: {
          brNo: VALID_BR_NO,
          cmNo: VALID_CM_NO,
          loanDiscTotalCorrectionValue: 1000,
          internalJpyCorrectionValue: 2000,
          forexCreditTotalCorrectionValue: 3000,
          shiShoTotalCorrectionValue: 4000,
          regulationTanpoCorrectionValueRegulationValue: 5000,
          regulationTanpoCorrectionValueJikaBase: 6000,
          correctionReason: VALID_REASON,
          lockInfo: VALID_LOCK_INFO
        }
      });
    });

    it("Apex 成功時、registersuccess CustomEvent を更新後 lockInfo 詳細とともに dispatch する", async () => {
      // given
      const successLockInfo = { exclusiveKey: "KEY-OK", exclusiveCount: 2 };
      registCorrectValue.mockResolvedValue({ lockInfo: successLockInfo });
      const handler = jest.fn();
      element.addEventListener("registersuccess", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.type).toBe("registersuccess");
      expect(event.detail.lockInfo).toEqual(successLockInfo);
    });

    it("Apex 失敗時、registererror CustomEvent を error.body.message 詳細とともに dispatch する", async () => {
      // given
      registCorrectValue.mockRejectedValue({
        body: { message: "楽観ロックエラー" }
      });
      const handler = jest.fn();
      element.addEventListener("registererror", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.type).toBe("registererror");
      expect(event.detail.message).toBe("楽観ロックエラー");
    });

    it.each([
      ["brNo 未設定", null, VALID_CM_NO, { ...VALID_LOCK_INFO }],
      ["cmNo 未設定", VALID_BR_NO, null, { ...VALID_LOCK_INFO }],
      ["lockInfo 未設定", VALID_BR_NO, VALID_CM_NO, null]
    ])(
      "%s の場合、Apex を呼ばず registererror（必須項目不足メッセージ）を dispatch する",
      async (_caseName, brNo, cmNo, lockInfo) => {
        // given
        element.brNo = brNo;
        element.cmNo = cmNo;
        element.lockInfo = lockInfo;
        const errorHandler = jest.fn();
        element.addEventListener("registererror", errorHandler);
        await flushPromises();

        // when
        clickButton(element, "補正値登録");
        await flushPromises();

        // then
        expect(registCorrectValue).not.toHaveBeenCalled();
        expect(errorHandler).toHaveBeenCalledTimes(1);
        const event = errorHandler.mock.calls[0][0];
        expect(event.type).toBe("registererror");
        expect(event.detail.message).toContain("必須項目");
      }
    );

    it("ペイロード仕様: brNo 3 桁 / cmNo 7 桁 / 補正値 6 項目フラット展開 / lockInfo オブジェクト構造", async () => {
      // given
      registCorrectValue.mockResolvedValue({ lockInfo: { ...VALID_LOCK_INFO } });

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      const callArg = registCorrectValue.mock.calls[0][0];
      expect(callArg).toHaveProperty("request");
      const payload = callArg.request;
      expect(payload.brNo).toMatch(/^\d{3}$/);
      expect(payload.cmNo).toMatch(/^\d{7}$/);
      expect(payload).toHaveProperty("loanDiscTotalCorrectionValue");
      expect(payload).toHaveProperty("internalJpyCorrectionValue");
      expect(payload).toHaveProperty("forexCreditTotalCorrectionValue");
      expect(payload).toHaveProperty("shiShoTotalCorrectionValue");
      expect(payload).toHaveProperty("regulationTanpoCorrectionValueRegulationValue");
      expect(payload).toHaveProperty("regulationTanpoCorrectionValueJikaBase");
      expect(payload).not.toHaveProperty("correctionValues");
      expect(payload.lockInfo).toEqual(
        expect.objectContaining({
          exclusiveKey: expect.any(String),
          exclusiveCount: expect.any(Number)
        })
      );
    });
  });

  // ==========================================================================
  // handleRegister - 境界・例外ケース
  // ==========================================================================

  describe("handleRegister - 境界・例外ケース", () => {
    const VALID_BR_NO = "010";
    const VALID_CM_NO = "9019149";
    const VALID_LOCK_INFO = {
      exclusiveKey: "rkANKEN111111111111",
      exclusiveCount: 1
    };

    beforeEach(async () => {
      element.showCalculationAndRegisterButtons = true;
      element.brNo = VALID_BR_NO;
      element.cmNo = VALID_CM_NO;
      element.lockInfo = { ...VALID_LOCK_INFO };
      // correctionValues / correctionReason は各ケースで個別設定
      document.body.appendChild(element);
      await flushPromises();
    });

    it("correctionValues が undefined の場合、補正値 6 項目はペイロードで全て null になる", async () => {
      // given - correctionValues 未設定
      registCorrectValue.mockResolvedValue({ lockInfo: { ...VALID_LOCK_INFO } });

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      const payload = registCorrectValue.mock.calls[0][0].request;
      expect(payload.loanDiscTotalCorrectionValue).toBeNull();
      expect(payload.internalJpyCorrectionValue).toBeNull();
      expect(payload.forexCreditTotalCorrectionValue).toBeNull();
      expect(payload.shiShoTotalCorrectionValue).toBeNull();
      expect(payload.regulationTanpoCorrectionValueRegulationValue).toBeNull();
      expect(payload.regulationTanpoCorrectionValueJikaBase).toBeNull();
    });

    it("correctionValues が部分埋めのとき、未指定項目のみペイロードで null となり、指定項目はそのまま伝搬する", async () => {
      // given - 一部のみ設定
      element.correctionValues = {
        loanDiscTotalCorrectionValue: 9999999,
        regulationTanpoCorrectionValueJikaBase: 1234567
      };
      registCorrectValue.mockResolvedValue({ lockInfo: { ...VALID_LOCK_INFO } });
      await flushPromises();

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      const payload = registCorrectValue.mock.calls[0][0].request;
      expect(payload.loanDiscTotalCorrectionValue).toBe(9999999);
      expect(payload.regulationTanpoCorrectionValueJikaBase).toBe(1234567);
      expect(payload.internalJpyCorrectionValue).toBeNull();
      expect(payload.forexCreditTotalCorrectionValue).toBeNull();
      expect(payload.shiShoTotalCorrectionValue).toBeNull();
      expect(payload.regulationTanpoCorrectionValueRegulationValue).toBeNull();
    });

    it("correctionReason が undefined の場合、ペイロードで null として伝搬する", async () => {
      // given - correctionReason 未設定
      registCorrectValue.mockResolvedValue({ lockInfo: { ...VALID_LOCK_INFO } });

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      const payload = registCorrectValue.mock.calls[0][0].request;
      expect(payload.correctionReason).toBeNull();
    });

    it("Apex 失敗時 error.body が存在しない場合、registererror.detail.message は文字列化された error となる", async () => {
      // given - body プロパティが無い Error オブジェクト
      const networkError = new Error("Network Error");
      registCorrectValue.mockRejectedValue(networkError);
      const handler = jest.fn();
      element.addEventListener("registererror", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.detail.message).toBe(String(networkError));
    });

    it("Apex 失敗時 error.body はあるが message が無い場合、registererror.detail.message は String(error) フォールバックとなる", async () => {
      // given - body はあるが message プロパティが無い
      const error = { body: {} };
      registCorrectValue.mockRejectedValue(error);
      const handler = jest.fn();
      element.addEventListener("registererror", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.detail.message).toBe(String(error));
    });

    it("Apex 成功時 response.lockInfo が undefined の場合、registersuccess.detail.lockInfo は null となる", async () => {
      // given - lockInfo を含まない response
      registCorrectValue.mockResolvedValue({});
      const handler = jest.fn();
      element.addEventListener("registersuccess", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.detail.lockInfo).toBeNull();
    });

    it("Apex 成功時 response 全体が undefined の場合でも registersuccess は dispatch され、detail.lockInfo は null となる", async () => {
      // given - response 自体が undefined
      registCorrectValue.mockResolvedValue(undefined);
      const handler = jest.fn();
      element.addEventListener("registersuccess", handler);

      // when
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler.mock.calls[0][0].detail.lockInfo).toBeNull();
    });

    it("連続押下: 1 回目成功 → 2 回目も Apex を呼べる（finally の isLoading=false 化を間接検証）", async () => {
      // given - 1 回目: 成功
      registCorrectValue.mockResolvedValueOnce({ lockInfo: { ...VALID_LOCK_INFO } });

      // when - 1 回目
      clickButton(element, "補正値登録");
      await flushPromises();

      // given - 2 回目: 成功
      registCorrectValue.mockResolvedValueOnce({ lockInfo: { ...VALID_LOCK_INFO } });

      // when - 2 回目
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(registCorrectValue).toHaveBeenCalledTimes(2);
    });

    it("連続押下: 1 回目失敗 → 2 回目も Apex を呼べる（catch 後の finally で isLoading=false 化を間接検証）", async () => {
      // given - 1 回目: 失敗
      registCorrectValue.mockRejectedValueOnce({ body: { message: "1 回目失敗" } });

      // when - 1 回目
      clickButton(element, "補正値登録");
      await flushPromises();
      await flushPromises();

      // given - 2 回目: 成功
      registCorrectValue.mockResolvedValueOnce({ lockInfo: { ...VALID_LOCK_INFO } });

      // when - 2 回目
      clickButton(element, "補正値登録");
      await flushPromises();

      // then
      expect(registCorrectValue).toHaveBeenCalledTimes(2);
    });

    it("必須不足による early return では Apex を一切呼ばず、後続の正常押下も独立して動作する", async () => {
      // given - 1 回目: brNo 未設定で必須不足
      element.brNo = null;
      const errorHandler = jest.fn();
      element.addEventListener("registererror", errorHandler);
      await flushPromises();

      // when - 1 回目
      clickButton(element, "補正値登録");
      await flushPromises();

      // then - 1 回目は Apex 呼ばれず、registererror 発火
      expect(registCorrectValue).not.toHaveBeenCalled();
      expect(errorHandler).toHaveBeenCalledTimes(1);

      // given - 2 回目: brNo を埋めて正常リクエスト
      element.brNo = VALID_BR_NO;
      registCorrectValue.mockResolvedValueOnce({ lockInfo: { ...VALID_LOCK_INFO } });
      const successHandler = jest.fn();
      element.addEventListener("registersuccess", successHandler);
      await flushPromises();

      // when - 2 回目
      clickButton(element, "補正値登録");
      await flushPromises();

      // then - 2 回目は Apex 呼ばれ、registersuccess 発火
      expect(registCorrectValue).toHaveBeenCalledTimes(1);
      expect(successHandler).toHaveBeenCalledTimes(1);
    });
  });

  // ==========================================================================
  // handleAction（プレースホルダー / 「計数再取得」ボタン）
  // ==========================================================================

  describe("handleAction", () => {
    it("「計数再取得」ボタン押下でも例外を投げず、Apex も呼ばれない（プレースホルダー）", async () => {
      // given
      document.body.appendChild(element);
      await flushPromises();

      // when
      const action = () => clickButton(element, "計数再取得");

      // then
      expect(action).not.toThrow();
      expect(registCorrectValue).not.toHaveBeenCalled();
    });
  });
});
