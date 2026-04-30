package jp.co.btm.irl.rlr.rg004.dto.item;

/**
 * 市場性与信科目明細の1行分データ
 * <p>市場性与信科目明細1〜10で共通の構造。キーは科目コード。</p>
 */
public class MarketSubjectMeisai {

    /** 科目コード（業務名。市場性与信の科目種別を識別するキー） */
    private String kamokuCode;

    /** 指定月末残高 */
    private Long getsumatsuZandaka;

    /** 指定月末極度額 */
    private Long kyodogaku;

    /** 本件後与信額 */
    private Long honkengoZandaka;

    /** 当月増減額（計算結果） */
    private Long tougetsZougen;

    public String getKamokuCode() { return kamokuCode; }
    public void setKamokuCode(String v) { this.kamokuCode = v; }
    public Long getGetsumatsuZandaka() { return getsumatsuZandaka; }
    public void setGetsumatsuZandaka(Long v) { this.getsumatsuZandaka = v; }
    public Long getKyodogaku() { return kyodogaku; }
    public void setKyodogaku(Long v) { this.kyodogaku = v; }
    public Long getHonkengoZandaka() { return honkengoZandaka; }
    public void setHonkengoZandaka(Long v) { this.honkengoZandaka = v; }
    public Long getTougetsZougen() { return tougetsZougen; }
    public void setTougetsZougen(Long v) { this.tougetsZougen = v; }
}
