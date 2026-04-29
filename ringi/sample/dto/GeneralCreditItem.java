package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 一般与信状況の1行分データ（横持ち）
 * <p>旧システムでは配列インデックスで管理されていた各項目を、業務名フィールドで保持する。</p>
 */
public class GeneralCreditItem {

    /** 科目コード（業務的な識別キー） 例: "kashitsuke_01", "kashitsuke_02" 等 // 旧: 配列インデックス */
    private String kamokuCode;

    /** 科目・適用（ラベル） // 旧: F_KMK_RMT[i] */
    private String subjectLabel;

    /** 極度額 // 旧: F_LMT[i] */
    private Long creditLimit;

    /** 指定月末残高 // 旧: F_MEND_ZAN[i] */
    private Long monthEndBalance;

    /** 当月増減額 // 旧: F_IPNYSNDLTZGG[i] */
    private Long monthlyChange;

    /** 本件後残高 // 旧: F_HONAF_ZAN[i] */
    private Long postLoanBalance;

    /** 実勢現在残高 // 旧: F_JISKSN[i] */
    private Long actualBalance;

    /** 補正値 // 旧: F_HOSCH[i] */
    private Long correctionValue;

    public String getKamokuCode() { return kamokuCode; }
    public void setKamokuCode(String v) { this.kamokuCode = v; }
    public String getSubjectLabel() { return subjectLabel; }
    public void setSubjectLabel(String v) { this.subjectLabel = v; }
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
    public Long getCorrectionValue() { return correctionValue; }
    public void setCorrectionValue(Long v) { this.correctionValue = v; }
}
