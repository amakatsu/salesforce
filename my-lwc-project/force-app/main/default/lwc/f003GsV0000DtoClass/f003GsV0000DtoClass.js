/**
 * f003 共通 DTO クラス群
 *
 * API リクエスト用の業務メタデータを保持する単純な setter ベースのクラス。
 * 業務ロジックを持たず、setter で同名 field に値を格納するだけの構造。
 * jest テストでは実体使用し、`getMetadata()` または field 直参照で検証する。
 */

/**
 * リクエスト業務情報 DTO。
 * 8 個の setter（業務メタ各項目）と 1 個の `getMetadata()` を提供する。
 * setter は fluent（this を返す）ではなく、純粋に内部フィールドを更新するのみ。
 */
export class RequestMetadataDto {
  /** @param {string} value 業務サブシステム ID */
  setSubSystemId(value) {
    this.subSystemId = value;
  }

  /** @param {string} value 画面 ID */
  setDisplayId(value) {
    this.displayId = value;
  }

  /** @param {string} value 画面論理名 */
  setDisplayName(value) {
    this.displayName = value;
  }

  /** @param {string} value オペレーション名（INIT/ADD/UPDATE/DELETE/HOSEICHI_REGISTER 等） */
  setOperationName(value) {
    this.operationName = value;
  }

  /** @param {string} value 店番（必要に応じてゼロ埋め済み） */
  setBranchNo(value) {
    this.branchNo = value;
  }

  /** @param {string} value 取引先番号 */
  setCustomerNo(value) {
    this.customerNo = value;
  }

  /** @param {string} value 案件番号（LcNo） */
  setLcNo(value) {
    this.lcNo = value;
  }

  /** @param {string} value 案件枝番（LcSeqNo） */
  setLcSeqNo(value) {
    this.lcSeqNo = value;
  }

  /**
   * 全フィールドを 1 つのオブジェクトとして返す（API 送信用）。
   * 未設定フィールドは undefined のまま含まれる（呼び出し側で除外要なら適宜処理）。
   *
   * @returns {{
   *   subSystemId: string|undefined,
   *   displayId: string|undefined,
   *   displayName: string|undefined,
   *   operationName: string|undefined,
   *   branchNo: string|undefined,
   *   customerNo: string|undefined,
   *   lcNo: string|undefined,
   *   lcSeqNo: string|undefined
   * }}
   */
  getMetadata() {
    return {
      subSystemId: this.subSystemId,
      displayId: this.displayId,
      displayName: this.displayName,
      operationName: this.operationName,
      branchNo: this.branchNo,
      customerNo: this.customerNo,
      lcNo: this.lcNo,
      lcSeqNo: this.lcSeqNo
    };
  }
}
