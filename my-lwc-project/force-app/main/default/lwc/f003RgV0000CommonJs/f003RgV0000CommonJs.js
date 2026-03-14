/**
 * f003RgV系共通ユーティリティ
 * サンプルデータ生成関数と定数を一元管理
 */

// ========================================
// サンプルデータ生成関数
// ========================================

/**
 * パターン化されたサンプル文字列を生成する
 * @param {string} pattern - mixedByte / mixedChar / half / numeric
 * @param {number} length - 生成する文字(またはバイト)長
 * @returns {string} パターン化されたサンプル文字列
 */
const generateData = (pattern, length) => {
  if (!Number.isInteger(length) || length <= 0) {
    throw new Error("length は 1 以上の整数を指定してください。");
  }

  const FULL = "〇";
  const MARK = "●";
  const HALF = "W";
  const DIGIT = "9";

  const twoDigitLabel = (n) => String(n).slice(-2);

  const generateLabeledByChars = (n, baseChar, markChar) => {
    let result = "";

    for (let pos = 1; pos <= n; pos++) {
      const indexInBlock = ((pos - 1) % 10) + 1;
      const blockNumber = Math.floor((pos - 1) / 10) + 1;

      let ch = baseChar;

      if (markChar && indexInBlock === 5) {
        ch = markChar;
      }

      if (indexInBlock === 9 || indexInBlock === 10) {
        const label = twoDigitLabel(blockNumber * 10);
        const digitIndex = indexInBlock - 9;
        ch = label[digitIndex];
      }

      result += ch;
    }

    return result;
  };

  if (pattern === "half") {
    return generateLabeledByChars(length, HALF, null);
  }
  if (pattern === "numeric") {
    return DIGIT.repeat(length);
  }
  if (pattern === "mixedChar") {
    return generateLabeledByChars(length, FULL, MARK);
  }
  if (pattern === "mixedByte") {
    const tokenForBlock = (block) => {
      if (block % 10 === 0) return twoDigitLabel(block);
      if (block % 5 === 0) return MARK;
      return FULL;
    };

    let result = "";
    let usedBytes = 0;
    let block = 1;

    while (length - usedBytes >= 2) {
      result += tokenForBlock(block++);
      usedBytes += 2;
    }

    if (usedBytes < length) {
      result += HALF;
    }

    return result;
  }

  throw new Error(
    'pattern は "mixedByte" / "mixedChar" / "half" / "numeric" のいずれかを指定してください。'
  );
};

export { generateData };
