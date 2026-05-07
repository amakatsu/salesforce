package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 計数計算結果DTO
 * <p>計数計算サービスの全計算結果を保持する。
 * 一般与信状況・本件後保全状況・科目明細当月増減額・保全率の4つの計算結果DTOを格納する。</p>
 */
public class KeisuCalcResultDto {

    /** 一般与信状況計算結果 */
    private GeneralCreditCalcResultDto generalCreditResult;

    /** 本件後保全状況計算結果 */
    private CollateralStatusCalcResultDto collateralStatusResult;

    /** 科目明細当月増減額計算結果 */
    private SubjectMonthlyChangeCalcResultDto subjectMonthlyChangeResult;

    /** 保全率計算結果 */
    private CoverageRatioCalcResultDto coverageRatioResult;

    public GeneralCreditCalcResultDto getGeneralCreditResult() { return generalCreditResult; }
    public void setGeneralCreditResult(GeneralCreditCalcResultDto v) { this.generalCreditResult = v; }
    public CollateralStatusCalcResultDto getCollateralStatusResult() { return collateralStatusResult; }
    public void setCollateralStatusResult(CollateralStatusCalcResultDto v) { this.collateralStatusResult = v; }
    public SubjectMonthlyChangeCalcResultDto getSubjectMonthlyChangeResult() { return subjectMonthlyChangeResult; }
    public void setSubjectMonthlyChangeResult(SubjectMonthlyChangeCalcResultDto v) { this.subjectMonthlyChangeResult = v; }
    public CoverageRatioCalcResultDto getCoverageRatioResult() { return coverageRatioResult; }
    public void setCoverageRatioResult(CoverageRatioCalcResultDto v) { this.coverageRatioResult = v; }
}
