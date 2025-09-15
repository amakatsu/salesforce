import { LightningElement, api, track } from "lwc";
import {
  generateMockData,
  REVIEW_RESULT_OPTIONS,
  SUBJECT_OPTIONS,
  SAVING_BTN_LIST
} from "./rowDynamicOPCMockData";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { validateElement } from "c/f003GsV0000DataValidation";

/* ========================================
 * メインコンポーネントクラス
 * ======================================== */

export default class RowDynamicOPC extends LightningElement {
  /* ----------------------------------------
   * プロパティ定義
   * ---------------------------------------- */
  /* 選択された行のインデックス配列 */
  selectedRows = [];
  /* テーブルデータ */
  @track tableData = structuredClone(generateMockData(50));

  /* ピックリストオプション */
  reviewResultOptions = REVIEW_RESULT_OPTIONS;
  subjectOptions = SUBJECT_OPTIONS;

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
   * データ入力関連のメソッド（直接編集機能）
   * ---------------------------------------- */

  /**
   * テーブル内の入力項目変更処理（MultiHeaderから移植）
   */
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
   * テスト・デバッグ用メソッド（実装時は削除してください）
   * ---------------------------------------- */

  handleTestAllData() {
    const selectedData = this.tableData.filter((_, idx) =>
      this.selectedRows.includes(idx)
    );
    const selectedCount = this.selectedRows.length;

    let message = `【選択データ詳細構造】\n`;
    message += `総データ数: ${this.tableData.length}件\n`;
    message += `選択データ数: ${selectedCount}件\n`;
    message += `生成日時: ${new Date().toLocaleString()}\n\n`;

    if (selectedData.length === 0) {
      message += `データが選択されていません。\n`;
    } else {
      // 選択されたデータの詳細表示
      selectedData.forEach((data, i) => {
        message += `★[${i + 1}] ID:${data.Id} ${data.label}\n`;
        message += `  数値1=${data.num1} 数値2=${data.num2}\n`;
        message += `  文字列1="${data.str1}" 文字列2="${data.str2}"\n`;
        message += `  審査結果="${data.ReviewResult}" 科目="${data.Subject}"\n`;
        message += `  選択状態: UI選択=${data.checked} データチェック=${data.dataCheck}\n`;
        message += `  日付1=${data.date1} 日付2=${data.date2}\n\n`;
      });
    }

    alert(message);
  }

  /**
   * 全選択機能のテスト
   */
  handleTestSelectAll() {
    const event = { target: { checked: true } };
    this.handleSelectFullCheck(event);

    const message = `【全選択テスト完了】\n全データ数: ${
      this.tableData.length
    }件\n選択状態: 全て選択されました\n選択行配列: [${this.selectedRows.join(
      ", "
    )}]`;
    alert(message);
  }

  /**
   * 全解除機能のテスト
   */
  handleTestDeselectAll() {
    const event = { target: { checked: false } };
    this.handleSelectFullCheck(event);

    const message = `【全解除テスト完了】\n全データ数: ${
      this.tableData.length
    }件\n選択状態: 全て解除されました\n選択行配列: [${this.selectedRows.join(
      ", "
    )}]`;
    alert(message);
  }

  /**
   * 保存データ確認（選択されたデータのみ）
   */
  handleTestGetSavingDatas() {
    try {
      // 選択されたデータのみを保存対象として取得
      const selectedData = this.tableData.filter((_, idx) =>
        this.selectedRows.includes(idx)
      );

      let message = `【保存データ確認】\n`;
      message += `全データ数: ${this.tableData.length}件\n`;
      message += `選択データ数: ${selectedData.length}件\n\n`;

      if (selectedData.length === 0) {
        message += `保存対象データが選択されていません。\n`;
      } else {
        message += `保存対象データ:\n`;
        selectedData.forEach((data, i) => {
          message += `[${i + 1}] ID:${data.Id} ${data.label}\n`;
          message += `  数値1=${data.num1} 文字列1=${data.str1}\n`;
          message += `  審査結果=${data.ReviewResult} データチェック=${data.dataCheck}\n`;
          message += `  選択=${data.checked}\n\n`;
        });
      }

      alert(message);
    } catch (error) {
      alert(`【保存データ確認エラー】\n${error.message}`);
    }
  }

  /* ----------------------------------------
   * 保存処理（モック実装）
   * ---------------------------------------- */

  async handleSave() {
    try {
      // 選択されたデータのみを保存対象として取得
      const selectedData = this.tableData.filter((_, idx) =>
        this.selectedRows.includes(idx)
      );

      // 選択チェック
      if (selectedData.length === 0) {
        this.dispatchEvent(
          new ShowToastEvent({
            title: "選択エラー",
            message: "保存するデータが選択されていません。",
            variant: "warning"
          })
        );
        return;
      }

      // モック保存処理：実際のAPIコール処理をシミュレート
      const savingData = {
        tableData: selectedData,
        timestamp: new Date().toISOString(),
        recordCount: selectedData.length,
        validation: 0
      };

      // コンソールに保存データを出力（デバッグ用）
      console.log("【OPC保存実行】選択されたデータ:", savingData);

      // 短い遅延でAPI呼び出しをシミュレート
      await new Promise((resolve) => setTimeout(resolve, 500));

      this.dispatchEvent(
        new ShowToastEvent({
          title: "保存完了（OPC）",
          message: `選択された${selectedData.length}件のデータを保存しました。コンソールで内容を確認できます。`,
          variant: "success"
        })
      );
    } catch (error) {
      console.error("【OPC保存エラー】", error);
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
