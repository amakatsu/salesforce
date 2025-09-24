import { LightningElement, api, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { validateElement } from "c/f003GsV0000DataValidation";

export default class RirituKeisuPage extends LightningElement {
  @api activeTab = "riritu";
  @api rirituData;
  @api keisuData;
  @track multiHeaderData = [];
  @track isSpinnerVisible = false;

  /**
   * コンポーネント初期化
   */
  connectedCallback() {
    this.multiHeaderData = [];
  }

  /**
   * 子コンポーネントからのバリデーションエラー通知処理
   */
  handleValidationError(event) {
    const { message, field, value } = event.detail;
    const errorMessage =
      field && value !== undefined
        ? `「${field}」フィールドの入力値「${value}」が無効です。`
        : message || "入力値に問題があります。";

    this.showToast("入力エラー", errorMessage, "error");
  }

  handleFieldChange() {}

  /**
   * データ確認ボタン処理：選択されたデータの詳細表示
   */
  handleDataVerification(event) {
    const component = this.getComponent(event.target.dataset.component);
    if (!component?.tableData) {
      this.showToast("エラー", "コンポーネントが見つかりません", "error");
      return;
    }

    const checkedData = component.tableData.filter((r) => r.checked);
    if (checkedData.length === 0) {
      this.showToast(
        "データ確認",
        "⚠️ チェックされたデータがありません",
        "warning"
      );
      return;
    }

    let message = `📊 ${event.target.dataset.component.toUpperCase()}テーブル (editableTableData)\n選択件数: ${
      checkedData.length
    }件\n\n`;

    checkedData.forEach((record, index) => {
      message += `■ レコード${index + 1}\nID: ${record.Id}\n`;

      const elements = component.getElementsById(record.Id);
      const hasError = this.checkValidationErrors(elements);
      message += hasError
        ? "⚠️ バリデーションエラーあり\n"
        : "✅ バリデーション正常\n";

      // データ値表示
      Object.keys(record)
        .filter(
          (key) =>
            !["Id", "checked"].includes(key) &&
            !key.endsWith("Class") &&
            !key.endsWith("Disabled")
        )
        .forEach((field) => {
          message += `${field}\n└ ${record[field] || "(空)"}\n`;
        });

      // DOM値表示
      if (elements?.length > 0) {
        message += "--- DOM実際値 ---\n";
        Array.from(elements).forEach((el) => {
          const field = el.dataset.field;
          if (field) {
            const domValue = this.getDomValue(el);
            const isMatch = String(domValue) === String(record[field]);
            message += `${field} ${
              isMatch ? "✅" : "❌"
            }\n└ DOM: ${domValue}\n`;
          }
        });
      }
      message += "\n";
    });

    this.showToast("選択データ詳細", message, "info");
  }

  /**
   * 保存ボタン処理：選択データのバリデーション・保存実行
   */
  handleSave(event) {
    const componentType = event.target.dataset.component;
    this.handleApiSave(componentType);
  }

  /**
   * API連携（正常・連携1回）イベント
   */
  async handleApiSave(componentType) {
    try {
      // 変数初期化
      this.isSpinnerVisible = true;
      let isValid = 0;

      // 子コンポーネントからデータ抽出・単項目チェック
      const component = this.getComponent(componentType);
      // getApiDataList戻り値: [itemList, valid]
      // itemList: { tableData: [...], selectedCount: 数値, componentName: 文字列, apiType: 文字列 }
      // valid: バリデーションエラー数（0=正常、1以上=エラーあり）
      const [itemList, valid] = component.getApiDataList();
      isValid += valid;

      if (isValid > 0) {
        // エラー時 - 単項目チェックエラー表示共通処理に連携
        this.validateErrorHandler();
        return;
      }

      // 保存処理実行
      this.performSave(itemList.tableData);

    } catch (error) {
      this.systemErrorHandler(error, 'SAVE_OPERATION');
    }
  }

  /**
   * 単項目チェックエラー表示共通処理
   */
  validateErrorHandler() {
    // 共通トーストエラー表示
    this.showToast(
      "バリデーションエラー",
      "入力内容に誤りがあります。赤枠の項目を確認してください。",
      "error"
    );
    // スピナーを非表示
    this.isSpinnerVisible = false;
  }

  /**
   * システムエラー表示共通処理
   */
  systemErrorHandler(error, operation) {
    console.error(`System Error in ${operation}:`, error);
    this.showToast(
      "システムエラー",
      `システムエラーが発生しました。管理者に連絡してください。\n操作: ${operation}`,
      "error"
    );
    this.isSpinnerVisible = false;
  }

  /**
   * 保存処理実行
   */
  async performSave(selectedData) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    this.showToast(
      "保存完了",
      `${selectedData.length}件のデータを保存しました。`,
      "success"
    );
    this.isSpinnerVisible = false;
  }

  // ========== ヘルパーメソッド ==========

  /**
   * コンポーネント取得
   */
  getComponent(type) {
    return this.template.querySelector(
      type === "opc" ? "c-row-dynamic-o-p-c" : "c-row-dynamic-multi-header"
    );
  }

  /**
   * バリデーションエラー確認（既存のvalidateElement準拠）
   */
  checkValidationErrors(elements) {
    if (!elements?.length) return false;
    return Array.from(elements).some(
      (el) =>
        el.classList.contains("slds-has-error") ||
        el.getAttribute("aria-invalid") === "true" ||
        el.classList.contains("error") ||
        !el.validity.valid
    );
  }

  /**
   * DOM要素から値を取得（数値エラー対応）
   */
  getDomValue(el) {
    if (el.type === "number" && el.validity?.badInput) {
      return "(無効な数値入力)";
    }
    return el.type === "checkbox" ? el.checked : el.value;
  }

  /**
   * トースト表示
   */
  showToast(title, message, variant) {
    this.dispatchEvent(
      new ShowToastEvent({ title, message, variant, mode: "sticky" })
    );
  }
}
