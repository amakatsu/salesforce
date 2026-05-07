package jp.mufg.bk.yus.infra.repository.dbaccess.tables.impl;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatNullPointerException;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.util.Objects;

import javax.sql.DataSource;

import org.apache.ibatis.exceptions.PersistenceException;
import org.apache.ibatis.io.Resources;
import org.apache.ibatis.jdbc.ScriptRunner;
import org.apache.ibatis.mapping.Environment;
import org.apache.ibatis.session.Configuration;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;
import org.apache.ibatis.transaction.jdbc.JdbcTransactionFactory;
import org.h2.jdbcx.JdbcDataSource;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import com.github.database.rider.core.api.configuration.DBUnit;
import com.github.database.rider.core.api.configuration.Orthography;
import com.github.database.rider.core.api.connection.ConnectionHolder;
import com.github.database.rider.core.api.dataset.DataSet;
import com.github.database.rider.core.api.dataset.ExpectedDataSet;
import com.github.database.rider.junit5.api.DBRider;

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.infra.mapper.tables.RinsashoKeisuHoseichiMapper;

/** {@link RinsashoKeisuHoseichiRepositoryImpl} の統合テスト（H2 + DBRider）。 */
@ExtendWith(com.github.database.rider.junit5.DBUnitExtension.class)
@DBRider
@DBUnit(caseInsensitiveStrategy = Orthography.UPPERCASE, allowEmptyFields = true)
class RinsashoKeisuHoseichiRepositoryImplTest {

    private static final String INITIAL_DATASET = "datasets/rinsasho_keisu_hoseichi_initial.yml";
    private static final String AFTER_UPDATE_DATASET = "datasets/after_update.yml";
    private static final String AFTER_UPDATE_NULL_DATASET = "datasets/after_update_null.yml";
    private static final String AFTER_INSERT_DATASET = "datasets/after_insert.yml";
    private static final String AFTER_INSERT_NULL_DATASET = "datasets/after_insert_null.yml";

    private static DataSource dataSource;
    private static SqlSessionFactory sqlSessionFactory;

    // フィールド名 connectionHolder は DBRider の反射規約により変更不可
    @SuppressWarnings("unused")
    private static final ConnectionHolder connectionHolder = () -> dataSource.getConnection();

    private SqlSession session;
    private RinsashoKeisuHoseichiRepositoryImpl sut;

    @BeforeAll
    static void setUpDatabase() throws Exception {
        // DB_CLOSE_DELAY=-1: 全 Connection クローズ後も in-memory DB を保持し、@BeforeEach 毎の再構築を不要にする
        JdbcDataSource ds = new JdbcDataSource();
        ds.setURL("jdbc:h2:mem:rinsasho_test;MODE=Oracle;DB_CLOSE_DELAY=-1");
        ds.setUser("sa");
        ds.setPassword("");
        dataSource = ds;

        runSchema();
        // SqlSessionFactory は重い構築のため @BeforeAll で 1 回だけ作る
        sqlSessionFactory = buildSqlSessionFactory(dataSource);
    }

    private static void runSchema() throws Exception {
        try (Connection c = dataSource.getConnection();
             Reader r = new InputStreamReader(
                     Objects.requireNonNull(
                             Resources.getResourceAsStream("schema.sql"),
                             "schema.sql not found on test classpath"),
                     StandardCharsets.UTF_8)) {
            ScriptRunner sr = new ScriptRunner(c);
            sr.setLogWriter(null);
            sr.setErrorLogWriter(null);
            sr.setStopOnError(true);
            sr.runScript(r);
        }
    }

    private static SqlSessionFactory buildSqlSessionFactory(DataSource ds) {
        Environment env = new Environment("test", new JdbcTransactionFactory(), ds);
        Configuration config = new Configuration(env);
        // SNAKE_CASE 物理カラム名 ↔ camelCase Entity フィールド名の自動マッピングで ResultMap 手書きを回避
        config.setMapUnderscoreToCamelCase(true);
        config.addMapper(RinsashoKeisuHoseichiMapper.class);
        return new SqlSessionFactoryBuilder().build(config);
    }

    @BeforeEach
    void setUpSut() {
        // autoCommit=true: 各 SQL 直後にコミットされ、DBRider の検証 Connection から即可視
        session = sqlSessionFactory.openSession(true);
        sut = new RinsashoKeisuHoseichiRepositoryImpl(
                session.getMapper(RinsashoKeisuHoseichiMapper.class));
    }

    @AfterEach
    void closeSession() {
        if (session != null) {
            session.close();
        }
    }

    @Nested
    @DisplayName("updateByPrimaryKeyAndDelFlg: 主キー + delFlg 一致行を更新する")
    class UpdateByPrimaryKeyAndDelFlg {

        @Nested
        @DisplayName("正常系")
        class 正常系 {

            @Test
            @DisplayName("PK 一致 + DEL_FLG=0 のとき、補正値カラムを更新し件数 1 を返す（EXCLUSIVE_* は不変）")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_UPDATE_DATASET)
            void 補正値カラムを更新する() {
                // given
                RinsashoKeisuHoseichi row = pkRow("0000010", "9019149", "0");
                row.setLoanDiscTotalCorrectionValue(11111);
                row.setInternalJpyCorrectionValue(22222);
                row.setForexCreditTotalCorrectionValue(33333);
                row.setShiShoTotalCorrectionValue(44444);
                row.setRegulationTanpoCorrectionValueRegulationValue(55555);
                row.setRegulationTanpoCorrectionValueJikaBase(66666);
                row.setCorrectionReason("UPDATE_REASON");

                // when
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // then
                assertThat(actual).isEqualTo(1);
            }

