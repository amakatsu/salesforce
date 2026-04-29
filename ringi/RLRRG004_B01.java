/*******************************************************************
 *   システム名：融資禀議・個人ローンBPR
 *   サブシステム名：電子禀議
 *   処理名：
 *   処理概要：
 *   ファイル名:  RLRRG004_B01.java
 ******************************************************************/
package jp.co.btm.irl.rlr.rg000;

import java.util.Hashtable ;
import java.util.Enumeration ;
import java.util.ArrayList ;
import java.text.DecimalFormat;
import com.ibm.jp.wacs.CraftsTrxFolder ;
import com.ibm.jp.wacs.db.CraftsDBConnector;
import com.ibm.jp.wacs.db.CraftsDBParam ;
import com.ibm.jp.wacs.CraftsDataBean ;
import com.ibm.jp.wacs.WACSSysException;
import com.ibm.jp.wacs.WACSApplException;
import jp.co.btm.irl.rlr.rg004.RLRRG004_B01_DB;
import java.math.BigDecimal;    // 2011/11/18 ADD@M.Hayashi GEC23-C-051

/**
 * <B>計数情報共通クラス</B>
 * 計数情報の共通処理を行う。
 * @author M.Nitami
 *
 * Date        Name      Reason for change
 *----------------------------------------------
 * 2002/11/19  M.Nitami  新規作成
 * 2003/04/17  S.Seimura ホスト連携時の計算方法を変更
 * 2003/04/27  S.Seimura 顧客情報系の計算(computeKokyaku)を一部、計算ボタン押下時、禀議取得時、に分割
 * 2003/05/14  S.Seimura QA票si-rg-00140の対応
 * 2003/05/15  S.Seimura 桁あふれチェックを追加

 */
