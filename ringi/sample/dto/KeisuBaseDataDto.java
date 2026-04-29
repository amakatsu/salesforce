package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 計数ベースデータDTO
 * <p>ホスト計数情報と顧客財務関連データをマージした計算用ベースデータ。
 * 意味の異なる項目は個別フィールド、同構造の繰り返し明細はListで管理する。</p>
 */
public class KeisuBaseDataDto {

    // ========================================
    // 一般与信状況 — 貸付金・割引明細（12行）
    // ========================================

    /** 貸付金・割引合計 // 旧: [V_KEISU_KASHISHO_TOT_BAP] */
    private GeneralCreditItem kashitsukeTotalItem;

    /** （内円貨） // 旧: [V_KEISU_UCHIENKA_BAP] */
    private GeneralCreditItem uchienkaItem;

    /** 貸付金明細（12行、同構造の繰り返し） // 旧: [V_KEISU_KASHISHO_MEISAI1_BAP]〜[MEISAI12_BAP] */
    private List<GeneralCreditItem> kashitsukeMeisaiList;

    // ========================================
    // 一般与信状況 — 外為与信
    // ========================================

    /** 外為与信明細（12行、同構造の繰り返し。種別キー: gaitameKamokuCode） */
    private List<GaitameMeisai> gaitameMeisaiList;

    /** 外為与信合計（計算結果） */
    private GeneralCreditItem gaitameTotalItem;

    // ========================================
    // 一般与信状況 — 支払承諾
    // ========================================

    /** 支払承諾明細（同構造の繰り返し。種別キー: shishoKamokuCode） */
    private List<ShiharaiShodakuMeisai> shiharaiShodakuMeisaiList;

    /** 支払承諾合計（計算結果） */
    private GeneralCreditItem shiharaiShodakuTotal;

    // ========================================
    // 一般与信状況 — その他・合計
    // ========================================

    /** 私募債 // 旧: [V_KEISU_SHIBOSAI_BAP] */
    private GeneralCreditItem shibosai;

    /** 協保貸 // 旧: [V_KEISU_KYOHOGASHI_BAP] */
    private GeneralCreditItem kyohoGashi;

    /** その他一般与信 // 旧: [V_KEISU_IPNYSSNT_BAP] */
    private GeneralCreditItem sonotaIppanYoshin;

    /** 限度算入ローン合計 // 旧: [V_KEISU_GENDOLOAN_TOT_BAP] */
    private GeneralCreditItem gendoLoanTotal;

    /** 内 HL信用不算入 */
    private GeneralCreditItem hlFusannyu;

    /** オンバランス合計 // 旧: [V_KEISU_ONBALANCE_TOT_BAP] */
    private GeneralCreditItem onBalanceTotal;

    /** オフバランス合計 // 旧: [V_KEISU_OFFBALANCE_TOT_BAP] */
    private GeneralCreditItem offBalanceTotal;

    /** 限度不算入与信合計 // 旧: [V_KEISU_GNDFUSAN_TOT_BAP] */
    private GeneralCreditItem gendoFusannyuTotal;

    /** 年金転貸 */
    private GeneralCreditItem nenkinTentai;

    /** 指定L/C小切手 */
    private GeneralCreditItem shiteiLcKogitte;

    /** L/G（限度不算入） */
    private GeneralCreditItem gendoFusannyuLg;

    /** 一般与信合計 // 旧: [V_KEISU_IPPANYSN_TOT_BAP] */
    private GeneralCreditItem ippanYoshinTotal;

    /** 特定与信合計 // 旧: [V_KEISU_SONOTA_TOT_BAP] */
    private GeneralCreditItem tokuteiYoshinTotal;

    /** 特定与信1 // 旧: [V_KEISU_SONOTA_YSN1_BAP] */
    private GeneralCreditItem tokuteiYoshin1;

    /** 特定与信2 // 旧: [V_KEISU_SONOTA_YSN2_BAP] */
    private GeneralCreditItem tokuteiYoshin2;

