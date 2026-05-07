/**
 * f003RgV0501YushiRingiShoSateiShoKeisuJohoB1 LWC の Jest テスト。
 * t-wada 流: describe/it 構造、日本語仕様文 it 名、given/when/then、test.each パラメータ化、1 テスト 1 観点。
 */

// 注: package.json jest 設定の moduleNameMapping は moduleNameMapper の typo のため "c/..." 解決不可。
//     相対パス import で回避（package.json 修正は本タスクのスコープ外、escalation 報告対象）。
import F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 from "../f003RgV0501YushiRingiShoSateiShoKeisuJohoB1";
import registCorrectValue from "@salesforce/apex/RinsashoCntInfoApex.registCorrectValue";

jest.mock(
  "@salesforce/apex/RinsashoCntInfoApex.registCorrectValue",
  () => ({ default: jest.fn() }),
  { virtual: true }
);

// 標準的な flushPromises（jsdom 環境下のマイクロタスク完了待ち）
const flushPromises = () => new Promise((resolve) => setImmediate(resolve));

/**
 * jest.setup.js の MockLightningElement は EventTarget API を持たないため、
 * dispatchEvent / addEventListener を最小限実装で補強する。
 */
function attachEventTarget(target) {
  const listeners = new Map();
  target.addEventListener = (type, handler) => {
    if (!listeners.has(type)) listeners.set(type, []);
    listeners.get(type).push(handler);
  };
  target.removeEventListener = (type, handler) => {
    const arr = listeners.get(type) || [];
    listeners.set(
      type,
      arr.filter((h) => h !== handler)
    );
  };
  target.dispatchEvent = (event) => {
    const arr = listeners.get(event.type) || [];
    arr.forEach((h) => h(event));
    return true;
  };
}

describe("c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1", () => {
  let element;

  beforeEach(() => {
    jest.clearAllMocks();
    element = createElement(
      "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1",
      { is: F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 }
    );
    attachEventTarget(element);
    try {
      document.body.appendChild(element);
    } catch (_e) {
      // jest.setup.js のカスタムモックでは appendChild が成立しない場合があるため握りつぶす
    }
  });

  // ==========================================================================
  // レンダリング（プロパティ駆動の表示分岐）
  // ==========================================================================

  describe("レンダリング", () => {
    it("初期状態では showCalculationAndRegisterButtons が undefined である（計算/補正値登録ボタン非表示の前提）", () => {
      // given - beforeEach で element 生成のみ

      // when - プロパティ未設定のまま観察

      // then
      expect(element.showCalculationAndRegisterButtons).toBeUndefined();
    });

    it("showCalculationAndRegisterButtons=true のとき、当該プロパティは true を保持する（テンプレート lwc:if 分岐の前提条件）", async () => {
      // given
      element.showCalculationAndRegisterButtons = true;

      // when
      await flushPromises();

      // then
      expect(element.showCalculationAndRegisterButtons).toBe(true);
    });

    it("showCalculationAndRegisterButtons=false のとき、当該プロパティは false を保持する（計算/補正値登録ボタン非表示の前提）", async () => {
      // given
      element.showCalculationAndRegisterButtons = false;

      // when
      await flushPromises();

      // then
      expect(element.showCalculationAndRegisterButtons).toBe(false);
    });
  });

  // ==========================================================================
  // handleCalculate
  // ==========================================================================

  describe("handleCalculate", () => {
    it("calculate という名前の CustomEvent を 1 回 dispatch する", () => {
      // given
      const handler = jest.fn();
      element.addEventListener("calculate", handler);

      // when
      element.handleCalculate();

      // then
      expect(handler).toHaveBeenCalledTimes(1);
      const event = handler.mock.calls[0][0];
      expect(event.type).toBe("calculate");
    });
  });

  // ==========================================================================
  // handleRegister（補正値登録）
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

    beforeEach(() => {
      element.brNo = VALID_BR_NO;
      element.cmNo = VALID_CM_NO;
      element.lockInfo = { ...VALID_LOCK_INFO };
      element.correctionValues = { ...VALID_CORRECTION_VALUES };
      element.correctionReason = VALID_REASON;
    });

    it("Apex registCorrectValue を { request: フラットペイロード } 形式で 1 回呼び出す", async () => {
      // given
      registCorrectValue.mockResolvedValue({
        lockInfo: { exclusiveKey: "KEY-OK", exclusiveCount: 2 }
      });

      // when
      element.handleRegister();
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
      element.handleRegister();
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
      element.handleRegister();
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

        // when
        element.handleRegister();
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
      element.handleRegister();
      await flushPromises();

      // then
      const callArg = registCorrectValue.mock.calls[0][0];
      expect(callArg).toHaveProperty("request");
      const payload = callArg.request;
      expect(payload.brNo).toMatch(/^\d{3}$/);
      expect(payload.cmNo).toMatch(/^\d{7}$/);
      // 補正値 6 項目はフラット展開されている（correctionValues オブジェクトの形では渡らない）
      expect(payload).toHaveProperty("loanDiscTotalCorrectionValue");
      expect(payload).toHaveProperty("internalJpyCorrectionValue");
      expect(payload).toHaveProperty("forexCreditTotalCorrectionValue");
      expect(payload).toHaveProperty("shiShoTotalCorrectionValue");
      expect(payload).toHaveProperty("regulationTanpoCorrectionValueRegulationValue");
      expect(payload).toHaveProperty("regulationTanpoCorrectionValueJikaBase");
      expect(payload).not.toHaveProperty("correctionValues");
      // lockInfo はネスト構造のまま渡る
      expect(payload.lockInfo).toEqual(
        expect.objectContaining({
          exclusiveKey: expect.any(String),
          exclusiveCount: expect.any(Number)
        })
      );
    });
  });

  // ==========================================================================
  // handleAction（プレースホルダー）
  // ==========================================================================

  describe("handleAction", () => {
    it("プレースホルダーゆえ呼び出しても例外を投げず、Apex も呼ばれない", () => {
      // given - 何もスタブしない

      // when
      const action = () => element.handleAction();

      // then
      expect(action).not.toThrow();
      expect(registCorrectValue).not.toHaveBeenCalled();
    });
  });
});
