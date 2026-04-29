package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 本件後保全状況計算結果DTO
 * <p>規定担保・規定外担保の各小計・合計・裸与信を保持する。
 * 小計・合計・裸与信は同構造（規定値+時価ベースのペア）の繰り返しなので
 * List&lt;TanpoShototal&gt;（種別キー付き）で管理する。
 * 担保明細はList&lt;TanpoItem&gt;（担保区分+担保種別キー）で管理する。</p>
 */
public class CollateralStatusCalcResultDto {

    /**
     * 担保明細（規定・規定外の全明細項目）
     * <p>種別キー: tanpoKubun + tanpoShubetsu</p>
     */
    private List<TanpoItem> tanpoItemList;

    /**
     * 担保小計・合計・裸与信（同構造の繰り返し）
     * <p>種別キー(shubetsu):
     * "kitei_yuryo_shototal", "kitei_ippan_fudo_tei", "kitei_ippan_shototal",
     * "kitei_sonota_shototal", "kitei_total", "kitei_hosei",
     * "kiteigai_yuryo_shototal", "kiteigai_ippan_shototal",
     * "kiteigai_sonota", "kiteigai_total", "hadaka_yoshin"</p>
     */
    private List<TanpoShototal> tanpoShototalList;

    public List<TanpoItem> getTanpoItemList() { return tanpoItemList; }
    public void setTanpoItemList(List<TanpoItem> v) { this.tanpoItemList = v; }
    public List<TanpoShototal> getTanpoShototalList() { return tanpoShototalList; }
    public void setTanpoShototalList(List<TanpoShototal> v) { this.tanpoShototalList = v; }
}
