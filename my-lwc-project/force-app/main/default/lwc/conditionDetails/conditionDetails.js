import { LightningElement, track } from 'lwc';

export default class ConditionDetails extends LightningElement {
  // 上部入力欄データ
  @track topRows = [
    {
      id: '1',
      condition: '条件1',
      timing: '契約締結時',
      dueDate: '2025-03-31'
    },
    {
      id: '2',
      condition: '条件2',
      timing: '融資実行前',
      dueDate: '2025-04-15'
    }
  ];

  // 条件行データ
  @track conditionRows = [
    {
      id: '1',
      condition: '決算書提出',
      conditionSupplement: '直近3期分',
      timing: '年度末',
      dueDate: '2025-05-31'
    },
    {
      id: '2',
      condition: '試算表提出',
      conditionSupplement: '四半期ごと',
      timing: '各四半期末',
      dueDate: '2025-06-30'
    },
    {
      id: '3',
      condition: '資金使途報告',
      conditionSupplement: '設備投資計画',
      timing: '融資実行後',
      dueDate: '2025-07-15'
    },
    {
      id: '4',
      condition: '担保物件保険',
      conditionSupplement: '火災保険加入',
      timing: '契約時',
      dueDate: '2025-03-31'
    },
    {
      id: '5',
      condition: '事業計画書提出',
      conditionSupplement: '向こう3年分',
      timing: '年度初め',
      dueDate: '2025-04-30'
    },
    {
      id: '6',
      condition: '財務制限条項',
      conditionSupplement: '自己資本比率維持',
      timing: '継続',
      dueDate: ''
    }
  ];

  nextTopId = 3;
  nextId = 7;

  // 本件条件のコンボボックスオプション
  conditionOptions = [
    { label: '条件1', value: '条件1' },
    { label: '条件2', value: '条件2' },
    { label: '条件3', value: '条件3' },
    { label: '条件4', value: '条件4' },
    { label: '条件5', value: '条件5' }
  ];

  relatedInquiryNumber = '';

  // 上部行追加
  handleAddTopRow() {
    const newRow = {
      id: String(this.nextTopId++),
      condition: '',
      timing: '',
      dueDate: ''
    };
    this.topRows = [...this.topRows, newRow];
  }

  // 上部行削除
  handleRemoveTopRow(event) {
    const rowId = event.target.dataset.id;
    this.topRows = this.topRows.filter(row => row.id !== rowId);
  }

  // 上部行データ変更
  handleTopRowChange(event) {
    const rowId = event.target.dataset.id;
    const field = event.target.dataset.field;
    const value = event.target.value;

    this.topRows = this.topRows.map(row => {
      if (row.id === rowId) {
        return { ...row, [field]: value };
      }
      return row;
    });
  }

  // 行追加
  handleAddRow() {
    const newRow = {
      id: String(this.nextId++),
      condition: '',
      conditionSupplement: '',
      timing: '',
      dueDate: ''
    };
    this.conditionRows = [...this.conditionRows, newRow];
  }

  // 行削除
  handleRemoveRow(event) {
    const rowId = event.target.dataset.id;
    this.conditionRows = this.conditionRows.filter(row => row.id !== rowId);
  }

  // 行データ変更
  handleRowChange(event) {
    const rowId = event.target.dataset.id;
    const field = event.target.dataset.field;
    const value = event.target.value;

    this.conditionRows = this.conditionRows.map(row => {
      if (row.id === rowId) {
        return { ...row, [field]: value };
      }
      return row;
    });
  }

  handleRelatedInquiryNumberChange(event) {
    this.relatedInquiryNumber = event.target.value;
  }

  handleRelatedInquiry() {
    // 実際の照会処理が接続された際に差し替える
    // eslint-disable-next-line no-console
    console.log('関連厘差照会番号', this.relatedInquiryNumber);
  }
}
