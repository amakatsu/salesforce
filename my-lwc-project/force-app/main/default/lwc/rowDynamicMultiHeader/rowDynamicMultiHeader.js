import { LightningElement, api, track } from "lwc";
import {
  generateMockData,
  REVIEW_RESULT_OPTIONS,
  SUBJECT_OPTIONS,
  PRIORITY_OPTIONS,
  STATUS_OPTIONS,
  SAVING_FIELD_LIST
} from "./rowDynamicMultiHeaderMockData";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { validateElement } from "c/f003GsV0000DataValidation";

/* ========================================
 * メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicMultiHeader extends LightningElement {
  /* ----------------------------------------
   * プロパティ定義
   * ---------------------------------------- */
  /* 選択された行のインデックス配列*/
  selectedRows = []; //
  /* テーブルデータ*/
  @track tableData = structuredClone(generateMockData());

  /* ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;
  priorityOptions = PRIORITY_OPTIONS;
  statusOptions = STATUS_OPTIONS;

  /**
   * カスタマイズテーブル・行選択処理
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowIndex = parseInt(event.target.dataset.idx, 10);
    const isAlreadySelected = this.selectedRows.includes(rowIndex);

    // 事前チェックで条件分岐を簡潔に
    if (checked) {
      if (!isAlreadySelected) {
        this.selectedRows.push(rowIndex);
      }
    } else {
      this.selectedRows = this.selectedRows.filter((idx) => idx !== rowIndex);
    }

    // tableData更新
    this.tableData = this.tableData.map((item, idx) =>
      idx === rowIndex ? { ...item, checked: checked } : item
    );
  }

  /**
   * カスタマイズテーブル・全選択・全選択解除処理
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked;

    // 選択行配列をリセット
    this.selectedRows = [];

    if (checked) {
      // 全データのインデックスを選択行配列に追加
      this.selectedRows = [...Array(this.tableData.length).keys()];
    }

    // 全データの checked フラグを更新
    this.tableData = this.tableData.map((item) => ({
      ...item,
      checked: checked
    }));
  }

  /**
   * 保存ボタン押下時の処理<br>
   *
   * @return { Array.<Object, Array.<Element>> } APIに渡す用のリストと、単項目チェック用のリストを返却する。
   */
  @api
  getSavingDatas() {
    let itemList = {};
    let validationResult = 0;

    // 画面上の固定要素からデータを取得
    const nonTableElements = this.template.querySelectorAll(
      "[data-id]:not(tr *)"
    );
    const [fixedData, validationElements] = getComponentDataList(
      nonTableElements,
      SAVING_FIELD_LIST
    );

    // バリデーション実行
    validateElement(validationElements);

    // 結果をまとめる
    itemList = { ...fixedData };
    itemList.tableData = this.tableData;

    return [itemList, validationResult];
  }

  /* ----------------------------------------
   * データ入力関連のメソッド（MultiHeader固有機能）
   * ---------------------------------------- */
  handleInputChange(event) {
    const { id, field } = event.target.dataset;
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;

    // 該当レコードのフィールドを更新
    this.tableData = this.tableData.map((record) => {
      if (record.Id === id) {
        return { ...record, [field]: value };
      }
      return record;
    });
  }

  /* ----------------------------------------
   * テスト・デバッグ用メソッド（実装時は削除してください
   * ---------------------------------------- */
  handleTestAllData() {
    const checkedCount = this.tableData.filter((data) => data.checked).length;
    const selectedCount = this.selectedRows.length;

    let message = `【全データ詳細構造】\n`;
    message += `総データ数: ${this.tableData.length}件\n`;
    message += `選択データ数: ${checkedCount}件\n`;
    message += `選択行配列: ${selectedCount}件\n`;
    message += `生成日時: ${new Date().toLocaleString()}\n\n`;

    // 全データの詳細表示
    this.tableData.forEach((data, i) => {
      const isSelected = this.selectedRows.includes(i) ? "★" : "　";
      message += `${isSelected}[${i + 1}] ID:${data.Id} ${data.label}\n`;

      // 上段データ（1行目）
      message += `  ■上段: 数値1=${data.num1} 数値2=${data.num2}\n`;
      message += `    文字列1="${data.str1}" 文字列2="${data.str2}" 文字列3="${data.str3}"\n`;
      message += `    チェック=${data.dataCheck} 審査結果="${data.ReviewResult}" 科目="${data.Subject}"\n`;
      message += `    日付1=${data.date1} 日付2=${data.date2}\n`;

      // 下段データ（2行目）
      message += `  ■下段: 数値3=${data.num3} 数値4=${data.num4}\n`;
      message += `    文字列4="${data.str4}" 文字列5="${data.str5}" 文字列6="${data.str6}"\n`;
      message += `    チェック2=${data.checked2} 優先度="${data.Priority}" ステータス="${data.Status}"\n`;
      message += `    日付3=${data.date3} 日付4=${data.date4}\n`;

      // 選択状態
      message += `  ◆選択状態: UI選択=${data.checked} データチェック=${data.dataCheck}\n\n`;
    });

    // コンソールにも出力（長いデータの場合）
    console.log("【全データ詳細】", {
      totalCount: this.tableData.length,
      checkedCount,
      selectedCount,
      selectedRows: this.selectedRows,
      tableData: this.tableData
    });

    alert(message);
  }

  handleTestSavingData() {
    try {
      const [itemList, validation] = this.getSavingDatas();

      let message = `【保存データ構造】\n`;
      message += `テーブルデータ数: ${itemList.tableData.length}件\n`;
      message += `バリデーション結果: ${validation}\n\n`;

      message += `サンプルデータ（最初の2件）:\n`;
      itemList.tableData.slice(0, 2).forEach((data, i) => {
        message += `[${i + 1}] ID:${data.Id} ${data.label}\n`;
        message += `  上段: 数値1=${data.num1} 文字列1=${data.str1}\n`;
        message += `  下段: 数値3=${data.num3} 詳細=${data.str4}\n`;
        message += `  選択=${data.checked} データチェック=${data.dataCheck}\n\n`;
      });

      alert(message);
    } catch (error) {
      alert(`【エラー】\n保存データ取得に失敗\nエラー: ${error.message}`);
    }
  }

  async handleSave() {
    try {
      // 実際に保存データを取得して処理（モック実装）
      const [itemList, validation] = this.getSavingDatas();

      // モック保存処理：実際のAPIコール処理をシミュレート
      const savingData = {
        tableData: itemList.tableData,
        timestamp: new Date().toISOString(),
        recordCount: itemList.tableData.length,
        validation: validation
      };

      // コンソールに保存データを出力（デバッグ用）
      console.log("【モック保存実行】保存データ:", savingData);

      // 短い遅延でAPI呼び出しをシミュレート
      await new Promise((resolve) => setTimeout(resolve, 500));

      this.dispatchEvent(
        new ShowToastEvent({
          title: "保存完了（モック）",
          message: `${itemList.tableData.length}件のデータを保存しました。コンソールで内容を確認できます。`,
          variant: "success"
        })
      );
    } catch (error) {
      console.error("【保存エラー】", error);
      this.dispatchEvent(
        new ShowToastEvent({
          title: "保存エラー",
          message: `保存に失敗しました: ${error.message}`,
          variant: "error"
        })
      );
    }
  }
}

