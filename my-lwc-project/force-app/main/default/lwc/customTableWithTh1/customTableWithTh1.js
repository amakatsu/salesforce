import { LightningElement, track } from "lwc";

const REVIEW_RESULT_OPTIONS = [
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

const SUBJECT_OPTIONS = [
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

export const TABLE_DATA = {
  l1_label: "横ラベル1",
  l1_num1: 7777777,
  l1_num2: -7777777,
  l1_str1: "サンプル参照テキスト１",
  l1_str2: "サンプル入力テキスト１",
  l1_check: true,
  l1_reviewResult: "審査中",
  l1_subject: "貸付金",
  l2_label: "横ラベル2",
  l2_num1: 8888888,
  l2_num2: 88888888,
  l2_str1: "サンプル参照テキスト２",
  l2_str2: "サンプル入力テキスト２",
  l2_check: true,
  l2_reviewResult: "未審査",
  l2_subject: "手形",
  l3_label: "横ラベル3",
  l3_num1: 9999999,
  l3_num2: -999999999,
  l3_date1: "2023-09-15",
  l3_date2: "2023-10-15",
  l3_check: true,
  l3_reviewResult: "合格",
  l3_subject: "与信枠"
};

export default class F003DrV0000MeisaiMockC2 extends LightningElement {
  records = TABLE_DATA;
  @track record = { ...this.records };
  /**
   * レコードの変更処理（value値取得）<br>
   *
   * @param { ChangeEvent } event 項目内のデータを変更した際のイベント情報が格納されたオブジェクト
   */
  /**
   * レコードの変更処理（value値取得）<br>
   *
   * @param { ChangeEvent } event 項目内のデータを変更した際のイベント情報が格納されたオブジェクト
   */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;

  handleRecordValueChange(event) {
    this.record[event.target.dataset.id] = event.target.value;
    const inputElement = event.target;
    const childDataList = [inputElement];
    validateElement(childDataList);
  }

  handleRecordCheckedChange(event) {
    this.record[event.target.dataset.id] = event.target.checked;
  }

  handleComboboxChange(event) {
    const { id } = event.target.dataset;
    this.record[id] = event.target.value;
  }
}
