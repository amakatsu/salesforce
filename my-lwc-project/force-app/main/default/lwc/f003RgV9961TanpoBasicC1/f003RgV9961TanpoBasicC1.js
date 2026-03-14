/**
* 担保カテゴリボードコンポーネント
* 担保条件の登録・編集を行うフォームコンポーネント
*/
import { LightningElement, api, track } from "lwc";
import LightningConfirm from "lightning/confirm";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { generateData } from "c/f003RgV0000CommonJs";

const SAMPLE_TEXT_30 = generateData("mixedByte", 30);
const SAMPLE_TEXT_30_CHAR = generateData("mixedChar", 30);
const SAMPLE_TEXT_60 = generateData("mixedByte", 60);
const SAMPLE_TEXT_140 = generateData("mixedByte", 140);
const SAMPLE_TEXT_280 = generateData("mixedByte", 280);
const SAMPLE_TEXT_390 = generateData("mixedByte", 390);

// ========================================
// 定数: テンプレート
// ========================================
 
/**
* 担保条件２の空白行テンプレート
*/
const BLANK_COLLATERAL_DETAIL_ROW = {
  condition: "",
  timing: "",
  dueDate: ""
};
 
/** 担保条件２の最大追加可能件数 */
const MAX_COLLATERAL_DETAIL_ROWS = 9;
 
// ========================================
// 定数: 選択肢オプション
// ========================================
 
/**
* 共通の選択肢を生成するヘルパー関数
* @param {Array} items - ラベルと値のペアの配列
* @returns {Array} オプションリスト
*/
const createOptions = (items) =>
  items.map(([label, value]) => ({ label, value }));
 
/**
* すべての選択肢を一元管理するオブジェクト
*/
const OPTIONS = {
  // 科目の選択肢
  subject: [
    { label: "01", value: "01" },
    { label: "02", value: "02" },
    { label: "03", value: "03" },
    { label: "04", value: "04" }
  ],
 
  // 新規・既存の選択肢
  dealType: createOptions([
    ["新規", "01"], // 新規
    ["既存", "02"], // 既存
    ["新規・協会優先", "03"], // 新規協会優先
    ["既存・協会優先", "04"], // 既存協会優先
    ["新規・DHC優先", "05"], // 新規DHC優先
    ["既存・DHC優先", "06"] // 既存DHC優先
  ]),
 
  // 設定区分の選択肢
  setupCategory: createOptions([
    ["緊急措置", "01"], // 緊急措置
    ["緊急措置", "02"] // 緊急措置
  ]),
 
  // 評価方法の選択肢
  extinguish: createOptions([
    ["DPR", "01"], // DPR
    ["自店", "02"] // 自店
  ]),
 
  // 根担保紐付けの選択肢
  rootLink: createOptions([
    ["極度", "01"], // 極度
    ["実残", "02"] // 実残
  ]),
 
  // 保証種別の選択肢（パターン別）
  // "01": normalパターン（一般的な保証）
  // "02": tkkパターン（ＴＫＫ、全石協）
  // "03": dhcパターン（ＤＨＣ保証）
  // "04": associationGuaranteeパターン（協会保証）
  guaranteeType: {
    "01": createOptions([
      ["特定債務保証", "01"], // 特定債務保証
      ["極度期限付保証", "02"], // 極度期限付保証
      ["特定極度根保証", "03"], // 特定極度根保証
      ["特定根保証", "04"], // 特定根保証
      ["包括根保証", "05"], // 包括根保証
      ["包括根（極度付）", "06"], // 包括根（極度付）
      ["包括根（期限付）", "07"], // 包括根（期限付）
      ["その他", "99"] // その他
    ]),
    "02": createOptions([
      ["貸付個別保証", "11"], // 貸付個別保証
      ["貸付根保証", "12"], // 貸付根保証
      ["手割個別保証", "13"], // 手割個別保証
      ["手割根保証", "14"], // 手割根保証
      ["その他", "99"] // その他
    ]),
    "03": createOptions([
      ["極度期限付保証", "21"], // 極度期限付保証
      ["貸付個別保証", "22"], // 貸付個別保証
      ["その他", "99"] // その他
    ]),
    "04": createOptions([
      ["貸付個別保証", "31"], // 貸付個別保証
      ["貸付根保証", "32"], // 貸付根保証
      ["手割個別保証", "33"], // 手割個別保証
      ["手割根保証", "34"], // 手割根保証
      ["その他", "99"] // その他
    ])
  },
 
  // 保証人区分の選択肢
  individualCorporate: createOptions([
    ["代表取締役", "01"], // 代表取締役
    ["取締役・理事・執行役", "02"], // 取締役・理事・執行役
    ["大株主", "03"], // 大株主
    ["共同事業者", "04"], // 共同事業者
    ["配偶者（事業性）", "05"], // 配偶者（事業性）
    ["配偶者（非事業性）", "06"], // 配偶者（非事業性）
    ["第三者個人（事業性）", "07"], // 第三者個人（事業性）
    ["第三者個人（非事業性）", "08"], // 第三者個人（非事業性）
    ["法人（上場）", "09"], // 法人（上場）
    ["法人（非上場）", "10"], // 法人（非上場）
    ["金融機関", "11"], // 金融機関
    ["国際協力銀行", "12"], // 国際協力銀行
    ["全石協", "13"], // 全石協
    ["ECFA", "14"], // ECFA
    ["その他社団法人", "15"], // その他社団法人
    ["DHC", "16"], // DHC
    ["VEC", "17"], // VEC
    ["その他財団法人", "18"], // その他財団法人
    ["IPA", "19"], // IPA
    ["その他特殊法人", "20"], // その他特殊法人
    ["国・地方公共団体", "21"], // 国・地方公共団体
    ["外国政府", "22"], // 外国政府
    ["国際機関", "23"], // 国際機関
    ["外国法人", "24"], // 外国法人
    ["TKK", "25"] // TKK
  ]),
 
  // 規定区分の選択肢（法人保証の場合のみ）
  corporateGuaranteeCategory: createOptions([
    ["規定・優良", "01"], // 規定・優良
    ["規定・一般", "02"], // 規定・一般
    ["規定・その他", "03"], // 規定・その他
    ["規定外・優良", "04"], // 規定外・優良
    ["規定外・一般", "05"], // 規定外・一般
    ["規定外・その他", "06"] // 規定外・その他
  ]),
 
  // 保証期間の選択肢
  guaranteePeriod: createOptions([
    ["期間", "01"], // 期間
    ["日付", "02"] // 日付
  ]),
 
  // 協会保証種別の選択肢
  associationType: createOptions([
    ["普通保証", "01"], // 普通保証
    ["超短期", "02"] // 超短期
  ]),
 
  // 既存保証条件の選択肢
  associationExistingCondition: createOptions([
    ["有", "01"], // 有
    ["無", "02"] // 無
  ]),
 
  // 承諾条件の選択肢
  associationApprovalCondition: createOptions([
    ["条件なし", "01"], // 条件なし
    ["不動産優先充当", "02"], // 不動産優先充当
    ["連帯保証人", "03"], // 連帯保証人
    ["不動産優先充当（付保免除）", "04"], // 不動産優先充当（付保免除）
    ["不動産優先充当・連帯保証人", "05"], // 不動産優先充当・連帯保証人
    ["不動産優先充当（付保免除）・連帯保証人", "06"], // 不動産優先充当（付保免除）・連帯保証人
    ["その他", "99"] // その他
  ]),
 
  // 履行タイミングの選択肢
  timing: createOptions([
    ["取引開始前/同時", "取引開始前/同時"],
    ["取引都度", "取引都度"],
    ["取引開始後", "取引開始後"]
  ])
};
 