/* ========================================
 * 補足説明・Sample1との詳細比較
 * ========================================
 *
 * 【Sample1から完全移植（変更なし）】
 * ✅ handleSelectFullCheck - ロジックが完璧だったため変更なし
 * ✅ updateRecord - ID一致判定とスプレッド構文、完璧だったため変更なし
 *
 * 【Sample1から移植・効率化修正】
 * 🔧 handleRowSelection - 重複チェック処理の効率化
 *    Sample1: havingFlg判定後の複雑な条件分岐
 *    MultiHeader: isAlreadySelectedで事前判定、シンプルな条件分岐
 *
 * 【Sample1から移植・モック実装に変更】
 * 🔄 checkSelectedRows - AlertError.open → showAlertMessage
 *    変更理由: MultiHeaderプロジェクトにAlertErrorがないため
 * 🔄 handleRecordEditClick - ModalView.open → showEditModal + トースト通知追加
 *    変更理由: MultiHeaderプロジェクトにModalViewがないため + UX向上
 *
 * 【Sample1から移植・変数名修正】
 * 🔧 getSavingDatas - dtoList → tableData, valid → validationResult
 *    変更理由: MultiHeaderの命名規則に統一
 *
 * 【Sample1から移植・参考実装でコメントアウト】
 * 💭 handleSelectPossibility - 機能は移植したが非推奨でコメントアウト
 *    理由: handleInputChangeがより汎用的で上位互換
 *
 * 【Sample1から移植・不要でコメントアウト】
 * ❌ renderedCallback + adjustHeaderPositions
 *    理由: MultiHeaderでは複数ヘッダーの位置調整が不要と判断
 *
 * 【MultiHeader固有の追加機能】
 * 🆕 handleInputChange - 汎用入力変更処理（Sample1のhandleSelectPossibilityの上位互換）
 * 🆕 showAlertMessage / showEditModal - Sample1の外部コンポーネントのモック実装
 * 🆕 handleTest* シリーズ - デバッグ・テスト機能群
 * 🆕 handleSave - 保存処理（モック実装）
 *
 * 【2行データ構造への対応】
 * - モックデータ生成を別ファイルに分離
 * - 上段/下段データの表示・編集対応
 * - ピックリストオプションの2行構造対応
 *
 * 【チェックボックスの分離設計】
 * - data.checked: 行選択用（UI制御のみ）
 * - data.dataCheck: データ項目（保存対象）
 * この分離により、行選択とデータ項目が独立して動作
 */
