/*******************************************************************
 *   システム名    ：融資禀議・個人ローンＢＰＲ
 *   サブシステム名：電子禀議
 *   処理名        ：計数情報計数再取得
 *   処理概要      ：計数情報の計数再取得処理を行う
 *   ファイル名    ：RLRRG004_B01_U04.java
 ******************************************************************/
package jp.co.btm.irl.rlr.rg004 ;

import java.util.Hashtable;
import com.ibm.jp.wacs.CraftsTransaction;
import com.ibm.jp.wacs.WACSSysException;
import com.ibm.jp.wacs.WACSApplException;
import com.ibm.jp.wacs.CraftsDataBean;
import com.ibm.jp.wacs.WACSUser;
import com.ibm.jp.wacs.db.CraftsDBConnector;
import com.ibm.jp.wacs.db.CraftsDBParam;
import jp.co.btm.irl.rlr.rg000.*;

import jp.co.btm.irl.rlr.cm000.*;

/**
 *   <b>計数画面－計数再取得処理</b>
 *   計数情報画面の計数情報の再取得処理を行う。
 *   @author  M.Nitami
 *
 * Date        Name        Reason for change
 * ------------------------------------------------------------------
 * 2002/12/5   M.Nitami    新規作成
 * 2003/04/25  M.OTAKE     ITb障害対応（項目入力プロテクト制御）
 * 2003/05/23  S.Seimura   ホスト連携時移管後の店CIFで処理を行うように修正
 * 2003/06/23  M.OTAKE     禀議書で取引日が指定されている場合、取引日で計数取得を行う修正(01148)
 * 2005/02/23  S.Seimura   ボタン制御一部修正
 */