// ========================================
// 定数: 大分類・小分類の設定
// ========================================
 
/**
* 大分類カテゴリ設定
* 各大分類に対応する小分類の選択肢を定義
*/
const MAJOR_CATEGORY_CONFIG = {
  "01": {
    // 預金
    label: "預金",
    minors: [
      { label: "預金・規制", value: "01" },
      { label: "預金・自由", value: "02" },
      { label: "外貨預金", value: "03" },
      { label: "NCD", value: "04" }
    ]
  },
  "02": {
    // 電債
    label: "電債",
    minors: [
      { label: "規定手形", value: "05" },
      { label: "規定外手形", value: "07" }
    ]
  },
  "03": {
    // 一般保証
    label: "一般保証",
    minors: [
      { label: "個人保証", value: "41" },
      { label: "一般法人・上場", value: "34" },
      { label: "一般法人・非上場", value: "35" },
      { label: "金融機関", value: "30" },
      { label: "国・地公体", value: "31" },
      { label: "公益法人", value: "32" },
      { label: "特殊法人", value: "33" },
      { label: "ＴＫＫ", value: "36" },
      { label: "ＶＥＣ", value: "37" },
      { label: "全石協", value: "38" },
      { label: "ＩＰＡ", value: "39" },
      { label: "ＥＣＦＡ", value: "40" },
      { label: "外国政府", value: "42" },
      { label: "外国法人", value: "43" },
      { label: "国際機関", value: "44" },
      { label: "貿易金融保険", value: "73" },
      { label: "輸出入銀行", value: "74" },
      { label: "提携先保証", value: "80" },
      { label: "保証会社保証", value: "81" },
      { label: "保証保険", value: "82" },
      { label: "ＤＣ保証", value: "83" },
      { label: "ジャックス保証", value: "84" },
      { label: "ＤＨＣ保証", value: "85" },
      { label: "ＭＵＬＢ保証", value: "86" }
    ]
  },
  "04": {
    // 協会保証
    label: "協会保証",
    minors: [
      { label: "東京（環）", value: "45" },
      { label: "東京（極）", value: "46" },
      { label: "東京（活）", value: "47" },
      { label: "東京（体）", value: "48" },
      { label: "東京（一般）", value: "51" },
      { label: "東京（振興）", value: "52" },
      { label: "東京（改）", value: "53" },
      { label: "東京（都）", value: "54" },
      { label: "東京（小企）", value: "55" },
      { label: "東京（直）", value: "56" },
      { label: "東京（小特）", value: "57" },
      { label: "東京（公）", value: "58" },
      { label: "東京（その他）", value: "59" },
      { label: "神奈川（一般）", value: "61" },
      { label: "千葉（一般）", value: "62" },
      { label: "大阪（一般）", value: "63" },
      { label: "愛知（一般）", value: "64" },
      { label: "埼玉（一般）", value: "65" },
      { label: "京都（一般）", value: "66" },
      { label: "兵庫（一般）", value: "67" },
      { label: "その他協会（一般）", value: "69" },
      { label: "神奈川（制度）", value: "91" },
      { label: "千葉（制度）", value: "92" },
      { label: "大阪（制度）", value: "93" },
      { label: "愛知（制度）", value: "94" },
      { label: "埼玉（制度）", value: "95" },
      { label: "京都（制度）", value: "96" },
      { label: "兵庫（制度）", value: "97" },
      { label: "その他協会・制度", value: "99" }
    ]
  },
  "05": {
    // 動産・不動産
    label: "動産・不動産",
    minors: [
      { label: "商品", value: "11" },
      { label: "機械・器具", value: "12" },
      { label: "不動産", value: "13" },
      { label: "工場", value: "14" },
      { label: "工場財団", value: "15" },
      { label: "その他財団", value: "16" },
      { label: "船舶", value: "17" }
    ]
  },
  "06": {
    // 有価証券・債権
    label: "有価証券・債権",
    minors: [
      { label: "有価証券", value: "08" },
      { label: "債権", value: "09" },
      { label: "債権・一括支払", value: "10" }
    ]
  },
  "09": {
    // その他担保
    label: "その他担保",
    minors: [
      { label: "入居保証金", value: "18" },
      { label: "ゴルフ会員権", value: "19" },
      { label: "記名式信託受益証券", value: "20" },
      { label: "その他", value: "90" }
    ]
  }
};
 