public class RLRRG004_B01
                implements IRingi, IRingiItem, IRingiItemKeisu {


    private CraftsTrxFolder   folder  = null;
    private CraftsDBConnector dbcon   = null;
    private CraftsDBParam     dbparam = null;

    private static final double double0  =  0.0;
    private static final double double6  =  6.0;
    private static final double double12 = 12.0;
    private static final double double100 = 100.0;
    private static final double double10000 = 10000.0;
    private static final int intM1 = -1;
    private static final int intM2 = -2;
    private static final int int0  =  0;
    private static final int int1  =  1;
    private static final int int2  =  2;
    private static final int int4  =  4;

// 2011/11/18 ADD@M.Hayashi GEC23-C-051 Start
    /** 金額単位文言配列 */
    public static final String[] V_STR_TANI_MSG = {
        "千円　",
        "百万円",
        "億円　"
    };

    /** 金額単位コード配列 */
    public static final String[] V_STR_TANI = {
        "1",
        "2",
        "3"
    };
// 2011/11/18 ADD@M.Hayashi GEC23-C-051 End



    /**<P>規定･優良担保･商手(規定値)</P>*/
    public static final String F_SUTNTE = "sutnte";

// GEC294-C-004 S
    /**<P>科目･適用、禀議査定番号リスト</P>*/
    private static final String F_KMK_RMT_LIST = "kmk_rmt_list";
    /**<P>禀議査定番号リスト</P>*/
    private static final String F_RSNO_LIST = "rsno_list";

    /**<P>科目･適用 禀議査定番号有開始行</P>*/
    private static final int F_KMK_RMT_START = 2;
    /**<P>科目･適用 禀議査定番号有終了行</P>*/
    private static final int F_KMK_RMT_END = 13;
// GEC294-C-004 E
    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数業務共通クラスコンストラクタ<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param      CraftsTrxFolder    folder    トランザクションフォルダインスタンス
     *   @param      CraftsDBConnector  dbcon     DB接続インスタンス
     *   @param      CraftsDBParam      dbparam   DBパラメータインスタンス
     */
    public RLRRG004_B01(CraftsTrxFolder folder,CraftsDBConnector dbcon,CraftsDBParam dbparam){

        this.folder  = folder;
        this.dbcon   = dbcon;
        this.dbparam = dbparam;

    }

    /**
     * <DL>
     * <DL><b>計数情報項目の計算を行う。</b></DL>
     * </DL>
     * 補正値を使用して一般与信項目の計算を行う（計数再取得ボタンを押下時、または初期表示時）
     * @param   Hashtable       hstComBasket   共有情報
     */
    public void computeYosin( Hashtable hstComBasket ) {

        Hashtable hstDb = (Hashtable)hstComBasket.get(K_DB_DATA);
        String[] strKyokudo  = (String[])hstDb.get(F_LMT);
        String[] strHonkengo = (String[])hstDb.get(F_HONAF_ZAN);
        String[] strHosei    = (String[])hstDb.get(F_HOSCH);
        String[] strGetuZan  = (String[])hstDb.get(F_MEND_ZAN);
        String[] strZogen    = (String[])hstDb.get(F_IPNYSNDLTZGG);
        String[] strJissei   = (String[])hstDb.get(F_JISKSN);
        String[] strZogenTot = new String[int1];
        String[] strLmtTot = (String[])hstDb.get(F_LMT_TOT);            // 2003.08.06 (50966)
        String[] strHonafTot = (String[])hstDb.get(F_HONAF_ZAN_TOT);    // 2003.08.06 (50966)

        int dataValue = 0;

        int intData = 0 ;
        // 補正値が有る配列番号
        int[] intHosei = { V_KEISU_KASHISHO_TOT_BAP, V_KEISU_UCHIENKA_BAP, V_KEISU_GAITAME_TOT_BAP, V_KEISU_SHISHO_TOT_BAP };

        /*
         * 支払承諾合計の計算
         */
        // 月末残高
        if( strGetuZan[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
            strGetuZan[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
            strGetuZan[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
        ){
            dataValue = getDataValue(strGetuZan[V_KEISU_SHISHO_IPAN_BAP]) +
                        getDataValue(strGetuZan[V_KEISU_SHISHO_IPANGAITA_BAP]) +
                        getDataValue(strGetuZan[V_KEISU_SHISHO_DAIRIKSTK_BAP]);

            strGetuZan[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strGetuZan[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


        // 極度額
        if( strKyokudo[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
            strKyokudo[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
            strKyokudo[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
        ){
            dataValue = getDataValue(strKyokudo[V_KEISU_SHISHO_IPAN_BAP]) +
                        getDataValue(strKyokudo[V_KEISU_SHISHO_IPANGAITA_BAP]) +
                        getDataValue(strKyokudo[V_KEISU_SHISHO_DAIRIKSTK_BAP]);

            strKyokudo[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strKyokudo[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


        // 本件後残高
        if( strHonkengo[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
            strHonkengo[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
            strHonkengo[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
        ){
            dataValue = getDataValue(strHonkengo[V_KEISU_SHISHO_IPAN_BAP]) +
                        getDataValue(strHonkengo[V_KEISU_SHISHO_IPANGAITA_BAP]) +
                        getDataValue(strHonkengo[V_KEISU_SHISHO_DAIRIKSTK_BAP]);

            strHonkengo[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strHonkengo[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


        // 実勢現在残
        if( strJissei[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
            strJissei[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
            strJissei[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
        ){
            dataValue = getDataValue(strJissei[V_KEISU_SHISHO_IPAN_BAP]) +
                        getDataValue(strJissei[V_KEISU_SHISHO_IPANGAITA_BAP]) +
                        getDataValue(strJissei[V_KEISU_SHISHO_DAIRIKSTK_BAP]);

            strJissei[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strJissei[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
        }



        /*
         * 一般与信の項目計算を行うが、対象は以下のもののみ
         * 補正値がある「貸付金・商手合計」「内円貨」「外為与信」「支払承諾合計」
         */
        /*
         * 計算の方法は以下のとおり
         * １．計算対象データ有り、補正値データ無し：そのまま出力
         * ２．計算対象データ有り、補正値データ有り：計算結果を出力（結果が０以下の時は０を出力）
         * ３．計算対象データ無し　　　　　　　　　：補正値データの有無に関わらず、出力無し
         */

        /*
         * 一般与信合計
         */
        for(int i = 0; i < intHosei.length; i++ ) {
            // 極度額
            if( strKyokudo[intHosei[i]].length() != 0 ) {
                    intData = getDataValue(strKyokudo[intHosei[i]]) - getDataValue(strHosei[intHosei[i]]);
                if( intData <= 0 ) {
                    intData = 0;
                }
                strKyokudo[intHosei[i]] = Integer.toString(intData);

                // 極度額が無い時は、計算を行わない
            } else {
                strKyokudo[intHosei[i]] = V_EMPTY_STRING;
            }


            // 本件後残高
            if( strHonkengo[intHosei[i]].length() != 0 ) {

                intData = getDataValue(strHonkengo[intHosei[i]]) - getDataValue(strHosei[intHosei[i]]);
                if( intData <= 0 ) {
                    intData = 0 ;
                }
                strHonkengo[intHosei[i]] = Integer.toString(intData);
            } else {
                strHonkengo[intHosei[i]] = V_EMPTY_STRING;
            }

        }

// ADD 2003.07.30 m.otake 補正される項目を使用しているものも再計算の対象にする(50966)

        if (!( strHosei[intHosei[0]].length() == 0
            && strHosei[intHosei[2]].length() == 0
            && strHosei[intHosei[3]].length() == 0)) {


// 2005.03.01   Chg Start K.Sato(GEC16-C-143-005)
// オンバランス合計の計算式修正
// 変更前：貸付金・商手合計＋外為与信合計＋支払承諾合計＋限度算入ローン合計
// 変更後：貸付金・商手合計＋外為与信合計＋支払承諾合計＋私募債＋協保貸＋限度算入ローン合計
/*
 * 2007.01.16 Mod  M.Kawano(GEC18-C-043)
 * オンバランス合計・極度額の計算式不備を修正(協保貸の削除)
 */

        // オンバランス合計（極度額）
//          if (strKyokudo[intHosei[0]].length() != 0 ||
//              strKyokudo[intHosei[2]].length() != 0 ||
//              strKyokudo[intHosei[3]].length() != 0 ||
//              strKyokudo[V_KEISU_SHIBOSAI_BAP].length() != 0 ||
//              strKyokudo[V_KEISU_KYOHOGASHI_BAP].length() != 0 ||
//              strKyokudo[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0) {
//              strKyokudo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(
//                                    getDataValue(strKyokudo[intHosei[0]])
//                                  + getDataValue(strKyokudo[intHosei[2]])
//                                  + getDataValue(strKyokudo[intHosei[3]])
//                                  + getDataValue(strKyokudo[V_KEISU_SHIBOSAI_BAP])
//                                  + getDataValue(strKyokudo[V_KEISU_KYOHOGASHI_BAP])
//                                  + getDataValue(strKyokudo[V_KEISU_GENDOLOAN_TOT_BAP]));
//          }
            if (strKyokudo[intHosei[0]].length() != 0 ||
                strKyokudo[intHosei[2]].length() != 0 ||
                strKyokudo[intHosei[3]].length() != 0 ||
                strKyokudo[V_KEISU_SHIBOSAI_BAP].length() != 0 ||
                strKyokudo[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0) {
                strKyokudo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(
                                      getDataValue(strKyokudo[intHosei[0]])
                                    + getDataValue(strKyokudo[intHosei[2]])
                                    + getDataValue(strKyokudo[intHosei[3]])
                                    + getDataValue(strKyokudo[V_KEISU_SHIBOSAI_BAP])
                                    + getDataValue(strKyokudo[V_KEISU_GENDOLOAN_TOT_BAP]));
            }
// 2007.01.15 Mod End  M.Kawano(GEC18-C-043)
// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start
//オンバランス合計・本件後残高の計算式を変更（その他一般与信を追加）
        // オンバランス合計（本件後残高）
//          if (strHonkengo[intHosei[0]].length() != 0 ||
//              strHonkengo[intHosei[2]].length() != 0 ||
//              strHonkengo[intHosei[3]].length() != 0 ||
//              strHonkengo[V_KEISU_SHIBOSAI_BAP].length() != 0 ||
//              strHonkengo[V_KEISU_KYOHOGASHI_BAP].length() != 0 ||
//              strHonkengo[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0) {
//              strHonkengo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(
//                                    getDataValue(strHonkengo[intHosei[0]])
//                                  + getDataValue(strHonkengo[intHosei[2]])
//                                  + getDataValue(strHonkengo[intHosei[3]])
//                                  + getDataValue(strHonkengo[V_KEISU_SHIBOSAI_BAP])
//                                  + getDataValue(strHonkengo[V_KEISU_KYOHOGASHI_BAP])
//                                  + getDataValue(strHonkengo[V_KEISU_GENDOLOAN_TOT_BAP]));
//          }
            if (strHonkengo[intHosei[0]].length() != 0 ||
                strHonkengo[intHosei[2]].length() != 0 ||
                strHonkengo[intHosei[3]].length() != 0 ||
                strHonkengo[V_KEISU_SHIBOSAI_BAP].length() != 0 ||
                strHonkengo[V_KEISU_KYOHOGASHI_BAP].length() != 0 ||
                strHonkengo[V_KEISU_IPNYSSNT_BAP].length() != 0 ||
                strHonkengo[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0) {
                strHonkengo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(
                                      getDataValue(strHonkengo[intHosei[0]])
                                    + getDataValue(strHonkengo[intHosei[2]])
                                    + getDataValue(strHonkengo[intHosei[3]])
                                    + getDataValue(strHonkengo[V_KEISU_SHIBOSAI_BAP])
                                    + getDataValue(strHonkengo[V_KEISU_KYOHOGASHI_BAP])
                                    + getDataValue(strHonkengo[V_KEISU_IPNYSSNT_BAP])
                                    + getDataValue(strHonkengo[V_KEISU_GENDOLOAN_TOT_BAP]));
            }

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end
// 2005.03.01   Chg End K.Sato(GEC16-C-143-005)


        // 限度算入与信合計（極度）
            if (strKyokudo[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||
                strKyokudo[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0) {
                strLmtTot[V_KEISU_GENDOSAN_TOT_BAP] =   Integer.toString(
                                      getDataValue(strKyokudo[V_KEISU_ONBALANCE_TOT_BAP])
                                    + getDataValue(strKyokudo[V_KEISU_OFFBALANCE_TOT_BAP]));
            }

        // 限度算入与信合計（本件後残高）
            if (strHonkengo[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||
                strHonkengo[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0) {
                strHonafTot[V_KEISU_GENDOSAN_TOT_BAP] =   Integer.toString(
                                      getDataValue(strHonkengo[V_KEISU_ONBALANCE_TOT_BAP])
                                    + getDataValue(strHonkengo[V_KEISU_OFFBALANCE_TOT_BAP]));
            }

        // 一般与信合計（極度）
            if (strLmtTot[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||
                strKyokudo[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0) {
                strKyokudo[V_KEISU_IPPANYSN_TOT_BAP] =   Integer.toString(
                                      getDataValue(strLmtTot[V_KEISU_GENDOSAN_TOT_BAP])
                                    + getDataValue(strKyokudo[V_KEISU_GNDFUSAN_TOT_BAP]));
            }

        // 一般与信合計（本件後残高）
            if (strHonafTot[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||
                strHonkengo[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0) {
                strHonkengo[V_KEISU_IPPANYSN_TOT_BAP] =   Integer.toString(
                                      getDataValue(strHonafTot[V_KEISU_GENDOSAN_TOT_BAP])
                                    + getDataValue(strHonkengo[V_KEISU_GNDFUSAN_TOT_BAP]));
            }
        }
// ADD 2003.07.30 m.otake
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start

        // 特定与信合計（本件後残高）
        // [特定与信1]＋[特定与信2]
        // ※この計算では補正値を使用しない
        if (strHonkengo[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||
            strHonkengo[V_KEISU_SONOTA_YSN2_BAP].length() != 0 ) {
            strHonkengo[V_KEISU_SONOTA_TOT_BAP] =   Integer.toString(
                                getDataValue(strHonkengo[V_KEISU_SONOTA_YSN1_BAP])
                              + getDataValue(strHonkengo[V_KEISU_SONOTA_YSN2_BAP]));
        }

// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end

        /*
         * 各行の増減額の計算を行う
         * 全ての計算式は以下の通り
         * 極度額がある時：（本件後残高）－（極度額）
         * 極度額がない時：（本件後残高）－（月末残高）
         * また極度額が０の時は、極度額が無い時の計算とする
         * ※限度算入与信合計は計算に入れていないが、後で計算されるので、ここでは行わない
         * ※対象の項目に値がない場合、計算は行わずに空文字を入れる
         */




        // 以下のfor文内は画面のリスト項目
        for(int i = 0; i < V_KEISU_IPNYSN_ARR_NUM; i++) {

            int ysnValue = getDataValue(strKyokudo[i]);

// 2005.04.01   Chg Start K.Sato(GEC16-C-143-005)
// 限度不算入与信合計も計算対象外
            // 限度不算入与信合計、年金転貸、指定L/C小切手、L/Gの当月増減額は計算を行わない
            if( V_KEISU_GNDFUSAN_TOT_BAP <= i && i <= V_KEISU_GNDFUSAN_LG_BAP ) {
                continue;
            }
// 2005.04.01   Chg End K.Sato(GEC16-C-143-005)


// 2003/06/23 ADD@S.SEIMURA 内円貨の当月増減額は計算を行わない(01313)
// 2005.02.14   Chg Start K.Sato(GEC16-C-143-005)
// 協保貸も当月増減額は計算を行わない
            if ( i == V_KEISU_UCHIENKA_BAP || i == V_KEISU_KYOHOGASHI_BAP) {
                continue;
            }
// 2005.02.14   Chg End K.Sato(GEC16-C-143-005)

// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start
// その他一般与信・特定与信合計・特定与信1は計算対象外
            if( i == V_KEISU_IPNYSSNT_BAP || i == V_KEISU_SONOTA_TOT_BAP || i == V_KEISU_SONOTA_YSN1_BAP ) {
                 continue;
            }
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end

            if(ysnValue == 0){
                if(strHonkengo[i].length() != 0 || strGetuZan[i].length() != 0){
                    dataValue = getDataValue(strHonkengo[i]) - getDataValue(strGetuZan[i]);
                    strZogen[i] = Integer.toString(dataValue);
                }else{
                    strZogen[i] = V_EMPTY_STRING;
                }
            }else{
                if(strHonkengo[i].length() != 0 || strKyokudo[i].length() != 0){
                    dataValue = getDataValue(strHonkengo[i]) - getDataValue(strKyokudo[i]);
                    strZogen[i] = Integer.toString(dataValue);
                }else{
                    strZogen[i] = V_EMPTY_STRING;
                }
            }
        }

        /*
         * 各合計の増減額を求める
         *
         */
        //貸付金・商手合計(増減額)
        if( strZogen[V_KEISU_KASHISHO_MEISAI1_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI2_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI3_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI4_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI5_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI6_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI7_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI8_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI9_BAP].length()     != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI10_BAP].length()    != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI11_BAP].length()    != 0 ||
            strZogen[V_KEISU_KASHISHO_MEISAI12_BAP].length()    != 0
        ){
            dataValue = getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI1_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI2_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI3_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI4_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI5_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI6_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI7_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI8_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI9_BAP])    +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI10_BAP])   +
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI11_BAP])+
                        getDataValue(strZogen[V_KEISU_KASHISHO_MEISAI12_BAP]);

            strZogen[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(dataValue);


        }else{
            strZogen[V_KEISU_KASHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


// CHG@2003/09/02   m.otake トラブル(00263)
// 変更管理番号(50966)の対応漏れ
// 外為与信合計を輸出(小計)、輸入(小計)から計算するように変更
// 小計と合計の計算する順番変更及び合計の計算方法変更
        //外為与信合計(増減額)
        if( strZogen[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
            strZogen[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
            strZogen[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
            strZogen[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
            strZogen[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
            strZogen[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
        ){
            dataValue = getDataValue(strZogen[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +
                        getDataValue(strZogen[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +
                        getDataValue(strZogen[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +
                        getDataValue(strZogen[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +
                        getDataValue(strZogen[V_KEISU_GAITAME_KOSHOLC_BAP]) +
                        getDataValue(strZogen[V_KEISU_GAITAME_USANSHIFT_BAP]);
                strZogen[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strZogen[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
        }
// トラブル(00263)End.

        // 支払承諾合計(増減額)
        if( strZogen[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
            strZogen[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
            strZogen[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
        ){
            dataValue = getDataValue(strZogen[V_KEISU_SHISHO_IPAN_BAP]) +
                        getDataValue(strZogen[V_KEISU_SHISHO_IPANGAITA_BAP]) +
                        getDataValue(strZogen[V_KEISU_SHISHO_DAIRIKSTK_BAP]);

            strZogen[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strZogen[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


        if( strZogen[V_KEISU_KASHISHO_TOT_BAP].length()  != 0 ||
            strZogen[V_KEISU_GAITAME_TOT_BAP].length() != 0 ||
            strZogen[V_KEISU_SHISHO_TOT_BAP].length() != 0 ||
            strZogen[V_KEISU_SHIBOSAI_BAP].length() != 0 ||
            strZogen[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0
        ){
            dataValue = getDataValue(strZogen[V_KEISU_KASHISHO_TOT_BAP])  +
                        getDataValue(strZogen[V_KEISU_GAITAME_TOT_BAP]) +
                        getDataValue(strZogen[V_KEISU_SHISHO_TOT_BAP]) +
                        getDataValue(strZogen[V_KEISU_SHIBOSAI_BAP]) +
                        getDataValue(strZogen[V_KEISU_GENDOLOAN_TOT_BAP]);

            strZogen[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strZogen[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;
        }
// 2007.01.15 Mod End  M.Kawano(GEC18-C-043)

        // 限度算入与信合計(増減額)
        if( strZogen[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||
            strZogen[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0
        ){
            dataValue = getDataValue(strZogen[V_KEISU_ONBALANCE_TOT_BAP])  +
                        getDataValue(strZogen[V_KEISU_OFFBALANCE_TOT_BAP]);
            strZogenTot[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(dataValue);
        }else{
            strZogenTot[V_KEISU_KASHISHO_TOT_BAP] = V_EMPTY_STRING;
        }


        // 一般与信合計(増減額)
        if(strZogenTot[V_KEISU_GENDOSAN_TOT_BAP].length() != 0){
            strZogen[V_KEISU_IPPANYSN_TOT_BAP] = strZogenTot[V_KEISU_GENDOSAN_TOT_BAP];
        }else{
            strZogen[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;
        }


        /*
         * 結果を共有情報に登録する
         */
        hstDb.put(F_LMT, strKyokudo);
        hstDb.put(F_HONAF_ZAN, strHonkengo);

//2003.03.13 Add
        hstDb.put(F_MEND_ZAN, strGetuZan);
        hstDb.put(F_IPNYSNDLTZGG, strZogen);
        hstDb.put(F_JISKSN, strJissei);
        hstDb.put(F_IPNYSNDLTZGG_TOT, strZogenTot);

//2003.07.30 Add m.otake    変更管理連絡票(50966)
        hstDb.put(F_LMT_TOT, strLmtTot);
        hstDb.put(F_HONAF_ZAN_TOT, strHonafTot);

        hstComBasket.put(K_DB_DATA, hstDb);


        return;

    }

/*******  ここまで一般与信  *******/





    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数画面で計算ボタンを押された時に、入力されている一般与信データと
     *   ＤＢに登録されている一般与信データの差分を求め、
     *   合計項目値を取得する。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable  hstTbl              画面からの入力データ
     *   @param  Hashtable  hstComBasket    ＤＢからの入力データ
     */
    public void computeYosinKeisan(Hashtable hstTbl, Hashtable hstComBasket) {


        /*
         * 画面から入力されたテーブルデータの、横系の計算を行う
         * 横系の計算：当月増減額の算出
         */

        try {

            Hashtable sabun = new Hashtable();
            Hashtable db = (Hashtable)hstComBasket.get(K_DB_DATA);


            //与信状況・極度額
            String[] strYosinKyokudoL  = (String[])hstTbl.get(F_LMT);
            //与信状況・指定月末残高
            String[] strYosinGetuzanL  = (String[])hstTbl.get(F_MEND_ZAN);
            //与信状況・当月増減額
            String[] strYosinZogenL    = (String[])hstTbl.get(F_IPNYSNDLTZGG);
            //与信状況・本件後残高
            String[] strYosinHonkengoL = (String[])hstTbl.get(F_HONAF_ZAN);
            //与信状況・実勢現在残
            String[] strYosinJisseiL   = (String[])hstTbl.get(F_JISKSN);



            //画面から取得したデータ領域
            // 限度算入与信合計（指定月末残高）
            String strGokeiGetuzan = null;
            // 限度算入与信合計（極度額）
            String strGokeiKyokudo = null;
            // 限度算入与信合計（当月増減額）
            String strGokeiZogen = null;
            // 限度算入与信合計（本件後残高）
            String strGokeiHonkengo = null;
            // 限度算入与信合計（実勢現在残高）
            String strGokeiJissei = null;


            //差分の格納領域
            String[] Kyokudo = new String[V_KEISU_IPNYSN_ARR_NUM];
            String[] Getuzan = new String[V_KEISU_IPNYSN_ARR_NUM];
            String[] Zogen  = new String[V_KEISU_IPNYSN_ARR_NUM];
            String[] Honkengo = new String[V_KEISU_IPNYSN_ARR_NUM];
            String[] Jissei  = new String[V_KEISU_IPNYSN_ARR_NUM];

            // 画面から入力された情報を、新しい配列にコピー
            System.arraycopy(strYosinKyokudoL,  0, Kyokudo,  0, strYosinKyokudoL.length );
            System.arraycopy(strYosinGetuzanL,  0, Getuzan,  0, strYosinGetuzanL.length );
            System.arraycopy(strYosinZogenL,    0, Zogen,    0, strYosinZogenL.length   );
            System.arraycopy(strYosinHonkengoL, 0, Honkengo, 0, strYosinHonkengoL.length);
            System.arraycopy(strYosinJisseiL,   0, Jissei,   0, strYosinJisseiL.length  );

            //DBから取得したデータ領域
            String[] dbGetuzan  = (String[])db.get(F_MEND_ZAN);
            String[] dbKyokudo  = (String[])db.get(F_LMT);
            String[] dbZogen   = (String[])db.get(F_IPNYSNDLTZGG);
            String[] dbHonkengo = (String[])db.get(F_HONAF_ZAN);
            String[] dbJissei   = (String[])db.get(F_JISKSN);


            int dataValue  = 0;
            int intWorkValue1 = 0;
            int intWorkValue2 = 0;
            int intWorkValue3 = 0;


            /* --------------------------------------------------------
             * 与信状況の項目
             * --------------------------------------------------------
             */

            /*
             * 各行の増減額の計算を行う
             * 全ての計算式は以下の通り
             * 極度額がある時：（本件後残高）－（極度額）
             * 極度額がない時：（本件後残高）－（月末残高）
             * また極度額が０の時は、極度額が無い時の計算とする
             * ※限度算入与信合計は計算に入れていないが、後で計算されるので、ここでは行わない
             */

// 2003.03.14 Add
            // 以下のfor文内は画面のリスト項目
            for(int i = 0; i < V_KEISU_IPNYSN_ARR_NUM; i++) {

                int ysnValue = getDataValue(strYosinKyokudoL[i]);

// 2005.04.01   Chg Start K.Sato(GEC16-C-143-005)
// 限度不算入与信合計も計算対象外
            // 限度不算入与信合計、年金転貸、指定L/C小切手、L/Gの当月増減額は計算を行わない
            if( V_KEISU_GNDFUSAN_TOT_BAP <= i && i <= V_KEISU_GNDFUSAN_LG_BAP ) {
                    continue;
                }
// 2005.04.01   Chg End K.Sato(GEC16-C-143-005)


// 2003/06/23 ADD@S.SEIMURA 内円貨の当月増減額は計算を行わない(01313)
// 2005.02.14   Chg Start K.Sato(GEC16-C-143-005)
// 協保貸も当月増減額は計算を行わない
            if ( i == V_KEISU_UCHIENKA_BAP || i == V_KEISU_KYOHOGASHI_BAP) {
                continue;
            }
// 2005.02.14   Chg End K.Sato(GEC16-C-143-005)

// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start
// その他一般与信・特定与信1は計算対象外
            if ( i == V_KEISU_IPNYSSNT_BAP || i == V_KEISU_SONOTA_YSN1_BAP) {
                continue;
            }
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end

                if(ysnValue == 0){
                    if(strYosinHonkengoL[i].length() != 0 || strYosinGetuzanL[i].length() != 0){
                        dataValue = getDataValue(strYosinHonkengoL[i]) - getDataValue(strYosinGetuzanL[i]);
                        strYosinZogenL[i] = Integer.toString(dataValue);
                    }else{
                        strYosinZogenL[i] = V_EMPTY_STRING;
                    }
                }else{
                    if(strYosinHonkengoL[i].length() != 0 || strYosinKyokudoL[i].length() != 0){
                        dataValue = getDataValue(strYosinHonkengoL[i]) - getDataValue(strYosinKyokudoL[i]);
                        strYosinZogenL[i] = Integer.toString(dataValue);
                    }else{
                        strYosinZogenL[i] = V_EMPTY_STRING;
                    }
                }
            }


            /* --------------------------------------------------------
             * ここまでが小計、合計以外の横計算
             * --------------------------------------------------------
             */




            /*
             * 計算結果とＤＢに登録されているデータとの差分を求める
             */
            for(int i = 0; i < V_KEISU_IPNYSN_ARR_NUM; i++) {

// 2005.06.27   Chg Start K.Sato(GEC16-C-143-005)
// 協保貸は増減額の差分計算を行う
                // 年金転貸・指定L/C小切手・L/Gの月末残高・極度額・当月増減の
                // 差分計算を行わない
//              if( ( i <= V_KEISU_GNDFUSAN_TOT_BAP || V_KEISU_IPPANYSN_TOT_BAP <= i ) && i != V_KEISU_KYOHOGASHI_BAP ) {
                if( i <= V_KEISU_GNDFUSAN_TOT_BAP || V_KEISU_IPPANYSN_TOT_BAP <= i ) {


                    // 月末残高
                    if( strYosinGetuzanL[i].length() != 0 ||
                        dbGetuzan[i].length() != 0
                    ){
                        dataValue = getDataValue(strYosinGetuzanL[i]) -
                                                    getDataValue(dbGetuzan[i]);
                        Getuzan[i] = Integer.toString(dataValue);
                    }else{
                        Getuzan[i] = V_EMPTY_STRING;
                    }


                    // 極度額
                    if( strYosinKyokudoL[i].length() != 0 ||
                        dbKyokudo[i].length() != 0
                    ){
                        dataValue = getDataValue(strYosinKyokudoL[i] ) -
                                                    getDataValue(dbKyokudo[i]);
                        Kyokudo[i] = Integer.toString(dataValue);
                    }else{
                        Kyokudo[i] = V_EMPTY_STRING;
                    }


                    // 当月増減
                    if( strYosinZogenL[i].length() != 0 ||
                        dbZogen[i].length() != 0
                    ){
                        dataValue = getDataValue(strYosinZogenL[i]) -
                                                    getDataValue(dbZogen[i]);
                        Zogen[i] = Integer.toString(dataValue);
                    }else{
                        Zogen[i] = V_EMPTY_STRING;
                    }
                }

// 2005.06.27   Chg End K.Sato(GEC16-C-143-005)


                // 本件後残高
                if( strYosinHonkengoL[i].length() != 0 ||
                    dbHonkengo[i].length() != 0
                ){
                    dataValue = getDataValue(strYosinHonkengoL[i]) -
                                                getDataValue(dbHonkengo[i]);
                    Honkengo[i] = Integer.toString(dataValue);
                }else{
                    Honkengo[i] = V_EMPTY_STRING;
                }


                // 実勢現在残
                if( strYosinJisseiL[i].length() != 0 ||
                    dbJissei[i].length() != 0
                ){
                    dataValue = getDataValue(strYosinJisseiL[i]) -
                                                getDataValue(dbJissei[i]);
                    Jissei[i] = Integer.toString(dataValue);
                }else{
                    Jissei[i] = V_EMPTY_STRING;
                }
            }

            /* --------------------------------------------------------
             * ここまでがＤＢに登録されている項目との差分計算
             * --------------------------------------------------------
             */




            /*
             * 合計項目の計算（縦系の計算）
             * 計算された差分を使用して、合計項目の差分を算出する
             */


            /*
             * 貸付金・商手合計の項目（明細より算出）
             */
            int intGetuzan = 0;
            int intKyokudo = 0;
            int intZogen = 0;
            int intHonkengo = 0;
            int intJissei = 0;

            Getuzan[V_KEISU_KASHISHO_TOT_BAP]   = V_EMPTY_STRING;
            Kyokudo[V_KEISU_KASHISHO_TOT_BAP]   = V_EMPTY_STRING;
            Zogen[V_KEISU_KASHISHO_TOT_BAP]     = V_EMPTY_STRING;
            Honkengo[V_KEISU_KASHISHO_TOT_BAP]  = V_EMPTY_STRING;
            Jissei[V_KEISU_KASHISHO_TOT_BAP]    = V_EMPTY_STRING;


            // 月末残高
            for(int i = V_KEISU_KASHISHO_MEISAI1_BAP ; i <= V_KEISU_KASHISHO_MEISAI12_BAP ; i++ ){
                if(Getuzan[i].length() != 0){
                    for(int j = V_KEISU_KASHISHO_MEISAI1_BAP ; j <= V_KEISU_KASHISHO_MEISAI12_BAP ; j++){
                        intGetuzan += getDataValue(Getuzan[j]);
                    }
                    Getuzan[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(intGetuzan);
                    break;
                }
            }


            // 極度額
            for(int i = V_KEISU_KASHISHO_MEISAI1_BAP ; i <= V_KEISU_KASHISHO_MEISAI12_BAP ; i++ ){
                if(Kyokudo[i].length() != 0){
                    for(int j = V_KEISU_KASHISHO_MEISAI1_BAP ; j <= V_KEISU_KASHISHO_MEISAI12_BAP ; j++){
                        intKyokudo += getDataValue(Kyokudo[j]);
                    }
                    Kyokudo[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(intKyokudo);
                    break;
                }
            }


            // 増減額
            for(int i = V_KEISU_KASHISHO_MEISAI1_BAP ; i <= V_KEISU_KASHISHO_MEISAI12_BAP ; i++ ){
                if(Zogen[i].length() != 0){
                    for(int j = V_KEISU_KASHISHO_MEISAI1_BAP ; j <= V_KEISU_KASHISHO_MEISAI12_BAP ; j++){
                        intZogen += getDataValue(Zogen[j]);
                    }
                    Zogen[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(intZogen);
                    break;
                }
            }


            // 本件後残高
            for(int i = V_KEISU_KASHISHO_MEISAI1_BAP ; i <= V_KEISU_KASHISHO_MEISAI12_BAP ; i++ ){
                if(Honkengo[i].length() != 0){
                    for(int j = V_KEISU_KASHISHO_MEISAI1_BAP ; j <= V_KEISU_KASHISHO_MEISAI12_BAP ; j++){
                        intHonkengo += getDataValue(Honkengo[j]);
                    }
                    Honkengo[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(intHonkengo);
                    break;
                }
            }


            // 実勢現在残
            for(int i = V_KEISU_KASHISHO_MEISAI1_BAP ; i <= V_KEISU_KASHISHO_MEISAI12_BAP ; i++ ){
                if(Jissei[i].length() != 0){
                    for(int j = V_KEISU_KASHISHO_MEISAI1_BAP ; j <= V_KEISU_KASHISHO_MEISAI12_BAP ; j++){
                        intJissei += getDataValue(Jissei[j]);
                    }
                    Jissei[V_KEISU_KASHISHO_TOT_BAP] = Integer.toString(intJissei);
                    break;
                }
            }

// CHG@2003/07/30   m.otake 変更管理番号(50966)
// 外為与信合計を輸出(小計)、輸入(小計)から計算するように変更
// 小計と合計の計算する順番変更及び合計の計算方法変更
            /*
             * 外為与信・輸出小計項目
             */
            // 外為与信・輸出小計（指定月末残高）
            if( Getuzan[V_KEISU_GAITAME_SHITEIGAILC_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_DPDA_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_GAIKAKITTE_BAP].length() != 0
            ){
                dataValue = getDataValue(Getuzan[V_KEISU_GAITAME_SHITEIGAILC_BAP]) +        // [外為与信・指定外Ｌ／Ｃ（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_GAITAME_DPDA_BAP]) +       // [外為与信・Ｄ／Ｐ・Ｄ／Ａ（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_GAITAME_GAIKAKITTE_BAP]);      // [外為与信・外貨小切手（指定月末残高）]
                Getuzan[V_KEISU_GAITAME_YUSYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Getuzan[V_KEISU_GAITAME_YUSYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸出小計（極度額）
            if( Kyokudo[V_KEISU_GAITAME_SHITEIGAILC_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_DPDA_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_GAIKAKITTE_BAP].length() != 0
            ){
                dataValue = getDataValue(Kyokudo[V_KEISU_GAITAME_SHITEIGAILC_BAP]) +        // [外為与信・指定外Ｌ／Ｃ（極度額）]
                            getDataValue(Kyokudo[V_KEISU_GAITAME_DPDA_BAP]) +       // [外為与信・Ｄ／Ｐ・Ｄ／Ａ（極度額）]
                            getDataValue(Kyokudo[V_KEISU_GAITAME_GAIKAKITTE_BAP]);      // [外為与信・外貨小切手（極度額）]
                Kyokudo[V_KEISU_GAITAME_YUSYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Kyokudo[V_KEISU_GAITAME_YUSYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸出小計（本件後残高）
            if( Honkengo[V_KEISU_GAITAME_SHITEIGAILC_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_DPDA_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_GAIKAKITTE_BAP].length() != 0
            ){
                dataValue = getDataValue(Honkengo[V_KEISU_GAITAME_SHITEIGAILC_BAP]) +       // [外為与信・指定外Ｌ／Ｃ（本件後残高）]
                            getDataValue(Honkengo[V_KEISU_GAITAME_DPDA_BAP]) +      // [外為与信・Ｄ／Ｐ・Ｄ／Ａ（本件後残高）]
                            getDataValue(Honkengo[V_KEISU_GAITAME_GAIKAKITTE_BAP]);     // [外為与信・外貨小切手（本件後残高）]
                Honkengo[V_KEISU_GAITAME_YUSYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Honkengo[V_KEISU_GAITAME_YUSYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸出小計（当月増減額）
            if( Zogen[V_KEISU_GAITAME_SHITEIGAILC_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_DPDA_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_GAIKAKITTE_BAP].length() != 0
            ){

                dataValue = getDataValue(Zogen[V_KEISU_GAITAME_SHITEIGAILC_BAP]) +      // [外為与信・指定外Ｌ／Ｃ（当月増減額）]
                            getDataValue(Zogen[V_KEISU_GAITAME_DPDA_BAP]) +     // [外為与信・Ｄ／Ｐ・Ｄ／Ａ（当月増減額）]
                            getDataValue(Zogen[V_KEISU_GAITAME_GAIKAKITTE_BAP]) ;       // [外為与信・外貨小切手（当月増減額）]
                Zogen[V_KEISU_GAITAME_YUSYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Zogen[V_KEISU_GAITAME_YUSYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸出小計（実勢現在残高）
            if( Jissei[V_KEISU_GAITAME_SHITEIGAILC_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_DPDA_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_GAIKAKITTE_BAP].length() != 0
            ){
                dataValue = getDataValue(Jissei[V_KEISU_GAITAME_SHITEIGAILC_BAP]) +         // [外為与信・指定外Ｌ／Ｃ（実勢現在残高）]
                            getDataValue(Jissei[V_KEISU_GAITAME_DPDA_BAP]) +            // [外為与信・Ｄ／Ｐ・Ｄ／Ａ（実勢現在残高）]
                            getDataValue(Jissei[V_KEISU_GAITAME_GAIKAKITTE_BAP]);           // [外為与信・外貨小切手（実勢現在残高）]
                Jissei[V_KEISU_GAITAME_YUSYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Jissei[V_KEISU_GAITAME_YUSYU_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 外為与信・輸入小計項目
             */

// 2004/04/13 CHG@S.SEIMURA 判定式の修正(GEC16-C-006)
            // 外為与信・輸入小計（指定月末残高）
            if( Getuzan[V_KEISU_GAITAME_YUNYULC_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_USANCE_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_LG_BAP].length() != 0
            ){
                dataValue = getDataValue(Getuzan[V_KEISU_GAITAME_YUNYULC_BAP]) +        // [外為与信・輸入Ｌ／Ｃ（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_GAITAME_USANCE_BAP]) +     // [外為与信・ユーザンス（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_GAITAME_LG_BAP]);      // [外為与信・Ｌ／Ｇ（指定月末残高）]
                Getuzan[V_KEISU_GAITAME_YUNYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Getuzan[V_KEISU_GAITAME_YUNYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸入小計（本件後残高）
            if( Honkengo[V_KEISU_GAITAME_YUNYULC_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_USANCE_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_LG_BAP].length() != 0
            ){
                dataValue = getDataValue(Honkengo[V_KEISU_GAITAME_YUNYULC_BAP]) +       // [外為与信・輸入Ｌ／Ｃ（本件後残高）]
                            getDataValue(Honkengo[V_KEISU_GAITAME_USANCE_BAP]) +        // [外為与信・ユーザンス（本件後残高）]
                            getDataValue(Honkengo[V_KEISU_GAITAME_LG_BAP]);     // [外為与信・Ｌ／Ｇ（本件後残高）]
                Honkengo[V_KEISU_GAITAME_YUNYU_STOT_BAP] = Integer.toString(dataValue);
                intWorkValue1 = dataValue;
            }else{
                Honkengo[V_KEISU_GAITAME_YUNYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸入小計（極度額）
            if( Kyokudo[V_KEISU_GAITAME_YUNYULC_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_USANCE_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_LG_BAP].length() != 0
            ){
                dataValue = getDataValue(Kyokudo[V_KEISU_GAITAME_YUNYULC_BAP]) +        // [外為与信・輸入Ｌ／Ｃ（極度額）]
                            getDataValue(Kyokudo[V_KEISU_GAITAME_USANCE_BAP]) +     // [外為与信・ユーザンス（極度額）]
                            getDataValue(Kyokudo[V_KEISU_GAITAME_LG_BAP]);      // [外為与信・Ｌ／Ｇ（極度額）]
                Kyokudo[V_KEISU_GAITAME_YUNYU_STOT_BAP] = Integer.toString(dataValue);
                intWorkValue2 = dataValue;
            }else{
                Kyokudo[V_KEISU_GAITAME_YUNYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸入小計（当月増減額）
            if( Zogen[V_KEISU_GAITAME_YUNYULC_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_USANCE_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_LG_BAP].length() != 0
            ){
                dataValue = getDataValue(Zogen[V_KEISU_GAITAME_YUNYULC_BAP]) +      // [外為与信・輸入Ｌ／Ｃ（当月増減額）]
                            getDataValue(Zogen[V_KEISU_GAITAME_USANCE_BAP]) +       // [外為易与信・ユーザンス（当月増減額）]
                            getDataValue(Zogen[V_KEISU_GAITAME_LG_BAP]);            // [外為与信・Ｌ／Ｇ（当月増減額）]
                Zogen[V_KEISU_GAITAME_YUNYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Zogen[V_KEISU_GAITAME_YUNYU_STOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信・輸入小計（実勢現在残高）
            if( Jissei[V_KEISU_GAITAME_YUNYULC_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_USANCE_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_LG_BAP].length() != 0
            ){
                dataValue = getDataValue(Jissei[V_KEISU_GAITAME_YUNYULC_BAP]) +     // [外為与信・輸入Ｌ／Ｃ（実勢現在残高）]
                            getDataValue(Jissei[V_KEISU_GAITAME_USANCE_BAP]) +      // [外為与信・ユーザンス（実勢現在残高）]
                            getDataValue(Jissei[V_KEISU_GAITAME_LG_BAP]);       // [外為与信・Ｌ／Ｇ（実勢現在残高）]
                Jissei[V_KEISU_GAITAME_YUNYU_STOT_BAP] = Integer.toString(dataValue);
            }else{
                Jissei[V_KEISU_GAITAME_YUNYU_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 外為与信合計項目
             */
            // 指定月末残高
            if( Getuzan[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
                Getuzan[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
            ){
                dataValue = getDataValue(Getuzan[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +     //輸出(小計)
                            getDataValue(Getuzan[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +     //貸出(輸出)
                            getDataValue(Getuzan[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +     //輸入(小計)
                            getDataValue(Getuzan[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +     //貸出(輸入)
                            getDataValue(Getuzan[V_KEISU_GAITAME_KOSHOLC_BAP]) +        //故障指定L/C
                            getDataValue(Getuzan[V_KEISU_GAITAME_USANSHIFT_BAP]);       //ユーザンスシフト外貨
                Getuzan[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Getuzan[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信合計（極度額）
            if( Kyokudo[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
                Kyokudo[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
            ){
                dataValue = getDataValue(Kyokudo[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +     //輸出(小計)
                            getDataValue(Kyokudo[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +     //貸出(輸出)
                            getDataValue(Kyokudo[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +     //輸入(小計)
                            getDataValue(Kyokudo[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +     //貸出(輸入)
                            getDataValue(Kyokudo[V_KEISU_GAITAME_KOSHOLC_BAP]) +        //故障指定L/C
                            getDataValue(Kyokudo[V_KEISU_GAITAME_USANSHIFT_BAP]);       //ユーザンスシフト外貨
                Kyokudo[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Kyokudo[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
            }



            // 外為与信合計（当月増減額）
            if( Zogen[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
                Zogen[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
            ){
                dataValue = getDataValue(Zogen[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +       //輸出(小計)
                            getDataValue(Zogen[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +       //貸出(輸出)
                            getDataValue(Zogen[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +       //輸入(小計)
                            getDataValue(Zogen[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +       //貸出(輸入)
                            getDataValue(Zogen[V_KEISU_GAITAME_KOSHOLC_BAP]) +      //故障指定L/C
                            getDataValue(Zogen[V_KEISU_GAITAME_USANSHIFT_BAP]);         //ユーザンスシフト外貨
                Zogen[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Zogen[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信合計（本件後残高）
            if( Honkengo[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
                Honkengo[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
            ){
                dataValue = getDataValue(Honkengo[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +        //輸出(小計)
                            getDataValue(Honkengo[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +        //貸出(輸出)
                            getDataValue(Honkengo[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +        //輸入(小計)
                            getDataValue(Honkengo[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +        //貸出(輸入)
                            getDataValue(Honkengo[V_KEISU_GAITAME_KOSHOLC_BAP]) +       //故障指定L/C
                            getDataValue(Honkengo[V_KEISU_GAITAME_USANSHIFT_BAP]);      //ユーザンスシフト外貨
                Honkengo[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Honkengo[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
            }


            // 外為与信合計（実勢現在残高）
            if( Jissei[V_KEISU_GAITAME_YUSYU_STOT_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_KSDS_YUSYU_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_YUNYU_STOT_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_KSDS_YUNYU_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_KOSHOLC_BAP].length() != 0 ||
                Jissei[V_KEISU_GAITAME_USANSHIFT_BAP].length() != 0
            ){
                dataValue = getDataValue(Jissei[V_KEISU_GAITAME_YUSYU_STOT_BAP]) +      //輸出(小計)
                            getDataValue(Jissei[V_KEISU_GAITAME_KSDS_YUSYU_BAP]) +      //貸出(輸出)
                            getDataValue(Jissei[V_KEISU_GAITAME_YUNYU_STOT_BAP]) +      //輸入(小計)
                            getDataValue(Jissei[V_KEISU_GAITAME_KSDS_YUNYU_BAP]) +      //貸出(輸入)
                            getDataValue(Jissei[V_KEISU_GAITAME_KOSHOLC_BAP]) +     //故障指定L/C
                            getDataValue(Jissei[V_KEISU_GAITAME_USANSHIFT_BAP]);        //ユーザンスシフト外貨
                Jissei[V_KEISU_GAITAME_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Jissei[V_KEISU_GAITAME_TOT_BAP] = V_EMPTY_STRING;
            }

// CHG@2003/07/30   m.otake 変更管理番号(50966)   修正範囲ここまで


            /*
             * 支払承諾合計項目
             */
            // 支払承諾合計（指定月末残高）
            if( Getuzan[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
                Getuzan[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
                Getuzan[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
            ){
                dataValue = getDataValue(Getuzan[V_KEISU_SHISHO_IPAN_BAP]) +        // [支払承諾・支承・一般（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_SHISHO_IPANGAITA_BAP]) +       // [支払承諾・支承・一般外為（指定月末残高）]
                            getDataValue(Getuzan[V_KEISU_SHISHO_DAIRIKSTK_BAP]);        // [支払承諾・代理貸付（指定月末残高）]
                Getuzan[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);
            }else{
                Getuzan[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;
            }


            // 支払承諾合計（極度額）
            if( Kyokudo[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||
                Kyokudo[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||
                Kyokudo[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0
            ){
                dataValue = getDataValue(Kyokudo[V_KEISU_SHISHO_IPAN_BAP]) +        // [支払承諾・支承・一般（極度額）]
                            getDataValue(Kyokudo[V_KEISU_SHISHO_IPANGAITA_BAP]) +       // [支払承諾・支承・一般外為（極度額）

]

                            getDataValue(Kyokudo[V_KEISU_SHISHO_DAIRIKSTK_BAP]);        // [支払承諾・代理貸付（極度額）]

                Kyokudo[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Kyokudo[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;

            }



            // 支払承諾合計（当月増減額）

            if( Zogen[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||

                Zogen[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||

                Zogen[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0

            ){

                dataValue = getDataValue(Zogen[V_KEISU_SHISHO_IPAN_BAP]) +      // [支払承諾・支承・一般（当月増減額）]

                            getDataValue(Zogen[V_KEISU_SHISHO_IPANGAITA_BAP]) +     // [支払承諾・支承・一般外為（当月増減額）]

                            getDataValue(Zogen[V_KEISU_SHISHO_DAIRIKSTK_BAP]);          // [支払承諾・代理貸付（当月増減額）]

                Zogen[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Zogen[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;

            }



            // 支払承諾合計（本件後残高）

            if( Honkengo[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||

                Honkengo[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||

                Honkengo[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0

            ){

                dataValue = getDataValue(Honkengo[V_KEISU_SHISHO_IPAN_BAP]) +       // [支払承諾・支承・一般（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_SHISHO_IPANGAITA_BAP]) +      // [支払承諾・支承・一般外為（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_SHISHO_DAIRIKSTK_BAP]);       // [支払承諾・代理貸付（本件後残高）]

                Honkengo[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Honkengo[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;

            }



            // 支払承諾合計（実勢現在残高）

            if( Jissei[V_KEISU_SHISHO_IPAN_BAP].length() != 0 ||

                Jissei[V_KEISU_SHISHO_IPANGAITA_BAP].length() != 0 ||

                Jissei[V_KEISU_SHISHO_DAIRIKSTK_BAP].length() != 0

            ){

                dataValue = getDataValue(Jissei[V_KEISU_SHISHO_IPAN_BAP]) +     // [支払承諾・支承・一般（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_SHISHO_IPANGAITA_BAP]) +        // [支払承諾・支承・一般外為（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_SHISHO_DAIRIKSTK_BAP]);     // [支払承諾・代理貸付（実勢現在残高）]

                Jissei[V_KEISU_SHISHO_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Jissei[V_KEISU_SHISHO_TOT_BAP] = V_EMPTY_STRING;

            }




// 2005.03.01   Chg Start K.Sato(GEC16-C-143-005)

// オンバランス合計の計算方法の変更

// 変更前：貸付金・商手合計＋外為与信合計＋支払承諾合計＋限度算入ローン合計

// 変更後：貸付金・商手合計＋外為与信合計＋支払承諾合計＋私募債＋協保貸＋限度算入ローン合計

            /*

             * オンバランス合計・オフバランス合計

             */

            // オンバランス合計（指定月末残高）

            if( Getuzan[V_KEISU_KASHISHO_TOT_BAP].length()  != 0 ||

                Getuzan[V_KEISU_GAITAME_TOT_BAP].length()   != 0 ||

                Getuzan[V_KEISU_SHISHO_TOT_BAP].length()    != 0 ||

                Getuzan[V_KEISU_SHIBOSAI_BAP].length()      != 0 ||

                Getuzan[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Getuzan[V_KEISU_KASHISHO_TOT_BAP]) +   // [一般与信合計（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_GAITAME_TOT_BAP])  +   // [貿易与信合計（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_SHISHO_TOT_BAP])   +   // [支払承諾合計（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_SHIBOSAI_BAP])     +   // [私募債（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_GENDOLOAN_TOT_BAP]);   // [限度算入ローン合計（指定月末残高）]

                Getuzan[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Getuzan[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

            }



            // オンバランス合計（極度額）

            if( Kyokudo[V_KEISU_KASHISHO_TOT_BAP].length()  != 0 ||

                Kyokudo[V_KEISU_GAITAME_TOT_BAP].length()   != 0 ||

                Kyokudo[V_KEISU_SHISHO_TOT_BAP].length()    != 0 ||

                Kyokudo[V_KEISU_SHIBOSAI_BAP].length()      != 0 ||

                Kyokudo[V_KEISU_GENDOLOAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Kyokudo[V_KEISU_KASHISHO_TOT_BAP] )    +   // [一般与信合計（極度額）]

                            getDataValue(Kyokudo[V_KEISU_GAITAME_TOT_BAP])      +   // [貿易与信合計（極度額）]

                            getDataValue(Kyokudo[V_KEISU_SHISHO_TOT_BAP])       +   // [支払承諾合計（極度額）]

                            getDataValue(Kyokudo[V_KEISU_SHIBOSAI_BAP])         +   // [私募債（極度額）]

                            getDataValue(Kyokudo[V_KEISU_GENDOLOAN_TOT_BAP]);       // [限度算入ローン合計（極度額）]

                Kyokudo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Kyokudo[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

            }



// 2005.06.27   Chg Start K.Sato(GEC16-C-143-005)

// 協保貸も計算対象とする

// 変更前：貸付金・商手合計＋外為与信合計＋支払承諾合計＋私募債＋限度算入ローン合計

// 変更後：貸付金・商手合計＋外為与信合計＋支払承諾合計＋私募債＋協保貸＋限度算入ローン合計


// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start

// オンバランス合計（当月増減額・本件後残高・実勢現在残）の計算式を変更

// その他一般与信を追加

            // オンバランス合計（当月増減額）

//          if( Zogen[V_KEISU_KASHISHO_TOT_BAP].length()    != 0 ||

//              Zogen[V_KEISU_GAITAME_TOT_BAP].length()     != 0 ||

//              Zogen[V_KEISU_SHISHO_TOT_BAP].length()      != 0 ||

//              Zogen[V_KEISU_SHIBOSAI_BAP].length()        != 0 ||

//              Zogen[V_KEISU_KYOHOGASHI_BAP].length()      != 0 ||

//              Zogen[V_KEISU_GENDOLOAN_TOT_BAP].length()   != 0

//          ){

//              dataValue = getDataValue(Zogen[V_KEISU_KASHISHO_TOT_BAP] )  +   // [一般与信合計（当月増減額）]

//                          getDataValue(Zogen[V_KEISU_GAITAME_TOT_BAP])    +   // [貿易与信合計（当月増減額）]

//                          getDataValue(Zogen[V_KEISU_SHISHO_TOT_BAP])     +   // [支払承諾合計（当月増減額）]

//                          getDataValue(Zogen[V_KEISU_SHIBOSAI_BAP])       +   // [私募債（当月増減額）]

//                          getDataValue(Zogen[V_KEISU_KYOHOGASHI_BAP])     +   // [協保貸（当月増減額）]

//                          getDataValue(Zogen[V_KEISU_GENDOLOAN_TOT_BAP]);     // [限度算入ローン合計（当月増減額）]

//              Zogen[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

//          }else{

//              Zogen[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

//          }


            if( Zogen[V_KEISU_KASHISHO_TOT_BAP].length()    != 0 ||

                Zogen[V_KEISU_GAITAME_TOT_BAP].length()     != 0 ||

                Zogen[V_KEISU_SHISHO_TOT_BAP].length()      != 0 ||

                Zogen[V_KEISU_SHIBOSAI_BAP].length()        != 0 ||

                Zogen[V_KEISU_KYOHOGASHI_BAP].length()      != 0 ||

                Zogen[V_KEISU_IPNYSSNT_BAP].length()        != 0 ||

                Zogen[V_KEISU_GENDOLOAN_TOT_BAP].length()   != 0

            ){

                dataValue = getDataValue(Zogen[V_KEISU_KASHISHO_TOT_BAP] )  +   // [一般与信合計（当月増減額）]

                            getDataValue(Zogen[V_KEISU_GAITAME_TOT_BAP])    +   // [貿易与信合計（当月増減額）]

                            getDataValue(Zogen[V_KEISU_SHISHO_TOT_BAP])     +   // [支払承諾合計（当月増減額）]

                            getDataValue(Zogen[V_KEISU_SHIBOSAI_BAP])       +   // [私募債（当月増減額）]

                            getDataValue(Zogen[V_KEISU_KYOHOGASHI_BAP])     +   // [協保貸（当月増減額）]

                            getDataValue(Zogen[V_KEISU_IPNYSSNT_BAP])       +   // [その他一般与信（当月増減額）]

                            getDataValue(Zogen[V_KEISU_GENDOLOAN_TOT_BAP]);     // [限度算入ローン合計（当月増減額）]

                Zogen[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Zogen[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

            }

// 2005.06.27   Chg End K.Sato(GEC16-C-143-005)



            // オンバランス合計（本件後残高）

//          if( Honkengo[V_KEISU_KASHISHO_TOT_BAP].length() != 0 ||

//              Honkengo[V_KEISU_GAITAME_TOT_BAP].length()  != 0 ||

//              Honkengo[V_KEISU_SHISHO_TOT_BAP].length()   != 0 ||

//              Honkengo[V_KEISU_SHIBOSAI_BAP].length()     != 0 ||

//              Honkengo[V_KEISU_KYOHOGASHI_BAP].length()       != 0 ||

//              Honkengo[V_KEISU_GENDOLOAN_TOT_BAP].length()    != 0

//          ){

//              dataValue = getDataValue(Honkengo[V_KEISU_KASHISHO_TOT_BAP] )   +   // [一般与信合計（本件後残高）]

//                          getDataValue(Honkengo[V_KEISU_GAITAME_TOT_BAP])     +   // [貿易与信合計（本件後残高）]

//                          getDataValue(Honkengo[V_KEISU_SHISHO_TOT_BAP])      +   // [支払承諾合計（本件後残高）]

//                          getDataValue(Honkengo[V_KEISU_SHIBOSAI_BAP])        +   // [私募債（本件後残高）]

//                          getDataValue(Honkengo[V_KEISU_KYOHOGASHI_BAP])      +   // [協保貸（本件後残高）]

//                          getDataValue(Honkengo[V_KEISU_GENDOLOAN_TOT_BAP]);      // [限度算入ローン合計（本件後残高）]

//              Honkengo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

//          }else{

//              Honkengo[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

//          }

            if( Honkengo[V_KEISU_KASHISHO_TOT_BAP].length() != 0 ||

                Honkengo[V_KEISU_GAITAME_TOT_BAP].length()  != 0 ||

                Honkengo[V_KEISU_SHISHO_TOT_BAP].length()   != 0 ||

                Honkengo[V_KEISU_SHIBOSAI_BAP].length()     != 0 ||

                Honkengo[V_KEISU_KYOHOGASHI_BAP].length()       != 0 ||

                Honkengo[V_KEISU_IPNYSSNT_BAP].length()         != 0 ||

                Honkengo[V_KEISU_GENDOLOAN_TOT_BAP].length()    != 0

            ){

                dataValue = getDataValue(Honkengo[V_KEISU_KASHISHO_TOT_BAP] )   +   // [一般与信合計（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_GAITAME_TOT_BAP])     +   // [貿易与信合計（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_SHISHO_TOT_BAP])      +   // [支払承諾合計（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_SHIBOSAI_BAP])        +   // [私募債（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_KYOHOGASHI_BAP])      +   // [協保貸（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_IPNYSSNT_BAP])        +   // [その他一般与信（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_GENDOLOAN_TOT_BAP]);      // [限度算入ローン合計（本件後残高）]

                Honkengo[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Honkengo[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

            }



            // オンバランス合計（実勢現在残高）

//          if( Jissei[V_KEISU_KASHISHO_TOT_BAP].length()   != 0 ||

//              Jissei[V_KEISU_GAITAME_TOT_BAP].length()    != 0 ||

//              Jissei[V_KEISU_SHISHO_TOT_BAP].length()     != 0 ||

//              Jissei[V_KEISU_SHIBOSAI_BAP].length()       != 0 ||

//              Jissei[V_KEISU_KYOHOGASHI_BAP].length()     != 0 ||

//              Jissei[V_KEISU_GENDOLOAN_TOT_BAP].length()  != 0

//          ){

//              dataValue = getDataValue(Jissei[V_KEISU_KASHISHO_TOT_BAP] ) +   // [一般与信合計（実勢現在残高）]

//                          getDataValue(Jissei[V_KEISU_GAITAME_TOT_BAP])   +   // [貿易与信合計（実勢現在残高）]

//                          getDataValue(Jissei[V_KEISU_SHISHO_TOT_BAP])    +   // [支払承諾合計（実勢現在残高）]

//                          getDataValue(Jissei[V_KEISU_SHIBOSAI_BAP])      +   // [私募債（実勢現在残高）]

//                          getDataValue(Jissei[V_KEISU_KYOHOGASHI_BAP])    +   // [協保貸（実勢現在残高）]

//                          getDataValue(Jissei[V_KEISU_GENDOLOAN_TOT_BAP]);        // [限度算入ローン合計（実勢現在残高）]

//              Jissei[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

//          }else{

//              Jissei[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

//          }

            if( Jissei[V_KEISU_KASHISHO_TOT_BAP].length()   != 0 ||

                Jissei[V_KEISU_GAITAME_TOT_BAP].length()    != 0 ||

                Jissei[V_KEISU_SHISHO_TOT_BAP].length()     != 0 ||

                Jissei[V_KEISU_SHIBOSAI_BAP].length()       != 0 ||

                Jissei[V_KEISU_KYOHOGASHI_BAP].length()     != 0 ||

                Jissei[V_KEISU_IPNYSSNT_BAP].length()       != 0 ||

                Jissei[V_KEISU_GENDOLOAN_TOT_BAP].length()  != 0

            ){

                dataValue = getDataValue(Jissei[V_KEISU_KASHISHO_TOT_BAP] ) +   // [一般与信合計（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_GAITAME_TOT_BAP])   +   // [貿易与信合計（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_SHISHO_TOT_BAP])    +   // [支払承諾合計（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_SHIBOSAI_BAP])      +   // [私募債（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_KYOHOGASHI_BAP])    +   // [協保貸（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_IPNYSSNT_BAP])      +   // [その他一般与信（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_GENDOLOAN_TOT_BAP]);    // [限度算入ローン合計（実勢現在残高）]

                Jissei[V_KEISU_ONBALANCE_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Jissei[V_KEISU_ONBALANCE_TOT_BAP] = V_EMPTY_STRING;

            }

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end

// 2005.03.14   Chg End K.Sato(GEC16-C-143-005)



            /*

             * 限度算入与信合計項目

             */

            // 限度算入与信合計（指定月末残高）

            if( Getuzan[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||

                Getuzan[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Getuzan[V_KEISU_ONBALANCE_TOT_BAP]) +      // [オンバランス合計（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_OFFBALANCE_TOT_BAP]);      // [オフバランス合計（指定月末残高）]

                strGokeiGetuzan = Integer.toString(dataValue);

            }else{

                strGokeiGetuzan = V_EMPTY_STRING;

            }




            // 限度算入与信合計（極度額）

            if( Kyokudo[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||

                Kyokudo[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Kyokudo[V_KEISU_ONBALANCE_TOT_BAP]) +      // [オンバランス合計（極度額）]

                            getDataValue(Kyokudo[V_KEISU_OFFBALANCE_TOT_BAP]);      // [オフバランス合計（極度額）]

                strGokeiKyokudo = Integer.toString(dataValue);

            }else{

                strGokeiKyokudo = V_EMPTY_STRING;

            }



            // 限度算入与信合計（当月増減額）

            if( Zogen[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||

                Zogen[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Zogen[V_KEISU_ONBALANCE_TOT_BAP]) +        // [オンバランス合計（当月増減額）]

                            getDataValue(Zogen[V_KEISU_OFFBALANCE_TOT_BAP]);        // [オフバランス合計（当月増減額）]

                strGokeiZogen = Integer.toString(dataValue);

            }else{

                strGokeiZogen = V_EMPTY_STRING;

            }



            // 限度算入与信合計（本件後残高）

            if( Honkengo[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||

                Honkengo[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Honkengo[V_KEISU_ONBALANCE_TOT_BAP]) +     // [オンバランス合計（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_OFFBALANCE_TOT_BAP]);     // [オフバランス合計（本件後残高）]

                strGokeiHonkengo = Integer.toString(dataValue);

            }else{

                strGokeiHonkengo = V_EMPTY_STRING;

            }



            // 限度算入与信合計（実勢現在残高）

            if( Jissei[V_KEISU_ONBALANCE_TOT_BAP].length() != 0 ||

                Jissei[V_KEISU_OFFBALANCE_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(Jissei[V_KEISU_ONBALANCE_TOT_BAP]) +       // [オンバランス合計（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_OFFBALANCE_TOT_BAP]);       // [オフバランス合計（実勢現在残高）]

                strGokeiJissei = Integer.toString(dataValue);

            }else{

                strGokeiJissei = V_EMPTY_STRING;

            }



// 2005.02.14   Chg Start K.Sato(GEC16-C-143-005)

// 限度不算入与信合計の計算方法の変更

// 変更前：協保貸＋年金転貸＋指定L/C小切手＋L/G

// 変更後：年金転貸＋指定L/C小切手＋L/G

            /*

             * 限度不算入与信合計項目

             */

            // 限度不算入与信合計（本件後残高）

            if( Honkengo[V_KEISU_GNDFUSAN_NENKIN_BAP].length()  != 0 ||

                Honkengo[V_KEISU_GNDFUSAN_SITEILC_BAP].length() != 0 ||

                Honkengo[V_KEISU_GNDFUSAN_LG_BAP].length()      != 0

            ){

                dataValue = getDataValue(Honkengo[V_KEISU_GNDFUSAN_NENKIN_BAP])     +   // [限度不算入与信・年金転貸（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_GNDFUSAN_SITEILC_BAP])    +   // [限度不算入与信・指定Ｌ／Ｃ小切手（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_GNDFUSAN_LG_BAP]);            // [限度不算入与信・Ｌ／Ｇ（本件後残高）]

                Honkengo[V_KEISU_GNDFUSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Honkengo[V_KEISU_GNDFUSAN_TOT_BAP] = V_EMPTY_STRING;

            }


            // 限度不算入与信合計（実勢現在残高）

            if( Jissei[V_KEISU_GNDFUSAN_NENKIN_BAP].length()    != 0 ||

                Jissei[V_KEISU_GNDFUSAN_SITEILC_BAP].length()   != 0 ||

                Jissei[V_KEISU_GNDFUSAN_LG_BAP].length()        != 0

            ){

                dataValue = getDataValue(Jissei[V_KEISU_GNDFUSAN_NENKIN_BAP])   +   // [限度不算入与信・年金転貸（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_GNDFUSAN_SITEILC_BAP])  +   // [限度不算入与信・指定Ｌ／Ｃ小切手（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_GNDFUSAN_LG_BAP]);          // [限度不算入与信・Ｌ／Ｇ（実勢現在残高）]

                Jissei[V_KEISU_GNDFUSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Jissei[V_KEISU_GNDFUSAN_TOT_BAP] = V_EMPTY_STRING;

            }

// 2005.02.14   Chg End K.Sato(GEC16-C-143-005)


            /*

             * 一般与信合計項目

             */

            // 一般与信合計（指定月末残高）

            if( strGokeiGetuzan.length() != 0 ||

                Getuzan[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(strGokeiGetuzan) +     // [与信状況限度算入与信合計（指定月末残高）]

                            getDataValue(Getuzan[V_KEISU_GNDFUSAN_TOT_BAP]);        // [限度不算入与信合計（指定月末残高）]

                Getuzan[V_KEISU_IPPANYSN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Getuzan[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;

            }



// 2003/07/01 ADD@S.SEIMURA 計算式の追加(01252)

            // 一般与信合計（極度額）

            if( strGokeiKyokudo.length() != 0 ||

                Kyokudo[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(strGokeiKyokudo) +     // [与信状況限度算入与信合計（極度額）]

                            getDataValue(Kyokudo[V_KEISU_GNDFUSAN_TOT_BAP]);        // [限度不算入与信合計（極度額）]

                Kyokudo[V_KEISU_IPPANYSN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Kyokudo[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;

            }



            // 一般与信合計（当月増減額）

            if( strGokeiZogen.length() != 0 ||

                Zogen[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(strGokeiZogen) +       // [与信状況限度算入与信合計（当月増減額）]

                            getDataValue(Zogen[V_KEISU_GNDFUSAN_TOT_BAP]);          // [限度不算入与信合計（当月増減額）]

                Zogen[V_KEISU_IPPANYSN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Zogen[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;

            }



            // 一般与信合計（本件後残高）

            if( strGokeiHonkengo.length() != 0 ||

                Honkengo[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(strGokeiHonkengo) +    // [与信状況限度算入与信合計（本件後残高）]

                            getDataValue(Honkengo[V_KEISU_GNDFUSAN_TOT_BAP]);       // [限度不算入与信合計（本件後残高）]

                Honkengo[V_KEISU_IPPANYSN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Honkengo[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;

            }



            // 一般与信合計（実勢現在残高）

            if( strGokeiJissei.length() != 0 ||

                Jissei[V_KEISU_GNDFUSAN_TOT_BAP].length() != 0

            ){

                dataValue = getDataValue(strGokeiJissei) +      // [与信状況限度算入与信合計（実勢現在残高）]

                            getDataValue(Jissei[V_KEISU_GNDFUSAN_TOT_BAP]);     // [限度不算入与信合計（実勢現在残高）]

                Jissei[V_KEISU_IPPANYSN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Jissei[V_KEISU_IPPANYSN_TOT_BAP] = V_EMPTY_STRING;

            }




            /*

             * その他与信合計項目

             */

            // その他与信合計（指定月末残高）

            if( Getuzan[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||

                Getuzan[V_KEISU_SONOTA_YSN2_BAP].length() != 0

            ){

                dataValue = getDataValue(Getuzan[V_KEISU_SONOTA_YSN1_BAP]) + getDataValue(Getuzan[V_KEISU_SONOTA_YSN2_BAP]);

                Getuzan[V_KEISU_SONOTA_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Getuzan[V_KEISU_SONOTA_TOT_BAP] = V_EMPTY_STRING;

            }


            // その他与信合計（極度額）

            if( Kyokudo[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||

                Kyokudo[V_KEISU_SONOTA_YSN2_BAP].length() != 0

            ){

                dataValue = getDataValue(Kyokudo[V_KEISU_SONOTA_YSN1_BAP]) + getDataValue(Kyokudo[V_KEISU_SONOTA_YSN2_BAP]);

                Kyokudo[V_KEISU_SONOTA_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Kyokudo[V_KEISU_SONOTA_TOT_BAP] = V_EMPTY_STRING;

            }



            // その他与信合計（当月増減額）

            if( Zogen[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||

                Zogen[V_KEISU_SONOTA_YSN2_BAP].length() != 0

            ){

                dataValue = getDataValue(Zogen[V_KEISU_SONOTA_YSN1_BAP]) + getDataValue(Zogen[V_KEISU_SONOTA_YSN2_BAP]);

                Zogen[V_KEISU_SONOTA_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Zogen[V_KEISU_SONOTA_TOT_BAP] = V_EMPTY_STRING;

            }



            // その他与信合計（本件後残高）

            if( Honkengo[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||

                Honkengo[V_KEISU_SONOTA_YSN2_BAP].length() != 0

            ){

                dataValue = getDataValue(Honkengo[V_KEISU_SONOTA_YSN1_BAP]) + getDataValue(Honkengo[V_KEISU_SONOTA_YSN2_BAP]);

                Honkengo[V_KEISU_SONOTA_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Honkengo[V_KEISU_SONOTA_TOT_BAP] = V_EMPTY_STRING;

            }



            // その他与信合計（実勢現在残高）

            if( Jissei[V_KEISU_SONOTA_YSN1_BAP].length() != 0 ||

                Jissei[V_KEISU_SONOTA_YSN2_BAP].length() != 0

            ){

                dataValue = getDataValue(Jissei[V_KEISU_SONOTA_YSN1_BAP]) + getDataValue(Jissei[V_KEISU_SONOTA_YSN2_BAP]);

                Jissei[V_KEISU_SONOTA_TOT_BAP] = Integer.toString(dataValue);

            }else{

                Jissei[V_KEISU_SONOTA_TOT_BAP] = V_EMPTY_STRING;

            }


        /*-------------------------------------------------------------------------

        ここまでが合計を含めた差分計算

        --------------------------------------------------------------------------*/



            /*

             * ここから、ＤＢのデータと差分データを足したものを作成する

             */

            String[] strArr1 = new String[int1];

            String[] strArr2 = new String[int1];

            String[] strArr3 = new String[int1];

            String[] strArr4 = new String[int1];

            String[] strArr5 = new String[int1];

            String[] strWorkArr = new String[int1];


            /*

             * 配列になっている限度算入与信合計項目

             */


            // 限度算入与信合計・月末残高

            strWorkArr = (String[])db.get(F_MEND_ZAN_TOT);

            if( strWorkArr[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||

                strGokeiGetuzan.length() != 0

            ){

                dataValue = getDataValue(strWorkArr[V_KEISU_GENDOSAN_TOT_BAP]) +

                            getDataValue(strGokeiGetuzan);

                strArr1[V_KEISU_GENDOSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                strArr1[V_KEISU_GENDOSAN_TOT_BAP] = V_EMPTY_STRING;

            }

            hstTbl.put(F_MEND_ZAN_TOT, strArr1);




            // 限度算入与信合計・極度額

            strWorkArr = (String[])db.get(F_LMT_TOT);

            if( strWorkArr[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||

                strGokeiKyokudo.length() != 0

            ){

                dataValue = getDataValue(strWorkArr[V_KEISU_GENDOSAN_TOT_BAP]) +

                            getDataValue(strGokeiKyokudo);

                strArr2[V_KEISU_GENDOSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                strArr2[V_KEISU_GENDOSAN_TOT_BAP] = V_EMPTY_STRING;

            }

            hstTbl.put(F_LMT_TOT, strArr2);



            // 限度算入与信合計・当月増減

            strWorkArr = (String[])db.get(F_IPNYSNDLTZGG_TOT);

            if( strWorkArr[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||

                strGokeiZogen.length() != 0

            ){

                dataValue = getDataValue(strWorkArr[V_KEISU_GENDOSAN_TOT_BAP]) +

                            getDataValue(strGokeiZogen);

                strArr3[V_KEISU_GENDOSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                strArr3[V_KEISU_GENDOSAN_TOT_BAP] = V_EMPTY_STRING;

            }

            hstTbl.put(F_IPNYSNDLTZGG_TOT, strArr3);



            // 限度算入与信合計・本件後残高

            strWorkArr = (String[])db.get(F_HONAF_ZAN_TOT);

            if( strWorkArr[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||

                strGokeiHonkengo.length() != 0

            ){

                dataValue = getDataValue(strWorkArr[V_KEISU_GENDOSAN_TOT_BAP]) +

                            getDataValue(strGokeiHonkengo);

                strArr4[V_KEISU_GENDOSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                strArr4[V_KEISU_GENDOSAN_TOT_BAP] = V_EMPTY_STRING;

            }

            hstTbl.put(F_HONAF_ZAN_TOT, strArr4);




            // 限度算入与信合計・実勢現在残

            strWorkArr = (String[])db.get(F_JISKSN_TOT);

            if( strWorkArr[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||

                strGokeiJissei.length() != 0

            ){

                dataValue = getDataValue(strWorkArr[V_KEISU_GENDOSAN_TOT_BAP]) +

                            getDataValue(strGokeiJissei);

                strArr5[V_KEISU_GENDOSAN_TOT_BAP] = Integer.toString(dataValue);

            }else{

                strArr5[V_KEISU_GENDOSAN_TOT_BAP] = V_EMPTY_STRING;

            }

            hstTbl.put(F_JISKSN_TOT, strArr5);




            /*

             * 配列になっている項目

             */



            for(int j = 0; j < V_KEISU_IPNYSN_ARR_NUM; j++) {


                if( j <= V_KEISU_GNDFUSAN_TOT_BAP || V_KEISU_IPPANYSN_TOT_BAP <= j ) {


                    // 月末残高

                    if( Getuzan[j].length() != 0 ||

                        dbGetuzan[j].length() != 0

                    ){

                        dataValue = getDataValue(Getuzan[j]) + getDataValue(dbGetuzan[j]);

                        dbGetuzan[j] = Integer.toString(dataValue);

                    }else{

                        dbGetuzan[j] = V_EMPTY_STRING;

                    }


                    // 極度額

                    if( Kyokudo[j].length() != 0 ||

                        dbKyokudo[j].length() != 0

                    ){

                        dataValue = getDataValue(Kyokudo[j]) + getDataValue(dbKyokudo[j]);

                        dbKyokudo[j] = Integer.toString(dataValue);

                    }else{

                        dbKyokudo[j] = V_EMPTY_STRING;

                    }



                    // 当月増減

                    if( Zogen[j].length() != 0 ||

                        dbZogen[j].length() != 0

                    ){

                        dataValue = getDataValue(Zogen[j]) + getDataValue(dbZogen[j]);

                        dbZogen[j] = Integer.toString(dataValue);

                    }else{

                        dbZogen[j] = V_EMPTY_STRING;

                    }

                }



                // 本件後残高

                if( Honkengo[j].length() != 0 ||

                    dbHonkengo[j].length() != 0

                ){

                    dataValue = getDataValue(Honkengo[j]) + getDataValue(dbHonkengo[j]);

                    dbHonkengo[j] = Integer.toString(dataValue);

                }else{

                    dbHonkengo[j] = V_EMPTY_STRING;

                }



                // 実勢現在残

                if( Jissei[j].length() != 0 ||

                    dbJissei[j].length() != 0

                ){

                    dataValue = getDataValue(Jissei[j]) + getDataValue(dbJissei[j]);

                    dbJissei[j] = Integer.toString(dataValue);

                }else{

                    dbJissei[j] = V_EMPTY_STRING;

                }

            }


            //

            // dbDataに一般与信データをput

            //



            //与信状況・指定月末残高

            hstTbl.put(F_MEND_ZAN, dbGetuzan);


            //与信状況・極度額

            hstTbl.put(F_LMT, dbKyokudo);


            //与信状況・当月増減額

            hstTbl.put(F_IPNYSNDLTZGG, dbZogen);


            //与信状況・本件後残高

            hstTbl.put(F_HONAF_ZAN, dbHonkengo);


            //与信状況・実勢現在残

            hstTbl.put(F_JISKSN, dbJissei);


// 2009/06/23 DEL@R.Matsumura GEC20-C-059 start


// 本件後保全状況を差分計算に変更したことにより、

// 本件後保全状況の計算においてもDBデータが必要なので上書き処理を削除

            //hstComBasketにdbDataをputする

//          hstComBasket.put(K_DB_DATA, hstTbl);

// 2009/06/23 DEL@R.Matsumura GEC20-C-059 end



        }finally{

        }



    }



    /**

     *　 <DL>

     *   <DT><b>メソッド概要:</b><DD>

     *   計数で初期表示、計数再取得ボタン、または計算ボタンが押された時に、

     *   一般与信以外の項目のデータ計算を行う。<BR>

     *   </DD></DT>

     *   </DL>

     *   <BR>

     *   @param  Hashtable  hstComBasket    共有情報

     */

    public void computeKokyaku( Hashtable hstComBasket ) {



        Hashtable dbData = (Hashtable)hstComBasket.get( K_DB_DATA ) ;



        String[] strGokeiKitei = (String[])dbData.get( F_HIKIATE_KITEITI_TOT ) ;

        String[] strGokeiJika  = (String[])dbData.get( F_HIKIATE_JIKA_TOT    ) ;

        String[] strKitei      = (String[])dbData.get( F_HIKIATE_KITEITI     ) ;

        String[] strJika       = (String[])dbData.get( F_HIKIATE_JIKA        ) ;

//2009/06/23 ADD@R.Matsumura GEC20-C-059 start

        // 裸与信対象与信合計を取得

        String   strStrcreTshoTot  = (String)dbData.get( F_STRCRE_TSHO_TOT   ) ;

//2009/06/23 ADD@R.Matsumura GEC20-C-059 end


        int dataValue  = 0 ;

        int workValue1 = 0 ;

        int workValue2 = 0 ;

        int workValue3 = 0 ;

        double riritu = 0.0 ;

        double workRiritu1 = 0.0 ;

        double workRiritu2 = 0.0 ;

        String doubleData1 = null ;

        String doubleData2 = null ;


        int allGetuzan    = 0 ;

        int allKyokudo    = 0 ;

        int allZougen     = 0 ;

        int allHonkengo   = 0 ;

        int allJissei    = 0 ;

        int allJissei2   = 0 ;

        int allSouteiSnin = 0 ;

        int allSouteiZan  = 0 ;




// 2003/04/08 CHG@S.SEIMURA 引当状況計算項目をlong型で計算を行うよう修正

//                          getDataValue() → getDataValue2()使用

        long dataValue2 = 0 ;

        /*

         * 規定項目

         */

// 2005.02.14   Chg Start K.Sato(GEC16-C-143-005)

/*

* 規定・優良小計の計算式変更

* 変更前：

* 規定・優良・預金＋規定・優良・商手＋規定・優良・担手＋規定・優良・有証＋

* 規定・優良・保証＋規定・優良・一括支払＋規定・優良・その他

* 変更後：

* 規定・優良・預金＋規定・優良・商手＋規定・優良・担手＋規定・優良・有証＋

* 規定・優良・協会保証＋規定・優良・保証（除協会）＋規定・優良・一般Ｌ／Ｃ＋

* 規定・優良・手形保険＋規定・優良・一括支払＋規定・優良・その他

*/

        // 規定・優良のリストを生成

        int[] intIndexListKiteiYuryo = {V_KEISU_KTI_YUTNP_YOKIN_BAP, V_KEISU_KTI_YUTNP_SYOTE_BAP, V_KEISU_KTI_YUTNP_TANTE_BAP, V_KEISU_KTI_YUTNP_YUSYO_BAP, V_KEISU_KTI_YUTNP_KYOHO_BAP, V_KEISU_KTI_YUTNP_HOSYO_BAP, V_KEISU_KTI_YUTNP_IPANLC_BAP, V_KEISU_KTI_YUTNP_TEGATAHO_BAP, V_KEISU_KTI_YUTNP_IKKATU_BAP, V_KEISU_KTI_YUTNP_SONOTA_BAP};


        // 規定・優良小計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_YUTNP_YOKIN_BAP] )     +   // [規定・優良・預金（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] )     +   // [規定・優良・商手（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_TANTE_BAP] )     +   // [規定・優良・担手（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_YUSYO_BAP] )     +   // [規定・優良・有証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_KYOHO_BAP] )     +   // [規定・優良・協会保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_HOSYO_BAP] )     +   // [規定・優良・保証（除協会）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_IPANLC_BAP] )    +   // [規定・優良・一般L/C（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_TEGATAHO_BAP] )  +   // [規定・優良・手形保険（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_IKKATU_BAP] )    +   // [規定・優良・一括支払（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_YUTNP_SONOTA_BAP] ) ;      // [規定・優良・その他（規定値）]


        // BAPから取得した全ての値が""の時、合計値を""にする

        strKitei[V_KEISU_KTI_YUTNP_STOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiYuryo, dataValue2 );


        // 規定・優良小計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTI_YUTNP_YOKIN_BAP] )      +   // [規定・優良・預金（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_SYOTE_BAP] )      +   // [規定・優良・商手（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_TANTE_BAP] )      +   // [規定・優良・担手（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_YUSYO_BAP] )      +   // [規定・優良・有証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_KYOHO_BAP] )      +   // [規定・優良・協会保証（規定値）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_HOSYO_BAP] )      +   // [規定・優良・保証（除協会）（規定値）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_IPANLC_BAP] )     +   // [規定・優良・一般L/C（規定値）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_TEGATAHO_BAP] )   +   // [規定・優良・手形保険（規定値）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_IKKATU_BAP] )     +   // [規定・優良・一括支払（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_YUTNP_SONOTA_BAP] ) ;       // [規定・優良・その他（時価ベース）]

        strJika[V_KEISU_KTI_YUTNP_STOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiYuryo, dataValue2 );

// 2005.02.14   Chg End K.Sato(GEC16-C-143-005)



/* YC20218-02 Start */

        // 規定・一般・不動産（抵）のリストを生成

        int[] intIndexListKiteiIppanFudoTei = {V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP, V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP};


        // 規定・一般・不動産（抵）（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] ) +      // [規定・一般・不動産（抵）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP] ) ;  // [規定･一般担保･内HL(抵)（規定値）]

        strKitei[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiIppanFudoTei, dataValue2 );


        // 規定・一般・不動産（抵）（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] ) +       // [規定・一般・不動産（抵）（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP] ) ;   // [規定･一般担保･内HL(抵)（時価ベース）]

        strJika[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiIppanFudoTei, dataValue2 );

/* YC20218-02 End */



// 2005.02.14   Chg Start K.Sato(GEC16-C-143-005)

/*

* 規定・一般小計の計算式変更

* 変更前：

* 規定・一般・有証＋規定・一般・保証＋規定・一般・不動産（抵）＋規定・一般・不動産（根）＋

* 規定・一般・一般Ｌ／Ｃ＋規定・一般・手形保険\＋[規定・一般・Ｄ／Ｆ保証（規定値）]＋[規定・一般・その他

* 変更後：

* 規定・一般・有証＋規定・一般・保証＋規定・一般・不動産（抵）＋規定・一般・不動産（根）＋

* 一般・Ｄ／Ｆ保証＋規定・一般・その他

*/

        // 規定・一般のリストを生成

        int[] intIndexListKiteiIppan = {V_KEISU_KTI_IPNTNP_YUSYO_BAP, V_KEISU_KTI_IPNTNP_HOSYO_BAP, V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP, V_KEISU_KTI_IPNTNP_FUDO_NE_BAP, V_KEISU_KTI_IPNTNP_DFHOSYO_BAP, V_KEISU_KTI_IPNTNP_SONOTA_BAP};


        // 規定・一般小計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_YUSYO_BAP]  ) +     // [規定・一般・有証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_HOSYO_BAP] ) +      // [規定・一般・保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] ) +       // [規定・一般・不動産（抵）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP] ) +        // [規定・一般・不動産（根）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP] ) +        // [規定・一般・Ｄ／Ｆ保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_SONOTA_BAP] ) ;         // [規定・一般・その他（規定値）]

        strKitei[V_KEISU_KTI_IPNTNP_STOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiIppan, dataValue2 );



        // 規定・一般小計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTI_IPNTNP_YUSYO_BAP] ) +       // [規定・一般・有証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_HOSYO_BAP] ) +       // [規定・一般・保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] ) +        // [規定・一般・不動産（抵）（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP] ) +         // [規定・その他小計（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP] ) +         // [規定・一般・Ｄ／Ｆ保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_SONOTA_BAP] ) ;      // [規定・一般・その他（時価ベース）]

        strJika[V_KEISU_KTI_IPNTNP_STOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiIppan, dataValue2 );

// 2005.02.14   Chg End.Sato(GEC16-C-143-005)




        // 規定・その他のリストを生成

        int[] intIndexListKiteiSonota = {V_KEISU_KTI_SNTTNP_YUSYO_BAP, V_KEISU_KTI_SNTTNP_HOSYO_BAP, V_KEISU_KTI_SNTTNP_DHCDC_BAP, V_KEISU_KTI_SNTTNP_SONOTA_BAP};


        // 規定・その他小計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_YUSYO_BAP] ) +      // [規定・その他・有証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_HOSYO_BAP] ) +      // [規定・その他・保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_DHCDC_BAP] ) +      // [規定・その他・ＤＨＣ・ＤＣ保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_SONOTA_BAP] ) ;     // [規定・その他・その他（規定値）]

        strKitei[V_KEISU_KTI_SNTTNP_STOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiSonota, dataValue2 );



        // 規定・その他小計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTI_SNTTNP_YUSYO_BAP] ) +       // [規定・その他・有証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_SNTTNP_HOSYO_BAP] ) +       // [規定・その他・保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_SNTTNP_DHCDC_BAP] ) +       // [規定・その他・ＤＨＣ・ＤＣ保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_SNTTNP_SONOTA_BAP]) ;       // [規定・その他・その他（時価ベース）]

        strJika[V_KEISU_KTI_SNTTNP_STOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiSonota, dataValue2 );



        // 規定担保合計のリストを生成

        int[] intIndexListKiteiGoukei = {V_KEISU_KTI_YUTNP_STOT_BAP, V_KEISU_KTI_IPNTNP_STOT_BAP, V_KEISU_KTI_SNTTNP_STOT_BAP};


        // 規定担保合計（規定値）

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start

// 規定担保合計（規定値）を補正値を使用した計算に変更

//      dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_YUTNP_STOT_BAP] ) +        // [規定・優良小計（規定値）]

//                   getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_STOT_BAP] ) +       // [規定・一般小計（規定値）]

//                   getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_STOT_BAP] ) ;       // [規定・その他小計（規定値）]


        dataValue2 = getDataValue2( strKitei[V_KEISU_KTI_YUTNP_STOT_BAP]    ) +     // [規定・優良小計（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_STOT_BAP]   ) +     // [規定・一般小計（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTI_SNTTNP_STOT_BAP]   ) -     // [規定・その他小計（規定値）]

                     getDataValue2( strGokeiKitei[V_KEISU_KTITNP_HOSCH_BAP] );      // [規定担保補正値（規定値）]



        // 結果が０以下の場合は０を設定

        if( dataValue2 <= 0 ) {

                dataValue2 = 0;

        }

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end

        strGokeiKitei[V_KEISU_KTITNP_TOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiGoukei, dataValue2 );


        // 規定担保合計（時価ベース）

/*

* 2007.01.16 Mod  M.Kawano(GEC18-C-043)

* 優良小計の参照に使用する定数相違の修正

*/

//      dataValue2 = getDataValue2( strJika[V_KEISU_KTITNP_TOT_BAP] ) +     // [規定・優良小計（時価ベース）]

//                   getDataValue2( strJika[V_KEISU_KTI_IPNTNP_STOT_BAP] ) +        // [規定・一般小計（時価ベース）]

//                   getDataValue2( strJika[V_KEISU_KTI_SNTTNP_STOT_BAP] ) ;        // [規定・その他小計（時価ベース）]

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start

// 規定担保合計（時価ベース）を補正値を使用した計算に変更

//      dataValue2 = getDataValue2( strJika[V_KEISU_KTI_YUTNP_STOT_BAP] ) +         // [規定・優良小計（時価ベース）]

//                   getDataValue2( strJika[V_KEISU_KTI_IPNTNP_STOT_BAP] ) +        // [規定・一般小計（時価ベース）]

//                   getDataValue2( strJika[V_KEISU_KTI_SNTTNP_STOT_BAP] ) ;        // [規定・その他小計（時価ベース）]

        dataValue2 = getDataValue2( strJika[V_KEISU_KTI_YUTNP_STOT_BAP] ) +         // [規定・優良小計（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_IPNTNP_STOT_BAP] ) +        // [規定・一般小計（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTI_SNTTNP_STOT_BAP] ) -        // [規定・その他小計（時価ベース）]

                     getDataValue2( strGokeiJika[V_KEISU_KTITNP_HOSCH_BAP] );       // [規定担保補正値（時価ベース）]


        // 結果が０以下の場合は０を設定

        if( dataValue2 <= 0 ) {

                dataValue2 = 0;

        }

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end

// 2007.01.15 Mod End  M.Kawano(GEC18-C-043)

        strGokeiJika[V_KEISU_KTITNP_TOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiGoukei, dataValue2 );


        /*

         * 規定外項目

         */

        // 規定外・優良のリストを生成

        int[] intIndexListKiteiGaiYuryou = {V_KEISU_KTIG_YUTNP_YOKIN_BAP, V_KEISU_KTIG_YUTNP_YUSYO_BAP, V_KEISU_KTIG_YUTNP_HOSYO_BAP, V_KEISU_KTIG_YUTNP_SONOTA_BAP};


        // 規定外・優良小計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTIG_YUTNP_YOKIN_BAP] ) +      // [規定外・優良・預金（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_YUTNP_YUSYO_BAP] ) +      // [規定外・優良・有証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_YUTNP_HOSYO_BAP] ) +      // [規定外・優良・保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_YUTNP_SONOTA_BAP] ) ;         // [規定外・優良・その他（規定値）]

        strKitei[V_KEISU_KTIG_YUTNP_STOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiGaiYuryou, dataValue2 );


        // 規定外・優良小計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTIG_YUTNP_YOKIN_BAP] ) +       // [規定外・優良・預金（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_YUTNP_YUSYO_BAP] ) +       // [規定外・優良・有証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_YUTNP_HOSYO_BAP] ) +       // [規定外・優良・保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_YUTNP_SONOTA_BAP] ) ;      // [規定外・優良・その他（時価ベース）]

        strJika[V_KEISU_KTIG_YUTNP_STOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiGaiYuryou, dataValue2 );



        // 規定外・優良のリストを生成

        int[] intIndexListKiteiGaiIppan = {V_KEISU_KTIG_IPNTNP_YUSYO_BAP, V_KEISU_KTIG_IPNTNP_HOSYO_BAP, V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP, V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP, V_KEISU_KTIG_IPNTNP_NYUKYO_BAP, V_KEISU_KTIG_IPNTNP_SAIKEN_BAP, V_KEISU_KTIG_IPNTNP_SONOTA_BAP};


        // 規定外・一般小計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_YUSYO_BAP] ) +         // [規定外・一般・有証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_HOSYO_BAP] ) +         // [規定外・一般・保証（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP] ) +      // [規定外・一般・不動産（抵）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP] ) +       // [規定外・一般・不動産（根）（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP] ) +        // [規定外・一般・入居保証金（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP] ) +        // [規定外・一般・債券（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_SONOTA_BAP] ) ;        // [規定外・一般・その他（規定値）]

        strKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiGaiIppan, dataValue2 );


        // 規定外・一般小計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_YUSYO_BAP] ) +      // [規定外・一般・有証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_HOSYO_BAP] ) +      // [規定外・一般・保証（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP] ) +       // [規定外・一般・不動産（抵）（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP] ) +        // [規定外・一般・不動産（根）（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP] ) +         // [規定外・一般・入居保証金（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP] ) +         // [規定外・一般・債券（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_SONOTA_BAP] ) ;         // [規定外・一般・その他（時価ベース）]

        strJika[V_KEISU_KTIG_IPNTNP_STOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiGaiIppan, dataValue2 );



        // 規定外担保合計のリストを生成

        int[] intIndexListKiteiGaiGoukei = {V_KEISU_KTIG_YUTNP_STOT_BAP, V_KEISU_KTIG_IPNTNP_STOT_BAP, V_KEISU_KTIG_SONOTA_BAP};


        // 規定外担保合計（規定値）

        dataValue2 = getDataValue2( strKitei[V_KEISU_KTIG_YUTNP_STOT_BAP] ) +       // [規定外・優良小計（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP] ) +      // [規定外・一般小計（規定値）]

                     getDataValue2( strKitei[V_KEISU_KTIG_SONOTA_BAP]) ;        // [規定外・その他（規定値）]

        strKitei[V_KEISU_KTIG_TOT_BAP] = getOutHonkengoValue( strKitei, intIndexListKiteiGaiGoukei, dataValue2 );


        // 規定外担保合計（時価ベース）

        dataValue2 = getDataValue2( strJika[V_KEISU_KTIG_YUTNP_STOT_BAP] ) +        // [規定外・優良小計（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_IPNTNP_STOT_BAP] ) +       // [規定外・一般小計（時価ベース）]

                     getDataValue2( strJika[V_KEISU_KTIG_SONOTA_BAP] ) ;        // [規定外・その他（時価ベース）]

        strJika[V_KEISU_KTIG_TOT_BAP] = getOutHonkengoValue( strJika, intIndexListKiteiGaiGoukei, dataValue2 );




        String[] strYosinTot = (String[])dbData.get(F_HONAF_ZAN_TOT);
        String[] strYosin = (String[])dbData.get(F_HONAF_ZAN);
        dataValue2 = getDataValue2( strYosinTot[V_KEISU_GENDOSAN_TOT_BAP] ) -            // [限度算入与信合計（本件後残高）]
                     getDataValue2( strStrcreTshoTot ) -                                 // [裸与信対象与信合計]
                     getDataValue2( strGokeiKitei[V_KEISU_KTITNP_TOT_BAP] ) -            // [規定担保合計（規定値）]
                   ( getDataValue2( strYosin[V_KEISU_HLSHINYOFUSANNYU_BAP] ) -           // [内HL信用不算入（本件後残高）]
                     getDataValue2( strKitei[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP] ) ) ;  // [規定･一般担保･内HL(抵)（規定値）]
        String[] strHadakaYosin = {    strYosinTot[V_KEISU_GENDOSAN_TOT_BAP],
                                       strStrcreTshoTot,
                                    strGokeiKitei[V_KEISU_KTITNP_TOT_BAP],
                                    strYosin[V_KEISU_HLSHINYOFUSANNYU_BAP],
                                    strKitei[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP]
                                    };
        // 裸与信の合計値がマイナス値の場合
        if ( dataValue2 < 0 ) {
            dataValue2 = 0 + getDataValue2( strStrcreTshoTot );
        // 裸与信の合計値がプラス値の場合
        }else{
            dataValue2 = dataValue2 + getDataValue2( strStrcreTshoTot );
        }
/* YC20218-02 End */
//2009/06/23 CHG@R.Matsumura GEC20-C-059 end
        strGokeiKitei[V_KEISU_STRCRE_BAP] = getOutHonkengoValue(strHadakaYosin, dataValue2);

        dbData.put( F_HIKIATE_KITEITI_TOT, strGokeiKitei ) ;
        dbData.put( F_HIKIATE_JIKA_TOT,    strGokeiJika  ) ;
        dbData.put( F_HIKIATE_KITEITI,     strKitei      ) ;
        dbData.put( F_HIKIATE_JIKA,        strJika       ) ;



        // 結果データを設定
        hstComBasket.put( K_DB_DATA, dbData ) ;


        return ;

    }


    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数画面で計算ボタンを押された時のみに、
     *   一般与信以外の項目のデータ計算を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable  hstComBasket    共有情報
     */

    public void computeKokyakuKeisan( Hashtable hstComBasket ) {

        Hashtable dbData = (Hashtable)hstComBasket.get( K_DB_DATA ) ;

        int dataValue  = 0 ;
        int workValue1 = 0 ;
        int workValue2 = 0 ;
        double riritu = 0.0 ;
        double workRiritu1 = 0.0 ;
        double workRiritu2 = 0.0 ;
        String doubleData1 = null ;
        String doubleData2 = null ;

        int allGetuzan    = 0 ;
        int allKyokudo    = 0 ;
        int allHonkengo   = 0 ;
        int allJissei     = 0 ;
        int allJissei2    = 0 ;

        String[] strGetuzan    = new String[10];
        String[] strKyokudo    = new String[10];
        String[] strHonkengo   = new String[10];
        String[] strJissei     = new String[10];
        String[] strJissei2    = new String[10];

        /*
         * 中間決算項目
         */
        DecimalFormat df = new DecimalFormat( "#0.00" );

        // 中間決算（平均月商）
        doubleData1 = (String)getData(dbData, F_URIAGE4) ;
        if( doubleData1.length() != 0 ) {
            riritu = new Double(doubleData1).doubleValue() / double6 ;          // [中間決算（純売上高）]
            dataValue = (int)Math.round( riritu ) ;
            addHash( dbData,  F_URIAGEGESSHO4, dataValue ) ;

        // doubleの数値文字列長が０、すなわち数値変換できない時
        } else {
            dbData.put( F_URIAGEGESSHO4, new String(V_EMPTY_STRING) ) ;
        }

        // 中間決算（経常利益率）
        doubleData1 = (String)getData(dbData, F_KEIJOEKI4) ;
        doubleData2 = (String)getData(dbData, F_URIAGE4  ) ;
        // 経常利益、純売上高のデータが存在する
        if( doubleData1.length() != 0 &&
            doubleData2.length() != 0 ) {

            workRiritu1 = new Double( doubleData1 ).doubleValue() ; // [中間決算（経常利益）]
            workRiritu2 = new Double( doubleData2 ).doubleValue() ; // [中間決算（純売上高）]
            riritu = ( workRiritu2 == 0 ) ?
                double0 : ( workRiritu1 / workRiritu2 ) ;

            // 下３桁目を四捨五入する
            riritu *= double10000 ;
            riritu = Math.round( riritu ) / double100 ;
            dbData.put( F_KEIJOEKI_RIT4, df.format( riritu ) ) ;

        // doubleの数値文字列長が０、すなわち数値変換できない時
        } else {
            dbData.put( F_KEIJOEKI_RIT4, new String(V_EMPTY_STRING) ) ;
        }

        // 中間決算（当期利益率）
        doubleData1 = (String)getData(dbData, F_TOKIEKI4) ;
        doubleData2 = (String)getData(dbData, F_URIAGE4 ) ;

        // 当期利益、純売上高のデータが存在する
        if( doubleData1.length() != 0 &&
            doubleData2.length() != 0 ) {

            workRiritu1 = new Double( doubleData1 ).doubleValue() ; // [中間決算（当期利益）]
            workRiritu2 = new Double( doubleData2 ).doubleValue() ; // [中間決算（純売上高）]
            riritu = ( workRiritu2 == 0 ) ?
            double0 : ( workRiritu1 / workRiritu2 ) ;

            // 下３桁目を四捨五入する
            riritu *= double10000 ;
            riritu = Math.round( riritu ) / double100 ;
            dbData.put( F_TOKIEKI_RIT4, df.format( riritu ) ) ;

        // doubleの数値文字列長が０、すなわち数値変換できない時
        } else {
            dbData.put( F_TOKIEKI_RIT4, new String(V_EMPTY_STRING) ) ;

        }

        /*
         * 決算予想項目
         */
        // 決算予想（平均月商）
        doubleData1 = (String)getData(dbData, F_URIAGE5) ;
        if( doubleData1.length() != 0 ) {
                riritu = new Double(doubleData1).doubleValue() / double12 ; // [決算予想（純売上高）]
                dataValue = (int)Math.round( riritu ) ;
                addHash( dbData,  F_URIAGEGESSHO5, dataValue ) ;
        } else {
            dbData.put( F_URIAGEGESSHO5, new String(V_EMPTY_STRING) ) ;
        }

        // 決算予想（経常利益率）
        doubleData1 = (String)getData(dbData, F_KEIJOEKI5) ;
        doubleData2 = (String)getData(dbData, F_URIAGE5  ) ;

        // 経常利益、純売上高のデータが存在する
        if( doubleData1.length() != 0 &&
            doubleData2.length() != 0 ) {
            workRiritu1 = new Double( doubleData1 ).doubleValue() ; // [決算予想（経常利益）]
            workRiritu2 = new Double( doubleData2 ).doubleValue() ; // [決算予想（純売上高）]
            riritu = ( workRiritu2 == 0 ) ?
                double0 : ( workRiritu1 / workRiritu2 ) ;

            // 下３桁目を四捨五入する
            riritu *= double10000 ;
            riritu = Math.round( riritu ) / double100 ;
            dbData.put( F_KEIJOEKI_RIT5, df.format( riritu ) ) ;

        } else {
            dbData.put( F_KEIJOEKI_RIT5, new String(V_EMPTY_STRING) ) ;
        }

        // 決算予想（当期利益率）
        doubleData1 = (String)getData(dbData, F_TOKIEKI5) ;
        doubleData2 = (String)getData(dbData, F_URIAGE5  ) ;
        if( doubleData1.length() != 0 &&
            doubleData2.length() != 0 ) {
                workRiritu1 = new Double( doubleData1 ).doubleValue() ; // [決算予想（当期利益）]
            workRiritu2 = new Double( doubleData2 ).doubleValue() ; // [決算予想（純売上高）]
            riritu = ( workRiritu2 == 0 ) ?
                double0 : ( workRiritu1 / workRiritu2 ) ;

            // 下３桁目を四捨五入する
            riritu *= double10000 ;
            riritu = Math.round( riritu ) / double100 ;
            dbData.put( F_TOKIEKI_RIT5, df.format( riritu ) ) ;

        } else {
            dbData.put( F_TOKIEKI_RIT5, new String(V_EMPTY_STRING) ) ;
        }


        /* --------------------------------------------------------
         * 市場性与信の項目
         * --------------------------------------------------------
         */
        for(int i = 0; i < 10; i++) {

            // 指定月末残高
            String sijoGetuzanL[] = {
                        F_MEND_ZAN_1,   F_MEND_ZAN_2,   F_MEND_ZAN_3,
                        F_MEND_ZAN_4,   F_MEND_ZAN_5,   F_MEND_ZAN_6,
                        F_MEND_ZAN_7,   F_MEND_ZAN_8,   F_MEND_ZAN_9,
                        F_MEND_ZAN_10
                        } ;
            String sijoGetuzanV = (String)getData( dbData,  sijoGetuzanL[i] ) ;
            strGetuzan[i] = (String)getData( dbData,  sijoGetuzanL[i] ) ;

            // 指定月末極度額
            String sijoKyokudoL[] = {
                        F_LMT_1,        F_LMT_2,        F_LMT_3,
                        F_LMT_4,        F_LMT_5,        F_LMT_6,
                        F_LMT_7,        F_LMT_8,        F_LMT_9,
                        F_LMT_10
                        } ;
            String sijoKyokudoV = (String)getData( dbData,  sijoKyokudoL[i] ) ;
            strKyokudo[i] = (String)getData( dbData,  sijoKyokudoL[i] ) ;

            // 当月増減額 の合計値は計算を行わない

            // 本件後与信額
            String sijoHonkengoL[] = {
                        F_HONAF_ZAN_1,  F_HONAF_ZAN_2,  F_HONAF_ZAN_3,
                        F_HONAF_ZAN_4,  F_HONAF_ZAN_5,  F_HONAF_ZAN_6,
                        F_HONAF_ZAN_7,  F_HONAF_ZAN_8,  F_HONAF_ZAN_9,
                        F_HONAF_ZAN_10
                        } ;
            String sijoHonkengoV = (String)getData( dbData,  sijoHonkengoL[i] ) ;
            strHonkengo[i] = (String)getData( dbData,  sijoHonkengoL[i] ) ;

            // 実勢現在残1
            String sijoJisseiL[] = {
                        F_CEPERN_JITU_ZAN1_1,   F_CEPERN_JITU_ZAN1_2,
                        F_CEPERN_JITU_ZAN1_3,   F_CEPERN_JITU_ZAN1_4,
                        F_CEPERN_JITU_ZAN1_5,   F_CEPERN_JITU_ZAN1_6,
                        F_CEPERN_JITU_ZAN1_7,   F_CEPERN_JITU_ZAN1_8,
                        F_CEPERN_JITU_ZAN1_9,   F_CEPERN_JITU_ZAN1_10
                        } ;
            String sijoJisseiV = (String)getData( dbData,  sijoJisseiL[i] ) ;
            strJissei[i] = (String)getData( dbData,  sijoJisseiL[i] ) ;

            // 実勢現在残2
            String sijoJissei2L[] = {
                        F_CERN_JITU_ZAN1_1,     F_CERN_JITU_ZAN1_2,
                        F_CERN_JITU_ZAN1_3,     F_CERN_JITU_ZAN1_4,
                        F_CERN_JITU_ZAN1_5,     F_CERN_JITU_ZAN1_6,
                        F_CERN_JITU_ZAN1_7,     F_CERN_JITU_ZAN1_8,
                        F_CERN_JITU_ZAN1_9,     F_CERN_JITU_ZAN1_10
                        } ;
            String sijoJissei2V = (String)getData( dbData,  sijoJissei2L[i] ) ;
            strJissei2[i] = (String)getData( dbData,  sijoJissei2L[i] ) ;


            // 各リストデータの足しこみ
            allGetuzan    += getDataValue( sijoGetuzanV    ) ;
            allKyokudo    += getDataValue( sijoKyokudoV    ) ;
            allHonkengo   += getDataValue( sijoHonkengoV   ) ;
            allJissei     += getDataValue( sijoJisseiV     ) ;
            allJissei2    += getDataValue( sijoJissei2V    ) ;


            // 各リストデータの足しこみが終了時
            if( i == 9 ) {
                // 各リストデータの登録
                dbData.put( F_LMTINTL_RN_MEND_ZAN      ,getOutShijoValue( strGetuzan    ,allGetuzan    )) ;
                dbData.put( F_LMTINTL_RN_LMT           ,getOutShijoValue( strKyokudo    ,allKyokudo    )) ;
                dbData.put( F_LMTINTL_RN_HONAF_ZAN     ,getOutShijoValue( strHonkengo   ,allHonkengo   )) ;
                dbData.put( F_LMTINTL_RN_CEPERN_JI     ,getOutShijoValue( strJissei     ,allJissei     )) ;
                dbData.put( F_LMTINTL_RN_CERN_JITU     ,getOutShijoValue( strJissei2    ,allJissei2    )) ;
            }
        }


        /*
         * 市場性与信合計項目
         */
        // 市場性与信合計（指定月末残高）
        dbData.put( F_SIJOYSNRN_MEND_ZAN,
                 getData( dbData, F_LMTINTL_RN_MEND_ZAN ) ) ;   // [限度算入与信合計（指定月末残高）]
        // 市場性与信合計（指定月末極度額）
        dbData.put( F_SIJOYSNRN_LMT,
                 getData( dbData, F_LMTINTL_RN_LMT ) ) ;        // [限度算入与信合計（指定月末極度額）]
        // 市場性与信合計（本件後与信額）
        dbData.put( F_SIJOYSNRN_HONAF_ZAN,
                 getData( dbData, F_LMTINTL_RN_HONAF_ZAN ) ) ;  // [限度算入与信合計（本件後与信額）]
        // 市場性与信合計（実勢現在残１）
        dbData.put( F_SIJOYSNRN_CEPERN_JITU_ZAN1,
                 getData( dbData, F_LMTINTL_RN_CEPERN_JI ) ) ;  // [限度算入与信合計（実勢現在残１）]

        // 市場性与信合計（実勢現在残２）
        dbData.put( F_SIJOYSNRN_CERN_JITU_ZAN1,
                 getData( dbData, F_LMTINTL_RN_CERN_JITU ) ) ;  // [限度算入与信合計（実勢現在残２）]



        /* --------------------------------------------------------
         * 市場性与信の項目
         * --------------------------------------------------------
         */
        // 規定担保計（規定値）
        dataValue = getDataValue( getData( dbData, F_KITANTANTKITE ) ) +    // [規定担保・担手（規定値）]
                    getDataValue( getData( dbData, F_KITANYKNKITE  ) ) +    // [規定担保・預金（規定値）]
                    getDataValue( getData( dbData, F_KITANSCTYKITE ) ) +    // [規定担保・有証（規定値）]
                    getDataValue( getData( dbData, F_KITANHSYKITE  ) ) +    // [規定担保・保証（規定値）]
                    getDataValue( getData( dbData, F_KITANFUDOKITE ) ) +    // [規定担保・不動産（規定値）]
                    getDataValue( getData( dbData, F_KITANTAKITE   ) ) ;    // [規定担保・その他（規定値）]
        String[] strKiteiKeiKitei = {   (String)getData( dbData, F_KITANTANTKITE ),
                                        (String)getData( dbData, F_KITANYKNKITE ),
                                        (String)getData( dbData, F_KITANSCTYKITE ),
                                        (String)getData( dbData, F_KITANHSYKITE ),
                                        (String)getData( dbData, F_KITANFUDOKITE ),
                                        (String)getData( dbData, F_KITANTAKITE )
                                    };
        dbData.put( F_KITANKIKITE, getOutShijoValue(strKiteiKeiKitei, dataValue) );

        // 規定担保計（参考値）
        dataValue = getDataValue( getData( dbData, F_KITANTANTSNKO ) ) +    // [規定担保・担手（参考値）]
                    getDataValue( getData( dbData, F_KITANYKNSNKO  ) ) +    // [規定担保・預金（参考値）]
                    getDataValue( getData( dbData, F_KITANSCTYSNKO ) ) +    // [規定担保・有証（参考値）]
                    getDataValue( getData( dbData, F_KITANHSYSNKO  ) ) +    // [規定担保・保証（参考値）]
                    getDataValue( getData( dbData, F_KITANFUDOSNKO ) ) +    // [規定担保・不動産（参考値）]
                    getDataValue( getData( dbData, F_KITANTASNKO   ) ) ;    // [規定担保・その他（参考値）]
        String[] strKiteiKeiSanko = {   (String)getData( dbData, F_KITANTANTSNKO ),
                                        (String)getData( dbData, F_KITANYKNSNKO ),
                                        (String)getData( dbData, F_KITANSCTYSNKO ),
                                        (String)getData( dbData, F_KITANHSYSNKO ),
                                        (String)getData( dbData, F_KITANFUDOSNKO ),
                                        (String)getData( dbData, F_KITANTASNKO )
                                    };
        dbData.put( F_KITANKISNKO, getOutShijoValue(strKiteiKeiSanko, dataValue) );

// 2004/04/13 CHG@S.SEIMURA 判定式の修正(GEC16-C-006)
        // 規定外担保計（見込取分）
        dataValue = getDataValue( getData( dbData, F_KGITTTMKOM  ) ) +      // [規定外担保・担手（見込取分）]
                    getDataValue( getData( dbData, F_KGITFDMKOM  ) ) +      // [規定外担保・不動産（見込取分）]
                    getDataValue( getData( dbData, F_KGITNHMKOM  ) ) +      // [規定外担保・入居保証金（見込取分）]
                    getDataValue( getData( dbData, F_KGITSKMKOM  ) ) +      // [規定外担保・債権（見込取分）]
                    getDataValue( getData( dbData, F_KGITTAMKOM  ) ) ;      // [規定外担保・その他（見込取分）]
        String[] strKiteiGaiKeiMikomi = {   (String)getData( dbData, F_KGITTTMKOM ),
                                            (String)getData( dbData, F_KGITFDMKOM ),
                                            (String)getData( dbData, F_KGITNHMKOM ),
                                            (String)getData( dbData, F_KGITSKMKOM ),
                                            (String)getData( dbData, F_KGITTAMKOM )
                                        };
        dbData.put( F_KGITMKOM, getOutShijoValue(strKiteiGaiKeiMikomi, dataValue) );

        // 規定外担保計（参考値）
        dataValue = getDataValue( getData( dbData, F_KGITTTSNKO  ) ) +      // [規定外担保・担手（参考値）]
                    getDataValue( getData( dbData, F_KGITFDSNKO  ) ) +      // [規定外担保・不動産（参考値）]
                    getDataValue( getData( dbData, F_HKGITNHSNKO ) ) +      // [規定外担保・入居保証金（参考値）]
                    getDataValue( getData( dbData, F_HKGITSKSNKO ) ) +      // [規定外担保・債権（参考値）]
                    getDataValue( getData( dbData, F_HKGITTASNKO ) ) ;      // [規定外担保・その他（参考値）]
        String[] strKiteiGaiKeiSanko = {    (String)getData( dbData, F_KGITTTSNKO ),
                                            (String)getData( dbData, F_KGITFDSNKO ),
                                            (String)getData( dbData, F_HKGITNHSNKO ),
                                            (String)getData( dbData, F_HKGITSKSNKO ),
                                            (String)getData( dbData, F_HKGITTASNKO )
                                        };
        dbData.put( F_KGITSNKO, getOutShijoValue(strKiteiGaiKeiSanko, dataValue) );


// 2003/05/29 MOV@S.SEIMURA 計算時のみ計算するように変更(00962)
        /* --------------------------------------------------------
         * 市場性本件後の項目
         * --------------------------------------------------------
        */
        // 全体（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））
        dataValue = getDataValue( getData( dbData, F_REFKESR1_NT_JZAN_CEPE ) ) +// [為替取引（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR2_NT_JZAN_CEPE ) ) +// [スワップ／オプション取引（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR3_NT_JZAN_CEPE ) ) +// [マーケットリスク内在型取引（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR4_NT_JZAN_CEPE ) ) +// [先物取引（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR5_NT_JZAN_CEPE ) ) ;// [その他市場性与信（ネット実勢現在残高（Ｃ／Ｅ＋Ｐ／Ｅ））]
        String[] strNetCEPE = { (String)getData( dbData, F_REFKESR1_NT_JZAN_CEPE ),
                                (String)getData( dbData, F_REFKESR2_NT_JZAN_CEPE ),
                                (String)getData( dbData, F_REFKESR3_NT_JZAN_CEPE ),
                                (String)getData( dbData, F_REFKESR4_NT_JZAN_CEPE ),
                                (String)getData( dbData, F_REFKESR5_NT_JZAN_CEPE ),
                            };
        dbData.put( F_REFKESR6_NT_JZAN_CEPE, getOutShijoValue(strNetCEPE, dataValue) );

        // 全体（ネット実勢現在残高（Ｃ／Ｅ））
        dataValue = getDataValue( getData( dbData, F_REFKESR1_NT_JZAN_CE ) ) +  // [為替取引（ネット実勢現在残高（Ｃ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR2_NT_JZAN_CE ) ) +  // [スワップ／オプション取引（ネット実勢現在残高（Ｃ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR3_NT_JZAN_CE ) ) +  // [マーケットリスク内在型取引（ネット実勢現在残高（Ｃ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR4_NT_JZAN_CE ) ) +  // [先物取引（ネット実勢現在残高（Ｃ／Ｅ））]
                    getDataValue( getData( dbData, F_REFKESR5_NT_JZAN_CE ) ) ;  // [その他市場性与信（ネット実勢現在残高（Ｃ／Ｅ））]
        String[] strNetCE = {   (String)getData( dbData, F_REFKESR1_NT_JZAN_CE ),
                                (String)getData( dbData, F_REFKESR2_NT_JZAN_CE ),
                                (String)getData( dbData, F_REFKESR3_NT_JZAN_CE ),
                                (String)getData( dbData, F_REFKESR4_NT_JZAN_CE ),
                                (String)getData( dbData, F_REFKESR5_NT_JZAN_CE ),
                            };
        dbData.put( F_REFKESR6_NT_JZAN_CE, getOutShijoValue(strNetCE, dataValue) );


        /*
         * 裸与信項目
         */
        // 裸与信（規定値）計数情報（市場性与信）
        dataValue = getDataValue( getData( dbData, F_LMTINTL_RN_HONAF_ZAN ) ) - // [限度算入与信合計（本件後与信額）]
                    getDataValue( getData( dbData, F_KITANKIKITE      ) ) ; // [規定担保計（規定値）]
        String[] strHadakaYosinKite = { (String)getData( dbData, F_LMTINTL_RN_HONAF_ZAN ),
                                        (String)getData( dbData, F_KITANKIKITE ),
                                        };
// 2003/06/25 CHG@S.SEIMURA 裸与信の合計値がマイナス値の場合、0を設定する(01222)
        if ( dataValue < 0 ) {
            dataValue = 0;
        }
        dbData.put( F_STRCREKITE, getOutShijoValue(strHadakaYosinKite, dataValue) );

        // 裸与信（参考値）計数情報（市場性与信）
        dataValue = getDataValue( getData( dbData, F_LMTINTL_RN_HONAF_ZAN ) ) - // [限度算入与信合計（本件後与信額）]
                    getDataValue( getData( dbData, F_KITANKISNKO      ) ) ; // [規定担保計（参考値）]
        String[] strHadakaYosinSanko = {    (String)getData( dbData, F_LMTINTL_RN_HONAF_ZAN ),
                                            (String)getData( dbData, F_KITANKISNKO ),
                                        };
// 2003/06/23 CHG@S.SEIMURA 裸与信の合計値がマイナス値の場合、0を設定する(01222)
        if ( dataValue < 0 ) {
            dataValue = 0;
        }
        dbData.put( F_STRCRESNKO, getOutShijoValue(strHadakaYosinSanko, dataValue) );


        // 結果データを設定
        hstComBasket.put( K_DB_DATA, dbData ) ;

        return ;

    }


    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数で初期表示、または計数再取得ボタンが押された時のみに、
     *   一般与信以外の項目のデータ計算を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable  hstComBasket    共有情報
     */

    public void computeKokyakuShutoku( Hashtable hstComBasket ) {

        Hashtable dbData = (Hashtable)hstComBasket.get( K_DB_DATA ) ;

        String[] strKitei      = (String[])dbData.get( F_HIKIATE_KITEITI     ) ;
        String[] strJika       = (String[])dbData.get( F_HIKIATE_JIKA        ) ;

        int dataValue  = 0 ;
        int workValue1 = 0 ;
        int allSouteiSnin = 0 ;
        int allSouteiZan  = 0 ;

        int intShote1 = 0;
        int intShote2 = 0;

        int checkLength = 0;


        /* --------------------------------------------------------
         * 本件後引当状況の項目
         * --------------------------------------------------------
         */
        // 規定・優良・商手（規定値・時価ベース）の計算
        if ( !strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP].trim().equals( V_EMPTY_STRING ) ||
                !( (String)getData( dbData, F_SUTNTE ) ).trim().equals( V_EMPTY_STRING ) ) {
            intShote1 = getDataValue ( strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] ) ;        // [規定・優良・商手（規定値）]
            intShote2 = getDataValue ( getData( dbData, F_SUTNTE ) ) ;

            // 合計値が0より大きい場合、規定・優良・商手（規定値・時価ベース）に設定
            if ( ( intShote1 + intShote2 ) > 0 ) {
                strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] = String.valueOf( intShote1 + intShote2 ) ;
                strJika[V_KEISU_KTI_YUTNP_SYOTE_BAP]  = String.valueOf( intShote1 + intShote2 ) ;

                dbData.put( F_HIKIATE_KITEITI, strKitei ) ;
                dbData.put( F_HIKIATE_JIKA,    strJika  ) ;

            // 合計値が0以下の場合は、規定・優良・商手（規定値・時価ベース）に""を設定
            } else {
                strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] = V_EMPTY_STRING ;
                strJika[V_KEISU_KTI_YUTNP_SYOTE_BAP]  = V_EMPTY_STRING ;

                dbData.put( F_HIKIATE_KITEITI, strKitei ) ;
                dbData.put( F_HIKIATE_JIKA,    strJika  ) ;
            }

        // 共に""の場合は、規定・優良・商手（規定値・時価ベース）に""を設定
        } else {
            strKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] = V_EMPTY_STRING ;
            strJika[V_KEISU_KTI_YUTNP_SYOTE_BAP]  = V_EMPTY_STRING ;

            dbData.put( F_HIKIATE_KITEITI, strKitei ) ;
            dbData.put( F_HIKIATE_JIKA,    strJika  ) ;
        }


        /*
         * 裸与信項目 禀議取得時、「規定担保計」は値がない為(手入力計算であるから)、計算結果は限度算入与信合計の値のみ
         */
        // 裸与信（規定値）計数情報（市場性与信）
        dbData.put( F_STRCREKITE, (String)getData( dbData, F_LMTINTL_RN_HONAF_ZAN ) ) ; // [限度算入与信合計（本件後与信額）]

        // 裸与信（参考値）計数情報（市場性与信）
        dbData.put( F_STRCRESNKO, (String)getData( dbData, F_LMTINTL_RN_HONAF_ZAN ) ) ; // [限度算入与信合計（本件後与信額）]


        // 経営指標のキーを設定
        dbData.put( F_URIAGEGESSHO4, new String(V_EMPTY_STRING) ) ;
        dbData.put( F_KEIJOEKI_RIT4, new String(V_EMPTY_STRING) ) ;
        dbData.put( F_TOKIEKI_RIT4,  new String(V_EMPTY_STRING) ) ;
        dbData.put( F_URIAGEGESSHO5, new String(V_EMPTY_STRING) ) ;
        dbData.put( F_KEIJOEKI_RIT5, new String(V_EMPTY_STRING) ) ;
        dbData.put( F_TOKIEKI_RIT5,  new String(V_EMPTY_STRING) ) ;


        // 結果データを設定
        hstComBasket.put( K_DB_DATA, dbData ) ;

        return ;

    }

    /**
     * <DL>
     * <DL><b>Hashtableから、指定されたキーの有無判定と、値の取得を行う。</b></DL>
     * </DL>
     * @param   Hashtable    tbl    ハッシュテーブル情報
     * @param   String       name   ハッシュから検索を行うキー名
     * @return  Object              ハッシュから取得したデータオブジェクト
     */
    private Object getData( Hashtable tbl, String name ) {


        Object obj = ( tbl.containsKey( name ) ) ?
                        tbl.get( name ) : new String( V_EMPTY_STRING ) ;
        return obj ;

    }


    /**
     * <DL>
     * <DL><b>数値文字列からint数値への変換を行う。</b></DL>
     * </DL>
     * @param   Object       numData   ハッシュから取得したデータオブジェクト
     * @return  int                    変換されたint型データ
     */
    private int getDataValue( Object numData ) {

        String data = null ;

        // パラメータのオブジェクトが、Stringのインスタンス時に処理を行う
        if( numData instanceof String ) {
            data = numData.toString() ;
        } else {
            return int0 ;
        }
        if( data == V_NULL_STRING ||
              data.equals(V_EMPTY_STRING) ) {

            return 0;
        } else {

            return Integer.parseInt(data);
        }

    }


    /**
     * <DL>
     * <DL><b>数値文字列からlong数値への変換を行う。</b></DL>
     * </DL>
     * @param   Object       numData   ハッシュから取得したデータオブジェクト
     * @return  int                    変換されたint型データ
     */
    private long getDataValue2( Object numData ) {

        String data = null ;

        // パラメータのオブジェクトが、Stringのインスタンス時に処理を行う
        if( numData instanceof String ) {
            data = numData.toString() ;
        } else {
            return int0 ;
        }
        if( data == V_NULL_STRING ||
              data.equals(V_EMPTY_STRING) ) {

            return 0;
        } else {

            return Long.parseLong(data);
        }

    }


    /**
     * <DL>
     * <DL><b>指定された名前で、共有情報に整数値で登録（put）する。</b></DL>
     * </DL>
     * @param   Hashtable    dHash  共有情報
     * @param   String       name   登録する名前
     * @param   int          data   登録するデータ
     */
    private void addHash( Hashtable dHash, String name, int data ) {

        dHash.put( name, Integer.toString( data ) ) ;


    }

    /**
     * <DL>
     * <DL><b>計算結果が0の場合、出力する値を0とするか""とするかをチェックする</b></DL>
     * </DL>
     * @param   String[]      strValueList 値が入った配列
     * @param   int[]         intIndexList チェックを行う値の入った配列のインデックス値
     * @param   long          longKekka    計算結果
     * @return  String        Long.toString(longKekka)/V_EMPTY_STRING
     */
    private String getOutHonkengoValue ( String[] strValueList, int[] intIndexList, long longKekka ) {

        int intListLength = intIndexList.length;

        // 計算結果が0の場合、計算に使用した各値が全て""の場合
        // 合計値も""とする
        if ( longKekka == 0 ) {

            for ( int i = 0 ; i < intIndexList.length ; i++ ) {
                if ( strValueList[intIndexList[i]].trim().equals( V_EMPTY_STRING ) ) {
                    intListLength-- ;
                }
            }

            // 全て""の場合
            if ( intListLength == 0 ) {
                return V_EMPTY_STRING;
            }
        }

        return Long.toString( longKekka );

    }

    /**


     * <DL>
     * <DL><b>計算結果が0の場合、出力する値を0とするか""とするかをチェックする</b></DL>
     * </DL>
     * @param   String[]      strValueList 値が入った配列
     * @param   long          intKekka    計算結果
     * @return  String        Long.toString(lngKekka)/V_EMPTY_STRING
     */
    private String getOutHonkengoValue ( String[] strValueList, long lngKekka ) {

        int intListLength = strValueList.length;

        // 計算結果が0の場合、計算に使用した各値が全て""の場合
        // 合計値も""とする
        if ( lngKekka == 0 ) {

            for ( int i = 0 ; i < strValueList.length ; i++ ) {
                if( (strValueList[i] == V_NULL_STRING) ||
                    ( strValueList[i].trim().equals( V_EMPTY_STRING )) ) {
                    intListLength-- ;
                }
            }

            // 全て""の場合
            if ( intListLength == 0 ) {
                return V_EMPTY_STRING;
            }
        }

        return Long.toString( lngKekka );

    }

    /**
     * <DL>
     * <DL><b>計算結果が0の場合、出力する値を0とするか""とするかをチェックする</b></DL>
     * </DL>
     * @param   String[]      strValueList 値が入った配列
     * @param   int           intKekka    計算結果
     * @return  String        Integer.toString(intKekka)/V_EMPTY_STRING
     */
    private String getOutShijoValue ( String[] strValueList, int intKekka ) {

        int intListLength = strValueList.length;

        // 計算結果が0の場合、計算に使用した各値が全て""の場合
        // 合計値も""とする
        if ( intKekka == 0 ) {

            for ( int i = 0 ; i < strValueList.length ; i++ ) {
                if ( strValueList[i].trim().equals( V_EMPTY_STRING ) ) {
                    intListLength-- ;
                }
            }

            // 全て""の場合
            if ( intListLength == 0 ) {
                return V_EMPTY_STRING;
            }
        }

        return Integer.toString( intKekka );

    }

    /**
     * <DL>
     * <DL><b>同時審査の計数案件番号を設定する。</b></DL>
     * </DL>
     * @param   Hashtable       hstComBasket   共有情報
     */
     public void setKeisuAnkenNoLink( Hashtable hstComBasket )
                        throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException ,WACSApplException{

        try {

            // 共有情報から案件番号を取得
            Hashtable hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
            String strAnken = (String)hstKey.get( F_LC_NO ) ;   // 設定対象LC_NO
            if (strAnken==null ) {      // パラメタチェック
                hstComBasket.put(K_RETURN, new Integer(RC_EPARAM)) ;
                return ;
            }

            // 禀議ＷＦクラスのインスタンスを取得
            RLRRGCOM_WF wf = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;

            // 禀議共通ＤＢクラスのインスタンスを取得
            RLRRGCOM_DB db = new RLRRGCOM_DB( folder, dbcon, dbparam ) ;

            // ワークフロー共通領域
            Hashtable hstWF = null ;

            // 関連案件番号(同時審査対象)の取得
            wf.getKanrenAnken(hstComBasket);
            hstWF = (Hashtable)hstComBasket.get(K_WF_DATA);

            // 取得件数の取得
            int result = ((Integer)hstComBasket.get(K_RETURN)).intValue();

            // 同時審査対象の案件番号が０件の時
            if(result == IRingi.RC_DATA_NOT_FOUND){

                // 同時審査対象外の実行結果を設定
                hstComBasket.put(K_RETURN, new Integer(RC_DOJI_SINSA_GAI)) ;
                return ;

            }

            // 同時審査案件番号の取得と設定
            String[] ankenList = (String[])(hstWF.get( F_KANREN_ANKEN )) ;
            hstKey.put(F_DOJISINSA_LC_NO, ankenList);
            hstComBasket.put(K_KEY_DATA, hstKey);
            db.setKeisuAnkenNoLink( hstComBasket ) ;


            // 共有情報の実行結果に正常'0'を設定し、処理を終了
            hstComBasket.put( K_RETURN, new Integer( RC_OK ) ) ;


        } catch( com.ibm.jp.wacs.db.WACSDBException e ) {
            throw e;
        } catch( WACSSysException e ) {
            throw e;
        } finally {

        }

        return ;

    }


    /**
     * <DL>
     * <DL><b>同時審査の計数案件番号を解除する。</b></DL>
     * </DL>
     * @param   Hashtable       hstComBasket   共有情報
     */
//  public void cancelKeisuAnkenNoLink( Hashtable hstComBasket )
//                  throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException, WACSApplException {
//      cancelKeisuAnkenNoLink( hstComBasket,0 );
//      cancelKeisuAnkenNoLink( hstComBasket,1 );  // TSR DEBUG用
//  }


    /**
     * <DL>
     * <DL><b>同時審査の計数案件番号を解除する。</b></DL>
     * </DL>
     * @param   Hashtable       hstComBasket   　共有情報
     * @param   int             intKeisuCopyFlag 0:計数複写なし else:計数複写あり
     */
    public void cancelKeisuAnkenNoLink( Hashtable hstComBasket,int intKeisuCopyFlag )
                    throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException, WACSApplException {


        try {

            // 共有情報から案件番号を取得
            // キー共通領域
            Hashtable hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
            String strAnken = (String)hstKey.get( F_LC_NO ) ;   // 解除対象LC_NO
            if (strAnken==null ) {
                hstComBasket.put(K_RETURN, new Integer(RC_EPARAM)) ;
                return ;
            }

            // 禀議ＷＦクラスのインスタンスを取得
            RLRRGCOM_WF wf = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;

            // 禀議共通ＤＢクラスのインスタンスを取得
            RLRRGCOM_DB db = new RLRRGCOM_DB( folder, dbcon, dbparam ) ;

            // ワークフロー共通領域
            Hashtable hstWF = null ;

            // 関連案件番号(同時審査対象)の取得
            wf.getKanrenAnken(hstComBasket);
            hstWF = (Hashtable)hstComBasket.get(K_WF_DATA);

            // 取得件数の取得
            int result = ((Integer)hstComBasket.get(K_RETURN)).intValue();

            // 同時審査対象の案件番号が０件の時
            if(result == IRingi.RC_DATA_NOT_FOUND){

                // 同時審査対象外の実行結果を設定
                hstComBasket.put( K_RETURN, new Integer( RC_DOJI_SINSA_GAI ) ) ;
                return ;

            }

            // 同時審査案件番号の取得と設定
            // 計数情報の複写フラグは'0'固定
            String[] ankenList = (String[])hstWF.get(F_KANREN_ANKEN) ;

            hstKey.put(F_KAIJO_LC_NO, strAnken) ;           // 解除対象LC_NO
            hstKey.put(F_DOJISINSA_LC_NO, ankenList) ;      // 同時審査対象LC_NO
            if (intKeisuCopyFlag==0) {
                hstKey.put(F_KEISU_CP_FLG,new String("0"));     // 計数複写なし
            } else {
                hstKey.put(F_KEISU_CP_FLG,new String("1"));     // 計数複写あり
            }

            hstComBasket.put(K_KEY_DATA,hstKey);

            db.cancelKeisuAnkenNoLink( hstComBasket ) ;     // DB同時審査計数案件解除処理


            // 共有情報の実行結果に正常'0'を設定し、処理を終了
            hstComBasket.put( K_RETURN, new Integer( RC_OK ) ) ;


        } catch( com.ibm.jp.wacs.db.WACSDBException e ) {
            throw e;
        } catch( WACSSysException e ) {
            throw e;
        } finally {

        }

        return ;

    }


    /**
     * <DL>
     * <DL><b>同時審査の計数案件番号を解除し、計数情報も分割（複写）する。</b></DL>
     * </DL>
     * @param   Hashtable       hstComBasket   共有情報
     */
    public void partitionDojiShinsa( Hashtable hstComBasket )
                throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException, WACSApplException {

        try {

            // 共有情報から案件番号を取得
            // ？？？？は案件番号[]のＫｅｙ
            // String inAnken = (String)hstComBasket.get( "????" ) ;

            // 禀議ＷＦクラスのインスタンスを取得
            RLRRGCOM_WF wf = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;

            // 禀議共通ＤＢクラスのインスタンスを取得
            RLRRGCOM_DB db = new RLRRGCOM_DB( folder, dbcon, dbparam ) ;

            // ワークフロー共通領域
            Hashtable hstWF = null ;

            // キー共通領域
            Hashtable hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            // 関連案件番号(同時審査対象)の取得
            wf.getKanrenAnken(hstComBasket);
            hstWF = (Hashtable)hstComBasket.get(K_WF_DATA);

            int result = ((Integer)hstComBasket.get(K_RETURN)).intValue();

            if(result == IRingi.RC_DATA_NOT_FOUND){
                // 同時審査対象外の実行結果を設定
                hstComBasket.put( K_RETURN, new Integer( RC_DOJI_SINSA_GAI ) ) ;
                return ;
            }

            // 同時審査案件番号の取得と設定
            // 計数情報の複写フラグは'1'固定
            String[] ankenList = (String[])hstWF.get(F_KANREN_ANKEN) ;
            hstKey.put(F_KAIJO_LC_NO, hstKey.get(F_LC_NO));
            hstKey.put(F_DOJISINSA_LC_NO, ankenList);
            hstKey.put(F_KEISU_CP_FLG,new String("1"));
            hstComBasket.put(K_KEY_DATA,hstKey);
            db.cancelKeisuAnkenNoLink( hstComBasket ) ;

            // 共有情報の実行結果に正常'0'を設定し、処理を終了
            hstComBasket.put( K_RETURN, new Integer( RC_OK ) ) ;

        } catch( com.ibm.jp.wacs.db.WACSDBException e ) {
            throw e;
        } catch( WACSSysException e ) {
            throw e;
        } finally {
        }

        return ;

    }





    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   Hashtable中の全てのデータを違うHashtableにコピーする<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param      Hashtable    hstTbl1   コピー元のハッシュ
     *   @param      Hashtable    hstTbl2   コピー先のハッシュ
     */
    public void setHashToHash( Hashtable hstTbl1, Hashtable hstTbl2 ) {


        /*
         * リスト項目以外は全て設定
         */
        Enumeration e = hstTbl1.keys() ;
        while( e.hasMoreElements() ) {

            Object obj  = e.nextElement() ;
            Object obj2 = hstTbl1.get( obj ) ;


            hstTbl2.put( obj, obj2 ) ;
        }


        return ;

    }



    /**
     *   <DL>
     *   <DT><b>メソッド概要：</b><DD>
     *   出力データ設定<BR>
     *　 </DD><DT>
     *   </DL>
     *   @param      CraftsDataBean ibean        入力データビーン
     *   @param      CraftsDataBean obean        出力データビーン
     *   @param      Hashtable      hstComBasket 共有情報
     */
    public void setOutData( CraftsDataBean ibean,
                            CraftsDataBean obean,
                            Hashtable hstComBasket ) {

        /*
         * 入力データをそのまま設定
         */
        String[] keys = ibean.getKeyNames() ;
        for(int i = 0; i < keys.length; i++) {

            if( ibean.getArraySize( keys[i] ) < 0 ) {
                obean.setString( keys[i], ibean.getString( keys[i] ) ) ;

            } else {
                obean.setStringArray( keys[i], ibean.getStringArray( keys[i] ) ) ;
            }
        }



        /*
         * 以下で変更が有ったものや、新たに取得したデータを設定する
         */

        /*
         * 処理結果
         */
        obean.setString( F_SUCCESS_FLAG, V_TRUE         ) ;
        obean.setString( F_ERROR_ID    , new String(V_EMPTY_STRING) ) ;
        obean.setString( F_ERROR_TYPE  , new String(V_EMPTY_STRING) ) ;
        obean.setString( F_ERROR_MSG   , new String(V_EMPTY_STRING) ) ;


        /*
         * 照会・更新区分
         */
        obean.setString( F_UPDATE_MODE_FLG, ibean.getString( F_UPDATE_MODE_FLG ) ) ;


        /*
         * 色変情報＆ボタン制御情報
         */


        /*
         * ＤＢのハッシュから全ての情報を設定
         * この時点でＤＢハッシュには、ホスト、ＤＢ、計算項目が設定されている
         */
        Hashtable dbData = (Hashtable)hstComBasket.get( K_DB_DATA ) ;
        Enumeration e = dbData.keys() ;
        while( e.hasMoreElements() ) {

            // キー名とデータを取得
            Object obj  = e.nextElement() ;
            Object obj2 = dbData.get( obj ) ;

            if( obj2 instanceof String ) {
                obean.setString( (String)obj, (String)obj2 ) ;
            } else if( obj2 instanceof String[] ) {
                obean.setStringArray( (String)obj, (String[])obj2 ) ;
            }
        }


        /*
         * 取引先店番が７桁の時、３桁にして画面に返す
         */
        String inBrno = obean.getString( F_BRNO ) ;
        if( inBrno != null && inBrno.length() == 7 ) {
            obean.setString( F_BRNO, inBrno.substring(int4) ) ;
        }

// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
        /*
         * 保全率・金額単位の全角スペースをトリムして画面に返す
         */
        RLRRGCOM_DB dbCom = new RLRRGCOM_DB(this.folder, this.dbcon, this.dbparam);
        String strHozenTaniMsg = obean.getString( F_HOZEN_TANI_MSG ) ;
        obean.setString( F_HOZEN_TANI_MSG, dbCom.trimZenkakuBlank( strHozenTaniMsg ) ) ;
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End

        return ;


    }




    /**
     * <DL>
     * <DL><b>計数情報項目の計算を行う。</b></DL>
     * </DL>
     * 保存項目のオーバーフローチェック
     * @param   Hashtable   hstComBasket    共有情報
     * @return  int          0              正常
     * @return  int         -1              日付の異常
     * @return  int         -2              オーバーフロー
     */
    public int checkOverFlow( Hashtable hstComBasket ) {


        Hashtable tbl = (Hashtable)hstComBasket.get( K_DB_DATA ) ;

        /*
         * 指定日付のチェック
         */

        /*
         * チェック対象はその他与信の日付２つ、経営指標の中間と決算
         */

// 2005.02.15   Chg Start K.Sato(GEC16-C-143-005)
// 日付項目のオーバーフローチェックロジックの修正

        // 日付項目
        ArrayList arrHidukeData = new ArrayList();

        // 経営指標
//      String[] hiduke = { F_KESSANKI4,       F_KESSANKI5 } ;
        String[] strKeiShihyo = { F_KESSANKI4,     F_KESSANKI5 } ;

        // 一般与信状況
        String[] strKbi = (String[])tbl.get(F_KBI);

//      for(int i = 0; i < hiduke.length + int2; i++) {
//
//          String str = V_EMPTY_STRING ;
//          if( i < hiduke.length ) {
//              str = (String)getData( tbl, hiduke[i] ) ;
//          } else {
//              str = strKbi[int40+i];
//          }
//
//
//          int intLen = 0 ;
//          intLen = str.length() ;
//
//          // 入力されたデータは、必ず"YYMM"か""で送られる
//          if( intLen != 4 && intLen != 0  ) {
//              // -1をリターン
//              return intM1 ;
//          }
//
//
//          // 指定の月が異常
//          if( intLen != 0 ) {
//              int value = new Integer( str.substring( 2, 4 ) ).intValue() ;
//              if( value < 1 || 12 < value ) {
//                  // -1をリターン
//                  return intM1 ;
//              }
//          }
//
//      }

        /*
         * チェックする日付項目データ取得
         */
        // 一般与信状況
// 2009/06/23 DEL@R.Matsumura GEC20-C-059 start
//      arrHidukeData.add ( strKbi[V_KEISU_SONOTA_YSN1_BAP] );
// 2009/06/23 DEL@R.Matsumura GEC20-C-059 end
        arrHidukeData.add ( strKbi[V_KEISU_SONOTA_YSN2_BAP] );

        // 経営指標
        for( int i = 0 ; i < strKeiShihyo.length ; i++ ){
            arrHidukeData.add ( (String)getData( tbl, strKeiShihyo[i] ) );
        }

        String[] strHidukeData = (String[])arrHidukeData.toArray( new String[0] ) ;

        for( int i = 0; i < strHidukeData.length ; i++ ){

            int intLen = 0 ;
            intLen = strHidukeData[i].length() ;

            // 入力されたデータは、必ず"YYMM"か""で送られる
            if( intLen != 4 && intLen != 0  ) {
                // -1をリターン
                return intM1 ;
            }


            // 指定の月が異常
            if( intLen != 0 ) {
                int value = new Integer( strHidukeData[i].substring( 2, 4 ) ).intValue() ;
                if( value < 1 || 12 < value ) {
                    // -1をリターン
                    return intM1 ;
                }
            }

        }
// 2005.02.15   Chg End K.Sato(GEC16-C-143-005)



        /*
         *
         * 以下でオーバーフローデータが有るかを確認する
         *
         */


        //オーバーフローチェック単体編
        String[][] valueOverFlow = {

                { F_LMTINTL_RN_HONAF_ZAN,       "5", "0" }, /* 限度算入与信合計(本件後与信額) */
                { F_LMTINTL_RN_CEPERN_JI,       "5", "0" }, /* 限度算入与信合計(実勢現在残1) */
                { F_LMTINTL_RN_CERN_JITU,       "5", "0" }, /* 限度算入与信合計(実勢現在残2) */
                { F_LMTINTL_RN_LMT,             "5", "0" }, /* 限度算入与信合計(指定月末極度額) */
                { F_LMTINTL_RN_MEND_ZAN,        "5", "0" }, /* 限度算入与信合計(指定月末残高) */
                { F_SIJOYSNRN_HONAF_ZAN,        "5", "0" }, /* 市場性与信合計(本件後与信額) */
                { F_SIJOYSNRN_CEPERN_JITU_ZAN1, "5", "0" }, /* 市場性与信合計(実勢現在残1) */
                { F_SIJOYSNRN_CERN_JITU_ZAN1,   "5", "0" }, /* 市場性与信合計(実勢現在残2) */
                { F_SIJOYSNRN_MEND_ZAN,         "5", "0" }, /* 市場性与信合計(指定月末残高) */
                { F_SIJOYSNRN_LMT,              "5", "0" }, /* 市場性与信合計(指定月末極度額) */
                { F_KEIJOEKI_RIT4,              "2", "1" }, /* 中間決算(経常利益率) */
                { F_TOKIEKI_RIT4,               "2", "1" }, /* 中間決算(当期利益率) */
                { F_KEIJOEKI_RIT5,              "2", "1" }, /* 決算予想(経常利益率) */
                { F_TOKIEKI_RIT5,               "2", "1" }, /* 決算予想(当期利益率) */
                { F_KITANKIKITE,                "5", "0" }, /* 規定担保計(規定値) */
                { F_KITANKISNKO,                "5", "0" }, /* 規定担保計(参考値) */
                { F_STRCREKITE,                 "5", "0" }, /* 裸与信(規定値) */
                { F_STRCRESNKO,                 "5", "0" }, /* 裸与信(参考値) */
                { F_KGITMKOM,                   "5", "0" }, /* 規定外担保計(見込取分) */
                { F_KGITSNKO,                   "5", "0" }, /* 規定外担保計(参考値) */
                { F_REFKESR6_NT_JZAN_CEPE,      "5", "0" }, /* 全体(ネット実勢現在残高(C/E+P/E))</P> */
// 2011/12/22 CHG@M.Hayashi GEC23-C-051(ISID-C1202-02-ITa-0001(00770)) Start
                { F_REFKESR6_NT_JZAN_CE,        "5", "0" }, /* 全体(ネット実勢現在残高(C/E))</P> */
                { F_HOZEN_IPNYSN,               "8", "0" }, /* 保全率・限度算入一般与信 */
                { F_HOZEN_HOZENRT,              "3", "1" }, /* 保全率・保全率 */
// 2011/12/22 CHG@M.Hayashi GEC23-C-051(ISID-C1202-02-ITa-0001(00770)) End
// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
                { F_HOZEN_SOGOSNYO,             "9", "0" }, /* 保全率・総合信用 */
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End
                };




        for(int i = 0; i < valueOverFlow.length; i++){

            //DBHashtableからデータを取得
            String valueData = (String)getData( tbl, valueOverFlow[i][int0] );

            if( valueData.length() <= 0 ){
                continue;
            }

            /*
             * 計算の結果により、どのような値が入るか分からないため
             * 全ての値に対して、絶対値（正数）にしてチェックを行う
             */

            //符号有無チェック（少数点なし）
            if( valueOverFlow[i][int2].equals( "0" ) ){
                valueData = Math.abs( Integer.parseInt( valueData ) ) + V_EMPTY_STRING;

            //小数点有無チェック
            }else if( valueOverFlow[i][int2].equals( "1" ) ){
                valueData = Math.abs( Double.parseDouble( valueData ) ) + V_EMPTY_STRING;
                valueData = new Double(valueData).intValue() + V_EMPTY_STRING;

            }

            //オーバーフローチェック
            if( valueData.length() > Integer.parseInt( valueOverFlow[i][1] ) ){
                // -2をリターン
                return intM2;
            }
        }


        // オーバーフローチェック配列編
        // 配列データ
// 2005.02.15   Chg Start K.Sato(GEC16-C-143-005)
// 配列2番目のインデックス値はIRingiItemKeisuで定義している定数を使用する
        String[][] listOverFlow = {

                    // 与信状況


//2004/07/07 CHG@N.SAKASHITA (GEC16-C-012-411)
                    { F_IPNYSNDLTZGG_TOT,   V_KEISU_GENDOSAN_TOT_BAP + "",          "0" },
                    { F_HONAF_ZAN_TOT,      V_KEISU_KASHISHO_TOT_BAP + "",          "0" },
                    { F_JISKSN_TOT,         V_KEISU_KASHISHO_TOT_BAP + "",          "0" },
                    { F_LMT_TOT,            V_KEISU_KASHISHO_TOT_BAP + "",          "0" },
                    { F_MEND_ZAN_TOT,       V_KEISU_KASHISHO_TOT_BAP + "",          "0" },
                    { F_HONAF_ZAN,          V_KEISU_KASHISHO_TOT_BAP + "",          "0" }, // 本件後残高
                    { F_HONAF_ZAN,          V_KEISU_GAITAME_TOT_BAP  + "",          "0" },
                    { F_HONAF_ZAN,          V_KEISU_GAITAME_YUSYU_STOT_BAP + "",    "0" },
                    { F_HONAF_ZAN,          V_KEISU_GAITAME_YUNYU_STOT_BAP + "",    "0" },
                    { F_HONAF_ZAN,          V_KEISU_SHISHO_TOT_BAP + "",            "0" },
                    { F_HONAF_ZAN,          V_KEISU_GENDOLOAN_TOT_BAP + "",         "0" },
/* YC20218-02 Start */
                    { F_HONAF_ZAN,          V_KEISU_HLSHINYOFUSANNYU_BAP + "",      "0" },
/* YC20218-02 End */
                    { F_HONAF_ZAN,          V_KEISU_GNDFUSAN_TOT_BAP + "",          "0" },
                    { F_HONAF_ZAN,          V_KEISU_IPPANYSN_TOT_BAP + "",          "0" },
                    { F_HONAF_ZAN,          V_KEISU_SONOTA_TOT_BAP + "",            "0" },
                    { F_JISKSN,             V_KEISU_KASHISHO_TOT_BAP + "",          "0" }, // 実勢現在残
                    { F_JISKSN,             V_KEISU_GAITAME_TOT_BAP  + "",          "0" },
                    { F_JISKSN,             V_KEISU_GAITAME_YUSYU_STOT_BAP + "",    "0" },
                    { F_JISKSN,             V_KEISU_GAITAME_YUNYU_STOT_BAP + "",    "0" },
                    { F_JISKSN,             V_KEISU_SHISHO_TOT_BAP + "",            "0" },
                    { F_JISKSN,             V_KEISU_GENDOLOAN_TOT_BAP + "",         "0" },
/* YC20218-02 Start */
                    { F_JISKSN,             V_KEISU_HLSHINYOFUSANNYU_BAP + "",      "0" },
/* YC20218-02 End */
                    { F_JISKSN,             V_KEISU_GNDFUSAN_TOT_BAP + "",          "0" },
                    { F_JISKSN,             V_KEISU_IPPANYSN_TOT_BAP + "",          "0" },
                    { F_JISKSN,             V_KEISU_SONOTA_TOT_BAP + "",            "0" },
                    { F_LMT,                V_KEISU_KASHISHO_TOT_BAP + "",          "0" }, // 極度額
                    { F_LMT,                V_KEISU_GAITAME_TOT_BAP  + "",          "0" },
                    { F_LMT,                V_KEISU_GAITAME_YUSYU_STOT_BAP + "",    "0" },
                    { F_LMT,                V_KEISU_GAITAME_YUNYU_STOT_BAP + "",    "0" },
                    { F_LMT,                V_KEISU_SHISHO_TOT_BAP + "",            "0" },
                    { F_LMT,                V_KEISU_GENDOLOAN_TOT_BAP + "",         "0" },
/* YC20218-02 Start */
                    { F_LMT,                V_KEISU_HLSHINYOFUSANNYU_BAP + "",      "0" },
/* YC20218-02 End */
                    { F_LMT,                V_KEISU_IPPANYSN_TOT_BAP + "",          "0" },
                    { F_LMT,                V_KEISU_SONOTA_TOT_BAP + "",            "0" },
                    { F_MEND_ZAN,           V_KEISU_KASHISHO_TOT_BAP + "",          "0" }, // 月末残高
                    { F_MEND_ZAN,           V_KEISU_GAITAME_TOT_BAP  + "",          "0" },
                    { F_MEND_ZAN,           V_KEISU_GAITAME_YUSYU_STOT_BAP + "",    "0" },
                    { F_MEND_ZAN,           V_KEISU_GAITAME_YUNYU_STOT_BAP + "",    "0" },
                    { F_MEND_ZAN,           V_KEISU_SHISHO_TOT_BAP + "",            "0" },
                    { F_MEND_ZAN,           V_KEISU_GENDOLOAN_TOT_BAP + "",         "0" },
/* YC20218-02 Start */
                    { F_MEND_ZAN,           V_KEISU_HLSHINYOFUSANNYU_BAP + "",      "0" },
/* YC20218-02 End */
                    { F_MEND_ZAN,           V_KEISU_GNDFUSAN_TOT_BAP + "",          "0" },
                    { F_MEND_ZAN,           V_KEISU_IPPANYSN_TOT_BAP + "",          "0" },
                    { F_MEND_ZAN,           V_KEISU_SONOTA_TOT_BAP + "",            "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_KASHISHO_TOT_BAP + "",          "0" }, // 当月増減
                    { F_IPNYSNDLTZGG,       V_KEISU_GAITAME_TOT_BAP  + "",          "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_GAITAME_YUSYU_STOT_BAP + "",    "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_GAITAME_YUNYU_STOT_BAP + "",    "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_SHISHO_TOT_BAP + "",            "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_GENDOLOAN_TOT_BAP + "",         "0" },
/* YC20218-02 Start */
                    { F_IPNYSNDLTZGG,       V_KEISU_HLSHINYOFUSANNYU_BAP + "",      "0" },
/* YC20218-02 End */
                    { F_IPNYSNDLTZGG,       V_KEISU_IPPANYSN_TOT_BAP + "",          "0" },
                    { F_IPNYSNDLTZGG,       V_KEISU_SONOTA_TOT_BAP + "",            "0" },

                };
// 2005.02.15   Chg End K.Sato(GEC16-C-143-005)


        for(int i = 0; i < listOverFlow.length; i++){
            String checkData = new String();
            if( tbl.containsKey( listOverFlow[i][int0] ) == false ){
                continue;
            }

            //DBHashtableから配列データを取得
            String[] listData = (String[])tbl.get( listOverFlow[i][int0] );
            int intSub = Integer.parseInt( listOverFlow[i][int1] );


            if( listData[intSub]==V_NULL_STRING ||  listData[intSub].length() <= 0 ){ //2003.07.31
                continue;
            }

            //符号有無チェック
            checkData = Math.abs( Integer.parseInt( listData[intSub] ) ) + V_EMPTY_STRING;

//2004/07/06 CHG@N.SAKASHITA (GEC16-C-012-411)
            //オーバーフローチェック
//          if( checkData.length() > 5 ){
            if( checkData.length() > 7 ){
                // -2をリターン
                return intM2;
            }
        }


// 2003/12/22 CHG@S.SEIMURA (080-111)
// 2005.02.15   Chg Start K.Sato(GEC16-C-143-005)
// 配列2番目のインデックス値はIRingiItemKeisuで定義している定数を使用する
        // オーバーフローチェック配列編7桁
        // 配列データ
        String[][] listOverFlow7Keta = {

            // 本件後引当状況 規定担保
            { F_HIKIATE_KITEITI_TOT, V_KEISU_KTITNP_TOT_BAP + "",           "0" },
            { F_HIKIATE_KITEITI_TOT, V_KEISU_STRCRE_BAP + "",               "0" },
            { F_HIKIATE_JIKA_TOT, V_KEISU_KTITNP_TOT_BAP + "",              "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_STOT_BAP + "",          "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_STOT_BAP + "",       "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_YOKIN_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_YOKIN_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_SYOTE_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_SYOTE_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_TANTE_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_TANTE_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_YUSYO_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_YUSYO_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_KYOHO_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_KYOHO_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_HOSYO_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_HOSYO_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_IPANLC_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_IPANLC_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_TEGATAHO_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_TEGATAHO_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_IKKATU_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_IKKATU_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_YUTNP_SONOTA_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_YUTNP_SONOTA_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_STOT_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_STOT_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_YUSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_YUSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_HOSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_HOSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP + "",     "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP + "",  "0" },
/* YC20218-02 Start */
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP + "", "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP + "", "0" },
/* YC20218-02 End */
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_FUDO_NE_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_FUDO_NE_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_DFHOSYO_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_DFHOSYO_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_IPNTNP_SONOTA_BAP + "",       "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_IPNTNP_SONOTA_BAP + "",    "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_SNTTNP_STOT_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_SNTTNP_STOT_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_SNTTNP_YUSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_SNTTNP_YUSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_SNTTNP_HOSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_SNTTNP_HOSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_SNTTNP_DHCDC_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_SNTTNP_DHCDC_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTI_SNTTNP_SONOTA_BAP + "",       "0" }, { F_HIKIATE_JIKA, V_KEISU_KTI_SNTTNP_SONOTA_BAP + "",    "0" },

            // 本件後引当状況 規定外担保
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_TOT_BAP + "",                "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_TOT_BAP + "",             "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_YUTNP_STOT_BAP + "",         "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_YUTNP_STOT_BAP + "",      "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_YUTNP_YOKIN_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_YUTNP_YOKIN_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_YUTNP_YUSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_YUTNP_YUSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_YUTNP_HOSYO_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_YUTNP_HOSYO_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_YUTNP_SONOTA_BAP + "",       "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_YUTNP_SONOTA_BAP + "",    "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_STOT_BAP + "",        "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_STOT_BAP + "",     "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_YUSYO_BAP + "",       "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_YUSYO_BAP + "",    "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_HOSYO_BAP + "",       "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_HOSYO_BAP + "",    "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP + "",    "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP + "", "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP + "",     "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP + "",  "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_NYUKYO_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_NYUKYO_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_SAIKEN_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_SAIKEN_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_IPNTNP_SONOTA_BAP + "",      "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_IPNTNP_SONOTA_BAP + "",   "0" },
            { F_HIKIATE_KITEITI,  V_KEISU_KTIG_SONOTA_BAP + "",             "0" }, { F_HIKIATE_JIKA, V_KEISU_KTIG_SONOTA_BAP + "",          "0" },

        };
// 2005.02.15   Chg End K.Sato(GEC16-C-143-005)

        for(int i = 0; i < listOverFlow7Keta.length; i++){
            String checkData = new String();
            if( tbl.containsKey( listOverFlow7Keta[i][int0] ) == false ){
                continue;
            }

            //DBHashtableから配列データを取得
            String[] listData = (String[])tbl.get( listOverFlow7Keta[i][int0] );
            int intSub = Integer.parseInt( listOverFlow7Keta[i][int1] );


            if( listData[intSub] == V_NULL_STRING ||  listData[intSub].length() <= 0 ){ //2003.07.31
                continue;
            }


// 2005.02.25   Chg Start K.Sato(GEC16-C-143-005)
// 数値文字列をString型⇒Long型⇒String型に変換し、チェックする。
            //符号有無チェック
//          checkData = Math.abs( Integer.parseInt( listData[intSub] ) ) + V_EMPTY_STRING;
            checkData = Math.abs( Long.parseLong( listData[intSub] ) ) + V_EMPTY_STRING;
// 2005.02.25   Chg End K.Sato(GEC16-C-143-005)

            //オーバーフローチェック
            if( checkData.length() > 7 ){
                // -2をリターン
                return intM2;
            }
        }

        //正常終了
        return int0;

    }

    /**
     * <DL>
     * <DL><b>ホスト取得データ編集とＤＢデータ取得</b></DL>
     * </DL>
     * ＤＢクラスから外部取得項目を取得し、
     * 共有情報中にて渡されたホストからの取得データと合わせて
     * 出力形式に編集を行う
     * @param   Hashtable   hstComBasket    共有情報
     */
    public void setHostAndDbData(Hashtable hstComBasket)
        throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException, WACSApplException {


        try {

            /*
             * ＤＢから計数の情報を取得
             */

            // 共有情報からキー項目を取得
            Hashtable hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            // 店ＣＩＦを一時保存
            String strBrno = (String)hstKey.get(F_BRNO);
            String strTriskno = (String)hstKey.get(F_TRISKNO);


            // 禀議計数ＤＢクラスのインスタンスを取得する
            RLRRG004_B01_DB keisuDB = new RLRRG004_B01_DB(folder, dbcon, dbparam);


            // 外部管理下のデータを取得
            // キーは店ＣＩＦ
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
            hstKey.put(F_BRNO,    strBrno);
            hstKey.put(F_TRISKNO, strTriskno);
            hstComBasket.put(K_KEY_DATA,hstKey);


            keisuDB.getOutsideData(hstComBasket);
            // 戻り値判定
            int intRc = ( (Integer)hstComBasket.get(K_RETURN) ).intValue();
            if ( intRc == IRingiDB.RC_DAIHYOU_TENCIF_NG ) {
                return;
            }


            // ホストとＤＢの本件後引当項目を合わせる
            Hashtable hstDB   = (Hashtable)hstComBasket.get(K_DB_DATA);
            Hashtable hstHOST = (Hashtable)hstComBasket.get(K_HOST_DATA);
            String[] strDbKitei   = (String[])hstDB.get(F_HIKIATE_KITEITI);
            String[] strHostKitei = (String[])hstHOST.get(F_HIKIATE_KITEITI);
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start
// 規定担保補正値の設定
            String[] strDbKiteiTot   = (String[])hstDB.get(F_HIKIATE_KITEITI_TOT);
            String[] strHostKiteiTot = (String[])hstHOST.get(F_HIKIATE_KITEITI_TOT);
            String[] strDbJikaTot    = (String[])hstDB.get(F_HIKIATE_JIKA_TOT);
            String[] strHostJikaTot  = (String[])hstHOST.get(F_HIKIATE_JIKA_TOT);
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end
            strDbKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP]  = strHostKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP];
            strDbKitei[V_KEISU_KTI_YUTNP_TANTE_BAP]  = strHostKitei[V_KEISU_KTI_YUTNP_TANTE_BAP];
            strDbKitei[V_KEISU_KTI_YUTNP_IPANLC_BAP] = strHostKitei[V_KEISU_KTI_YUTNP_IPANLC_BAP];
            strDbKitei[V_KEISU_KTI_YUTNP_TEGATAHO_BAP] = strHostKitei[V_KEISU_KTI_YUTNP_TEGATAHO_BAP];
            strDbKitei[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP] = strHostKitei[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP];
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start
// ＤＢデータから取得した規定担保補正値がホストデータで上書かれないよう
// ホストデータ側に設定しておく
            strHostKiteiTot[V_KEISU_KTITNP_HOSCH_BAP] = strDbKiteiTot[V_KEISU_KTITNP_HOSCH_BAP];
            strHostJikaTot[V_KEISU_KTITNP_HOSCH_BAP]  = strDbJikaTot[V_KEISU_KTITNP_HOSCH_BAP];
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end

// 2005.02.14   Add Start K.Sato(GEC16-C-143-005)
// 協会保証の追加
            strDbKitei[V_KEISU_KTI_YUTNP_KYOHO_BAP] = strHostKitei[V_KEISU_KTI_YUTNP_KYOHO_BAP];
// 2005.02.14   Add End K.Sato(GEC16-C-143-005)
            hstHOST.put(F_HIKIATE_KITEITI, strDbKitei);
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 start
            hstHOST.put(F_HIKIATE_KITEITI_TOT, strHostKiteiTot);
            hstHOST.put(F_HIKIATE_JIKA_TOT, strHostJikaTot);
// 2009/06/23 ADD@R.Matsumura GEC20-C-059 end

/* YC20218-02 Start */
            // ホストとＤＢの与信状況項目を合わせる
            String[] strDbMendZan    = (String[])hstDB.get(F_MEND_ZAN);
            String[] strDbHonafZan   = (String[])hstDB.get(F_HONAF_ZAN);
            String[] strDbJisksn     = (String[])hstDB.get(F_JISKSN);

            hstHOST.put(F_MEND_ZAN ,strDbMendZan);
            hstHOST.put(F_HONAF_ZAN ,strDbHonafZan);
            hstHOST.put(F_JISKSN ,strDbJisksn);
/* YC20218-02 End */

            /*
             * 出力形式を同じにするために、ホストから取得したデータを
             * ＤＢクラスのレスポンスにコピーする
             */
            setHashToHash(hstHOST, hstDB);
            hstComBasket.put(K_HOST_DATA, hstHOST);
            hstComBasket.put(K_DB_DATA, hstDB);


            /*
             * 補正値を使用した計算を行う
             */
            computeYosin(hstComBasket);
            computeKokyakuShutoku(hstComBasket);    // 2003/04/17 ADD@S.SEIMURA
            computeKokyaku(hstComBasket);
            computeKokyaku2(hstComBasket);          // 2009/06/23 ADD@R.Matsumura GEC20-C-059
            computeHozen(hstComBasket);             // 2011/11/18 ADD@M.Hayashi GEC23-C-051


        } catch( com.ibm.jp.wacs.db.WACSDBException e ) {
            throw e;
        } catch( WACSSysException e ) {
            throw e;
        } catch( WACSApplException e) {
            throw e;
        } finally {
        }

        return ;



    }



    /**
     * <DL>
     * <DL><b>配列データ取得</b></DL>
     * </DL>
     * 画面から送られた配列型データを取得し、
     * 指定された配列に出力する
     * @param   CraftsDataBean  ibean   入力ビーン
     * @param   Hashtable       hstTbl  配列データ出力先のハッシュテーブル
     */
    public void setInArrayToHash( CraftsDataBean ibean, Hashtable hstTbl ) {

        /*
         * 一般与信
         */

        // 科目･適用
// GEC294-C-004 S
//      hstTbl.put( F_KMK_RMT, ibean.getStringArray(F_KMK_RMT) );
        // 禀議査定番号を含まない科目･適用をF_KMK_RMT_LISTに設定
        String[] strKmkrmt   = ibean.getStringArray(F_KMK_RMT);
        String[] strKmkrmtlist   = ibean.getStringArray(F_KMK_RMT_LIST);
        for(int i = 0; i < strKmkrmtlist.length; i++){
            if (i < F_KMK_RMT_START || F_KMK_RMT_END < i){
                strKmkrmtlist[i] = strKmkrmt[i];
            }
        }
        hstTbl.put( F_KMK_RMT_LIST, strKmkrmtlist );
// GEC294-C-004 E

        // 一般与信状況・限度算入与信合計・指定月末残高
        hstTbl.put( F_MEND_ZAN_TOT,
                    ibean.getStringArray(F_MEND_ZAN_TOT) );

        // 一般与信状況・限度算入与信合計・極度額
        hstTbl.put( F_LMT_TOT,
                    ibean.getStringArray(F_LMT_TOT) );

        // 一般与信状況・限度算入与信合計・当月増減
        hstTbl.put( F_IPNYSNDLTZGG_TOT,
                    ibean.getStringArray(F_IPNYSNDLTZGG_TOT) );

        // 一般与信状況・限度算入与信合計・本件後残高
        hstTbl.put( F_HONAF_ZAN_TOT,
                    ibean.getStringArray(F_HONAF_ZAN_TOT) );

        // 一般与信状況・限度算入与信合計・実勢現在残
        hstTbl.put( F_JISKSN_TOT,
                    ibean.getStringArray(F_JISKSN_TOT) );


        // 期日
        hstTbl.put( F_KBI, ibean.getStringArray(F_KBI) );

        // 利率
        hstTbl.put( F_RT, ibean.getStringArray(F_RT) );

        // 指定月末残高
        hstTbl.put( F_MEND_ZAN, ibean.getStringArray(F_MEND_ZAN) );

        // アスタリスク
        hstTbl.put( F_GSNLMT_HJ, ibean.getStringArray(F_GSNLMT_HJ) );

        // 極度額
        hstTbl.put( F_LMT, ibean.getStringArray(F_LMT) );

        // 当月増減額
        hstTbl.put( F_IPNYSNDLTZGG, ibean.getStringArray(F_IPNYSNDLTZGG) );

        // 本件後残高
        hstTbl.put( F_HONAF_ZAN, ibean.getStringArray(F_HONAF_ZAN) );

        // 実勢現在残高
        hstTbl.put( F_JISKSN, ibean.getStringArray(F_JISKSN) );

        // 補正値
        hstTbl.put( F_HOSCH, ibean.getStringArray(F_HOSCH) );
// GEC294-C-004 S
        // 禀議査定番号
        hstTbl.put( F_RSNO_LIST, ibean.getStringArray(F_RSNO_LIST) );
// GEC294-C-004 E


        /*
         * 本件後引当状況
         */

        // 本件後引当状況・規定値・合計
        hstTbl.put( F_HIKIATE_KITEITI_TOT,
                    ibean.getStringArray(F_HIKIATE_KITEITI_TOT) );

        // 本件後引当状況・時価ベース・合計
        hstTbl.put( F_HIKIATE_JIKA_TOT,
                    ibean.getStringArray(F_HIKIATE_JIKA_TOT) );

        // 本件後引当状況・規定値
        hstTbl.put( F_HIKIATE_KITEITI,
                    ibean.getStringArray(F_HIKIATE_KITEITI) );

        // 本件後引当状況・時価ベース
        hstTbl.put( F_HIKIATE_JIKA,
                    ibean.getStringArray(F_HIKIATE_JIKA) );

        // 保証人
        hstTbl.put( F_HSN_NM, ibean.getStringArray(F_HSN_NM) );

    }





    /**
     * <DL>
     * <DL><b>与信状況 科目･適用固定項目を挿入する。</b></DL>
     * </DL>
     * @param   Hashtable       hstComBasket   共有情報
     */
    public void getKamokuData( Hashtable hstComBasket ) {

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start
// その他一般与信を追加、""⇒特定与信に変更
// 2006/12/07 ChgStart M.Suzuki(GEC18-C-014)
// ラベル名D/P・D/A⇒D/P・D/A・輸出OA,その他与信⇒特定与信に変更

// 2005/02/08 ChgStart T.Saito(GEC16-C-143-005)
        String[] kmk_yosin_labal = {
// 2010/12/27 CHG@S.Fujimoto GEC22-C-019 Start
//                  "貸付金・商手合計",
                    "貸付金・割引合計",
// 2010/12/27 CHG@S.Fujimoto GEC22-C-019 End
                    "（内円貨）",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "外為与信合計",
                    "指定外L/C",
                    "D/P・D/A・輸出OA",
                    "外貨小切手",
                    "輸出(小計)",
                    "貸出(輸出)",
                    "輸入L/C",
                    "ﾕｰｻﾞﾝｽ",
                    "L/G",
                    "輸入(小計)",
                    "貸出(輸入)",
                    "故障指定L/C",
                    "ﾕｰｻﾞﾝｽｼﾌﾄ外貨",
                    "支払承諾合計",
                    "支承・一般",
                    "支承・一般外為",
                    "内他行保証支払承諾",
                    "代理貸付",
                    "私募債",
                    "協保貸",
                    "その他一般与信",
                    "限度算入ﾛｰﾝ合計",
/* YC20218-02 Start */
                    "内 HL信用不算入",
/* YC20218-02 End */
                    "オンバランス合計",
                    "オフバランス合計",
                    "限度不算入与信合計",
//                  "協保貸",
                    "年金転貸",
                    "指定L/C小切手",
                    "L/G",
                    "一般与信合計",
                    "特定与信合計",
//                  "",
                    "特定与信",
                    "" } ;
// 2005/02/08 ChgEnd T.Saito(GEC16-C-143-005)
// 2006/12/07 ChgEnd M.Suzuki(GEC18-C-014)
// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end

        Hashtable hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

        // DBより取得した一般与信の科目名称を挿入する
        String[] strKamoku = (String[])hstDB.get(F_KMK_RMT);

        if( strKamoku != null ) {

            for( int i = 0; i < strKamoku.length; i++ ) {

// 2009/06/23 CHG@R.Matsumura GEC20-C-059 start
// 対象から特定与信の位置をはずす
//              if( ( V_KEISU_KASHISHO_MEISAI1_BAP <= i && i <= V_KEISU_KASHISHO_MEISAI12_BAP ) || ( V_KEISU_SONOTA_YSN1_BAP <= i ) ) {
                if( ( V_KEISU_KASHISHO_MEISAI1_BAP <= i && i <= V_KEISU_KASHISHO_MEISAI12_BAP ) || ( V_KEISU_SONOTA_YSN2_BAP <= i ) ) {
// 2009/06/23 CHG@R.Matsumura GEC20-C-059 end
                    kmk_yosin_labal[i] = strKamoku[i];
                }

            }
        }

        hstDB.put(IRingiItemKeisu.F_KMK_RMT_TOT, kmk_rmt_tot_label);
        hstDB.put(IRingiItemKeisu.F_KMK_RMT, kmk_yosin_labal);
        hstDB.put(F_KMK_HIKIATE_TOT, kmk_hikiate_tot_label);
        hstDB.put(F_KMK_HIKIATE, kmk_hikiate_label);

        hstComBasket.put(K_DB_DATA, hstDB);

    }

// 2005/02/04 AddStart T.Saito(GEC16-C-143-005)

    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   DB形式から画面形式へ配列の内容を入れ替える。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param      String[]    strDbArrayBef      変換前配列格納用
     *   @return     String[]    strDispArrayAft    変更後配列格納用
     */
    public static String[] chgYosinDbToDisp (String[] strDbArrayBef) {

        // 変更後配列格納領域
        String[] strDispArrayAft = new String[ intDbBapCnvKeisuArr.length ];

        //DB形式から画面形式への変換処理
        for(int i = 0 ; i < intDbBapCnvKeisuArr.length ; i++ ){
            strDispArrayAft[ intDbBapCnvKeisuArr[i][0] ] = strDbArrayBef[ intDbBapCnvKeisuArr[i][1] ];
        }
        return strDispArrayAft;
    }

    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   画面形式からDB形式へ配列の内容を入れ替える。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param      String[]    strDispArrayBef    変換前配列格納用
     *   @return     String[]    strDbArrayAft    変更後配列格納用
     */
    public static String[] chgYosinDispToDb (String[] strDispArrayBef) {

        // 変更後配列格納領域
        String[] strDbArrayAft = new String[ intDbBapCnvKeisuArr.length ];

        // 画面形式からDB形式への変換処理
        for(int i = 0 ; i < intDbBapCnvKeisuArr.length ; i++ ){
            strDbArrayAft[ intDbBapCnvKeisuArr[i][1] ] = strDispArrayBef[ intDbBapCnvKeisuArr[i][0] ];
        }
        return strDbArrayAft;
    }
// 2005/02/04 AddEnd T.Saito(GEC16-C-143-005)

//2009/06/23 ADD@R.Matsumura GEC20-C-059 start
    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数画面で計算ボタンが押された際に、<BR>
     *   本件後保全状況欄は差分計算を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable  hstTbl    画面入出力データ(ハッシュ)
     *   @param  Hashtable  hstComBasket   共有情報(ハッシュ)
     */
    public void computeKokyakuSabunKeisan(Hashtable hstTbl, Hashtable hstComBasket) {

        try{

            Hashtable dbData = (Hashtable)hstComBasket.get( K_DB_DATA ) ;

            String[] dispGokeiKitei = (String[])hstTbl.get( F_HIKIATE_KITEITI_TOT ) ;
            String[] dispGokeiJika  = (String[])hstTbl.get( F_HIKIATE_JIKA_TOT    ) ;
            String[] dispKitei      = (String[])hstTbl.get( F_HIKIATE_KITEITI     ) ;
            String[] dispJika       = (String[])hstTbl.get( F_HIKIATE_JIKA        ) ;


            //差分の格納領域
            String[] sabunKitei   = new String[V_KEISU_HOZEN_ARR_NUM];
            String[] sabunJika    = new String[V_KEISU_HOZEN_ARR_NUM];
            String[] sabunGokeiKitei   = new String[V_KEISU_HOZEN_TOT_ARR_NUM];
            String[] sabunGokeiJika    = new String[V_KEISU_HOZEN_TOT_ARR_NUM];


            // 画面から入力された情報を、新しい配列にコピー
            System.arraycopy(dispKitei,  0, sabunKitei,  0, dispKitei.length );
            System.arraycopy(dispJika,  0, sabunJika,  0, dispJika.length );
            System.arraycopy(dispGokeiKitei,  0, sabunGokeiKitei,  0, dispGokeiKitei.length );
            System.arraycopy(dispGokeiJika,  0, sabunGokeiJika,  0, dispGokeiJika.length );


            //DBから取得したデータ領域
            String[] dbGokeiKitei   = (String[])dbData.get( F_HIKIATE_KITEITI_TOT   ) ;
            String[] dbGokeiJika    = (String[])dbData.get( F_HIKIATE_JIKA_TOT      ) ;
            String[] dbKitei        = (String[])dbData.get( F_HIKIATE_KITEITI       ) ;
            String[] dbJika         = (String[])dbData.get( F_HIKIATE_JIKA          ) ;
            String   strStrcreTshoTot   = (String)dbData.get( F_STRCRE_TSHO_TOT     ) ;

            long dataValue2 = 0 ;


            /*
            * 計算結果とＤＢに登録されているデータとの差分を求める
            */


            // 本件後保全状況（規定値）規定担保合計・規定担保補正値・裸与信以外
            for(int i = 0; i < V_KEISU_HOZEN_ARR_NUM; i++) {

                if( dispKitei[i].length() != 0 ||
                    dbKitei[i].length() != 0
                ){
                    dataValue2 = getDataValue2(dispKitei[i]) -
                                                getDataValue2(dbKitei[i]);
                    sabunKitei[i] = Long.toString(dataValue2);
                }else{
                    sabunKitei[i] = V_EMPTY_STRING;
                }

            }


            // 本件後保全状況（時価ベース）規定担保合計・規定担保補正値・裸与信以外
            for(int i = 0; i < V_KEISU_HOZEN_ARR_NUM; i++) {

                if( dispJika[i].length() != 0 ||
                    dbJika[i].length() != 0
                ){
                    dataValue2 = getDataValue2(dispJika[i]) -
                                                getDataValue2(dbJika[i]);
                    sabunJika[i] = Long.toString(dataValue2);
                }else{
                    sabunJika[i] = V_EMPTY_STRING;
                }

            }


            // 本件後保全状況合計欄（規定値）
            for(int i = 0; i < V_KEISU_HOZEN_TOT_ARR_NUM; i++) {

                // 規定担保補正値は計算対象外
                if( i != V_KEISU_KTITNP_HOSCH_BAP ) {

                    if( dispGokeiKitei[i].length() != 0 ||
                        dbGokeiKitei[i].length() != 0
                    ){
                        dataValue2 = getDataValue2(dispGokeiKitei[i]) -
                                                getDataValue2(dbGokeiKitei[i]);
                        sabunGokeiKitei[i] = Long.toString(dataValue2);
                    }else{
                        sabunGokeiKitei[i] = V_EMPTY_STRING;
                    }

                }
            }


            // 本件後保全状況合計欄（時価ベース）
            for(int i = 0; i < V_KEISU_HOZEN_TOT_ARR_NUM; i++) {

                // 規定担保補正値は計算対象外
                if( i != V_KEISU_KTITNP_HOSCH_BAP ) {

                    if( dispGokeiJika[i].length() != 0 ||
                        dbGokeiJika[i].length() != 0
                    ){
                        dataValue2 = getDataValue2(dispGokeiJika[i]) -
                                                getDataValue2(dbGokeiJika[i]);
                        sabunGokeiJika[i] = Long.toString(dataValue2);
                    }else{
                        sabunGokeiJika[i] = V_EMPTY_STRING;
                    }

                }
            }


            /* --------------------------------------------------------
             * ここまでがＤＢに登録されている項目との差分計算
             * --------------------------------------------------------
             */


            /*
             * 小計項目の計算
             * 計算された差分を使用して、小計項目の差分を算出する
            */


            /*
            * 規定・優良小計の計算
            *
            */

            // 規定・優良小計（規定値）
            if( sabunKitei[V_KEISU_KTI_YUTNP_YOKIN_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_TANTE_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_YUSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_KYOHO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_HOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_IPANLC_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_TEGATAHO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_IKKATU_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_YUTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_YOKIN_BAP] )       +   // [規定・優良・預金（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_SYOTE_BAP] )       +   // [規定・優良・商手（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_TANTE_BAP] )       +   // [規定・優良・担手（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_YUSYO_BAP] )       +   // [規定・優良・有証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_KYOHO_BAP] )       +   // [規定・優良・協会保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_HOSYO_BAP] )       +   // [規定・優良・保証（除協会）（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_IPANLC_BAP] )      +   // [規定・優良・一般L/C（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_TEGATAHO_BAP] )    +   // [規定・優良・手形保険（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_IKKATU_BAP] )      +   // [規定・優良・一括支払（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_SONOTA_BAP] ) ;        // [規定・優良・その他（規定値）]
                sabunKitei[V_KEISU_KTI_YUTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTI_YUTNP_STOT_BAP] = V_EMPTY_STRING;
            }

            // 規定・優良小計（時価ベース）
            if( sabunJika[V_KEISU_KTI_YUTNP_YOKIN_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_SYOTE_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_TANTE_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_YUSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_KYOHO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_HOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_IPANLC_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_TEGATAHO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_IKKATU_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_YUTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_YOKIN_BAP] )        +   // [規定・優良・預金（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_SYOTE_BAP] )        +   // [規定・優良・商手（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_TANTE_BAP] )        +   // [規定・優良・担手（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_YUSYO_BAP] )        +   // [規定・優良・有証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_KYOHO_BAP] )        +   // [規定・優良・協会保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_HOSYO_BAP] )        +   // [規定・優良・保証（除協会）（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_IPANLC_BAP] )       +   // [規定・優良・一般L/C（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_TEGATAHO_BAP] )     +   // [規定・優良・手形保険（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_IKKATU_BAP] )       +   // [規定・優良・一括支払（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_SONOTA_BAP] ) ;         // [規定・優良・その他（時価ベース）]
                sabunJika[V_KEISU_KTI_YUTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTI_YUTNP_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 規定・一般小計の計算
             *
             */

            // 規定・一般小計（規定値）
            if( sabunKitei[V_KEISU_KTI_IPNTNP_YUSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_HOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_YUSYO_BAP]  )     +   // [規定・一般・有証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_HOSYO_BAP] )      +   // [規定・一般・保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] )   +   // [規定・一般・不動産（抵）（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP] )    +   // [規定・一般・不動産（根）（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP] )    +   // [規定・一般・Ｄ／Ｆ保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_SONOTA_BAP] ) ;       // [規定・一般・その他（規定値）]
                sabunKitei[V_KEISU_KTI_IPNTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTI_IPNTNP_STOT_BAP] = V_EMPTY_STRING;
            }

            // 規定・一般小計（時価ベース）
            if( sabunJika[V_KEISU_KTI_IPNTNP_YUSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_HOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_YUSYO_BAP] )       +   // [規定・一般・有証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_HOSYO_BAP] )       +   // [規定・一般・保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP] )    +   // [規定・一般・不動産（抵）（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_FUDO_NE_BAP] )     +   // [規定・その他小計（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_DFHOSYO_BAP] )     +   // [規定・一般・Ｄ／Ｆ保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_SONOTA_BAP] ) ;        // [規定・一般・その他（時価ベース）]
                sabunJika[V_KEISU_KTI_IPNTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTI_IPNTNP_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 規定・その他小計の計算
             *
             */

            // 規定・その他小計（規定値）
            if( sabunKitei[V_KEISU_KTI_SNTTNP_YUSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_SNTTNP_HOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_SNTTNP_DHCDC_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_SNTTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTI_SNTTNP_YUSYO_BAP] )      +   // [規定・その他・有証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_SNTTNP_HOSYO_BAP] )      +   // [規定・その他・保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_SNTTNP_DHCDC_BAP] )      +   // [規定・その他・ＤＨＣ・ＤＣ保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_SNTTNP_SONOTA_BAP] ) ;       // [規定・その他・その他（規定値）]
                sabunKitei[V_KEISU_KTI_SNTTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTI_SNTTNP_STOT_BAP] = V_EMPTY_STRING;
            }

            // 規定・その他小計（時価ベース）
            if( sabunJika[V_KEISU_KTI_SNTTNP_YUSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_SNTTNP_HOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_SNTTNP_DHCDC_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_SNTTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTI_SNTTNP_YUSYO_BAP] )       +   // [規定・その他・有証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_SNTTNP_HOSYO_BAP] )       +   // [規定・その他・保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_SNTTNP_DHCDC_BAP] )       +   // [規定・その他・ＤＨＣ・ＤＣ保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_SNTTNP_SONOTA_BAP]) ;         // [規定・その他・その他（時価ベース）]
                sabunJika[V_KEISU_KTI_SNTTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTI_SNTTNP_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 規定外・優良小計の計算
             *
             */

            // 規定外・優良小計（規定値）
            if( sabunKitei[V_KEISU_KTIG_YUTNP_YOKIN_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_YUTNP_YUSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_YUTNP_HOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_YUTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTIG_YUTNP_YOKIN_BAP] )      +   // [規定外・優良・預金（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_YUTNP_YUSYO_BAP] )      +   // [規定外・優良・有証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_YUTNP_HOSYO_BAP] )      +   // [規定外・優良・保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_YUTNP_SONOTA_BAP] ) ;       // [規定外・優良・その他（規定値）]
                sabunKitei[V_KEISU_KTIG_YUTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTIG_YUTNP_STOT_BAP] = V_EMPTY_STRING;
            }

            // 規定外・優良小計（時価ベース）
            if( sabunJika[V_KEISU_KTIG_YUTNP_YOKIN_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_YUTNP_YUSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_YUTNP_HOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_YUTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTIG_YUTNP_YOKIN_BAP] )       +   // [規定外・優良・預金（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_YUTNP_YUSYO_BAP] )       +   // [規定外・優良・有証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_YUTNP_HOSYO_BAP] )       +   // [規定外・優良・保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_YUTNP_SONOTA_BAP] ) ;        // [規定外・優良・その他（時価ベース）]
                sabunJika[V_KEISU_KTIG_YUTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTIG_YUTNP_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 規定外・一般小計の計算
             *
             */

            // 規定外・一般小計（規定値）
            if( sabunKitei[V_KEISU_KTIG_IPNTNP_YUSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_HOSYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_YUSYO_BAP] )     +   // [規定外・一般・有証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_HOSYO_BAP] )     +   // [規定外・一般・保証（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP] )  +   // [規定外・一般・不動産（抵）（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP] )   +   // [規定外・一般・不動産（根）（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP] )    +   // [規定外・一般・入居保証金（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP] )    +   // [規定外・一般・債券（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_SONOTA_BAP] ) ;      // [規定外・一般・その他（規定値）]
                sabunKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP] = V_EMPTY_STRING;
            }

            // 規定外・一般小計（時価ベース）
            if( sabunJika[V_KEISU_KTIG_IPNTNP_YUSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_HOSYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_YUSYO_BAP] )      +   // [規定外・一般・有証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_HOSYO_BAP] )      +   // [規定外・一般・保証（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP] )   +   // [規定外・一般・不動産（抵）（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP] )    +   // [規定外・一般・不動産（根）（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_NYUKYO_BAP] )     +   // [規定外・一般・入居保証金（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_SAIKEN_BAP] )     +   // [規定外・一般・債券（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_SONOTA_BAP] ) ;       // [規定外・一般・その他（時価ベース）]
                sabunJika[V_KEISU_KTIG_IPNTNP_STOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTIG_IPNTNP_STOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 合計項目の計算
             * 計算された小計を使用して、合計項目の差分を算出する
            */


            /*
             * 規定担保合計の計算式
             *
             */

            // 規定担保合計（規定値）
            if( sabunKitei[V_KEISU_KTI_YUTNP_STOT_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_IPNTNP_STOT_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTI_SNTTNP_STOT_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTI_YUTNP_STOT_BAP] )        +   // [規定・優良小計（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_IPNTNP_STOT_BAP] )       +   // [規定・一般小計（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTI_SNTTNP_STOT_BAP] ) ;         // [規定・その他小計（規定値）]
                sabunGokeiKitei[V_KEISU_KTITNP_TOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunGokeiKitei[V_KEISU_KTITNP_TOT_BAP] = V_EMPTY_STRING;
            }

            // 規定担保合計（時価ベース）
            if( sabunJika[V_KEISU_KTI_YUTNP_STOT_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_IPNTNP_STOT_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTI_SNTTNP_STOT_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTI_YUTNP_STOT_BAP] )     +   // [規定・優良小計（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_IPNTNP_STOT_BAP] )    +   // [規定・一般小計（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTI_SNTTNP_STOT_BAP] ) ;      // [規定・その他小計（時価ベース）]
                sabunGokeiJika[V_KEISU_KTITNP_TOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunGokeiJika[V_KEISU_KTITNP_TOT_BAP] = V_EMPTY_STRING;
            }


            /*
             * 規定外担保合計の計算
             *
             */

            // 規定外担保合計（規定値）
            if( sabunKitei[V_KEISU_KTIG_YUTNP_STOT_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP].length() != 0 ||
                sabunKitei[V_KEISU_KTIG_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunKitei[V_KEISU_KTIG_YUTNP_STOT_BAP] )       +   // [規定外・優良小計（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_IPNTNP_STOT_BAP] )      +   // [規定外・一般小計（規定値）]
                             getDataValue2( sabunKitei[V_KEISU_KTIG_SONOTA_BAP]) ;              // [規定外・その他（規定値）]
                sabunKitei[V_KEISU_KTIG_TOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunKitei[V_KEISU_KTIG_TOT_BAP] = V_EMPTY_STRING;
            }

            // 規定外担保合計（時価ベース）
            if( sabunJika[V_KEISU_KTIG_YUTNP_STOT_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_IPNTNP_STOT_BAP].length() != 0 ||
                sabunJika[V_KEISU_KTIG_SONOTA_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( sabunJika[V_KEISU_KTIG_YUTNP_STOT_BAP] )        +   // [規定外・優良小計（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_IPNTNP_STOT_BAP] )       +   // [規定外・一般小計（時価ベース）]
                             getDataValue2( sabunJika[V_KEISU_KTIG_SONOTA_BAP] ) ;              // [規定外・その他（時価ベース）]
                sabunJika[V_KEISU_KTIG_TOT_BAP] = Long.toString(dataValue2);
            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                sabunJika[V_KEISU_KTIG_TOT_BAP] = V_EMPTY_STRING;
            }


            /*-------------------------------------------------------------------------
            ここまでが合計を含めた差分計算
            --------------------------------------------------------------------------*/

            /*
             * ここから、ＤＢのデータと差分データを足したものを作成する
             */


            // 本件後保全状況（規定値）規定担保合計・規定担保補正値・裸与信以外
            for(int i = 0; i < V_KEISU_HOZEN_ARR_NUM; i++) {

                if( sabunKitei[i].length() != 0 ||
                    dbKitei[i].length() != 0
                ){
                    dataValue2 = getDataValue2(sabunKitei[i]) +
                                                getDataValue2(dbKitei[i]);
                    dispKitei[i] = Long.toString(dataValue2);
                }else{
                    dispKitei[i] = V_EMPTY_STRING;
                }

            }


            // 本件後保全状況（時価ベース）規定担保合計・規定担保補正値・裸与信以外
            for(int i = 0; i < V_KEISU_HOZEN_ARR_NUM; i++) {

                if( sabunJika[i].length() != 0 ||
                    dbJika[i].length() != 0
                ){
                    dataValue2 = getDataValue2(sabunJika[i]) +
                                                getDataValue(dbJika[i]);
                    dispJika[i] = Long.toString(dataValue2);
                }else{
                    dispJika[i] = V_EMPTY_STRING;
                }

            }


            // 本件後保全状況合計欄（規定値）
            for(int i = 0; i < V_KEISU_HOZEN_TOT_ARR_NUM; i++) {

                // 規定担保補正値は計算対象外
                if( i != V_KEISU_KTITNP_HOSCH_BAP ) {

                    if( sabunGokeiKitei[i].length() != 0 ||
                        dbGokeiKitei[i].length() != 0
                    ){
                        dataValue2 = getDataValue2(sabunGokeiKitei[i]) +
                                                getDataValue2(dbGokeiKitei[i]);
                        dispGokeiKitei[i] = Long.toString(dataValue2);
                    }else{
                        dispGokeiKitei[i] = V_EMPTY_STRING;
                    }

                }
            }


            // 本件後保全状況合計欄（時価ベース）
            for(int i = 0; i < V_KEISU_HOZEN_TOT_ARR_NUM; i++) {

                // 規定担保補正値は計算対象外
                if( i != V_KEISU_KTITNP_HOSCH_BAP ) {

                    if( sabunGokeiJika[i].length() != 0 ||
                        dbGokeiJika[i].length() != 0
                    ){
                        dataValue2 = getDataValue2(sabunGokeiJika[i]) +
                                                getDataValue2(dbGokeiJika[i]);
                        dispGokeiJika[i] = Long.toString(dataValue2);
                    }else{
                        dispGokeiJika[i] = V_EMPTY_STRING;
                    }

                }
            }


            /*
             * ここまで、ＤＢのデータと差分データを足したものの作成
             */


            /*
             * 裸与信の計算
             *
             */

            // 裸与信（規定値）計数情報（一般与信）
/* YC20218-02 Start */
//          String[] strYosin = (String[])hstTbl.get(F_HONAF_ZAN_TOT);
//          if( strYosin[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||
//              strStrcreTshoTot.length() != 0 ||
//              dispGokeiKitei[V_KEISU_KTITNP_TOT_BAP].length() != 0
//          ){
//              dataValue2 = getDataValue2( strYosin[V_KEISU_GENDOSAN_TOT_BAP] ) -      // [限度算入与信合計（本件後残高）]
//                           getDataValue2( strStrcreTshoTot ) -                        // [裸与信対象与信合計]
//                           getDataValue2( dispGokeiKitei[V_KEISU_KTITNP_TOT_BAP] ) ;  // [規定担保計（規定値）]

//              if ( dataValue2 < 0 ) {
//                  dataValue2 = 0 + getDataValue2( strStrcreTshoTot );
//              }else{
//                  dataValue2 = dataValue2 + getDataValue2( strStrcreTshoTot );
//              }

//              dispGokeiKitei[V_KEISU_STRCRE_BAP] = Long.toString(dataValue2);

//          // BAPから取得した全ての値が""の時、合計値を""にする
//          }else{
//              dispGokeiKitei[V_KEISU_STRCRE_BAP] = V_EMPTY_STRING;
//          }
            // 裸与信（規定値）計算内容を変更
            //（信用限度不算入与信を考慮した権限判定上の裸与信に変更）
            String[] strYosinTot = (String[])hstTbl.get(F_HONAF_ZAN_TOT);
            String[] strYosin = (String[])hstTbl.get(F_HONAF_ZAN);
            if(    strYosinTot[V_KEISU_GENDOSAN_TOT_BAP].length() != 0 ||
                strStrcreTshoTot.length() != 0 ||
                dispGokeiKitei[V_KEISU_KTITNP_TOT_BAP].length() != 0 ||
                strYosin[V_KEISU_HLSHINYOFUSANNYU_BAP].length() != 0 ||
                dispKitei[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP].length() != 0
            ){
                dataValue2 = getDataValue2( strYosinTot[V_KEISU_GENDOSAN_TOT_BAP] ) -             // [限度算入与信合計（本件後残高）]
                             getDataValue2( strStrcreTshoTot ) -                                  // [裸与信対象与信合計]
                             getDataValue2( dispGokeiKitei[V_KEISU_KTITNP_TOT_BAP] ) -            // [規定担保計（規定値）]
                           ( getDataValue2( strYosin[V_KEISU_HLSHINYOFUSANNYU_BAP] ) -            // [内HL信用不算入（本件後残高）]
                             getDataValue2( dispKitei[V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP] ) ) ;  // [規定･一般担保･内HL(抵)（規定値）]

                if ( dataValue2 < 0 ) {
                    dataValue2 = 0 + getDataValue2( strStrcreTshoTot );
                }else{
                    dataValue2 = dataValue2 + getDataValue2( strStrcreTshoTot );
                }

                dispGokeiKitei[V_KEISU_STRCRE_BAP] = Long.toString(dataValue2);

            // BAPから取得した全ての値が""の時、合計値を""にする
            }else{
                dispGokeiKitei[V_KEISU_STRCRE_BAP] = V_EMPTY_STRING;
            }
/* YC20218-02 End */



            hstTbl.put( F_HIKIATE_KITEITI_TOT, dispGokeiKitei ) ;
            hstTbl.put( F_HIKIATE_JIKA_TOT,    dispGokeiJika  ) ;
            hstTbl.put( F_HIKIATE_KITEITI,     dispKitei      ) ;
            hstTbl.put( F_HIKIATE_JIKA,        dispJika       ) ;


            return ;


        }finally{
        }

    }

    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   一般与信以外の項目のデータ計算を行う。<BR>
     *   （初期表示・計数再取得、計算で共通の計算処理を行う）<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable  hstComBasket   共有情報(ハッシュ)
     */
    public void computeKokyaku2(Hashtable hstComBasket) {

        // パラメーターで渡された共有情報より、データを取得する
        Hashtable hstDB   = (Hashtable)hstComBasket.get( K_DB_DATA ) ;

        int dataValue  = 0 ;

        /* --------------------------------------------------------
         * 市場性与信の項目 各行の当月増減額のみ計算
         * --------------------------------------------------------
         */




        for(int i = 0; i < 10; i++) {

            // 指定月末残高
            String sijoGetuzanL[] = {
                        F_MEND_ZAN_1,   F_MEND_ZAN_2,   F_MEND_ZAN_3,
                        F_MEND_ZAN_4,   F_MEND_ZAN_5,   F_MEND_ZAN_6,
                        F_MEND_ZAN_7,   F_MEND_ZAN_8,   F_MEND_ZAN_9,
                        F_MEND_ZAN_10
                        } ;
            String sijoGetuzanV = (String)getData( hstDB,  sijoGetuzanL[i] ) ;

            // 指定月末極度額
            String sijoKyokudoL[] = {
                        F_LMT_1,        F_LMT_2,        F_LMT_3,
                        F_LMT_4,        F_LMT_5,        F_LMT_6,
                        F_LMT_7,        F_LMT_8,        F_LMT_9,
                        F_LMT_10
                        } ;
            String sijoKyokudoV = (String)getData( hstDB,  sijoKyokudoL[i] ) ;

            // 当月増減額
            String sijoZogenL[] = {
                        F_KMKDLTZGG_1,  F_KMKDLTZGG_2,  F_KMKDLTZGG_3,
                        F_KMKDLTZGG_4,  F_KMKDLTZGG_5,  F_KMKDLTZGG_6,
                        F_KMKDLTZGG_7,  F_KMKDLTZGG_8,  F_KMKDLTZGG_9,
                        F_KMKDLTZGG_10
                        } ;

            // 本件後与信額
            String sijoHonkengoL[] = {
                        F_HONAF_ZAN_1,  F_HONAF_ZAN_2,  F_HONAF_ZAN_3,
                        F_HONAF_ZAN_4,  F_HONAF_ZAN_5,  F_HONAF_ZAN_6,
                        F_HONAF_ZAN_7,  F_HONAF_ZAN_8,  F_HONAF_ZAN_9,
                        F_HONAF_ZAN_10
                        } ;
            String sijoHonkengoV = (String)getData( hstDB,  sijoHonkengoL[i] ) ;

            // 市場性与信の極度額が無い（存在しない）時
            // 極度額がない時：（本件後残高）－（月末残高）
            if ( sijoKyokudoV.length() == 0 || new Integer(sijoKyokudoV).intValue() == 0 ) {

                dataValue = getDataValue( sijoHonkengoV ) - getDataValue( sijoGetuzanV  );      //（本件後残高）－（月末残高）
                String[] strSijoZogenGk = { sijoHonkengoV,
                                            sijoGetuzanV
                                        };
                hstDB.put( sijoZogenL[i], getOutShijoValue(strSijoZogenGk, dataValue) );

            // 市場性与信の極度額がある（存在する）時
            // 極度額がある時：（本件後残高）－（極度額）
            } else {

                dataValue = getDataValue( sijoHonkengoV ) - getDataValue( sijoKyokudoV  );      //（本件後残高）－（極度額）
                String[] strSijoZogenGk = { sijoHonkengoV,
                                            sijoKyokudoV
                                        };
                hstDB.put( sijoZogenL[i], getOutShijoValue(strSijoZogenGk, dataValue) );
            }

        }


        /*
         * 簡易ＣＦ項目
         */
        // タグ作成＆データを計算する
        // もしタグが無かったら、空データ（タグ）を入れる
        if( hstDB.containsKey( F_KSKBTDLCF1 ) == false ) {
            hstDB.put( F_KSKBTDLCF1, new String( V_EMPTY_STRING ) ) ;
        }

        if( hstDB.containsKey( F_KSKBTDLCF2 ) == false ) {
            hstDB.put( F_KSKBTDLCF2, new String( V_EMPTY_STRING ) ) ;
        }

        if( hstDB.containsKey( F_KSKBTDLCF3 ) == false ) {
            hstDB.put( F_KSKBTDLCF3, new String( V_EMPTY_STRING ) ) ;
        }


        // 結果データを設定
        hstComBasket.put( K_DB_DATA, hstDB ) ;

        return ;

    }
//2009/06/23 ADD@R.Matsumura GEC20-C-059 end

// 2011/11/18 ADD@M.Hayashi GEC23-C-051 Start
    /**
     *   <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   保全率に関連する項目の計算を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  Hashtable hstComBasket 共有情報(ハッシュ)
     */
     public void computeHozen (Hashtable hstComBasket) {

        // 保全率の各項目の計算結果用変数
        String strHozenTaniMsg      = V_EMPTY_STRING;   // 保全率・金額単位
        String strHozenIpnysn       = V_EMPTY_STRING;   // 保全率・限度算入一般与信
        String strHozenSjoseiysn    = V_EMPTY_STRING;   // 保全率・限度算入市場性与信
        String strHozenKiteitanpo   = V_EMPTY_STRING;   // 保全率・規定担保合計
        String strHozenHozenrt      = V_EMPTY_STRING;   // 保全率・保全率
// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
        String strHozenSogoysn      = V_EMPTY_STRING;   // 保全率・総合与信
        String strHozenSogosnyo     = V_EMPTY_STRING;   // 保全率・総合信用
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End

        // 禀議共通DBクラスのインスタンスを取得する
        RLRRGCOM_DB dbCom           = new RLRRGCOM_DB(this.folder, this.dbcon, this.dbparam);


        /* --------------------------------------------------------
         * 保全率の関連する項目の計算に使用する値を取得する。
         * --------------------------------------------------------
         */

        // DBハッシュをhstComBasketから取得する。
        Hashtable dbData = (Hashtable)hstComBasket.get(K_DB_DATA);

        // 保全率の計算に使用する値をDBハッシュから取得する。
        String strDbTaniMsg1                    = (String)dbData.get(F_TANI_MSG_1);                     // 一般与信１タブ_金額単位（円）
        String strDbSjoseiinfTaniMsg1           = (String)dbData.get(F_SJOSEIINF_TANI_MSG_1);           // 市場性与信１タブ_金額単位（円）
        String[] strDbHonafZanArray             = (String[])dbData.get(F_HONAF_ZAN_TOT);
        String strDbHonafZan                    = strDbHonafZanArray[0];                                // 一般与信１タブ_限度算入与信合計（本件後残高）
        String strDbLmtintlRnHonafZan           = (String)dbData.get(F_LMTINTL_RN_HONAF_ZAN);           // 市場性与信１タブ_限度算入与信合計（本件後与信額）
        String[] strDbHikiateKiteitiTotArray    = (String[])dbData.get(F_HIKIATE_KITEITI_TOT);
        String strDbHikiateKiteitiTot           = strDbHikiateKiteitiTotArray[0];                       // 一般与信１タブ_規定担保合計（規定値）

        // 一般与信１タブ_金額単位（円）と市場性与信１タブ_金額単位（円）を比較した結果を格納する変数
        String strBiggerTani    = V_EMPTY_STRING;   // 大きいほうの金額単位コード
        int intBiggerTaniCd     = 99;               // 大きいほう単位コード
        String strSmallerTani   = V_EMPTY_STRING;   // 小さいほうの金額単位コード
        int intSmallerTaniCd    = 99;               // 小さいほうの単位コード


        /* --------------------------------------------------------
         * 保全率の各項目の計算を行う。
         * --------------------------------------------------------
         */

        /* --------------------------------
         保全率・金額単位
         * --------------------------------
         */
        // 一般与信１タブと市場性与信１タブの金額単位（円）から金額単位コードと単位コードを取得する。
        String strTaniMsg1Tani          = this.getTaniCdFromTaniMsg(strDbTaniMsg1);             // 一般与信１タブ_金額単位（円）の金額単位コード
        int intTaniMsg1TaniCd           = dbCom.getApiTani(strTaniMsg1Tani);                    // 一般与信１タブ_金額単位（円）の単位コード
        String strSjoseiinfTaniMsg1Tani = this.getTaniCdFromTaniMsg(strDbSjoseiinfTaniMsg1);    // 市場性与信１タブ_金額単位（円）の金額単位コード
        int intSjoseiinfTaniMsg1TaniCd  = dbCom.getApiTani(strSjoseiinfTaniMsg1Tani);           // 市場性与信１タブ_金額単位（円）の単位コード

        // 一般与信１タブと市場性与信１タブの金額単位コードを比較し、大小の金額単位コード、単位コードを取得する。
        if (getDataValue(strTaniMsg1Tani) >= getDataValue(strSjoseiinfTaniMsg1Tani)) {
            strBiggerTani =  strTaniMsg1Tani;
            intBiggerTaniCd = intTaniMsg1TaniCd;
            strSmallerTani = strSjoseiinfTaniMsg1Tani;
            intSmallerTaniCd = intSjoseiinfTaniMsg1TaniCd;
        } else {
            strBiggerTani = strSjoseiinfTaniMsg1Tani;
            intBiggerTaniCd = intSjoseiinfTaniMsg1TaniCd;
            strSmallerTani = strTaniMsg1Tani;
            intSmallerTaniCd = intTaniMsg1TaniCd;
        }

        // 大きいほうの金額単位コードを金額単位文言に変換し、計算結果に設定する。
        int i = 0;    // for用ループ変数
        if (strBiggerTani != null && strBiggerTani.equals(V_EMPTY_STRING) == false) {
            for (i = 0; i < V_STR_TANI_MSG.length; i++) {
                if (strBiggerTani.equals(V_STR_TANI[i])) {
                    strHozenTaniMsg = V_STR_TANI_MSG[i];
                    break;
                }
            }
        }

        /* --------------------------------
         保全率・限度算入一般与信
         * --------------------------------
         */
        // 一般与信１タブ_限度算入与信合計（本件後残高）がNULLまたはブランクの場合、ブランクを計算結果とする。
        if (strDbHonafZan == null || strDbHonafZan.equals(V_EMPTY_STRING) == true) {
            strHozenIpnysn = V_EMPTY_STRING;
        // 一般与信１タブ_限度算入与信合計（本件後残高）が0の場合は0を計算結果とする。
        } else if (strDbHonafZan.equals("0")) {
            strHozenIpnysn = strDbHonafZan;
        // 単位変換を行う。小数点以下は切り上げる。
        } else {
            strHozenIpnysn = dbCom.callTaniChange(strDbHonafZan, intTaniMsg1TaniCd, intBiggerTaniCd, 0, dbCom.K_KIRIAGE);
        }

        /* --------------------------------
         保全率・限度算入市場性与信
         * --------------------------------
         */
        // 市場性与信１タブ_限度算入与信合計（本件後与信額）がNULLまたはブランクの場合、ブランクを計算結果とする。
        if (strDbLmtintlRnHonafZan == null || strDbLmtintlRnHonafZan.equals(V_EMPTY_STRING) == true) {
            strHozenSjoseiysn = V_EMPTY_STRING;
        // 市場性与信１タブ_限度算入与信合計（本件後与信額）が0の場合は0を計算結果とする。
        } else if (strDbLmtintlRnHonafZan.equals("0")) {
            strHozenSjoseiysn = strDbLmtintlRnHonafZan;
        // 単位変換を行う。小数点以下は切り上げる。
        } else {
            strHozenSjoseiysn = dbCom.callTaniChange(strDbLmtintlRnHonafZan, intSjoseiinfTaniMsg1TaniCd, intBiggerTaniCd, 0, dbCom.K_KIRIAGE);
        }

        /* --------------------------------
         保全率・規定担保合計
         * --------------------------------
         */
        // 一般与信１タブ_規定担保合計（規定値）がNULLまたはブランクの場合、ブランクを計算結果とする。
        if (strDbHikiateKiteitiTot == null || strDbHikiateKiteitiTot.equals(V_EMPTY_STRING) == true) {
            strHozenKiteitanpo = V_EMPTY_STRING;
        // 一般与信１タブ_規定担保合計（規定値）が0の場合は0を計算結果とする。
        } else if (strDbHikiateKiteitiTot.equals("0")) {
            strHozenKiteitanpo = strDbHikiateKiteitiTot;
        // 単位変換を行う。小数点以下は切り捨てる。
        } else {
            strHozenKiteitanpo = dbCom.callTaniChange(strDbHikiateKiteitiTot, intTaniMsg1TaniCd, intBiggerTaniCd, 0, dbCom.K_KIRISUTE);
        }

        /* --------------------------------
         保全率・保全率
         * --------------------------------
         */

        int intHozenrtCalcTaniCd            = 99;                       // 計算用 単位コード
        String strHozenrtCalcIpnysn         = strDbHonafZan;            // 計算用 一般与信合計
        String strHozenrtCalcSjoseiysn      = strDbLmtintlRnHonafZan;   // 計算用 市場性与信合計
        String strHozenrtCalcKiteitiTot     = strDbHikiateKiteitiTot;   // 計算用 規定担保合計
        BigDecimal bdHozenrtCalcIpnysn      = null;                     // 計算用 一般与信合計
        BigDecimal bdHozenrtCalcSjoseiysn   = null;                     // 計算用 市場性与信合計
        BigDecimal bdHozenrtCalcKiteitiTot  = null;                     // 計算用 規定担保合計
        BigDecimal bdHozenHozenrt           = null;                     // 計算用 保全率
        BigDecimal bdCalcZero               = new BigDecimal(dbCom.getDoubleValue("0"));        // 計算用
        BigDecimal bdCalcPctg               = new BigDecimal(dbCom.getDoubleValue("100.0"));    // 計算用
        BigDecimal bdCalcMax                = new BigDecimal(dbCom.getDoubleValue("999.99"));   // 計算用

        // 一般与信合計、市場性与信合計がともにブランクの場合、ブランクを計算結果とする。
        if ((strHozenrtCalcIpnysn == null || strHozenrtCalcIpnysn.equals(V_EMPTY_STRING) == true) && (strHozenrtCalcSjoseiysn == null || strHozenrtCalcSjoseiysn.equals(V_EMPTY_STRING) == true)) {
            strHozenHozenrt = V_EMPTY_STRING;
        // 規定担保合計がブランクの場合、「0.00」を計算結果とする
        } else if (strHozenrtCalcKiteitiTot == null || strHozenrtCalcKiteitiTot.equals(V_EMPTY_STRING) == true) {
            strHozenHozenrt = "0.00";
        } else {
            // 一般与信合計、市場性与信合計がそれぞれNULLまたはブランクの場合、以降の計算で0を使用する。
            if (strHozenrtCalcIpnysn == null || strHozenrtCalcIpnysn.equals(V_EMPTY_STRING) == true) {
                strHozenrtCalcIpnysn = "0";
            }
            if (strHozenrtCalcSjoseiysn == null || strHozenrtCalcSjoseiysn.equals(V_EMPTY_STRING) == true) {
                strHozenrtCalcSjoseiysn = "0";
            }

            // 一般与信と市場性与信の金額単位コードを比較し、小さいほうの単位コードを保全率計算用単位コードとする。
            // 単位変換および計算用の型変換を行う。
            if (intTaniMsg1TaniCd == intSjoseiinfTaniMsg1TaniCd) {
                intHozenrtCalcTaniCd = intTaniMsg1TaniCd;
            } else {
                intHozenrtCalcTaniCd = intSmallerTaniCd;
                strHozenrtCalcIpnysn = dbCom.callTaniChange(strHozenrtCalcIpnysn, intTaniMsg1TaniCd, intHozenrtCalcTaniCd, 0, dbCom.K_KIRIAGE);
                strHozenrtCalcSjoseiysn = dbCom.callTaniChange(strHozenrtCalcSjoseiysn, intSjoseiinfTaniMsg1TaniCd, intHozenrtCalcTaniCd, 0, dbCom.K_KIRIAGE);
                strHozenrtCalcKiteitiTot = dbCom.callTaniChange(strHozenrtCalcKiteitiTot, intTaniMsg1TaniCd, intHozenrtCalcTaniCd, 0, dbCom.K_KIRISUTE);
            }

            bdHozenrtCalcIpnysn = new BigDecimal(strHozenrtCalcIpnysn);
            bdHozenrtCalcSjoseiysn = new BigDecimal(strHozenrtCalcSjoseiysn);
            bdHozenrtCalcKiteitiTot = new BigDecimal(strHozenrtCalcKiteitiTot);

            // 0割が発生する場合、ブランクを計算結果とする。
            if ((bdHozenrtCalcIpnysn.add(bdHozenrtCalcSjoseiysn)).equals(bdCalcZero)) {
                strHozenHozenrt = V_EMPTY_STRING;
            } else {
                // 保全率 = ( 規定担保合計 ÷ ( 一般与信合計 ＋ 市場性与信合計）) ) × 100.0の計算を行う。結果を小数点第3位で切り捨てる。
                bdHozenHozenrt = (bdHozenrtCalcKiteitiTot).multiply(bdCalcPctg).divide((bdHozenrtCalcSjoseiysn.add(bdHozenrtCalcIpnysn)), 2, BigDecimal.ROUND_DOWN);

                // 計算結果が「999.99」より大きい場合は「999.99」を計算結果とする。
                if (bdHozenHozenrt.compareTo(bdCalcMax) > 0) {
                    strHozenHozenrt = "999.99";
                }
                else
                {
                    strHozenHozenrt = bdHozenHozenrt.toPlainString();
                }
            }
        }

// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
        /* --------------------------------
        保全率・総合与信
        * --------------------------------
        */

        int intSogoysnSogosnyoCalcTaniCd    = 99;                       // 計算用 単位コード(総合与信、総合信用で共用)
        String strSogoysnCalcIpnysn         = strDbHonafZan;            // 計算用 一般与信合計
        String strSogoysnCalcSjoseiysn      = strDbLmtintlRnHonafZan;   // 計算用 市場性与信合計
        BigDecimal bdSogoysnCalcIpnysn      = null;                     // 計算用 一般与信合計
        BigDecimal bdSogoysnCalcSjoseiysn   = null;                     // 計算用 市場性与信合計
        BigDecimal bdHozenSogoysn           = null;                     // 計算用 総合与信

        // 一般与信合計、市場性与信合計がともにブランクの場合、ブランクを計算結果とする。
        if ((strSogoysnCalcIpnysn == null || strSogoysnCalcIpnysn.equals(V_EMPTY_STRING) == true) && (strSogoysnCalcSjoseiysn == null || strSogoysnCalcSjoseiysn.equals(V_EMPTY_STRING) == true)) {
            strHozenSogoysn = V_EMPTY_STRING;
        } else {
            // 一般与信合計、市場性与信合計がそれぞれNULLまたはブランクの場合、以降の計算で0を使用する。
            if (strSogoysnCalcIpnysn == null || strSogoysnCalcIpnysn.equals(V_EMPTY_STRING) == true) {
                strSogoysnCalcIpnysn = "0";
            }
            if (strSogoysnCalcSjoseiysn == null || strSogoysnCalcSjoseiysn.equals(V_EMPTY_STRING) == true) {
                strSogoysnCalcSjoseiysn = "0";
            }

            // 一般与信と市場性与信の金額単位コードを比較し、小さいほうの単位コードを総合与信・総合信用計算用単位コードとする。
            // 単位変換および計算用の型変換を行う。
            if (intTaniMsg1TaniCd == intSjoseiinfTaniMsg1TaniCd) {
                intSogoysnSogosnyoCalcTaniCd = intTaniMsg1TaniCd;
            } else {
                intSogoysnSogosnyoCalcTaniCd = intSmallerTaniCd;
                strSogoysnCalcIpnysn = dbCom.callTaniChange(strSogoysnCalcIpnysn, intTaniMsg1TaniCd, intSogoysnSogosnyoCalcTaniCd, 0, dbCom.K_KIRIAGE);
                strSogoysnCalcSjoseiysn = dbCom.callTaniChange(strSogoysnCalcSjoseiysn, intSjoseiinfTaniMsg1TaniCd, intSogoysnSogosnyoCalcTaniCd, 0, dbCom.K_KIRIAGE);
            }

            bdSogoysnCalcIpnysn = new BigDecimal(strSogoysnCalcIpnysn);
            bdSogoysnCalcSjoseiysn = new BigDecimal(strSogoysnCalcSjoseiysn);

            // 総合与信 = 一般与信合計 ＋ 市場性与信合計の計算を行う
            bdHozenSogoysn = bdSogoysnCalcIpnysn.add(bdSogoysnCalcSjoseiysn);

            // 単位変換を行う。小数点以下は切り捨てる。
            strHozenSogoysn = dbCom.callTaniChange(bdHozenSogoysn.toPlainString(), intSogoysnSogosnyoCalcTaniCd, intBiggerTaniCd, 0, dbCom.K_KIRIAGE);
        }

        /* --------------------------------
         保全率・総合信用
         * --------------------------------
         */

        String strSogosnyoCalcIpnysn        = strDbHonafZan;            // 計算用 一般与信合計
        String strSogosnyoCalcSjoseiysn     = strDbLmtintlRnHonafZan;   // 計算用 市場性与信合計
        String strSogosnyoCalcKiteitiTot    = strDbHikiateKiteitiTot;   // 計算用 規定担保合計
        BigDecimal bdSogosnyoCalcIpnysn     = null;                     // 計算用 一般与信合計
        BigDecimal bdSogosnyoCalcSjoseiysn  = null;                     // 計算用 市場性与信合計
        BigDecimal bdSogosnyoCalcKiteitiTot = null;                     // 計算用 規定担保合計
        BigDecimal bdHozenSogosnyo          = null;                     // 計算用 総合信用

        // 一般与信合計、市場性与信合計がともにブランクの場合、ブランクを計算結果とする。
        if ((strSogosnyoCalcIpnysn == null || strSogosnyoCalcIpnysn.equals(V_EMPTY_STRING) == true) && (strSogosnyoCalcSjoseiysn == null || strSogosnyoCalcSjoseiysn.equals(V_EMPTY_STRING) == true)) {
            strHozenSogosnyo = V_EMPTY_STRING;
        } else {
            // 一般与信合計、市場性与信合計、規定担保合計がそれぞれNULLまたはブランクの場合、以降の計算で0を使用する。
            if (strSogosnyoCalcIpnysn == null || strSogosnyoCalcIpnysn.equals(V_EMPTY_STRING) == true) {
                strSogosnyoCalcIpnysn = "0";
            }
            if (strSogosnyoCalcSjoseiysn == null || strSogosnyoCalcSjoseiysn.equals(V_EMPTY_STRING) == true) {
                strSogosnyoCalcSjoseiysn = "0";
            }
            if (strSogosnyoCalcKiteitiTot == null || strSogosnyoCalcKiteitiTot.equals(V_EMPTY_STRING) == true) {
                strSogosnyoCalcKiteitiTot = "0";
            }

            // 一般与信と市場性与信の金額単位コードを比較し、小さいほうの単位コードを保全率計算用単位コードとする。
            // 単位変換および計算用の型変換を行う。
            if (intTaniMsg1TaniCd == intSjoseiinfTaniMsg1TaniCd) {
                intSogoysnSogosnyoCalcTaniCd = intTaniMsg1TaniCd;
            } else {
                intSogoysnSogosnyoCalcTaniCd = intSmallerTaniCd;
                strSogosnyoCalcIpnysn = dbCom.callTaniChange(strSogosnyoCalcIpnysn, intTaniMsg1TaniCd, intSogoysnSogosnyoCalcTaniCd, 0, dbCom.K_KIRIAGE);
                strSogosnyoCalcSjoseiysn = dbCom.callTaniChange(strSogosnyoCalcSjoseiysn, intSjoseiinfTaniMsg1TaniCd, intSogoysnSogosnyoCalcTaniCd, 0, dbCom.K_KIRIAGE);
                strSogosnyoCalcKiteitiTot = dbCom.callTaniChange(strSogosnyoCalcKiteitiTot, intTaniMsg1TaniCd, intSogoysnSogosnyoCalcTaniCd, 0, dbCom.K_KIRISUTE);
            }

            bdSogosnyoCalcIpnysn = new BigDecimal(strSogosnyoCalcIpnysn);
            bdSogosnyoCalcSjoseiysn = new BigDecimal(strSogosnyoCalcSjoseiysn);
            bdSogosnyoCalcKiteitiTot = new BigDecimal(strSogosnyoCalcKiteitiTot);

            // 総合信用 = ( 一般与信合計 ＋ 市場性与信合計）－ 規定担保合計の計算を行う
            bdHozenSogosnyo = (bdSogosnyoCalcIpnysn.add(bdSogosnyoCalcSjoseiysn)).subtract(bdSogosnyoCalcKiteitiTot);

            // 計算結果が「0」より小さい場合は「0」を計算結果とする。
            if (bdHozenSogosnyo.compareTo(bdCalcZero) < 0) {
                strHozenSogosnyo = "0";
            } else {
                // 単位変換を行う。小数点以下は切り捨てる。
                strHozenSogosnyo = dbCom.callTaniChange(bdHozenSogosnyo.toPlainString(), intSogoysnSogosnyoCalcTaniCd, intBiggerTaniCd, 0, dbCom.K_KIRIAGE);
            }
        }
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End


        /* --------------------------------------------------------
         * 各項目の計算結果をDBハッシュに設定する。
         * --------------------------------------------------------
         */

        // 計算結果をhstComBasketに登録項目として設定する。
        dbData.put(F_HOZEN_TANI_MSG, strHozenTaniMsg);              // 保全率・金額単位
        dbData.put(F_HOZEN_IPNYSN, strHozenIpnysn);                 // 保全率・限度算入一般与信
        dbData.put(F_HOZEN_SJOSEIYSN, strHozenSjoseiysn);           // 保全率・限度算入市場性与信
        dbData.put(F_HOZEN_KITEITANPO, strHozenKiteitanpo);         // 保全率・規定担保合計
        dbData.put(F_HOZEN_HOZENRT, strHozenHozenrt);               // 保全率・保全率
// 2012/03/06 ADD@Y.Sato GEC23-C-078 Start
        dbData.put(F_HOZEN_SOGOYSN, strHozenSogoysn);               // 保全率・総合与信
        dbData.put(F_HOZEN_SOGOSNYO, strHozenSogosnyo);             // 保全率・総合信用
// 2012/03/06 ADD@Y.Sato GEC23-C-078 End

        // hstComBasketに出力用データを設定する。
        hstComBasket.put(K_DB_DATA, dbData);

        return;
     }

    /**
     *   <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   金額単位文言より禀議書で使用する金額単位コードを取得する。<BR>
     *   金額単位文言が千円、百万円、億円の場合、金額単位コードに変換して返却する。<BR>
     *   それ以外の場合、空を返却する。
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @param  String     金額単位文言
     *   @param  String     禀議書で使用する金額単位のコード
     */
     public String getTaniCdFromTaniMsg (String strTaniMsg) {

        String strTani = V_EMPTY_STRING;        // 金額単位コード
        int i = 0;                              // for用ループ変数

        // 金額単位文言より金額単位コードを取得する
        if (strTaniMsg != null && strTaniMsg.equals(V_EMPTY_STRING) == false) {
            strTaniMsg = strTaniMsg.trim();
            for (i = 0; i < V_STR_TANI_MSG.length; i++) {
                if (strTaniMsg.equals(V_STR_TANI_MSG[i].trim())) {
                    strTani = V_STR_TANI[i];
                    break;
                }
            }
        }
     return strTani;
    }
// 2011/11/18 ADD@M.Hayashi GEC23-C-051 End
}
