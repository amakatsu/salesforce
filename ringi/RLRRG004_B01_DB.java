/*******************************************************************
 *   システム名    ：融資禀議・個人ローンＢＰＲ
 *   サブシステム名：電子禀議
 *   処理名        ：計数情報ＤＢクラス
 *   処理概要      ：計数情報のＤＢアクセス処理を行う
 *   ファイル名    ：RLRRG004_B01_DB.java
 ******************************************************************/
package jp.co.btm.irl.rlr.rg004;

import java.util.Hashtable;
import java.util.ArrayList;

import com.ibm.jp.wacs.CraftsTrxFolder;
import com.ibm.jp.wacs.WACSSysException;
import com.ibm.jp.wacs.WACSApplException;
import com.ibm.jp.wacs.WACSUser;
import com.ibm.jp.wacs.db.CraftsDBConnector;
import com.ibm.jp.wacs.db.CraftsDBParam;
import com.ibm.jp.wacs.db.CraftsDBResult;

import jp.co.btm.irl.rlr.rg000.IRingi;
import jp.co.btm.irl.rlr.rg000.IRingiMsg;
import jp.co.btm.irl.rlr.rg000.IRingiDB;
import jp.co.btm.irl.rlr.rg000.IRingiItem;
import jp.co.btm.irl.rlr.rg000.IRingiItemKeisu;
import jp.co.btm.irl.rlr.rg000.IRingiItemKentoukai;
import jp.co.btm.irl.rlr.rg000.RLRRGCOM_DB;
import jp.co.btm.irl.rlr.tp000.RLRTPCOM_DaihyoBrnoCif;
import jp.co.btm.irl.rlr.cm000.RLRCMCOM_CalendarWrapper;
import jp.co.btm.irl.rlr.cm000.RLRCMCOM_TenCIFWrapper;
import jp.co.btm.irl.rlt.cf001.RLTCF001_001_R02;
import jp.co.btm.irl.rlt.cf001.RLTCF001_003_R01;
import jp.co.btm.irl.rlr.ci000.IRLRCICOM_GCIFConst;
import jp.co.btm.irl.rlr.ci000.RLRCICOM_GCIFfromAttr;
import jp.co.btm.irl.rlr.rg000.RLRRG004_B01;



