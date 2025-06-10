import { LightningElement, track } from "lwc";

/**
 * CreditSummary コンポーネント
 *  - 一般与信ツリーグリッド（補正値をモーダル編集）
 *  - 本件保全状況ツリーグリッド
 *  - 保証人テーブル
 *  - 取引先／審査情報・補正理由パネル
 *
 * 2025-06-10 完全版
 */
export default class CreditSummary extends LightningElement {
  /* ───────────────── ② 取引先情報 ───────────────── */
  @track branchNumber = "999";
  @track branchName =
    "店名サンプルAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
  @track customerName =
    "株式会社サンプル商事AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";

  /* ─────────────── ③ 審査番号・金額単位・括り ─────────────── */
  @track reviewNumber = "0313";
  @track amountUnit = "千円";
  @track groupNumber = "9";

  /* ─────────────────── ⑤ 補正理由関連 ─────────────────── */
  @track correctionReason =
    "① 計算方法の見直し、② 市場変動を反映、③ 保全評価の更新、④ 信用限度の変更、⑤ その他理由…";
  @track poolCategory = "99";
  @track protectionRate = "99.99%";
  @track limitGeneral = "9,999,999";
  @track marketInclusion = "99";
  @track regulatoryCollateral = "9,999,999";

  /* ──────────────────── 一般与信 - ツリーグリッド ──────────────────── */
  // 行アクション
  rowActions = [{ label: "補正値を編集", name: "editCorrection" }];

  // カラム定義
  treeGridColumns1 = [
    {
      type: "text",
      fieldName: "label",
      label: "科目・摘要・票番号",
      initialWidth: 200
    },
    { type: "text", fieldName: "dueDate", label: "期日", initialWidth: 100 },
    { type: "text", fieldName: "rate", label: "利率", initialWidth: 80 },
    {
      type: "number",
      fieldName: "balance99",
      label: "99月末残高",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "principal",
      label: "債原額",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "change",
      label: "当月増減",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "postBalance",
      label: "本件後残高",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "actualBalance",
      label: "実勢残高",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "correction",
      label: "補正値",
      cellAttributes: { alignment: "right" }
    },
    { type: "action", typeAttributes: { rowActions: this.rowActions } }
  ];

  /**
   * 初期データ生成ユーティリティ
   * @param {{ base: string, label: string, multiplier: number }} cfg
   * @returns {Object[]} children
   */
  createChildren(cfg) {
    return Array.from({ length: 20 }, (_, i) => {
      const seed = cfg.multiplier * 1_000_000;
      return {
        id: `${cfg.base}${i + 1}`,
        label: `${cfg.label}${i + 1}`,
        dueDate: "99/99",
        rate: "-",
        balance99: seed + i * 10_000,
        principal: seed + i * 10_000,
        change: i % 2 === 0 ? 0 : -10_000,
        postBalance: seed + i * 10_000,
        actualBalance: seed + i * 10_000,
        correction: 0
      };
    });
  }

  /**
   * 親ノード生成
   */
  createRoot(id, label, base, multiplier) {
    const children = this.createChildren({
      base,
      label: `${label}項目`,
      multiplier
    });
    const sum = (rows, key) => rows.reduce((acc, r) => acc + r[key], 0);

    return {
      id,
      label,
      dueDate: "",
      rate: "",
      balance99: sum(children, "balance99"),
      principal: sum(children, "balance99"),
      change: sum(children, "change"),
      postBalance: sum(children, "balance99"),
      actualBalance: sum(children, "balance99"),
      correction: sum(children, "correction"),
      _children: children
    };
  }

  // データ保持用トラック
  @track treeGridData1 = [];

  /* ───────────── 本件保全状況 ツリーグリッド ───────────── */
  treeGridColumns2 = [
    {
      type: "text",
      fieldName: "collateralType",
      label: "担保種類",
      initialWidth: 200
    },
    {
      type: "number",
      fieldName: "regValue",
      label: "規定値",
      cellAttributes: { alignment: "right" }
    },
    {
      type: "number",
      fieldName: "marketValue",
      label: "時価ベース",
      cellAttributes: { alignment: "right" }
    }
  ];
  @track treeGridData2 = [];

