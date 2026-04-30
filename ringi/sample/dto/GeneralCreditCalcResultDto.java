package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 一般与信状況計算結果DTO
 * <p>補正値適用・合計積み上げ・当月増減額計算の結果を保持する。
 * 明細行・合計行・小計行を同一構造のListで管理する。個別フィールドは持たない。</p>
 */
public class GeneralCreditCalcResultDto {

    /**
     * 一般与信の全行（明細+合計+小計+個別科目、補正適用・再計算後の値）
     * <p>種別キー: kamokuCode で行を識別する。
     * 合計行（例: "ippan_yoshin_total"）も明細行と同じ構造の1要素。</p>
     */
    private List<IppanYoshinRow> ippanYoshinRowList;

    public List<IppanYoshinRow> getIppanYoshinRowList() { return ippanYoshinRowList; }
    public void setIppanYoshinRowList(List<IppanYoshinRow> v) { this.ippanYoshinRowList = v; }
}
