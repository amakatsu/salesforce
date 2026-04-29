package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 支払承諾 明細の1行分データ（種別キー付き）
 * <p>支払承諾の各科目（支承・一般、支承・一般外為、代理貸付等）を種別コードで識別する。</p>
 */
public class ShiharaiShodakuMeisai {

    /** 支払承諾科目コード（識別キー） 例: "IPPAN", "IPPAN_GAITAME", "DAIRI_KASHITSUKE" 等 */
    private String shishoKamokuCode;

    /** 支払承諾科目名 例: "支承・一般", "支承・一般外為", "代理貸付" 等 */
    private String shishoKamokuName;

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

    public String getShishoKamokuCode() { return shishoKamokuCode; }
    public void setShishoKamokuCode(String v) { this.shishoKamokuCode = v; }
    public String getShishoKamokuName() { return shishoKamokuName; }
    public void setShishoKamokuName(String v) { this.shishoKamokuName = v; }
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
