/*************************************************************************************************************
 * テスト対象 ：  functions/hoseichiRegisterExe
 * テスト概要 ：  与信稟議書査定書計数情報画面の補正値登録処理
 * 設計書    ：  /home/shota/src/salesforce/ringi/補正値登録/design/03_request_response.md
 *
 * 【このファイルは何を確認するか（初参画者向け）】
 *   補正値登録ボタンを押した時の処理 (hoseichiRegisterExe) が正しく動くかを Jest で検証する。
 *   B1 / C2 / C6 の 3 つの子コンポからデータを集めて API に送信する一連の流れを、
 *   入力取得 → 確認モーダル → API 呼出 → 成功/エラー の各分岐ごとに 19 テストでカバーする。
 *
 * 【テスト構成】
 *   describe で振る舞いごとに章立てし、各 it は「○○したら○○する」の仕様文で記述する。
 *
 *     確認モーダル                ── キャンセル / OK の分岐
 *     子コンポーネント参照        ── B1 / C2 / C6 が正しいセレクタで呼ばれること
 *     API へ送る payload          ── 設計書 11 項目構造（brNo / lockInfo / 排他ロック優先順）
 *     子コンポーネントの責務分担  ── 補正値=C2 / 規定担保=B1 / 補正理由=C6
 *     エラー処理                  ── バリデーション / サーバ / 例外 の 3 層
 *     Spinner 制御                ── 画面フラグの true→false 切替
 *     DTO と後処理                ── RequestMetadataDto / initialize / handleRegister / ShowToast
 *     OpenAPI Dto ファクトリ      ── constructFromObject の引数検証
 *
 * 【モック方針（初参画者向け）】
 *   モック = テスト対象の「外側」を偽物に差し替える仕組み。本物の API や DB を叩くと
 *   テストが遅く・不安定になるので、境界（外部依存）だけ偽物にしてテスト対象の動きを純粋に
 *   検証する。逆に本体ロジックや純粋関数 (paddingZero) や DTO 値クラスは実体を使う方が
 *   振る舞いを正確に確認でき、設計変更時のテストの追従コストも下がる。
 *
 *   ── モックする (4 つ：境界の外部依存) ──
 *     postRequest      : c/f003GsV0000CallApi          （HTTP API 境界）
 *     ConfirmInfo      : c/f003GsV0000ConfirmInfo      （確認モーダル UI 境界）
 *     ShowToastEvent   : lightning/platformShowToastEvent  （LWC 公式トースト境界）
 *     validateElement  : c/f003GsV0000DataValidation   （バリデーション境界）
 *
 *   ── 実体使用（モックしない） ──
 *     RequestMetadataDto                          : c/f003GsV0000DtoClass
 *     paddingZero                                 : c/f003GsV0000Utils
 *     RG_DISP_LIST / SUBSYSTEM_ID_RG / RG_CONNECT : c/f003RgV0000Const
 *     YUSRG0501C_I / YUSRG0502C_I                 : c/f003RgV0000MsgConst
 *     RgV0501HoseichiRegisterRequest              : c/f003RgV0000OpenApiModel
 *     OPERATION / ENDPOINT                        : ../f003RgV0501YushiRingiShoSateiShoKeisuJohoConst
 *
 *   ── 子コンポ B1/C2/C6 は this.template.querySelector の戻り値を mock オブジェクトで差し替え ──
 *
 * 【検証スタイル】
 *   paddingZero / RequestMetadataDto は実体ゆえ呼出 spy ではなく結果値で検証する。
 *   例: dto.branchNo === "0000010" / payload.brNo === "010"
 ************************************************************************************************************/

// =====================================================================
// 境界モック宣言
//   ここで境界の依存を偽物に差し替える。jest.mock はファイル全体に対して有効になる
//   （jest が import より先に実行する仕組み）。virtual:true はローカルに実体ファイルが
//   無いモジュールでもモックを許可するためのフラグ。
// =====================================================================

