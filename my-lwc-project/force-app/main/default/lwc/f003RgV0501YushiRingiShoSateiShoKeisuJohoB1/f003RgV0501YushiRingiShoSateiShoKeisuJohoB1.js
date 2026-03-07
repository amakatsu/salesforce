import { LightningElement, api } from "lwc";

export default class F003RgV0501YushiRingiShoSateiShoKeisuJohoB1 extends LightningElement {
  @api showCalculationAndRegisterButtons;

  handleFetchCalculation() {
    console.log("計数再取得");
  }

  handleCalculate() {
    console.log("計算");
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

  handlePastReview() {
    console.log("過去禀査");
  }

  handleRecentInquiry() {
    console.log("直近計数照会");
  }

  handleDepositDetail() {
    console.log("預金担保明細");
  }

  handlePayerBalance() {
    console.log("支払人別残高推移");
  }

  handleBillBalance() {
    console.log("電債担保残高");
  }

  handleSecuritiesDetail() {
    console.log("有価証券担保明細");
  }

  handleAssociationGuarantee() {
    console.log("協会保証明細");
  }

  handleGeneralGuarantee() {
    console.log("一般保証明細");
  }

  handleOtherCollateral() {
    console.log("その他担保明細");
  }

  handleRealEstateDetail() {
    console.log("不動産担保明細");
  }
}