//担保設定区分
const COLLATERAL_SETTING_CONFIG = {
  "01": {
    // 預金
    label: "預金",
    minors: [{ label: "正式", value: "1" }]
  },
  "02": {
    // 電債
    label: "電債",
    minors: [{ label: "正式", value: "1" }]
  },
  "03": {
    // 一般保証
    label: "一般保証",
    minors: [
      { label: "正式", value: "1" },
      { label: "その他", value: "9" }
    ]
  },
  "04": {
    // 協会保証
    label: "協会保証",
    minors: [{ label: "正式", value: "1" }]
  },
  "05": {
    // 動産・不動産
    label: "動産・不動産",
    minors: [
      { label: "正式", value: "1" },
      { label: "見返", value: "2" },
      { label: "権利証", value: "5" },
      { label: "Ｎ／Ｃ", value: "6" },
      { label: "その他", value: "9" }
    ]
  },
  "06": {
    // 有価証券・債権
    label: "有価証券・債権",
    minors: [{ label: "正式", value: "1" }]
  },
  "09": {
    // その他担保
    label: "その他担保",
    minors: [{ label: "正式", value: "1" }]
  }
};
 
//担保種類区分
const COLLATERAL_TYPE_CONFIG = {
  "01": {
    // 預金
    label: "預金",
    minors: [{ label: "その他", value: "9" }]
  },
  "02": {
    // 電債
    label: "電債",
    minors: [
      { label: "返済充当", value: "3" },
      { label: "預金入金", value: "4" }
    ]
  },
  "03": {
    // 一般保証
    label: "一般保証",
    minors: [
      { label: "個別保証", value: "5" },
      { label: "根保証", value: "6" }
    ]
  },
  "04": {
    // 協会保証
    label: "協会保証",
    minors: [
      { label: "個別保証", value: "5" },
      { label: "根保証", value: "6" }
    ]
  },
  "05": {
    // 動産・不動産
    label: "動産・不動産",
    minors: [
      { label: "抵当権", value: "1" },
      { label: "根抵当権", value: "2" },
      { label: "その他", value: "9" }
    ]
  },
  "06": {
    // 有価証券・債権
    label: "有価証券・債権",
    minors: [{ label: "その他", value: "9" }]
  },
  "09": {
    // その他担保
    label: "その他担保",
    minors: [{ label: "その他", value: "9" }]
  }
};
 
