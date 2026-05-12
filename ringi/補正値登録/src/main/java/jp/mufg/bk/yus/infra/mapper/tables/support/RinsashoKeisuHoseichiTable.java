package jp.mufg.bk.yus.infra.mapper.tables.support;

import java.sql.JDBCType;
import org.mybatis.dynamic.sql.SqlColumn;
import org.mybatis.dynamic.sql.SqlTable;

/**
 * 計数情報(禀議計数補正値) テーブルの MyBatis Dynamic SQL 用 Table support。
 *
 * <p>⚠ テーブル物理名・カラム物理名は仮値（実物理名未確定、E-17 escalation 参照）。</p>
 */
public final class RinsashoKeisuHoseichiTable extends SqlTable {

    public static final RinsashoKeisuHoseichiTable rinsashoKeisuHoseichi = new RinsashoKeisuHoseichiTable();

    public final SqlColumn<String>  brNo                                          = column("BR_NO",                                              JDBCType.VARCHAR);
    public final SqlColumn<String>  cmNo                                          = column("CM_NO",                                              JDBCType.VARCHAR);
    public final SqlColumn<String>  delFlg                                        = column("DEL_FLG",                                            JDBCType.VARCHAR);
    public final SqlColumn<Integer> loanDiscTotalCorrectionValue                  = column("LOAN_DISC_TOTAL_CORRECTION_VALUE",                   JDBCType.INTEGER);
    public final SqlColumn<Integer> internalJpyCorrectionValue                    = column("INTERNAL_JPY_CORRECTION_VALUE",                      JDBCType.INTEGER);
    public final SqlColumn<Integer> forexCreditTotalCorrectionValue               = column("FOREX_CREDIT_TOTAL_CORRECTION_VALUE",                JDBCType.INTEGER);
    public final SqlColumn<Integer> shiShoTotalCorrectionValue                    = column("SHI_SHO_TOTAL_CORRECTION_VALUE",                     JDBCType.INTEGER);
    public final SqlColumn<Integer> regulationTanpoCorrectionValueRegulationValue = column("REGULATION_TANPO_CORRECTION_VALUE_REGULATION_VALUE", JDBCType.INTEGER);
    public final SqlColumn<Integer> regulationTanpoCorrectionValueJikaBase        = column("REGULATION_TANPO_CORRECTION_VALUE_JIKA_BASE",        JDBCType.INTEGER);
    public final SqlColumn<String>  correctionReason                              = column("CORRECTION_REASON",                                  JDBCType.VARCHAR);
    public final SqlColumn<String>  exclusiveKey                                  = column("EXCLUSIVE_KEY",                                      JDBCType.VARCHAR);
    public final SqlColumn<Integer> exclusiveCount                                = column("EXCLUSIVE_COUNT",                                    JDBCType.INTEGER);

    private RinsashoKeisuHoseichiTable() {
        super("RINSASHO_KEISU_HOSEICHI");
    }
}
