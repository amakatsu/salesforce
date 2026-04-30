package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 計数ベースデータDTO
 * <p>ホスト計数情報と顧客財務関連データをマージした計算用ベースデータ。
 * 画面タブ/セクション単位でサブDTOに分割する。
 * 横軸（列構造）が同じ行は全てListで管理し、合計行・小計行もListの1要素として持つ。</p>
 */
public class KeisuBaseDataDto {

    // ========================================
    // 一般与信タブ
    // ========================================

    /**
     * 一般与信の全行（明細+合計+小計+個別科目を全て含む）
     * <p>種別キー: kamokuCode で行を識別する。
     * 合計行（例: "kashitsuke_shote_total"）も明細行と同じ構造の1要素。</p>
     */
    private List<IppanYoshinRow> ippanYoshinRowList;

    /** 一般与信1タブの金額単位 */
    private String ippanYoshinTaniMsg;

    // ========================================
    // 本件後引当状況タブ
    // ========================================

    /**
     * 担保の全行（明細+小計+合計+補正値+裸与信を全て含む）
     * <p>種別キー: tanpoKubun + tanpoShubetsu の複合キーで行を識別する。
     * 合計行（例: tanpoKubun="kitei", tanpoShubetsu="total"）も明細行と同じ構造の1要素。</p>
     */
    private List<TanpoItem> tanpoItemList;

    /** 規定・優良担保・商手(規定値) */
    private Long kiteiYuryoTanpoShote;

    /** 裸与信対象与信合計 */
    private Long hadakaYoshinTaishoTotal;

    // ========================================
    // 市場性与信タブ
    // ========================================

    /**
     * 市場性与信科目明細（10行、同構造の繰り返し）
     * <p>種別キー: kamokuCode で行を識別する。</p>
     */
    private List<MarketSubjectMeisai> shijoKamokuMeisaiList;

    /** 市場性与信_限度算入与信合計(本件後与信額) */
    private Long shijoGendoSannyuHonkengoZandaka;

    /** 市場性与信1タブの金額単位 */
    private String shijoYoshinTaniMsg;

    // ========================================
    // 簡易CF
    // ========================================

    /** 簡易CF1 */
    private Long kanICf1;

    /** 簡易CF2 */
    private Long kanICf2;

    /** 簡易CF3 */
    private Long kanICf3;

    // --- getter/setter ---

    public List<IppanYoshinRow> getIppanYoshinRowList() { return ippanYoshinRowList; }
    public void setIppanYoshinRowList(List<IppanYoshinRow> v) { this.ippanYoshinRowList = v; }
    public String getIppanYoshinTaniMsg() { return ippanYoshinTaniMsg; }
    public void setIppanYoshinTaniMsg(String v) { this.ippanYoshinTaniMsg = v; }
    public List<TanpoItem> getTanpoItemList() { return tanpoItemList; }
    public void setTanpoItemList(List<TanpoItem> v) { this.tanpoItemList = v; }
    public Long getKiteiYuryoTanpoShote() { return kiteiYuryoTanpoShote; }
    public void setKiteiYuryoTanpoShote(Long v) { this.kiteiYuryoTanpoShote = v; }
    public Long getHadakaYoshinTaishoTotal() { return hadakaYoshinTaishoTotal; }
    public void setHadakaYoshinTaishoTotal(Long v) { this.hadakaYoshinTaishoTotal = v; }
    public List<MarketSubjectMeisai> getShijoKamokuMeisaiList() { return shijoKamokuMeisaiList; }
    public void setShijoKamokuMeisaiList(List<MarketSubjectMeisai> v) { this.shijoKamokuMeisaiList = v; }
    public Long getShijoGendoSannyuHonkengoZandaka() { return shijoGendoSannyuHonkengoZandaka; }
    public void setShijoGendoSannyuHonkengoZandaka(Long v) { this.shijoGendoSannyuHonkengoZandaka = v; }
    public String getShijoYoshinTaniMsg() { return shijoYoshinTaniMsg; }
    public void setShijoYoshinTaniMsg(String v) { this.shijoYoshinTaniMsg = v; }
    public Long getKanICf1() { return kanICf1; }
    public void setKanICf1(Long v) { this.kanICf1 = v; }
    public Long getKanICf2() { return kanICf2; }
    public void setKanICf2(Long v) { this.kanICf2 = v; }
    public Long getKanICf3() { return kanICf3; }
    public void setKanICf3(Long v) { this.kanICf3 = v; }
}