/**
* 大分類の選択肢
* MAJOR_CATEGORY_CONFIGから生成
*/
const MAJOR_OPTIONS = Object.entries(MAJOR_CATEGORY_CONFIG).map(
  ([value, config]) => ({
    label: config.label,
    value
  })
);
 
/**
* 履行期限・保証期間を入力可能とする保証種別
*/
const EXECUTION_ALLOWED_TYPES = {
  association: ["32", "34"],
  guarantee: [
    "03", // 特定極度根保証
    "04", // 特定根保証
    "05", // 包括根保証
    "06", // 包括根（極度付）
    "07" // 包括根（期限付）
  ]
};
 
// ========================================
// 定数: 担保種類（小分類）と保証人区分のマッピング
// ========================================
 
/**
* 担保種類（小分類）に応じた保証人区分のマッピング
* 各担保種類の値に対して、表示すべき保証人区分の値の配列を定義
*/
const COLLATERAL_TO_GUARANTOR_MAPPING = {
  30: ["11"], // 金融機関 → 金融機関
  31: ["21"], // 国・地公体 → 国・地方公共団体
  32: ["15", "18"], // 公益法人 → その他社団法人、その他財団法人
  33: ["20"], // 特殊法人 → その他特殊法人
  34: ["09"], // 一般法人・上場 → 法人（上場）
  35: ["10"], // 一般法人・非上場 → 法人（非上場）
  36: ["25"], // TKK → TKK
  37: ["17"], // VEC → VEC
  38: ["13"], // 全石協 → 全石協
  39: ["19"], // IPA → IPA
  40: ["14"], // ECFA → ECFA
  41: ["01", "02", "03", "04", "05", "06", "07", "08"], // 個人保証 → 代表取締役、取締役・理事・執行役、大株主、共同事業者、配偶者（事業性）、配偶者（非事業性）、第三者個人（事業性）、第三者個人（非事業性）
  42: ["22"], // 外国政府 → 外国政府
  43: ["24"], // 外国法人 → 外国法人
  44: ["23"], // 国際機関 → 国際機関
  73: ["18", "20", "21"], // 貿易金融保険 → その他財団法人、その他特殊法人、国・地方公共団体
  74: ["21", "22"], // 輸出入銀行 → 国・地方公共団体、外国政府
  80: ["16"], // 提携先保証 → DHC
  81: ["16", "21"], // 保証会社保証 → DHC、国・地方公共団体
  82: ["16", "21"], // 保証保険 → DHC、国・地方公共団体
  83: ["16"], // DC保証 → DHC
  84: ["16"], // ジャックス保証 → DHC
  85: ["16"], // DHC保証 → DHC
  86: ["16"] // MULB保証 → DHC
};
 
// ========================================
// 定数: 動的選択肢の連動ルール
// ========================================
 
/**
* 動的選択肢の連動ルール設定
* 小分類や大分類に応じて選択肢を切り替えるロジックを定義
*/
const DYNAMIC_OPTIONS_CONFIG = {
  // 保証種別の連動ルール
  guaranteeType: {
    // 保証の場合のみ連動（大分類："03"=一般保証）
    shouldApply: (column) => column.majorValue === "03",
    // 小分類の値に応じたパターンのマッピング
    getPattern: (column) => {
      const minorValue = column.minorValue;
      // ＴＫＫ（36）、全石協（38） → "02" tkkパターン（保証種別：11-14, 99）
      if (minorValue === "36" || minorValue === "38") {
        return "02";
      }
      // ＤＨＣ保証（85） → "03" dhcパターン（保証種別：21-22, 99）
      if (minorValue === "85") {
        return "03";
      }
      // その他の小分類 → "01" normalパターン（保証種別：01-07, 99）
      return "01";
    }
  }
};
 
// ========================================
// 定数: サンプルデータ
// ========================================
 
/**
* 担保条件２のサンプルデータ
*/
const SAMPLE_COLLATERAL_DETAIL_ROWS = [
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-06-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-09-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2026-03-31"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2025-12-31"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2026-02-28"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引都度",
    dueDate: "2025-08-31"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始後",
    dueDate: "2025-11-30"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引開始前/同時",
    dueDate: "2026-01-31"
  },
  {
    condition: SAMPLE_TEXT_140,
    timing: "取引都度",
    dueDate: "2026-04-30"
  }
];
 
// ========================================
// 定数: テンプレートデータ
// ========================================
 
