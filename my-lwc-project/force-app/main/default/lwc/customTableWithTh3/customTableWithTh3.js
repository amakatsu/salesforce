import { LightningElement, api, track } from "lwc";
import ModalView from "c/f003DrV0000MeisaiMockM";
import {
  COMPONENT_KEY,
  SAVING_BTN_LIST,
  API_DATA
} from "./f003DrV0000MeisaiMockC1Const";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { validateElement } from "c/f003GsV0000DataValidation";
import { YUSGS5015C_E, YUSGS5016C_E } from "c/f003GsV0000MsgConst";
// import ConfirmInfo from 'c/f003GsV0000ConfirmInfo';
import AlertError from "c/f003GsV0000AlertError";
export default class F003DrV0000MeisaiMockC1 extends LightningElement {
  initialize = false;
  selectedRows = [];
  @track record = API_DATA;
  @track tableData = [...structuredClone(API_DATA.dtoList), { checked: false }];
  /**
   * LWCがDOMにレンダリングされた後実行されるライフサイクルフック
   * レンダリングの度に呼び出されるため、個別の制御が必要。
   */
  renderedCallback() {
    if (!this.initialize) this.adjustHeaderPositions();
    this.initialize = true;
  }
  /**
   * カスタマイズテーブル・行選択処理
   */
  handleRowSelection(event) {
    const checked = event.target.checked;
    const rowidx = parseInt(event.target.dataset.idx, 10);
    const havingFlg = this.selectedRows.includes(rowidx);
    if (checked) {
      if (havingFlg) {
        this.selectedRows = this.selectedRows.filter(function (selectRow) {
          return selectRow !== rowidx;
        });
      } else {
        this.selectedRows.push(rowidx);
      }
    } else {
      this.selectedRows = this.selectedRows.filter(function (selectRow) {
        return selectRow !== rowidx;
      });
    }
    this.tableData = this.tableData.map((item, idx) =>
      idx === rowidx ? { ...item, checked: checked } : item
    );
  }
  /**
   * カスタマイズテーブル・全選択・全選択解除処理
   */
  handleSelectFullCheck(event) {
    const checked = event.target.checked; // 選択行の初期化
    this.selectedRows = [];
    if (checked) {
      // 取得した件数分のインデックス番号があればいい。
      this.selectedRows = [...Array(this.tableData.length).keys()];
    }
    this.tableData = this.tableData.map((item) => ({
      ...item,
      checked: checked
    }));
  }
  handleSelectPossibility(event) {
    const check = event.target.checked;
    const rowidx = event.target.dataset.idx;
    const row = { ...this.tableData[rowidx] };
    row.possibility = check;
    this.tableData[rowidx] = row;
  }
  /**
   * 行選択状況チェック処理
   */
  async checkSelectedRows() {
    if (this.selectedRows.length > 1) {
      const result = await AlertError.open({
        size: "small",
        message: YUSGS5016C_E,
        code: "YUSGS5016C-E"
      });
      return result;
    } else if (this.selectedRows.length === 0) {
      const result = await AlertError.open({
        size: "small",
        message: YUSGS5015C_E,
        code: "YUSGS5015C-E"
      });
      return result;
    }
    return "";
  }
  /**
   * レコード修正イベント
   */
  async handleRecordEditClick() {
    // 行選択チェック
    let checkResult = "";
    checkResult = await this.checkSelectedRows(); // チェック問題なければ先進め
    if (checkResult === "") {
      // 編集モーダル表示
      const idx = this.selectedRows[0];
      const modalResult = await ModalView.open({
        size: "medium",
        label: "Test Modal Title",
        record: this.tableData[idx]
      }); // 「更新」ボタン押下の場合、レコード更新 // 最終的に保存処理などのAPI連携でDB反映する想定のため、画面上のレコードのみ更新
      if (modalResult !== "cancel" && modalResult !== undefined) {
        this.updateRecord(modalResult);
      }
    }
  }
  /**
   * レコード更新処理
   */
  updateRecord(updatedRecord) {
    // 行番号が一致しているテーブルデータを更新
    this.tableData = this.tableData.map((item) => {
      if (item.id === updatedRecord.id) {
        return { ...item, ...updatedRecord };
      }
      return item;
    });
  }
  /**
   * 保存ボタン押下時の処理<br>
   *
   * @return { Array.<Object, Array.<Element>> } APIに渡す用のリストと、単項目チェック用のリストを返却する。
   */
  @api
  getSavingDatas() {
    let itemList = {};
    let valid = 0; // 可変のテーブルデータを除いたdata-idを持つ要素を取得する。
    const notTableData = this.template.querySelectorAll("[data-id]:not(tr *)");
    const [iList, dList] = getComponentDataList(notTableData, SAVING_BTN_LIST);
    validateElement(dList);
    itemList = { ...iList };
    itemList.dtoList = this.tableData; // 下については、画面に表示されているデータを直接取得し、個別に改めて単項目チェックを実施する必要があるケースにおいて利用する。     return [itemList, valid];
  } // 複数のヘッダーを固定するための設定（レンダリングの度呼び出す）
  adjustHeaderPositions() {
    const headerRows = this.template.querySelectorAll("thead tr");
    let topPosition = 0;
    headerRows.forEach((row) => {
      const thElements = row.querySelectorAll("th");
      thElements.forEach((th) => {
        th.style.top = `${topPosition}px`;
      });
      topPosition += row.clientHeight;
    });
  }
}