jest.mock(
  "lightning/platformShowToastEvent",
  () => ({ ShowToastEvent: jest.fn() }),
  { virtual: true }
);

jest.mock(
  "c/f003GsV0000CallApi",
  () => ({ postRequest: jest.fn() }),
  { virtual: true }
);

jest.mock(
  "c/f003GsV0000ConfirmInfo",
  () => ({ __esModule: true, default: { open: jest.fn() } }),
  { virtual: true }
);

jest.mock(
  "c/f003GsV0000DataValidation",
  () => ({ validateElement: jest.fn() }),
  { virtual: true }
);

import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { postRequest } from "c/f003GsV0000CallApi";
import { RequestMetadataDto } from "c/f003GsV0000DtoClass";
import { paddingZero } from "c/f003GsV0000Utils";
import ConfirmInfo from "c/f003GsV0000ConfirmInfo";
import {
  RG_DISP_LIST,
  SUBSYSTEM_ID_RG,
  RG_CONNECT
} from "c/f003RgV0000Const";
import { YUSRG0501C_I, YUSRG0502C_I } from "c/f003RgV0000MsgConst";
import { RgV0501HoseichiRegisterRequest } from "c/f003RgV0000OpenApiModel";
import {
  OPERATION,
  ENDPOINT
} from "../f003RgV0501YushiRingiShoSateiShoKeisuJohoConst";
import { hoseichiRegisterExe } from "../functions/hoseichiRegisterExe";

// =====================================================================
// 集約定数
//   テストで何度も使うデータを上部にまとめる。各テストは override で差分のみを与える設計。
//   Object.freeze は「うっかり書き換え」防止のためのガード（凍結したオブジェクトは更新できない）。
// =====================================================================

const B1_SELECTOR = "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-b1";
const C2_SELECTOR = "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c2";
const C6_SELECTOR = "c-f003-rg-v0501-yushi-ringi-sho-satei-sho-keisu-joho-c6";

// 責務分担: B1=規定担保2項目 / C2=補正値4項目 / C6=correctionReason
const DEFAULT_B1_PAYLOAD = Object.freeze({
  regulationTanpoCorrectionValueRegulationValue: 5000000,
  regulationTanpoCorrectionValueJikaBase: 6000000
});

const DEFAULT_C2_PAYLOAD = Object.freeze({
  loanDiscTotalCorrectionValue: 1000000,
  internalJpyCorrectionValue: 2000000,
  forexCreditTotalCorrectionValue: 3000000,
  shiShoTotalCorrectionValue: 4000000
});

const DEFAULT_C6_PAYLOAD = Object.freeze({ correctionReason: "テスト補正理由" });

// hdnBrNo は Dto 時点で 3 桁の生値前提（paddingZero 不要）
const DEFAULT_RECORDS = Object.freeze({
  hdnBrNo: "010",
  hdnCmNo: "9019149",
  hdnRefNo: "rkANKEN111111111111"
});

const DEFAULT_API_RECORDS_LIST = Object.freeze({
  hdnExclusiveCount: 1,
  exclusiveKey: "rkANKEN111111111111"
});

// これが API に送るべき payload の「正解の形」。設計書 03_request_response.md の
// Request Body 11 項目に対応する（root 10 キー + lockInfo 内 2 キー = 計 11 値）。
// 複数テストで同じ期待値を共有するため Object.freeze で固定する。
const EXPECTED_FULL_PAYLOAD = Object.freeze({
  brNo: "010",
  cmNo: "9019149",
  loanDiscTotalCorrectionValue: 1000000,
  internalJpyCorrectionValue: 2000000,
  forexCreditTotalCorrectionValue: 3000000,
  shiShoTotalCorrectionValue: 4000000,
  regulationTanpoCorrectionValueRegulationValue: 5000000,
  regulationTanpoCorrectionValueJikaBase: 6000000,
  correctionReason: "テスト補正理由",
  lockInfo: { exclusiveKey: "rkANKEN111111111111", exclusiveCount: 1 }
});