const SAMPLE_COLUMNS = [
  {
    id: "col-import",
    subject: "01",
    majorValue: "01", // 預金
    minorValue: "01",
    dealType: "01", // 新規
    setupCategory: "1",
    collateralCategory: "9",
    amount: "999999999",
    share: "999999999",
    extinguish: "",
    rootLink: "01", // 極度
    timing: "取引開始前/同時",
    dueDate: "",
    remark: SAMPLE_TEXT_60
  },
  {
    id: "col-export",
    subject: "02",
    majorValue: "02", // 電債
    minorValue: "05",
    dealType: "02", // 既存
    setupCategory: "1",
    collateralCategory: "3",
    amount: "999999999",
    share: "999999999",
    extinguish: "",
    rootLink: "02", // 実残
    timing: "取引開始前/同時",
    dueDate: "",
    remark: SAMPLE_TEXT_60
  },
  {
    id: "col-guarantee",
    subject: "03",
    majorValue: "03", // 一般保証
    minorValue: "34",
    dealType: "01", // 新規
    setupCategory: "1",
    collateralCategory: "5",
    amount: "999999999",
    share: "999999999",
    extinguish: "",
    rootLink: "02", // 実残
    timing: "取引開始前/同時",
    dueDate: "",
    remark: SAMPLE_TEXT_60,
    guaranteeType: "05", // 包括根保証
    guarantorName: SAMPLE_TEXT_30_CHAR,
    guarantorCategory: "01", // 代表取締役
    corporateGuaranteeCategory: "01", // 規定・優良
    debtorRelationship: "01", // 代表取締役
    guaranteePeriod: "", // 期間
    guaranteePeriodYears: "",
    guaranteePeriodMonths: "",
    guaranteeDeadline: ""
  },
  {
    id: "col-association",
    subject: "04",
    majorValue: "04", // 協会保証
    minorValue: "45",
    dealType: "01", // 新規
    setupCategory: "1",
    collateralCategory: "6",
    amount: "999999999",
    share: "999999999",
    extinguish: "",
    rootLink: "02", // 実残
    timing: "取引開始前/同時",
    dueDate: "2026-05-31",
    remark: SAMPLE_TEXT_60,
    associationType: "32", // 貸付根保証
    associationGuaranteeNumber: "999999999999999999",
    associationExistingCondition: "01", // 有
    associationApprovalCondition: "01", // 条件なし
    associationGuaranteePeriod: "02", // 日付
    associationPeriodYears: "",
    associationPeriodMonths: "",
    associationDeadline: "2027-03-31"
  }
];

const COLUMN_TEMPLATES = {
  patternYushi: SAMPLE_COLUMNS,
  patternShiharaiYushutsuYunyuShijosei: SAMPLE_COLUMNS,
  patternAbcp: []
};
 
// ========================================
// ユーティリティ関数
// ========================================
 
/**
* 行データにIDと空白テンプレートを適用してビルドする
* @param {Array} rows - 元の行データ
* @param {string} prefix - ID のプレフィックス
* @param {Object} blankRow - 空白行のテンプレート
* @returns {Array} IDを付与された行データ
*/
const buildRows = (rows, prefix, blankRow) =>
  rows.map((row, index) => ({
    id: `${prefix}-${index + 1}`,
    ...blankRow,
    ...row
  }));
 
/**
* 大分類の値から小分類の選択肢を取得
* @param {string} majorValue - 大分類の値
* @returns {Object} 小分類の選択肢リストと担保設定区分、担保種類区分
*/
const getOptionsByMajorValue = (majorValue) => {
  const minorOptions = MAJOR_CATEGORY_CONFIG[majorValue]?.minors ?? [];
  const collateralSettingOptions =
    COLLATERAL_SETTING_CONFIG[majorValue]?.minors ?? [];
  const collateralTypeOptions =
    COLLATERAL_TYPE_CONFIG[majorValue]?.minors ?? [];
 
  return {
    minorOptions,
    collateralSettingOptions,
    collateralTypeOptions
  };
};
 
/**
* 小分類に応じた保証種別の選択肢を取得
* @param {string} majorValue - 大分類の値
* @param {string} minorValue - 小分類の値
* @returns {Array} 保証種別の選択肢リスト
*/
const getGuaranteeTypeOptions = (majorValue, minorValue) => {
  const config = DYNAMIC_OPTIONS_CONFIG.guaranteeType;
  const column = { majorValue, minorValue };
 
  if (config.shouldApply(column)) {
    const pattern = config.getPattern(column);
    return OPTIONS.guaranteeType[pattern];
  }
  return OPTIONS.guaranteeType["01"]; // デフォルトはnormalパターン
};
 
