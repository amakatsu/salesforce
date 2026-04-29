package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 保全率計算結果DTO
 * <p>保全率（%）・総合与信・総合信用の計算結果を保持する。配列なし。</p>
 */
public class CoverageRatioCalcResultDto {

    /** 保全率・金額単位（「千円」「百万円」「億円」のいずれか） // 旧: F_HOZEN_TANI_MSG */
    private String amountUnitLabel;

    /** 保全率・限度算入一般与信（単位変換後） // 旧: F_HOZEN_IPNYSN */
    private String includedGeneralCredit;

    /** 保全率・限度算入市場性与信（単位変換後） // 旧: F_HOZEN_SJOSEIYSN */
    private String includedMarketCredit;

    /** 保全率・規定担保合計（単位変換後） // 旧: F_HOZEN_KITEITANPO */
    private String standardCollateralTotal;

    /** 保全率・保全率（小数点第2位まで、上限999.99） // 旧: F_HOZEN_HOZENRT */
    private String coverageRatio;

    /** 保全率・総合与信 // 旧: F_HOZEN_SOGOYSN */
    private String totalCredit;

    /** 保全率・総合信用 // 旧: F_HOZEN_SOGOSNYO */
    private String totalTrust;

    public String getAmountUnitLabel() { return amountUnitLabel; }
    public void setAmountUnitLabel(String v) { this.amountUnitLabel = v; }
    public String getIncludedGeneralCredit() { return includedGeneralCredit; }
    public void setIncludedGeneralCredit(String v) { this.includedGeneralCredit = v; }
    public String getIncludedMarketCredit() { return includedMarketCredit; }
    public void setIncludedMarketCredit(String v) { this.includedMarketCredit = v; }
    public String getStandardCollateralTotal() { return standardCollateralTotal; }
    public void setStandardCollateralTotal(String v) { this.standardCollateralTotal = v; }
    public String getCoverageRatio() { return coverageRatio; }
    public void setCoverageRatio(String v) { this.coverageRatio = v; }
    public String getTotalCredit() { return totalCredit; }
    public void setTotalCredit(String v) { this.totalCredit = v; }
    public String getTotalTrust() { return totalTrust; }
    public void setTotalTrust(String v) { this.totalTrust = v; }
}