public class RLRRG004_B01_DB extends RLRRGCOM_DB
                implements IRingi, IRingiDB, IRingiItem, IRingiItemKeisu,
                                IRLRCICOM_GCIFConst, IRingiMsg {

    private static final int intM12 =  -12;
    private static final int intM5  =  -5;
    private static final int intM2  =  -2;
    private static final int intM1  =  -1;
    private static final int int0   =  0;
    private static final int int1   =  1;
    private static final int int2   =  2;
    private static final int int3   =  3;
    private static final int int4   =  4;
    private static final int int5   =  5;
    private static final int int6   =  6;
    private static final int int7   =  7;
    private static final int int8   =  8;
    private static final int int9   =  9;
    private static final int int10  =  10;
    private static final int int30  =  30;
    private static final long lng0  =  0;
    private static final double dbl0             = 0.0;
    private static final double dbl100           = 100.0;
    private static final String str0             = "0";
    private static final String str1             = "1";

    /**<P> 金額単位取得用SQL </P>*/
    public static final String SQL_CODE_2023 = "rlskk_o2023";

    /**<P> 顧客属性取得用DBResult </P>*/
    private CraftsDBResult rs_o0501 = null;
    /**<P> 取推管理顧客GCIF月次(直近)取得用DBResult </P>*/
    private CraftsDBResult rs_o4051_1 = null;
    /**<P> 取推管理顧客GCIF月次(前年)取得用DBResult </P>*/
    private CraftsDBResult rs_o4051_2 = null;
    /**<P> 取推関係先月次(直近)取得用DBResult </P>*/
    private CraftsDBResult rs_o4053_1 = null;
    /**<P> 取推関係先月次(前年)取得用DBResult </P>*/
    private CraftsDBResult rs_o4053_2 = null;
    /**<P> 銀取(総借入)取得用DBResult </P>*/
    private CraftsDBResult rs_o4181 = null;
    /**<P> 銀取(当行)取得用DBResult </P>*/
    private CraftsDBResult rs_o4182 = null;
    /**<P> 銀取(上位3行)月計数60取得用DBResult </P>*/
    private CraftsDBResult rs_o4183 = null;
    /**<P> 計数情報引当状況取得用DBResult </P>*/
    private CraftsDBResult rs_o4184 = null;
    /**<P> 一般保証明細取得用DBResult </P>*/
    private CraftsDBResult rs_o4185 = null;
    /**<P> 自己査定取得用DBResult </P>*/
    private CraftsDBResult rs_o4186 = null;
    /**<P> 単体財務決算分析(貸借対照表)取得用DBResult </P>*/
    private CraftsDBResult rs_o4187 = null;
    /**<P> 単体財務決算分析(損益計算書･利益処分)取得用DBResult </P>*/
    private CraftsDBResult rs_o4188 = null;
    /**<P> 単体財務決算分析(経営指標)取得用DBResult </P>*/
    private CraftsDBResult rs_o4189 = null;
    /**<P> 単体財務にゅーとん分析指標(直近)取得用DBResult </P>*/
    private CraftsDBResult rs_o4191_1 = null;
    /**<P> 単体財務にゅーとん分析指標(前期)取得用DBResult </P>*/
    private CraftsDBResult rs_o4191_2 = null;
    /**<P> 単体財務にゅーとん分析指標(前々期)取得用DBResult </P>*/
    private CraftsDBResult rs_o4191_3 = null;
    /**<P> 実態BS取得用DBResult </P>*/
    private CraftsDBResult rs_o4192 = null;
    /**<P> 禀議計数補正値取得用DBResult </P>*/
    private CraftsDBResult rs_o4193 = null;
    /**<P> 単体財務取得用DBResult </P>*/
    private CraftsDBResult rs_o4194 = null;
    /**<P> 直近計数案件番号取得用DBResult </P>*/
    private CraftsDBResult rs_o4195 = null;
    /**<P> 名寄せ件数取得用DBResult </P>*/
    private CraftsDBResult rs_o4301 = null;
/*
 * 2007.02.21 Add.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 単体財務決算分析(資金調達運用表)用の定義を追加。
 */
    /**<P> 単体財務決算分析(資金調達運用表)取得用DBResult </P>*/
    private CraftsDBResult rs_o4312 = null;
// 2007.02.21 Add. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/* YC20218-02 Start */
    /**<P> プロパーローン情報取得用DBResult </P>*/
    private CraftsDBResult rs_o4196 = null;
/* YC20218-02 End */

    /**<P> 取推-表示月(FROM) </P>*/
    private String strHyoujiFrom    = V_EMPTY_STRING;
    /**<P> 取推-表示月(TO) </P>*/
    private String strHyoujiTo      = V_EMPTY_STRING;
    /**<P> 取推-前年分表示月(FROM) </P>*/
    private String strHyoujiFromAgo = V_EMPTY_STRING;
    /**<P> 取推-前年分表示月(TO) </P>*/
    private String strHyoujiToAgo   = V_EMPTY_STRING;
    /**<P> 取推-表示月取得用TEMPフィールド </P>*/
    private String strTempYM        = V_EMPTY_STRING;
    /**<P> 取推-データ保有最終月 </P>*/
    private String strHoyuLastMonth = V_EMPTY_STRING;
    /**<P> 取推管理顧客GCIF月次直近データ数 </P>*/
    private int intNowDataNum   = 0;
    /**<P> 取推管理顧客GCIF月次前年データ数 </P>*/
    private int intAgoDataNum   = 0;
    /**<P> 取推関係先月次直近データ数 </P>*/
    private int intGRNowDataNum = 0;
    /**<P> 取推関係先月次前年データ数 </P>*/
    private int intGRAgoDataNum = 0;
    /**<P> 金額単位 </P>*/
    private String strTani      = V_EMPTY_STRING;
    /**<P> 作成日 </P>*/
    private String strMkbi      = V_EMPTY_STRING;
    /**<P> 単体財務取得用決算期 </P>*/
    private String[] strKessankiShutoku = null;

    private String[] strBunruiTemp       = null;
    private String[] strKmkTemp          = null;
    private String[] strKbiTemp          = null;
    private String[] strRtTemp           = null;
    private String[] strMendZanTemp      = null;
    private String[] strGsnlmtHjTemp     = null;
    private String[] strLmtTemp          = null;
    private String[] strIpnysndltzggTemp = null;
    private String[] strHonafZanTemp     = null;
    private String[] strJisksnTemp       = null;
    private String[] strHoschTemp        = null;
// GEC294-C-004 S
    private String[] strRsnoTemp          = null;
// GEC294-C-004 E
    private String[] strHoshoninTemp     = null;

    /**<P>本件後引当状況・合計数</P>*/
//2009/06/22 CHG@R.Matsumura GEC20-C-059 start
//  private static final int intHikiateTotNum = 2;
    private static final int intHikiateTotNum = 3;
//2009/06/22 CHG@R.Matsumura GEC20-C-059 end
    /**<P>本件後引当状況数</P>*/
// 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
//  private static final int intHikiateNum    = 37;
/* YC20218-02 Start */
//  private static final int intHikiateNum    = 38;
    private static final int intHikiateNum    = 39;
/* YC20218-02 End */
// 2005/02/08 CHG M.Kudo END

/* YC20218-02 Start */
    /**<P>規定･一般担保･内HL(抵)(BAP)インデックス</P>*/
    private static final int intKtitnpIptnp1FudoteHloanNum    = 15;
/* YC20218-02 End */

    /**<P>本件後引当状況・規定値・合計</P>*/
    private static final String[] strHikiateKiteitiTot = {
        IRingiItemKeisu.F_KTITNP_TOT1,
        F_KTITNP_HOSCH1,        // 2009/06/22 ADD@R.Matsumura GEC20-C-059
        F_STRCREKITE
    };

/* 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
 * F_KTITNP_YUTNP1_KYKHSHO を追加
 * F_IPTNPM1_GENLC1  を移動
 * F_IPTNPM1_TEGHKN1 を移動
 */
    /**<P>本件後引当状況・規定値</P>*/
    private static final String[] strHikiateKiteiti = {
        F_KTITNP_YUTNP1_SHKEI,
        F_KTITNP_YUTNP1_YOTAN,
        F_SUTNTE1,
        F_KTITNP_YUTNP1_TANTE,
        F_KTITNP_YUTNP1_SCTY,
        F_KTITNP_YUTNP1_KYKHSHO,
        F_KTITNP_YUTNP1_HOSHO,
        F_IPTNPM1_GENLC1,
        F_IPTNPM1_TEGHKN1,
        F_KTITNP_YUTNP1_SUM_FCT,
        F_KTITNP_YUTNP1_SONOTA,
        F_KTITNP_IPTNP1_SHKEI,
        F_KTITNP_IPTNP1_SCTY,
        F_KTITNP_IPTNP1_HOSHO,
        F_KTITNP_IPTNP1_FUDOTE,
/* YC20218-02 Start */
        F_KTITNP_IPTNP1_FUDOTE_HLOAN,
/* YC20218-02 End */
        F_KTITNP_IPTNP1_FUDONE,
//      F_IPTNPM1_GENLC1,
//      F_IPTNPM1_TEGHKN1,
        F_DFHS11,
        F_KTITNP_IPTNP1_SONOTA,
        F_KTITNP_SNTTNP1_SHKEI,
        F_KTITNP_SNTTNP1_SCTY,
        F_KTITNP_SNTTNP1_HOSHO,
        F_DCHSKITE,
        F_KTITNP_SNTTNP1_SONOTA,
        F_KTIGTNP_TOT1,
        F_KTIGTNP_YUTNP1_SHKEI,
        F_KTIGTNP_YUTNP1_YOTAN,
        F_KTIGTNP_YUTNP1_SCTY,
        F_KTIGTNP_YUTNP1_HOSHO,
        F_KTIGTNP_YUTNP1_SONOTA,
        F_KTIGTNP_IPTNP1_SHKEI,
        F_KTIGTNP_IPTNP1_SCTY,
        F_KTIGTNP_IPTNP1_HOSHO,
        F_KTIGTNP_IPTNP1_FUDOTE,
        F_KTIGTNP_IPTNP1_FUDONE,
        F_KTIGTNP_IPTNP1_NYK_HOSKN,
        F_KGIIPBNDKITE,
        F_KTIGTNP_IPTNP1_SONOTA,
        F_KTIGTNP_SNTTNP1_SONOTA
    };
// 2005/02/08 CHG M.Kudo END

    /**<P>本件後引当状況・時価ベース・合計</P>*/
    private static final String[] strHikiateJikaTot = {
        F_KTITNP_TOT2,
        F_KTITNP_HOSCH2,        // 2009/06/22 ADD@R.Matsumura GEC20-C-059
        F_STRCREJIKA
    };

/* 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
 * F_KTITNP_YUTNP2_KYKHSHO を追加
 * F_IPTNPM1_GENLC2  を移動
 * F_IPTNPM1_TEGHKN2 を移動
 */
    /**<P>本件後引当状況・時価ベース</P>*/
    private static final String[] strHikiateJika = {
        F_KTITNP_YUTNP2_SHKEI,
        F_KTITNP_YUTNP2_YOTAN,
        F_SUTNTE2,
        F_KTITNP_YUTNP2_TANTE,
        F_KTITNP_YUTNP2_SCTY,
        F_KTITNP_YUTNP2_KYKHSHO,
        F_KTITNP_YUTNP2_HOSHO,
        F_IPTNPM1_GENLC2,
        F_IPTNPM1_TEGHKN2,
        F_KTITNP_YUTNP2_SUM_FCT,
        F_KTITNP_YUTNP2_SONOTA,
        F_KTITNP_IPTNP2_SHKEI,
        F_KTITNP_IPTNP2_SCTY,
        F_KTITNP_IPTNP2_HOSHO,
        F_KTITNP_IPTNP2_FUDOTE,
/* YC20218-02 Start */
        F_KTITNP_IPTNP2_FUDOTE_HLOAN,
/* YC20218-02 End */
        F_KTITNP_IPTNP2_FUDONE,
//      F_IPTNPM1_GENLC2,
//      F_IPTNPM1_TEGHKN2,
        F_DFHS12,
        F_KTITNP_IPTNP2_SONOTA,
        F_KTITNP_SNTTNP2_SHKEI,
        F_KTITNP_SNTTNP2_SCTY,
        F_KTITNP_SNTTNP2_HOSHO,
        F_KTITNP_SNTTNP2_DHC_DC_HOSHO,
        F_KTITNP_SNTTNP2_SONOTA,
        F_KTIGTNP_TOT2,
        F_KTIGTNP_YUTNP2_SHKEI,
        F_KTIGTNP_YUTNP2_YOTAN,
        F_KTIGTNP_YUTNP2_SCTY,
        F_KTIGTNP_YUTNP2_HOSHO,
        F_KTIGTNP_YUTNP2_SONOTA,
        F_KTIGTNP_IPTNP2_SHKEI,
        F_KGIIPSCTJIKA,
        F_KGIIPHSYJIKA,
        F_KTIGTNP_IPTNP2_FUDOTE,
        F_KTIGTNP_IPTNP2_FUDONE,
        F_KTIGTNP_IPTNP2_NYK_HOSKN,
        F_KGIIPBNDJIKA,
        F_KTIGTNP_IPTNP2_SONOTA,
        F_KTIGTNP_SNTTNP2_SONOTA
    };
// 2005/02/08 CHG M.Kudo END

    /**<P>限度算入与信合計数</P>*/
    private static final int intIppanTotNum = 1;

// 2005/03/11 DEL S.Seimura START (GEC16-C-143-005)
// 使用していないため削除
//  /**<P>一般与信明細開始通番</P>*/
//  private static final int intKmkRmtStart = 4;
//  /**<P>一般与信明細終了通番</P>*/
//  private static final int intKmkRmtEnd   = 15;
//
//  /**<P>一般与信状況明細・分類</P>*/
//  private static final String[] strBunruicd = {
//      F_BNRUICD1,
//      F_BNRUICD2,
//      F_BNRUICD3,
//      F_BNRUICD4,
//      F_BNRUICD5,
//      F_BNRUICD6,
//      F_BNRUICD7,
//      F_BNRUICD8,
//      F_BNRUICD9,
//      F_BNRUICD10,
//      F_BNRUICD11,
//      F_BNRUICD12
//  };
// 2005/03/11 DEL S.Seimura END

    /**<P>一般与信明細数(限度算入合計以外)</P>*/
// 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
//2009/06/22  CHG@R.Matsumura GEC20-C-059 start
//  private static final int intIpnYsnNum      = 44;
//  private static final int intIpnYsnNum      = 45;
/* YC20218-02 Start */
//  private static final int intIpnYsnNum      = 46;
    private static final int intIpnYsnNum      = 47;
/* YC20218-02 End */
//2009/06/22  CHG@R.Matsumura GEC20-C-059 end
// 2005/02/08 CHG M.Kudo END

// 2005/02/08 ADD M.Kudo START (GEC16-C-143-005)
    /**<P>一般与信明細の最大通番数（ＤＢ）</P>*/
//2009/06/22  CHG@R.Matsumura GEC20-C-059 start
//  private static final int V_INSERT_TUNO_MAX = 46;
/* YC20218-02 Start */
//  private static final int V_INSERT_TUNO_MAX = 47;
    private static final int V_INSERT_TUNO_MAX = 48;
/* YC20218-02 End */
//2009/06/22  CHG@R.Matsumura GEC20-C-059 end
// 2005/02/08 ADD M.Kudo END

// 2005/02/08 DEL M.Kudo START (GEC16-C-143-005)
// 使用していないため削除
//  /**<P>その他与信開始通番</P>*/
//  private static final int intSonotaKmkStart = 44;
//  /**<P>その他与信終了通番</P>*/
//  private static final int intSonotaKmkEnd   = 45;
// 2005/02/08 DEL M.Kudo END

// 2005/03/11 DEL S.Seimura START (GEC16-C-143-005)
// 使用していないため削除
//  /**<P>その他与信明細・科目</P>*/
//  private static final String[] strSonotaKmk = {
//      F_KMK_RMT1_SONOTA,
//      F_KMK_RMT2_SONOTA
//  };
// 2005/03/11 DEL S.Seimura END

// 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
//  /**<P>一般与信合計・補正値配列インデックス</P>*/
//  private static final int intHoschIpn       = 0;
//  /**<P>内円貨・補正値配列インデックス</P>*/
//  private static final int intHoschUchi      = 1;
//  /**<P>貿易与信合計・補正値配列インデックス</P>*/
//  private static final int intHoschBoueki    = 14;
//  /**<P>支払承諾合計・補正値配列インデックス</P>*/
//  private static final int intHoschShisho    = 27;
//
//  /**<P>一般与信補正値通番</P>*/
//  private static final int intIpnHoschNum    = 2;
//  /**<P>内円貨補正値通番</P>*/
//  private static final int intUchiHoschNum   = 3;
//  /**<P>貿易与信補正値通番</P>*/
//  private static final int intBouekiHoschNum = 16;
//  /**<P>支払承諾補正値通番</P>*/
//  private static final int intShishoHoschNum = 29;

    /**<P>一般与信合計・補正値配列インデックス</P>*/
    private static final int intHoschIpn       = V_KEISU_KASHISHO_TOT_DB;
    /**<P>内円貨・補正値配列インデックス</P>*/
    private static final int intHoschUchi      = V_KEISU_UCHIENKA_DB;
    /**<P>外為与信合計・補正値配列インデックス</P>*/
    private static final int intHoschBoueki    = V_KEISU_GAITAME_TOT_DB;
    /**<P>支払承諾合計・補正値配列インデックス</P>*/
    private static final int intHoschShisho    = V_KEISU_SHISHO_TOT_DB;

    /**<P>一般与信補正値通番</P>*/
    private static final int intIpnHoschNum    = V_KEISU_KASHISHO_TOT_DB + 2;
    /**<P>内円貨補正値通番</P>*/
    private static final int intUchiHoschNum   = V_KEISU_UCHIENKA_DB + 2;
    /**<P>外為与信補正値通番</P>*/
    private static final int intBouekiHoschNum = V_KEISU_GAITAME_TOT_DB + 2;
    /**<P>支払承諾補正値通番</P>*/
    private static final int intShishoHoschNum = V_KEISU_SHISHO_TOT_DB + 2;
// 2005/02/08 CHG M.Kudo END

//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
     /**<P>規定担保補正値インデックス</P>*/
     private static final int intKiteHosch   = V_KEISU_KTITNP_HOSCH_BAP;
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

    /**<P>保証人数</P>*/
    private static final int intHoshoninNum    = 5;

    /**<P>限度算入与信数</P>*/
    private static final int intGendSannyuNum  = 10;

    /**<P>科目明細(与信科目)</P>*/
    private static final String[] strYsnKndGendo = {
        V_EMPTY_STRING,
        F_YSNKND_1,
        F_YSNKND_2,
        F_YSNKND_3,
        F_YSNKND_4,
        F_YSNKND_5,
        F_YSNKND_6,
        F_YSNKND_7,
        F_YSNKND_8,
        F_YSNKND_9,
        F_YSNKND_10
    };
    /**<P>科目明細(ワーニング情報)</P>*/
    private static final String[] strWrnmsgStdbiGendo = {
        V_EMPTY_STRING,
        F_WRNMSG_STDBI_1,
        F_WRNMSG_STDBI_2,
        F_WRNMSG_STDBI_3,
        F_WRNMSG_STDBI_4,
        F_WRNMSG_STDBI_5,
        F_WRNMSG_STDBI_6,
        F_WRNMSG_STDBI_7,
        F_WRNMSG_STDBI_8,
        F_WRNMSG_STDBI_9,
        F_WRNMSG_STDBI_10
    };
    /**<P>科目明細(グロス･ネット区分名称)</P>*/
    private static final String[] strGrsNetIdGendo = {
        V_EMPTY_STRING,
        F_GRSNETID_1,
        F_GRSNETID_2,
        F_GRSNETID_3,
        F_GRSNETID_4,
        F_GRSNETID_5,
        F_GRSNETID_6,
        F_GRSNETID_7,
        F_GRSNETID_8,
        F_GRSNETID_9,
        F_GRSNETID_10
    };
    /**<P>科目明細(期日)</P>*/
    private static final String[] strKbiGendo = {
        V_EMPTY_STRING,
        F_KBI_1,
        F_KBI_2,
        F_KBI_3,
        F_KBI_4,
        F_KBI_5,
        F_KBI_6,
        F_KBI_7,
        F_KBI_8,
        F_KBI_9,
        F_KBI_10
    };
    /**<P>科目明細(マージン)</P>*/
    private static final String[] strMarginGendo = {
        V_EMPTY_STRING,
        F_MARGIN_1,
        F_MARGIN_2,
        F_MARGIN_3,
        F_MARGIN_4,
        F_MARGIN_5,
        F_MARGIN_6,
        F_MARGIN_7,
        F_MARGIN_8,
        F_MARGIN_9,
        F_MARGIN_10
    };
    /**<P>科目明細(指定月末残高)</P>*/
    private static final String[] strMendZanGendo = {
        V_EMPTY_STRING,
        F_MEND_ZAN_1,
        F_MEND_ZAN_2,
        F_MEND_ZAN_3,
        F_MEND_ZAN_4,
        F_MEND_ZAN_5,
        F_MEND_ZAN_6,
        F_MEND_ZAN_7,
        F_MEND_ZAN_8,
        F_MEND_ZAN_9,
        F_MEND_ZAN_10
    };
    /**<P>科目明細(指定月末極度額)</P>*/
    private static final String[] strLmtGendo = {
        V_EMPTY_STRING,
        F_LMT_1,
        F_LMT_2,
        F_LMT_3,
        F_LMT_4,
        F_LMT_5,
        F_LMT_6,
        F_LMT_7,
        F_LMT_8,
        F_LMT_9,
        F_LMT_10
    };
    /**<P>科目明細(当月増減額)</P>*/
    private static final String[] strKmkdltzggGendo = {
        V_EMPTY_STRING,
        F_KMKDLTZGG_1,
        F_KMKDLTZGG_2,
        F_KMKDLTZGG_3,
        F_KMKDLTZGG_4,
        F_KMKDLTZGG_5,
        F_KMKDLTZGG_6,
        F_KMKDLTZGG_7,
        F_KMKDLTZGG_8,
        F_KMKDLTZGG_9,
        F_KMKDLTZGG_10
    };
    /**<P>科目明細(本件後与信額)</P>*/
    private static final String[] strHonafZanGendo = {
        V_EMPTY_STRING,
        F_HONAF_ZAN_1,
        F_HONAF_ZAN_2,
        F_HONAF_ZAN_3,
        F_HONAF_ZAN_4,
        F_HONAF_ZAN_5,
        F_HONAF_ZAN_6,
        F_HONAF_ZAN_7,
        F_HONAF_ZAN_8,
        F_HONAF_ZAN_9,
        F_HONAF_ZAN_10
    };
    /**<P>科目明細(実勢現在残1(アスタリスク))</P>*/
    private static final String[] strWarningGendo = {
        V_EMPTY_STRING,
        F_WARNING_1,
        F_WARNING_2,
        F_WARNING_3,
        F_WARNING_4,
        F_WARNING_5,
        F_WARNING_6,
        F_WARNING_7,
        F_WARNING_8,
        F_WARNING_9,
        F_WARNING_10
    };
    /**<P>科目明細(実勢現在残1)</P>*/
    private static final String[] strCepernJituZan1Gendo = {
        V_EMPTY_STRING,
        F_CEPERN_JITU_ZAN1_1,
        F_CEPERN_JITU_ZAN1_2,
        F_CEPERN_JITU_ZAN1_3,
        F_CEPERN_JITU_ZAN1_4,
        F_CEPERN_JITU_ZAN1_5,
        F_CEPERN_JITU_ZAN1_6,
        F_CEPERN_JITU_ZAN1_7,
        F_CEPERN_JITU_ZAN1_8,
        F_CEPERN_JITU_ZAN1_9,
        F_CEPERN_JITU_ZAN1_10
    };
    /**<P>科目明細(実勢現在残1(C/E+P/E))</P>*/
    private static final String[] strCepernJituZan2Gendo = {
        V_EMPTY_STRING,
        F_CEPERN_JITU_ZAN2_1,
        F_CEPERN_JITU_ZAN2_2,
        F_CEPERN_JITU_ZAN2_3,
        F_CEPERN_JITU_ZAN2_4,
        F_CEPERN_JITU_ZAN2_5,
        F_CEPERN_JITU_ZAN2_6,
        F_CEPERN_JITU_ZAN2_7,
        F_CEPERN_JITU_ZAN2_8,
        F_CEPERN_JITU_ZAN2_9,
        F_CEPERN_JITU_ZAN2_10
    };
    /**<P>科目明細(実勢現在残2)</P>*/
    private static final String[] strCernJituZan1Gendo = {
        V_EMPTY_STRING,
        F_CERN_JITU_ZAN1_1,
        F_CERN_JITU_ZAN1_2,
        F_CERN_JITU_ZAN1_3,
        F_CERN_JITU_ZAN1_4,
        F_CERN_JITU_ZAN1_5,
        F_CERN_JITU_ZAN1_6,
        F_CERN_JITU_ZAN1_7,
        F_CERN_JITU_ZAN1_8,
        F_CERN_JITU_ZAN1_9,
        F_CERN_JITU_ZAN1_10
    };
    /**<P>科目明細(実勢現在残2(C/E))</P>*/
    private static final String[] strCernJituZan2Gendo = {
        V_EMPTY_STRING,
        F_CERN_JITU_ZAN2_1,
        F_CERN_JITU_ZAN2_2,
        F_CERN_JITU_ZAN2_3,
        F_CERN_JITU_ZAN2_4,
        F_CERN_JITU_ZAN2_5,
        F_CERN_JITU_ZAN2_6,
        F_CERN_JITU_ZAN2_7,
        F_CERN_JITU_ZAN2_8,
        F_CERN_JITU_ZAN2_9,
        F_CERN_JITU_ZAN2_10
    };
    /**<P>科目明細(想定元本承認額)</P>*/
    private static final String[] strSningkPrcpalGendo = {
        V_EMPTY_STRING,
        F_SNINGK_PRCPAL_1,
        F_SNINGK_PRCPAL_2,
        F_SNINGK_PRCPAL_3,
        F_SNINGK_PRCPAL_4,
        F_SNINGK_PRCPAL_5,
        F_SNINGK_PRCPAL_6,
        F_SNINGK_PRCPAL_7,
        F_SNINGK_PRCPAL_8,
        F_SNINGK_PRCPAL_9,
        F_SNINGK_PRCPAL_10
    };
    /**<P>科目明細(想定元本実勢現在残)</P>*/
    private static final String[] strJzanPrcpalGendo = {
        V_EMPTY_STRING,
        F_JZAN_PRCPAL_1,
        F_JZAN_PRCPAL_2,
        F_JZAN_PRCPAL_3,
        F_JZAN_PRCPAL_4,
        F_JZAN_PRCPAL_5,
        F_JZAN_PRCPAL_6,
        F_JZAN_PRCPAL_7,
        F_JZAN_PRCPAL_8,
        F_JZAN_PRCPAL_9,
        F_JZAN_PRCPAL_10
    };

    /**<P>為替予約残高推移数</P>*/
    private static final int intKawaseNum = 8;

    /**<P>指定表示月</P>*/
    private static final String[] strYoykAvezan = {
        V_EMPTY_STRING,
        F_YOYK_AVEZAN_1,
        F_YOYK_AVEZAN_2,
        F_YOYK_AVEZAN_3,
        F_YOYK_AVEZAN_4,
        F_YOYK_AVEZAN_5,
        F_YOYK_AVEZAN_6,
        F_YOYK_AVEZAN_7,
        F_YOYK_AVEZAN_8
    };
    /**<P>予約平残</P>*/
    private static final String[] strYoykPeak = {
        V_EMPTY_STRING,
        F_YOYK_PEAK_1,
        F_YOYK_PEAK_2,
        F_YOYK_PEAK_3,
        F_YOYK_PEAK_4,
        F_YOYK_PEAK_5,
        F_YOYK_PEAK_6,
        F_YOYK_PEAK_7,
        F_YOYK_PEAK_8
    };
    /**<P>予約ピーク</P>*/
    private static final String[] strTektRuigk = {
        V_EMPTY_STRING,
        F_TEKT_RUIGK_1,
        F_TEKT_RUIGK_2,
        F_TEKT_RUIGK_3,
        F_TEKT_RUIGK_4,
        F_TEKT_RUIGK_5,
        F_TEKT_RUIGK_6,
        F_TEKT_RUIGK_7,
        F_TEKT_RUIGK_8
    };
    /**<P>当月締結累計額</P>*/
    private static final String[] strAveTurnKkn = {
        V_EMPTY_STRING,
        F_AVE_TURN_KKN_1,
        F_AVE_TURN_KKN_2,
        F_AVE_TURN_KKN_3,
        F_AVE_TURN_KKN_4,
        F_AVE_TURN_KKN_5,
        F_AVE_TURN_KKN_6,
        F_AVE_TURN_KKN_7,
        F_AVE_TURN_KKN_8
    };
    /**<P>平均回転期間</P>*/
    private static final String[] strMM = {
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        V_EMPTY_STRING,


        F_MM_3,
        F_MM_4,
        F_MM_5,
        F_MM_6,
        F_MM_7,
        F_MM_8
    };


    /**<P>決算期</P>*/
    private static final String[] strKessanki = {
        F_KESSANKI1,
        F_KESSANKI2,
        F_KESSANKI3
    };
    /**<P>純売上高</P>*/
    private static final String[] strUriage = {
        F_URIAGE1,
        F_URIAGE2,
        F_URIAGE3
    };
    /**<P>平均月商</P>*/
    private static final String[] strGessho = {
        F_URIAGEGESSHO1,
        F_URIAGEGESSHO2,
        F_URIAGEGESSHO3
    };
    /**<P>経常利益</P>*/
    private static final String[] strKeijoeki = {
        F_KEIJOEKI1,
        F_KEIJOEKI2,
        F_KEIJOEKI3
    };
    /**<P>経常利益率</P>*/
    private static final String[] strKeijoekiRit = {
        F_KEIJOEKI_RIT1,
        F_KEIJOEKI_RIT2,
        F_KEIJOEKI_RIT3
    };
    /**<P>当期利益</P>*/
    private static final String[] strTokieki = {
        F_TOKIEKI1,
        F_TOKIEKI2,
        F_TOKIEKI3
    };
    /**<P>当期利益率</P>*/
    private static final String[] strTokiekiRit = {
        F_TOKIEKI_RIT1,
        F_TOKIEKI_RIT2,
        F_TOKIEKI_RIT3
    };
    /**<P>減価償却</P>*/
    private static final String[] strShokyaku = {
        F_SHOKYAKUJISSHIGAK_TOKI1,
        F_SHOKYAKUJISSHIGAK_TOKI2,
        F_SHOKYAKUJISSHIGAK_TOKI3
    };
    /**<P>簡易CF</P>*/
    private static final String[] strKskbtdlCF = {
        F_KSKBTDLCF1,
        F_KSKBTDLCF2,
        F_KSKBTDLCF3
    };
    /**<P>配当率</P>*/
    private static final String[] strHaitoRit = {
        F_HAITO_RIT1,
        F_HAITO_RIT2,
        F_HAITO_RIT3
    };
    /**<P>純資産額</P>*/
    private static final String[] strShomishisan = {
        F_SHOMISHISAN1,
        F_SHOMISHISAN2,
        F_SHOMISHISAN3
    };
    /**<P>借入金回転期間</P>*/
    private static final String[] strKariireKaiten = {
        F_KARIIREKAITEN1,
        F_KARIIREKAITEN2,
        F_KARIIREKAITEN3
    };
    /**<P>純金利負担率</P>*/
    private static final String[] strFutanRitu = {
        F_URIAGEKINRIFUTAN_RIT1,
        F_URIAGEKINRIFUTAN_RIT2,
        F_URIAGEKINRIFUTAN_RIT3
    };
    /**<P>自己資本比率</P>*/
    private static final String[] strJikoshihonHirt = {
        F_JIKOSHIHON_HIRT1,
        F_JIKOSHIHON_HIRT2,
        F_JIKOSHIHON_HIRT3
    };
    /**<P>経常収支比率</P>*/
    private static final String[] strKeijoshushiHrit = {
        F_KEIJOSHUSHI_HRIT1,
        F_KEIJOSHUSHI_HRIT2,
        F_KEIJOSHUSHI_HRIT3
    };
    /**<P>売上総利益</P>*/
    private static final String[] strUrisoek = {
        F_URISOEK1_ANK,
        F_URISOEK2_ANK
    };
    /**<P>営業利益</P>*/
    private static final String[] strEigyek = {
        F_EIGYEK1_ANK,
        F_EIGYEK2_ANK
    };
    /**<P>有利子負債</P>*/
    private static final String[] strYrsliab = {
        F_YRSLIAB1_ANK,
        F_YRSLIAB2_ANK
    };


/* 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
 * 規定・優良担保・協会保証に対応する V_EMPTY_STRING を追加
 * 規定・一般担保・一般L/Cに対応する  V_EMPTY_STRING を移動
 * 規定・一般担保・手形保険に対応する V_EMPTY_STRING を移動
 */
    /**<P> 本件後引当状況-規定値取得用リスト </P>*/
    private static final String[] strKeiHikiateKite = {
        V_EMPTY_STRING,
        F_KTITNP_YUTNP1_YOTAN,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP1_SCTY,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP1_HOSHO,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP1_SONOTA,
        V_EMPTY_STRING,
        F_KTITNP_IPTNP1_SCTY,
        F_KTITNP_IPTNP1_HOSHO,
        F_KTITNP_IPTNP1_FUDOTE,
/* YC20218-02 Start */
        V_EMPTY_STRING,
/* YC20218-02 End */
        F_KTITNP_IPTNP1_FUDONE,
//      V_EMPTY_STRING,
//      V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_IPTNP1_SONOTA,
        V_EMPTY_STRING,
        F_KTITNP_SNTTNP1_SCTY,
        F_KTITNP_SNTTNP1_HOSHO,
// 2013/09/17 CHG@K.Nishio GEC25-C-032 start
//      V_EMPTY_STRING,
        F_KTITNP_SNTTNP1_LOAN,
// 2013/09/17 CHG@K.Nishio GEC25-C-032 end
        F_KTITNP_SNTTNP1_SONOTA,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTIGTNP_YUTNP1_SCTY,
        F_KTIGTNP_YUTNP1_HOSHO,
        F_KTIGTNP_YUTNP1_SONOTA,
        V_EMPTY_STRING,
        F_KTIGTNP_IPTNP1_SCTY,
        F_KTIGTNP_IPTNP1_HOSHO,
        F_KTIGTNP_IPTNP1_FUDOTE,
        F_KTIGTNP_IPTNP1_FUDONE,
        F_KTIGTNP_IPTNP1_NYK_HOSKN,
        F_KTIGTNP_IPTNP1_BOND,
        F_KTIGTNP_IPTNP1_SONOTA,
        F_KTIGTNP_SNTTNP1_SONOTA
    };
// 2005/02/08 CHG M.Kudo END

/* 2005/02/08 CHG M.Kudo START (GEC16-C-143-005)
 * 規定・優良担保・協会保証に対応する V_EMPTY_STRING を追加
 * 規定・一般担保・一般L/Cに対応する  V_EMPTY_STRING を移動
 * 規定・一般担保・手形保険に対応する V_EMPTY_STRING を移動
 */
    /**<P> 本件後引当状況-時価ベース取得用リスト </P>*/
    private static final String[] strKeiHikiateJika = {
        V_EMPTY_STRING,
        F_KTITNP_YUTNP2_YOTAN,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP2_SCTY,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP2_HOSHO,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_YUTNP2_SONOTA,
        V_EMPTY_STRING,
        F_KTITNP_IPTNP2_SCTY,
        F_KTITNP_IPTNP2_HOSHO,
        F_KTITNP_IPTNP2_FUDOTE,
/* YC20218-02 Start */
        V_EMPTY_STRING,
/* YC20218-02 End */
        F_KTITNP_IPTNP2_FUDONE,
//      V_EMPTY_STRING,
//      V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTITNP_IPTNP2_SONOTA,
        V_EMPTY_STRING,
        F_KTITNP_SNTTNP2_SCTY,
        F_KTITNP_SNTTNP2_HOSHO,
// 2013/09/17 CHG@K.Nishio GEC25-C-032 start
//      V_EMPTY_STRING,
        F_KTITNP_SNTTNP2_LOAN,
// 2013/09/17 CHG@K.Nishio GEC25-C-032 end
        F_KTITNP_SNTTNP2_SONOTA,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        V_EMPTY_STRING,
        F_KTIGTNP_YUTNP2_SCTY,
        F_KTIGTNP_YUTNP2_HOSHO,
        F_KTIGTNP_YUTNP2_SONOTA,
        V_EMPTY_STRING,
        F_KTIGTNP_IPTNP2_SCTY,
        F_KTIGTNP_IPTNP2_HOSHO,
        F_KTIGTNP_IPTNP2_FUDOTE,
        F_KTIGTNP_IPTNP2_FUDONE,
        F_KTIGTNP_IPTNP2_NYK_HOSKN,
        F_KTIGTNP_IPTNP2_BOND,
        F_KTIGTNP_IPTNP2_SONOTA,
        F_KTIGTNP_SNTTNP2_SONOTA
    };
// 2005/02/08 CHG M.Kudo END


    /**<P> 代表店番CIF番号 </P>*/
    private String strDaihyouBrnoTriskno = V_EMPTY_STRING;

// GEC294-C-004 S
    /**<P>科目･適用、禀議査定番号リスト</P>*/
    private static final String F_KMK_RMT_LIST = "kmk_rmt_list";
    /**<P>禀議査定番号リスト</P>*/
    private static final String F_RSNO_LIST = "rsno_list";
// GEC294-C-004 E

/**<P> 単体財務決算分析(貸借対照表)取得用動的SQL-1 </P>*/
/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 項目から「資本合計」を削除して、「自己資本」「コマーシャルペーパー」「純資産合計」を追加
 */
//private final String P_SQL_4187_1
//  = "SELECT ksanh,capit_kei,ryass_kei,cashykn,uketegt,urikkn,zaiko_kei,fixass_kei,fixassy_kei,krnass_kei,ass_kei,ryliab_kei,site,kaikkn,warite,skari,fixliab_kei,kbond,lkari,liabcapit_kei,lkari_rpay1,kbond_rpay1 FROM (SELECT ksanh,capit_kei,ryass_kei,cashykn,uketegt,urikkn,zaiko_kei,fixass_kei,fixassy_kei,krnass_kei,ass_kei,ryliab_kei,site,kaikkn,warite,skari,fixliab_kei,kbond,lkari,liabcapit_kei,lkari_rpay1,kbond_rpay1 FROM t_ciw_tanzm_bs WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
private final String P_SQL_4187_1
    = "SELECT ksanh,jikocapit,ryass_kei,cashykn,uketegt,urikkn,zaiko_kei,fixass_kei,fixassy_kei,krnass_kei,ass_kei,ryliab_kei,site,kaikkn,warite,skari,fixliab_kei,kbond,lkari,liabjnass_kei,lkari_rpay1,kbond_rpay1,cp_val,jnass_kei FROM (SELECT /*+ index(t_ciw_tanzm_bs p_ciw_tanzm_bs) */ksanh,jikocapit,ryass_kei,cashykn,uketegt,urikkn,zaiko_kei,fixass_kei,fixassy_kei,krnass_kei,ass_kei,ryliab_kei,site,kaikkn,warite,skari,fixliab_kei,kbond,lkari,liabjnass_kei,lkari_rpay1,kbond_rpay1,cp_val,jnass_kei FROM t_ciw_tanzm_bs WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/**<P> 単体財務決算分析(貸借対照表)取得用動的SQL-2 </P>*/
private final String P_SQL_4187_2
    = ") ORDER BY ksanh DESC) WHERE ROWNUM<=3" ;

/**<P> 単体財務決算分析(損益計算書･利益処分)取得用動的SQL-1 </P>*/
/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 項目から「法人税等引当額」「中間配当金」「期末配当」「役員賞与」を削除
 */
//private final String P_SQL_4188_1
//  = "SELECT ksanh,uriage,uriagemsh,keiek,urisoek_rit,urikeiek_rit,tohek,uritohek_rit,urisoek,eigyek,hjzeiet_hkgk,midhtkn,hend_htkn,yaksyoyo,toh_gensyo_jisigk FROM (SELECT ksanh,uriage,uriagemsh,keiek,urisoek_rit,urikeiek_rit,tohek,uritohek_rit,urisoek,eigyek,hjzeiet_hkgk,midhtkn,hend_htkn,yaksyoyo,toh_gensyo_jisigk FROM t_ciw_tanzm_pl WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
private final String P_SQL_4188_1
    = "SELECT ksanh,uriage,uriagemsh,keiek,urisoek_rit,urikeiek_rit,tohek,uritohek_rit,urisoek,eigyek,toh_gensyo_jisigk FROM (SELECT /*+ index(t_ciw_tanzm_pl p_ciw_tanzm_pl) */ksanh,uriage,uriagemsh,keiek,urisoek_rit,urikeiek_rit,tohek,uritohek_rit,urisoek,eigyek,toh_gensyo_jisigk FROM t_ciw_tanzm_pl WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/**<P> 単体財務決算分析(損益計算書･利益処分)取得用動的SQL-2 </P>*/
private final String P_SQL_4188_2
    = ") ORDER BY ksanh DESC) WHERE ROWNUM<=3" ;

/**<P> 単体財務決算分析(経営指標)取得用動的SQL-1 </P>*/
/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 項目から「配当率」を削除
 */
//private final String P_SQL_4189_1
//  = "SELECT ksanh,htrt,karikaitn,jikocapit_hrit,urijunintfutan_rit FROM (SELECT ksanh,htrt,karikaitn,jikocapit_hrit,urijunintfutan_rit FROM t_ciw_tanzm_ksnshihyo WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
private final String P_SQL_4189_1
    = "SELECT ksanh,karikaitn,jikocapit_hrit,urijunintfutan_rit FROM (SELECT /*+ index(t_ciw_tanzm_ksnshihyo p_ciw_tanzm_ksnshihyo) */ksanh,karikaitn,jikocapit_hrit,urijunintfutan_rit FROM t_ciw_tanzm_ksnshihyo WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/**<P> 単体財務決算分析(経営指標)取得用動的SQL-2 </P>*/
private final String P_SQL_4189_2
    = ") ORDER BY ksanh DESC) WHERE ROWNUM<=3" ;

/*
 * 2007.02.21 Add.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 単体財務決算分析(資金調達運用表)取得用の動的SQL定義を追加。
 */
/**<P> 単体財務決算分析(資金調達運用表)取得用動的SQL-1 </P>*/
private final String P_SQL_4312_1
    = "SELECT ksanh,ido_keijsysi,ido_keijsysi_hrit,syuek_yrsliab_cf FROM (SELECT /*+ index(t_ciw_tanzm_chtunyo p_ciw_tanzm_chtunyo) */ksanh,ido_keijsysi,ido_keijsysi_hrit,syuek_yrsliab_cf FROM t_ciw_tanzm_chtunyo WHERE gcif_no=':gcif_no' AND del_flg='0' AND ksanh IN (" ;

/**<P> 単体財務決算分析(資金調達運用表)取得用動的SQL-2 </P>*/
private final String P_SQL_4312_2
    = ") ORDER BY ksanh DESC) WHERE ROWNUM<=3" ;
// 2007.02.19 Add. End  M.Kawano(GEC18-C-014, にゅーとん対応)


/**
 *　 <DL>
 *   <DT><b>メソッド概要:</b><DD>
 *   DBクラスコンストラクタ<BR>
 *   </DD></DT>
 *   </DL>
 *   <BR>
 *   @param      CraftsTrxFolder    folder    トランザクションフォルダインスタンス
 *   @param      CraftsDBConnector  dbcon     DB接続インスタンス
 *   @param      CraftsDBParam      dbparam   DBパラメータインスタンス
 *   @return     String                     禀議DBクラスインスタンス
 */
    public RLRRG004_B01_DB(CraftsTrxFolder folder,CraftsDBConnector dbcon,CraftsDBParam dbparam){

        super(folder, dbcon, dbparam);

    }

/**
 *　 <DL>
 *   <DT><b>メソッド概要:全項目取得</b><DD>
 *   融資禀議書・査定書の全項目を取得する。<BR>
 *   </DD></DT>
 *   </DL>
 *   <BR>
 *   @param      Hashtable        hstComBasket  共有情報
 *   @exception  WACSSysException
 *   @exception  com.ibm.jp.wacs.db.WACSDBException
 */
    public void getAllData(Hashtable hstComBasket)
                            throws com.ibm.jp.wacs.db.WACSDBException, WACSSysException {

        try {
            // 初期処理 ---------------------------------------------------------
            int i = int0;                   // forループ変数

            // DB共通領域のHashtableを取得する
            hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

            // KEY共通領域のHashtableを取得する
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            // KEY共通領域の情報を取得
            String strLcNo       = (String)hstKey.get(F_LC_NO);
            String strHoseiKubun = (String)hstKey.get(F_HOSEIKUBUN);

            // 計数情報、計数情報(その他項目)、計数情報(経営指標決算期別明細)、
            // 計数情報(市場性与信状況)、計数情報(参考計数)、計数情報(自己査定)、
            // 計数情報(主要行取引状況)、計数情報(取引採算)、計数情報(本件後引当状況)、
            // 計数情報(本件後市場性与信引当状況)の全項目を取得する ----
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_LC_NO.toLowerCase(),strLcNo);
            dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseiKubun);

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4101)(PreparedStatement)
            CraftsDBResult rs_o4101 = dbcon.executeQueryPS(SQL_4101,dbparam);
            if (rs_o4101.getNumResult() == int0) {
                    hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DATA_NOT_FOUND));
                return;
            }

            // 計数情報(一般与信状況明細)の全項目を取得する ----

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4102)(PreparedStatement)
            CraftsDBResult rs_o4102 = dbcon.executeQueryPS(SQL_4102,dbparam);
            if (rs_o4102.getNumResult() == int0) {
                hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DATA_NOT_FOUND));
                return;
            }

            // 計数情報(保証人)の全項目を取得する ----

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4103)(PreparedStatement)
            CraftsDBResult rs_o4103 = dbcon.executeQueryPS(SQL_4103,dbparam);
            if (rs_o4103.getNumResult() == int0) {
                hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DATA_NOT_FOUND));
                return;
            }

            // 計数情報(限度算入与信状況)の全項目を取得する ----

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4104)(PreparedStatement)
            CraftsDBResult rs_o4104 = dbcon.executeQueryPS(SQL_4104,dbparam);
            if (rs_o4104.getNumResult() == int0) {
                hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DATA_NOT_FOUND));
                return;
            }

            // 計数情報(為替予約残高推移月別明細)の全項目を取得する ----

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4105)(PreparedStatement)
            CraftsDBResult rs_o4105 = dbcon.executeQueryPS(SQL_4105,dbparam);
            if (rs_o4105.getNumResult() == int0) {
                hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DATA_NOT_FOUND));
                return;
            }

            // 取得データの設定 -------------------------------------------------
            // 計数情報の項目を設定する
            hstDB.put(F_SSKBRNO,ns(rs_o4101.getString2(F_SSKBRNO,0)));
            hstDB.put(F_SSKBRNM,ns(rs_o4101.getString2(F_SSKBRNM,0)));
            hstDB.put(F_BRNO,ns(rs_o4101.getString2(F_BRNO,0)));
            hstDB.put(F_TRISKNO,ns(rs_o4101.getString2(F_TRISKNO,0)));
            hstDB.put(F_TRINM,ns(rs_o4101.getString2(F_TRINM,0)));
            hstDB.put(F_SJOSEIINF_TANI_MSG,ns(rs_o4101.getString2(F_SJOSEIINF_TANI_MSG,0)));
            hstDB.put(F_SJOSEIINF_KKRID,ns(rs_o4101.getString2(F_SJOSEIINF_KKRID,0)));
            hstDB.put(F_HOSRSN,ns(rs_o4101.getString2(F_HOSRSN,0)));
            hstDB.put(F_KKNNMMO2,ns(rs_o4101.getString2(F_KKNNMMO2,0)));
            hstDB.put(F_KKNNMMO3,ns(rs_o4101.getString2(F_KKNNMMO3,0)));
