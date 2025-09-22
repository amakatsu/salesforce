/*************************************************************************************************************
 * 処理名   ：  データチェック
 * 処理概要 ：  単項目・相関チェックに関連する処理
 ************************************************************************************************************/
// ========================================
// モック定数・関数（依存コンポーネントの代替）
// ========================================

// エラーメッセージ定数（モック）
const YUSGS5000C_E = "入力値が不正です。";
const YUSGS5002C_E = "入力形式が正しくありません。パターン: {0}";
const YUSGS5003C_E = "最大値 {0} を超えています。";
const YUSGS5004C_E = "最小値 {0} を下回っています。";
const YUSGS5006C_E = "必須項目です。";
const YUSGS5007C_E = "日付は {0} 以前で入力してください。";
const YUSGS5008C_E = "日付は {0} 以降で入力してください。";
const YUSGS5009C_E = "最大文字数 {0} を超えています。";
const YUSGS5010C_E = "最小文字数 {0} 未満です。";
const YUSGS5012C_E = "小数点以下は {0} 桁以内で入力してください。";
const YUSGS5013C_E = "最大バイト数 {0} を超えています。";
const YUSGS5093C_E = "文字数は {0} 桁で入力してください。";

// パターン定数（モック）
const PATTERNS = {
  NUMBER_COMMA_SIGN: {
    regex: "^[+-]?\\d{1,3}(,\\d{3})*(\\.\\d+)?$",
    name: "数値（カンマ区切り）"
  }
};

// ユーティリティ関数（モック）
const getMessage = (template, ...args) => {
  let message = template;
  args.forEach((arg, index) => {
    message = message.replace(`{${index}}`, arg);
  });
  return message;
};

const getErrorField = async (displayId, code) => {
  // モック: エラーフィールド情報を返す
  console.log("getErrorField called with:", displayId, code);
  return [{ field: "mock", message: "モックエラー" }];
};

const checkDigits = (elm) => {
  // モック: 高精度数値チェック
  console.log("checkDigits called for element:", elm?.name || elm?.type);
  return "";
};

/**
 * HTMLの要素に対して、エラーの挿入、取出しを行う。
 *
 * @param { Element | null } field     フィールド情報が詰まったノードオブジェクトもしくはNull値
 *
 */
export const showValidity = (field, CustomValidity = "") => {
  try {
    if (field) {
      field.setCustomValidity(CustomValidity);
      field.reportValidity();
    }
    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
  }
  // END-NOSCAN
  // SonarQube コードブロックを無視する設定
};

/**
 * 文字列がSJISで指定したbyte桁数以下であるかを判断する。
 *
 * @param { string }  str      - バイト数を計算する対象の文字列
 * @param { number }  maxBytes - 最大バイト数
 * @return { boolean }         - バイト数チェックの結果
 *
 */
