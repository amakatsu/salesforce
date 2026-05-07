package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 顧客財務関連データDTO
 * <p>DB取得の顧客情報・財務情報・銀取計数・補正値等を横持ちで保持する。イミュータブル。</p>
 * <p>一般与信状況の月末残高・本件後残高・実勢現在残高はDB値が最新として優先される項目。</p>
 */
public class CustomerFinancialDataDto {

    // 一般与信の月末残高・本件後残高・実勢現在残高は
    // KeisuBaseDataDtoと同じ構造のGeneralCreditItemで全行を保持する。
    // ここではDB優先項目と補正値のみ代表フィールドとして記載。

    /** 規定担保補正値・規定値（DB管理、ホストより優先） // 旧: F_HIKIATE_KITEITI_TOT[KTITNP_HOSCH] */
    private final Long collateralCorrectionStandard;

    /** 規定担保補正値・時価ベース（DB管理、ホストより優先） // 旧: F_HIKIATE_JIKA_TOT[KTITNP_HOSCH] */
    private final Long collateralCorrectionMarket;

    /** 内HL信用不算入（本件後残高） */
    private final Long hlExcludedPostLoanBalance;

    /** 一般与信1タブの金額単位 // 旧: F_TANI_MSG_1 */
    private final String generalCreditUnitLabel;

    /** 市場性与信1タブの金額単位 // 旧: F_SJOSEIINF_TANI_MSG_1 */
    private final String marketCreditUnitLabel;

    // ※ 実装時は一般与信全行のGeneralCreditItem（月末残高/本件後残高/実勢残高のみDB値）、
    //    保全状況の全明細項目もフィールドとして定義する。

    public CustomerFinancialDataDto(Long collateralCorrectionStandard,
                                    Long collateralCorrectionMarket,
                                    Long hlExcludedPostLoanBalance,
                                    String generalCreditUnitLabel,
                                    String marketCreditUnitLabel) {
        this.collateralCorrectionStandard = collateralCorrectionStandard;
        this.collateralCorrectionMarket = collateralCorrectionMarket;
        this.hlExcludedPostLoanBalance = hlExcludedPostLoanBalance;
        this.generalCreditUnitLabel = generalCreditUnitLabel;
        this.marketCreditUnitLabel = marketCreditUnitLabel;
    }

    public Long getCollateralCorrectionStandard() { return collateralCorrectionStandard; }
    public Long getCollateralCorrectionMarket() { return collateralCorrectionMarket; }
    public Long getHlExcludedPostLoanBalance() { return hlExcludedPostLoanBalance; }
    public String getGeneralCreditUnitLabel() { return generalCreditUnitLabel; }
    public String getMarketCreditUnitLabel() { return marketCreditUnitLabel; }
}