/**
* 小分類に応じた保証人区分の選択肢を取得
* @param {string} majorValue - 大分類の値
* @param {string} minorValue - 小分類の値
* @returns {Array} 保証人区分の選択肢リスト
*/
const getGuarantorCategoryOptions = (majorValue, minorValue) => {
  // 一般保証（"03"）の場合のみフィルタリング
  if (majorValue !== "03") {
    return OPTIONS.individualCorporate;
  }
 
  // 小分類に基づくマッピングを取得
  const allowedValues = COLLATERAL_TO_GUARANTOR_MAPPING[minorValue];
 
  // マッピングが存在しない場合は全選択肢を返す
  if (!allowedValues || allowedValues.length === 0) {
    return OPTIONS.individualCorporate;
  }
 
  // マッピングに基づいて選択肢をフィルタリング
  return OPTIONS.individualCorporate.filter((option) =>
    allowedValues.includes(option.value)
  );
};
 
/**
* 履行期限・保証期間項目の活性制御
* 協会保証/一般保証ごとの許可パターンをまとめる
*/
const canEditExecutionFields = (column) =>
  EXECUTION_ALLOWED_TYPES.association.includes(column.associationType) ||
  EXECUTION_ALLOWED_TYPES.guarantee.includes(column.guaranteeType);
 
/**
* 履行関連項目を許可状態に合わせて初期化
*/
const sanitizeExecutionFields = (column) => {
  if (canEditExecutionFields(column)) {
    return column;
  }
 
  return {
    ...column,
    dueDate: "",
    guaranteePeriod: "",
    guaranteePeriodYears: "",
    guaranteePeriodMonths: "",
    guaranteeDeadline: "",
    associationGuaranteePeriod: "",
    associationPeriodYears: "",
    associationPeriodMonths: "",
    associationDeadline: ""
  };
};
 
/**
* 保証期間・期日項目のフィールド名と値を取得
*/
const getExecutionFieldConfig = (column, isAssociation) => {
  if (isAssociation) {
    return {
      periodField: "associationGuaranteePeriod",
      periodValue: column.associationGuaranteePeriod,
      periodYearsField: "associationPeriodYears",
      periodYearsValue: column.associationPeriodYears,
      periodMonthsField: "associationPeriodMonths",
      periodMonthsValue: column.associationPeriodMonths,
      deadlineField: "associationDeadline",
      deadlineValue: column.associationDeadline
    };
  }
 
  return {
    periodField: "guaranteePeriod",
    periodValue: column.guaranteePeriod,
    periodYearsField: "guaranteePeriodYears",
    periodYearsValue: column.guaranteePeriodYears,
    periodMonthsField: "guaranteePeriodMonths",
    periodMonthsValue: column.guaranteePeriodMonths,
    deadlineField: "guaranteeDeadline",
    deadlineValue: column.guaranteeDeadline
  };
};
 
/**
* 列データに表示用のプロパティを追加
* @param {Object} column - 元の列データ
* @returns {Object} デコレートされた列データ
*/
const decorateColumn = (column) => {
  const normalizedColumn = sanitizeExecutionFields(column);
  const isGuarantee = normalizedColumn.majorValue === "03"; // 一般保証
  const isAssociation = normalizedColumn.majorValue === "04"; // 協会保証
  const isAsset = normalizedColumn.majorValue === "05"; // 動産・不動産
  const isGuaranteeOrAssociation = isGuarantee || isAssociation;
  const optionsForMajor = getOptionsByMajorValue(normalizedColumn.majorValue);
 
  // 保証種別の値を取得（一般保証 or 協会保証）
  const guaranteeTypeValue = isAssociation
    ? normalizedColumn.associationType
    : normalizedColumn.guaranteeType;
 
  // 履行期限と保証期間の入力を許容する協会保証・一般保証かを判定
  const canEditExecution = canEditExecutionFields(normalizedColumn);
  const executionFieldConfig = getExecutionFieldConfig(
    normalizedColumn,
    isAssociation
  );
 
  // 保証期間入力の制御フラグ
  const basePeriodDisabled = executionFieldConfig.periodValue === "02";
  const baseDateDisabled = executionFieldConfig.periodValue === "01";
 
  return {
    ...normalizedColumn,
    minorOptions: optionsForMajor.minorOptions,
    collateralSettingOptions: optionsForMajor.collateralSettingOptions,
    collateralTypeOptions: optionsForMajor.collateralTypeOptions,
    guaranteeTypeOptions: getGuaranteeTypeOptions(
      normalizedColumn.majorValue,
      normalizedColumn.minorValue
    ),
    // 保証人区分の動的選択肢を追加
    guarantorCategoryOptions: getGuarantorCategoryOptions(
      normalizedColumn.majorValue,
      normalizedColumn.minorValue
    ),
    isGuaranteeCategory: isGuarantee,
    isAssociationCategory: isAssociation,
    isGuaranteeOrAssociation,
    isCorporateGuarantor: normalizedColumn.guarantorCategory === "corporate",
    // 規定区分の入力制御（一般保証の個人保証以外の時のみ有効）
    isCorporateGuaranteeCategoryDisabled:
      !isGuarantee || normalizedColumn.minorValue === "41",
    // 保証種別の統一プロパティ
    guaranteeTypeValue: guaranteeTypeValue,
    guaranteeTypeOptionsForDisplay: isAssociation
      ? OPTIONS.guaranteeType["04"]
      : getGuaranteeTypeOptions(
          normalizedColumn.majorValue,
          normalizedColumn.minorValue
        ), // 協会保証は"04"パターン
    guaranteeTypeField: isAssociation ? "associationType" : "guaranteeType",
    guaranteeTypeHelp: isAssociation
      ? "協会保証のインフォメーション情報がここにでます"
      : undefined,
    // 評価方法の入力制御（動産・不動産のみ有効）
    isExtinguishDisabled: !isAsset,
    // 履行期限と保証期間入力の共通制御
    isDueDateDisabled: !canEditExecution,
    isExecutionScheduleDisabled: !canEditExecution,
    // 保証期間の統一プロパティ
    ...executionFieldConfig,
    // 保証期間の入力制御（協会保証の指定条件時のみ有効）
    isPeriodInputDisabled: !canEditExecution || basePeriodDisabled,
    isDateInputDisabled: !canEditExecution || baseDateDisabled
  };
};
 
