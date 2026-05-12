package jp.mufg.bk.yus.infra.mapper.tables;

import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.brNo;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.cmNo;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.correctionReason;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.delFlg;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.exclusiveCount;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.exclusiveKey;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.forexCreditTotalCorrectionValue;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.internalJpyCorrectionValue;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.loanDiscTotalCorrectionValue;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.regulationTanpoCorrectionValueJikaBase;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.regulationTanpoCorrectionValueRegulationValue;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.rinsashoKeisuHoseichi;
import static jp.mufg.bk.yus.infra.mapper.tables.support.RinsashoKeisuHoseichiTable.shiShoTotalCorrectionValue;
import static org.mybatis.dynamic.sql.SqlBuilder.isEqualTo;
import org.apache.ibatis.annotations.Mapper;
import org.mybatis.dynamic.sql.util.mybatis3.CommonInsertMapper;
import org.mybatis.dynamic.sql.util.mybatis3.CommonUpdateMapper;
import org.mybatis.dynamic.sql.util.mybatis3.MyBatis3Utils;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;

/** 計数情報(禀議計数補正値) テーブルへの単一テーブル CRUD を担う MyBatis Mapper。 */
@Mapper
public interface RinsashoKeisuHoseichiMapper extends
        CommonInsertMapper<TRgKeisuHoseichi>,
        CommonUpdateMapper {

    /**
     * 主キー（店番・取引先番号）と削除フラグ条件で計数情報(禀議計数補正値) を更新する。
     *
     * @param row 更新対象レコード（PK と更新カラム値を保持、非 null）
     * @return UPDATE 件数（0 または 1）
     */
    default int updateByPrimaryKeyAndDelFlg(TRgKeisuHoseichi row) {
        return MyBatis3Utils.update(this::update, rinsashoKeisuHoseichi, c ->
                c.set(loanDiscTotalCorrectionValue).equalTo(row::getLoanDiscTotalCorrectionValue)
                 .set(internalJpyCorrectionValue).equalTo(row::getInternalJpyCorrectionValue)
                 .set(forexCreditTotalCorrectionValue).equalTo(row::getForexCreditTotalCorrectionValue)
                 .set(shiShoTotalCorrectionValue).equalTo(row::getShiShoTotalCorrectionValue)
                 .set(regulationTanpoCorrectionValueRegulationValue).equalTo(row::getRegulationTanpoCorrectionValueRegulationValue)
                 .set(regulationTanpoCorrectionValueJikaBase).equalTo(row::getRegulationTanpoCorrectionValueJikaBase)
                 .set(correctionReason).equalTo(row::getCorrectionReason)
                 .where(brNo,   isEqualTo(row::getBrno))
                 .and(cmNo,     isEqualTo(row::getCmNo))
                 .and(delFlg,   isEqualTo(row::getDelFlg)));
    }

    /**
     * 計数情報(禀議計数補正値) に新規レコードを追加する。
     *
     * @param row 登録対象レコード（PK と全カラム値を保持、非 null）
     * @return INSERT 件数（通常 1）
     */
    default int insert(TRgKeisuHoseichi row) {
        return MyBatis3Utils.insert(this::insert, row, rinsashoKeisuHoseichi, c ->
                c.map(brNo).toProperty("brno")
                 .map(cmNo).toProperty("cmNo")
                 .map(delFlg).toProperty("delFlg")
                 .map(loanDiscTotalCorrectionValue).toProperty("loanDiscTotalCorrectionValue")
                 .map(internalJpyCorrectionValue).toProperty("internalJpyCorrectionValue")
                 .map(forexCreditTotalCorrectionValue).toProperty("forexCreditTotalCorrectionValue")
                 .map(shiShoTotalCorrectionValue).toProperty("shiShoTotalCorrectionValue")
                 .map(regulationTanpoCorrectionValueRegulationValue).toProperty("regulationTanpoCorrectionValueRegulationValue")
                 .map(regulationTanpoCorrectionValueJikaBase).toProperty("regulationTanpoCorrectionValueJikaBase")
                 .map(correctionReason).toProperty("correctionReason")
                 .map(exclusiveKey).toProperty("exclusiveKey")
                 .map(exclusiveCount).toProperty("exclusiveCount"));
    }
}