// 2011/11/18 ADD@M.Hayashi GEC23-C-051 Start
            hstDB.put(F_HOZEN_POOLID,ns(rs_o4101.getString2(F_HOZEN_POOLID,0)));
            hstDB.put(F_HOZEN_TANI_MSG,ns(rs_o4101.getString2(F_HOZEN_TANI_MSG,0)));
            hstDB.put(F_HOZEN_IPNYSN,ns(rs_o4101.getString2(F_HOZEN_IPNYSN,0)));
            hstDB.put(F_HOZEN_SJOSEIYSN,ns(rs_o4101.getString2(F_HOZEN_SJOSEIYSN,0)));
            hstDB.put(F_HOZEN_KITEITANPO,ns(rs_o4101.getString2(F_HOZEN_KITEITANPO,0)));
            hstDB.put(F_HOZEN_HOZENRT,ns(rs_o4101.getString2(F_HOZEN_HOZENRT,0)));
// 2011/11/18 ADD@M.Hayashi GEC23-C-051 End
// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
            hstDB.put(F_HOZEN_SOGOYSN,ns(rs_o4101.getString2(F_HOZEN_SOGOYSN,0)));
            hstDB.put(F_HOZEN_SOGOSNYO,ns(rs_o4101.getString2(F_HOZEN_SOGOSNYO,0)));
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End
            hstDB.put(F_MEMO,ns(rs_o4101.getString2(F_MEMO,0)));
            hstDB.put(F_CKKKNKEISU_LC_NO,ns(rs_o4101.getString2(F_CKKKNKEISU_LC_NO,0)));
            hstDB.put(F_MKBI,ns(rs_o4101.getString2(F_MKBI,0)));
            hstDB.put(F_TANI_MSG_1,ns(rs_o4101.getString2(F_TANI_MSG,0)));
            hstDB.put(F_KKRID_1,ns(rs_o4101.getString2(F_KKRID,0)));
            hstDB.put(F_TANI_MSG_2,ns(rs_o4101.getString2(F_TANI_MSG,0)));
            hstDB.put(F_KKRID_2,ns(rs_o4101.getString2(F_KKRID,0)));
            hstDB.put(F_SJOSEIINF_TANI_MSG_1,ns(rs_o4101.getString2(F_SJOSEIINF_TANI_MSG,0)));
            hstDB.put(F_SJOSEIINF_KKRID_1,ns(rs_o4101.getString2(F_SJOSEIINF_KKRID,0)));
            hstDB.put(F_SJOSEIINF_TANI_MSG_2,ns(rs_o4101.getString2(F_SJOSEIINF_TANI_MSG,0)));
            hstDB.put(F_SJOSEIINF_KKRID_2,ns(rs_o4101.getString2(F_SJOSEIINF_KKRID,0)));
            /* YC20218-02 START */
            hstDB.put(F_HLOAN_GENDFSN, ns(rs_o4101.getString2(F_HLOAN_GENDFSN, 0)));
            /* YC20218-02 START */

//STEP2 ADD RSNO

            hstDB.put(F_RSNO, ns(rs_o4101.getString2(F_RSNO, 0)));


// 2003/09/12 ADD@S.SEIMURA 同時審査対応(00331)
            // 案件サマリー用の項目を取得
            hstDB.put(F_CKKKN_ANK,ns(rs_o4101.getString2(F_CKKKN_ANK,0)));
            hstDB.put(F_RYUDOSHISAN_KEI_ANK,ns(rs_o4101.getString2(F_RYUDOSHISAN_KEI_ANK,0)));
            hstDB.put(F_GENYOKIN_ANK,ns(rs_o4101.getString2(F_GENYOKIN_ANK,0)));
            hstDB.put(F_UKETEGATA_URIKAKE_ANK,ns(rs_o4101.getString2(F_UKETEGATA_URIKAKE_ANK,0)));
            hstDB.put(F_TANAOROSHI_KEI_ANK,ns(rs_o4101.getString2(F_TANAOROSHI_KEI_ANK,0)));
            hstDB.put(F_KOTEISHISAN_KEI_ANK,ns(rs_o4101.getString2(F_KOTEISHISAN_KEI_ANK,0)));
            hstDB.put(F_YUKEIKOTEISHISAN_KEI_ANK,ns(rs_o4101.getString2(F_YUKEIKOTEISHISAN_KEI_ANK,0)));
            hstDB.put(F_KURINOBESHISAN_KEI_ANK,ns(rs_o4101.getString2(F_KURINOBESHISAN_KEI_ANK,0)));
            hstDB.put(F_SHISAN_KEI_ANK,ns(rs_o4101.getString2(F_SHISAN_KEI_ANK,0)));
            hstDB.put(F_RYUDOFUSAI_KEI_ANK,ns(rs_o4101.getString2(F_RYUDOFUSAI_KEI_ANK,0)));
            hstDB.put(F_SHITEGATA_KAIKAKE_ANK,ns(rs_o4101.getString2(F_SHITEGATA_KAIKAKE_ANK,0)));
            hstDB.put(F_WARITEGATA_ANK,ns(rs_o4101.getString2(F_WARITEGATA_ANK,0)));
            hstDB.put(F_TANKARIKIN_ANK,ns(rs_o4101.getString2(F_TANKARIKIN_ANK,0)));
            hstDB.put(F_KOTEIFUSAI_KEI_ANK,ns(rs_o4101.getString2(F_KOTEIFUSAI_KEI_ANK,0)));
            hstDB.put(F_SHASAI_CHOKARIKIN_ANK,ns(rs_o4101.getString2(F_SHASAI_CHOKARIKIN_ANK,0)));
            hstDB.put(F_SHIHON_KEI_ANK,ns(rs_o4101.getString2(F_SHIHON_KEI_ANK,0)));
            hstDB.put(F_FUSAISHIHON_KEI_ANK,ns(rs_o4101.getString2(F_FUSAISHIHON_KEI_ANK,0)));


            // 計数情報(その他項目)の項目を設定する
// 2010/10/14 DEL@S.Fujimoto GEC21-C-067 Start
//          hstDB.put(F_MOCHAI_MBKHV_CM_KABUTO_GK,ns(rs_o4101.getString2(F_MOCHAI_MBKHV_CM_KABUTO_GK,0)));
// 2010/10/14 DEL@S.Fujimoto GEC21-C-067 End
            hstDB.put(F_MOCHAI_SIBOSAI_HIKIUZAN,ns(rs_o4101.getString2(F_MOCHAI_SIBOSAI_HIKIUZAN,0)));
// 2010/10/14 DEL@S.Fujimoto GEC21-C-067 Start
//          hstDB.put(F_MOCHAI_YNBOND_HIKIUZAN,ns(rs_o4101.getString2(F_MOCHAI_YNBOND_HIKIUZAN,0)));
//          hstDB.put(F_MOCHAI_CMHV_MBK_KABUTO_GK,ns(rs_o4101.getString2(F_MOCHAI_CMHV_MBK_KABUTO_GK,0)));
// 2010/10/14 DEL@S.Fujimoto GEC21-C-067 End
            hstDB.put(F_HKSTM_HNN_YKN,ns(rs_o4101.getString2(F_HKSTM_HNN_YKN,0)));
            hstDB.put(F_HKSTM_HNN_KBIKEK,ns(rs_o4101.getString2(F_HKSTM_HNN_KBIKEK,0)));
            hstDB.put(F_HKSTM_HSYNIN_YKN,ns(rs_o4101.getString2(F_HKSTM_HSYNIN_YKN,0)));
            hstDB.put(F_HKSTM_HSYNIN_KBIKEK,ns(rs_o4101.getString2(F_HKSTM_HSYNIN_KBIKEK,0)));
            hstDB.put(F_DAITEZAN,ns(rs_o4101.getString2(F_DAITEZAN,0)));
            hstDB.put(F_KKN_HYOJ,ns(rs_o4101.getString2(F_KKN_HYOJ,0)));
            hstDB.put(F_SHNJLN_ZAN,ns(rs_o4101.getString2(F_SHNJLN_ZAN,0)));
            hstDB.put(F_ETCSHNJLNKYG,ns(rs_o4101.getString2(F_ETCSHNJLNKYG,0)));
            hstDB.put(F_ETCSHNJLNAFZN,ns(rs_o4101.getString2(F_ETCSHNJLNAFZN,0)));
            hstDB.put(F_SUM_HRI_ZAN,ns(rs_o4101.getString2(F_SUM_HRI_ZAN,0)));
            hstDB.put(F_ETCSUMHRIKYG,ns(rs_o4101.getString2(F_ETCSUMHRIKYG,0)));
            hstDB.put(F_ETCSUMHRIAFZN,ns(rs_o4101.getString2(F_ETCSUMHRIAFZN,0)));
// 2010/10/14 ADD@S.Fujimoto GEC21-C-067 Start
            hstDB.put(F_ETC_TANI_MSG,ns(rs_o4101.getString2(F_TANI_MSG,0)));
            hstDB.put(F_SSTKABU_KABUSU,ns(rs_o4101.getString2(F_SSTKABU_KABUSU,0)));
            hstDB.put(F_SSTKABU_BOKA,ns(rs_o4101.getString2(F_SSTKABU_BOKA,0)));
            hstDB.put(F_SSTKABU_SHUTKGK,ns(rs_o4101.getString2(F_SSTKABU_SHUTKGK,0)));
            hstDB.put(F_SSTKABU_JIKA,ns(rs_o4101.getString2(F_SSTKABU_JIKA,0)));
            hstDB.put(F_SSTKABU_HYKABU,ns(rs_o4101.getString2(F_SSTKABU_HYKABU,0)));
            hstDB.put(F_SSTKABU_HYJIKA,ns(rs_o4101.getString2(F_SSTKABU_HYJIKA,0)));
            hstDB.put(F_SSTKABU_SAISAN,ns(rs_o4101.getString2(F_SSTKABU_SAISAN,0)));
// 2010/10/14 ADD@S.Fujimoto GEC21-C-067 End


            // 計数情報(経営指標決算期別明細)の項目を設定する
            hstDB.put(F_KESSANKI1,ns(rs_o4101.getString2(F_KESSANKI1,0)));
            hstDB.put(F_URIAGE1,ns(rs_o4101.getString2(F_URIAGE1,0)));
            hstDB.put(F_URIAGEGESSHO1,ns(rs_o4101.getString2(F_URIAGEGESSHO1,0)));
            hstDB.put(F_KEIJOEKI1,ns(rs_o4101.getString2(F_KEIJOEKI1,0)));
            hstDB.put(F_KEIJOEKI_RIT1,ns(rs_o4101.getString2(F_KEIJOEKI_RIT1,0)));
            hstDB.put(F_TOKIEKI1,ns(rs_o4101.getString2(F_TOKIEKI1,0)));
            hstDB.put(F_TOKIEKI_RIT1,ns(rs_o4101.getString2(F_TOKIEKI_RIT1,0)));
            hstDB.put(F_SHOKYAKUJISSHIGAK_TOKI1,ns(rs_o4101.getString2(F_SHOKYAKUJISSHIGAK_TOKI1,0)));
            hstDB.put(F_KSKBTDLCF1,ns(rs_o4101.getString2(F_KSKBTDLCF1,0)));
            hstDB.put(F_HAITO_RIT1,ns(rs_o4101.getString2(F_HAITO_RIT1,0)));
            hstDB.put(F_SHOMISHISAN1,ns(rs_o4101.getString2(F_SHOMISHISAN1,0)));
            hstDB.put(F_KARIIREKAITEN1,ns(rs_o4101.getString2(F_KARIIREKAITEN1,0)));
            hstDB.put(F_URIAGEKINRIFUTAN_RIT1,ns(rs_o4101.getString2(F_URIAGEKINRIFUTAN_RIT1,0)));
            hstDB.put(F_JIKOSHIHON_HIRT1,ns(rs_o4101.getString2(F_JIKOSHIHON_HIRT1,0)));
            hstDB.put(F_KEIJOSHUSHI_HRIT1,ns(rs_o4101.getString2(F_KEIJOSHUSHI_HRIT1,0)));
            hstDB.put(F_KESSANKI2,ns(rs_o4101.getString2(F_KESSANKI2,0)));
            hstDB.put(F_URIAGE2,ns(rs_o4101.getString2(F_URIAGE2,0)));
            hstDB.put(F_URIAGEGESSHO2,ns(rs_o4101.getString2(F_URIAGEGESSHO2,0)));
            hstDB.put(F_KEIJOEKI2,ns(rs_o4101.getString2(F_KEIJOEKI2,0)));
            hstDB.put(F_KEIJOEKI_RIT2,ns(rs_o4101.getString2(F_KEIJOEKI_RIT2,0)));
            hstDB.put(F_TOKIEKI2,ns(rs_o4101.getString2(F_TOKIEKI2,0)));
            hstDB.put(F_TOKIEKI_RIT2,ns(rs_o4101.getString2(F_TOKIEKI_RIT2,0)));
            hstDB.put(F_SHOKYAKUJISSHIGAK_TOKI2,ns(rs_o4101.getString2(F_SHOKYAKUJISSHIGAK_TOKI2,0)));
            hstDB.put(F_KSKBTDLCF2,ns(rs_o4101.getString2(F_KSKBTDLCF2,0)));
            hstDB.put(F_HAITO_RIT2,ns(rs_o4101.getString2(F_HAITO_RIT2,0)));
            hstDB.put(F_SHOMISHISAN2,ns(rs_o4101.getString2(F_SHOMISHISAN2,0)));
            hstDB.put(F_KARIIREKAITEN2,ns(rs_o4101.getString2(F_KARIIREKAITEN2,0)));
            hstDB.put(F_URIAGEKINRIFUTAN_RIT2,ns(rs_o4101.getString2(F_URIAGEKINRIFUTAN_RIT2,0)));
            hstDB.put(F_JIKOSHIHON_HIRT2,ns(rs_o4101.getString2(F_JIKOSHIHON_HIRT2,0)));
            hstDB.put(F_KEIJOSHUSHI_HRIT2,ns(rs_o4101.getString2(F_KEIJOSHUSHI_HRIT2,0)));
            hstDB.put(F_KESSANKI3,ns(rs_o4101.getString2(F_KESSANKI3,0)));
            hstDB.put(F_URIAGE3,ns(rs_o4101.getString2(F_URIAGE3,0)));
            hstDB.put(F_URIAGEGESSHO3,ns(rs_o4101.getString2(F_URIAGEGESSHO3,0)));
            hstDB.put(F_KEIJOEKI3,ns(rs_o4101.getString2(F_KEIJOEKI3,0)));
            hstDB.put(F_KEIJOEKI_RIT3,ns(rs_o4101.getString2(F_KEIJOEKI_RIT3,0)));
            hstDB.put(F_TOKIEKI3,ns(rs_o4101.getString2(F_TOKIEKI3,0)));
            hstDB.put(F_TOKIEKI_RIT3,ns(rs_o4101.getString2(F_TOKIEKI_RIT3,0)));
            hstDB.put(F_SHOKYAKUJISSHIGAK_TOKI3,ns(rs_o4101.getString2(F_SHOKYAKUJISSHIGAK_TOKI3,0)));
            hstDB.put(F_KSKBTDLCF3,ns(rs_o4101.getString2(F_KSKBTDLCF3,0)));
            hstDB.put(F_HAITO_RIT3,ns(rs_o4101.getString2(F_HAITO_RIT3,0)));
            hstDB.put(F_SHOMISHISAN3,ns(rs_o4101.getString2(F_SHOMISHISAN3,0)));
            hstDB.put(F_KARIIREKAITEN3,ns(rs_o4101.getString2(F_KARIIREKAITEN3,0)));
            hstDB.put(F_URIAGEKINRIFUTAN_RIT3,ns(rs_o4101.getString2(F_URIAGEKINRIFUTAN_RIT3,0)));
            hstDB.put(F_JIKOSHIHON_HIRT3,ns(rs_o4101.getString2(F_JIKOSHIHON_HIRT3,0)));
            hstDB.put(F_KEIJOSHUSHI_HRIT3,ns(rs_o4101.getString2(F_KEIJOSHUSHI_HRIT3,0)));
            hstDB.put(F_KESSANKI4,ns(rs_o4101.getString2(F_KESSANKI4,0)));
            hstDB.put(F_URIAGE4,ns(rs_o4101.getString2(F_URIAGE4,0)));
            hstDB.put(F_URIAGEGESSHO4,ns(rs_o4101.getString2(F_URIAGEGESSHO4,0)));
            hstDB.put(F_KEIJOEKI4,ns(rs_o4101.getString2(F_KEIJOEKI4,0)));
            hstDB.put(F_KEIJOEKI_RIT4,ns(rs_o4101.getString2(F_KEIJOEKI_RIT4,0)));
            hstDB.put(F_TOKIEKI4,ns(rs_o4101.getString2(F_TOKIEKI4,0)));
            hstDB.put(F_TOKIEKI_RIT4,ns(rs_o4101.getString2(F_TOKIEKI_RIT4,0)));
            hstDB.put(F_SHOKYAKUJISSHIGAK_TOKI4,ns(rs_o4101.getString2(F_SHOKYAKUJISSHIGAK_TOKI4,0)));
            hstDB.put(F_CHKCF,ns(rs_o4101.getString2(F_CHKCF,0)));
            hstDB.put(F_HAITO_RIT4,ns(rs_o4101.getString2(F_HAITO_RIT4,0)));
            hstDB.put(F_SHOMISHISAN4,ns(rs_o4101.getString2(F_SHOMISHISAN4,0)));
            hstDB.put(F_KARIIREKAITEN4,ns(rs_o4101.getString2(F_KARIIREKAITEN4,0)));
            hstDB.put(F_URIAGEKINRIFUTAN_RIT4,ns(rs_o4101.getString2(F_URIAGEKINRIFUTAN_RIT4,0)));
            hstDB.put(F_JIKOSHIHON_HIRT4,ns(rs_o4101.getString2(F_JIKOSHIHON_HIRT4,0)));
            hstDB.put(F_KESSANKI5,ns(rs_o4101.getString2(F_KESSANKI5,0)));
            hstDB.put(F_URIAGE5,ns(rs_o4101.getString2(F_URIAGE5,0)));
            hstDB.put(F_URIAGEGESSHO5,ns(rs_o4101.getString2(F_URIAGEGESSHO5,0)));
            hstDB.put(F_KEIJOEKI5,ns(rs_o4101.getString2(F_KEIJOEKI5,0)));
            hstDB.put(F_KEIJOEKI_RIT5,ns(rs_o4101.getString2(F_KEIJOEKI_RIT5,0)));
            hstDB.put(F_TOKIEKI5,ns(rs_o4101.getString2(F_TOKIEKI5,0)));
            hstDB.put(F_TOKIEKI_RIT5,ns(rs_o4101.getString2(F_TOKIEKI_RIT5,0)));
            hstDB.put(F_SHOKYAKUJISSHIGAK_TOKI5,ns(rs_o4101.getString2(F_SHOKYAKUJISSHIGAK_TOKI5,0)));
            hstDB.put(F_KSYSOCF,ns(rs_o4101.getString2(F_KSYSOCF,0)));
            hstDB.put(F_HAITO_RIT5,ns(rs_o4101.getString2(F_HAITO_RIT5,0)));
            hstDB.put(F_SHOMISHISAN5,ns(rs_o4101.getString2(F_SHOMISHISAN5,0)));
            hstDB.put(F_KARIIREKAITEN5,ns(rs_o4101.getString2(F_KARIIREKAITEN5,0)));
            hstDB.put(F_GRJTJNSSGK,ns(rs_o4101.getString2(F_GRJTJNSSGK,0)));

