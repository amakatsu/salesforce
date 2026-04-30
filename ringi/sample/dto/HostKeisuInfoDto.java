package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * ホスト計数情報DTO
 * <p>ホストから取得した計数情報を保持する。イミュータブル（読み取り専用）。
 * 画面タブ/セクション単位で構造化する。
 * 横軸が同じ行は全てListで管理し、合計行もListの1要素として持つ。</p>
 */
public class HostKeisuInfoDto {

    /** 一般与信の全行（明細+合計+小計+個別科目） */
    private final List<IppanYoshinRow> ippanYoshinRowList;

    /** 一般与信1タブの金額単位 */
    private final String ippanYoshinTaniMsg;

    /** 担保の全行（明細+小計+合計+補正値+裸与信） */
    private final List<TanpoItem> tanpoItemList;

    /** 規定・優良担保・商手(規定値) */
    private final Long kiteiYuryoTanpoShote;

    /** 裸与信対象与信合計 */
    private final Long hadakaYoshinTaishoTotal;

    /** 市場性与信科目明細（10行） */
    private final List<MarketSubjectMeisai> shijoKamokuMeisaiList;

    /** 市場性与信_限度算入与信合計(本件後与信額) */
    private final Long shijoGendoSannyuHonkengoZandaka;

    /** 市場性与信1タブの金額単位 */
    private final String shijoYoshinTaniMsg;

    /** 簡易CF1 */
    private final Long kanICf1;

    /** 簡易CF2 */
    private final Long kanICf2;

    /** 簡易CF3 */
    private final Long kanICf3;

    public HostKeisuInfoDto(
            List<IppanYoshinRow> ippanYoshinRowList,
            String ippanYoshinTaniMsg,
            List<TanpoItem> tanpoItemList,
            Long kiteiYuryoTanpoShote,
            Long hadakaYoshinTaishoTotal,
            List<MarketSubjectMeisai> shijoKamokuMeisaiList,
            Long shijoGendoSannyuHonkengoZandaka,
            String shijoYoshinTaniMsg,
            Long kanICf1, Long kanICf2, Long kanICf3) {
        this.ippanYoshinRowList = ippanYoshinRowList;
        this.ippanYoshinTaniMsg = ippanYoshinTaniMsg;
        this.tanpoItemList = tanpoItemList;
        this.kiteiYuryoTanpoShote = kiteiYuryoTanpoShote;
        this.hadakaYoshinTaishoTotal = hadakaYoshinTaishoTotal;
        this.shijoKamokuMeisaiList = shijoKamokuMeisaiList;
        this.shijoGendoSannyuHonkengoZandaka = shijoGendoSannyuHonkengoZandaka;
        this.shijoYoshinTaniMsg = shijoYoshinTaniMsg;
        this.kanICf1 = kanICf1;
        this.kanICf2 = kanICf2;
        this.kanICf3 = kanICf3;
    }

    public List<IppanYoshinRow> getIppanYoshinRowList() { return ippanYoshinRowList; }
    public String getIppanYoshinTaniMsg() { return ippanYoshinTaniMsg; }
    public List<TanpoItem> getTanpoItemList() { return tanpoItemList; }
    public Long getKiteiYuryoTanpoShote() { return kiteiYuryoTanpoShote; }
    public Long getHadakaYoshinTaishoTotal() { return hadakaYoshinTaishoTotal; }
    public List<MarketSubjectMeisai> getShijoKamokuMeisaiList() { return shijoKamokuMeisaiList; }
    public Long getShijoGendoSannyuHonkengoZandaka() { return shijoGendoSannyuHonkengoZandaka; }
    public String getShijoYoshinTaniMsg() { return shijoYoshinTaniMsg; }
    public Long getKanICf1() { return kanICf1; }
    public Long getKanICf2() { return kanICf2; }
    public Long getKanICf3() { return kanICf3; }
}
