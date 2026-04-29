/*******************************************************************
 *   システム名：
 *   サブシステム名：
 *   処理名：
 *   処理概要：
 *   ファイル名:  RLRRG004_B01_U06.java
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
import jp.co.btm.irl.rlt.cf001.RLTCF001_004_R01;

/**
 *   <b>計数画面－補正値登録処理</b>
 *   計数情報画面の補正値の登録処理を行う。
 *   @author  M.Nitami
 *
 * Date        Name        Reason for change
 * ------------------------------------------------------------------
 * 2002/12/6   M.Nitami    新規作成
 * 2009/06/23  R.Matsumura 【Day2.1】融資管理システム・Crafts!対応(GEC20-C-059)
 * 2010/02/04  R.Matsumura 貸外逆集約対応(変更管理)(GEC21-C-025)
 */
public class RLRRG004_B01_U06 extends CraftsTransaction
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


    /**
     *   <b>メソッド概要：</b>
     *   コンストラクタ。
     */
    public RLRRG004_B01_U06() {
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
     *   計数情報画面の補正値の登録処理を行う。<BR>
     *   </DD></DT>
     *   </DL>
     *   <BR>
     *   @exception  WACSSysException
     *   @exception  com.ibm.jp.wacs.db.WACSDBException
     */
    protected void doProcess()
                        throws WACSSysException,com.ibm.jp.wacs.db.WACSDBException,WACSApplException    {

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
            // RLRRG004_B01 keisuCom = new RLRRG004_B01( folder, dbcon, dbparam ) ;

            // 禀議共通ＤＢクラスのインスタンスを取得する
            // RLRRGCOM_DB dbCom = new RLRRGCOM_DB( folder, dbcon, dbparam ) ;

            // 計数共通ＤＢクラスのインスタンスを取得する
            RLRRG004_B01_DB keisuDB = new RLRRG004_B01_DB( folder, dbcon, dbparam ) ;

            // 禀議共通ＷＦクラスのインスタンスを取得する
            // RLRRGCOM_WF wfCom = new RLRRGCOM_WF( folder, dbcon, dbparam ) ;



            // ユーザーＩＤ、店ＣＩＦを共有情報に設定する
            hstKey = (Hashtable)hstComBasket.get( K_KEY_DATA ) ;

// 2010/02/04 CHG@R.Matsumura GEC21-C-025 start
// 設定する店ＣＩＦの取得元を移管後のデータに変更
//          hstKey.put( F_BRNO,    ibean.getString( F_BRNO    ) ) ;
//          hstKey.put( F_TRISKNO, ibean.getString( F_TRISKNO ) ) ;
            //(移管後)取引先貸外店番を取得し、3桁->7桁変換をかける。
            RLTCF001_004_R01 cngdeff = new RLTCF001_004_R01( folder );
            hstKey.put( F_BRNO,    cngdeff.getSeverTenban( ibean.getString( F_BRNO_IKNATO ) ) ) ;
            hstKey.put( F_TRISKNO, ibean.getString( F_TRISKNO_IKNATO ) ) ;
// 2010/02/04 CHG@R.Matsumura GEC21-C-025 end

            // hstComBasket.put( K_KEY_DATA, hstKey ) ;


            /*
             * 補正値全て（４つ）をＤＢハッシュに設定する
             */
            hstKey.put( F_HOSCH, ibean.getStringArray( F_HOSCH ) ) ;
            hstKey.put( F_HOSRSN, ibean.getString( F_HOSRSN ) ) ;
//2009/06/23 ADD@R.Matsumura GEC20-C-059 start
            // 規定担保補正値の設定を追加
            hstKey.put( F_HIKIATE_KITEITI_TOT, ibean.getStringArray( F_HIKIATE_KITEITI_TOT ) ) ;
            hstKey.put( F_HIKIATE_JIKA_TOT, ibean.getStringArray( F_HIKIATE_JIKA_TOT ) ) ;
//2009/06/23 ADD@R.Matsumura GEC20-C-059 end
            hstComBasket.put( K_KEY_DATA, hstKey ) ;


            keisuDB.setHoseichi( hstComBasket ) ;


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
