/**
 * RG（補正値登録）系メッセージ定数
 *
 * sample 系 import で参照されていた c/f003CvV0000MsgConst / c/f003GsV0000MsgConst に対応する RG 版。
 * 命名規約（既存 GsV0000MsgConst 踏襲）: YUS<サブシステム><画面ID><連番>C_<種別>
 *   種別: I=Information, W=Warning, E=Error
 */

// 確認: 補正値登録ボタン押下時の確認モーダルに表示する。
export const YUSRG0501C_I = "補正値を登録します。よろしいですか？";

// 通知: 補正値登録 API 成功時に Success トーストへ表示する。
export const YUSRG0502C_I = "補正値登録が完了しました。";
