package jp.co.btm.irl.rlr.rg004.dto.item;

/**
 * 担保項目の1行分データ（種別キー付き）
 * <p>引当状況の画面1行に対応。明細行・小計行・合計行・補正値・裸与信を同一構造で保持する。
 * 担保区分+担保種別の複合キーで行の意味を識別する。</p>
 *
 * <p>種別キー例:
 * 明細: tanpoKubun="kitei_yuryo", tanpoShubetsu="yokin" 等
 * 小計: tanpoKubun="kitei_yuryo", tanpoShubetsu="shototal" 等
 * 合計: tanpoKubun="kitei", tanpoShubetsu="total"
 *       tanpoKubun="kiteigai", tanpoShubetsu="total"
 * 補正値: tanpoKubun="kitei", tanpoShubetsu="hosei"
 * 裸与信: tanpoKubun="hadaka", tanpoShubetsu="yoshin"
 * その他: tanpoKubun="kiteigai", tanpoShubetsu="sonota"
 * </p>
 */
public class TanpoItem {

    /** 担保区分（"kitei_yuryo", "kitei_ippan", "kitei_sonota", "kiteigai_yuryo", "kiteigai_ippan", "kitei", "kiteigai", "hadaka"） */
    private String tanpoKubun;

    /** 担保種別（"yokin", "shote", "shototal", "total", "hosei", "yoshin" 等） */
    private String tanpoShubetsu;

    /** 規定値 */
    private Long kiteitiValue;

    /** 時価ベース */
    private Long jikaValue;

    public String getTanpoKubun() { return tanpoKubun; }
    public void setTanpoKubun(String v) { this.tanpoKubun = v; }
    public String getTanpoShubetsu() { return tanpoShubetsu; }
    public void setTanpoShubetsu(String v) { this.tanpoShubetsu = v; }
    public Long getKiteitiValue() { return kiteitiValue; }
    public void setKiteitiValue(Long v) { this.kiteitiValue = v; }
    public Long getJikaValue() { return jikaValue; }
    public void setJikaValue(Long v) { this.jikaValue = v; }
}
