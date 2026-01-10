import { LightningElement, api } from "lwc";

export default class F003DrV0000MeisaiMockM extends LightningElement {
  @api size;
  @api label;
  @api record;

  // モーダル表示のモック実装
  static async open(config) {
    return new Promise((resolve) => {
      // モック実装：常に更新されたレコードを返す
      const mockUpdatedRecord = {
        ...config.record,
        // 何らかの更新をモック
        lastModified: new Date().toISOString()
      };

      // 実際の実装では、ユーザーの操作に応じて resolve する
      // ここでは簡単なモックとして更新されたレコードを返す
      setTimeout(() => {
        resolve(mockUpdatedRecord);
      }, 100);
    });
  }

  handleCancel() {
    this.dispatchEvent(new CustomEvent("cancel"));
  }

  handleSave() {
    this.dispatchEvent(
      new CustomEvent("save", {
        detail: { record: this.record }
      })
    );
  }
}