// ========================================
// コンポーネント
// ========================================
 
/**
* 担保カテゴリボードコンポーネント
* 親画面タイプに応じて列データのテンプレートを切り替える
*/
export default class f003RgV9961TanpoBasicC1 extends LightningElement {
  // ========================================
  // プロパティ: 画面設定
  // ========================================
  _parentScreenType = "patternYushi";
  globalRemark = SAMPLE_TEXT_280;
 
  // ========================================
  // プロパティ: 選択肢オプション
  // ========================================
  subjectOptions = OPTIONS.subject;
  majorOptions = MAJOR_OPTIONS;
  dealTypeOptions = OPTIONS.dealType;
  setupCategoryOptions = OPTIONS.setupCategory;
  extinguishOptions = OPTIONS.extinguish;
  rootLinkOptions = OPTIONS.rootLink;
  guaranteeTypeOptions = OPTIONS.guaranteeType.normal;
  guarantorCategoryOptions = OPTIONS.individualCorporate;
  debtorRelationshipOptions = OPTIONS.individualCorporate;
  corporateGuaranteeCategoryOptions = OPTIONS.corporateGuaranteeCategory;
  guaranteePeriodOptions = OPTIONS.guaranteePeriod;
  associationTypeOptions = OPTIONS.associationType;
  associationExistingConditionOptions = OPTIONS.associationExistingCondition;
  associationApprovalConditionOptions = OPTIONS.associationApprovalCondition;
  timingOptions = OPTIONS.timing;
 
  // ========================================
  // プロパティ: データ
  // ========================================
  @track columns = COLUMN_TEMPLATES.patternYushi.map(decorateColumn);
  @track collateralDetailRows = buildRows(
    SAMPLE_COLLATERAL_DETAIL_ROWS,
    "collateral-detail",
    BLANK_COLLATERAL_DETAIL_ROW
  );
  nextCollateralDetailId = this.collateralDetailRows.length + 1;
 
  // ========================================
  // API プロパティ
  // ========================================
 
  /**
   * 親画面タイプを取得
   * @returns {string} 親画面タイプ
   */
  @api
  get parentScreenType() {
    return this._parentScreenType;
  }
 
  /**
   * 親画面タイプを設定し、対応するパターンを適用
   * @param {string} value - 親画面タイプ
   */
  set parentScreenType(value) {
    this._parentScreenType = value || "patternYushi";
    this.applyPattern(this._parentScreenType);
  }
 
  // ========================================
  // 算出プロパティ
  // ========================================
 
  /**
   * 科目列の表示フラグ
   * @returns {boolean} defaultの場合のみtrue
   */
  get showSubjectColumn() {
    return this.parentScreenType === "patternYushi";
  }
 
  /**
   * 担保条件セクション（担保条件１・２）の表示フラグ
   * @returns {boolean} patternAbcp以外の場合true
   */
  get showCollateralConditions() {
    return this.parentScreenType !== "patternAbcp";
  }

  /**
   * 備考欄のインフォメーションテキスト
   * @returns {string|undefined} ABCP時はundefined（非表示）
   */
  get remarksFieldLevelHelp() {
    return this.parentScreenType === "patternAbcp" ? undefined : "〇〇〇";
  }