// 2003/09/12 ADD@S.SEIMURA 同時審査対応(00331)
            // 案件サマリー用の項目を取得
            hstDB.put(F_URISOEK1_ANK,ns(rs_o4101.getString2(F_URISOEK1_ANK,0)));
            hstDB.put(F_EIGYEK1_ANK,ns(rs_o4101.getString2(F_EIGYEK1_ANK,0)));
            hstDB.put(F_YRSLIAB1_ANK,ns(rs_o4101.getString2(F_YRSLIAB1_ANK,0)));
            hstDB.put(F_URISOEK2_ANK,ns(rs_o4101.getString2(F_URISOEK2_ANK,0)));
            hstDB.put(F_EIGYEK2_ANK,ns(rs_o4101.getString2(F_EIGYEK2_ANK,0)));
            hstDB.put(F_YRSLIAB2_ANK,ns(rs_o4101.getString2(F_YRSLIAB2_ANK,0)));


            // 計数情報(市場性与信状況)の項目を設定する
            hstDB.put(F_SJOSEIINF_ZNM1,ns(rs_o4101.getString2(F_SJOSEIINF_ZNM1,0)));
            hstDB.put(F_SJOSEIINF_ZNM2,ns(rs_o4101.getString2(F_SJOSEIINF_ZNM2,0)));
            hstDB.put(F_LMTINTL_RN_MEND_ZAN,ns(rs_o4101.getString2(F_LMTINTL_RN_MEND_ZAN,0)));
            hstDB.put(F_LMTINTL_RN_LMT,ns(rs_o4101.getString2(F_LMTINTL_RN_LMT,0)));
            hstDB.put(F_LMTINTL_RN_HONAF_ZAN,ns(rs_o4101.getString2(F_LMTINTL_RN_HONAF_ZAN,0)));
            hstDB.put(F_LMTINTL_RN_CEPERN_JI,ns(rs_o4101.getString2(F_LMTINTL_RN_CEPERN_JI,0)));
            hstDB.put(F_LMTINTL_RN_CERN_JITU,ns(rs_o4101.getString2(F_LMTINTL_RN_CERN_JITU,0)));
            hstDB.put(F_LMTINTL_RN_JZAN_PRCP,ns(rs_o4101.getString2(F_LMTINTL_RN_JZAN_PRCP,0)));
            hstDB.put(F_LMTOUT_RN1_SNINGK_PR,ns(rs_o4101.getString2(F_LMTOUT_RN1_SNINGK_PR,0)));
            hstDB.put(F_LMTOUT_RN1_JZAN_PRCP,ns(rs_o4101.getString2(F_LMTOUT_RN1_JZAN_PRCP,0)));
            hstDB.put(F_LMTOUT_RN2_SNINGK_PR,ns(rs_o4101.getString2(F_LMTOUT_RN2_SNINGK_PR,0)));
            hstDB.put(F_LMTOUT_RN2_JZAN_PRCP,ns(rs_o4101.getString2(F_LMTOUT_RN2_JZAN_PRCP,0)));
            hstDB.put(F_LMTOUT_RN3_SNINGK_PR,ns(rs_o4101.getString2(F_LMTOUT_RN3_SNINGK_PR,0)));
            hstDB.put(F_LMTOUT_RN3_JZAN_PRCP,ns(rs_o4101.getString2(F_LMTOUT_RN3_JZAN_PRCP,0)));
            hstDB.put(F_LMTOUTTL_RN_SNINGK_P,ns(rs_o4101.getString2(F_LMTOUTTL_RN_SNINGK_P,0)));
            hstDB.put(F_LMTOUTTL_RN_JZAN_PRC,ns(rs_o4101.getString2(F_LMTOUTTL_RN_JZAN_PRC,0)));
            hstDB.put(F_SIJOYSNRN_MEND_ZAN,ns(rs_o4101.getString2(F_SIJOYSNRN_MEND_ZAN,0)));
            hstDB.put(F_SIJOYSNRN_LMT,ns(rs_o4101.getString2(F_SIJOYSNRN_LMT,0)));
            hstDB.put(F_SIJOYSNRN_HONAF_ZAN,ns(rs_o4101.getString2(F_SIJOYSNRN_HONAF_ZAN,0)));
            hstDB.put(F_SIJOYSNRN_CEPERN_JITU_ZAN1,ns(rs_o4101.getString2(F_SIJOYSNRN_CEPERN_JITU_ZAN1,0)));
            hstDB.put(F_SIJOYSNRN_CERN_JITU_ZAN1,ns(rs_o4101.getString2(F_SIJOYSNRN_CERN_JITU_ZAN1,0)));
            hstDB.put(F_SIJOYSNRN_JZAN_PRCPAL,ns(rs_o4101.getString2(F_SIJOYSNRN_JZAN_PRCPAL,0)));


            // 計数情報(参考計数)の項目を設定する
            hstDB.put(F_REFKESR1_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR1_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR1_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR1_NT_JZAN_CE,0)));
            hstDB.put(F_REFKESR2_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR2_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR2_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR2_NT_JZAN_CE,0)));
            hstDB.put(F_REFKESR3_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR3_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR3_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR3_NT_JZAN_CE,0)));
            hstDB.put(F_REFKESR4_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR4_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR4_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR4_NT_JZAN_CE,0)));
            hstDB.put(F_REFKESR5_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR5_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR5_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR5_NT_JZAN_CE,0)));
            hstDB.put(F_REFKESR6_NT_JZAN_CEPE,ns(rs_o4101.getString2(F_REFKESR6_NT_JZAN_CEPE,0)));
            hstDB.put(F_REFKESR6_NT_JZAN_CE,ns(rs_o4101.getString2(F_REFKESR6_NT_JZAN_CE,0)));


            // 計数情報(自己査定)の項目を設定する
            hstDB.put(F_HIBNRI_GK,ns(rs_o4101.getString2(F_HIBNRI_GK,0)));
            hstDB.put(F_TWO_BNRUI_GK,ns(rs_o4101.getString2(F_TWO_BNRUI_GK,0)));
            hstDB.put(F_THREE_BNRUI_GK,ns(rs_o4101.getString2(F_THREE_BNRUI_GK,0)));
            hstDB.put(F_FOUR_BNRUI_GK,ns(rs_o4101.getString2(F_FOUR_BNRUI_GK,0)));
            hstDB.put(F_TOT,ns(rs_o4101.getString2(F_TOT,0)));
            hstDB.put(F_UYKNRSKN,ns(rs_o4101.getString2(F_UYKNRSKN,0)));
            hstDB.put(F_CRERLT_CST,ns(rs_o4101.getString2(F_CRERLT_CST,0)));


            // 計数情報(主要行取引状況)の項目を設定する
            hstDB.put(F_JYOIBKNAME1,ns(rs_o4101.getString2(F_JYOIBKNAME1,0)));
            hstDB.put(F_JYOIBKNAME2,ns(rs_o4101.getString2(F_JYOIBKNAME2,0)));
            hstDB.put(F_JYOIBKNAME3,ns(rs_o4101.getString2(F_JYOIBKNAME3,0)));
            hstDB.put(F_MBKY1ME,ns(rs_o4101.getString2(F_MBKY1ME,0)));
            hstDB.put(F_MBKY2ME,ns(rs_o4101.getString2(F_MBKY2ME,0)));
            hstDB.put(F_MBKZNM,ns(rs_o4101.getString2(F_MBKZNM,0)));
            hstDB.put(F_MBKGAISHARE,ns(rs_o4101.getString2(F_MBKGAISHARE,0)));
            hstDB.put(F_SHAREY1ME,ns(rs_o4101.getString2(F_SHAREY1ME,0)));
            hstDB.put(F_SHAREY2ME,ns(rs_o4101.getString2(F_SHAREY2ME,0)));
            hstDB.put(F_SHAREZNM,ns(rs_o4101.getString2(F_SHAREZNM,0)));
            hstDB.put(F_JYOIBK1Y1ME,ns(rs_o4101.getString2(F_JYOIBK1Y1ME,0)));
            hstDB.put(F_JYOIBK1Y2ME,ns(rs_o4101.getString2(F_JYOIBK1Y2ME,0)));
            hstDB.put(F_JYOIBK1ZNM,ns(rs_o4101.getString2(F_JYOIBK1ZNM,0)));
            hstDB.put(F_JYOIBK1GAISHR,ns(rs_o4101.getString2(F_JYOIBK1GAISHR,0)));
            hstDB.put(F_JYOIBK2Y1ME,ns(rs_o4101.getString2(F_JYOIBK2Y1ME,0)));
            hstDB.put(F_JYOIBK2Y2ME,ns(rs_o4101.getString2(F_JYOIBK2Y2ME,0)));
            hstDB.put(F_JYOIBK2ZNM,ns(rs_o4101.getString2(F_JYOIBK2ZNM,0)));
            hstDB.put(F_JYOIBK2GAISHR,ns(rs_o4101.getString2(F_JYOIBK2GAISHR,0)));
            hstDB.put(F_JYOIBK3Y1ME,ns(rs_o4101.getString2(F_JYOIBK3Y1ME,0)));
            hstDB.put(F_JYOIBK3Y2ME,ns(rs_o4101.getString2(F_JYOIBK3Y2ME,0)));
            hstDB.put(F_JYOIBK3ZNM,ns(rs_o4101.getString2(F_JYOIBK3ZNM,0)));
            hstDB.put(F_JYOIBK3GAISHR,ns(rs_o4101.getString2(F_JYOIBK3GAISHR,0)));
            hstDB.put(F_SOKIY1ME,ns(rs_o4101.getString2(F_SOKIY1ME,0)));
            hstDB.put(F_SOKIY2ME,ns(rs_o4101.getString2(F_SOKIY2ME,0)));
            hstDB.put(F_SOKIZNM,ns(rs_o4101.getString2(F_SOKIZNM,0)));
            hstDB.put(F_SOKIGAISHR,ns(rs_o4101.getString2(F_SOKIGAISHR,0)));


            // 計数情報(取引採算)の項目を設定する
            hstDB.put(F_TANI_KEISU_TORISAI,ns(rs_o4101.getString2(F_TANI_KEISU_TORISAI,0)));
            hstDB.put(F_TANICD_KEISU_TORISAI,ns(rs_o4101.getString2(F_TANICD_KEISU_TORISAI,0)));
            hstDB.put(F_KAKM6FROM,ns(rs_o4101.getString2(F_KAKM6FROM,0)));
            hstDB.put(F_KAKM6TO,ns(rs_o4101.getString2(F_KAKM6TO,0)));
            hstDB.put(F_S_ELKANRIGAKU_RATE_S_EL1,ns(rs_o4101.getString2(F_S_ELKANRIGAKU_RATE_S_EL1,0)));
            hstDB.put(F_S_ELKANRIGAKU_RATE_S_EL2,ns(rs_o4101.getString2(F_S_ELKANRIGAKU_RATE_S_EL2,0)));
            hstDB.put(F_S_ELKANRIGAKU_RATE1,ns(rs_o4101.getString2(F_S_ELKANRIGAKU_RATE1,0)));
            hstDB.put(F_S_ELKANRIGAKU_RATE2,ns(rs_o4101.getString2(F_S_ELKANRIGAKU_RATE2,0)));
            hstDB.put(F_S_ELKANRIRITU_RATE1,ns(rs_o4101.getString2(F_S_ELKANRIRITU_RATE1,0)));
            hstDB.put(F_S_ELKANRIRITU_RATE2,ns(rs_o4101.getString2(F_S_ELKANRIRITU_RATE2,0)));
            hstDB.put(F_GR_S_ELKANRIGAKU_RATE1,ns(rs_o4101.getString2(F_GR_S_ELKANRIGAKU_RATE1,0)));
            hstDB.put(F_GR_S_ELKANRIGAKU_RATE2,ns(rs_o4101.getString2(F_GR_S_ELKANRIGAKU_RATE2,0)));
            hstDB.put(F_GR_S_ELKANRIRITU_RATE1,ns(rs_o4101.getString2(F_GR_S_ELKANRIRITU_RATE1,0)));
            hstDB.put(F_GR_S_ELKANRIRITU_RATE2,ns(rs_o4101.getString2(F_GR_S_ELKANRIRITU_RATE2,0)));


            // 計数情報(本件後引当状況)の項目を設定する…[配列設定]
            // 規定値・合計の各項目を設定する
            // 時価ベース・合計の各項目を設定する
            String[] strKiteTot = new String[intHikiateTotNum];
            String[] strJikaTot = new String[intHikiateTotNum];

            for (i = int0; i < intHikiateTotNum; i++) {
                strKiteTot[i] = ns(rs_o4101.getString2(strHikiateKiteitiTot[i],int0));
                strJikaTot[i] = ns(rs_o4101.getString2(strHikiateJikaTot[i],int0));
            }
            hstDB.put(F_HIKIATE_KITEITI_TOT,strKiteTot);
            hstDB.put(F_HIKIATE_JIKA_TOT,strJikaTot);

            // 規定値の各項目を設定する
            // 時価ベースの各項目を設定する
            String[] strKite = new String[intHikiateNum];
            String[] strJika = new String[intHikiateNum];

            for (i = int0; i < intHikiateNum; i++) {
                strKite[i] = ns(rs_o4101.getString2(strHikiateKiteiti[i],int0));
                strJika[i] = ns(rs_o4101.getString2(strHikiateJika[i],int0));
            }
            hstDB.put(F_HIKIATE_KITEITI,strKite);
            hstDB.put(F_HIKIATE_JIKA,strJika);
//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
            // 裸与信対象与信合計を設定
            hstDB.put(F_STRCRE_TSHO_TOT,ns(rs_o4101.getString2(F_STRCRE_TSHO_TOT,0)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

// 2003/09/12 ADD@S.SEIMURA 同時審査対応(00331)
            // 付属資料用の項目を取得
            hstDB.put(F_RYTNPM1_SCTY,ns(rs_o4101.getString2(F_RYTNPM1_SCTY,0)));
            hstDB.put(F_RYTNPM2_SCTY,ns(rs_o4101.getString2(F_RYTNPM2_SCTY,0)));
            hstDB.put(F_IPTNPM1_SCTY,ns(rs_o4101.getString2(F_IPTNPM1_SCTY,0)));
            hstDB.put(F_IPTNPM2_SCTY,ns(rs_o4101.getString2(F_IPTNPM2_SCTY,0)));


            // 計数情報(本件後市場性与信引当状況)の項目を設定する
            hstDB.put(F_KITANYKNKITE,ns(rs_o4101.getString2(F_KITANYKNKITE,0)));
            hstDB.put(F_KITANYKNSNKO,ns(rs_o4101.getString2(F_KITANYKNSNKO,0)));
            hstDB.put(F_KITANTANTKITE,ns(rs_o4101.getString2(F_KITANTANTKITE,0)));
            hstDB.put(F_KITANTANTSNKO,ns(rs_o4101.getString2(F_KITANTANTSNKO,0)));
            hstDB.put(F_KITANSCTYKITE,ns(rs_o4101.getString2(F_KITANSCTYKITE,0)));
            hstDB.put(F_KITANSCTYSNKO,ns(rs_o4101.getString2(F_KITANSCTYSNKO,0)));
            hstDB.put(F_KITANHSYKITE,ns(rs_o4101.getString2(F_KITANHSYKITE,0)));
            hstDB.put(F_KITANHSYSNKO,ns(rs_o4101.getString2(F_KITANHSYSNKO,0)));
            hstDB.put(F_KITANFUDOKITE,ns(rs_o4101.getString2(F_KITANFUDOKITE,0)));
            hstDB.put(F_KITANFUDOSNKO,ns(rs_o4101.getString2(F_KITANFUDOSNKO,0)));
            hstDB.put(F_KITANTAKITE,ns(rs_o4101.getString2(F_KITANTAKITE,0)));
            hstDB.put(F_KITANTASNKO,ns(rs_o4101.getString2(F_KITANTASNKO,0)));
            hstDB.put(F_KITANKIKITE,ns(rs_o4101.getString2(F_KITANKIKITE,0)));
            hstDB.put(F_KITANKISNKO,ns(rs_o4101.getString2(F_KITANKISNKO,0)));

            hstDB.put(F_STRCREKITE,ns(rs_o4101.getString2(F_STRCREKITE_SHIJO,0)));
            hstDB.put(F_STRCRESNKO,ns(rs_o4101.getString2(F_STRCRESNKO,0)));
            hstDB.put(F_KGITTTMKOM,ns(rs_o4101.getString2(F_KGITTTMKOM,0)));
            hstDB.put(F_KGITTTSNKO,ns(rs_o4101.getString2(F_KGITTTSNKO,0)));
            hstDB.put(F_KGITFDMKOM,ns(rs_o4101.getString2(F_KGITFDMKOM,0)));
            hstDB.put(F_KGITFDSNKO,ns(rs_o4101.getString2(F_KGITFDSNKO,0)));
            hstDB.put(F_KGITNHMKOM,ns(rs_o4101.getString2(F_KGITNHMKOM,0)));
            hstDB.put(F_HKGITNHSNKO,ns(rs_o4101.getString2(F_HKGITNHSNKO,0)));
            hstDB.put(F_KGITSKMKOM,ns(rs_o4101.getString2(F_KGITSKMKOM,0)));
            hstDB.put(F_HKGITSKSNKO,ns(rs_o4101.getString2(F_HKGITSKSNKO,0)));
            hstDB.put(F_KGITTAMKOM,ns(rs_o4101.getString2(F_KGITTAMKOM,0)));
            hstDB.put(F_HKGITTASNKO,ns(rs_o4101.getString2(F_HKGITTASNKO,0)));
            hstDB.put(F_KGITMKOM,ns(rs_o4101.getString2(F_KGITMKOM,0)));
            hstDB.put(F_KGITSNKO,ns(rs_o4101.getString2(F_KGITSNKO,0)));


            // 計数情報(一般与信状況明細)の項目を設定する…[一部配列設定]
            // 表示指定月を設定する
            hstDB.put(F_ZNM,ns(rs_o4102.getString2(F_ZNM,int0)));

            // 限度算入与信合計の各項目を設定する
            String[] strMendZanTot = {ns(rs_o4102.getString2(F_MEND_ZAN,int0))};
            hstDB.put(F_MEND_ZAN_TOT,strMendZanTot);

            String[] strLmtTot = {ns(rs_o4102.getString2(F_LMT,int0))};
            hstDB.put(F_LMT_TOT,strLmtTot);

            String[] strIpnYsnDltzggTot = {ns(rs_o4102.getString2(F_IPNYSNDLTZGG,int0))};
            hstDB.put(F_IPNYSNDLTZGG_TOT,strIpnYsnDltzggTot);

            String[] strHonafZanTot = {ns(rs_o4102.getString2(F_HONAF_ZAN,int0))};
            hstDB.put(F_HONAF_ZAN_TOT,strHonafZanTot);

            String[] strJisksnTot = {ns(rs_o4102.getString2(F_JISKSN,int0))};
            hstDB.put(F_JISKSN_TOT,strJisksnTot);

            // 一般与信の各項目を設定する
            String[] strKmk = new String[intIpnYsnNum];
            String[] strKbi = new String[intIpnYsnNum];
            String[] strRt = new String[intIpnYsnNum];
            String[] strMendZan = new String[intIpnYsnNum];
            String[] strGsnlmtHj = new String[intIpnYsnNum];
            String[] strLmt = new String[intIpnYsnNum];
            String[] strIpnysndltzgg = new String[intIpnYsnNum];
            String[] strHonafZan = new String[intIpnYsnNum];
            String[] strJisksn = new String[intIpnYsnNum];
            String[] strHosch = new String[intIpnYsnNum];
// 2003/09/12 ADD@S.SEIMURA (00331)
            String[] strBnruiCd = new String[intIpnYsnNum];
// GEC294-C-004 S
            String[] strRsno = new String[intIpnYsnNum];
            String[] strKmkRsno = new String[intIpnYsnNum];
// GEC294-C-004 E

            for (i = int0; i < intIpnYsnNum; i++) {
                strKmk[i] = ns(rs_o4102.getString2(F_KMK_RMT,i + int1));
                strKbi[i] = ns(rs_o4102.getString2(F_KBI,i + int1));
                strRt[i] = ns(rs_o4102.getString2(F_RT,i + int1));
                strMendZan[i] = ns(rs_o4102.getString2(F_MEND_ZAN,i + int1));
                strGsnlmtHj[i] = ns(rs_o4102.getString2(F_GSNLMT_HJ,i + int1));
                strLmt[i] = ns(rs_o4102.getString2(F_LMT,i + int1));
                strIpnysndltzgg[i] = ns(rs_o4102.getString2(F_IPNYSNDLTZGG,i + int1));
                strHonafZan[i] = ns(rs_o4102.getString2(IRingiItemKeisu.F_HONAF_ZAN,i + int1));
                strJisksn[i] = ns(rs_o4102.getString2(F_JISKSN,i + int1));
                strHosch[i] = ns(rs_o4102.getString2(F_HOSCH,i + int1));
// 2003/09/12 ADD@S.SEIMURA (00331)
                strBnruiCd[i] = ns(rs_o4102.getString2(F_BNRUICD,i + int1));
// GEC294-C-004 S
                strRsno[i] = ns(rs_o4102.getString2(F_YSNMEISAI_RSNO,i + int1));
                if ( V_EMPTY_STRING.equals(ns(rs_o4102.getString2(F_YSNMEISAI_RSNO,i + int1)))) {
                    strKmkRsno[i] = ns(rs_o4102.getString2(F_KMK_RMT,i + int1));
                } else {
                    strKmkRsno[i] = ns(rs_o4102.getString2(F_KMK_RMT,i + int1)) + V_COLON_STRING +ns(rs_o4102.getString2(F_YSNMEISAI_RSNO,i + int1));
                }
// GEC294-C-004 E
            }

// 2005/02/08 ADD M.Kudo START (GEC16-C-143-005)
            // 配列要素の順序を画面にあわせる
            strKmk              = RLRRG004_B01.chgYosinDbToDisp(strKmk);
            strKbi              = RLRRG004_B01.chgYosinDbToDisp(strKbi);
            strRt               = RLRRG004_B01.chgYosinDbToDisp(strRt);
            strMendZan          = RLRRG004_B01.chgYosinDbToDisp(strMendZan);

//計数情報(限度算入与信状況明細)---------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(限度算入与信状況明細)の項目を登録更新する
            if(updflg.equals("on")){
                //10回繰り返す
                for(i = int1;i <= intGendSannyuNum; i++){

                    //SQLパラメータを設定する
                    dbparam = setParamGendo(hstKey, strReqid, strUserId, i);

                    //更新処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_681, SQL_4121, dbparam});

                    //(SQL-ID=rlrrg_o4121)(PreparedStatement)
                    int rs_o4121 = dbcon.executeUpdatePS(SQL_4121,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_682, SQL_4121});
                }
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(限度算入与信状況明細)の項目の追加を行う
            if(updflg.equals("off")){

                //10回繰り返す
                for(j = int1; j <= intGendSannyuNum; j++){

                    //SQLパラメータを設定する
                    dbparam = setParamGendo(hstKey, strReqid, strUserId, j);

                    // 補正区分を"0"に設定する。
                    strHoseikubunTemp = V_HOSEI_MAE;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_683, SQL_4122, dbparam});

                    //(SQL-ID=rlrrg_o4122)(PreparedStatement)
                    int rs_o4122 = dbcon.executeUpdatePS(SQL_4122,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_684, SQL_4122});

                    if(rs_o4122 != int0){

                        // 補正区分を"1"に設定する。
                        strHoseikubunTemp = V_HOSEI_ATO;
                        dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                        //挿入処理を実行し戻り値を取得する
                        // CP検証メッセージ：開始
                        logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_685, SQL_4122, dbparam});

                        //(SQL-ID=rlrrg_o4122)(PreparedStatement)
                        int rs_o4122_2 = dbcon.executeUpdatePS(SQL_4122,dbparam);

                        // CP検証メッセージ：終了
                        logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_686, SQL_4122});
                    }
                }
            }




