/*******************************************************************
 *   システム名：
 *   サブシステム名：
 *   処理名：
 *   処理概要：
 *   ファイル名:  RLRRG004_B01_U07.java
 ******************************************************************/
package jp.co.btm.irl.rlr.rg004 ;

import java.util.Hashtable;
import java.util.Enumeration;
import com.ibm.jp.wacs.CraftsTransaction;
import com.ibm.jp.wacs.WACSSysException;
import com.ibm.jp.wacs.WACSApplException;
import com.ibm.jp.wacs.CraftsDataBean;
import com.ibm.jp.wacs.WACSUser;
import com.ibm.jp.wacs.db.CraftsDBConnector;
import com.ibm.jp.wacs.db.CraftsDBParam;
import jp.co.btm.irl.rlr.rg000.*;


/**
 *   <b>計数画面－登録処理</b>
 *   計数情報画面の計数情報の登録処理を行う。
 *   @author  M.Nitami
 *
 * Date        Name        Reason for change
 * ------------------------------------------------------------------
 * 2002/12/6   M.Nitami    新規作成
 */
public class RLRRG004_B01_U07 extends CraftsTransaction
                  implements IRingi, IRingiItem, IRingiMsg, IRingiItemKeisu {

    private CraftsDataBean    ibean   = null;
    private CraftsDataBean    obean   = null;

    private CraftsDBConnector dbcon   = null;
    private CraftsDBParam     dbparam = null;

    private Hashtable hstComBasket  = null;
    private Hashtable hstKey        = null;
    private Hashtable hstWF         = null;
    private Hashtable hstDB         = null;
    private Hashtable hstHOST       = null;

    private static final String strHidukeErrMsg = "入力された日付" ;

    /**
     *   <b>メソッド概要：</b>
     *   コンストラクタ。
     */
    public RLRRG004_B01_U07() {
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
     *   計数情報画面の計数情報の登録処理を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @exception  WACSSysException
     *   @exception  WACSApplException
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
            RLRRGCOM_RINGI ringiCom = new RLRRGCOM_RINGI( folder, dbcon, dbparam ) ;

            // 共有情報の生成と初期化を行う
            hstComBasket = ringiCom.initialComBasket(ibean);

            // 操作者ユーザーIDを取得する。
            WACSUser user    = folder.getUser();
            String strUserId = user.getUserID();

            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA );
            hstKey.put( F_USER_ID, strUserId );
            hstComBasket.put( K_KEY_DATA, hstKey );



            // 計数業務共通クラスのインスタンスを取得する
            RLRRG004_B01 keisuCom = new RLRRG004_B01( folder, dbcon, dbparam ) ;

            // 禀議共通ＤＢクラスのインスタンスを取得する
            // RLRRGCOM_DB dbCom = new RLRRGCOM_DB( folder, dbcon, dbparam ) ;

            // 禀議個別ＤＢクラスのインスタンスを取得する
            RLRRG004_B01_DB keisuDB = new RLRRG004_B01_DB( folder, dbcon, dbparam ) ;

            // 禀議共通ＷＦクラスのインスタンスを取得する
            // RLRRGCOM_WF wfCom = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;



            // ユーザーＩＤ、店ＣＩＦを共有情報に設定する
            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA ) ;
            hstKey.put( F_BRNO,    ibean.getString( F_BRNO    ) ) ;
            hstKey.put( F_TRISKNO, ibean.getString( F_TRISKNO ) ) ;
            hstComBasket.put( K_KEY_DATA, hstKey ) ;
            hstDB = (Hashtable)hstComBasket.get(K_DB_DATA);

            /*
             * 入力情報全てをＤＢハッシュに設定する
             */
            String[] keys = ibean.getKeyNames() ;
            for(int i = 0 ; i < keys.length ; i++ ) {

                if( ibean.getArraySize( keys[i] ) < 0 ) {
                    hstDB.put( keys[i], ibean.getString( keys[i] ) ) ;

                } else {
                    hstDB.put( keys[i], ibean.getStringArray( keys[i] ) ) ;
                }
            }


            // 入力情報で一括で取得できないもの（配列データ）を
            // 一時ハッシュに格納する
            keisuCom.setInArrayToHash( ibean, hstDB );
            hstComBasket.put( K_DB_DATA, hstDB ) ;

            /*
             * オーバーフロー項目と日付の整合性のチェック
             */
            rc = keisuCom.checkOverFlow( hstComBasket ) ;


            // 日付の入力エラー
            if( rc == -1 ) {

                // rlrrgs1041w
                String strMessageID   = MSG_RRGS1041 ;
                String[] strText = { strHidukeErrMsg } ;
                String strMessageText = getMessageText(strMessageID, strText);

                obean.setString( F_SUCCESS_FLAG, V_FALSE             ) ;
                obean.setString( F_ERROR_ID    , strMessageID        ) ;
                obean.setString( F_ERROR_TYPE  , CD_ERR_TYPE_WARNING ) ;
                obean.setString( F_ERROR_MSG   , strMessageText      ) ;

                dbcon.commit() ;
                return ;


            // オーバーフロー等の発生時
            } else if( rc == -2 ) {

                // rlrrgs1068w
// 2003/04/18 CHG@S.SEIMURA メッセージ変更
//              String strMessageID = MSG_RRGS1040;
                String strMessageID = MSG_RRGS1068;
                String strMessageText = getMessageText( strMessageID, null ) ;

                obean.setString( F_SUCCESS_FLAG, V_FALSE             ) ;
                obean.setString( F_ERROR_ID    , strMessageID        ) ;
                obean.setString( F_ERROR_TYPE  , CD_ERR_TYPE_WARNING ) ;
                obean.setString( F_ERROR_MSG   , strMessageText      ) ;

                dbcon.commit() ;
                return ;

            }


            /*
             * 取得した計数情報をＤＢに登録する
             */

            keisuCom.setHashToHash(hstDB, hstKey);
            hstComBasket.put( K_KEY_DATA, hstKey ) ;

            keisuDB.setAllData( hstComBasket ) ;


            /*
             * ＤＢへの登録に失敗した時
             */


            /*
             * 出力データの設定
             * CraftsErrBeanを返す
             */
            obean.setString( F_SUCCESS_FLAG, V_TRUE ) ;

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
