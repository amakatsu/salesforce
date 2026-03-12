import { LightningElement, api } from 'lwc';
import LightningConfirm from 'lightning/confirm';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
 
// ========================================
// 定数定義: ブランク行テンプレート
// ========================================
 
/**
* 明細行の空白テンプレート
*/
const BLANK_DETAIL_ROW = {
  condition: '',
  timing: '',
  dueDate: ''
};
 
/**
* トップ入力欄の空白テンプレート（条件補足を含む）
*/
const BLANK_TOP_ROW = {
  ...BLANK_DETAIL_ROW,
  conditionSupplement: ''
};
 
// ========================================
// 定数定義: サンプルテキスト
// ========================================
 
/** 32文字のサンプルテキスト */
const SAMPLE_TEXT_32 = '〇'.repeat(29);
 
/** 366文字のサンプルテキスト */
const SAMPLE_TEXT_366 = '〇'.repeat(366);
 
// ========================================
// 定数定義: サンプルデータ
// ========================================
 
/**
* トップ入力欄のサンプルデータ
*/
const SAMPLE_TOP_ROWS = [
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '融資実行前',
    dueDate: '2025-03-15'
  },
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '四半期末',
    dueDate: '2025-06-30'
  },
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '融資実行前',
    dueDate: '2025-04-10'
  },
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '半期末',
    dueDate: '2025-07-15'
  },
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '四半期末',
    dueDate: '2025-09-30'
  },
  {
    condition: '極度内運用○○○○○○○○○○',
    conditionSupplement: SAMPLE_TEXT_32,
    timing: '融資実行前',
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
    timing: '月末',
    dueDate: '2026-02-28'
  }
];
 
/**
* 明細入力欄のサンプルデータ
*/
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
    timing: '融資実行前',
    dueDate: '2025-12-15'
  }
];
 
// ========================================
// 定数定義: 画面オプション
// ========================================
 
