package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 外為与信 科目明細の1行分データ（種別キー付き）
 * <p>外為与信の各科目（指定外L/C、D/P・D/A、輸入L/C等）を種別コードで識別する。</p>
 */
public class GaitameMeisai {

    /** 外為科目コード（識別キー） 例: "SHITEI_GAI_LC", "DP_DA", "GAIKA_KITTE" 等 */
    private String gaitameKamokuCode;

    /** 外為科目名 例: "指定外L/C", "D/P・D/A・輸出OA" 等 */
    private String gaitameKamokuName;

    /** 極度額 */
    private Long creditLimit;

    /** 指定月末残高 */
    private Long monthEndBalance;

    /** 当月増減額 */
    private Long monthlyChange;

    /** 本件後残高 */
    private Long postLoanBalance;

    /** 実勢現在残高 */
    private Long actualBalance;

    public String getGaitameKamokuCode() { return gaitameKamokuCode; }
    public void setGaitameKamokuCode(String v) { this.gaitameKamokuCode = v; }
    public String getGaitameKamokuName() { return gaitameKamokuName; }
    public void setGaitameKamokuName(String v) { this.gaitameKamokuName = v; }
    public Long getCreditLimit() { return creditLimit; }
    public void setCreditLimit(Long v) { this.creditLimit = v; }
    public Long getMonthEndBalance() { return monthEndBalance; }
    public void setMonthEndBalance(Long v) { this.monthEndBalance = v; }
    public Long getMonthlyChange() { return monthlyChange; }
    public void setMonthlyChange(Long v) { this.monthlyChange = v; }
    public Long getPostLoanBalance() { return postLoanBalance; }
    public void setPostLoanBalance(Long v) { this.postLoanBalance = v; }
    public Long getActualBalance() { return actualBalance; }
    public void setActualBalance(Long v) { this.actualBalance = v; }
}