    // ========================================
    // 限度算入与信合計
    // ========================================

    /** 限度算入与信合計_極度額 // 旧: F_LMT_TOT[V_KEISU_GENDOSAN_TOT_BAP] */
    private Long includedCreditLimitTotal;

    /** 限度算入与信合計_本件後残高 // 旧: F_HONAF_ZAN_TOT[V_KEISU_GENDOSAN_TOT_BAP] */
    private Long includedPostLoanBalanceTotal;

    // ========================================
    // 本件後引当状況 — 担保明細（同構造の繰り返し、種別キー付き）
    // ========================================

    /** 担保明細（規定・優良/規定・一般/規定・その他/規定外の全明細。種別キー: tanpoShubetsuCode + tanpoKubun） */
    private List<TanpoItem> tanpoItemList;

    // ========================================
    // 本件後引当状況 — 合計・補正値・裸与信
    // ========================================

    /** 規定担保合計（規定値） // 旧: F_HIKIATE_KITEITI_TOT */
    private Long kiteiTanpoTotal;

    /** 規定担保合計（時価ベース） // 旧: F_HIKIATE_JIKA_TOT */
    private Long jikaTanpoTotal;

    /** 規定担保補正値（規定値、DB値を採用） // 旧: [V_KEISU_KTITNP_HOSCH_BAP] */
    private Long kiteiTanpoCorrection;

    /** 規定担保補正値（時価ベース、DB値を採用） */
    private Long jikaTanpoCorrection;

    /** 裸与信（規定値） */
    private Long hadakaYoshinKitei;

    /** 裸与信（時価ベース） */
    private Long hadakaYoshinJika;

    /** 規定・優良担保・商手(規定値) // 旧: F_SUTNTE */
    private Long standardCollateralBills;

    /** 市場性与信_限度算入与信合計(本件後与信額) // 旧: F_LMTINTL_RN_HONAF_ZAN */
    private Long marketCreditIncludedTotal;

    /** 裸与信対象与信合計 // 旧: F_STRCRE_TSHO_TOT */
    private Long nakedCreditTargetTotal;

    /** 内HL信用不算入（本件後残高） */
    private Long hlExcludedPostLoanBalance;

    // ========================================
    // 市場性与信 科目明細（10行）
    // ========================================

    /** 市場性与信 科目明細（10行、同構造の繰り返し） // 旧: F_MEND_ZAN_1〜10, F_LMT_1〜10, F_HONAF_ZAN_1〜10 */
    private List<MarketSubjectMeisai> marketSubjectMeisaiList;

    // ========================================
    // 簡易CF・金額単位
    // ========================================

    /** 簡易CF1 // 旧: F_KSKBTDLCF1 */
    private String simpleCf1;
    /** 簡易CF2 // 旧: F_KSKBTDLCF2 */
    private String simpleCf2;
    /** 簡易CF3 // 旧: F_KSKBTDLCF3 */
    private String simpleCf3;

    /** 一般与信1タブの金額単位 // 旧: F_TANI_MSG_1 */
    private String generalCreditUnitLabel;
    /** 市場性与信1タブの金額単位 // 旧: F_SJOSEIINF_TANI_MSG_1 */
    private String marketCreditUnitLabel;

    // --- getter/setter は全フィールドに対して生成（代表例のみ記載）---

    public GeneralCreditItem getKashitsukeTotalItem() { return kashitsukeTotalItem; }
    public void setKashitsukeTotalItem(GeneralCreditItem v) { this.kashitsukeTotalItem = v; }
    public GeneralCreditItem getUchienkaItem() { return uchienkaItem; }
    public void setUchienkaItem(GeneralCreditItem v) { this.uchienkaItem = v; }
    public List<GeneralCreditItem> getKashitsukeMeisaiList() { return kashitsukeMeisaiList; }
    public void setKashitsukeMeisaiList(List<GeneralCreditItem> v) { this.kashitsukeMeisaiList = v; }
    // ... 以下、全フィールドについて同形式のgetter/setterを定義 ...
    // ※ サンプルとして代表フィールドのみ記載。実装時は全フィールドに生成すること。

