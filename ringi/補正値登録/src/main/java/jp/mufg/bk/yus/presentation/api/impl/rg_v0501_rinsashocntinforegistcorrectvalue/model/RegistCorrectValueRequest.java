package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;

/** 計数情報 補正値登録 API のリクエスト Body。 */
public class RegistCorrectValueRequest {

    @NotNull(message = "店番は必須です")
    @Pattern(regexp = "[0-9]{3}", message = "店番は 3 桁の数字で入力してください")
    private String brNo;

    @NotNull(message = "取引先番号は必須です")
    @Pattern(regexp = "[0-9]{7}", message = "取引先番号は 7 桁の数字で入力してください")
    private String cmNo;

    @PositiveOrZero(message = "貸付金・割引合計（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "貸付金・割引合計（補正値）は整数 7 桁以内で入力してください")
    private Integer loanDiscTotalCorrectionValue;

    @PositiveOrZero(message = "内円貨（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "内円貨（補正値）は整数 7 桁以内で入力してください")
    private Integer internalJpyCorrectionValue;

    @PositiveOrZero(message = "外為与信合計（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "外為与信合計（補正値）は整数 7 桁以内で入力してください")
    private Integer forexCreditTotalCorrectionValue;

    @PositiveOrZero(message = "支払承諾合計（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "支払承諾合計（補正値）は整数 7 桁以内で入力してください")
    private Integer shiShoTotalCorrectionValue;

    @PositiveOrZero(message = "規定担保（規定値）（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "規定担保（規定値）（補正値）は整数 7 桁以内で入力してください")
    private Integer regulationTanpoCorrectionValueRegulationValue;

    @PositiveOrZero(message = "規定担保（時価ベース）（補正値）は 0 以上で入力してください")
    @Digits(integer = 7, fraction = 0, message = "規定担保（時価ベース）（補正値）は整数 7 桁以内で入力してください")
    private Integer regulationTanpoCorrectionValueJikaBase;

    // 仕様は ByteLength 0〜100 だが Bean Validation 標準にバイト長制約が無いため文字数で代替。
    @Size(max = 100, message = "補正理由は 100 文字以内で入力してください")
    private String correctionReason;

    @NotNull(message = "排他ロック情報は必須です")
    @Valid
    private LockInfo lockInfo;

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

    public void setRegulationTanpoCorrectionValueRegulationValue(
            Integer regulationTanpoCorrectionValueRegulationValue) {
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

    public LockInfo getLockInfo() {
        return lockInfo;
    }

    public void setLockInfo(LockInfo lockInfo) {
        this.lockInfo = lockInfo;
    }
}
