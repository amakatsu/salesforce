package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 科目明細当月増減額計算結果DTO
 * <p>市場性与信10行分の当月増減額と簡易CF項目を保持する。
 * 10行は同構造の繰り返しなのでList&lt;MarketSubjectMeisai&gt;で管理する。</p>
 */
public class SubjectMonthlyChangeCalcResultDto {

    /** 科目明細当月増減額（10行、同構造の繰り返し） // 旧: F_KMKDLTZGG_1〜10 */
    private List<MarketSubjectMeisai> subjectMonthlyChangeList;

    /** 簡易CF1 // 旧: F_KSKBTDLCF1 */
    private String simpleCf1;

    /** 簡易CF2 // 旧: F_KSKBTDLCF2 */
    private String simpleCf2;

    /** 簡易CF3 // 旧: F_KSKBTDLCF3 */
    private String simpleCf3;

    public List<MarketSubjectMeisai> getSubjectMonthlyChangeList() { return subjectMonthlyChangeList; }
    public void setSubjectMonthlyChangeList(List<MarketSubjectMeisai> v) { this.subjectMonthlyChangeList = v; }
    public String getSimpleCf1() { return simpleCf1; }
    public void setSimpleCf1(String v) { this.simpleCf1 = v; }
    public String getSimpleCf2() { return simpleCf2; }
    public void setSimpleCf2(String v) { this.simpleCf2 = v; }
    public String getSimpleCf3() { return simpleCf3; }
    public void setSimpleCf3(String v) { this.simpleCf3 = v; }
}