public class RLRRG004_B01_U04
            extends RLRRGCOM_HOST_BASE
            implements IRingiMsg, IRingiWF {

    private CraftsDBParam   dbparam = null;

    private Hashtable hstComBasket  = null;
    private Hashtable hstKey        = null;
    private Hashtable hstWF         = null;
    private Hashtable hstDB         = null;
    private Hashtable hstHOST       = null;

    private static final String F_PROP_CHANGE_EXECUTE = "rlrPropChangeExecute";
    private static final String strReqId = "rlrrg004_b01_u04";
    private static final int intBtnCnt = 6;
    private static final String strHidukeErrMsg = "入力された日付" ;
/* 2003/05/14 計数COMに移動
    private String[] kmk_yosin = {
                                "貸付金・商手合計",
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
                                "D/P・D/A",
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
                                "限度算入ﾛｰﾝ合計",
                                "オンバランス合計",
                                "オフバランス合計",
                                "限度不算入与信合計",
                                "協保貸",
                                "年金転貸",
                                "指定L/C小切手",
                                "L/G",
                                "一般与信合計",
                                "その他与信合計",
                                "",
                                "" } ;
*/

    // メッセージ格納用宣言
    private String strMessageID;
    private String strMessageText;


    /**
     *   <b>メソッド概要：</b>
     *   コンストラクタ。
     */
    public RLRRG004_B01_U04() {
        super();
    }

    /**
     *   <DL>
     *   <DT><b>メソッド概要：</b><DD>
     *   入力チェック<BR>
     *　 </DD><DT>
     *   </DL>
     *   @return boolean 入力チェック結果
     */
    protected boolean checkInput() {
        return true ;
    }


    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数情報画面の計数情報の再取得処理を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @exception  WACSSysException
     *   @exception  com.ibm.jp.wacs.db.WACSDBException
     */
    protected void doProcess()
                        throws WACSSysException,WACSApplException,com.ibm.jp.wacs.db.WACSDBException    {

        try {

            int rc = 0 ;

            // 入力データビーンを取得する
            ibean = getInDataBean();

            // 出力データビーンを取得する
            obean = getOutDataBean();

            // DB接続インスタンス(オートコミットOFF)を取得する
            dbcon   = connect(false);
            dbparam = getDBParam();

            // 禀議業務共通クラスのインスタンスを取得する
            RLRRGCOM_RINGI ringiCom = new RLRRGCOM_RINGI(folder, dbcon, dbparam);

            // 共有情報の生成と初期化を行う
            hstComBasket = ringiCom.initialComBasket(ibean);

            // ボタン制御用の項目を定義
            String[] strBtn = new String[intBtnCnt] ;
            int intNo = 0 ;

            // 基準日(取引日)設定用項目を定義
            String strTribi = null;

// 2003.10.14 Add K.Sato@STEP2  -->
            // clone項目
            Hashtable hstClnComBasket = null;
            Hashtable hstClnDB = null;
            Hashtable hstClnKey = null;
// <--

            // 操作者ユーザーIDを取得する。
            WACSUser user    = folder.getUser();
            String strUserId = user.getUserID();

            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA );
            hstKey.put( F_USER_ID, strUserId );
            hstComBasket.put( K_KEY_DATA, hstKey );

            // 計数業務共通クラスのインスタンスを取得する
            RLRRG004_B01 keisuCom = new RLRRG004_B01( folder, dbcon, dbparam ) ;

            // 禀議個別ＤＢクラスのインスタンスを取得する
            RLRRG004_B01_DB keisuDB = new RLRRG004_B01_DB( folder, dbcon, dbparam ) ;

            // 禀議共通ＨＯＳＴクラスのインスタンスを取得する
            // RLRRGCOM_HOST hostCom = new RLRRGCOM_HOST( folder, dbcon, dbparam ) ;

            // 禀議共通ワークフロークラスのインスタンスを取得する
            RLRRGCOM_WF wfCom = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;

            // 項目属性管理クラスのインスタンスを取得する
            RLRRGCOM_PROP_BASE strProp = RLRRGCOM_PROP_FACT.getPropInstance(strReqId);

// 2003.10.03 Add K.Sato@STEP2  -->
            // カレンダークラスのインスタンスを生成する
            RLRCMCOM_CalendarWrapper Cal = new RLRCMCOM_CalendarWrapper(folder, dbcon, getDBParam());
// <--

// 2003.10.06 Add K.Sato@STEP2  -->
            // 禀議共通DBクラスのインスタンスを生成する
            RLRRGCOM_DB dbCom = new RLRRGCOM_DB( folder, dbcon, dbparam );
// <--

            /*
             * ホスト情報の取得
             */
            // ホストパラメータの設定

            // ユーザーの詳細情報取得
            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA ) ;
            hstKey.put( F_USER_ID, strUserId );
            hstComBasket.put( K_KEY_DATA, hstKey ) ;
            wfCom.getOperatorInfo(hstComBasket);


            // 店ＣＩＦ、ユーザー情報（ユーザーＩＤ、部店エリアコード、課・グループコード、役職順コード）
            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA );
            hstWF  = (Hashtable)hstComBasket.get( K_WF_DATA  );
            hstKey.put( F_USER_ID      , hstWF.get( F_USER_ID       ));
            hstKey.put( F_BUTEN_AREA_CD, hstWF.get( F_BUTEN_AREA_CD ));
            hstKey.put( F_KA_GRP_CD    , hstWF.get( F_KA_GRP_CD     ));
            hstKey.put( F_SHOK_JUN     , hstWF.get( F_SHOK_JUN      ));

//          hstKey.put( F_BRNO         , ibean.getString( F_BRNO    )) ;
//          hstKey.put( F_TRISKNO      , ibean.getString( F_TRISKNO )) ;
// 2003/05/26 CHG@S.SEIMURA 移管
            // 案件基本情報を取得
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
            hstKey.put(F_LC_NO,ibean.getString(F_LC_NO));
            hstKey.put(F_CP_NO,V_CP_NO_DEFAULT);
            hstComBasket.put(K_KEY_DATA,hstKey);
            wfCom.getAnkenInfo(hstComBasket);

            hstWF = (Hashtable)hstComBasket.get(K_WF_DATA);

            hstKey.put(F_BRNO,         ns(hstWF.get(F_BRNO)));
            hstKey.put(F_TRISKNO,      ns(hstWF.get(F_TRISKNO)));
            String strIkangoBrno    = (String)ns(hstWF.get(F_BRNO));
            String strIkangoTriskno = (String)ns(hstWF.get(F_TRISKNO));

// 2003/06/23 DEL
//          if( ibean.containsData( F_LC_NO ) ){
//              hstKey.put( F_LC_NO        , ibean.getString( F_LC_NO )) ;
//          }

