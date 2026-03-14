import { LightningElement } from "lwc";
import { generateData } from "c/f003RgV0000CommonJs";

// ========================================
// 定数・サンプルデータ
// ========================================

const SAMPLE_CONDITIONS = [
  { id: 1, transactionCondition: generateData("half", 29), selectedCondition: "" },
  { id: 2, transactionCondition: generateData("half", 29), selectedCondition: "" },
  { id: 3, transactionCondition: generateData("half", 29), selectedCondition: "" },
  { id: 4, transactionCondition: "", selectedCondition: "" },
  { id: 5, transactionCondition: "", selectedCondition: "" }
];

const CONDITION_OPTIONS = [
  { label: "荷受入に当行以外を指定", value: "option1" },
  { label: "荷受入に当行以外を指定", value: "option2" },
  { label: "荷受入に当行以外を指定", value: "option3" },
  { label: "荷受入に当行以外を指定", value: "option4" },
  { label: "荷受入に当行以外を指定", value: "option5" }
];

// ========================================
// コンポーネントクラス
// ========================================

export default class f003RgV9952HonkenJokenNgaiLinkC1 extends LightningElement {
  activeSections = ["b"];
  conditions = SAMPLE_CONDITIONS.map((c) => ({ ...c }));
  honkenJokenComment = generateData("half", 366);
  conditionOptions = CONDITION_OPTIONS;

  handleConditionChange(event) {
    const conditionId = parseInt(event.target.dataset.id, 10);
    const field = event.target.dataset.field;
    const value = event.target.value;
    this.conditions = this.conditions.map((condition) =>
      condition.id === conditionId
        ? { ...condition, [field]: value }
        : condition
    );
  }

  handleCommentChange(event) {
    this.honkenJokenComment = event.target.value;
  }
}
