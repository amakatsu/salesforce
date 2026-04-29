package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 市場性与信 科目明細の1行分データ
 * <p>市場性与信科目明細10行分の繰り返し構造。</p>
 */
public class MarketSubjectMeisai {

    /** 科目コード（業務的な識別キー） 例: "shijo_kamoku_01" 等 */
    private String kamokuCode;

    /** 指定月末残高 // 旧: F_MEND_ZAN_{N} */
    private Long monthEndBalance;

    /** 指定月末極度額 // 旧: F_LMT_{N} */
    private Long creditLimit;

    /** 本件後与信額 // 旧: F_HONAF_ZAN_{N} */
    private Long postLoanAmount;

    /** 当月増減額（計算結果） // 旧: F_KMKDLTZGG_{N} */
    private Long monthlyChange;

    public String getKamokuCode() { return kamokuCode; }
    public void setKamokuCode(String v) { this.kamokuCode = v; }
    public Long getMonthEndBalance() { return monthEndBalance; }
    public void setMonthEndBalance(Long v) { this.monthEndBalance = v; }
    public Long getCreditLimit() { return creditLimit; }
    public void setCreditLimit(Long v) { this.creditLimit = v; }
    public Long getPostLoanAmount() { return postLoanAmount; }
    public void setPostLoanAmount(Long v) { this.postLoanAmount = v; }
    public Long getMonthlyChange() { return monthlyChange; }
    public void setMonthlyChange(Long v) { this.monthlyChange = v; }
}
