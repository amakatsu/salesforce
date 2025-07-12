import { LightningElement, track } from "lwc";

export default class EditableTableWithHighlight extends LightningElement {
  // 初期データ（再取得用）
  initialData = [
    { id: 1, name: "佐藤", title: "マネージャー" },
    { id: 2, name: "田中", title: "エンジニア" }
  ];

  // 保存されたデータ
  originalData = [];
  @track records = [];

  connectedCallback() {
    this.resetData();
  }

  // データのリセットと初期化
  resetData() {
    // initialDataをディープコピーして、originalDataとrecordsを初期化
    this.originalData = JSON.parse(JSON.stringify(this.initialData));
    this.records = JSON.parse(JSON.stringify(this.initialData)).map((item) => ({
      ...item,
      nameClass: "",
      titleClass: ""
    }));
  }

  handleChange(event) {
    const id = parseInt(event.target.dataset.id, 10);
    const field = event.target.dataset.field;
    const value = event.target.value;

    // records内のデータを更新
    this.records = this.records.map((record) => {
      if (record.id === id) {
        return { ...record, [field]: value };
      }
      return record;
    });
  }

  handleSave() {
    // 変更を保存し、UIに反映
    this.records = this.records.map((record) => {
      const original = this.originalData.find((r) => r.id === record.id);
      const newRecord = { ...record };

      // Nameの変更を確認
      if (original.name !== record.name) {
        newRecord.nameClass = "changed-cell";
      }

      // Titleの変更を確認
      if (original.title !== record.title) {
        newRecord.titleClass = "changed-cell";
      }

      return newRecord;
    });

    // 現在のrecordsをoriginalDataとして保存
    this.originalData = JSON.parse(
      JSON.stringify(
        this.records.map(({ id, name, title }) => ({ id, name, title }))
      )
    );
  }

  handleReset() {
    this.resetData();
  }
}
