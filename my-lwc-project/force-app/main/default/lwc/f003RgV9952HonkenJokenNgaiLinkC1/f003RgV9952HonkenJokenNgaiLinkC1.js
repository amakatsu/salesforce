import { LightningElement } from 'lwc';
 
 
const generatePatternStringWithNumbers = (pattern, length) => {
  if (!Number.isInteger(length) || length <= 0) {
    throw new Error("length は 1 以上の整数を指定してください。");
  }
 
  const FULL = "〇";
  const MARK = "●"; // 5の位置用
  const HALF = "W";
  const DIGIT = "9";
 
  // 10,20,30,... → "10","20","30"...（3桁以上は末尾2桁だけ）
  const twoDigitLabel = (n) => String(n).slice(-2);
 
  // 10文字ブロックごとに「ベース文字＋末尾2桁ラベル」を作るパターン
  //   baseChar: 〇 / W
  //   markChar: mixedChar のときだけ ●（half のときは null）
  const generateLabeledByChars = (n, baseChar, markChar) => {
    let result = "";
 
    for (let pos = 1; pos <= n; pos++) {
      const indexInBlock = ((pos - 1) % 10) + 1;      // 1〜10
      const blockNumber  = Math.floor((pos - 1) / 10) + 1; // 1,2,3,...
 
      let ch = baseChar;
 
      // 5文字目は ●（mixedChar のみ）
      if (markChar && indexInBlock === 5) {
        ch = markChar;
      }
 
      // 9–10文字目は "10","20","30"... の末尾2桁
      if (indexInBlock === 9 || indexInBlock === 10) {
        const label = twoDigitLabel(blockNumber * 10); // 10→"10", 100→"00"
        const digitIndex = indexInBlock - 9;           // 9→0, 10→1
        ch = label[digitIndex];
      }
 
      result += ch;
    }
 
    return result;
  };
 
  // --- half / numeric ---
  if (pattern === "half") {
    // ベースW＋各10文字ブロックの末尾2桁に "10","20"... を入れる
    return generateLabeledByChars(length, HALF, null);
  }
  if (pattern === "numeric") {
    return DIGIT.repeat(length);
  }
 
  // --- mixedChar（全角・文字数指定） ---
  if (pattern === "mixedChar") {
    // ベース〇＋5文字目●＋9,10文字目に "10","20"...（末尾2桁）
    return generateLabeledByChars(length, FULL, MARK);
  }
 
  // --- mixedByte（全角=2B / 半角=1B・バイト数指定） ---
  if (pattern === "mixedByte") {
    // ブロック番号ごとのトークン（どれも「2バイトぶん」として扱う）
    const tokenForBlock = (block) => {
      if (block % 10 === 0) return twoDigitLabel(block); // 10→"10", 20→"20", 100→"00"
      if (block % 5  === 0) return MARK;                 // 5,15,25,...ブロック
      return FULL;                                       // それ以外は〇
    };
 
    let result    = "";
    let usedBytes = 0;
    let block     = 1;
 
    // 2バイト単位でトークンを詰める
    while (length - usedBytes >= 2) {
      result    += tokenForBlock(block++);
      usedBytes += 2;
    }
 
    // 端数 1 バイトがあれば W で埋める
    if (usedBytes < length) {
      result += HALF;
    }
 
    return result;
  }
 
  throw new Error('pattern は "mixedByte" / "mixedChar" / "half" / "numeric" のいずれかを指定してください。');
};
export default class f003RgV9952HonkenJokenNgaiLinkC1 extends LightningElement {
    // Active sections in the component
    activeSections = ['b'];
 
    // Conditions with transaction conditions and selected conditions
    conditions = [
        { id: 1, transactionCondition: generatePatternStringWithNumbers('half', 29), selectedCondition: '' },
        { id: 2, transactionCondition: generatePatternStringWithNumbers('half', 29), selectedCondition: '' },
        { id: 3, transactionCondition: generatePatternStringWithNumbers('half', 29), selectedCondition: '' },
        { id: 4, transactionCondition: '', selectedCondition: '' },
        { id: 5, transactionCondition: '', selectedCondition: '' }
    ];
 
    // Comment with 366 characters of repeated pattern 'W' with numbers every 10 characters
    honkenJokenComment = generatePatternStringWithNumbers('half', 366);
 
    // Options for conditions
    conditionOptions = [
        { label: '荷受入に当行以外を指定', value: 'option1' },
        { label: '荷受入に当行以外を指定', value: 'option2' },
        { label: '荷受入に当行以外を指定', value: 'option3' },
        { label: '荷受入に当行以外を指定', value: 'option4' },
        { label: '荷受入に当行以外を指定', value: 'option5' }
    ];
 
 
 
    // Handle changes to condition selection
    handleConditionChange(event) {
        const conditionId = event.target.dataset.id;
        const selectedCondition = event.target.value;
        this.conditions = this.conditions.map(condition => {
            if (condition.id === parseInt(conditionId, 10)) {
                return { ...condition, selectedCondition };
            }
            return condition;
        });
    }
}