//計数情報(市場性与信状況)-------------------------------

// 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(市場性与信状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamShijo(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_687, SQL_4123, dbparam});

                //(SQL-ID=rlrrg_o4123)(PreparedStatement)
                int rs_o4123 = dbcon.executeUpdatePS(SQL_4123,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_688, SQL_4123});
            }

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                //SQLパラメータを設定する
                dbparam = setParamShijo(hstKey, strReqid, strUserId);
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_689, SQL_4124, dbparam});

                //(SQL-ID=rlrrg_o4124)(PreparedStatement)
                int rs_o4124 = dbcon.executeUpdatePS(SQL_4124,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_690, SQL_4124});

                if(rs_o4124 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_691, SQL_4124, dbparam});

                    //(SQL-ID=rlrrg_o4124)(PreparedStatement)
                    int rs_o4124_2 = dbcon.executeUpdatePS(SQL_4124,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_692, SQL_4124});
                }
            }



//計数情報(参考計数)--------------------------------------

// m.isogai 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(参考計数)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamSanko(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_693, SQL_4125, dbparam});

                //(SQL-ID=rlrrg_o4125)(PreparedStatement)
                int rs_o4125 = dbcon.executeUpdatePS(SQL_4125,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_694, SQL_4125});
            }

// m.isogai 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamSanko(hstKey, strReqid, strUserId);


                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_695, SQL_4126, dbparam});

                //(SQL-ID=rlrrg_o4126)(PreparedStatement)
                int rs_o4126 = dbcon.executeUpdatePS(SQL_4126,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_696, SQL_4126});

                if(rs_o4126 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_697, SQL_4126, dbparam});

                    //(SQL-ID=rlrrg_o4126)(PreparedStatement)
                    int rs_o4126_2 = dbcon.executeUpdatePS(SQL_4126,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_698, SQL_4126});
                }
            }



//計数情報(自己査定)--------------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(自己査定)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamJikoSatei(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_699, SQL_4127, dbparam});

                //(SQL-ID=rlrrg_o4127)(PreparedStatement)
                int rs_o4127 = dbcon.executeUpdatePS(SQL_4127,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_700, SQL_4127});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamJikoSatei(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_701, SQL_4128, dbparam});

                //(SQL-ID=rlrrg_o4128)(PreparedStatement)
                int rs_o4128 = dbcon.executeUpdatePS(SQL_4128,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_702, SQL_4128});

                if(rs_o4128 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_703, SQL_4128, dbparam});

                    //(SQL-ID=rlrrg_o4128)(PreparedStatement)
                    int rs_o4128_2 = dbcon.executeUpdatePS(SQL_4128,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_704, SQL_4128});
                }
            }



//計数情報(主要取引状況)------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(主要取引状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamShuyouBank(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_705, SQL_4129, dbparam});

                //(SQL-ID=rlrrg_o4129)(PreparedStatement)
                int rs_o4129 = dbcon.executeUpdatePS(SQL_4129,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_706, SQL_4129});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(主要取引状況)の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamShuyouBank(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_707, SQL_4130, dbparam});

                //(SQL-ID=rlrrg_o4130)(PreparedStatement)
                int rs_o4130 = dbcon.executeUpdatePS(SQL_4130,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_708, SQL_4130});

                if(rs_o4130 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_709, SQL_4130, dbparam});

                    //(SQL-ID=rlrrg_o4130)(PreparedStatement)
                    int rs_o4130_2 = dbcon.executeUpdatePS(SQL_4130,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_710, SQL_4130});
                }
            }



//計数情報(取引採算)----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(取引採算)の項目を登録更新する
            if(updflg.equals("on")){
                //SQLパラメータを設定する
                dbparam = setParamTorihikiSaisan(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_711, SQL_4131, dbparam});

                //(SQL-ID=rlrrg_o4131)(PreparedStatement)
                int rs_o4131 = dbcon.executeUpdatePS(SQL_4131,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_712, SQL_4131});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(取引採算)の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamTorihikiSaisan(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_713, SQL_4132, dbparam});

                //(SQL-ID=rlrrg_o4132)(PreparedStatement)
                int rs_o4132 = dbcon.executeUpdatePS(SQL_4132,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_714, SQL_4132});

                if(rs_o4132 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_715, SQL_4132, dbparam});

                    //(SQL-ID=rlrrg_o4132)(PreparedStatement)
                    int rs_o4132_2 = dbcon.executeUpdatePS(SQL_4132,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_716, SQL_4132});
                }
            }



//計数情報(保証人)-----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更
                // Key共通領域より各配列を取得
                strHoshoninTemp = nsa( hstKey.get(F_HSN_NM), intIpnYsnNum );

            // アップデートフラグがonの場合、計数情報(保証人)の項目を登録更新する
            if(updflg.equals("on")){


                //5回繰り返す
                for(i = int1; i <= intHoshoninNum; i++){

                    //SQLパラメータを設定する
                    dbparam = setParamHoshonin(hstKey, strReqid, strUserId, i);

                    //更新処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_717, SQL_4133, dbparam});

                    //(SQL-ID=rlrrg_o4133)(PreparedStatement)
                    int rs_o4133 = dbcon.executeUpdatePS(SQL_4133,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_718, SQL_4133});
                }
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(保証人)の項目の追加を行う
            if(updflg.equals("off")){

                //5回繰り返す
                for(j = int1; j <= intHoshoninNum; j++){

                     //SQLパラメータを設定する
                    dbparam = setParamHoshonin(hstKey, strReqid, strUserId, j);

                    // 補正区分を"0"に設定する。
                    strHoseikubunTemp = V_HOSEI_MAE;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_719, SQL_4134, dbparam});

                    //(SQL-ID=rlrrg_o4134)(PreparedStatement)
                    int rs_o4134 = dbcon.executeUpdatePS(SQL_4134,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_720, SQL_4134});

                    if(rs_o4134 != int0){
                        // 補正区分を"1"に設定する。
                        strHoseikubunTemp = V_HOSEI_ATO;
                        dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                        //挿入処理を実行し戻り値を取得する
                        // CP検証メッセージ：開始
                        logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_721, SQL_4134, dbparam});

                        //(SQL-ID=rlrrg_o4134)(PreparedStatement)
                        int rs_o4134_2 = dbcon.executeUpdatePS(SQL_4134,dbparam);

                        // CP検証メッセージ：終了
                        logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_722, SQL_4134});
                    }
                }
            }



//計数情報(本件後引当状況)-------------------------------------------------

// 2003.9.2 m.isogai 判定方法変更
                //SQLパラメータを設定する
                dbparam = setParamHonkengo(hstKey, strReqid, strUserId);

                // 付属資料で使用する項目を設定する
                dbparam.setParameter(F_RYTNPM1_SCTY.toLowerCase(),(String)no(hstKey.get(F_RYTNPM1_SCTY)));
                dbparam.setParameter(F_RYTNPM2_SCTY.toLowerCase(),(String)no(hstKey.get(F_RYTNPM2_SCTY)));
                dbparam.setParameter(F_IPTNPM1_SCTY.toLowerCase(),(String)no(hstKey.get(F_IPTNPM1_SCTY)));
                dbparam.setParameter(F_IPTNPM2_SCTY.toLowerCase(),(String)no(hstKey.get(F_IPTNPM2_SCTY)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
                // 裸与信対象与信合計を設定する
                dbparam.setParameter(F_STRCRE_TSHO_TOT.toLowerCase(),(String)no(hstKey.get(F_STRCRE_TSHO_TOT)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

            // アップデートフラグがonの場合、計数情報(本件後引当状況)の項目を登録更新する
            if(updflg.equals("on")){


                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_723, SQL_4135, dbparam});

                //(SQL-ID=rlrrg_o4135)(PreparedStatement)
                int rs_o4135 = dbcon.executeUpdatePS(SQL_4135,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_724, SQL_4135});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_725, SQL_4136, dbparam});

                //(SQL-ID=rlrrg_o4136)(PreparedStatement)
                int rs_o4136 = dbcon.executeUpdatePS(SQL_4136,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_726, SQL_4136});

                if(rs_o4136 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_727, SQL_4136, dbparam});

                    //(SQL-ID=rlrrg_o4136)(PreparedStatement)
                    int rs_o4136_2 = dbcon.executeUpdatePS(SQL_4136,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_728, SQL_4136});
                }
            }



//計数情報(本件後市場性与信引当状況)----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(本件後市場性与信引当状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamHonkengoShijo(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_729, SQL_4137, dbparam});

                //(SQL-ID=rlrrg_o4137)(PreparedStatement)
                int rs_o4137 = dbcon.executeUpdatePS(SQL_4137,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_730, SQL_4137});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamHonkengoShijo(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_731, SQL_4138, dbparam});

                //(SQL-ID=rlrrg_o4138)(PreparedStatement)
                int rs_o4138 = dbcon.executeUpdatePS(SQL_4138,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_732, SQL_4138});

                if(rs_o4138 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_733, SQL_4138, dbparam});

                    //(SQL-ID=rlrrg_o4138)(PreparedStatement)
                    int rs_o4138_2 = dbcon.executeUpdatePS(SQL_4138,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_734, SQL_4138});
                }
            }

            //終了処理-----------------------------------------------------------
            hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_OK));

        }catch(com.ibm.jp.wacs.db.WACSDBException e){
            throw e;
        }catch(WACSSysException e){
            throw e;
        }catch(WACSApplException e){
            throw e;
        }finally{
        }

    }

//計数情報(限度算入与信状況明細)---------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(限度算入与信状況明細)の項目を登録更新する
            if(updflg.equals("on")){
                //10回繰り返す
                for(i = int1;i <= intGendSannyuNum; i++){

                    //SQLパラメータを設定する
                    dbparam = setParamGendo(hstKey, strReqid, strUserId, i);

                    //更新処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_681, SQL_4121, dbparam});

                    //(SQL-ID=rlrrg_o4121)(PreparedStatement)
                    int rs_o4121 = dbcon.executeUpdatePS(SQL_4121,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_682, SQL_4121});
                }
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(限度算入与信状況明細)の項目の追加を行う
            if(updflg.equals("off")){

                //10回繰り返す
                for(j = int1; j <= intGendSannyuNum; j++){

                    //SQLパラメータを設定する
                    dbparam = setParamGendo(hstKey, strReqid, strUserId, j);

                    // 補正区分を"0"に設定する。
                    strHoseikubunTemp = V_HOSEI_MAE;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_683, SQL_4122, dbparam});

                    //(SQL-ID=rlrrg_o4122)(PreparedStatement)
                    int rs_o4122 = dbcon.executeUpdatePS(SQL_4122,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_684, SQL_4122});

                    if(rs_o4122 != int0){

                        // 補正区分を"1"に設定する。
                        strHoseikubunTemp = V_HOSEI_ATO;
                        dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                        //挿入処理を実行し戻り値を取得する
                        // CP検証メッセージ：開始
                        logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_685, SQL_4122, dbparam});

                        //(SQL-ID=rlrrg_o4122)(PreparedStatement)
                        int rs_o4122_2 = dbcon.executeUpdatePS(SQL_4122,dbparam);

                        // CP検証メッセージ：終了
                        logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_686, SQL_4122});
                    }
                }
            }




//計数情報(市場性与信状況)-------------------------------

// 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(市場性与信状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamShijo(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_687, SQL_4123, dbparam});

                //(SQL-ID=rlrrg_o4123)(PreparedStatement)
                int rs_o4123 = dbcon.executeUpdatePS(SQL_4123,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_688, SQL_4123});
            }

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                //SQLパラメータを設定する
                dbparam = setParamShijo(hstKey, strReqid, strUserId);
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_689, SQL_4124, dbparam});

                //(SQL-ID=rlrrg_o4124)(PreparedStatement)
                int rs_o4124 = dbcon.executeUpdatePS(SQL_4124,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_690, SQL_4124});

                if(rs_o4124 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_691, SQL_4124, dbparam});

                    //(SQL-ID=rlrrg_o4124)(PreparedStatement)
                    int rs_o4124_2 = dbcon.executeUpdatePS(SQL_4124,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_692, SQL_4124});
                }
            }



//計数情報(参考計数)--------------------------------------

// m.isogai 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(参考計数)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamSanko(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_693, SQL_4125, dbparam});

                //(SQL-ID=rlrrg_o4125)(PreparedStatement)
                int rs_o4125 = dbcon.executeUpdatePS(SQL_4125,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_694, SQL_4125});
            }

// m.isogai 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamSanko(hstKey, strReqid, strUserId);


                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_695, SQL_4126, dbparam});

                //(SQL-ID=rlrrg_o4126)(PreparedStatement)
                int rs_o4126 = dbcon.executeUpdatePS(SQL_4126,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_696, SQL_4126});

                if(rs_o4126 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_697, SQL_4126, dbparam});

                    //(SQL-ID=rlrrg_o4126)(PreparedStatement)
                    int rs_o4126_2 = dbcon.executeUpdatePS(SQL_4126,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_698, SQL_4126});
                }
            }



//計数情報(自己査定)--------------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            //アップデートフラグがonの場合、計数情報(自己査定)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamJikoSatei(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_699, SQL_4127, dbparam});

                //(SQL-ID=rlrrg_o4127)(PreparedStatement)
                int rs_o4127 = dbcon.executeUpdatePS(SQL_4127,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_700, SQL_4127});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamJikoSatei(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_701, SQL_4128, dbparam});

                //(SQL-ID=rlrrg_o4128)(PreparedStatement)
                int rs_o4128 = dbcon.executeUpdatePS(SQL_4128,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_702, SQL_4128});

                if(rs_o4128 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_703, SQL_4128, dbparam});

                    //(SQL-ID=rlrrg_o4128)(PreparedStatement)
                    int rs_o4128_2 = dbcon.executeUpdatePS(SQL_4128,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_704, SQL_4128});
                }
            }



//計数情報(主要取引状況)------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(主要取引状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamShuyouBank(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_705, SQL_4129, dbparam});

                //(SQL-ID=rlrrg_o4129)(PreparedStatement)
                int rs_o4129 = dbcon.executeUpdatePS(SQL_4129,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_706, SQL_4129});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(主要取引状況)の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamShuyouBank(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_707, SQL_4130, dbparam});

                //(SQL-ID=rlrrg_o4130)(PreparedStatement)
                int rs_o4130 = dbcon.executeUpdatePS(SQL_4130,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_708, SQL_4130});

                if(rs_o4130 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_709, SQL_4130, dbparam});

                    //(SQL-ID=rlrrg_o4130)(PreparedStatement)
                    int rs_o4130_2 = dbcon.executeUpdatePS(SQL_4130,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_710, SQL_4130});
                }
            }



//計数情報(取引採算)----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(取引採算)の項目を登録更新する
            if(updflg.equals("on")){
                //SQLパラメータを設定する
                dbparam = setParamTorihikiSaisan(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_711, SQL_4131, dbparam});

                //(SQL-ID=rlrrg_o4131)(PreparedStatement)
                int rs_o4131 = dbcon.executeUpdatePS(SQL_4131,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_712, SQL_4131});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(取引採算)の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamTorihikiSaisan(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_713, SQL_4132, dbparam});

                //(SQL-ID=rlrrg_o4132)(PreparedStatement)
                int rs_o4132 = dbcon.executeUpdatePS(SQL_4132,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_714, SQL_4132});

                if(rs_o4132 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_715, SQL_4132, dbparam});

                    //(SQL-ID=rlrrg_o4132)(PreparedStatement)
                    int rs_o4132_2 = dbcon.executeUpdatePS(SQL_4132,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_716, SQL_4132});
                }
            }



//計数情報(保証人)-----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更
                // Key共通領域より各配列を取得
                strHoshoninTemp = nsa( hstKey.get(F_HSN_NM), intIpnYsnNum );

            // アップデートフラグがonの場合、計数情報(保証人)の項目を登録更新する
            if(updflg.equals("on")){


                //5回繰り返す
                for(i = int1; i <= intHoshoninNum; i++){

                    //SQLパラメータを設定する
                    dbparam = setParamHoshonin(hstKey, strReqid, strUserId, i);

                    //更新処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_717, SQL_4133, dbparam});

                    //(SQL-ID=rlrrg_o4133)(PreparedStatement)
                    int rs_o4133 = dbcon.executeUpdatePS(SQL_4133,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_718, SQL_4133});
                }
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報(保証人)の項目の追加を行う
            if(updflg.equals("off")){

                //5回繰り返す
                for(j = int1; j <= intHoshoninNum; j++){

                     //SQLパラメータを設定する
                    dbparam = setParamHoshonin(hstKey, strReqid, strUserId, j);

                    // 補正区分を"0"に設定する。
                    strHoseikubunTemp = V_HOSEI_MAE;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_719, SQL_4134, dbparam});

                    //(SQL-ID=rlrrg_o4134)(PreparedStatement)
                    int rs_o4134 = dbcon.executeUpdatePS(SQL_4134,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_720, SQL_4134});

                    if(rs_o4134 != int0){
                        // 補正区分を"1"に設定する。
                        strHoseikubunTemp = V_HOSEI_ATO;
                        dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                        //挿入処理を実行し戻り値を取得する
                        // CP検証メッセージ：開始
                        logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_721, SQL_4134, dbparam});

                        //(SQL-ID=rlrrg_o4134)(PreparedStatement)
                        int rs_o4134_2 = dbcon.executeUpdatePS(SQL_4134,dbparam);

                        // CP検証メッセージ：終了
                        logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_722, SQL_4134});
                    }
                }
            }



//計数情報(本件後引当状況)-------------------------------------------------

