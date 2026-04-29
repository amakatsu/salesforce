package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 一般与信状況計算結果DTO
 * <p>補正値適用・合計積み上げ・当月増減額計算の結果を横持ちで保持する。
 * 各項目はGeneralCreditItemで極度額・本件後残高・当月増減額等を一括管理する。</p>
 */
public class GeneralCreditCalcResultDto {

    // 計算結果は KeisuBaseDataDto と同じ構造の GeneralCreditItem で保持する。
    // 補正適用後・再計算後の値が設定される。

    /** 貸付金・割引合計（補正適用後） */
    private GeneralCreditItem kashitsukeTotalItem;

    /** （内円貨）（補正適用後） */
    private GeneralCreditItem uchienkaItem;

    /** 外為与信合計（補正適用後） */
    private GeneralCreditItem gaitameTotalItem;

    /** 支払承諾合計（補正適用後） */
    private GeneralCreditItem shiharaiShodakuTotal;

    /** オンバランス合計（再計算後） */
    private GeneralCreditItem onBalanceTotal;

    /** オフバランス合計 */
    private GeneralCreditItem offBalanceTotal;

    /** 限度算入与信合計_極度額（再計算後） */
    private Long includedCreditLimitTotal;

    /** 限度算入与信合計_本件後残高（再計算後） */
    private Long includedPostLoanBalanceTotal;

    /** 一般与信合計（再計算後） */
    private GeneralCreditItem ippanYoshinTotal;

    /** 特定与信合計（本件後残高のみ） */
    private Long tokuteiYoshinTotal;

    /** 限度算入与信合計_当月増減額 */
    private Long includedMonthlyChangeTotal;

    public GeneralCreditItem getKashitsukeTotalItem() { return kashitsukeTotalItem; }
    public void setKashitsukeTotalItem(GeneralCreditItem v) { this.kashitsukeTotalItem = v; }
    public GeneralCreditItem getUchienkaItem() { return uchienkaItem; }
    public void setUchienkaItem(GeneralCreditItem v) { this.uchienkaItem = v; }
    public GeneralCreditItem getGaitameTotalItem() { return gaitameTotalItem; }
    public void setGaitameTotalItem(GeneralCreditItem v) { this.gaitameTotalItem = v; }
    public GeneralCreditItem getShiharaiShodakuTotal() { return shiharaiShodakuTotal; }
    public void setShiharaiShodakuTotal(GeneralCreditItem v) { this.shiharaiShodakuTotal = v; }
    public GeneralCreditItem getOnBalanceTotal() { return onBalanceTotal; }
    public void setOnBalanceTotal(GeneralCreditItem v) { this.onBalanceTotal = v; }
    public GeneralCreditItem getOffBalanceTotal() { return offBalanceTotal; }
    public void setOffBalanceTotal(GeneralCreditItem v) { this.offBalanceTotal = v; }
    public Long getIncludedCreditLimitTotal() { return includedCreditLimitTotal; }
    public void setIncludedCreditLimitTotal(Long v) { this.includedCreditLimitTotal = v; }
    public Long getIncludedPostLoanBalanceTotal() { return includedPostLoanBalanceTotal; }
    public void setIncludedPostLoanBalanceTotal(Long v) { this.includedPostLoanBalanceTotal = v; }
    public GeneralCreditItem getIppanYoshinTotal() { return ippanYoshinTotal; }
    public void setIppanYoshinTotal(GeneralCreditItem v) { this.ippanYoshinTotal = v; }
    public Long getTokuteiYoshinTotal() { return tokuteiYoshinTotal; }
    public void setTokuteiYoshinTotal(Long v) { this.tokuteiYoshinTotal = v; }
    public Long getIncludedMonthlyChangeTotal() { return includedMonthlyChangeTotal; }
    public void setIncludedMonthlyChangeTotal(Long v) { this.includedMonthlyChangeTotal = v; }
}
