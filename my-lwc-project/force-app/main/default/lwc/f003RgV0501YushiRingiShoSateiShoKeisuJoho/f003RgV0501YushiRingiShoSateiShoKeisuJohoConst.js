/**
 * f003RgV0501 与信禀査書査定書計数情報 用 内部定数
 *
 * 親（無印）および ./functions/*Exe から相対パスで import される component bundle 内サブモジュール。
 * sample/ 配下に存在した CvV0103KanrenRinsaJohoMConst のパターンを踏襲し、
 * OPERATION（業務操作識別子）/ ENDPOINT（API パス）/ BTN_PATTERN（ボタン押下種別）の 3 種を集約する。
 */

// 業務操作識別子。RequestMetadataDto.setOperationName() に渡すため、API ヘッダの監査ログに記録される。
export const OPERATION = {
  INIT: "init",
  HOSEICHI_REGISTER: "hoseichiregister"
};

// API エンドポイントパス。postRequest / getRequest の第 2 引数として使われる。
export const ENDPOINT = {
  INIT: "/init",
  HOSEICHI_REGISTER: "/hoseichi-register"
};

// ボタン押下種別。確認モーダル文言や operationName の分岐に用いる。
// sample/c/f003CvV0103KanrenRinsaJohoMConst の BTN_PATTERN と同形式。
export const BTN_PATTERN = {
  HOSEICHI_REGISTER: "HOSEICHI_REGISTER"
};