// 2003.9.2 m.isogai 判定方法変更
                //SQLパラメータを設定する
                dbparam = setParamHonkengo(hstKey, strReqid, strUserId);

                // 付属資料で使用する項目を設定する
                dbparam.setParameter(F_RYTNPM1_SCTY.toLowerCase(),(String)no(hstKey.get(F_RYTNPM1_SCTY)));
                dbparam.setParameter(F_RYTNPM2_SCTY.toLowerCase(),(String)no(hstKey.get(F_RYTNPM2_SCTY)));
                dbparam.setParameter(F_IPTNPM1_SCTY.toLowerCase(),(String)no(hstKey.get(F_IPTNPM1_SCTY)));
                dbparam.setParameter(F_IPTNPM2_SCTY.toLowerCase(),(String)no(hstKey.get(F_IPTNPM2_SCTY)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
                // 裸与信対象与信合計を設定する
                dbparam.setParameter(F_STRCRE_TSHO_TOT.toLowerCase(),(String)no(hstKey.get(F_STRCRE_TSHO_TOT)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

            // アップデートフラグがonの場合、計数情報(本件後引当状況)の項目を登録更新する
            if(updflg.equals("on")){


                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_723, SQL_4135, dbparam});

                //(SQL-ID=rlrrg_o4135)(PreparedStatement)
                int rs_o4135 = dbcon.executeUpdatePS(SQL_4135,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_724, SQL_4135});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_725, SQL_4136, dbparam});

                //(SQL-ID=rlrrg_o4136)(PreparedStatement)
                int rs_o4136 = dbcon.executeUpdatePS(SQL_4136,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_726, SQL_4136});

                if(rs_o4136 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_727, SQL_4136, dbparam});

                    //(SQL-ID=rlrrg_o4136)(PreparedStatement)
                    int rs_o4136_2 = dbcon.executeUpdatePS(SQL_4136,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_728, SQL_4136});
                }
            }



//計数情報(本件後市場性与信引当状況)----------------------------------------------

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがonの場合、計数情報(本件後市場性与信引当状況)の項目を登録更新する
            if(updflg.equals("on")){

                //SQLパラメータを設定する
                dbparam = setParamHonkengoShijo(hstKey, strReqid, strUserId);

                //更新処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_729, SQL_4137, dbparam});

                //(SQL-ID=rlrrg_o4137)(PreparedStatement)
                int rs_o4137 = dbcon.executeUpdatePS(SQL_4137,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_730, SQL_4137});
            }

// 2003.9.2 m.isogai 判定方法変更

            // アップデートフラグがoffの場合、計数情報の項目の追加を行う
            if(updflg.equals("off")){

                //SQLパラメータを設定する
                dbparam = setParamHonkengoShijo(hstKey, strReqid, strUserId);
                // 補正区分を"0"に設定する。
                strHoseikubunTemp = V_HOSEI_MAE;
                dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                //挿入処理を実行し戻り値を取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_731, SQL_4138, dbparam});

                //(SQL-ID=rlrrg_o4138)(PreparedStatement)
                int rs_o4138 = dbcon.executeUpdatePS(SQL_4138,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_732, SQL_4138});

                if(rs_o4138 != int0){

                    // 補正区分を"1"に設定する。
                    strHoseikubunTemp = V_HOSEI_ATO;
                    dbparam.setParameter(F_HOSEIKUBUN.toLowerCase(),strHoseikubunTemp);

                    //挿入処理を実行し戻り値を取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_733, SQL_4138, dbparam});

                    //(SQL-ID=rlrrg_o4138)(PreparedStatement)
                    int rs_o4138_2 = dbcon.executeUpdatePS(SQL_4138,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_734, SQL_4138});
                }
            }

            //終了処理-----------------------------------------------------------
            hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_OK));

        }catch(com.ibm.jp.wacs.db.WACSDBException e){
            throw e;
        }catch(WACSSysException e){
            throw e;
        }catch(WACSApplException e){
            throw e;
        }finally{
        }

    }

/**
 *　 <DL>
 *   <DT><b>メソッド概要:全項目更新</b><DD>
 *   禀議査定書(計数情報)の全項目を更新する。<BR>
 *   正し、表示項目のみを有するテーブルは更新しない。
 *   </DD></DT>
 *   </DL>
 *   <BR>
 *   @param      Hashtable        hstComBasket  共有情報
 *   @exception  WACSSysException
 *   @exception  com.ibm.jp.wacs.db.WACSDBException
 *   @exception  WACSApplException
 */
    public void setAllData (Hashtable hstComBasket)
                            throws com.ibm.jp.wacs.db.WACSDBException, WACSSysException, WACSApplException{
        try{
            //初期処理-------------------------------------------------------
            //forループで使用
            int i;

            //KEY共通領域のHashtableを取得する
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            //KEY共通領域の情報を取得
            String strLcNo = (String)hstKey.get(F_LC_NO);

            //操作者ユーザーIDを取得する
            WACSUser user    = getUser();
            String strUserId = user.getUserID();

            //リクエストIDを取得する
            String strReqid = folder.getREQID();


            //KEY共通領域に補正区分"1"を設定する
            String strHoseiKubun = V_HOSEI_ATO;
            hstKey.put(F_HOSEIKUBUN, strHoseiKubun);

            //禀議査定書(計数情報)の全項目を更新する-----------------------------------

            //計数情報の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamKeisu(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4151)(PreparedStatement)
            int rs_o4151 = dbcon.executeUpdatePS(SQL_4151,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4151 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }


            //計数情報(その他項目)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamSonota(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4152)(PreparedStatement)
            int rs_o4152 = dbcon.executeUpdatePS(SQL_4152,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4152 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }


            //計数情報(一般与信状況明細)の全項目を更新する ---------------------------------------------

            // Key共通領域より各配列を取得
            strBunruiTemp = nsa( hstKey.get(F_BNRUICD), intIpnYsnNum );
            strKbiTemp = nsa( hstKey.get(F_KBI), intIpnYsnNum );
// GEC294-C-004 S
//          strKmkTemp = nsa( hstKey.get(F_KMK_RMT), intIpnYsnNum );
            strKmkTemp = nsa( hstKey.get(F_KMK_RMT_LIST), intIpnYsnNum );
// GEC294-C-004 E
            strRtTemp = nsa( hstKey.get(F_RT), intIpnYsnNum );
            strMendZanTemp = nsa( hstKey.get(F_MEND_ZAN), intIpnYsnNum );
            strGsnlmtHjTemp = nsa( hstKey.get(F_GSNLMT_HJ), intIpnYsnNum );
            strLmtTemp = nsa( hstKey.get(F_LMT), intIpnYsnNum );
            strIpnysndltzggTemp = nsa( hstKey.get(F_IPNYSNDLTZGG), intIpnYsnNum );
            strHonafZanTemp = nsa( hstKey.get(IRingiItemKeisu.F_HONAF_ZAN), intIpnYsnNum );
            strJisksnTemp = nsa( hstKey.get(F_JISKSN), intIpnYsnNum );
            strHoschTemp= nsa( hstKey.get(F_HOSCH), intIpnYsnNum );
// GEC294-C-004 S
            strRsnoTemp = nsa( hstKey.get(F_RSNO_LIST), intIpnYsnNum );
// GEC294-C-004 E

// 2005/02/08 ADD M.Kudo START (GEC16-C-143-005)
            // 配列要素の順序をＤＢの項目にあわせる
            strBunruiTemp       = RLRRG004_B01.chgYosinDispToDb(strBunruiTemp);
            strKbiTemp          = RLRRG004_B01.chgYosinDispToDb(strKbiTemp);
            strKmkTemp          = RLRRG004_B01.chgYosinDispToDb(strKmkTemp);
            strRtTemp           = RLRRG004_B01.chgYosinDispToDb(strRtTemp);
            strMendZanTemp      = RLRRG004_B01.chgYosinDispToDb(strMendZanTemp);
            strGsnlmtHjTemp     = RLRRG004_B01.chgYosinDispToDb(strGsnlmtHjTemp);
            strLmtTemp          = RLRRG004_B01.chgYosinDispToDb(strLmtTemp);
            strIpnysndltzggTemp = RLRRG004_B01.chgYosinDispToDb(strIpnysndltzggTemp);
            strHonafZanTemp     = RLRRG004_B01.chgYosinDispToDb(strHonafZanTemp);
            strJisksnTemp       = RLRRG004_B01.chgYosinDispToDb(strJisksnTemp);
            strHoschTemp        = RLRRG004_B01.chgYosinDispToDb(strHoschTemp);
// GEC294-C-004 S
            strRsnoTemp     = RLRRG004_B01.chgYosinDispToDb(strRsnoTemp);
// GEC294-C-004 E
            // アップデートで行数が足りないと落ちてしまうので、行数のチェックおよび追加
            checkAndInsert(V_INSERT_TUNO_MAX, strReqid, strUserId);
// 2005/02/08 ADD M.Kudo END

            for(i = int1; i <= intIppanTotNum + intIpnYsnNum; i++){     //1～ intIppanTotNum + intIpnYsnNum カウントの繰り返し処理

                //SQLパラメータを設定する
                dbparam = setParamIppanYoshin(hstKey, strReqid, strUserId, i);

                //処理を実行し戻り値を取得する
                //(SQL-ID=rlrrg_o4154)(PreparedStatement)
                int rs_o4154 = dbcon.executeUpdatePS(SQL_4154,dbparam);

                //戻り値が0の場合、例外:WACSExceptionを発生させる。
                if(rs_o4154 == int0){
                    //エラー処理
                    WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                    throw e;
                }
            }

            //計数情報(経営指標決算期別明細)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamKeieiShihyo(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4155)(PreparedStatement)
            int rs_o4155 = dbcon.executeUpdatePS(SQL_4155,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4155 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }

            //計数情報(限度算入与信状況)の全項目を更新する ---------------------------------------------

            for(i = int1; i <= intGendSannyuNum; i++){  //1～10カウントの繰り返し処理

                //SQLパラメータを設定する
                dbparam = setParamGendo(hstKey, strReqid, strUserId, i);

                //処理を実行し戻り値を取得する
                //(SQL-ID=rlrrg_o4156)(PreparedStatement)
                int rs_o4156 = dbcon.executeUpdatePS(SQL_4156,dbparam);

                //戻り値が0の場合、例外:WACSExceptionを発生させる。
                if(rs_o4156 == int0){
                    //エラー処理
                    WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                    throw e;
                }
            }

            //計数情報(市場性与信状況)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamShijo(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4157)(PreparedStatement)
            int rs_o4157 = dbcon.executeUpdatePS(SQL_4157,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4157 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }


            //計数情報(参考計数)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamSanko(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4158)(PreparedStatement)
            int rs_o4158 = dbcon.executeUpdatePS(SQL_4158,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4158 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }


            //計数情報(主要行取引状況)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamShuyouBank(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4160)(PreparedStatement)
            int rs_o4160 = dbcon.executeUpdatePS(SQL_4160,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4160 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }

            //計数情報(本件後引当状況)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamHonkengo(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4163)(PreparedStatement)
            int rs_o4163 = dbcon.executeUpdatePS(SQL_4163,dbparam);

            //戻り値が0の場合、例外:WACSExceptionを発生させる。
            if(rs_o4163 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }

            //計数情報(本件後市場性与信引当状況)の全項目を更新する ---------------------------------------------

            //SQLパラメータを設定する
            dbparam = setParamHonkengoShijo(hstKey, strReqid, strUserId);

            //処理を実行し戻り値を取得する
            //(SQL-ID=rlrrg_o4164)(PreparedStatement)
            int rs_o4164 = dbcon.executeUpdatePS(SQL_4164,dbparam);
            //戻り値が0の場合、例外:WACSExceptionを発生させる。

            if(rs_o4164 == int0){
                //エラー処理
                WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                throw e;
            }


// 2003/02/26 ADD@S.SEIMURA 保証人を更新可能にする
            //計数情報(保証人)の項目を更新する

            // Key共通領域より各配列を取得
            strHoshoninTemp = nsa( hstKey.get(F_HSN_NM), intIpnYsnNum );

            // 5回繰り返す
            for(i = int1; i <= intHoshoninNum; i++){

                //SQLパラメータを設定する
                dbparam = setParamHoshonin(hstKey, strReqid, strUserId, i);

                //更新処理を実行し戻り値を取得する
                //(SQL-ID=rlrrg_o4162)(PreparedStatement)
                int rs_o4162 = dbcon.executeUpdatePS(SQL_4162,dbparam);

                //戻り値が0の場合、例外:WACSExceptionを発生させる。
                if(rs_o4162 == int0){
                    //エラー処理
                    WACSApplException e = createApplException(MSG_RRGS1019,null,null);
                    throw e;
                }

            }

            //終了処理-----------------------------------------------------------
            hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_OK));

        }catch(com.ibm.jp.wacs.db.WACSDBException e){
            throw e;
        }catch(WACSSysException e){
            throw e;
        }catch(WACSApplException e){
            throw e;
        }finally{
        }
    }

/**
 *　 <DL>
 *   <DT><b>メソッド概要:顧客系データ取得</b><DD>
 *   計数情報の外部(顧客系テーブル)より取得する項目を取得する。<BR>
 *   </DD></DT>
 *   </DL>
 *   <BR>
 *   @param      Hashtable        hstComBasket  共有情報
 *   @exception  WACSSysException
 *   @exception  com.ibm.jp.wacs.db.WACSDBException
 */
    public void getOutsideData(Hashtable hstComBasket)
                        throws com.ibm.jp.wacs.db.WACSDBException, WACSSysException, WACSApplException {

        try {
            // 初期処理 ---------------------------------------------------------
            int i;                  // forループ

            // DB共通領域のHashtableを取得する
            hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

            // KEY共通領域のHashtableを取得する
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            // KEY共通領域の情報を取得
            String strBrNo    = (String)hstKey.get(F_BRNO);
            String strTriskNo = (String)hstKey.get(F_TRISKNO);
            String strTaniMsg = (String)hstKey.get(F_TANI_MSG_1);



            // 計数全体の単位を求める
            if (strTaniMsg == V_NULL_STRING ||
                    strTaniMsg.trim().length() == int0) {
                strTani = V_EMPTY_STRING;

//          // 金額単位文言より金額単位コードを取得する
//          // コードユーティリティインスタンスを生成する。
            } else {
//              RLRCMCOM_CodeUtil instanceCode = new RLRCMCOM_CodeUtil(folder);
//              strTani = instanceCode.getCode(SQL_CODE_2023, strTaniMsg);
                strTaniMsg = strTaniMsg.trim();
                for ( i = 0; i < strHostTaniMsg.length; i++ ) {
                    if ( strTaniMsg.equals(strHostTaniMsg[i]) ) {
                        strTani = strHostTani[i];
                    }
                }
            }

            // 当日営業日を取得
            // カレンダークラスラッパーのインスタンスを取得する
            dbparam.clearAllData();
            RLRCMCOM_CalendarWrapper instanceCalendarWrap =
                                new RLRCMCOM_CalendarWrapper(folder,dbcon,dbparam);
            // 当日営業日取得メソッドをcallする
            String strToDay = instanceCalendarWrap.getEigyoDay();
            // 作成日として設定
            strMkbi = strToDay;


            // ------------------------------------------------------------------------
            // 組織店番、組織店名を取得する ---------------------------------------------
            // ------------------------------------------------------------------------
            String strSskBrNo = V_EMPTY_STRING;
            String strSskBrNm = V_EMPTY_STRING;

            // 店CIF関係クラスラッパーのインスタンスを取得する
            dbparam.clearAllData();
            RLRCMCOM_TenCIFWrapper instanceTenCifWrap =
                                new RLRCMCOM_TenCIFWrapper(folder,dbcon,dbparam);
            // 担当情報取得メソッドをcallする
            RLTCF001_001_R02 returnTenCifWrap =
                                instanceTenCifWrap.getTantoInfo(strBrNo, strTriskNo);
            // 処理結果がnullでない時、組織店番・店名を取得する。
            if (returnTenCifWrap != null) {
                strSskBrNo = returnTenCifWrap.getStrButenNo();
                // 2003/01/14 CHG@Seimura 仕様メソッド変更
                strSskBrNm = returnTenCifWrap.getStrButenRyakusyo();

                // 2003/01/15 CHG@Seimura ITAバグ029対応
                if (strSskBrNm.length() > int10) {
                    strSskBrNm = strSskBrNm.substring(int0, int10);
                }
            }
            // 組織店番
            hstDB.put(F_SSKBRNO,strSskBrNo);
            // 組織店名
            hstDB.put(F_SSKBRNM,strSskBrNm);


            // ------------------------------------------------------------------------
            // ------------------------------------------------------------------------
            // 顧客系などのテーブルからデータを取得する -------------------------------
            // ------------------------------------------------------------------------

            // 顧客情報テーブルのデータを取得する ----
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_601, SQL_0501, dbparam});

            // (SQL-ID=rlrrg_o0501)(PreparedStatement)
            rs_o0501 = dbcon.executeQueryPS(SQL_0501,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_602, SQL_0501});

            // 取得できた場合、GCIF番号を結果セットインスタンスより取得する
            if (rs_o0501.getNumResult() != int0) {
                String strGcifNo = (String)rs_o0501.getString2(F_GCIF_NO,int0);
            }

            // -------------------------------------------------------
            // 管理顧客代表店CIFを取得する ----
            // -------------------------------------------------------
// 2003/03/26 CHG@S.SEIMURA WACSApplExcpetionを吸収

            String strConDaihyoBrnoCif = V_EMPTY_STRING;
            String strDaihyoBrnoCif[]  = new String[2];

            RLRTPCOM_DaihyoBrnoCif instanceDaihyoBrnoCif =
                                        new RLRTPCOM_DaihyoBrnoCif(folder);
            dbparam.clearAllData();

            try {

                strDaihyoBrnoCif =
                        instanceDaihyoBrnoCif.getDaihyoBrnoCif(strBrNo,strTriskNo,dbcon,dbparam);

            } catch ( WACSApplException e ) {

                hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_DAIHYOU_TENCIF_NG));
                hstComBasket.put(K_DETAIL,e.getErrorCd());
                return;

            }

            // 7桁7桁の店CIFを連結する
            strConDaihyoBrnoCif = strDaihyoBrnoCif[int0].concat(strDaihyoBrnoCif[int1]);


            /*
             * 2004/09/30 ADD@S.SEIMURA(GEC16-C-012-711)
             * 代表店CIFをクラス変数に設定する
             */
            strDaihyouBrnoTriskno = strConDaihyoBrnoCif;



// 2004/02/02 CHG@S.SEIMURA 銀取レベルアップ(GEC15-C-080-215)
// START(GEC15-C-080-215)
            // -------------------------------------------------------
            // 名寄せ件数のデータを取得する ----
            // -------------------------------------------------------

            // 名寄せ件数テーブルからフラグの値を取得する
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_DAI_ATTR_NO.toLowerCase(),strConDaihyoBrnoCif);

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_643, SQL_4301, dbparam});

            // (SQL-ID=rlrrg_o4301)(PreparedStatement)
            rs_o4301 = dbcon.executeQueryPS(SQL_4301,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_644, SQL_4301});


            // -------------------------------------------------------
            // 銀取計数テーブルのデータを取得する ----
            // -------------------------------------------------------

            // プロパティファイルよりMTFGコード、当行コードを取得する
            String strToukou = getAppl2PropValue(F_TOUKOU_PROPCD);
            String strMTFG   = getAppl2PropValue(F_MTFG_PROPCD);

            String strSqlId = null;

            // 銀取計数テーブルから合計データを取得する
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_DAI_ATTR_NO.toLowerCase(),strConDaihyoBrnoCif);
            dbparam.setParameter(F_TOUKOU.toLowerCase(),strToukou);


//          // 検索処理を実行し結果セットインスタンスを取得する
//          // CP検証メッセージ：開始
//          logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_603, SQL_4181, dbparam});
//
//          // (SQL-ID=rlrrg_o4181)(PreparedStatement)
//          rs_o4181 = dbcon.executeQueryPS(SQL_4181,dbparam);
//
//          // CP検証メッセージ：終了
//          logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_604, SQL_4181});
//
//          // 銀取計数テーブルから当行のデータを取得する
//
//          // 検索処理を実行し結果セットインスタンスを取得する
//          // CP検証メッセージ：開始
//          logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_605, SQL_4182, dbparam});
//
//          // (SQL-ID=rlrrg_o4182)(PreparedStatement)
//          rs_o4182 = dbcon.executeQueryPS(SQL_4182,dbparam);
//
//          // CP検証メッセージ：終了
//          logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_606, SQL_4182});
//
//          // 銀取計数テーブルから上位３行のデータを取得する
//
//          // 検索処理を実行し結果セットインスタンスを取得する
//          // CP検証メッセージ：開始
//          logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_607, SQL_4183, dbparam});
//
//          // (SQL-ID=rlrrg_o4183)(PreparedStatement)
//          rs_o4183 = dbcon.executeQueryPS(SQL_4183,dbparam);
//
//          // CP検証メッセージ：終了
//          logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_608, SQL_4183});


            // ------------------------
            // 銀取総借入データを取得
            // ------------------------

            // SQLIDを取得(総借入)
            strSqlId = setGinkouTorihikiSqlId(1);

            // SQLIDが取得できたらSQLを実行する
            if ( strSqlId != null ) {
                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_603, strSqlId, dbparam});

                // (SQL-ID=strSqlId)(PreparedStatement)
                rs_o4181 = dbcon.executeQueryPS(strSqlId,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_604, strSqlId});
            }


            // ------------------------
            // 銀取当行データを取得
            // ------------------------

            // SQLIDを取得(当行)
            strSqlId = setGinkouTorihikiSqlId(2);

            // SQLIDが取得できたらSQLを実行する
            if ( strSqlId != null ) {
                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_605, strSqlId, dbparam});

                // (SQL-ID=strSqlId)(PreparedStatement)
                rs_o4182 = dbcon.executeQueryPS(strSqlId,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_606, strSqlId});
            }


            // ------------------------
            // 銀取上位三行データを取得
            // ------------------------

            // SQLIDを取得(上位三行)
            strSqlId = setGinkouTorihikiSqlId(3);

            // SQLIDが取得できたらSQLを実行する
            if ( strSqlId != null ) {
                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_607, strSqlId, dbparam});

                // (SQL-ID=strSqlId)(PreparedStatement)
                rs_o4183 = dbcon.executeQueryPS(strSqlId,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_608, strSqlId});
            }
