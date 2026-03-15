/**
 * 計数サマリー・補正理由等コンポーネント (C6)
 *
 * 禀査番号・基準日・計数サマリー(限度算入/規定担保/保全率)・プール区分・補正理由を表示する。
 * 編集可能なテーブル数値セルを持たないため、applySavedHighlight は空実装。
 */
import { LightningElement, api } from "lwc";
import { makeTestData } from "c/testDataGenerator";

/* ── 定数 ── */

const ACTIVE_SECTIONS = "abcdefghijklmnopqr".split("");

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

  /* ── プール区分・補正理由 ── */

  poolCategory = makeTestData("numeric", 2);
  correctionReason = makeTestData("mixedChar", 105);

  /* ── 公開API ── */

  @api
  applySavedHighlight() {
    // C6は編集可能なテーブル数値セルを持たないため空実装
  }
}