  /* ───────────── 保証人テーブル ───────────── */
  guarantorColumns = [{ label: "保証人", fieldName: "name", type: "text" }];
  @track guarantorData = [];

  /* ───────────── モーダル編集用 ───────────── */
  @track isModalOpen = false;
  @track editRow = {};

  /* ───────────────── ライフサイクル ───────────────── */
  connectedCallback() {
    // 一般与信ツリーグリッド生成
    this.treeGridData1 = [
      this.createRoot("root1", "貸付金", "l", 1),
      this.createRoot("root2", "外為与信", "e", 2),
      this.createRoot("root3", "支払承諾", "s", 3)
    ];

    // 本件保全状況データ生成
    this.treeGridData2 = [
      this.generateCollateral("collGeneral", "規定一般承継", 8_000_000, "cg"),
      this.generateCollateral("collOther", "規定その他承継", 5_000_000, "co")
    ];

    // 保証人 5 名生成
    this.guarantorData = Array.from({ length: 5 }, (_, i) => ({
      id: `g${i + 1}`,
      name: `保証人${i + 1}`
    }));
  }

  /**
   * 保全状況データ生成
   */
  generateCollateral(id, typeLabel, baseValue, prefix) {
    const children = Array.from({ length: 20 }, (_, i) => ({
      id: `${prefix}${i + 1}`,
      collateralType: `担保種別${i + 1}`,
      regValue: baseValue / 16 + i * 5_000,
      marketValue: baseValue / 16 + i * 5_000
    }));
    const sum = (rows, key) => rows.reduce((a, r) => a + r[key], 0);
    return {
      id,
      collateralType: typeLabel,
      regValue: sum(children, "regValue"),
      marketValue: sum(children, "marketValue"),
      _children: children
    };
  }

  /* ───────────────── 行アクション (補正値編集) ───────────────── */
  handleRowAction(event) {
    const { action, row } = event.detail;
    if (action.name === "editCorrection") {
      this.editRow = { ...row };
      this.isModalOpen = true;
    }
  }

  handleCorrectionInput(event) {
    this.editRow.correction = Number(event.target.value);
  }

  closeModal() {
    this.isModalOpen = false;
  }

  saveCorrection() {
    // 再帰的更新関数
    const update = (rows, id, value) => {
      for (const r of rows) {
        if (r.id === id) {
          r.correction = value;
          return true;
        }
        if (r._children && update(r._children, id, value)) {
          // 親合計も再計算
          r.correction = r._children.reduce((acc, c) => acc + c.correction, 0);
          return true;
        }
      }
      return false;
    };

    update(this.treeGridData1, this.editRow.id, this.editRow.correction);
    // 強制再描画
    this.treeGridData1 = [...this.treeGridData1];
    this.isModalOpen = false;
  }

  /* ───────────────── 操作ボタン (ダミー) ───────────────── */
  handleFetchCalculation() {
    console.log("計数再取得");
  }
  handleCalculate() {
    console.log("計算");
  }
  handleRegisterCorrection() {
    console.log("補正値登録");
  }
  handleRegister() {
    console.log("登録");
  }
  handleFileExport() {
    console.log("ファイル出力");
  }
  handleExcelExport() {
    console.log("Excel出力");
  }
  handleRecentInquiry() {
    console.log("直近計数照会");
  }
  handlePastReview() {
    console.log("過去審査");
  }
  handleDepositDetail() {
    console.log("預金担保明細");
  }
  handleBillBalance() {
    console.log("手形電債残高");
  }
  handleSecuritiesDetail() {
    console.log("有価証券明細");
  }
  handleAssociationGuarantee() {
    console.log("協会保証明細");
  }
  handleRealEstateDetail() {
    console.log("不動産担保明細");
  }
}
