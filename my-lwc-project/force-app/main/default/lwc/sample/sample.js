/************************************************************************************************************* * 画面名   ：  関連禀査情報 * 画面概要 ：  関連禀査情報画面のC1子コンポーネント ************************************************************************************************************/ import {
  LightningElement,
  track,
  api
} from "lwc";
import { CV_DISP_LIST } from "c/f003CvV0000Const";
import {
  COMPONENT_KEY,
  RELATED_RINSA_INFO_LIST_COLUMNS,
  C1_CHANGE_REQ_LIST,
  C1_CHANGE_LIST,
  C1_ADD_REQ_LIST,
  C1_ADD_LIST
} from "./f003CvV0103KanrenRinsaJohoMC1Const";
import { getCodeList, getCodeListWithBlank } from "c/f003GsV0000Code";
import { CATEGORY_SELECTION } from "c/f003CvV0000CodeConst";
import { validateElement } from "c/f003GsV0000DataValidation";
import { PATTERNS } from "c/f003GsV0000Const";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { YUSCV0017C_I, YUSCV1711C_E } from "c/f003CvV0000MsgConst";
import AlertInfo from "c/f003GsV0000AlertInfo";
import { getComponentDataList } from "c/f003GsV0000GetComponentDataList";
import { navigateHelp } from "c/f003CvV0000Utils";
export default class F003CvV0103KanrenRinsaJohoMC1 extends LightningElement {
  // データロードフラグ
  isLoaded = false;

  // 子コンポーネントデータレコード
  @track record = {};

  // 選択行データリスト
  selectedRows = [];

  // 外部コード名称
  cbxCategorySelectOptions = [];

  parentParameterList = {};

  relatedRinsaInfoList = [];

  // 初期Value値設定
  relatedRinsaInfoListColumns = RELATED_RINSA_INFO_LIST_COLUMNS;

  // パターン取得
  PATTERNS = PATTERNS;

  // ボタン制御フラグ
  isBtnDisabledFlg = false;

  /**   * 親コンポーネントからのレコードデータのgetter   *   * @returns {Object} レコードデータ   */
  @api
  get records() {
    return this._records;
  }

  /**   * 親コンポーネントからのレコードデータのsetter   *   * @param {Object} value レコードデータ   */
  set records(value) {
    this._records = value;

    this.dataSetting();
  }

  /**   * データ設定処理   */
  async dataSetting() {
    try {
      // レコードデータチェック
      if (
        !this.records ||
        typeof this.records !== "object" ||
        this.records.constructor !== Object ||
        Object.keys(this.records).length === 0
      ) {
        return;
      }

      // 親コンポーネントからパラメータ引継ぎ
      this.parentParameterList = this._records.parameterList;

      // コンポーネントデータの初期化
      const componentData = {};
      // Const定義のCOMPONENT_KEY宣言項目のディープコピー
      COMPONENT_KEY.forEach((key) => {
        componentData[key] = typeof this._records[key] !== "undefined" ? this._records[key] : "";
      });

      // リストに、名称変換時のコード値退避用要素creditRinsaValueを追加
      componentData.relatedRinsaInfoList = componentData.relatedRinsaInfoList.map((item) => ({
        ...item,

        creditRinsaValue: ""
      }));

      // 初回呼出の場合
      if (!this.isLoaded) {
        // 外部コード系のデータ取得処理はここで実装
        await this.getCodeList();

        // データロードフラグをオンにする
        this.isLoaded = true;
      }

      // 画面制御
      this.btnDisabled();

      // テーブルデータコピー
      const tempList = {
        ...componentData
      }.relatedRinsaInfoList;

      // Proxyオブジェクトを通常のオブジェクトに変換
      const normalObject = JSON.parse(JSON.stringify(tempList));

      const tableList = structuredClone(normalObject);

      this.relatedRinsaInfoList = this.convertCodeToName(tableList);

      if (this.parentParameterList.hdnSourceDispId === CV_DISP_LIST.CvV0501.ID) {
        // 遷移元が抵触要管理シートの場合
        componentData.categorySelect = "4";
      } else {
        componentData.categorySelect = "";
      }

      // 遷移元画面情報（店番、取引先番号）
      const reqHdnParam = {
        brNo: this.parentParameterList.hdnBrNo,

        cmNo: this.parentParameterList.hdnCmNo
      };
      // 子コンポーネントデータレコードの更新
      this.record = Object.assign(reqHdnParam, componentData);
    } catch (error) {
      this.systemErrorHandler(error);
    }
  }

