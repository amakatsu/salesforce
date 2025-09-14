/* ========================================
 * rowDynamicMultiHeader専用モックデータ生成
 * ========================================
 /* ========================================
 * ピックリスト選択肢定義
 * ======================================== */

export const REVIEW_RESULT_OPTIONS = [
  { label: "合格", value: "合格" },
  { label: "否認", value: "否認" },
  { label: "保留", value: "保留" },
  { label: "再審査", value: "再審査" },
  { label: "一時承認", value: "一時承認" },
  { label: "条件付き合格", value: "条件付き合格" },
  { label: "一部否認", value: "一部否認" },
  { label: "キャンセル", value: "キャンセル" },
  { label: "取下げ", value: "取下げ" },
  { label: "差戻し", value: "差戻し" },
  { label: "審査中", value: "審査中" },
  { label: "未審査", value: "未審査" }
];

export const SUBJECT_OPTIONS = [
  { label: "貸付金", value: "貸付金" },
  { label: "手形", value: "手形" },
  { label: "与信枠", value: "与信枠" },
  { label: "割引", value: "割引" },
  { label: "支払保証", value: "支払保証" },
  { label: "リース", value: "リース" },
  { label: "デリバティブ", value: "デリバティブ" },
  { label: "コミットメントライン", value: "コミットメントライン" },
  { label: "スタンドバイ・クレジット", value: "スタンドバイ・クレジット" },
  { label: "その他金融商品", value: "その他金融商品" }
];

export const PRIORITY_OPTIONS = [
  { label: "高", value: "高" },
  { label: "中", value: "中" },
  { label: "低", value: "低" }
];

export const STATUS_OPTIONS = [
  { label: "処理中", value: "処理中" },
  { label: "完了", value: "完了" },
  { label: "保留", value: "保留" }
];

/* ========================================
 * 保存対象フィールド定義
 * ======================================== */

export const SAVING_FIELD_LIST = [
  // 基本情報
  "Id",
  "label",

  // 1行目データ（上段）
  "num1",
  "num2",
  "str1",
  "str2",
  "str3",
  "dataCheck",
  "ReviewResult",
  "Subject",
  "date1",
  "date2",

  // 2行目データ（下段）
  "num3",
  "num4",
  "str4",
  "str5",
  "str6",
  "checked2",
  "Priority",
  "Status",
  "date3",
  "date4"
];

/* ========================================
 * モックデータ生成関数
 * ======================================== */

/**
 * 2行構造テーブル用モックデータを生成
 * @param {number} count 生成するデータ件数（デフォルト: 3件）
 * @return {Array} モックデータ配列
 */
export function generateMockData(count = 3) {
  return Array.from({ length: count }, (_, i) => ({
    // 基本情報
    Id: `${i + 1}`.padStart(3, "0"),
    label: `横ラベル${i + 1}`,
    checked: false, // 行選択用（UI表示のみ）

    // 1行目データ（上段）
    num1: 1000000 + i * 100000,
    num2: -2000000 - i * 200000,
    str1: `入力文字列1-${i + 1}`,
    str2: `表示文字列2-${i + 1}`,
    str3: `入力文字列3-${i + 1}`,
    dataCheck: i % 3 === 0, // データ用チェックボックス
    ReviewResult: REVIEW_RESULT_OPTIONS[i % REVIEW_RESULT_OPTIONS.length].value,
    Subject: SUBJECT_OPTIONS[i % SUBJECT_OPTIONS.length].value,
    date1: new Date(2024, 0, 15 + i).toISOString().split("T")[0],
    date2: new Date(2024, 1, 15 + i).toISOString().split("T")[0],

    // 2行目データ（下段）
    num3: 3000000 + i * 300000,
    num4: -4000000 - i * 400000,
    str4: `詳細情報${i + 1}`,
    str5: `備考・メモ欄\n複数行テキスト${i + 1}`,
    str6: `追加情報${i + 1}`,
    checked2: i % 4 === 0,
    Priority: PRIORITY_OPTIONS[i % PRIORITY_OPTIONS.length].value,
    Status: STATUS_OPTIONS[i % STATUS_OPTIONS.length].value,
    date3: new Date(2024, 2, 1 + i).toISOString().split("T")[0],
    date4: new Date(2024, 3, 1 + i).toISOString().split("T")[0]
  }));
}