  get remarksSize() {
    return this.parentScreenType === "patternAbcp" ? "10" : "5";
  }
 
  /**
   * アクティブなアコーディオンセクション
   * @returns {string[]} アクティブセクション名の配列
   */
  get activeSections() {
    return ["b"];
  }
 
  // ========================================
  // ヘルパーメソッド
  // ========================================
 
  /**
   * パターンに応じた列データテンプレートを適用
   * @param {string} screenType - 画面タイプ
   */
  applyPattern(screenType) {
    const templates = COLUMN_TEMPLATES[screenType] || COLUMN_TEMPLATES.patternYushi;
    const displayTemplates = screenType === "patternShiharaiYushutsuYunyuShijosei" ? templates.slice(0, 1) : templates;
    this.columns = displayTemplates.map(decorateColumn);
    // パターン3の場合は担保コメントのサンプルデータを390バイトに設定
    this.globalRemark = screenType === "patternAbcp" ? SAMPLE_TEXT_390 : SAMPLE_TEXT_280;
  }
 
  // ========================================
  // イベントハンドラー: 担保条件１
  // ========================================
 
  /**
   * 大分類変更ハンドラー
   * 大分類が変更されたら小分類を最初の選択肢に設定
   * @param {Event} event - 変更イベント
   */
  handleMajorChange(event) {
    const { columnId } = event.target.dataset;
    const nextValue = event.detail.value;
    const { minorOptions, collateralSettingOptions, collateralTypeOptions } =
      getOptionsByMajorValue(nextValue);
 
    this.columns = this.columns.map((column) =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            majorValue: nextValue,
            minorValue: minorOptions[0]?.value || "",
            collateralSettingValue: collateralSettingOptions[0]?.value || "",
            collateralTypeValue: collateralTypeOptions[0]?.value || ""
          })
        : column
    );
  }
 
  /**
   * フィールド変更ハンドラー
   * 各フィールドの値を更新
   * @param {Event} event - 変更イベント
   */
  handleFieldChange(event) {
    const { columnId, field } = event.target.dataset;
    const value = event.detail.value;
 
    this.columns = this.columns.map((column) =>
      column.id === columnId
        ? decorateColumn({
            ...column,
            [field]: value
          })
        : column
    );
  }
 
  /**
   * 数値入力ハンドラー
   * c-f003-gs-v0000-number からの変更を受けて列を更新
   * @param {CustomEvent} event - 数値変更イベント
   */
  handleNumberChange(event) {
    const { id, field, value } = event.detail;
 
    this.columns = this.columns.map((column) =>
      column.id === id
        ? decorateColumn({
            ...column,
            [field]: value
          })
        : column
    );
  }
 
  // ========================================
  // イベントハンドラー: 担保条件２
  // ========================================
 
  /**
   * 担保条件２の行変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleCollateralDetailRowChange(event) {
    const { id, field } = event.target.dataset;
    let value = event.target.value;
 
    if (typeof value === "undefined") {
      value = event.detail?.value;
    }
 
    this.collateralDetailRows = this.collateralDetailRows.map((row) =>
      row.id === id ? { ...row, [field]: value } : row
    );
  }
 
  /**
   * 担保条件２の行追加ハンドラー
   * 最大件数に達している場合は警告を表示
   */
  handleAddCollateralDetailRow() {
    if (this.collateralDetailRows.length >= MAX_COLLATERAL_DETAIL_ROWS) {
      this.dispatchEvent(
        new ShowToastEvent({
          title: "上限に達しました",
          message: `担保条件２は最大${MAX_COLLATERAL_DETAIL_ROWS}件まで追加できます`,
          variant: "warning"
        })
      );
      return;
    }
 
    const newRow = {
      id: `collateral-detail-${this.nextCollateralDetailId++}`,
      ...BLANK_COLLATERAL_DETAIL_ROW
    };
    this.collateralDetailRows = [...this.collateralDetailRows, newRow];
  }
 
  /**
   * 担保条件２の行削除ハンドラー
   * 削除前に確認ダイアログを表示
   * @param {Event} event - クリックイベント
   */
  async handleRemoveCollateralDetailRow(event) {
    const rowId = event.target.dataset.id;
    const confirmed = await LightningConfirm.open({
      label: "削除の確認",
      message: "選択した行を削除しますか？",
      theme: "warning"
    });
 
    if (!confirmed) {
      return;
    }
 
    this.collateralDetailRows = this.collateralDetailRows.filter(
      (row) => row.id !== rowId
    );
  }
 
  // ========================================
  // イベントハンドラー: 担保コメント
  // ========================================
 
  /**
   * 備考変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleRemarksChange(event) {
    this.globalRemark = event.detail.value;
  }
}