/**
 * B1 子コンポの「ニセモノ」を作るファクトリ関数。
 *
 * 本物の B1 LWC コンポーネントの代わりに、テストでは this.template.querySelector が
 * このオブジェクトを返すように設定して使う。getHoseichiNoCheckList / getHoseichiList の
 * 戻り値や例外を override で差し替え、多様なケースを 1 行で表現できる。
 *
 * @param {object} options
 * @param {object} [options.payload]      - 戻り値として渡すデータ
 * @param {number} [options.valid]        - getHoseichiList の第 2 戻り値（バリエラー数）
 * @param {Error}  [options.noCheckThrows] - getHoseichiNoCheckList が throw する Error
 * @param {Error}  [options.listThrows]    - getHoseichiList が throw する Error
 */
function createMockB1Component({
  payload = DEFAULT_B1_PAYLOAD,
  valid = 0,
  noCheckThrows = null,
  listThrows = null
} = {}) {
  return {
    getHoseichiNoCheckList: jest.fn(() => {
      if (noCheckThrows) throw noCheckThrows;
      return [payload];
    }),
    getHoseichiList: jest.fn(() => {
      if (listThrows) throw listThrows;
      return [payload, valid];
    })
  };
}

/**
 * C2 子コンポのニセモノ。getHoseichiList のみ実装（NoCheck 版は使わない設計）。
 * テスト対象は C2 から補正値 4 項目を受け取る前提なので、戻り値は補正値オブジェクト + valid。
 */
function createMockC2Component({
  payload = DEFAULT_C2_PAYLOAD,
  valid = 0,
  listThrows = null
} = {}) {
  return {
    getHoseichiList: jest.fn(() => {
      if (listThrows) throw listThrows;
      return [payload, valid];
    })
  };
}

/**
 * C6 子コンポのニセモノ。getHoseiriyuList は B1.getHoseichiList / C2.getHoseichiList と同じく
 * [itemList, valid] のタプル形式で返す（valid > 0 でバリデーションエラー扱い）。
 */
function createMockC6Component({
  payload = DEFAULT_C6_PAYLOAD,
  valid = 0,
  throws: throwsErr = null
} = {}) {
  return {
    getHoseiriyuList: jest.fn(() => {
      if (throwsErr) throw throwsErr;
      return [payload, valid];
    })
  };
}

/**
 * テスト対象 hoseichiRegisterExe を bind() して呼び出す時の `this` コンテキストを丸ごと作る。
 *
 * hoseichiRegisterExe は内部で次のものを参照する:
 *   this.template.querySelector(...)              → 子コンポ取得
 *   this.records.hdnBrNo / hdnCmNo / hdnRefNo     → 親が保持する隠し項目
 *   this.apiRecordsList.exclusiveKey / hdnExclusiveCount → 排他ロック情報
 *   this.validateErrorHandler() / serverErrorHandler() / systemErrorHandler() → エラー 3 層
 *   this.initialize() / this.handleRegister() / this.dispatchEvent() → 後処理
 *   this.isSpinnerVisible / isServerErrorVisible  → 画面フラグ
 * 本物の親（LightningModal/Element）の代わりに、これらを揃えた素のオブジェクトを返す。
 */
function createMockThis({
  b1 = createMockB1Component(),
  c2 = createMockC2Component(),
  c6 = createMockC6Component(),
  records = DEFAULT_RECORDS,
  apiRecordsList = DEFAULT_API_RECORDS_LIST
} = {}) {
  return {
    template: {
      querySelector: jest.fn((selector) => {
        if (selector === B1_SELECTOR) return b1;
        if (selector === C2_SELECTOR) return c2;
        if (selector === C6_SELECTOR) return c6;
        return null;
      })
    },
    records,
    apiRecordsList,
    isSpinnerVisible: false,
    isServerErrorVisible: false,
    validateErrorHandler: jest.fn(),
    serverErrorHandler: jest.fn(),
    systemErrorHandler: jest.fn(),
    initialize: jest.fn(),
    handleRegister: jest.fn(),
    dispatchEvent: jest.fn()
  };
}