/**
* 画面タイプ別のオプションセット
* 各画面タイプに応じた条件とタイミングの選択肢を定義
*/
const SCREEN_OPTION_SETS = {
  default: {
    condition: [
      { label: '極度内運用○○○○○○○○○○', value: '極度内運用○○○○○○○○○○' },
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
      { label: '極度内運用○○○○○○○○○○', value: '極度内運用○○○○○○○○○○' },
      { label: '在庫調達確認', value: '在庫調達確認' },
      { label: '信用保証更新', value: '信用保証更新' },
      { label: 'その他', value: 'その他' }
    ],
    timing: [
      { label: '輸入信用状開設', value: '輸入信用状開設' },
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
 
// ========================================
// 定数定義: 画面動作設定
// ========================================
 
/** サポートされている親画面タイプ */
const SUPPORTED_PARENT_SCREENS = ['patternImport', 'patternExport', 'patternAbcp'];
 
/** デフォルトのセクション表示設定 */
const DEFAULT_SECTIONS = {
  topInput: true,
  detailInput: true,
  remarks: true,
  inquiry: true
};
 
/**
* 画面タイプ別の動作設定
* デフォルト値からの差分のみを定義
*/
const SCREEN_BEHAVIOR_BY_PARENT = {
  default: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 6
  },
  patternImport: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 6
  },
  patternExport: {
    sections: DEFAULT_SECTIONS,
    topInputLimit: 12
  },
  patternAbcp: {
    sections: {
      ...DEFAULT_SECTIONS,
      topInput: false,
      inquiry: false
    },
    topInputLimit: 0
  }
};
 
/** 明細行の最大追加可能件数 */
const MAX_DETAIL_ROWS = 6;
 
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
 
// ========================================
// コンポーネントクラス
// ========================================
 
/**
* 本件条件コンポーネント
* 親画面タイプに応じて条件入力欄の表示内容を切り替える
*/
export default class f003RgV9951HonkenJokenBasicC1 extends LightningElement {
  topRows = buildRows(SAMPLE_TOP_ROWS, 'top', BLANK_TOP_ROW);
  conditionRows = buildRows(SAMPLE_DETAIL_ROWS, 'detail', BLANK_DETAIL_ROW);
 
  @api parentScreenType;
  nextDetailId = this.conditionRows.length + 1;
  relatedInquiryNumber = SAMPLE_TEXT_32;
  remarks = SAMPLE_TEXT_366;
  activeTopSections = ['section1'];
  activeDetailSections = ['section2'];
 
  // ========================================
  // イベントハンドラー
  // ========================================
 
  /**
   * 行変更ハンドラー（トップ入力欄用）
   * @param {Event} event - 変更イベント
   */
  handleTopRowChange(event) {
    this.topRows = this.updateRows(this.topRows, event);
  }
 
  /**
   * 行変更ハンドラー（明細入力欄用）
   * @param {Event} event - 変更イベント
   */
  handleRowChange(event) {
    this.conditionRows = this.updateRows(this.conditionRows, event);
  }
 
  /**
   * 明細行追加ハンドラー
   * 最大件数に達している場合は警告を表示
   */
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
 
  /**
   * 明細行削除ハンドラー
   * 削除前に確認ダイアログを表示
   * @param {Event} event - クリックイベント
   */
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
 
  /**
   * 関連照会番号変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleRelatedInquiryNumberChange(event) {
    this.relatedInquiryNumber = event.target.value;
  }
 
  /**
   * 備考変更ハンドラー
   * @param {Event} event - 変更イベント
   */
  handleRemarksChange(event) {
    this.remarks = event.target.value;
  }
 
  /**
   * 関連照会ボタンクリックハンドラー
   * TODO: 実装接続時に差し替え予定のスタブ
   */
  handleRelatedInquiry() {
    // eslint-disable-next-line no-console
    console.log('関連厘差照会番号', this.relatedInquiryNumber);
  }
 
  /**
   * トップアコーディオン開閉ハンドラー
   * @param {Event} event - トグルイベント
   */
  handleTopAccordionToggle(event) {
    this.activeTopSections = event.detail.openSections;
  }
 
  /**
   * 明細アコーディオン開閉ハンドラー
   * @param {Event} event - トグルイベント
   */
  handleDetailAccordionToggle(event) {
    this.activeDetailSections = event.detail.openSections;
  }
 
  // ========================================
  // ヘルパーメソッド
  // ========================================
 
  /**
   * 行データを更新する
   * @param {Array} rows - 更新対象の行データ
   * @param {Event} event - 変更イベント
   * @returns {Array} 更新された行データ
   */
  updateRows(rows, event) {
    const { id, field } = event.target.dataset;
    const { value } = event.target;
    return rows.map(row => (row.id === id ? { ...row, [field]: value } : row));
  }
 
  // ========================================
  // ゲッタープロパティ
  // ========================================
 
  /**
   * 現在の画面タイプに応じた動作設定を取得
   * @returns {Object} 画面動作設定オブジェクト
   */
  get screenBehavior() {
    return (
      SCREEN_BEHAVIOR_BY_PARENT[this.parentScreenType] ||
      SCREEN_BEHAVIOR_BY_PARENT.default
    );
  }
 
  /**
   * 条件の選択肢を取得
   * @returns {Array} 条件オプションリスト
   */
  get conditionOptions() {
    return (SCREEN_OPTION_SETS[this.parentScreenType] || SCREEN_OPTION_SETS.default).condition;
  }
 
  /**
   * タイミングの選択肢を取得
   * @returns {Array} タイミングオプションリスト
   */
  get timingOptions() {
    return (SCREEN_OPTION_SETS[this.parentScreenType] || SCREEN_OPTION_SETS.default).timing;
  }
 
  /**
   * トップ入力欄セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showTopInputSection() {
    return this.screenBehavior.sections.topInput;
  }
 
  /**
   * 明細入力欄セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showDetailInputSection() {
    return this.screenBehavior.sections.detailInput;
  }
 
  /**
   * 備考セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showRemarksSection() {
    return this.screenBehavior.sections.remarks;
  }
 
  /**
   * 関連照会セクションの表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get showInquirySection() {
    return this.screenBehavior.sections.inquiry;
  }
 
  /**
   * トップ入力欄の上限件数を取得
   * @returns {number} 上限件数
   */
  get topInputLimit() {
    return this.screenBehavior.topInputLimit;
  }
 
  /**
   * 表示用のトップ行データ（上限件数まで）を取得
   * @returns {Array} 表示用行データ
   */
  get topRowsForDisplay() {
    return this.topRows.slice(0, this.topInputLimit);
  }
 
  /**
   * トップ行が上限件数を超過しているかチェック
   * @returns {boolean} 超過している場合true
   */
  get isTopRowLimitExceeded() {
    return this.topRows.length > this.topInputLimit;
  }
 
  /**
   * コンポーネント全体の表示フラグ
   * @returns {boolean} 表示する場合true
   */
  get isVisible() {
    return (
      !this.parentScreenType ||
      SUPPORTED_PARENT_SCREENS.includes(this.parentScreenType)
    );
  }
}