// 2003/06/23 CHG@M.OTAKE (01148)対応
            hstComBasket.put( K_KEY_DATA, hstKey ) ;

            if( ibean.containsData( F_LC_NO ) ){
    //          hstKey.put( F_LC_NO        , ibean.getString( F_LC_NO )) ;

                // 禀議共通DBクラスのインスタンスを取得する
                RLRRGCOM_DB ringiDB = new RLRRGCOM_DB(folder,dbcon,dbparam);

    //          hstKey.put(F_HOSEIKUBUN, V_HOSEI_MAE);
                ringiCom.getHoseiKbn(hstComBasket);     // 補正区分取得
                Hashtable hstCom = null;
                hstCom = (Hashtable)hstComBasket.get(K_COM_DATA);

                // 融資DBより表示対象の禀議書データを取得
                hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
                hstKey.put(F_HOSEIKUBUN,(String)hstCom.get(F_HOSEIKUBUN));


                ringiDB.getRingishoKgn(hstComBasket);   // 取引日取得

// 2003.10.03 Comment&Add K.Sato@STEP2  -->
//              Hashtable hstTmpDB  = (Hashtable)hstComBasket.get(K_DB_DATA);
//              String strtribi    = (String)hstTmpDB.get(F_TRIBI);
//
//                                  // 取引日の指定がある場合、取引日を指定する。
//              if( strtribi.trim().length()!=0 ){
//                      hstKey.put( F_TRIBI        , strtribi.trim()) ;
//              }

                // 取引日の取得･設定を行う
                strTribi = ringiCom.cnvNullData(ibean.getString(F_TRIBI));
                if(strTribi.equals(V_EMPTY_STRING)){
                    // 当日営業日を取得する
                    strTribi = Cal.getEigyoDay();
                }

                hstKey.put(F_TRIBI, strTribi);
// <--

// 2003.10.03 Add K.Sato@STEP2  -->
            } else {
                // 案件番号が取得できなかった場合、当日営業日を取得・設定する
                strTribi = Cal.getEigyoDay();

                hstKey.put(F_TRIBI, strTribi);
            }
// <--
            hstComBasket.put( K_KEY_DATA, hstKey ) ;



            // ホストからデータを取得
            super.rqstKeisuRiritugaiSyokai(hstComBasket);

            int intRc = ( (Integer)hstComBasket.get(K_RETURN) ).intValue();
            //エラーの場合
            if(intRc != IRingiHOST.RC_OK ){

                //DBロールバック
                if(dbcon != null) {
                    dbcon.rollback();
                }

                hstHOST = (Hashtable)hstComBasket.get(K_HOST_DATA);
                String[] strErrField = {(String)hstHOST.get(IRingiHOST.KY_ERROR_MESSAGE)};
                String strMsgId = ringiCom.getHostErrorMsgId(
                                    ( (Integer)hstComBasket.get(K_DETAIL) ).intValue(),
                                    ( (Integer)hstComBasket.get(K_RETURN) ).intValue(),
                                    true );
                String strMessageText = getMessageText(strMsgId, strErrField);

                obean.setString(F_SUCCESS_FLAG, V_FALSE);
                obean.setString(F_ERROR_ID, strMsgId);
                obean.setString(F_ERROR_TYPE, CD_ERR_TYPE_WARNING);
                obean.setString(F_ERROR_MSG, strMessageText);
                return;
            }




            /*
             * ＤＢから計数の情報を取得
             */
            hstKey = (Hashtable) hstComBasket.get(K_KEY_DATA);
            hstHOST = (Hashtable) hstComBasket.get(K_HOST_DATA);

// 2003/05/14 DEL@S.SEIMURA 計数COMに移動
//          // 科目を出力データとして設定
//
//          // ホストから取得した一般与信の科目を編集する
//          hstHOST = (Hashtable)hstComBasket.get(K_HOST_DATA);
//          String[] strKamoku = (String[])hstHOST.get(IRingiItemKeisu.F_KMK_RMT);
//          for( int i = 0; i < strKamoku.length; i++ ) {
//
//              if( ( 2 <= i && i <= 13 ) || ( 42 <= i ) ) {
//                  kmk_yosin[i] = strKamoku[i];
//              }
//
//          }
//
//          hstHOST.put(IRingiItemKeisu.F_KMK_RMT, kmk_yosin);
//          hstHOST.put(IRingiItemKeisu.F_KMK_RMT_TOT, kmk_rmt_tot_label);
//          obean.setStringArray(F_KMK_HIKIATE, kmk_hikiate_label);
//          obean.setStringArray(F_KMK_HIKIATE_TOT, kmk_hikiate_tot_label);
//          obean.setStringArray(IRingiItemKeisu.F_KMK_RMT_TOT, kmk_rmt_tot_label);


            /*
             * ホストクラスから取得したデータを
             * ＤＢクラスへのパラメータに設定する
             */
            keisuCom.setHashToHash( hstHOST, hstKey );

            // サーバー入力の店ＣＩＦをパラメータに設定
