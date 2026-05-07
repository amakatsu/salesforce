package jp.co.btm.irl.rlr.rg004.dto.item;

/**
 * 一般与信の1行分データ（種別キー付き）
 * <p>画面の一般与信タブの1行に対応。明細行・合計行・小計行を同一構造で保持する。
 * 種別キー（kamokuCode）で行の意味を識別する。</p>
 *
 * <p>種別キー例:
 * 明細: "kashitsuke_meisai_01"〜"kashitsuke_meisai_12"
 * 合計: "kashitsuke_shote_total", "gaitame_total", "shisho_total",
 *       "onbalance_total", "offbalance_total",
 *       "gendo_sannyu_total", "gendo_fusannyu_total",
 *       "ippan_yoshin_total", "gendo_loan_total"
 * 小計: "yusyu_shototal", "yunyu_shototal"
 * 個別: "uchienka", "shibosai", "kyoho_gashi", "sonota_ippan_yoshin",
 *       "tokutei_yoshin_total", "tokutei_yoshin_1", "tokutei_yoshin_2",
 *       "hl_shinyo_fusannyu"
 * 外為明細: "shitei_gai_lc", "dp_da", "gaika_kitte", "kasidashi_yusyu",
 *          "yunyu_lc", "usance", "lg", "kasidashi_yunyu", "kosho_lc", "usan_shift"
 * 支払承諾: "shisho_ippan", "shisho_ippan_gaita", "shisho_dairi_kasitsuki"
 * </p>
 */
public class IppanYoshinRow {

    /** 種別キー（行の業務的な意味を識別する） */
    private String kamokuCode;

    /** 科目名（表示用） */
    private String kamokuName;

    /** 極度額 */
    private Long kyodogaku;

    /** 本件後残高 */
    private Long honkengoZandaka;

    /** 指定月末残高 */
    private Long getsumatsuZandaka;

    /** 実勢現在残高 */
    private Long jisseiZandaka;

    /** 当月増減額 */
    private Long tougetsZougen;

    /** 分類コード */
    private String bunruiCode;

    /** 期日 */
    private String kijitsu;

    /** 利率 */
    private String riritsu;

    /** 補正値 */
    private Long hoseiValue;

    /** 禀査番号 */
    private String rinsaNo;

    public String getKamokuCode() { return kamokuCode; }
    public void setKamokuCode(String v) { this.kamokuCode = v; }
    public String getKamokuName() { return kamokuName; }
    public void setKamokuName(String v) { this.kamokuName = v; }
    public Long getKyodogaku() { return kyodogaku; }
    public void setKyodogaku(Long v) { this.kyodogaku = v; }
    public Long getHonkengoZandaka() { return honkengoZandaka; }
    public void setHonkengoZandaka(Long v) { this.honkengoZandaka = v; }
    public Long getGetsumatsuZandaka() { return getsumatsuZandaka; }
    public void setGetsumatsuZandaka(Long v) { this.getsumatsuZandaka = v; }
    public Long getJisseiZandaka() { return jisseiZandaka; }
    public void setJisseiZandaka(Long v) { this.jisseiZandaka = v; }
    public Long getTougetsZougen() { return tougetsZougen; }
    public void setTougetsZougen(Long v) { this.tougetsZougen = v; }
    public String getBunruiCode() { return bunruiCode; }
    public void setBunruiCode(String v) { this.bunruiCode = v; }
    public String getKijitsu() { return kijitsu; }
    public void setKijitsu(String v) { this.kijitsu = v; }
    public String getRiritsu() { return riritsu; }
    public void setRiritsu(String v) { this.riritsu = v; }
    public Long getHoseiValue() { return hoseiValue; }
    public void setHoseiValue(Long v) { this.hoseiValue = v; }
    public String getRinsaNo() { return rinsaNo; }
    public void setRinsaNo(String v) { this.rinsaNo = v; }
}
