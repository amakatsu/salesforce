package jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces;

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;

/**
 * 計数情報(禀議計数補正値) テーブルに対する DB アクセス契約。
 */
public interface RinsashoKeisuHoseichiRepository {

    /**
     * 主キー（店番・取引先番号）と削除フラグ条件でレコードを更新する。
     *
     * @param record 更新対象（PK と更新カラム値を保持、非 null）
     * @return UPDATE 件数。0 件なら新規登録すべき
     * @throws NullPointerException 引数が null の場合
     */
    int updateByPrimaryKeyAndDelFlg(RinsashoKeisuHoseichi record);

    /**
     * 新規レコードを追加する。
     *
     * @param record 登録対象（PK と全カラム値を保持、非 null）
     * @return INSERT 件数（通常 1）
     * @throws NullPointerException 引数が null の場合
     */
    int insert(RinsashoKeisuHoseichi record);
}
