/*******************************************************************
 *   システム名：
 *   サブシステム名：
 *   処理名：
 *   処理概要：
 *   ファイル名:  RLRRG004_B02_R01.java
 ******************************************************************/
package jp.co.btm.irl.rlr.rg004;

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
import jp.co.btm.irl.rlt.cf001.*;


/**
 *   <b>利率変更(計数情報)画面－初期表示：初期表示イベント処理</b>
 *   利率変更(計数情報)画面の新規処理およびデータの取得処理を行う。
 *   @author  K.Sato
 *
 * Date        Name        Reason for change
 * ------------------------------------------------------------------
 * 2002/12/16  K.Sato      新規作成
 *
 * 2003/10/07  K.Sato      STEP2反映
 * 2004/01/16  S.Seimura   レベルアップGEC15-C-080-214対応
 */


public class RLRRG004_B02_R01
    extends CraftsTransaction
    implements IRingiMsg, IRingiWF, IRingi, IRingiItem, IRingiItemRihenKeisu{

    private CraftsDataBean  ibean   = null;
    private CraftsDataBean  obean   = null;

    private CraftsDBConnector dbcon = null;
    private CraftsDBParam dbparam = null;

    private Hashtable hstComBasket = null;
    private Hashtable hstKey = null;
    private Hashtable hstWF = null;
    private Hashtable hstDB = null;

    private static final String str1 = "1";
    private static final String strCp_No = "0000000000";
    private static final String strReqId = "rlrrg004_b02_r01";
    private static final String F_PROP_CHANGE_EXECUTE = "rlrPropChangeExecute";
    private static final int intBtnCnt = 6;


    /**
     *   <b>メソッド概要：</b>
     *   コンストラクタ。
     */
    public RLRRG004_B02_R01() {
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
        return true;
    }


    /**
     *　 <DL>
     *   <DT><b>メソッド概要:</b><DD>
     *   計数情報画面の新規処理およびデータの取得処理を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @exception  WACSException
     */
    protected void doProcess() throws WACSSysException, com.ibm.jp.wacs.db.WACSDBException , WACSApplException{

        try {


            // 入力データビーンを取得する
            ibean = getInDataBean();


            // 出力データビーンを取得する
            obean = getOutDataBean();


            // DB接続インスタンス(オートコミットOFF)を取得する
            dbcon = connect(false);
            dbparam = getDBParam();


            // 禀議業務共通クラスのインスタンスを取得する
            RLRRGCOM_RINGI ringiCom = new RLRRGCOM_RINGI(folder, dbcon, dbparam);


            // 共有情報の生成と初期化を行う
            hstComBasket = ringiCom.initialComBasket(ibean);


            // ボタン制御用の項目を定義
            String[] strBtn = new String[intBtnCnt] ;
            int intNo = 0 ;
            int intModeFlg = 0;

            // 基準日設定用項目を定義
            String strMkbi = null;

            // 操作者ユーザーIDを取得する。
            WACSUser user = folder.getUser();
            String strUserId = user.getUserID();

            //          hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA );
            //          hstKey.put( F_USER_ID, strUserId );
            //          hstComBasket.put( K_KEY_DATA, hstKey );


            // 計数業務共通クラスのインスタンスを取得する
            RLRRG004_B02 rihenkeisuCom = new RLRRG004_B02(folder, dbcon, dbparam);

            // 禀議共通ＤＢクラスのインスタンスを取得する
//          RLRRGCOM_DB dbCom = new RLRRGCOM_DB(folder, dbcon, dbparam);

            // 禀議個別ＤＢクラスのインスタンスを取得する
            RLRRG004_B02_DB rihenkeisuDB = new RLRRG004_B02_DB(folder, dbcon, dbparam);

            // 禀議共通ワークフロークラスのインスタンスを取得する
            RLRRGCOM_WF wfCom = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;

            // 項目属性管理クラスのインスタンスを取得する
            RLRRGCOM_PROP_BASE strProp = RLRRGCOM_PROP_FACT.getPropInstance(strReqId);

// 2003.10.07 Add K.Sato@STEP2  -->
            // カレンダークラスのインスタンスを生成する
            RLRCMCOM_CalendarWrapper Cal = new RLRCMCOM_CalendarWrapper(folder, dbcon, getDBParam());
// <--

            // パラメータ設定
            // 案件番号、店ＣＩＦ
            // ユーザー情報（ユーザーＩＤ、部店エリアコード、課・グループコード、役職順コード）
            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA ) ;
            hstKey.put( F_USER_ID, strUserId );
            hstComBasket.put( K_KEY_DATA, hstKey ) ;
            wfCom.getOperatorInfo(hstComBasket);

            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA );
            hstWF  = (Hashtable)hstComBasket.get( K_WF_DATA  );
            hstKey.put(F_USER_ID      , hstWF.get( F_USER_ID        ));
            hstKey.put(F_BUTEN_AREA_CD, hstWF.get( F_BUTEN_AREA_CD  ));
            hstKey.put(F_KA_GRP_CD    , hstWF.get( F_KA_GRP_CD      ));
            hstKey.put(F_SHOK_JUN     , hstWF.get( F_SHOK_JUN       ));
            hstKey.put(F_BRNO         , ibean.getString( F_BRNO     )) ;
            hstKey.put(F_TRISKNO      , ibean.getString( F_TRISKNO  )) ;
            hstKey.put(F_LC_NO        , ibean.getString( F_LC_NO    )) ;
            hstComBasket.put(K_KEY_DATA, hstKey) ;



            // ＤＢクラスの全項目取得より、計数情報を取得
            // パラメータは案件番号
            hstKey.put(F_LC_NO, ibean.getString(F_LC_NO));
            hstKey.put(F_HOSEIKUBUN, str1);
            hstComBasket.put(K_KEY_DATA, hstKey);

            rihenkeisuDB.getAllData(hstComBasket);


            /*
             * 特定ステータスの時、ボタン制御と項目を変更不可にする
             * 変更するステータスは
             * C060M:取消済, C070M:取下中, C080M:取下済, C090M:削除
             * C130M:否認, 　C170M:承認, 　C140M:承認[ホスト未]
             * C150M:承認[ホストエラー],   C160M:承認[変更有]
             */
            String strStatus = (String)ibean.getString(F_WF_STATUS);
            if( strStatus.equals( RC_STAT_TORIKESHIZUMI ) ||
                strStatus.equals( RC_STAT_TORISAGETYU   ) ||
                strStatus.equals( RC_STAT_TORISAGEZUMI  ) ||
                strStatus.equals( RC_STAT_SAKUJYO       ) ||
                strStatus.equals( RC_STAT_HININ         ) ||
                strStatus.equals( RC_STAT_HOST_MI       ) ||
                strStatus.equals( RC_STAT_HOST_ERR      ) ||
                strStatus.equals( RC_STAT_HOST_ARI      ) ||
                strStatus.equals( RC_STAT_SHONIN )      ) {
                intModeFlg = 1; // 照会モードで画面起動
            }

            // ＤＢクラスメソッドの実行結果がNOT FOUNDの時
            if (((Integer) hstComBasket.get(K_RETURN)).intValue() == RC_DATA_NOT_FOUND){

// 2003/03/10 ADD@S.SEIMURA DBのデータがなくてもヘッダー情報を表示する
                hstKey.put(F_BRNO,    ibean.getString(F_BRNO));
                hstKey.put(F_TRISKNO, ibean.getString(F_TRISKNO));
                hstComBasket.put(K_KEY_DATA, hstKey);

                rihenkeisuDB.getKeisuHeaderInfo(hstComBasket);

                // ボタンの制御
                // 使用不可ボタン：ファイル作成、登録、直近計数照会
                strBtn[intNo++] = B_FILMK;
                strBtn[intNo++] = B_ENT;
                strBtn[intNo++] = B_CKKEISUINQ;

// 2003.10.07 Change K.Sato@STEP2   -->
                // Add. M.Nitami 2003/1/23
                /*
                 * 照会・更新区分が「照会」の時、計数再取得も使用不可とする
                 * 計数情報がない場合でも、作成中以外は再取得不可とする。
                 */

//              // 禀議書が作成中かを判定する
//              hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
//              hstKey.put(F_LC_NO,  ibean.getString(F_LC_NO));
//              hstKey.put(F_CP_NO,  strCp_No);
//              hstKey.put(F_HANTEI, F_SAKUSEITYU_CHECK);
//              hstComBasket.put(K_KEY_DATA, hstKey);
//              wfCom.chkRingiStatus(hstComBasket);
//              int intKettei = ((Integer) hstComBasket.get(K_RETURN)).intValue() ;
//
//              if (ibean.getString(F_UPDATE_MODE_FLG).equals(V_UPDATE_SHOKAI_MODE)) {
//                  // 照会モードの場合
//                  strBtn[intNo++] = B_KSRESHUT;
//              } else if( intKettei != RC_SAKUSEITYU ) {
//                  // 作成中以外
//                  strBtn[intNo++] = B_KSRESHUT;
//              }

                strStatus = (String)ibean.getString(F_WF_STATUS);

                if (ibean.getString(F_UPDATE_MODE_FLG).equals(V_UPDATE_SHOKAI_MODE)) {
                    // 照会モードの場合
                    strBtn[intNo++] = B_KSRESHUT;
                } else if(  strStatus.equals(RC_STAT_SAKUSEITYU) == false   &&
                            strStatus.equals(RC_STAT_KAIFU) == false            &&
                            strStatus.equals(RC_STAT_RINGITYU) == false     ) {
                    // 作成中・回付中･禀議中以外

                    strBtn[intNo++] = B_KSRESHUT;
                }

                // 基準日の設定を行う
                hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

//              strTribi = Cal.getYearMonthDayWareki(strTribi, V_EMPTY_STRING, Cal.GGG_GENGO);

                hstDB.put(F_MKBI, Cal.getEigyoDay());
// <--
            }else{


                /*
                 * 色変情報の取得
                 */
                // 共有情報のDB入力パラメータを設定する。
                hstKey.put(F_LC_NO, ibean.getString(F_LC_NO));

// 2003.10.07 Add K.Sato@STEP2  -->
                // 取引日の取得・設定を行う
                hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

                if( hstDB.containsKey(F_MKBI) ){
                    if( ringiCom.cnvNullData( (String)hstDB.get(F_MKBI) ).length() > 0 ){

                        // DBに基準日が存在した場合
                        strMkbi = ringiCom.cnvNullData( (String)hstDB.get(F_MKBI) );
                    } else {
                        strMkbi = V_EMPTY_STRING;
                    }
                } else {

                    // DBに基準日が存在しない場合
                    strMkbi = Cal.getEigyoDay();
                }

                hstDB.put(F_MKBI, strMkbi);


                // ＤＢから取得したデータ全てをパラメータに設定する
                rihenkeisuCom.setHashToHash(hstDB, hstKey);
// <--

                hstComBasket.put(K_KEY_DATA, hstKey);

                // 色変項目取得メソッドを呼ぶと、共有情報内の
                // ＤＢデータが上書きされるので、複製を作ってメソッドを実行する
                Hashtable hstComBasket2 = ringiCom.initialComBasket(ibean);
                hstComBasket2.put(K_KEY_DATA, hstComBasket.get(K_DB_DATA));

                //色変チェック
                rihenkeisuDB.compareItemData(hstComBasket2);

                // 変更項目の色変を設定
                Hashtable hstTbl = (Hashtable)hstComBasket2.get(K_DB_DATA);

                strProp.setEditedColor((String[])hstTbl.get(F_UPDATE_ITEM));

                /*
                 * ボタン制御値の設定
                 */
                // 直近計数案件番号が取得できなかった時は
                // 直近計数照会ボタンを使用不可にする
                hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);
                String chkknLc_no = (String)hstDB.get(F_CKKKNKEISU_LC_NO);


                if(chkknLc_no == null || chkknLc_no.length() == 0) {
                    strBtn[intNo++] = B_CKKEISUINQ;
                }





                // 照会・更新区分が「照会」の時
                // if(hstComBasket.get(K_RETURN).equals(V_UPDATE_SHOKAI_MODE)) {
                if (ibean.getString(F_UPDATE_MODE_FLG).equals(V_UPDATE_SHOKAI_MODE)) {

                        /*
                         * 計数再取得・登録を使用不可にする
                         */
                        strBtn[intNo++] = B_KSRESHUT;
                        strBtn[intNo++] = B_ENT;


                // 照会・更新区分が「更新」の時
                } else {

                    String strStat = ibean.getString(F_WF_STATUS);

                    /*
                     * ＷＦのステータスで処理を振り分ける
                     */


// 2003/01/16 CHG@S.SEIMURA レベルアップGEC15-C-080-214
//            作成中以外でも、回付中、禀議中で計数再取得ボタンを使用可に変更。

//                  // Mod. M.Nitami 2003/1/23
//                  // 禀議書が作成中かを判定する
//                  hstKey = (Hashtable)hstComBasket.get(K_KEY_DATA);
//                  hstKey.put(F_LC_NO,  ibean.getString(F_LC_NO));
//                  hstKey.put(F_CP_NO,  strCp_No);
//                  hstKey.put(F_HANTEI, F_SAKUSEITYU_CHECK);
//                  hstComBasket.put(K_KEY_DATA, hstKey);
//                  wfCom.chkRingiStatus(hstComBasket);
//                  int intKettei = ((Integer) hstComBasket.get(K_RETURN)).intValue() ;
//
//                  // 作成中以外
//                  if( intKettei != RC_SAKUSEITYU ) {

                    // 作成中、回付中、禀議中以外の場合
                    if ( !strStat.equals( RC_STAT_SAKUSEITYU ) &&
                            !strStat.equals( RC_STAT_KAIFU ) &&
                            !strStat.equals( RC_STAT_RINGITYU ) ) {

//                      /*
//                       * 特定ステータスの時、ボタン制御と項目を変更不可にする
//                       * 変更するステータスは
//                       * C060M:取消済, C070M:取下中, C080M:取下済, C090M:削除
//                       * C130M:否認, 　C170M:承認, 　C140M:承認[ホスト未]
//                       * C150M:承認[ホストエラー],   C160M:承認[変更有]
//                       */
//                      String strStatus = (String)ibean.getString(F_WF_STATUS);
//                      if( strStatus.equals( RC_STAT_TORIKESHIZUMI ) ||
//                          strStatus.equals( RC_STAT_TORISAGETYU   ) ||
//                          strStatus.equals( RC_STAT_TORISAGEZUMI  ) ||
//                          strStatus.equals( RC_STAT_SAKUJYO       ) ||
//                          strStatus.equals( RC_STAT_HININ         ) ||
//                          strStatus.equals( RC_STAT_HOST_MI       ) ||
//                          strStatus.equals( RC_STAT_HOST_ERR      ) ||
//                          strStatus.equals( RC_STAT_HOST_ARI      ) ||
//                          strStatus.equals( RC_STAT_SHONIN )      ) {
//                              intModeFlg = 1;
//                      }

                        /*
                         * ステータスが決定以降かどうかでボタン制御を振り分ける
                         */
//                      hstKey.put(F_HANTEI, F_SHONIN_CHECK);
//                      hstComBasket.put(K_KEY_DATA, hstKey);
//                      wfCom.chkRingiStatus(hstComBasket);
//                      intKettei = ((Integer) hstComBasket.get(K_RETURN)).intValue() ;

//                      // 決定（承認）以降の時
//                      if( intKettei == RC_SHONIN_GO ) {

                        if( intModeFlg == 1 ) { // 登録できないステータスの場合
                            /*
                             *  計数再取得、登録を使用不可にする。
                             */
                            strBtn[intNo++] = B_KSRESHUT;
                            strBtn[intNo++] = B_ENT;


                        // 決定以外の場合
                        } else {
                            /*
                             *　計数再取得を使用不可にする
                             */
                            strBtn[intNo++] = B_KSRESHUT;
                        }

                    }


// 以下、ワークフローステータスの判定が変わったため、変更
//
//                  // WFステータスの取得
//                  String strStat = ibean.getString(F_WF_STATUS);
//
//                  /*
//                   * WFステータスで処理を振り分ける
//                   */
//                  // 承認(C170M)と辞書比較を行う
//                  int result = strStat.compareTo(IRingiWF.RC_STAT_SHONIN);
//
//                  // WFステータスが決定以降
//                  if(result >= IRingiWF.RC_ZERO){
//
//                      /*
//                       * 計数再取得・登録を使用不可にする
//                       */
//                      strBtn[intNo++] = B_KSRESHUT;
//                      strBtn[intNo++] = B_ENT;
//
//                  // WFステータスが作成中の時
//                  } else if(strStat.equals(RC_STAT_SAKUSEITYU)) {
//
//                      /*
//                       * 全てのボタンを使用可にする
//                       */
//
//                  // WFステータスが作成中以外の時
//                  } else {
//
//                      /*
//                       * 計数再取得を使用不可にする
//                       */
//                      strBtn[intNo++] = B_KSRESHUT;
//
//                  }
                }
            }


            // 出力データの設定
            rihenkeisuCom.getKamokuData(hstComBasket);

