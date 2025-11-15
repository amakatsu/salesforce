import { LightningElement } from 'lwc';

const BLANK_DETAIL_ROW = {
  condition: '',
  timing: '',
  dueDate: ''
};

const BLANK_TOP_ROW = {
  ...BLANK_DETAIL_ROW,
  conditionSupplement: ''
};

const SAMPLE_TEXT_32 = '〇'.repeat(32);
const SAMPLE_TEXT_366 = '〇'.repeat(366);

const SAMPLE_TOP_ROWS = [
  {
    condition: '与信審査報告受領',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '融資実行前',
    dueDate: '2025-03-15'
  },
  {
    condition: '信用限度管理表提出',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '四半期末',
    dueDate: '2025-06-30'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '融資実行前',
    dueDate: '2025-04-10'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '半期末',
    dueDate: '2025-07-15'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '四半期末',
    dueDate: '2025-09-30'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: 'その他',
    dueDate: '2025-12-15'
  }
];

const SAMPLE_DETAIL_ROWS = [
  {
    condition: SAMPLE_TEXT_32,
    timing: '半期末',
    dueDate: '2025-07-31'
  },
  {
    condition: SAMPLE_TEXT_32,
    timing: '契約更新時',
    dueDate: '2025-08-15'
  },
  {
    condition: '信用供与枠確認',
    timing: '融資実行前',
    dueDate: '2025-04-10'
  },
  {
    condition: '信用状況ヒアリング',
    timing: '四半期末',
    dueDate: '2025-06-30'
  },
  {
    condition: '信用保証料支払明細',
    timing: '半期末',
    dueDate: '2025-09-30'
  },
  {
    condition: '信用情報照会結果提出',
    timing: 'その他',
    dueDate: '2025-12-15'
  }
];

const CONDITION_OPTIONS = [
  { label: '与信審査報告受領', value: '与信審査報告受領' },
  { label: '信用限度管理表提出', value: '信用限度管理表提出' },
  { label: '信用リスク見直し', value: '信用リスク見直し' },
  { label: '信用保証更新', value: '信用保証更新' },
  { label: 'その他', value: 'その他' }
];

const TIMING_OPTIONS = [
  { label: '融資実行前', value: '融資実行前' },
  { label: '四半期末', value: '四半期末' },
  { label: '半期末', value: '半期末' },
  { label: '契約更新時', value: '契約更新時' },
  { label: 'その他', value: 'その他' }
];

const buildRows = (rows, prefix, blankRow) =>
  rows.map((row, index) => ({
    id: `${prefix}-${index + 1}`,
    ...blankRow,
    ...row
  }));

export default class ConditionDetails extends LightningElement {
  topRows = buildRows(SAMPLE_TOP_ROWS, 'top', BLANK_TOP_ROW);
  conditionRows = buildRows(SAMPLE_DETAIL_ROWS, 'detail', BLANK_DETAIL_ROW);

  nextDetailId = this.conditionRows.length + 1;
  conditionOptions = CONDITION_OPTIONS;
  timingOptions = TIMING_OPTIONS;
  relatedInquiryNumber = SAMPLE_TEXT_32;
  remarks = SAMPLE_TEXT_366;

  handleTopRowChange(event) {
    this.topRows = this.updateRows(this.topRows, event);
  }

  handleAddRow() {
    const newRow = {
      id: `detail-${this.nextDetailId++}`,
      ...BLANK_DETAIL_ROW
    };
    this.conditionRows = [...this.conditionRows, newRow];
  }

  handleRemoveRow(event) {
    const rowId = event.target.dataset.id;
    this.conditionRows = this.conditionRows.filter(row => row.id !== rowId);
  }

  handleRowChange(event) {
    this.conditionRows = this.updateRows(this.conditionRows, event);
  }

  handleRelatedInquiryNumberChange(event) {
    this.relatedInquiryNumber = event.target.value;
  }

  handleRelatedInquiry() {
    // 実装接続時に差し替え予定のスタブ
    // eslint-disable-next-line no-console
    console.log('関連厘差照会番号', this.relatedInquiryNumber);
  }

  updateRows(rows, event) {
    const { id, field } = event.target.dataset;
    const { value } = event.target;
    return rows.map(row => (row.id === id ? { ...row, [field]: value } : row));
  }
}
