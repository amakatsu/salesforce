import { LightningElement, track } from 'lwc';
 
// ========================================
// 定数定義: サンプルデータ
// ========================================
 
 
// ========================================
// 定数定義: 選択肢オプション
// ========================================
 
/**
* 担保詳細のコンボボックスオプション
*/
const DETAIL_OPTIONS = [
  { label: '一般法人保証（非上場）', value: '不動産担保' },
  { label: '動産担保', value: '動産担保' },
  { label: '債権担保', value: '債権担保' },
  { label: '保証人', value: '保証人' },
  { label: '連帯保証', value: '連帯保証' },
  { label: '根保証', value: '根保証' },
  { label: '質権', value: '質権' },
  { label: '抵当権', value: '抵当権' },
  { label: '譲渡担保', value: '譲渡担保' },
  { label: 'その他', value: 'その他' }
];
 
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
 
 
/** 32文字のサンプルテキスト */
 
const SAMPLE_TEXT_25 = generatePatternStringWithNumbers('half', 25);
 
const SAMPLE_TEXT_32 = generatePatternStringWithNumbers('half', 66);
 
/** 366文字のサンプルテキスト */
const SAMPLE_TEXT_366 = generatePatternStringWithNumbers('half', 366);
 
 
// ========================================
// コンポーネントクラス
// ========================================
 
/**
* 担保詳細フォームコンポーネント
* 担保/保証の詳細情報を入力するフォーム
*/
export default class f003RgV9962TanpoNgaiLinkC1 extends LightningElement {
  // フォームデータ
  @track collateralGuarantee = SAMPLE_TEXT_25;
  @track selectedDetail = '';
  @track jurisdiction = SAMPLE_TEXT_32;
  @track governingLaw = SAMPLE_TEXT_32;
  @track note = SAMPLE_TEXT_366;
 
  /**
   * 担保詳細のコンボボックスオプション
   * @returns {Array} オプションリスト
   */
  get detailOptions() {
    return DETAIL_OPTIONS;
  }
 
  // ========================================
  // イベントハンドラー
  // ========================================
 
  /**
   * Collateral/Guarantee入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleCollateralChange(event) {
    this.collateralGuarantee = event.target.value;
  }
 
  /**
   * 担保詳細コンボボックス変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleDetailChange(event) {
    this.selectedDetail = event.target.value;
  }
 
  /**
   * Jurisdiction入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleJurisdictionChange(event) {
    this.jurisdiction = event.target.value;
  }
 
  /**
   * Governing Law入力変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleGoverningLawChange(event) {
    this.governingLaw = event.target.value;
  }
 
  /**
   * Note変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleNoteChange(event) {
    this.note = event.target.value;
  }
}