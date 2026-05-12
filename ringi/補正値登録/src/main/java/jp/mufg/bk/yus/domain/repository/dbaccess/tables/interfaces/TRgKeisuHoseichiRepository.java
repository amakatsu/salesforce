package jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces;

import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.base.TRgKeisuHoseichiBaseRepository;

/**
 * 計数情報(禀議計数補正値) テーブルへの本サービス用 Repository。
 *
 * <p>共通 CRUD は {@link TRgKeisuHoseichiBaseRepository} に集約し、
 * 本 interface は本サービス固有の差分操作を出すための拡張ポイントとして用意する。</p>
 */
public interface TRgKeisuHoseichiRepository extends TRgKeisuHoseichiBaseRepository {
}
