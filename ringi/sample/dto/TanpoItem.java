package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 担保情報の1項目分データ（種別キー付き）
 * <p>規定担保・規定外担保の各明細を種別コードで識別する。
 * 規定値と時価ベースの2種類の金額を保持する。</p>
 */
public class TanpoItem {

    /** 担保種別コード（識別キー） 例: "YOKIN", "SHOTE", "TANTE", "YUSHO" 等 */
    private String tanpoShubetsuCode;

    /** 担保種別名 例: "預金", "商手", "担手", "有証" 等 */
    private String tanpoShubetsuName;

    /** 担保区分 例: "KITEI_YURYO", "KITEI_IPPAN", "KITEI_SONOTA", "KITEIGAI_YURYO" 等 */
    private String tanpoKubun;

    /** 金額（規定値） */
    private Long amountStandard;

    /** 金額（時価ベース） */
    private Long amountMarket;

    public String getTanpoShubetsuCode() { return tanpoShubetsuCode; }
    public void setTanpoShubetsuCode(String v) { this.tanpoShubetsuCode = v; }
    public String getTanpoShubetsuName() { return tanpoShubetsuName; }
    public void setTanpoShubetsuName(String v) { this.tanpoShubetsuName = v; }
    public String getTanpoKubun() { return tanpoKubun; }
    public void setTanpoKubun(String v) { this.tanpoKubun = v; }
    public Long getAmountStandard() { return amountStandard; }
    public void setAmountStandard(Long v) { this.amountStandard = v; }
    public Long getAmountMarket() { return amountMarket; }
    public void setAmountMarket(Long v) { this.amountMarket = v; }
}
