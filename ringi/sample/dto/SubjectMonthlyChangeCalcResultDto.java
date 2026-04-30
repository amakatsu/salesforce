package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 科目明細当月増減額計算結果DTO
 * <p>市場性与信10行分の当月増減額と簡易CF項目を保持する。
 * 10行は同構造の繰り返しなのでList&lt;MarketSubjectMeisai&gt;で管理する。</p>
 */
public class SubjectMonthlyChangeCalcResultDto {

    /** 市場性与信科目明細結果リスト（当月増減額が計算済みの科目明細、10要素） */
    private List<MarketSubjectMeisai> shijoKamokuMeisaiResultList;

    /** 簡易CF1（未設定時はnull） */
    private Long kanICf1;

    /** 簡易CF2（未設定時はnull） */
    private Long kanICf2;

    /** 簡易CF3（未設定時はnull） */
    private Long kanICf3;

    public List<MarketSubjectMeisai> getShijoKamokuMeisaiResultList() { return shijoKamokuMeisaiResultList; }
    public void setShijoKamokuMeisaiResultList(List<MarketSubjectMeisai> v) { this.shijoKamokuMeisaiResultList = v; }
    public Long getKanICf1() { return kanICf1; }
    public void setKanICf1(Long v) { this.kanICf1 = v; }
    public Long getKanICf2() { return kanICf2; }
    public void setKanICf2(Long v) { this.kanICf2 = v; }
    public Long getKanICf3() { return kanICf3; }
    public void setKanICf3(Long v) { this.kanICf3 = v; }
}