// 2003.10.07 Add K.Sato@STEP2  -->
            // 禀査番号の設定

            if( hstDB.containsKey(F_RSNO) &&
                ringiCom.cnvNullData( (String)hstDB.get(F_RSNO) ).length() == 4 ){

                // DBに禀査番号が存在する場合
                // 処理無し
                ;

            } else {

                // DBに禀査番号が存在しない場合
                // ibeanから取得した禀査番号を使用する
                hstDB.put(F_RSNO, ibean.getString(F_RSNO));
            }

            hstComBasket.put(K_DB_DATA, hstDB);
// <--

            rihenkeisuCom.setOutData(ibean, obean, hstComBasket);

            obean.setString("SUCCESS_FLAG", "true");

            // ボタンのプロテクトを実行
            strProp.setProtect(strBtn);

            // 設定した制御情報の全項目を取得
            RLRRGCOM_PROP_RES hsRes = strProp.getPropTables();
//          String[] strList = hsRes.getPropChangerList();
            String [] strFlg = {V_TRUE};
            obean.setStringArray(F_PROP_CHANGE_EXECUTE, strFlg);

            ringiCom.getOutDataBeanPropRes(obean, hsRes, strFlg) ;


// 2003/04/25 CHG@M.OTAKE 追加
            // 登録ボタンが使用不可の場合更新モードで画面起動
            for (int i=0;i<strBtn.length;i++) {
                if ( strBtn[i]!=null ) {
                    if ( strBtn[i].equals(B_ENT) ) {
                        intModeFlg = 1;
                    }
                }
            }

            // 更新モードで開かれて、特定のワークフローステータスの時は
            // 更新照会フラグに"false"を設定する(画面が照会モードで起動する）)
            if( intModeFlg == 1 ) {
                obean.setString(F_UPDATE_MODE_FLG, V_UPDATE_SHOKAI_MODE);
            }

            //コミットする（DB接続インスタンスがnullでない場合のみ）
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
}
