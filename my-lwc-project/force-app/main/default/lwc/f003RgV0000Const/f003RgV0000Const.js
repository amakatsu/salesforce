/**
 * RG（補正値登録）系汎用定数
 *
 * sample 系 import で参照されていた c/f003CvV0000Const に対応する RG 版。
 * 画面 ID / サブシステム ID / API 接続先名等、RG 業務横断で共有される定数を集約する。
 */

// 画面定義。RequestMetadataDto.setDisplayId / setDisplayName で使われる。
// sample CV_DISP_LIST.CvV0103.{ID,NAME} と同構造。
export const RG_DISP_LIST = {
  RgV0501: {
    ID: "RgV0501",
    NAME: "与信禀査書査定書計数情報"
  }
};

// サブシステム識別子。RequestMetadataDto.setSubSystemId() で使われ、
// バックエンドが業務系統を分類する際のキーとなる。
// sample SUBSYSTEM_ID_COVENANTS と対をなす RG 系版。
export const SUBSYSTEM_ID_RG = "RG";

// API 接続先名。postRequest / getRequest / deleteRequest の第 3 引数として渡され、
// 接続先 endpoint base / 認証コンテキストを決定する。
// sample CV_CONNECT と対をなす RG 系版。
export const RG_CONNECT = "RG_CONNECT";