// END(GEC15-C-080-215)



            // -------------------------------------------------------
            // 取引採算のデータを取得する ----
            // -------------------------------------------------------

            // データ保有最終月テーブルのデータを取得する ----

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_609, SQL_4056, dbparam});

            // (SQL-ID=rlrrg_o4056)(PreparedStatement)
            CraftsDBResult rs_o4056 = dbcon.executeQueryPS(SQL_4056,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_610, SQL_4056});

            // 結果セットインスタンスを判定し、データが取得できた場合、
            // データ保有最終月(YYYYMM形式)を設定する
            if (rs_o4056.getNumResult() != int0) {
                strHoyuLastMonth = ns(rs_o4056.getString2(F_HOYU_LASTTUKI,int0));
            }

            // データ保有最終月が、当月より2ヶ月以内であるかのチェックを行う
            // (データ保有最終月が、2002年8月であれば、当月は2002年10月、2002年9月ならOK)
            // 日付ユーティリティインスタンスを生成する
            if (instanceHiduke == null) {
                instanceHiduke = new RLTCF001_003_R01(folder);
            }

            // 対象日付取得(月数指定)メソッドをCALLする
            returnHiduke = instanceHiduke.addMonthR(strToDay, intM1, false);

            // 取得結果が成功の場合、当月より1ヶ月前の年月を取得する
            if (returnHiduke.getIntResult() == int0) {
                strTempYM = returnHiduke.getStrResultDate();

                // 当月より1ヶ月前の年月(YYYYMMの部分)とデータ保有最終月が一致した場合
                // 表示月(TO)に保有最終月を設定する
                if ( (strTempYM.substring(int0,int6)).equals(strHoyuLastMonth) == true ) {
                    strHyoujiTo = strHoyuLastMonth;

                // 1ヶ月前の年月と一致してない場合、2ヶ月前の年月と比較する
                } else {
                    // 対象日付取得(月数指定)メソッドをCALLする
                    returnHiduke = instanceHiduke.addMonthR(strToDay, intM2, false);

                    // 取得結果が成功の場合、当月より2ヶ月前の年月を取得する
                    if (returnHiduke.getIntResult() == int0) {
                        strTempYM = returnHiduke.getStrResultDate();

                        // 当月より2ヶ月前の年月(YYYYMMの部分)とデータ保有最終月が一致した場合
                        // 表示月(TO)に保有最終月を設定する
                        if ( (strTempYM.substring(int0,int6)).equals(strHoyuLastMonth) == true ) {
                            strHyoujiTo = strHoyuLastMonth;
                        }
                    }
                }
            }



            // 表示月(TO)が""以外の場合、表示月(FROM)を取得する
            // 表示月(TO)が2002年11月であれば、2002年6月
            if (strHyoujiTo.equals(V_EMPTY_STRING) != true) {
                // 対象日付取得(月数指定)メソッドをCALLする
                returnHiduke = instanceHiduke.addMonthR(
                                new StringBuffer().append(strHyoujiTo).append(str0 + str1).toString(),
                                intM5, false);

                // 取得結果が成功の場合、表示月(TO)より5ヶ月前の年月を取得する
                if (returnHiduke.getIntResult() == int0) {
                    strTempYM = returnHiduke.getStrResultDate();
                    // 取得した年月をYYYYMM形式に変換し、表示月(FROM)に設定する
                    strHyoujiFrom = strTempYM.substring(int0,int6);
                }
            }

            // 表示月(TO)、表示月(FROM)が""以外の場合、
            // 表示月(前年)(TO)、表示月(前年)(FROM)、を取得する
            if ( (strHyoujiTo.equals(V_EMPTY_STRING) != true) &&
                    (strHyoujiFrom.equals(V_EMPTY_STRING) != true) ) {
                // 対象日付取得(月数指定)メソッドをCALLする
                returnHiduke = instanceHiduke.addMonthR(
                                new StringBuffer().append(strHyoujiTo).append(str0 + str1).toString(),
                                intM12, false);

                // 取得結果が成功の場合、表示月(TO)より12ヶ月前の年月を取得する
                if (returnHiduke.getIntResult() == int0) {
                    strTempYM = returnHiduke.getStrResultDate();
                    // 取得した年月をYYYYMM形式に変換し、表示月(前年)(TO)に設定する
                    strHyoujiToAgo = strTempYM.substring(int0,int6);

                    // 対象日付取得(月数指定)メソッドをCALLする
                    returnHiduke = instanceHiduke.addMonthR(
                                    new StringBuffer().append(strHyoujiToAgo).append(str0 + str1).toString(),
                                    intM5, false);

                    // 取得結果が成功の場合、表示月(前年)(TO)より5ヶ月前の年月を取得する
                    if (returnHiduke.getIntResult() == int0) {
                        strTempYM = returnHiduke.getStrResultDate();
                        // 取得した年月をYYYYMM形式に変換し、表示月(前年)(FROM)に設定する
                        strHyoujiFromAgo = strTempYM.substring(int0,int6);
                    }
                }
            }


            // 取推管理顧客GCIF月次テーブルのデータを取得する ----

            // 表示月(TO)、表示月(FROM)が""以外の場合、
            // 取推管理顧客GCIF月次テーブルより直近のデータを取得する
            if ((strHyoujiTo.equals(V_EMPTY_STRING) != true) &&
                            (strHyoujiFrom.equals(V_EMPTY_STRING) != true)) {

                // SQLパラメータを設定する
                dbparam.clearAllData();
                dbparam.setParameter(F_DAI_BRNO.toLowerCase(),strDaihyoBrnoCif[int0]);
                dbparam.setParameter(F_DAI_TRISKNO.toLowerCase(),strDaihyoBrnoCif[int1]);
                dbparam.setParameter(F_STARTYM.toLowerCase(),strHyoujiFrom);
                dbparam.setParameter(F_ENDYM.toLowerCase(),strHyoujiTo);

                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_611, SQL_4051, dbparam});

                // (SQL-ID=rlrrg_o4051)(PreparedStatement)
                rs_o4051_1 = dbcon.executeQueryPS(SQL_4051,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_612, SQL_4051});

                // 検索結果数を取得する
                intNowDataNum = rs_o4051_1.getNumResult();

                // 表示月(前年)(TO)、表示月(前年)(FROM)が""以外の場合、
                // 取推管理顧客GCIF月次テーブルより1年前のデータを取得する
                if ((strHyoujiToAgo.equals(V_EMPTY_STRING) != true) &&
                            (strHyoujiFromAgo.equals(V_EMPTY_STRING) != true)) {

                    // SQLパラメータを設定する
                    dbparam.clearAllData();
                    dbparam.setParameter(F_DAI_BRNO.toLowerCase(),strDaihyoBrnoCif[int0]);
                    dbparam.setParameter(F_DAI_TRISKNO.toLowerCase(),strDaihyoBrnoCif[int1]);
                    dbparam.setParameter(F_STARTYM.toLowerCase(),strHyoujiFromAgo);
                    dbparam.setParameter(F_ENDYM.toLowerCase(),strHyoujiToAgo);

                    // 検索処理を実行し結果セットインスタンスを取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_613, SQL_4051, dbparam});

                    // (SQL-ID=rlrrg_o4051)(PreparedStatement)
                    rs_o4051_2 = dbcon.executeQueryPS(SQL_4051,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_614, SQL_4051});

                    // 検索結果数を取得する
                    intAgoDataNum = rs_o4051_2.getNumResult();

                }
            }

            // -------------------------------------------------------
            // コア企業GCIF番号を取得する ----
            // -------------------------------------------------------
            // 初期処理 ------
            String strCoreGCIFNo = V_EMPTY_STRING;              // コア企業GCIF番号

            // 属性番号→GCIF番号取得クラスのインスタンスを取得する
            dbparam.clearAllData();
            RLRCICOM_GCIFfromAttr instanceGCIFfromAttr =
                                new RLRCICOM_GCIFfromAttr(dbcon,dbparam,folder);
            int rc = instanceGCIFfromAttr.findGCIFHnays(strBrNo, strTriskNo);
            // 処理結果が正常の時、GCIF番号を取得する。
            if (rc == IRLRCICOM_GCIFConst.GCIF_RTN_OK) {
                strCoreGCIFNo = instanceGCIFfromAttr.getGCIFno();
            }

            // コア企業GCIF番号、表示月(TO)、表示月(FROM)が""以外の場合、
            // 取推関係先月次テーブルから直近のデータを取得する ----

            if ((strCoreGCIFNo.equals(V_EMPTY_STRING) != true) &&
                    (strHyoujiTo.equals(V_EMPTY_STRING) != true) &&
                            (strHyoujiFrom.equals(V_EMPTY_STRING) != true)) {

                // SQLパラメータを設定する
                dbparam.clearAllData();
                dbparam.setParameter(F_GCIF_NO.toLowerCase(),strCoreGCIFNo);
                dbparam.setParameter(F_STARTYM.toLowerCase(),strHyoujiFrom);
                dbparam.setParameter(F_ENDYM.toLowerCase(),strHyoujiTo);

                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_615, SQL_4053, dbparam});

                // (SQL-ID=rlrrg_o4053)(PreparedStatement)
                rs_o4053_1 = dbcon.executeQueryPS(SQL_4053,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_616, SQL_4053});

                // 検索結果数を取得する
                intGRNowDataNum = rs_o4053_1.getNumResult();

                // 表示月(前年)(TO)、表示月(前年)(FROM)が""以外の場合、
                // 取推関係先月次テーブルより1年前のデータを取得する
                if ((strHyoujiToAgo.equals(V_EMPTY_STRING) != true) &&
                        (strHyoujiFromAgo.equals(V_EMPTY_STRING) != true)) {
                    // SQLパラメータを設定する
                    dbparam.clearAllData();
                    dbparam.setParameter(F_GCIF_NO.toLowerCase(),strCoreGCIFNo);
                    dbparam.setParameter(F_STARTYM.toLowerCase(),strHyoujiFromAgo);
                    dbparam.setParameter(F_ENDYM.toLowerCase(),strHyoujiToAgo);

                    // 検索処理を実行し結果セットインスタンスを取得する
                    // CP検証メッセージ：開始
                    logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_617, SQL_4053, dbparam});

                    // (SQL-ID=rlrrg_o4053)(PreparedStatement)
                    rs_o4053_2 = dbcon.executeQueryPS(SQL_4053,dbparam);

                    // CP検証メッセージ：終了
                    logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_618, SQL_4053});

                    // 検索結果数を取得する
                    intGRAgoDataNum = rs_o4053_2.getNumResult();
                }
            }


            // -------------------------------------------------------
            // 計数情報引当状況テーブルからデータを取得する ----
            // -------------------------------------------------------
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_619, SQL_4184, dbparam});

            // (SQL-ID=rlrrg_o4184)(PreparedStatement)
            rs_o4184 = dbcon.executeQueryPS(SQL_4184,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_620, SQL_4184});

            // -------------------------------------------------------
            // 一般保証明細テーブルからデータを取得する ----
            // -------------------------------------------------------
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_621, SQL_4185, dbparam});

            // (SQL-ID=rlrrg_o4185)(PreparedStatement)
            rs_o4185 = dbcon.executeQueryPS(SQL_4185,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_622, SQL_4185});

            // -------------------------------------------------------
            // 自己査定テーブルからデータを取得する ----
            // -------------------------------------------------------
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            // 検索処理を実行し結果セットインスタンスを取得する
            // CP検証メッセージ：開始
            logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_623, SQL_4186, dbparam});

            // (SQL-ID=rlrrg_o4186)(PreparedStatement)
            rs_o4186 = dbcon.executeQueryPS(SQL_4186,dbparam);

            // CP検証メッセージ：終了
            logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_624, SQL_4186});


            // ---------------------------------------------------------------
            // 単体財務系テーブルからデータを取得する ----
            // ---------------------------------------------------------------

            // 顧客属性より取得したGCIF番号を結果セットインスタンスより取得する
            String strGcifNo = (String)ns(rs_o0501.getString2(F_GCIF_NO,int0));

            // 単体財務取得用決算期配列の初期化
            strKessankiShutoku = new String[] {V_EMPTY_STRING};

            // 取得したGCIF番号がNULLでない場合、単体財務テーブルより決算期を取得する
            if ( !strGcifNo.equals(V_EMPTY_STRING) ) {
                // SQLパラメータを設定する
                dbparam.clearAllData();
                dbparam.setParameter(F_GCIF_NO.toLowerCase(),strGcifNo);

                // 検索処理を実行し結果セットインスタンスを取得する
                // CP検証メッセージ：開始
                logDebug(SQL_LOG_0110, new Object[]{V_LOG_TUNO_625, SQL_4194, dbparam});

                // (SQL-ID=rlrrg_o4194)(PreparedStatement)
                rs_o4194 = dbcon.executeQueryPS(SQL_4194,dbparam);

                // CP検証メッセージ：終了
                logDebug(SQL_LOG_0111, new Object[]{V_LOG_TUNO_626, SQL_4194});

                // 取得結果が成功の場合、単体財務.決算期(最大3期分)を取得し
                if (rs_o4194.getNumResult() != int0) {
                    strKessankiShutoku = rs_o4194.getStringArray2(F_KSANH);
                }
// if文の直前に移動した為、削除
//              } else {
//                  strKessankiShutoku = new String[int1];
//                  strKessankiShutoku[0] = V_EMPTY_STRING;
//              }
            }

            // 決算期取得用が""でない場合、単体財務各テーブルより、データを取得する



        long lngYurishiFusai[] = {lng0, lng0};

        // 各値に妥当性がある場合、計算に加えてゆく
        for (i = int0; i < int2; i++) {
            intSonzaiFlag = int0;
            // 短期借入金
            if (callSingleStrNum(getString2PlusNLCHK(rs_o4187,F_SKARI,int4187[i + int1])) == int0) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns(rs_o4187.getString2(F_SKARI,int4187[i + int1])) );
                intSonzaiFlag++;
            }

/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 「有利子負債」の算出式変更の為、コメントアウトされていたものを復帰。
 */
            // 割引手形
            if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_WARITE,int4187[i + int1] ) ) == int0 ) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns( rs_o4187.getString2( F_WARITE,int4187[i + int1] ) ) );
                intSonzaiFlag++;
            }
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

            // 2002/01/23 ADD@S.SEIMURA 社債を計算に追加
            // 社債
            if (callSingleStrNum(getString2PlusNLCHK(rs_o4187,F_KBOND,int4187[i + int1])) == int0) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns(rs_o4187.getString2(F_KBOND,int4187[i + int1])) );
                intSonzaiFlag++;
            }
            // 長期借入金
            if (callSingleStrNum(getString2PlusNLCHK(rs_o4187,F_LKARI,int4187[i + int1])) == int0) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns(rs_o4187.getString2(F_LKARI,int4187[i + int1])) );
                intSonzaiFlag++;
            }
            // 1年以内返済長期借入金
            if (callSingleStrNum(getString2PlusNLCHK(rs_o4187,F_LKARI_RPAY1,int4187[i + int1])) == int0) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns(rs_o4187.getString2(F_LKARI_RPAY1,int4187[i + int1])) );
                intSonzaiFlag++;
            }
            // 1年以内償還社債
            if (callSingleStrNum(getString2PlusNLCHK(rs_o4187,F_KBOND_RPAY1,int4187[i + int1])) == int0) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns(rs_o4187.getString2(F_KBOND_RPAY1,int4187[i + int1])) );
                intSonzaiFlag++;
            }

/*
 * 2007.02.21 Add.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 「有利子負債」の算出式変更の為、「コマーシャルペーパー」の加算を追加。
 */
            // コマーシャルペーパー
            if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_CP_VAL,int4187[i + int1] ) ) == int0 ) {
                lngYurishiFusai[i] = lngYurishiFusai[i] +
                    getLongValue( ns( rs_o4187.getString2( F_CP_VAL,int4187[i + int1] ) ) );
                intSonzaiFlag++;
            }
// 2007.02.21 Add. End  M.Kawano(GEC18-C-014, にゅーとん対応)

            // いづれかの値に妥当性があった場合、有利子負債として設定を行う
            if (intSonzaiFlag != 0) {
                strYurishiFusai[i] = (new Long(lngYurishiFusai[i])).toString();
            }
        }

/*
 * 2007.02.21 Add.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 「短期借入金」の算出式変更の為、計算式を追加。
 */
        // 短期借入金の計算を行う
        // 短期借入金 ＋ 1年以内返済長期借入金 ＋ 1年以内償還社債 + コマーシャルペーパー
        // (全て直近期のみ)
        String  strSKari = V_EMPTY_STRING;
        long    lngSKari = lng0;

        intSonzaiFlag = int0;

        // 各値に妥当性がある場合、計算に加えてゆく
        // 短期借入金
        if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_SKARI,int4187[int2] ) ) == int0 ) {
            lngSKari = lngSKari + getLongValue( ns( rs_o4187.getString2( F_SKARI,int4187[int2] ) ) );
            intSonzaiFlag++;
        }

        // 1年以内返済長期借入金
        if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_LKARI_RPAY1,int4187[int2] ) ) == int0 ) {
            lngSKari = lngSKari + getLongValue( ns( rs_o4187.getString2( F_LKARI_RPAY1,int4187[int2] ) ) );
            intSonzaiFlag++;
        }

        // 1年以内償還社債
        if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_KBOND_RPAY1,int4187[int2] ) ) == int0 ) {
            lngSKari = lngSKari + getLongValue( ns( rs_o4187.getString2( F_KBOND_RPAY1,int4187[int2] ) ) );
            intSonzaiFlag++;
        }

        // コマーシャルペーパー
        if ( callSingleStrNum( getString2PlusNLCHK( rs_o4187,F_CP_VAL,int4187[int2] ) ) == int0 ) {
            lngSKari = lngSKari + getLongValue( ns( rs_o4187.getString2( F_CP_VAL,int4187[int2] ) ) );
            intSonzaiFlag++;
        }

        // 妥当性のある値が存在する場合、短期借入金として設定を行う
        if ( intSonzaiFlag != 0 ) {
            strSKari = (new Long(lngSKari)).toString();
        }
// 2007.02.21 Add. End  M.Kawano(GEC18-C-014, にゅーとん対応)


        // 2002/01/23 CHG@S.SEIMURA int4187[int0]→int4187[int2]
        // 単位変換(千円→百万円)
        // 直近期
        String strKsanhTempAnk = getString2PlusNLCHK(rs_o4187,F_KSANH, int4187[int2]);
        if ( (strKsanhTempAnk != null) && (strKsanhTempAnk.length() != int0) ) {
// 2003/07/07 西暦和暦変換を行う(01553)
            RLRCMCOM_CalendarWrapper instanceCal = new RLRCMCOM_CalendarWrapper(folder, dbcon, dbparam);

            String strWareki = instanceCal.getYearMonthWareki( strKsanhTempAnk, V_EMPTY_STRING, RLRCMCOM_CalendarWrapper.NO_GENGO);

            if ( strWareki != null && strWareki.length() == int4 ) {
                hstDB.put(F_CKKKN_ANK, strWareki);
            } else {
                hstDB.put(F_CKKKN_ANK, V_EMPTY_STRING);
            }
        } else {
            hstDB.put(F_CKKKN_ANK, V_EMPTY_STRING);
        }

        // 流動資産
        hstDB.put(F_RYUDOSHISAN_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_RYASS_KEI,int4187[int2]), int1, int3, int0, int1));
        // 現預金
        hstDB.put(F_GENYOKIN_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_CASHYKN,int4187[int2]), int1, int3, int0, int1));
        // 売上債権
        hstDB.put(F_UKETEGATA_URIKAKE_ANK,
            callTaniChange(strUriageSaiken, int1, int3, int0, int1));
        // 在庫
        hstDB.put(F_TANAOROSHI_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_ZAIKO_KEI,int4187[int2]), int1, int3, int0, int1));
        // 固定資産
        hstDB.put(F_KOTEISHISAN_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_FIXASS_KEI,int4187[int2]), int1, int3, int0, int1));
        // 有形固定資産
        hstDB.put(F_YUKEIKOTEISHISAN_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_FIXASSY_KEI,int4187[int2]), int1, int3, int0, int1));
        // 繰延資産
        hstDB.put(F_KURINOBESHISAN_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_KRNASS_KEI,int4187[int2]), int1, int3, int0, int1));
        // 資産合計
        hstDB.put(F_SHISAN_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_ASS_KEI,int4187[int2]), int1, int3, int0, int1));
        // 流動負債
        hstDB.put(F_RYUDOFUSAI_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_RYLIAB_KEI,int4187[int2]), int1, int3, int0, int1));
        // 支払債務
        hstDB.put(F_SHITEGATA_KAIKAKE_ANK,
            callTaniChange(strShiharaiSaimu, int1, int3, int0, int1));
        // 商手
        hstDB.put(F_WARITEGATA_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_WARITE,int4187[int2]), int1, int3, int0, int1));

/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * 「短期借入金」の値が計算による算出に変更になった為、設定処理を変更。
 */
        // 短期借入金
//      hstDB.put(F_TANKARIKIN_ANK,
//          callTaniChange(getString2PlusNLCHK(rs_o4187,F_SKARI,int4187[int2]), int1, int3, int0, int1));
        hstDB.put( F_TANKARIKIN_ANK, callTaniChange( strSKari, int1, int3, int0, int1 ) );
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

        // 固定負債
        hstDB.put(F_KOTEIFUSAI_KEI_ANK,
            callTaniChange(getString2PlusNLCHK(rs_o4187,F_FIXLIAB_KEI,int4187[int2]), int1, int3, int0, int1));
        // 社債･長期借入金
        hstDB.put(F_SHASAI_CHOKARIKIN_ANK,
            callTaniChange(strShasaiTyoukiKariire, int1, int3, int0, int1));


/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * データ取得に使用するSQL項目名が変更になった為、「資本合計」から「純資産合計」へ変更。
 */
        // 純資産
//      hstDB.put(F_SHIHON_KEI_ANK,
//          callTaniChange(getString2PlusNLCHK(rs_o4187,F_CAPIT_KEI,int4187[int2]), int1, int3, int0, int1));
        hstDB.put( F_SHIHON_KEI_ANK,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_JNASS_KEI, int4187[int2] ),
                   int1, int3, int0, int1 ) );
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/*
 * 2007.03.07 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * データ取得に使用するSQL項目名が変更になった為、「負債・資本合計」から「負債・純資産合計」へ変更。
 */
        // 負債・純資産合計
//      hstDB.put(F_FUSAISHIHON_KEI_ANK,
//          callTaniChange(getString2PlusNLCHK(rs_o4187,F_LIABCAPIT_KEI,int4187[int2]), int1, int3, int0, int1));
        hstDB.put( F_FUSAISHIHON_KEI_ANK,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_LIABJNASS_KEI, int4187[int2]),
                   int1, int3, int0, int1 ) );
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

        // 2002/01/23 CHG@S.SEIMURA int4187[i]→int4187[i + int1]
        for (i = int0; i < int2; i++) {
            // 売上総利益
            hstDB.put(strUrisoek[i],
                callTaniChange(getString2PlusNLCHK(rs_o4188,F_URISOEK,int4187[i + int1]), int1, int3, int0, int1));
            // 営業利益
            hstDB.put(strEigyek[i],
                callTaniChange(getString2PlusNLCHK(rs_o4188,F_EIGYEK,int4187[i + int1]), int1, int3, int0, int1));
            // 有利子負債
            hstDB.put(strYrsliab[i],
                callTaniChange(strYurishiFusai[i], int1, int3, int0, int1));
        }


        // Gr合算実態純資産額
        hstDB.put(F_GRJTJNSSGK,
            callTaniChange(getString2PlusNLCHK(rs_o4192,F_JITJUNASS_GC,int0), int1, int3, int0, int1));

