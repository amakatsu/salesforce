/**
 * f003 共通ユーティリティ群
 *
 * 文字列・数値の汎用ヘルパを集約する純粋関数のモジュール。
 * 業務ロジックを含まないため jest テストでは実体使用が望ましい。
 */

/**
 * 値を指定桁数まで左から `0` で埋めて文字列を返す。
 * null / undefined は空文字を返す（呼び出し側のガード簡略化のため）。
 *
 * @param {string|number|null|undefined} value 埋める対象（数値・文字列いずれも可、内部で String 化）
 * @param {number} len                          最終桁数
 * @returns {string}                            左 0 埋め後の文字列、もしくは空文字
 *
 * @example
 *   paddingZero("10", 3)      // "010"
 *   paddingZero("10", 7)      // "0000010"
 *   paddingZero(0, 4)         // "0000"
 *   paddingZero(null, 5)      // ""
 *   paddingZero(undefined, 5) // ""
 */
export function paddingZero(value, len) {
  if (value === null || value === undefined) return "";
  return String(value).padStart(len, "0");
}
