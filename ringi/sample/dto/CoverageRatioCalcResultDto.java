package jp.co.btm.irl.rlr.rg004.dto;

/**
 * 保全率計算結果DTO
 * <p>保全率（%）・総合与信・総合信用の計算結果を保持する。
 * 各項目の意味が異なるため全て個別フィールド。</p>
 */
public class CoverageRatioCalcResultDto {

    /** 保全率・金額単位（「千円」「百万円」「億円」のいずれか） */
    private String hozenTaniMsg;

    /** 保全率・限度算入一般与信（単位変換後） */
    private String hozenIppanYoshin;

    /** 保全率・限度算入市場性与信（単位変換後） */
    private String hozenShijoYoshin;

    /** 保全率・規定担保合計（単位変換後） */
    private String hozenKiteiTanpo;

    /** 保全率・保全率（小数点第2位まで、上限999.99） */
    private String hozenHozenritsu;

    /** 保全率・総合与信 */
    private String hozenSogoYoshin;

    /** 保全率・総合信用 */
    private String hozenSogoShinyo;

    public String getHozenTaniMsg() { return hozenTaniMsg; }
    public void setHozenTaniMsg(String v) { this.hozenTaniMsg = v; }
    public String getHozenIppanYoshin() { return hozenIppanYoshin; }
    public void setHozenIppanYoshin(String v) { this.hozenIppanYoshin = v; }
    public String getHozenShijoYoshin() { return hozenShijoYoshin; }
    public void setHozenShijoYoshin(String v) { this.hozenShijoYoshin = v; }
    public String getHozenKiteiTanpo() { return hozenKiteiTanpo; }
    public void setHozenKiteiTanpo(String v) { this.hozenKiteiTanpo = v; }
    public String getHozenHozenritsu() { return hozenHozenritsu; }
    public void setHozenHozenritsu(String v) { this.hozenHozenritsu = v; }
    public String getHozenSogoYoshin() { return hozenSogoYoshin; }
    public void setHozenSogoYoshin(String v) { this.hozenSogoYoshin = v; }
    public String getHozenSogoShinyo() { return hozenSogoShinyo; }
    public void setHozenSogoShinyo(String v) { this.hozenSogoShinyo = v; }
}