  /**   * 外部コード取得処理   */
  async getCodeList() {
    // 区分選択の初期表示分岐用変数
    let pattern = "";

    if (this.parentParameterList.hdnSourceDispId === CV_DISP_LIST.CvV0501.ID) {
      // 遷移元が抵触要管理シートの場合
      pattern = "3";
    } else {
      pattern = "2";
    }

    // 区分選択コンボ。一覧（与信禀査、関連禀査、抵触関連）。
    const [
      creditRinsaOptions,
      relatedRinsaOptions,
      violationRelatedOptions,
      _cbxCategorySelectOptions
    ] = await Promise.all([
      getCodeList(CATEGORY_SELECTION.CODE_ID, "2", "4"),

      getCodeList(CATEGORY_SELECTION.CODE_ID, "2", "5"),

      getCodeList(CATEGORY_SELECTION.CODE_ID, "2", "6"),

      getCodeListWithBlank(CATEGORY_SELECTION.CODE_ID, "1", pattern)
    ]);

    this.creditRinsaOptions = creditRinsaOptions;

    this.relatedRinsaOptions = relatedRinsaOptions;

    this.violationRelatedOptions = violationRelatedOptions;

    this.cbxCategorySelectOptions = _cbxCategorySelectOptions;
  }

  /**   * 外部コード変換処理   */
  convertCodeToName(dataList) {
    // オプションリストとの突合
    // 与信禀査、関連禀査、抵触関連
    dataList.forEach((t) => {
      const creditRinsaName =
        this.creditRinsaOptions
          .filter((item) => item.value === t.creditRinsa)
          .map((r) => (r.value === "" ? "" : r.label))[0] || "";

      const relatedRinsaName =
        this.relatedRinsaOptions
          .filter((item) => item.value === t.relatedRinsa)
          .map((r) => (r.value === "" ? "" : r.label))[0] || "";

      const violationRelatedName =
        this.violationRelatedOptions
          .filter((item) => item.value === t.violationRelated)
          .map((r) => (r.value === "" ? "" : r.label))[0] || "";

      // 名称変換前に外部コードのvalue値退避(分岐に使用)
      t.creditRinsaValue = t.creditRinsa;

      // 各要素を名称に変換
      t.creditRinsa = creditRinsaName;

      t.relatedRinsa = relatedRinsaName;

      t.violationRelated = violationRelatedName;
    });

    return dataList;
  }

  /**   * ボタン制御イベント   */
  btnDisabled() {
    if (this.parentParameterList.hdnKanrenRinsaJohoCanUpdateFlg === true) {
      //
      ボタン活性;
      this.isBtnDisabledFlg = false;
    } else {
      //
      ボタン非活性;
      this.isBtnDisabledFlg = true;
    }
  }

  /**   * 開くボタン押下イベント   */
  async handleOpenClick() {
    const result = await AlertInfo.open({
      size: "small",

      message: YUSCV0017C_I,

      code: "YUSCV0017C-I"
    });

    if (!result) {
      return;
    }

    if (this.selectedRows.length === 0) {
      const event = new ShowToastEvent({
        title: "Error",

        message: YUSCV1711C_E,

        variant: "error"
      });

      this.dispatchEvent(event);
    }
  }

