import { LightningElement, api } from 'lwc';
import LightningConfirm from 'lightning/confirm';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

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
  },
  {
    condition: '信用審査資料更新',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '年次決算後',
    dueDate: '2026-03-31'
  },
  {
    condition: '保証契約見直し',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '契約更新時',
    dueDate: '2025-10-01'
  },
  {
    condition: 'モニタリング報告書',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '四半期末',
    dueDate: '2025-12-31'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '半期末',
    dueDate: '2026-01-31'
  },
  {
    condition: '資金繰り予定提出',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '月末',
    dueDate: '2025-11-30'
  },
  {
    condition: SAMPLE_TEXT_32,
    conditionSupplement: SAMPLE_TEXT_32,
    timing: 'その他',
    dueDate: '2026-02-28'
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

const SCREEN_OPTION_SETS = {
  default: {
    condition: [
      { label: '与信審査報告受領', value: '与信審査報告受領' },
      { label: '信用限度管理表提出', value: '信用限度管理表提出' },
      { label: '信用リスク見直し', value: '信用リスク見直し' },
      { label: '信用保証更新', value: '信用保証更新' },
      { label: 'その他', value: 'その他' }
    ],
    timing: [
      { label: '融資実行前', value: '融資実行前' },
      { label: '四半期末', value: '四半期末' },
      { label: '半期末', value: '半期末' },
      { label: '契約更新時', value: '契約更新時' },
      { label: 'その他', value: 'その他' }
    ]
  },
  patternImport: {
    condition: [
      { label: '輸入信用状開設', value: '輸入信用状開設' },
      { label: '与信審査報告受領', value: '与信審査報告受領' },
      { label: '在庫調達確認', value: '在庫調達確認' },
      { label: '信用保証更新', value: '信用保証更新' },
      { label: 'その他', value: 'その他' }
    ],
    timing: [
      { label: '輸入契約締結時', value: '輸入契約締結時' },
      { label: '船積前', value: '船積前' },
      { label: '通関後', value: '通関後' },
      { label: '決済前', value: '決済前' },
      { label: 'その他', value: 'その他' }
    ]
  },
  patternExport: {
    condition: [
      { label: '輸出信用状確認', value: '輸出信用状確認' },
      { label: '船積書類受領', value: '船積書類受領' },
      { label: '輸出保険付保', value: '輸出保険付保' },
      { label: '為替予約締結', value: '為替予約締結' },
      { label: 'その他', value: 'その他' }
    ],
    timing: [
      { label: '船積前', value: '船積前' },
      { label: '船積後', value: '船積後' },
      { label: '支払期限前', value: '支払期限前' },
      { label: '為替決済時', value: '為替決済時' },
      { label: 'その他', value: 'その他' }
    ]
  },
  patternAbcp: {
    condition: [
      { label: 'SPC情報更新', value: 'SPC情報更新' },
      { label: '資産プール点検', value: '資産プール点検' },
      { label: '信用補完確認', value: '信用補完確認' },
      { label: '流動化契約遵守確認', value: '流動化契約遵守確認' },
      { label: 'その他', value: 'その他' }
    ],
    timing: [
      { label: '月次期日', value: '月次期日' },
      { label: '四半期期末', value: '四半期期末' },
      { label: '年次期末', value: '年次期末' },
      { label: '償還期限前', value: "償還期限前" },
      { label: 'その他', value: 'その他' }
    ]
  }
};

const SUPPORTED_PARENT_SCREENS = ['patternImport', 'patternExport', 'patternAbcp'];
const SCREEN_BEHAVIOR_BY_PARENT = {
  default: {
    sections: {
      topInput: true,
      detailInput: true,
      remarks: true,
      inquiry: true
    },
    topInputLimit: 6
  },
  patternImport: {
    sections: {
      topInput: true,
      detailInput: true,
      remarks: true,
      inquiry: true
    },
    topInputLimit: 6
  },
  patternExport: {
    sections: {
      topInput: true,
      detailInput: true,
      remarks: true,
      inquiry: true
    },
    topInputLimit: 12
  },
  patternAbcp: {
    sections: {
      topInput: false,
      detailInput: true,
      remarks: true,
      inquiry: false
    },
    topInputLimit: 0
  }
};
const MAX_DETAIL_ROWS = 6;

const buildRows = (rows, prefix, blankRow) =>
  rows.map((row, index) => ({
    id: `${prefix}-${index + 1}`,
    ...blankRow,
    ...row
  }));

export default class ConditionDetails extends LightningElement {
  topRows = buildRows(SAMPLE_TOP_ROWS, 'top', BLANK_TOP_ROW);
  conditionRows = buildRows(SAMPLE_DETAIL_ROWS, 'detail', BLANK_DETAIL_ROW);

  @api parentScreenType;
  nextDetailId = this.conditionRows.length + 1;
  relatedInquiryNumber = SAMPLE_TEXT_32;
  remarks = SAMPLE_TEXT_366;
  activeTopSections = ['section1'];
  activeDetailSections = ['section2'];

  handleTopRowChange(event) {
    this.topRows = this.updateRows(this.topRows, event);
  }

  handleAddRow() {
    if (this.conditionRows.length >= MAX_DETAIL_ROWS) {
      this.dispatchEvent(
        new ShowToastEvent({
          title: '上限に達しました',
          message: `明細は最大${MAX_DETAIL_ROWS}件まで追加できます`,
          variant: 'warning'
        })
      );
      return;
    }

    const newRow = {
      id: `detail-${this.nextDetailId++}`,
      ...BLANK_DETAIL_ROW
    };
    this.conditionRows = [...this.conditionRows, newRow];
  }

  async handleRemoveRow(event) {
    const rowId = event.target.dataset.id;
    const confirmed = await LightningConfirm.open({
      label: '削除の確認',
      message: '選択した行を削除しますか？',
      theme: 'warning'
    });

    if (!confirmed) {
      return;
    }

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

  handleTopAccordionToggle(event) {
    this.activeTopSections = event.detail.openSections;
  }

  handleDetailAccordionToggle(event) {
    this.activeDetailSections = event.detail.openSections;
  }

  updateRows(rows, event) {
    const { id, field } = event.target.dataset;
    const { value } = event.target;
    return rows.map(row => (row.id === id ? { ...row, [field]: value } : row));
  }

  get screenBehavior() {
    return (
      SCREEN_BEHAVIOR_BY_PARENT[this.parentScreenType] ||
      SCREEN_BEHAVIOR_BY_PARENT.default
    );
  }

  get optionSet() {
    return (
      SCREEN_OPTION_SETS[this.parentScreenType] ||
      SCREEN_OPTION_SETS.default
    );
  }

  get conditionOptions() {
    return this.optionSet.condition;
  }

  get timingOptions() {
    return this.optionSet.timing;
  }

  get sectionVisibility() {
    return this.screenBehavior.sections;
  }

  get showTopInputSection() {
    return this.sectionVisibility.topInput;
  }

  get showDetailInputSection() {
    return this.sectionVisibility.detailInput;
  }

  get showRemarksSection() {
    return this.sectionVisibility.remarks;
  }

  get showInquirySection() {
    return this.sectionVisibility.inquiry;
  }

  get topInputLimit() {
    return this.screenBehavior.topInputLimit;
  }

  get topRowsForDisplay() {
    return this.topRows.slice(0, this.topInputLimit);
  }

  get isTopRowLimitExceeded() {
    return this.topRows.length > this.topInputLimit;
  }

  get isVisible() {
    return (
      !this.parentScreenType ||
      SUPPORTED_PARENT_SCREENS.includes(this.parentScreenType)
    );
  }

}