    public Long getIncludedCreditLimitTotal() { return includedCreditLimitTotal; }
    public void setIncludedCreditLimitTotal(Long v) { this.includedCreditLimitTotal = v; }
    public Long getIncludedPostLoanBalanceTotal() { return includedPostLoanBalanceTotal; }
    public void setIncludedPostLoanBalanceTotal(Long v) { this.includedPostLoanBalanceTotal = v; }
    public List<TanpoItem> getTanpoItemList() { return tanpoItemList; }
    public void setTanpoItemList(List<TanpoItem> v) { this.tanpoItemList = v; }
    public List<GaitameMeisai> getGaitameMeisaiList() { return gaitameMeisaiList; }
    public void setGaitameMeisaiList(List<GaitameMeisai> v) { this.gaitameMeisaiList = v; }
    public List<ShiharaiShodakuMeisai> getShiharaiShodakuMeisaiList() { return shiharaiShodakuMeisaiList; }
    public void setShiharaiShodakuMeisaiList(List<ShiharaiShodakuMeisai> v) { this.shiharaiShodakuMeisaiList = v; }
    public GeneralCreditItem getGaitameTotalItem() { return gaitameTotalItem; }
    public void setGaitameTotalItem(GeneralCreditItem v) { this.gaitameTotalItem = v; }
    public GeneralCreditItem getShiharaiShodakuTotal() { return shiharaiShodakuTotal; }
    public void setShiharaiShodakuTotal(GeneralCreditItem v) { this.shiharaiShodakuTotal = v; }
    public Long getKiteiTanpoTotal() { return kiteiTanpoTotal; }
    public void setKiteiTanpoTotal(Long v) { this.kiteiTanpoTotal = v; }
    public Long getKiteiTanpoCorrection() { return kiteiTanpoCorrection; }
    public void setKiteiTanpoCorrection(Long v) { this.kiteiTanpoCorrection = v; }
    public Long getHadakaYoshinKitei() { return hadakaYoshinKitei; }
    public void setHadakaYoshinKitei(Long v) { this.hadakaYoshinKitei = v; }
    public Long getStandardCollateralBills() { return standardCollateralBills; }
    public void setStandardCollateralBills(Long v) { this.standardCollateralBills = v; }
    public Long getMarketCreditIncludedTotal() { return marketCreditIncludedTotal; }
    public void setMarketCreditIncludedTotal(Long v) { this.marketCreditIncludedTotal = v; }
    public Long getNakedCreditTargetTotal() { return nakedCreditTargetTotal; }
    public void setNakedCreditTargetTotal(Long v) { this.nakedCreditTargetTotal = v; }
    public Long getHlExcludedPostLoanBalance() { return hlExcludedPostLoanBalance; }
    public void setHlExcludedPostLoanBalance(Long v) { this.hlExcludedPostLoanBalance = v; }
    public List<MarketSubjectMeisai> getMarketSubjectMeisaiList() { return marketSubjectMeisaiList; }
    public void setMarketSubjectMeisaiList(List<MarketSubjectMeisai> v) { this.marketSubjectMeisaiList = v; }
    public String getSimpleCf1() { return simpleCf1; }
    public void setSimpleCf1(String v) { this.simpleCf1 = v; }
    public String getSimpleCf2() { return simpleCf2; }
    public void setSimpleCf2(String v) { this.simpleCf2 = v; }
    public String getSimpleCf3() { return simpleCf3; }
    public void setSimpleCf3(String v) { this.simpleCf3 = v; }
    public String getGeneralCreditUnitLabel() { return generalCreditUnitLabel; }
    public void setGeneralCreditUnitLabel(String v) { this.generalCreditUnitLabel = v; }
    public String getMarketCreditUnitLabel() { return marketCreditUnitLabel; }
    public void setMarketCreditUnitLabel(String v) { this.marketCreditUnitLabel = v; }
}