// 2003/05/26 CHG@S.SEIMURA 移管
//          hstKey.put(F_BRNO, ibean.getString(F_BRNO));
//          hstKey.put(F_TRISKNO, ibean.getString(F_TRISKNO));
            hstKey.put(F_BRNO,    strIkangoBrno);
            hstKey.put(F_TRISKNO, strIkangoTriskno);
            hstComBasket.put(K_KEY_DATA, hstKey);


            /*
             * 外部管理下ＤＢのデータを取得し、
             * 補正値を使用した計算を行い、結果をK_DB_DATAに格納する
             */
            keisuCom.setHostAndDbData(hstComBasket);
// 2003/03/26 ADD@S.SEIMURA 戻り値判定追加
            // 戻り値判定
            int intRc2 = ( (Integer)hstComBasket.get(K_RETURN) ).intValue();
            if ( intRc2 == IRingiDB.RC_DAIHYOU_TENCIF_NG ) {

                // 出力データビーンに値を設定
                strMessageID      = (String)hstComBasket.get(K_DETAIL);
                strMessageText    = getMessageText(strMessageID, null);

                obean.setString(F_SUCCESS_FLAG, V_FALSE);
                obean.setString(F_ERROR_ID    , strMessageID) ;
                obean.setString(F_ERROR_TYPE  , IRingi.CD_ERR_TYPE_WARNING);
                obean.setString(F_ERROR_MSG   , strMessageText);

                // DBロールバック
                if(dbcon != null){
                    dbcon.rollback();
                }

                // リターンし、処理を終了する
                return;
            }

            /*
             * オーバーフロー項目と日付の整合性のチェック
             */
            rc = keisuCom.checkOverFlow( hstComBasket ) ;
            // 日付の入力エラー
            if( rc == -1 ) {

                // rlrrgs1041w

                String strMessageID = MSG_RRGS1041;
                String[] strText = { strHidukeErrMsg } ;
                String strMessageText = getMessageText(strMessageID, strText);
                obean.setString(F_SUCCESS_FLAG, V_FALSE);
                obean.setString(F_ERROR_ID, strMessageID);
                obean.setString(F_ERROR_TYPE, CD_ERR_TYPE_WARNING);
                obean.setString(F_ERROR_MSG, strMessageText);

                dbcon.commit();
                return;

            }
// 2003/04/21 DEL@S.SEIMURA 計数再取得時にオーバーフローチェックは行わない
//          // オーバーフロー等の発生時
//          } else if( rc == -2 ) {
//
//              // rlrrgs1068w
//
//// 2003/04/18 CHG@S.SEIMURA メッセージ変更
////                String strMessageID = MSG_RRGS1040;
//              String strMessageID = MSG_RRGS1068;
//              String strMessageText = getMessageText(strMessageID, null);
//              obean.setString(F_SUCCESS_FLAG, V_FALSE);
//              obean.setString(F_ERROR_ID, strMessageID);
//              obean.setString(F_ERROR_TYPE, CD_ERR_TYPE_WARNING);
//              obean.setString(F_ERROR_MSG, strMessageText);
//
//              dbcon.commit();
//              return;
//
//          }


            /*
             * 取得した計数情報をＤＢに登録する
             */

            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
            hstKey.put( F_LC_NO, ibean.getString(F_LC_NO) );
// 2003/05/26 CHG@S.SEIMURA 移管
            hstKey.put(F_BRNO, ibean.getString(F_BRNO));
            hstKey.put(F_TRISKNO, ibean.getString(F_TRISKNO));

            // Add. M.Nitami 2003/1/24
            keisuCom.setHashToHash(
                (Hashtable)hstComBasket.get(K_DB_DATA), hstKey);

