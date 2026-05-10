/**
 * RG（補正値登録）系 OpenAPI モデル定義
 *
 * sample 系 import で参照されていた c/f003CvV0000OpenApiModel に対応する RG 版。
 * リクエスト Dto は constructFromObject 静的メソッドでインスタンス化する慣例（OpenAPI generator 流）。
 * 本ファイルは 0501 補正値登録 API のリクエスト型スタブを提供する。
 */

/**
 * 補正値登録 API リクエスト Dto
 *
 * sample CvV0103AddRequest.constructFromObject(reqParam) と同形式で呼ばれる。
 * スタブ実装ゆえ受け取った Object をそのまま返す。
 * 業務 API 確定後にフィールド単位の型検証・キャスト・必須チェックを追加する想定。
 */
export class RgV0501HoseichiRegisterRequest {
  /**
   * 素の Object からインスタンスを生成する。
   *
   * @param {object} obj リクエスト本体（隠し項目 + 補正値項目）
   * @returns {object} 渡された obj をそのまま返す（簡易実装）
   */
  static constructFromObject(obj) {
    return obj;
  }
}
