package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto;

/**
 * 補正値登録機能のサービス入力 DTO。Bean Validation は presentation 層で実施済。
 */
public class ServiceInputDto {

    /** 店番（3 桁、例: "010"）。Service 内で 7 桁サーバー用店番に変換される。 */
    private String brNo;

    /** 取引先番号（7 桁、例: "9019149"）。 */
    private String cmNo;

    private Integer loanDiscTotalCorrectionValue;
    private Integer internalJpyCorrectionValue;
    private Integer forexCreditTotalCorrectionValue;
    private Integer shiShoTotalCorrectionValue;
    private Integer regulationTanpoCorrectionValueRegulationValue;
    private Integer regulationTanpoCorrectionValueJikaBase;
    private String correctionReason;

    /** 排他ロック情報。Service 必須。 */
    private LockInfoDto lockInfo;

    public String getBrNo() {
        return brNo;
    }

    public void setBrNo(String brNo) {
        this.brNo = brNo;
    }

    public String getCmNo() {
        return cmNo;
    }

    public void setCmNo(String cmNo) {
        this.cmNo = cmNo;
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

    public void setRegulationTanpoCorrectionValueRegulationValue(Integer value) {
        this.regulationTanpoCorrectionValueRegulationValue = value;
    }

    public Integer getRegulationTanpoCorrectionValueJikaBase() {
        return regulationTanpoCorrectionValueJikaBase;
    }

    public void setRegulationTanpoCorrectionValueJikaBase(Integer value) {
        this.regulationTanpoCorrectionValueJikaBase = value;
    }

    public String getCorrectionReason() {
        return correctionReason;
    }

    public void setCorrectionReason(String correctionReason) {
        this.correctionReason = correctionReason;
    }

    public LockInfoDto getLockInfo() {
        return lockInfo;
    }

    public void setLockInfo(LockInfoDto lockInfo) {
        this.lockInfo = lockInfo;
    }
}