// 2003.10.07 Add K.Sato@STEP2  -->
// 2003.10.14 Change K.Sato@STEP2   -->
            // 計数案件番号を取得する
            hstClnComBasket = (Hashtable)hstComBasket.clone();

            hstClnKey = (Hashtable)hstClnComBasket.get(K_DB_DATA);
            hstClnKey.put(F_LC_NO, ibean.getString(F_LC_NO));
            hstClnKey.put(F_HOSEIKUBUN, V_HOSEI_MAE);
            hstClnComBasket.put(K_DB_DATA, hstClnKey);

            dbCom.getRingiKyotsu2(hstClnComBasket);

            hstClnDB = (Hashtable)hstClnComBasket.get(K_DB_DATA);
            String strKeisuLcNo = ringiCom.cnvNullData( (String)hstClnDB.get(F_KEISU_LC_NO) );


            // 計数案件番号から禀議書(共通)DB項目を取得する
            hstClnKey = (Hashtable)hstClnComBasket.get(K_DB_DATA);
            hstClnKey.put(F_LC_NO, strKeisuLcNo);
            hstClnKey.put(F_HOSEIKUBUN, V_HOSEI_MAE);
            hstClnComBasket.put(K_DB_DATA, hstClnKey);

            dbCom.getRingiKyotsu2(hstClnComBasket);

            hstClnDB = (Hashtable)hstClnComBasket.get(K_DB_DATA);
            strTribi = (String)hstClnDB.get(F_TRIBI);


            // 取引日(基準日)を設定する
            if(strTribi.length() > 0){
                // 取引日が設定している場合
                // 処理無し
                ;
            } else {
                // 取引日が設定していない(決定次第)の場合
                // 当日営業日を設定する
                strTribi = Cal.getEigyoDay();
            }
            hstKey.put(F_MKBI, strTribi);

            // 禀査番号を設定する
            hstKey.put(F_RSNO, ibean.getString(F_RSNO));
// <--

            hstComBasket.put( K_KEY_DATA, hstKey );
            keisuDB.setNewData( hstComBasket ) ;


// 2003.10.06 Add K.Sato@STEP2  -->
            // 計数取得要否を登録する
            hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);

            hstKey.put(F_LC_NO, ibean.getString(F_LC_NO));
            hstKey.put(F_KESR, V_KESR_YO);
            hstComBasket.put(K_KEY_DATA, hstKey);

            dbCom.setKeisuYohi(hstComBasket);
// <--

            /*
             * 色変情報の取得
             */

            // 案件番号が変更されている恐れが有るので、再設定
            hstKey.put(F_LC_NO, ibean.getString(F_LC_NO));

/* Del. M.Nitami 2003/1/24
            // ＤＢから取得したデータ全てをパラメータに設定する
            keisuCom.setHashToHash(
                (Hashtable)hstComBasket.get(K_DB_DATA), hstKey);
*/

            hstComBasket.put(K_KEY_DATA, hstKey);

/* Add. M.Nitami 2003/1/28 */
            keisuDB.getAllData( hstComBasket ) ;


// 2003.10.06 Add K.Sato@STEP2  -->
            // 基準日の設定
            hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

            strTribi = (String)hstDB.get(F_MKBI);
            strTribi = Cal.getYearMonthDayWareki(strTribi, V_EMPTY_STRING, Cal.GGG_GENGO);

            hstDB.put(F_MKBI, strTribi);

            hstComBasket.put(K_DB_DATA, hstDB);
// <--

            // 項目の色をデフォルトに設定
            strProp.setAllDefaultColor();


            /*
             * 出力データの設定
             */
            keisuCom.getKamokuData(hstComBasket);
            keisuCom.setOutData( ibean, obean, hstComBasket ) ;


//          /*
//           * ボタンと色変の制御（リセット）
//           */
//          strProp.setAllBtnNonProtect();
//          RLRRGCOM_PROP_RES hsRes = strProp.getPropTables();
//          String[] strList = hsRes.getPropChangerList();
//          String[] strFlg = {V_TRUE};
//          String[] strZeroLen = { "" };
//
//          // 項目属性情報の出力
//          String[] strPCList = hsRes.getPropChangerList();
//          for (int i = 0; i < strPCList.length; i++){
//
//              String[] strPCItem = hsRes.getItemArray(strPCList[i]);
//              if (strPCItem.length>0) {
//                  if (strPCItem[0] != null){
//                      obean.setStringArray(strPCList[i],strPCItem);
//                  } else {
//                      obean.setStringArray(strPCList[i], strZeroLen ) ;
//                  }
//              }
//          }
//
//          // 属性変更実行変数(Array形)
//          obean.setStringArray(F_PROP_CHANGE_EXECUTE,strFlg);


