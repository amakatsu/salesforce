import { LightningElement, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getCollateralData from "@salesforce/apex/CollateralDataService.getCollateralData";
import postCollateralData from "@salesforce/apex/CollateralDataService.postCollateralData";

export default class CollateralDataManager extends LightningElement {
  @track collateralData = [];
  @track showModal = false;
  @track modalTitle = "";
  @track selectedRecord = null;
  @track formData = {};


  // テーブルのカラム定義
  columns = [
    { label: "ID", fieldName: "id", type: "text" },
    {
      label: "担保種別",
      fieldName: "collateralType",
      type: "text",
      editable: true
    },
    {
      label: "規定価値",
      fieldName: "regValue",
      type: "currency",
      editable: true
    },
    {
      label: "市場価値",
      fieldName: "marketValue",
      type: "currency",
      editable: true
    },
    {
      type: "action",
      typeAttributes: {
        rowActions: [
          { label: "編集", name: "edit" },
          { label: "削除", name: "delete" }
        ]
      }
    }
  ];

  connectedCallback() {
    this.loadCollateralData();
  }

  // 担保データを取得
  async loadCollateralData() {
    try {
      const result = await getCollateralData();
      this.collateralData = JSON.parse(result);
    } catch (error) {
      this.showToast("エラー", "データの取得に失敗しました: " + error.body.message, "error");
    }
  }

  // 新規作成ボタンクリック
  handleCreate() {
    this.modalTitle = "新規担保データ作成";
    this.selectedRecord = null;
    this.formData = {
      collateralType: "",
      regValue: 0,
      marketValue: 0
    };
    this.showModal = true;
  }

  // 更新ボタンクリック
  handleRefresh() {
    this.loadCollateralData();
    this.showToast("成功", "データを更新しました", "success");
  }

  // 行アクション処理
  handleRowAction(event) {
    const actionName = event.detail.action.name;
    const row = event.detail.row;

    switch (actionName) {
      case "edit":
        this.handleEdit(row);
        break;
      case "delete":
        this.handleDelete(row);
        break;
    }
  }

  // 編集処理
  handleEdit(row) {
    this.modalTitle = "担保データ編集";
    this.selectedRecord = { ...row };
    this.formData = {
      collateralType: row.collateralType,
      regValue: row.regValue,
      marketValue: row.marketValue
    };
    this.showModal = true;
  }

  // 削除処理（DELETE APIが必要な場合はApexに追加）
  async handleDelete(row) {
    this.showToast("情報", "削除機能は現在準備中です", "info");
  }

  // インライン保存処理
  async handleSave(event) {
    const recordInputs = event.detail.draftValues;

    try {
      for (const record of recordInputs) {
        await postCollateralData({ dataObj: record });
      }

      this.showToast("成功", "データを更新しました", "success");
      this.loadCollateralData();
    } catch (error) {
      this.showToast("エラー", "更新に失敗しました: " + error.body.message, "error");
    }
  }

  // 入力値変更処理
  handleInputChange(event) {
    const fieldName = event.target.name;
    const fieldValue = event.target.value;
    this.formData = { ...this.formData, [fieldName]: fieldValue };
  }

  // フォーム送信処理
  async handleFormSubmit() {
    try {
      await postCollateralData({ dataObj: this.formData });
      
      this.showToast(
        "成功",
        this.selectedRecord ? "データを更新しました" : "データを作成しました",
        "success"
      );
      this.closeModal();
      this.loadCollateralData();
    } catch (error) {
      this.showToast("エラー", "操作に失敗しました: " + error.body.message, "error");
    }
  }

  // モーダルを閉じる
  closeModal() {
    this.showModal = false;
    this.formData = {};
  }

  // トースト表示
  showToast(title, message, variant) {
    const evt = new ShowToastEvent({
      title: title,
      message: message,
      variant: variant
    });
    this.dispatchEvent(evt);
  }
}
