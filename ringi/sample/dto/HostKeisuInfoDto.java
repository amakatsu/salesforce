package jp.co.btm.irl.rlr.rg004.dto;

/**
 * ホスト計数情報DTO
 * <p>ホストから取得した計数情報を横持ちで保持する。イミュータブル。
 * 一般与信状況の各項目はGeneralCreditItemで管理する。</p>
 * <p>フィールド数が多いためBuilderパターンでの生成を推奨。</p>
 */
public class HostKeisuInfoDto {

    // 一般与信状況の各行（貸付金・外為・支払承諾等）は
    // KeisuBaseDataDtoと同じGeneralCreditItem構造。
    // ここでは代表的なフィールドのみ記載。

    /** 貸付金・割引合計 // 旧: 配列[V_KEISU_KASHISHO_TOT_BAP] */
    private final GeneralCreditItem kashitsukeTotalItem;

    /** 外為与信合計 // 旧: 配列[V_KEISU_GAITAME_TOT_BAP] */
    private final GeneralCreditItem gaitameTotalItem;

    /** 支払承諾合計 // 旧: 配列[V_KEISU_SHISHO_TOT_BAP] */
    private final GeneralCreditItem shiharaiShodakuTotal;

    /** 本件後引当状況・規定担保合計（規定値） // 旧: F_HIKIATE_KITEITI_TOT */
    private final Long kiteiTanpoTotal;

    /** 本件後引当状況・規定担保合計（時価ベース） // 旧: F_HIKIATE_JIKA_TOT */
    private final Long jikaTanpoTotal;

    /** 裸与信（規定値） */
    private final Long hadakaYoshinKitei;

    /** 裸与信（時価ベース） */
    private final Long hadakaYoshinJika;

    /** 規定・優良担保・商手(規定値) // 旧: F_SUTNTE */
    private final Long standardCollateralBills;

    /** 市場性与信_限度算入与信合計(本件後与信額) // 旧: F_LMTINTL_RN_HONAF_ZAN */
    private final Long marketCreditIncludedTotal;

    /** 裸与信対象与信合計 // 旧: F_STRCRE_TSHO_TOT */
    private final Long nakedCreditTargetTotal;

    // ※ 実装時は全一般与信行（46項目分のGeneralCreditItem）と
    //    保全状況の全明細項目をフィールドとして定義する。
    //    ここではサンプルとして代表フィールドのみ記載。

    public HostKeisuInfoDto(GeneralCreditItem kashitsukeTotalItem,
                            GeneralCreditItem gaitameTotalItem,
                            GeneralCreditItem shiharaiShodakuTotal,
                            Long kiteiTanpoTotal, Long jikaTanpoTotal,
                            Long hadakaYoshinKitei, Long hadakaYoshinJika,
                            Long standardCollateralBills,
                            Long marketCreditIncludedTotal,
                            Long nakedCreditTargetTotal) {
        this.kashitsukeTotalItem = kashitsukeTotalItem;
        this.gaitameTotalItem = gaitameTotalItem;
        this.shiharaiShodakuTotal = shiharaiShodakuTotal;
        this.kiteiTanpoTotal = kiteiTanpoTotal;
        this.jikaTanpoTotal = jikaTanpoTotal;
        this.hadakaYoshinKitei = hadakaYoshinKitei;
        this.hadakaYoshinJika = hadakaYoshinJika;
        this.standardCollateralBills = standardCollateralBills;
        this.marketCreditIncludedTotal = marketCreditIncludedTotal;
        this.nakedCreditTargetTotal = nakedCreditTargetTotal;
    }

    public GeneralCreditItem getKashitsukeTotalItem() { return kashitsukeTotalItem; }
    public GeneralCreditItem getGaitameTotalItem() { return gaitameTotalItem; }
    public GeneralCreditItem getShiharaiShodakuTotal() { return shiharaiShodakuTotal; }
    public Long getKiteiTanpoTotal() { return kiteiTanpoTotal; }
    public Long getJikaTanpoTotal() { return jikaTanpoTotal; }
    public Long getHadakaYoshinKitei() { return hadakaYoshinKitei; }
    public Long getHadakaYoshinJika() { return hadakaYoshinJika; }
    public Long getStandardCollateralBills() { return standardCollateralBills; }
    public Long getMarketCreditIncludedTotal() { return marketCreditIncludedTotal; }
    public Long getNakedCreditTargetTotal() { return nakedCreditTargetTotal; }
}
