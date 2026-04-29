/*******************************************************************
 *   システム名：
 *   サブシステム名：
 *   処理名：
 *   処理概要：
 *   ファイル名:  RLRRG004_B01_U05.java
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

/**
 *   <b>計数画面－計算イベント処理</b>
 *   計数情報画面のデータの計算処理を行う。
 *   @author  M.Nitami
 *
 * Date        Name        Reason for change
 * ------------------------------------------------------------------
 * 2002/11/27  M.Nitami    新規作成
 * 2009/06/23  R.Matsumura 【Day2.1】融資管理システム・Crafts!対応(GEC20-C-059)<BR>
 * 2011/11/18  M.Hayashi  【中計案件(8)】Crafts!保全率表示機能(GEC23-C-051)<BR>
 */
public class RLRRG004_B01_U05 extends CraftsTransaction
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
    public RLRRG004_B01_U05() {
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
 *   計数情報画面の表示データとＤＢに登録されているデータの差分計算を行い、
 *   それを元にして計算項目のの計算処理を行う。<BR>
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


            // ＤＢクラスの全項目取得より、計数情報を取得
            // パラメータは案件番号と補正区分（0固定）

            hstKey.put( F_LC_NO, ibean.getString( F_LC_NO ) ) ;
            hstKey.put( F_HOSEIKUBUN, new String("0") ) ;
            hstComBasket.put( K_KEY_DATA, hstKey ) ;

            keisuDB.getAllData( hstComBasket ) ;


            // ＤＢクラスメソッドの実行結果がNOT FOUNDの時
            // 対象のレコードが無い時は、初期表示時に計算ボタンが
            // 押せなくなっているので、考慮しなくて良い



            // 入力情報を一時ハッシュに格納
            Hashtable tbl = new Hashtable() ;
            Hashtable sabun = new Hashtable() ;
            String[] keys = ibean.getKeyNames() ;
            for(int i = 0; i < keys.length; i++) {

                if( ibean.getArraySize( keys[i] ) < 0 ) {
                    tbl.put( keys[i], ibean.getString( keys[i] ) ) ;

                } else {
                    tbl.put( keys[i], ibean.getStringArray( keys[i] ) ) ;
                }
            }


            // 入力情報で一括で取得できないもの（配列データ）を
            // 一時ハッシュに格納する
            keisuCom.setInArrayToHash( ibean, tbl );


            /*
             * 一般与信項目の入力データとＤＢデータとの差分を取得する
             * この時の差分とは、（入力データ）－（ＤＢデータ）
             * ただし、合計項目の差分は、各差分を計算したもの
             */
            // keisuCom.computeDiff( tbl, hstComBasket ) ;

            /*
             * 差分を使用しての一般与信項目計算と、それ以外の計算を行う
             */
            keisuCom.computeYosinKeisan( tbl, hstComBasket ) ;
//2009/06/23 CHG@R.Matsumura GEC20-C-059 start
//          keisuCom.computeKokyaku( hstComBasket ) ;
            keisuCom.computeKokyakuSabunKeisan(tbl, hstComBasket);

            //hstComBasketに差分計算済みデータを設定
            hstComBasket.put(K_DB_DATA, tbl);

            //共通化させた一般与信以外の計算処理を行う。
            keisuCom.computeKokyaku2( hstComBasket ) ;
//2009/06/23 CHG@R.Matsumura GEC20-C-059 end
            keisuCom.computeKokyakuKeisan( hstComBasket ) ;     // 2003/04/17 ADD@S.SEIMURA
            keisuCom.computeHozen( hstComBasket ) ;             // 2011/11/9 ADD@M.Hayashi GEC23-C-051


            /*
             * 出力データの設定
             */
            keisuCom.setOutData( ibean, obean, hstComBasket ) ;


            /*
             *
             */
// 2003/04/07 ADD@S.SEIMURA
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
