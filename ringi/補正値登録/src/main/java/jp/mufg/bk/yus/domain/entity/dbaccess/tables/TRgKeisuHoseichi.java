package jp.mufg.bk.yus.domain.entity.dbaccess.tables;

/**
 * 計数情報(禀議計数補正値) テーブルの 1 レコードを表す Entity。
 */
public class TRgKeisuHoseichi {

    private String brno;
    private String cmNo;
    private String delFlg;

    private Integer loanDiscTotalCorrectionValue;
    private Integer internalJpyCorrectionValue;
    private Integer forexCreditTotalCorrectionValue;
    private Integer shiShoTotalCorrectionValue;

    private Integer regulationTanpoCorrectionValueRegulationValue;
    private Integer regulationTanpoCorrectionValueJikaBase;

    private String correctionReason;

    private String exclusiveKey;
    private Integer exclusiveCount;

    public String getBrno() {
        return brno;
    }

    public void setBrno(String brno) {
        this.brno = brno;
    }

    public String getCmNo() {
        return cmNo;
    }

    public void setCmNo(String cmNo) {
        this.cmNo = cmNo;
    }

    public String getDelFlg() {
        return delFlg;
    }

    public void setDelFlg(String delFlg) {
        this.delFlg = delFlg;
    }

    public Integer getLoanDiscTotalCorrectionValue() {
        return loanDiscTotalCorrectionValue;
    }

    public void setLoanDiscTotalCorrectionValue(Integer loanDiscTotalCorrectionValue) {
        this.loanDiscTotalCorrectionValue = loanDiscTotalCorrectionValue;
    }

    public Integer getInternalJpyCorrectionValue() {
        return internalJpyCorrectionValue;
    }

    public void setInternalJpyCorrectionValue(Integer internalJpyCorrectionValue) {
        this.internalJpyCorrectionValue = internalJpyCorrectionValue;
    }

    public Integer getForexCreditTotalCorrectionValue() {
        return forexCreditTotalCorrectionValue;
    }

    public void setForexCreditTotalCorrectionValue(Integer forexCreditTotalCorrectionValue) {
        this.forexCreditTotalCorrectionValue = forexCreditTotalCorrectionValue;
    }

    public Integer getShiShoTotalCorrectionValue() {
        return shiShoTotalCorrectionValue;
    }

    public void setShiShoTotalCorrectionValue(Integer shiShoTotalCorrectionValue) {
        this.shiShoTotalCorrectionValue = shiShoTotalCorrectionValue;
    }

    public Integer getRegulationTanpoCorrectionValueRegulationValue() {
        return regulationTanpoCorrectionValueRegulationValue;
    }

    public void setRegulationTanpoCorrectionValueRegulationValue(Integer regulationTanpoCorrectionValueRegulationValue) {
        this.regulationTanpoCorrectionValueRegulationValue = regulationTanpoCorrectionValueRegulationValue;
    }

    public Integer getRegulationTanpoCorrectionValueJikaBase() {
        return regulationTanpoCorrectionValueJikaBase;
    }

    public void setRegulationTanpoCorrectionValueJikaBase(Integer regulationTanpoCorrectionValueJikaBase) {
        this.regulationTanpoCorrectionValueJikaBase = regulationTanpoCorrectionValueJikaBase;
    }

    public String getCorrectionReason() {
        return correctionReason;
    }

    public void setCorrectionReason(String correctionReason) {
        this.correctionReason = correctionReason;
    }

    public String getExclusiveKey() {
        return exclusiveKey;
    }

    public void setExclusiveKey(String exclusiveKey) {
        this.exclusiveKey = exclusiveKey;
    }

    public Integer getExclusiveCount() {
        return exclusiveCount;
    }

    public void setExclusiveCount(Integer exclusiveCount) {
        this.exclusiveCount = exclusiveCount;
    }
}