  /**   * ヘルプボタン押下イベント   */
  handleHelpClick() {
    navigateHelp(CV_DISP_LIST.CvV0103.ID);
  }

  /**   * 変更ボタン押下イベント   */
  handleChangeClick() {
    const exe = new CustomEvent("update");

    this.dispatchEvent(exe);
  }

  /**   * 追加登録ボタン押下イベント   */
  handleAddClick() {
    const exe = new CustomEvent("add");

    this.dispatchEvent(exe);
  }

  /**   * 削除ボタン押下イベント   */
  handleDeleteClick() {
    const exe = new CustomEvent("delete");

    this.dispatchEvent(exe);
  }

  /**   * 入力項目値変更イベント   *   * @param {Event} event イベント   */
  handleRecordValueChange(event) {
    // データレコードの更新
    this.record[event.target.dataset.id] = event.target.value;

    // バリデーションチェック実施
    const inputElement = event.target;

    const childDataList = [inputElement];

    validateElement(childDataList);
  }

  /**   * システムエラー連携処理   */
  systemErrorHandler(error) {
    const exe = new CustomEvent("error", {
      detail: {
        error: error
      }
    });

    this.dispatchEvent(exe);
  }

  /**   * 行選択状況チェック処理   */
  @api
  async checkSelectedRows() {
    if (this.selectedRows.length === 0) {
      const event = new ShowToastEvent({
        title: "Error",

        message: YUSCV1711C_E,

        variant: "error"
      });

      this.dispatchEvent(event);

      return;
    }

    return "";
  }

  /**   * 選択行データ取得処理   *   * @param {Event} event イベント   */
  handleRowSelection(event) {
    // 選択行データリストの更新
    this.selectedRows = event.detail.selectedRows;
  }

  /**   * 変更処理：子コンポ―ネントデータ取得   */
  @api
  getChangeList() {
    let valid = 0;

    // 子コンポーネントのデータを抽出
    const data = this.template.querySelectorAll("[data-id]");

    // 必要な項目に絞ってリスト化
    const [itemList, dataList] = getComponentDataList(data, C1_CHANGE_LIST);

    // 単項目チェック
    valid = validateElement(dataList, C1_CHANGE_REQ_LIST, data);

    return [itemList, valid];
  }

  /**   * 変更処理：子コンポ―ネントデータ取得＿バリデーションチェックなし   */
  @api
  getChangeNoCheckList() {
    // 子コンポーネントのデータを抽出
    const data = this.template.querySelectorAll("[data-id]");

    // 必要な項目に絞ってリスト化
    const [itemList] = getComponentDataList(data, C1_CHANGE_LIST);

    return [itemList];
  }

  /**   * 追加登録処理：子コンポ―ネントデータ取得   */
  @api
  getAddList() {
    let valid = 0;

    // 子コンポーネントのデータを抽出
    const data = this.template.querySelectorAll("[data-id]");

    // 必要な項目に絞ってリスト化
    const [itemList, dataList] = getComponentDataList(data, C1_ADD_LIST);

    // 単項目チェック
    valid = validateElement(dataList, C1_ADD_REQ_LIST, data);

    return [itemList, valid];
  }

  /**   * 追加登録処理：子コンポ―ネントデータ取得＿バリデーションチェックなし   */
  @api
  getAddNoCheckList() {
    // 子コンポーネントのデータを抽出
    const data = this.template.querySelectorAll("[data-id]");

    // 必要な項目に絞ってリスト化
    const [itemList] = getComponentDataList(data, C1_ADD_LIST);

    return [itemList];
  }

  /**   * 選択行データ取得処理   */
  @api
  getSelectRecordList() {
    return this.selectedRows;
  }

  /**   * 選択行データクリア処理   */
  @api
  clearSelectedRows() {
    this.selectedRows = [];

    const datatable = this.template.querySelector('[data-id="relatedRinsaInfoList"]');

    if (datatable) {
      datatable.selectedRows = [];
    }
  }
}