export const checkByteLength = (str, maxBytes) => {
  try {
    let size = 0;
    const bytes = Number(maxBytes);
    if (!bytes) throw new TypeError("'maxBytes' must be a number");

    for (let i = 0; i < str.length; i++) {
      const charCode = str.charCodeAt(i);

      if (
        // ASCII文字
        (0x0 <= charCode && charCode < 0x81) ||
        // PUAのため基本的には意味を持たない領域（SJIS変換対策）
        charCode === 0xf8f0 ||
        // 半角カナ
        (0xff61 <= charCode && charCode < 0xffa0) ||
        // PUAのため基本的には意味を持たない領域（SJIS変換対策）
        (0xf8f1 <= charCode && charCode < 0xf8f4)
      ) {
        // 1バイトの文字
        size += 1;
      } else {
        // 2バイトの文字
        size += 2;
      }
    }

    return size <= bytes;

    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 要素のstep数から小数点の桁数を取得する。
 *
 * @param { number | string } num     対象の要素のstep数（anyの場合stringのため、stringも許容）
 * @returns { number } 小数点の桁数
 */
export const getDecimalPlaces = (num) => {
  try {
    let data = num || "any";

    // anyの場合、この時点で返却
    if (data === "any") return 0;

    // 文字列で連携されるため、一度数値に変換する
    data = Number(data);

    // 異常値の場合、この時点で返却
    if (!data || data < 0) return 0;

    // 数値を指数表記で確認
    const exponential = data.toExponential();

    // 指数部分を取得
    let exponent = parseInt(exponential.split("e")[1], 10);

    // 仮数部分も取得
    const mantissa = exponential.split("e")[0];

    // 仮数の桁数を取得
    const mDigit = mantissa.toString().replace(".", "").replace("-", "").length;

    // 仮数が1桁以外の場合、指数を調整する。
    // 0.22 → 2.2-e1 これだと1桁になるのでおかしいことになる。そのためこの桁数を調整する。
    if (mDigit !== 1) exponent = exponent + (mDigit - 1);

    if (exponent < 0) {
      // 加算値の計算
      const adjustment = 1 - Math.pow(10, exponent);
      data = adjustment;
    }

    // 数値を文字列に変換
    const numStr = data.toString();
    // 小数点の位置を取得
    const decimalIndex = numStr.indexOf(".");

    // 小数点が存在しない場合は0を返す
    if (decimalIndex === -1) return 0;

    // 小数点以下の桁数を計算
    return numStr.length - decimalIndex - 1;

    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 相関チェックの結果を反映する処理
 *
 *  @param { string }                       displayId     画面Id
 *  @param { Array.<Map.<string, Object>> } errors        APIから返却されたerrorsの中身
 *  @param { Array.<Element> }              dataList      親コンポーネントから抽出されたオブジェクトのリスト
 
*
 */
export const showCorrelationError = async (displayId, errors, dataList) => {
  try {
    if (typeof displayId !== "string" || !displayId)
      throw TypeError("'displayId' must be a truthy string");
    if (!Array.isArray(errors)) throw TypeError("'errors' must be an array");

    if (!Array.isArray(dataList) && !(dataList instanceof NodeList)) {
      throw new TypeError("'dataList' is not iterable");
    }

    // 取得したエラーの数に応じて、エラー対象フィールド取得処理を呼び出し、結果を各子コンポーネントに反映する。
    await Promise.all(
      errors.map(async (e) => {
        // コード値がない場合はスキップ
        if (!e.code) return;
        const errorFieldList = await getErrorField(displayId, e.code);
        // 子コンポーネント側に相関エラー反映処理がある場合に、処理を実行する。
        const promises = Array.from(dataList).map(async (c) => {
          if (typeof c.correlationCheck === "function")
            c.correlationCheck(errorFieldList);
        });
        await Promise.all(promises);
      })
    );

    return;
    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 入力値がスペースのみの空白文字列であるかを判定する処理
 *
 * @param { Object }       val 入力値
 * @returns { boolean }        空チェック結果（true: 空, false:空以外）
 *
 */
export const checkIsBlankInput = (val) => {
  try {
    if (typeof val === "string") return val.trim() === "";
    if (Array.isArray(val)) return val.length === 0;
    if (typeof val === "object" && val !== null)
      return Object.keys(val).length === 0;
    if (typeof val === "number") return Number.isNaN(val);
    if (val === null || val === undefined || val === "") return true;

    throw new TypeError("Unsupported input type");
    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 必須項目の個別判定処理
 *
 * @param { Object }       elm DOM要素
 * @returns { string }         エラーメッセージ
 *
 */
export const checkRequiredField = (elm) => {
  try {
    // チェックボックスの必須チェック
    if (elm.type === "checkbox") return elm.checked ? "" : YUSGS5006C_E;

    return checkIsBlankInput(elm.value) ? YUSGS5006C_E : "";
    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 右寄せ数値項目へのエラー判定の連携処理
 *
 * @param { Object }       node     DOM要素（右寄せ数値コンポーネント）
 * @param { Object }       nodeList DOM要素リスト
 * @param { Object }       reqFlg   必須項目フラグ
 *
 */
export const activateRightNumber = (node, nodeList, reqFlg) => {
  try {
    const numElement = Array.from(nodeList).filter(
      (d) => d.dataset.id === node.dataset.id
    )[0];
    numElement.setErrors(reqFlg);
    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * Byte数制限のチェック
 *
 * @param { Object }       elm DOM要素
 * @returns { string }         エラーメッセージ
 *
 */
export const checkByteLimit = (elm) => {
  try {
    const str = elm.value;
    const maxLengthValue = elm.dataset.byte;

    // valueが未定義な場合、検証不可の値の場合は検証せずに返却する。
    if (typeof str !== "string")
      throw new TypeError("'value' must be a string");
    // 空文字を許容しない正規表現
    const intPattern = /^\d+$/;
    if (!intPattern.test(maxLengthValue) || !maxLengthValue)
      throw new TypeError("'dataset.byte' must be an integer");

    // 最大値が0の場合は検証せずに返却する。
    if (!maxLengthValue) return "";

    const byteCheckFlag = checkByteLength(str, maxLengthValue);

    if (!byteCheckFlag) return getMessage(YUSGS5013C_E, maxLengthValue);

    return "";

    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 最大桁数のチェック
 *
 * @param { Object }       elm DOM要素
 * @returns { string }         エラーメッセージ
 *
 */
export const checkMaxLength = (elm) => {
  try {
    const str = elm.value;
    const maxLength = Number(elm.maxLength);
    const minLength = Number(elm.minLength);

    // 異常値の場合、この時点で返却
    if (maxLength < 0 || Number.isNaN(maxLength)) return "";

    if (str.length > maxLength) {
      if (maxLength === minLength)
        return getMessage(YUSGS5093C_E, elm.maxLength);

      return getMessage(YUSGS5009C_E, elm.maxLength);
    }

    return "";

    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

/**
 * 最小桁数のチェック
 *
 * @param { Object }       elm DOM要素
 * @returns { string }         エラーメッセージ
 *
 */
export const checkMinLength = (elm) => {
  try {
    const str = elm.value;
    const maxLength = Number(elm.maxLength);
    const minLength = Number(elm.minLength);

    // 異常値の場合、この時点で返却
    if (minLength < 0 || Number.isNaN(minLength)) return "";

    if (!elm.required && str.trim().length === 0) return "";

    if (minLength > str.length) {
      if (maxLength === minLength)
        return getMessage(YUSGS5093C_E, elm.minLength);

      return getMessage(YUSGS5010C_E, elm.minLength);
    }

    return "";

    // SonarQube コードブロックを無視する設定
    // BEGIN-NOSCAN
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
    // END-NOSCAN
    // SonarQube コードブロックを無視する設定
  }
};

// SonarQube コードブロックを無視する設定
// BEGIN-NOSCAN

/**
 * validationチェックのメイン処理
 *
 * @param { Object }       elm DOM要素
 * @returns { string }         エラーメッセージ
 *
 */
export const getErrorMessage = (elm) => {
  try {
    let message = "";

    // 必須チェックの確認
    if (elm.validity.valueMissing) return YUSGS5006C_E;
    // type(型)チェックの確認
    if (elm.validity.typeMismatch) return YUSGS5000C_E;

    // 正規表現チェックの確認
    if (elm.validity.patternMismatch) {
      // 高精度数値の正規表現であるか
      const isNumCommaSign = elm.pattern === PATTERNS.NUMBER_COMMA_SIGN.regex;

      // チェックした正規表現を共通定数から取得する
      for (const [, value] of Object.entries(PATTERNS)) {
        const isPatternMatch = value.regex === elm.pattern;
        // 共通定数のリストに一致した場合、高精度数値のメッセージか、正規表現パターンのメッセージどちらを返却する。
        if (isPatternMatch)
          return isNumCommaSign
            ? YUSGS5000C_E
            : getMessage(YUSGS5002C_E, value.name);
      }

      return YUSGS5000C_E;
    }

    // 最大値チェックの確認
    if (elm.validity.rangeOverflow)
      return elm.type === "date"
        ? getMessage(YUSGS5007C_E, elm.max)
        : getMessage(YUSGS5003C_E, elm.max);
    // 最小値チェックの確認
    if (elm.validity.rangeUnderflow)
      return elm.type === "date"
        ? getMessage(YUSGS5008C_E, elm.min)
        : getMessage(YUSGS5004C_E, elm.min);

    // step（刻み値）チェックの確認
    if (elm.validity.stepMismatch) {
      const numStr = getDecimalPlaces(elm.step);

      return getMessage(YUSGS5012C_E, numStr);
    }

    // 最大桁数チェックの確認
    if (elm.validity.tooLong)
      return elm.maxLength === elm.minLength
        ? getMessage(YUSGS5093C_E, elm.maxLength)
        : getMessage(YUSGS5009C_E, elm.maxLength);
    // 最小桁数チェックの確認
    if (elm.validity.tooShort)
      return elm.maxLength === elm.minLength
        ? getMessage(YUSGS5093C_E, elm.minLength)
        : getMessage(YUSGS5010C_E, elm.minLength);

    // 不正入力チェックの確認
    if (elm.validity.badInput) return YUSGS5000C_E;

    // 特定の必須チェックの確認
    if (elm.required) message = checkRequiredField(elm);

    // 最大値チェックの確認（デフォルトが検知しない範囲を補助するため）
    if (!message && elm.maxLength) message = checkMaxLength(elm);
    // 最小値チェックの確認（デフォルトが検知しない範囲を補助するため）
    if (!message && elm.minLength) message = checkMinLength(elm);
    // バイト数チェックの確認
    if (!message && "byte" in elm.dataset) message = checkByteLimit(elm);
    // 高精度数値項目編集チェックの確認
    if (!message && elm.classList.contains("hp-num"))
      message = checkDigits(elm);

    return message;
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
  }
};
// END-NOSCAN
// SonarQube コードブロックを無視する設定

/**
 * 単項目チェックを実施する処理
 *
 * @param { Array.<Object> } childDataList     子コンポーネントから抽出されたDOM要素のリスト
 * @param { Array.<String> } reqList            ボタン事の必須項目リスト
 * @param { Object } data                       コンポーネント全体のNodeList
 *
 * @returns { number }  エラーの有無をフラグで返却する。(0:エラーなし 1: エラーあり)
 */

// SonarQube コードブロックを無視する設定
// BEGIN-NOSCAN

export const validateElement = (childDataList, reqList = [], data = []) => {
  try {
    if (!Array.isArray(childDataList)) {
      throw new TypeError("'childDataList' must be an array");
    }

    if (!Array.isArray(reqList)) {
      throw new TypeError("'reqList' must be an array");
    }

    if (!Array.isArray(data) && !(data instanceof NodeList)) {
      throw new TypeError("'data' is not iterable");
    }

    let errorCount = 0;
    let message = "";
    let reqFlg = false;
    let eFlg = false;
    childDataList.forEach((c) => {
      // HTMLElement以外の要素がある場合は例外処理とする。
      if (!(c instanceof HTMLElement))
        throw new TypeError("'c' must be a HTMLElement");
      // setCustomValidity()を持たない要素はスキップする。
      if (typeof c.setCustomValidity !== "function") return;

      // メッセージの初期化
      message = "";
      // 必須フラグ初期化
      reqFlg = false;

      // ボタン毎必須チェック判定
      if (reqList.includes(c.dataset.id)) {
        // 必須チェック
        message = checkRequiredField(c);

        // 必須フラグ管理
        if (message) reqFlg = true;

        // 右寄せ数値の必須チェック
        // 必須チェックの時点で状態は確定しているため、右寄せ数値は背景色の変更や、フィールドの活性化を別途実施する。
        if (c.name === "rightNum") activateRightNumber(c, data, reqFlg);
      }

      // 通常のvalidityチェック
      if (!reqFlg) message = getErrorMessage(c);

      if (c.name === "rightNum" && data.length > 0) {
        // 右寄せ数値コンポーネント内で単項目エラーがあるときフォーカスをあてる必要がある
        eFlg = message ? true : false;
        activateRightNumber(c, data, eFlg);
      }

      showValidity(c, message);
      if (!c.validity.valid || message) errorCount = 1;
    });

    return errorCount;
  } catch (e) {
    // D4部のロギング処理が実装される想定

    // 例外を再スローする。
    throw e;
  }
};

// END-NOSCAN
// SonarQube コードブロックを無視する設定