// 2003/03/04 CHG@S.SEIMURA ホストより金額単位が取得できない場合の処理を追加 START
        if ( strTani != null && strTani.trim().length() != int0 ) {
            // 単位変換の変換単位を求める
            int intTani = (int)((new Long(strTani)).longValue());
            // 金額単位コードが2(百万円)の時、変換単位を3に設定
            if (intTani == int2) {
                intTani = int3;
            // 金額単位コードが3(億円)の時、変換単位を5に設定
            } else if (intTani == int3) {
                intTani = int5;
            }

            // 計数情報引当状況データの設定
            String[] strKite = nsa(hstKey.get(F_HIKIATE_KITEITI),intHikiateNum);
            String[] strJika = nsa(hstKey.get(F_HIKIATE_JIKA),intHikiateNum);

            for (i = int0; i < intHikiateNum; i++) {
                // 規定値
                if (strKeiHikiateKite[i].equals(V_EMPTY_STRING) != true) {
                    strKite[i] =
                        callTaniChange( ns(rs_o4184.getString2(strKeiHikiateKite[i],int0)),
//                          int0, intTani, int0, int0 );    // 取得元を千円に修正
                            int1, intTani, int0, int0 );
                    // 単位変換の結果が0の場合、空文字を設定する
                    if ( strKite[i].equals( str0 ) ) {
                        strKite[i] = V_EMPTY_STRING;
                    }
                }
                // 時価ベース
                if (strKeiHikiateJika[i].equals(V_EMPTY_STRING) != true) {
                    strJika[i] =
                        callTaniChange( ns(rs_o4184.getString2(strKeiHikiateJika[i],int0)),
//                          int0, intTani, int0, int0 );    // 取得元を千円に修正
                            int1, intTani, int0, int0 );
                    // 単位変換の結果が0の場合、空文字を設定する
                    if ( strJika[i].equals( str0 ) ) {
                        strJika[i] = V_EMPTY_STRING;
                    }
                }
            }
/* YC20218-02 Start */
            // 担保権利設定テーブルの設定

            //     規定値
            strKite[intKtitnpIptnp1FudoteHloanNum] =
                callTaniChange( ns(rs_o4196.getString2(F_JIKA_TORI_GK,int0)),
                            int0, intTani, int0, int0 );
            //     単位変換の結果が0の場合、空文字を設定する
            if ( str0.equals( strKite[intKtitnpIptnp1FudoteHloanNum] ) ) {
                strKite[intKtitnpIptnp1FudoteHloanNum] = V_EMPTY_STRING;
            }
/* YC20218-02 End */
            hstDB.put(F_HIKIATE_KITEITI,strKite);
            hstDB.put(F_HIKIATE_JIKA,strJika);


            // 自己査定データの設定①-1
            // 取得元のデータが既に0の場合は空文字にする。単位変換結果が0の場合はそのまま。
            hstDB.put(F_HIBNRI_GK, ( ( ns(rs_o4186.getString2(F_HIBNRI_GK,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_HIBNRI_GK,int0)), int0, intTani, int0, int0) ) );

            hstDB.put(F_TWO_BNRUI_GK, ( ( ns(rs_o4186.getString2(F_TWO_BNRUI_GK,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_TWO_BNRUI_GK,int0)), int0, intTani, int0, int0) ) );

            hstDB.put(F_THREE_BNRUI_GK, ( ( ns(rs_o4186.getString2(F_THREE_BNRUI_GK,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_THREE_BNRUI_GK,int0)), int0, intTani, int0, int0) ) );

            hstDB.put(F_FOUR_BNRUI_GK, ( ( ns(rs_o4186.getString2(F_FOUR_BNRUI_GK,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_FOUR_BNRUI_GK,int0)), int0, intTani, int0, int0) ) );

            hstDB.put(F_TOT, ( ( ns(rs_o4186.getString2(F_TOT,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_TOT,int0)), int0, intTani, int0, int0) ) );

            hstDB.put(F_UYKNRSKN, ( ( ns(rs_o4186.getString2(F_UYKNRSKN,int0)).equals( str0 ) ) ?
                V_EMPTY_STRING :
                callTaniChange(ns(rs_o4186.getString2(F_UYKNRSKN,int0)), int0, intTani, int0, int0) ) );
/* YC20218-02 Start */
            // オンローン（新貸外）個人レコード＜月末＞の設定

            //     内HL信用不算入
            String[] strMendZan = nsa(hstKey.get(F_MEND_ZAN),intIpnYsnNum);
            String[] strHonafZan = nsa(hstKey.get(F_HONAF_ZAN),intIpnYsnNum);
            String[] strJisksn = nsa(hstKey.get(F_JISKSN),intIpnYsnNum);


            //     内HL信用不算入（指定月末残高）
            strMendZan[V_KEISU_HLSHINYOFUSANNYU_BAP] =
                callTaniChange( ns(rs_o4196.getString2(F_INH_KASIZAN_G,int0)),
                            int0, intTani, int0, int2 );
            //     単位変換の結果が0の場合、空文字を設定する
            if ( str0.equals( strMendZan[V_KEISU_HLSHINYOFUSANNYU_BAP] ) ) {
                strMendZan[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING;
            }

            //     内HL信用不算入（本件後残高）
            strHonafZan[V_KEISU_HLSHINYOFUSANNYU_BAP] =
                callTaniChange( ns(rs_o4196.getString2(F_INH_KASIZAN_G,int0)),
                            int0, intTani, int0, int2 );
            //     単位変換の結果が0の場合、空文字を設定する
            if ( str0.equals( strHonafZan[V_KEISU_HLSHINYOFUSANNYU_BAP] ) ) {
                strHonafZan[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING;
            }

            //     内HL信用不算入（実勢現在残高）
            strJisksn[V_KEISU_HLSHINYOFUSANNYU_BAP] =
                callTaniChange( ns(rs_o4196.getString2(F_INH_KASIZAN_G,int0)),
                            int0, intTani, int0, int2 );
            //     単位変換の結果が0の場合、空文字を設定する
            if ( str0.equals( strJisksn[V_KEISU_HLSHINYOFUSANNYU_BAP] ) ) {
                strJisksn[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING;
            }

            hstDB.put(F_MEND_ZAN ,strMendZan);
            hstDB.put(F_HONAF_ZAN ,strHonafZan);
            hstDB.put(F_JISKSN ,strJisksn);
/* YC20218-02 End */


        } else {

            // 計数情報引当状況データの設定
            String[] strKite = nsa(hstKey.get(F_HIKIATE_KITEITI),intHikiateNum);
            String[] strJika = nsa(hstKey.get(F_HIKIATE_JIKA),intHikiateNum);

            for (i = int0; i < intHikiateNum; i++) {
                // 規定値
                if (strKeiHikiateKite[i].equals(V_EMPTY_STRING) != true) {
                    strKite[i] = V_EMPTY_STRING;
                }
                // 時価ベース
                if (strKeiHikiateJika[i].equals(V_EMPTY_STRING) != true) {
                    strJika[i] = V_EMPTY_STRING;
                }
            }
/* YC20218-02 Start */
            // 担保依頼情報テーブルの設定

            //     規定値
            strKite[intKtitnpIptnp1FudoteHloanNum] = V_EMPTY_STRING;
/* YC20218-02 End */

            hstDB.put(F_HIKIATE_KITEITI ,strKite);
            hstDB.put(F_HIKIATE_JIKA    ,strJika);

            // 自己査定データの設定①-2
            hstDB.put(F_HIBNRI_GK      ,V_EMPTY_STRING);
            hstDB.put(F_TWO_BNRUI_GK   ,V_EMPTY_STRING);
            hstDB.put(F_THREE_BNRUI_GK ,V_EMPTY_STRING);
            hstDB.put(F_FOUR_BNRUI_GK  ,V_EMPTY_STRING);
            hstDB.put(F_TOT            ,V_EMPTY_STRING);
            hstDB.put(F_UYKNRSKN       ,V_EMPTY_STRING);
/* YC20218-02 Start */
            // オンローン（新貸外）個人レコード＜月末＞の設定

            //     内HL信用不算入
            String[] strMendZan = nsa(hstKey.get(F_MEND_ZAN),intIpnYsnNum);
            String[] strHonafZan = nsa(hstKey.get(F_HONAF_ZAN),intIpnYsnNum);
            String[] strJisksn = nsa(hstKey.get(F_JISKSN),intIpnYsnNum);

            strMendZan[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING; // 指定月末残高
            strHonafZan[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING; // 本件後残高
            strJisksn[V_KEISU_HLSHINYOFUSANNYU_BAP] = V_EMPTY_STRING; // 実勢現在残高

            hstDB.put(F_MEND_ZAN ,strMendZan);
            hstDB.put(F_HONAF_ZAN ,strHonafZan);
            hstDB.put(F_JISKSN ,strJisksn);
/* YC20218-02 End */
        }



        // 一般保証明細データの設定
        String[] strHoshonin = new String[intHoshoninNum];
        for (i = int0; i < intHoshoninNum; i++) {
            strHoshonin[i] = ns(rs_o4185.getString2(F_HSN_NM, i));

            // 10桁を超えていた場合、10桁に変更する
            if (strHoshonin[i].length() > 10) {
                strHoshonin[i] = strHoshonin[i].substring(0,10);
            }
        }
        hstDB.put(F_HSN_NM,strHoshonin);


        // 自己査定データの設定②
        // 単位変換(円→千円)を行う
        // 取得元のデータが既に0の場合は空文字にする。単位変換結果が0の場合はそのまま。
        hstDB.put(F_CRERLT_CST, ( ( ns(rs_o4186.getString2(F_CRERLT_CST,int0)).equals( str0 ) ) ?
            V_EMPTY_STRING :
            callTaniChange(ns(rs_o4186.getString2(F_CRERLT_CST,int0)), int0, int1, int0, int0) ) );


        // 計数情報(禀議計数補正値)データの設定を行う
        String[] strHoseichi = new String[intIpnYsnNum];

        strHoseichi[intIpnHoschNum - int2] = ns(rs_o4193.getString2(F_IPNYSNTTHOSCH,int0));
        strHoseichi[intUchiHoschNum - int2] = ns(rs_o4193.getString2(F_UJPYKHOSCH,int0));
        strHoseichi[intBouekiHoschNum - int2] = ns(rs_o4193.getString2(F_BYSNTTHOSC,int0));
        strHoseichi[intShishoHoschNum - int2] = ns(rs_o4193.getString2(F_SISHOTTHOSCH,int0));
        hstDB.put(F_HOSCH,strHoseichi);
        hstDB.put(F_HOSRSN,ns(rs_o4193.getString2(F_HOSRSN,int0)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
        // 規定担保補正値の設定
        String[] strKtiTnpHoschKti = new String[intHikiateTotNum];
        String[] strKtiTnpHoschJika = new String[intHikiateTotNum];
        strKtiTnpHoschKti[intKiteHosch] = ns(rs_o4193.getString2(F_KTITNP_HOSCH1,int0));    // 規定担保補正値（規定値）
        strKtiTnpHoschJika[intKiteHosch] = ns(rs_o4193.getString2(F_KTITNP_HOSCH2,int0));   // 規定担保補正値（時価ベース）
        hstDB.put(F_HIKIATE_KITEITI_TOT,strKtiTnpHoschKti);
        hstDB.put(F_HIKIATE_JIKA_TOT,strKtiTnpHoschJika);
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

        // 直近計数案件番号の設定を行う
        hstDB.put(F_CKKKNKEISU_LC_NO,ns(rs_o4195.getString2(F_LC_NO,int0)));
//      // 作成日の設定を行う
//      hstDB.put(F_MKBI, strMkbi);


        /*
         * 2004/09/30 ADD@S.SEIMURA(GEC16-C-012-711)
         * 検討会使用メモ対応 START
         */

        // 代表店CIFを設定する
        hstDB.put(F_DAIHYOU_TENCIF, strDaihyouBrnoTriskno);

// 2010/09/07 DEL@M.Watanabe GEC22-C-046 start
//      // 取推の値を単位変換する前の値で設定する
//      hstDB.put(IRingiItemKentoukai.F_KNT_S_ELKANRIGAKU_RATE,      strSElkanrigakuRate1);
//      hstDB.put(IRingiItemKentoukai.F_KNT_S_ELKANRIGAKU_RATE_S_EL, strSElkanrigakuRateSEl1);
// 2010/09/07 DEL@M.Watanabe GEC22-C-046 end

        // 前期分の資産合計を設定する(int4187[int1]が前期分の入ったレコード)
        hstDB.put(IRingiItemKentoukai.F_KNT_SOSHISAN1,
            callTaniChange( getString2PlusNLCHK(rs_o4187,F_ASS_KEI,int4187[int1]),
                            getApiTani(V_TANI_SEN),
                            getApiTani(V_TANI_HYAKUMAN),
                            0,
                            K_SHISHAGONYU));

/*
 * 2007.02.21 Mod.  M.Kawano(GEC18-C-014, にゅーとん対応)
 * データ取得に使用するSQL項目名が変更になった為、「資本合計」から「自己資本」へ変更。
 * 自己資本(当期)の設定処理を追加。
 */
        // 前期分の資本を設定する(int4187[int1]が前期分の入ったレコード)
//      hstDB.put(IRingiItemKentoukai.F_KNT_SHOMISHISAN1,
//          callTaniChange( getString2PlusNLCHK(rs_o4187,F_CAPIT_KEI,int4187[int1]),
//                          getApiTani(V_TANI_SEN),
//                          getApiTani(V_TANI_HYAKUMAN),
//                          0,
//                          K_SHISHAGONYU));
        hstDB.put( IRingiItemKentoukai.F_KNT_SHOMISHISAN1,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_JIKOCAPIT, int4187[int1] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   0,
                                   K_SHISHAGONYU ) );

        hstDB.put( IRingiItemKentoukai.F_KNT_SHOMISHISAN2,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_JIKOCAPIT, int4187[int2] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   0,
                                   K_SHISHAGONYU ) );
// 2007.02.21 Mod. End  M.Kawano(GEC18-C-014, にゅーとん対応)

/*
 * 2007.02.20 Add.     M.Kawano(GEC18-C-014,にゅーとん対応)
 * 「経常収支」の取得元テーブル変更の為、データ設定処理を追加。
 * 2007.06.12 Mod.     M.Kawano(GEC18-C-014,にゅーとん対応)<ITaトラ報-00396対応>
 * 「経常収支」の金額単位変換処理(千円->百万円)を追加。
 */
//      hstDB.put( F_KEIJSYSI,
//                 getString2PlusNLCHK( rs_o4312, F_IDO_KEIJSYSI, int4312[int2] ) );
        hstDB.put( F_KEIJSYSI,
                   callTaniChange( getString2PlusNLCHK( rs_o4312, F_IDO_KEIJSYSI, int4312[int2] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   0,
                                   K_SHISHAGONYU ) );
// 2007.02.20 Add End  M.Kawano(GEC18-C-014,にゅーとん対応)
// 2007.06.12 Mod End  M.Kawano(GEC18-C-014,にゅーとん対応)<ITaトラ報-00396対応>

        /*
         * 2004/09/30 ADD@S.SEIMURA(GEC16-C-012-711)
         * 検討会使用メモ対応 END
         */

// 2010/09/07 ADD@M.Watanabe GEC22-C-046 start
        /**
         * 「有形固定資産」、「現預金」、「経常収支」の当期分のデータについては
         * 案件サマリーの項目を取得する処理で既に設定されているが、既存への影響を抑えるため、
         * 検討会使用メモで使用する別項目名で新たに取得・設定を行なう。
         */

        // 有形固定資産（前期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_FIXASSY_KEI1,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_FIXASSY_KEI, int4187[int1] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 有形固定資産（当期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_FIXASSY_KEI2,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_FIXASSY_KEI, int4187[int2] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 現預金（前期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_CASHYKN1,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_CASHYKN, int4187[int1] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 現預金（当期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_CASHYKN2,
                   callTaniChange( getString2PlusNLCHK( rs_o4187, F_CASHYKN, int4187[int2] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 経常収支（前期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_IDO_KEIJSYSI1,
                   callTaniChange( getString2PlusNLCHK( rs_o4312, F_IDO_KEIJSYSI, int4312[int1] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 経常収支（当期）を設定する
        hstDB.put( IRingiItemKentoukai.F_KNT_IDO_KEIJSYSI2,
                   callTaniChange( getString2PlusNLCHK( rs_o4312, F_IDO_KEIJSYSI, int4312[int2] ),
                                   getApiTani( V_TANI_SEN ),
                                   getApiTani( V_TANI_HYAKUMAN ),
                                   int0,
                                   K_SHISHAGONYU ) );

        // 以下、検討会使用メモにて和暦変換前の決算期が必要となるため設定をする
        // 決算期(前期、当期)をブランクで初期化する
        hstDB.put( IRingiItemKentoukai.F_SEIREKI_KESSANKI1, V_EMPTY_STRING );  // 決算期(前期)
        hstDB.put( IRingiItemKentoukai.F_SEIREKI_KESSANKI2, V_EMPTY_STRING );  // 決算期(当期)

        // 決算期が前期、当期共に取得されている場合
        if ( strKessankiShutoku.length >= 2 ) {
            // 決算期を格納している配列から決算期(前期、当期)を設定する
            hstDB.put( IRingiItemKentoukai.F_SEIREKI_KESSANKI1, strKessankiShutoku[int1] );
            hstDB.put( IRingiItemKentoukai.F_SEIREKI_KESSANKI2, strKessankiShutoku[int0] );

        // 決算期が当期のみ取得されている場合
        // (決算期が1期も取得できなかった場合も含め、この配列は必ず要素>=1である)
        } else if ( strKessankiShutoku[int0].length() != 0 ) {
            // 決算期を格納している配列から決算期(当期)を設定する
            hstDB.put( IRingiItemKentoukai.F_SEIREKI_KESSANKI2, strKessankiShutoku[int0] );
        }

// 2010/09/07 ADD@M.Watanabe GEC22-C-046 end

        // 終了処理 -------------------------------------------------------------
        hstComBasket.put(K_DB_DATA,hstDB);

    }


/**
 *　 <DL>
 *   <DT><b>メソッド概要:補正値登録</b><DD>
 *   計数情報の補正値を追加又は更新する<BR>
 *   </DD></DT>
 *   </DL>
 *   <BR>
 *   @param      Hashtable        hstComBasket  共有情報
 *   @exception  WACSSysException
 *   @exception  com.ibm.jp.wacs.db.WACSDBException
 *   @exception  WACSApplException
 */
    public void setHoseichi(Hashtable hstComBasket)
                throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException {

        try {

            // 初期処理 ---------------------------------------------------------

            // KEY共通領域のHashtableを取得する
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            // KEY共通領域の情報を取得
            String strBrNo       = (String)hstKey.get(F_BRNO);
            String strTriskNo    = (String)hstKey.get(F_TRISKNO);

            // 操作者ユーザーIDを取得する。
            WACSUser user    = getUser();
            String strUserId = user.getUserID();

            // リクエストIDを取得する。
            String strReqid = folder.getREQID();

            // SELECT FOR UPDATEで排他を取得する --------------------------------
            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            // 検索処理を実行し結果セットインスタンスを取得する
            // (SQL-ID=rlrrg_o4173)(PreparedStatement)
            dbcon.executeQueryPS(SQL_4173,dbparam);


            // SQLパラメータを設定する
            dbparam.clearAllData();
            dbparam.setParameter(F_BRNO.toLowerCase(),strBrNo);
            dbparam.setParameter(F_TRISKNO.toLowerCase(),strTriskNo);

            String[] strHoseich = nsa(hstKey.get(F_HOSCH), intIpnYsnNum);
            dbparam.setParameter(F_IPNYSNTTHOSCH.toLowerCase(),strHoseich[intHoschIpn]);
            dbparam.setParameter(F_UJPYKHOSCH.toLowerCase(),strHoseich[intHoschUchi]);
            dbparam.setParameter(F_BYSNTTHOSC.toLowerCase(),strHoseich[intHoschBoueki]);
            dbparam.setParameter(F_SISHOTTHOSCH.toLowerCase(),strHoseich[intHoschShisho]);
            dbparam.setParameter(F_HOSRSN.toLowerCase(),(String)no(hstKey.get(F_HOSRSN)));
//2009/06/22  ADD@R.Matsumura GEC20-C-059 start
            // 規定担保補正値を設定
            String[] strKiteTot = nsa( hstKey.get(F_HIKIATE_KITEITI_TOT), intHikiateTotNum );
            String[] strJikaTot = nsa( hstKey.get(F_HIKIATE_JIKA_TOT), intHikiateTotNum);
            dbparam.setParameter(F_KTITNP_HOSCH1.toLowerCase(),strKiteTot[intKiteHosch]);   // 規定担保補正値（規定値）
            dbparam.setParameter(F_KTITNP_HOSCH2.toLowerCase(),strJikaTot[intKiteHosch]);   // 規定担保補正値（時価ベース）
//2009/06/22  ADD@R.Matsumura GEC20-C-059 end

            // システム最終更新データ
            dbparam.setParameter(F_SYS_LST_UPPGMID.toLowerCase(),strReqid);
            dbparam.setParameter(F_SYS_LST_UPID.toLowerCase(),strUserId);


            // 更新処理を実行し、戻り値を取得する
            // (SQL-ID=rlrrg_o4171)(PreparedStatement)
            int rs_o4171 = dbcon.executeUpdatePS(SQL_4171,dbparam);


            // 戻り値が0である場合、挿入処理を実行し、戻り値を取得する
            if (rs_o4171 == int0) {
                // (SQL-ID=rlrrg_o4172)(PreparedStatement)
                int rs_o4172 = dbcon.executeUpdatePS(SQL_4172,dbparam);
            }


            //終了処理 ---------------------------------------------------------
            hstComBasket.put(K_RETURN,new Integer(IRingiDB.RC_OK));

        }catch(com.ibm.jp.wacs.db.WACSDBException e){
            throw e;
        }catch(WACSSysException e){
            throw e;
        }finally{
        }
    }