describe("hoseichiRegisterExe", () => {
  // 各テスト後に jest mock の呼び出し履歴をクリアして次のテストへ影響しないようにする
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("確認モーダル", () => {
    /**
     * 保証: ConfirmInfo.open() が false → postRequest を呼ばずに即座に return
     * 入力: ConfirmInfo.open.mockResolvedValue(false)
     * 期待: postRequest 不呼出 / 副作用 handler 系不呼出 / Spinner false 維持
     *
     * 【AAA パターンの読み方（このファイルで初めての方向け）】
     *   - Arrange: テスト用のデータと状態を準備するブロック
     *   - Act:     テスト対象の関数を実際に実行するブロック
     *   - Assert:  実行結果が期待通りか検証するブロック
     *   以降のテストでも同じ // === Arrange === / === Act === / === Assert === で区切る。
     */
    it("キャンセルしたら postRequest を呼ばずに終了する", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(false);
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      expect(ConfirmInfo.open).toHaveBeenCalledTimes(1);
      expect(ConfirmInfo.open).toHaveBeenCalledWith({
        size: "small",
        message: YUSRG0501C_I,
        code: "YUSRG0501C-I"
      });
      expect(postRequest).not.toHaveBeenCalled();
      expect(ctx.validateErrorHandler).not.toHaveBeenCalled();
      expect(ctx.serverErrorHandler).not.toHaveBeenCalled();
      expect(ctx.systemErrorHandler).not.toHaveBeenCalled();
      expect(ctx.dispatchEvent).not.toHaveBeenCalled();
      expect(ctx.isSpinnerVisible).toBe(false);
    });

    /**
     * 保証: ConfirmInfo.open() が true → postRequest が 1 回呼ばれる
     * 入力: ConfirmInfo.open.mockResolvedValue(true), postRequest.mockResolvedValue({})
     * 期待: postRequest が ENDPOINT.HOSEICHI_REGISTER / RG_CONNECT で呼ばれる
     */
    it("OK したら後続処理に進む", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      expect(ConfirmInfo.open).toHaveBeenCalledTimes(1);
      expect(postRequest).toHaveBeenCalledTimes(1);
      expect(postRequest).toHaveBeenCalledWith(
        expect.any(Object),
        ENDPOINT.HOSEICHI_REGISTER,
        RG_CONNECT,
        expect.any(Object)
      );
    });
  });

  describe("子コンポーネント参照", () => {
    /**
     * 保証: 確認モーダル前 B1 NoCheck 1 回 + OK 後 B1 Check 1 / C2 1 / C6 1 = 計 4 回
     * 入力: 既定 mock コンテキスト（ConfirmInfo OK / postRequest 成功）
     * 期待: querySelector が B1/C2/C6 セレクタで呼ばれ、子 mock メソッドも各 1 回ずつ
     */
    it("B1, C2, C6 を正しいセレクタで参照する", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const b1 = createMockB1Component();
      const c2 = createMockC2Component();
      const c6 = createMockC6Component();
      const ctx = createMockThis({ b1, c2, c6 });

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      expect(ctx.template.querySelector).toHaveBeenCalledWith(B1_SELECTOR);
      expect(ctx.template.querySelector).toHaveBeenCalledWith(C2_SELECTOR);
      expect(ctx.template.querySelector).toHaveBeenCalledWith(C6_SELECTOR);
      expect(ctx.template.querySelector).toHaveBeenCalledTimes(4);
      expect(b1.getHoseichiNoCheckList).toHaveBeenCalledTimes(1);
      expect(b1.getHoseichiList).toHaveBeenCalledTimes(1);
      expect(c2.getHoseichiList).toHaveBeenCalledTimes(1);
      expect(c6.getHoseiriyuList).toHaveBeenCalledTimes(1);
    });
  });

  describe("API へ送る payload", () => {
    /**
     * 保証: postRequest 第 4 引数の dto が設計書 03_request_response.md 通りの構造
     * 入力: 既定 mock コンテキスト
     * 期待: EXPECTED_FULL_PAYLOAD に等価
     */
    it("設計書 11 項目スキーマで構築される", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      // mock.calls[呼び出し番号][引数番号] で jest mock の呼び出し履歴にアクセスできる。
      // ここでは postRequest が 1 回目に呼ばれた時の第 4 引数（payload）を取り出している。
      const reqParamsDto = postRequest.mock.calls[0][3];
      expect(reqParamsDto).toEqual(EXPECTED_FULL_PAYLOAD);
      expect(Object.keys(reqParamsDto)).toHaveLength(10);
      expect(Object.keys(reqParamsDto.lockInfo)).toHaveLength(2);
    });

    /**
     * 保証: hdnBrNo="010"（既に 3 桁の生値）→ payload.brNo は paddingZero せずそのまま、
     *       metaInfo.setBranchNo はヘッダ用 7 桁変換で paddingZero("010", 7) = "0000010"
     * 入力: 既定 mock コンテキスト（DEFAULT_RECORDS.hdnBrNo = "010"）
     * 期待: payload.brNo === "010"（生値）/ dto.branchNo === "0000010"（7 桁変換）
     */
    it("brNo は3桁の生値、setBranchNo は7桁ゼロ埋め", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      const dto = postRequest.mock.calls[0][0];
      const reqParamsDto = postRequest.mock.calls[0][3];
      expect(reqParamsDto.brNo).toBe("010");
      expect(dto.branchNo).toBe("0000010");
    });

    /**
     * 保証: apiRecordsList.exclusiveKey が定義されていれば、records.hdnRefNo より優先される
     * 入力: apiRecordsList = { hdnExclusiveCount:7, exclusiveKey:"FROM_API" }, records.hdnRefNo:"FROM_RECORDS"
     * 期待: lockInfo.exclusiveKey === "FROM_API"
     */
    it("lockInfo.exclusiveKey は apiRecordsList 側を優先", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis({
        records: { hdnBrNo: "010", hdnCmNo: "9019149", hdnRefNo: "FROM_RECORDS" },
        apiRecordsList: { hdnExclusiveCount: 7, exclusiveKey: "FROM_API" }
      });

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      const reqParamsDto = postRequest.mock.calls[0][3];
      expect(reqParamsDto.lockInfo.exclusiveKey).toBe("FROM_API");
      expect(reqParamsDto.lockInfo.exclusiveCount).toBe(7);
    });

    /**
     * 保証: apiRecordsList.exclusiveKey が未定義 → records.hdnRefNo を採用
     * 入力: apiRecordsList = { hdnExclusiveCount:9 } のみ, records.hdnRefNo:"FROM_RECORDS_FALLBACK"
     * 期待: lockInfo.exclusiveKey === "FROM_RECORDS_FALLBACK"
     */
    it("apiRecordsList に exclusiveKey が無ければ hdnRefNo へフォールバック", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis({
        records: { hdnBrNo: "010", hdnCmNo: "9019149", hdnRefNo: "FROM_RECORDS_FALLBACK" },
        apiRecordsList: { hdnExclusiveCount: 9 }
      });

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      const reqParamsDto = postRequest.mock.calls[0][3];
      expect(reqParamsDto.lockInfo.exclusiveKey).toBe("FROM_RECORDS_FALLBACK");
      expect(reqParamsDto.lockInfo.exclusiveCount).toBe(9);
    });

  });

  describe("子コンポーネントの責務分担", () => {
    /**
     * 保証: 責務分担（補正値は C2 のツリーテーブル責務）が payload に正確に反映
     * 入力: 一意な値で B1/C2/C6 各 mock を構成
     * 期待: 補正値 4 項目は C2 由来、規定担保 2 項目は B1 由来、correctionReason は C6 由来
     */
    it("補正値は C2、規定担保は B1、補正理由は C6 から取得される", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const c2Source = {
        loanDiscTotalCorrectionValue: 11,
        internalJpyCorrectionValue: 22,
        forexCreditTotalCorrectionValue: 33,
        shiShoTotalCorrectionValue: 44
      };
      const b1Source = {
        regulationTanpoCorrectionValueRegulationValue: 55,
        regulationTanpoCorrectionValueJikaBase: 66
      };
      const c6Source = { correctionReason: "C6由来テキスト" };
      const ctx = createMockThis({
        b1: createMockB1Component({ payload: b1Source }),
        c2: createMockC2Component({ payload: c2Source }),
        c6: createMockC6Component({ payload: c6Source })
      });

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      const reqParamsDto = postRequest.mock.calls[0][3];
      expect(reqParamsDto.loanDiscTotalCorrectionValue).toBe(11);
      expect(reqParamsDto.internalJpyCorrectionValue).toBe(22);
      expect(reqParamsDto.forexCreditTotalCorrectionValue).toBe(33);
      expect(reqParamsDto.shiShoTotalCorrectionValue).toBe(44);
      expect(reqParamsDto.regulationTanpoCorrectionValueRegulationValue).toBe(55);
      expect(reqParamsDto.regulationTanpoCorrectionValueJikaBase).toBe(66);
      expect(reqParamsDto.correctionReason).toBe("C6由来テキスト");
    });
  });

  describe("エラー処理", () => {
    describe("バリデーション", () => {
      /**
       * 保証: b1Valid > 0 → validateErrorHandler 呼出 / postRequest 不呼出
       * 入力: createMockB1Component({ valid: 1 })
       * 期待: validateErrorHandler 1 回、postRequest 不呼出
       */
      it("B1 のバリデーションエラー時は validateErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const ctx = createMockThis({
          b1: createMockB1Component({ valid: 1 })
        });

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.validateErrorHandler).toHaveBeenCalledTimes(1);
        expect(postRequest).not.toHaveBeenCalled();
      });

      /**
       * 保証: c2Valid > 0 → validateErrorHandler 呼出 / postRequest 不呼出
       * 入力: createMockC2Component({ valid: 1 })
       * 期待: validateErrorHandler 1 回、postRequest 不呼出
       */
      it("C2 のバリデーションエラー時は validateErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const ctx = createMockThis({
          c2: createMockC2Component({ valid: 1 })
        });

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.validateErrorHandler).toHaveBeenCalledTimes(1);
        expect(postRequest).not.toHaveBeenCalled();
      });

      /**
       * 保証: c6Valid > 0 → validateErrorHandler 呼出 / postRequest 不呼出
       * 入力: createMockC6Component({ valid: 1, payload: { correctionReason: "100バイト超..." } })
       * 期待: validateErrorHandler 1 回、postRequest 不呼出
       * 補足: 設計書 03_request_response.md の correctionReason は ByteLength 0-100。
       *       それを超える入力で C6 側 validateElement が valid>0 を返す業務ケースを表現する。
       */
      it("C6 の補正理由バリデーションエラー時は validateErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const overSizedCorrectionReason = "あ".repeat(101); // 100 バイト超（UTF-8 想定）
        const ctx = createMockThis({
          c6: createMockC6Component({
            payload: { correctionReason: overSizedCorrectionReason },
            valid: 1
          })
        });

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.validateErrorHandler).toHaveBeenCalledTimes(1);
        expect(postRequest).not.toHaveBeenCalled();
      });
    });

    describe("サーバエラー", () => {
      /**
       * 保証: postRequest が errors を含む response を返す → serverErrorHandler 呼出
       * 入力: postRequest.mockResolvedValue({ errors: [...] })
       * 期待: serverErrorHandler 1 回、ShowToastEvent / dispatchEvent 不呼出
       */
      it("response.errors を含む応答は serverErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const errResponse = { errors: ["E001", "E002"] };
        postRequest.mockResolvedValue(errResponse);
        const ctx = createMockThis();

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.serverErrorHandler).toHaveBeenCalledTimes(1);
        expect(ctx.serverErrorHandler).toHaveBeenCalledWith(errResponse);
        expect(ShowToastEvent).not.toHaveBeenCalled();
        expect(ctx.dispatchEvent).not.toHaveBeenCalled();
      });
    });

    describe("例外", () => {
      /**
       * 保証: postRequest が reject → systemErrorHandler が原因 Error と OPERATION で呼ばれる
       * 入力: postRequest.mockRejectedValue(new Error(...))
       * 期待: systemErrorHandler 1 回、ShowToast 不呼出
       */
      it("postRequest 例外時は systemErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const networkError = new Error("Network failure");
        postRequest.mockRejectedValue(networkError);
        const ctx = createMockThis();

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.systemErrorHandler).toHaveBeenCalledTimes(1);
        expect(ctx.systemErrorHandler).toHaveBeenCalledWith(
          networkError,
          OPERATION.HOSEICHI_REGISTER
        );
        expect(ShowToastEvent).not.toHaveBeenCalled();
      });

      /**
       * 保証: 確認モーダル前の B1.getHoseichiNoCheckList が throw → systemErrorHandler
       * 入力: createMockB1Component({ noCheckThrows: new Error(...) })
       * 期待: systemErrorHandler 1 回、ConfirmInfo.open / postRequest 不呼出
       */
      it("B1.getHoseichiNoCheckList 例外時は systemErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        const childError = new Error("B1 NoCheck failure");
        const ctx = createMockThis({
          b1: createMockB1Component({ noCheckThrows: childError })
        });

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.systemErrorHandler).toHaveBeenCalledTimes(1);
        expect(ctx.systemErrorHandler).toHaveBeenCalledWith(
          childError,
          OPERATION.HOSEICHI_REGISTER
        );
        expect(ConfirmInfo.open).not.toHaveBeenCalled();
        expect(postRequest).not.toHaveBeenCalled();
      });

      /**
       * 保証: OK 後の C2.getHoseichiList が throw → systemErrorHandler
       * 入力: createMockC2Component({ listThrows: new Error(...) })
       * 期待: systemErrorHandler 1 回、postRequest 不呼出
       */
      it("C2.getHoseichiList 例外時は systemErrorHandler が呼ばれる", async () => {
        // === Arrange ===
        ConfirmInfo.open.mockResolvedValue(true);
        const c2Error = new Error("C2 getHoseichiList failure");
        const ctx = createMockThis({
          c2: createMockC2Component({ listThrows: c2Error })
        });

        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(ctx.systemErrorHandler).toHaveBeenCalledTimes(1);
        expect(ctx.systemErrorHandler).toHaveBeenCalledWith(
          c2Error,
          OPERATION.HOSEICHI_REGISTER
        );
        expect(postRequest).not.toHaveBeenCalled();
      });
    });
  });

  describe("Spinner 制御", () => {
    /**
     * 保証: postRequest 中は true（処理中）、完了後は false（解除）。isServerErrorVisible は OK 時 false 初期化
     * 入力: postRequest が呼ばれた瞬間の isSpinnerVisible を捕捉
     * 期待: 処理中 true、完了後 false
     */
    it("isSpinnerVisible は処理中 true、完了後 false に戻る", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      const ctx = createMockThis();
      let spinnerDuringRequest = null;
      let serverErrorVisibleDuringRequest = null;
      postRequest.mockImplementation(() => {
        spinnerDuringRequest = ctx.isSpinnerVisible;
        serverErrorVisibleDuringRequest = ctx.isServerErrorVisible;
        return Promise.resolve({});
      });

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      expect(spinnerDuringRequest).toBe(true);
      expect(serverErrorVisibleDuringRequest).toBe(false);
      expect(ctx.isSpinnerVisible).toBe(false);
    });
  });

  describe("DTO と後処理", () => {
    /**
     * 保証: subSystemId / displayId / displayName / branchNo / customerNo / lcNo / lcSeqNo / operationName
     * 入力: 既定 mock コンテキスト
     * 期待: postRequest 第 1 引数 (dto インスタンス) の field が実体定数値と一致
     */
    it("RequestMetadataDto の field 群が正しく設定される", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      const dto = postRequest.mock.calls[0][0];
      expect(dto).toBeInstanceOf(RequestMetadataDto);
      expect(dto.subSystemId).toBe(SUBSYSTEM_ID_RG);
      expect(dto.displayId).toBe(RG_DISP_LIST.RgV0501.ID);
      expect(dto.displayName).toBe(RG_DISP_LIST.RgV0501.NAME);
      expect(dto.branchNo).toBe("0000010");
      expect(dto.customerNo).toBe("9019149");
      expect(dto.lcNo).toBe("rkANKEN111111111111");
      expect(dto.lcSeqNo).toBe("");
      expect(dto.operationName).toBe(OPERATION.HOSEICHI_REGISTER);
    });

    /**
     * 保証: postRequest 成功 → initialize と handleRegister 各 1 回、ShowToastEvent が成功メッセージで dispatch
     * 入力: postRequest 成功
     * 期待: initialize 1 / handleRegister 1 / ShowToastEvent 1（YUSRG0502C_I）
     */
    it("成功時は initialize / handleRegister / ShowToast が呼ばれる", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      const ctx = createMockThis();

      // === Act ===
      await hoseichiRegisterExe.call(ctx);

      // === Assert ===
      expect(ctx.initialize).toHaveBeenCalledTimes(1);
      expect(ctx.handleRegister).toHaveBeenCalledTimes(1);
      expect(ShowToastEvent).toHaveBeenCalledTimes(1);
      expect(ShowToastEvent).toHaveBeenCalledWith({
        title: "Success",
        message: YUSRG0502C_I,
        variant: "success"
      });
      expect(ctx.dispatchEvent).toHaveBeenCalledTimes(1);
    });
  });

  describe("OpenAPI Dto ファクトリ", () => {
    /**
     * 保証: Dto ファクトリへの引数が EXPECTED_FULL_PAYLOAD と等価
     * 入力: 既定 mock コンテキスト + spy on constructFromObject
     * 期待: 1 回呼ばれ、引数が EXPECTED_FULL_PAYLOAD
     */
    it("constructFromObject に新11項目で渡される", async () => {
      // === Arrange ===
      ConfirmInfo.open.mockResolvedValue(true);
      postRequest.mockResolvedValue({});
      // jest.spyOn は実体を残したまま呼出履歴を記録するための仕組み。
      // jest.mock と違い元の関数が動き続けるので、constructFromObject の本来の振る舞いを
      // 保ちつつ「どんな引数で呼ばれたか」だけを検証できる。
      const constructSpy = jest.spyOn(
        RgV0501HoseichiRegisterRequest,
        "constructFromObject"
      );
      const ctx = createMockThis();

      try {
        // === Act ===
        await hoseichiRegisterExe.call(ctx);

        // === Assert ===
        expect(constructSpy).toHaveBeenCalledTimes(1);
        expect(constructSpy.mock.calls[0][0]).toEqual(EXPECTED_FULL_PAYLOAD);
      } finally {
        // spyOn は必ず復元する。残すと他のテストで実体ではなく spy のままになり、
        // テスト間の独立性が崩れる
        constructSpy.mockRestore();
      }
    });
  });
});
