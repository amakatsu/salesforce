package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 担保小計/合計/裸与信の1項目分データ（種別キー付き）
 * <p>規定担保・規定外担保の各小計・合計・裸与信を種別コードで識別する。
 * 規定値と時価ベースのペアで金額を保持する。</p>
 */
public class TanpoShototal {

    /**
     * 種別コード（識別キー）
     * <p>例: "kitei_yuryo_shototal", "kitei_ippan_shototal", "kitei_sonota_shototal",
     * "kitei_total", "kitei_hosei", "hadaka_yoshin",
     * "kiteigai_yuryo_shototal", "kiteigai_ippan_shototal", "kiteigai_sonota", "kiteigai_total"</p>
     */
    private String shubetsu;

    /** 規定値 */
    private Long kiteitiValue;

    /** 時価ベース */
    private Long jikaValue;

    public String getShubetsu() { return shubetsu; }
    public void setShubetsu(String v) { this.shubetsu = v; }
    public Long getKiteitiValue() { return kiteitiValue; }
    public void setKiteitiValue(Long v) { this.kiteitiValue = v; }
    public Long getJikaValue() { return jikaValue; }
    public void setJikaValue(Long v) { this.jikaValue = v; }
}