/*
 * 2005/02/23 CHG@S.SEIMURA STEP2修正分打消 START
 *
 * STEP2での修正後、Crafts!15年度レベルアップ(GEC15-C-080-214(再取得ボタン制御))の
 * 対応が行われ、STEP2での修正は不要であるため削除
 */
// 2003.10.06 Comment&Add K.Sato@STEP2  -->
            /*
             * ボタン制御
             */
            // 直近計数案件番号が取得できなかった時は
            // 直近計数照会ボタンを使用不可にする
            hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);
            String chkknLc_no = (String)hstDB.get( IRingiItemKeisu.F_CKKKNKEISU_LC_NO );
            if( chkknLc_no == null  ||  chkknLc_no.length() == 0 ) {
                strBtn[intNo++] = B_CKKEISUINQ;
            }

//          /*
//           * ボタン制御
//           */
//          // ステータスコードを取得する
//          String strStatus = (String)ibean.getString(F_WF_STATUS);
//
//          // 直近計数案件番号を取得する
//          hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);
//          String chkknLc_no = ringiCom.cnvNullData( (String)hstDB.get( IRingiItemKeisu.F_CKKKNKEISU_LC_NO ));
//
//          if(strStatus.equals(RC_STAT_SAKUSEITYU)){
//              // ステータスが「作成中」の場合
//              if(chkknLc_no.length() > 0){
//                  // 直近計数案件番号が取得できた場合
//                  // 処理無し
//                  ;
//              } else {
//                  // 直近計数が取得できなかった場合
//                  // 直近計数照会ボタンを使用不可にする
//                  strBtn[intNo++] = B_CKKEISUINQ;
//              }
//
//          } else {
//              // ステータスが「作成中」以外の場合
//              if(chkknLc_no.length() > 0){
//                  // 直近計数案件番号が取得できた場合
//                  // 計数再取得ボタンを使用不可にする
//                  strBtn[intNo++] = B_KSRESHUT;
//              } else {
//                  // 直近計数が取得できなかった場合
//                  // 計数再取得ボタン・直近計数照会ボタンを使用不可にする
//                  strBtn[intNo++] = B_KSRESHUT;
//                  strBtn[intNo++] = B_CKKEISUINQ;
//              }
//
//          }
// <--
/*
 * 2005/02/23 CHG@S.SEIMURA STEP2修正分打消 END
 */

            // ボタンのプロテクトを実行
            strProp.setProtect(strBtn);


            // 設定した制御情報の全項目を取得
            RLRRGCOM_PROP_RES hsRes = strProp.getPropTables();
            String[] strList = hsRes.getPropChangerList();
            String [] strFlg = {V_TRUE};
            ringiCom.getOutDataBeanPropRes( obean, hsRes, strFlg ) ;

            // 更新モードに設定
            obean.setString(F_UPDATE_MODE_FLG, V_UPDATE_KOUSIN_MODE);

            dbcon.commit();

        } catch (WACSApplException e) {
            logError(MSG_SKKS0105,
                new Object[]{getClass().getName(),RLRRG_METHOD_NAME},e);

            // DBロールバック
            if(dbcon != null) {
                dbcon.rollback();
            }
            throw e;

        } catch (com.ibm.jp.wacs.db.WACSDBException e) {
            //エラーログ出力
            logError(MSG_SKKS0104,
                new Object[]{getClass().getName(),RLRRG_METHOD_NAME},e);

            // DBロールバック
            if(dbcon != null) {
                dbcon.rollback();
            }
            throw e;

        } catch (WACSSysException e) {
            //エラーログ出力
            logError(MSG_SKKS0104,
                new Object[]{getClass().getName(),RLRRG_METHOD_NAME},e);

            // DBロールバック
            if(dbcon != null) {
                dbcon.rollback();
            }
            throw e;

        } finally {
            if(dbcon != null) {
                dbcon.close();
            }
        }

    }

    private Object ns(Object o){
        if(o == null){
            return "";
        }else{
            return o;
        }
    }
}