            @Test
            @DisplayName("補正値・補正理由を null で更新したとき、件数 1 を返し対象行が NULL クリアされる")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_UPDATE_NULL_DATASET)
            void null_クリアされる() {
                // given - PK のみ設定し、補正値カラムは Entity 既定の null のまま
                RinsashoKeisuHoseichi row = pkRow("0000010", "9019149", "0");

                // when
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // then
                assertThat(actual).isEqualTo(1);
            }
        }

        @Nested
        @DisplayName("対象外")
        class 対象外 {

            @Test
            @DisplayName("PK 不一致のとき、件数 0 を返し DB は初期状態のまま")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void PK不一致_件数0かつDB不変() {
                // given - 存在しない取引先番号
                RinsashoKeisuHoseichi row = pkRow("0000010", "9999999", "0");
                row.setLoanDiscTotalCorrectionValue(99999);

                // when
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // then
                assertThat(actual).isZero();
            }

            @Test
            @DisplayName("論理削除済 (DEL_FLG=1) は更新対象外で、DEL_FLG=0 で検索すると件数 0 かつ DB は不変")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void 削除済レコードは更新対象外() {
                // given - PK は存在するが削除済（DEL_FLG=1）の行を DEL_FLG="0" 条件で更新試行
                RinsashoKeisuHoseichi row = pkRow("0000020", "9019150", "0");
                row.setLoanDiscTotalCorrectionValue(11111);
                row.setCorrectionReason("SHOULD_NOT_APPLY");

                // when
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // then
                assertThat(actual).isZero();
            }

            @ParameterizedTest(name = "delFlg={0}")
            @ValueSource(strings = {"1", "9", " ", ""})
            @DisplayName("delFlg が \"0\" 以外（DEL_FLG=0 と非マッチ）のとき、件数 0 を返し DB は不変")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void delFlg_0以外は対象外(String delFlg) {
                // given - 既存 PK だが WHERE 条件 delFlg が初期データの "0" と一致しない
                RinsashoKeisuHoseichi row = pkRow("0000010", "9019149", delFlg);
                row.setLoanDiscTotalCorrectionValue(11111);

                // when
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // then
                assertThat(actual).isZero();
            }
        }

        @Nested
        @DisplayName("異常系")
        class 異常系 {

            @Test
            @DisplayName("引数 row が null のとき、NullPointerException を伝搬する（引数防衛）")
            void row_nullのときNPE() {
                // when / then
                assertThatNullPointerException()
                        .isThrownBy(() -> sut.updateByPrimaryKeyAndDelFlg(null))
                        .withMessageContaining("record");
            }
        }
    }

    @Nested
    @DisplayName("insert: 計数情報(禀議計数補正値) に新規レコードを追加する")
    class Insert {

        @Nested
        @DisplayName("正常系")
        class 正常系 {

            @Test
            @DisplayName("新規 PK で全カラム値あり: 件数 1 を返し、新規行が DB に追加される")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_INSERT_DATASET)
            void 全カラム値あり_INSERT件数1() {
                // given
                RinsashoKeisuHoseichi row = pkRow("0000030", "9019160", "0");
                row.setLoanDiscTotalCorrectionValue(70000);
                row.setInternalJpyCorrectionValue(80000);
                row.setForexCreditTotalCorrectionValue(90000);
                row.setShiShoTotalCorrectionValue(100000);
                row.setRegulationTanpoCorrectionValueRegulationValue(110000);
                row.setRegulationTanpoCorrectionValueJikaBase(120000);
                row.setCorrectionReason("INSERT_REASON");
                row.setExclusiveKey("rkANKEN333333333333");
                row.setExclusiveCount(0);

                // when
                int actual = sut.insert(row);

                // then
                assertThat(actual).isEqualTo(1);
            }

            @Test
            @DisplayName("補正値・補正理由を null で登録: 件数 1 を返し、当該カラムが NULL の行が DB に追加される")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_INSERT_NULL_DATASET)
            void 補正値null_INSERT成功() {
                // given - 補正値・補正理由は未設定（null）。NOT NULL 制約のあるカラムのみ値を持つ
                RinsashoKeisuHoseichi row = pkRow("0000030", "9019160", "0");
                row.setExclusiveKey("rkANKEN333333333333");
                row.setExclusiveCount(0);

                // when
                int actual = sut.insert(row);

                // then
                assertThat(actual).isEqualTo(1);
            }
        }

        @Nested
        @DisplayName("異常系")
        class 異常系 {

            @Test
            @DisplayName("既存 PK と重複したとき、PersistenceException を伝搬する（一意制約違反、握りつぶし禁止）")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void PK重複_PersistenceException伝搬() {
                // given - 初期データと同じ PK で登録試行
                RinsashoKeisuHoseichi row = pkRow("0000010", "9019149", "0");
                row.setLoanDiscTotalCorrectionValue(99999);
                row.setExclusiveKey("rkANKEN999999999999");
                row.setExclusiveCount(0);

                // when / then
                assertThatThrownBy(() -> sut.insert(row))
                        .isInstanceOf(PersistenceException.class);
            }

            @Test
            @DisplayName("引数 row が null のとき、NullPointerException を伝搬する（引数防衛）")
            void row_nullのときNPE() {
                // when / then
                assertThatNullPointerException()
                        .isThrownBy(() -> sut.insert(null))
                        .withMessageContaining("record");
            }
        }
    }

    private static RinsashoKeisuHoseichi pkRow(String brNo, String cmNo, String delFlg) {
        RinsashoKeisuHoseichi e = new RinsashoKeisuHoseichi();
        e.setBrNo(brNo);
        e.setCmNo(cmNo);
        e.setDelFlg(delFlg);
        return e;
    }
}
