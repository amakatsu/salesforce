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

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
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
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_正常系_PK一致+DEL_FLG=0のとき、補正値カラムを更新し件数1を返すこと（EXCLUSIVE_*は不変）_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_UPDATE_DATASET)
            void testUpdateByPrimaryKeyAndDelFlg_updatesCorrectionValueColumns() {
                // Arrange: PK 一致行への更新値をセット
                TRgKeisuHoseichi row = pkRow("0000010", "9019149", "0");
                row.setLoanDiscTotalCorrectionValue(11111);
                row.setInternalJpyCorrectionValue(22222);
                row.setForexCreditTotalCorrectionValue(33333);
                row.setShiShoTotalCorrectionValue(44444);
                row.setRegulationTanpoCorrectionValueRegulationValue(55555);
                row.setRegulationTanpoCorrectionValueJikaBase(66666);
                row.setCorrectionReason("UPDATE_REASON");

                // Act: テスト対象のメソッドを実行
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // Assert: 件数 1 を返すこと（DB 値は @ExpectedDataSet で検証）
                assertThat(actual).isEqualTo(1);
            }

            @Test
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_正常系_補正値・補正理由をnullで更新したとき、件数1を返し対象行がNULLクリアされること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_UPDATE_NULL_DATASET)
            void testUpdateByPrimaryKeyAndDelFlg_withNullCorrectionValues_clearsColumns() {
                // Arrange: PK のみ設定、補正値カラムは Entity 既定の null
                TRgKeisuHoseichi row = pkRow("0000010", "9019149", "0");

                // Act: テスト対象のメソッドを実行
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // Assert: 件数 1（DB 値は @ExpectedDataSet で NULL クリア検証）
                assertThat(actual).isEqualTo(1);
            }
        }

        @Nested
        @DisplayName("対象外")
        class 対象外 {

            @Test
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_準正常系_PK不一致のとき、件数0を返しDBは初期状態のままとなること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void testUpdateByPrimaryKeyAndDelFlg_withNonMatchingPk_returnsZeroAndDbUnchanged() {
                // Arrange: 存在しない取引先番号で更新試行
                TRgKeisuHoseichi row = pkRow("0000010", "9999999", "0");
                row.setLoanDiscTotalCorrectionValue(99999);

                // Act: テスト対象のメソッドを実行
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // Assert: 件数 0
                assertThat(actual).isZero();
            }

            @Test
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_準正常系_論理削除済(DEL_FLG=1)はDEL_FLG=0で検索すると件数0でDB不変となること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void testUpdateByPrimaryKeyAndDelFlg_withLogicallyDeletedRecord_excludesFromUpdate() {
                // Arrange: PK は存在するが削除済（DEL_FLG=1）の行を DEL_FLG="0" 条件で更新試行
                TRgKeisuHoseichi row = pkRow("0000020", "9019150", "0");
                row.setLoanDiscTotalCorrectionValue(11111);
                row.setCorrectionReason("SHOULD_NOT_APPLY");

                // Act: テスト対象のメソッドを実行
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // Assert: 件数 0
                assertThat(actual).isZero();
            }

            // UTR-021: 分岐判定のテストデータは境界値を設定（"1" / "9" / 半角空白 / 空文字）
            @ParameterizedTest(name = "delFlg={0}")
            @ValueSource(strings = {"1", "9", " ", ""})
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_準正常系_delFlgが0以外（非マッチ）のとき、件数0でDB不変となること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void testUpdateByPrimaryKeyAndDelFlg_withNonZeroDelFlg_excludesFromUpdate(String delFlg) {
                // Arrange: 既存 PK だが WHERE 条件 delFlg が初期データの "0" と非マッチ
                TRgKeisuHoseichi row = pkRow("0000010", "9019149", delFlg);
                row.setLoanDiscTotalCorrectionValue(11111);

                // Act: テスト対象のメソッドを実行
                int actual = sut.updateByPrimaryKeyAndDelFlg(row);

                // Assert: 件数 0
                assertThat(actual).isZero();
            }
        }

        @Nested
        @DisplayName("異常系")
        class 異常系 {

            @Test
            @DisplayName("updateByPrimaryKeyAndDelFlgメソッド_異常系_引数rowがnullのとき、NullPointerExceptionが伝搬すること（引数防衛）_1C4A")
            void testUpdateByPrimaryKeyAndDelFlg_withNullRow_throwsNpe() {
                // Arrange: 引数 row を null として準備

                // Act & Assert: NPE 伝搬とメッセージを検証
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
            @DisplayName("insertメソッド_正常系_新規PKで全カラム値ありの場合、件数1を返し新規行がDBに追加されること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_INSERT_DATASET)
            void testInsert_withAllColumnsPopulated_returnsOne() {
                // Arrange: 新規 PK で全カラム値ありの行を準備
                TRgKeisuHoseichi row = pkRow("0000030", "9019160", "0");
                row.setLoanDiscTotalCorrectionValue(70000);
                row.setInternalJpyCorrectionValue(80000);
                row.setForexCreditTotalCorrectionValue(90000);
                row.setShiShoTotalCorrectionValue(100000);
                row.setRegulationTanpoCorrectionValueRegulationValue(110000);
                row.setRegulationTanpoCorrectionValueJikaBase(120000);
                row.setCorrectionReason("INSERT_REASON");
                row.setExclusiveKey("rkANKEN333333333333");
                row.setExclusiveCount(0);

                // Act: テスト対象のメソッドを実行
                int actual = sut.insert(row);

                // Assert: 件数 1
                assertThat(actual).isEqualTo(1);
            }

            @Test
            @DisplayName("insertメソッド_正常系_補正値・補正理由をnullで登録の場合、件数1を返し当該カラムがNULLの行がDBに追加されること_1B4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = AFTER_INSERT_NULL_DATASET)
            void testInsert_withNullCorrectionValues_succeeds() {
                // Arrange: 補正値・補正理由は未設定（null）。NOT NULL 制約のあるカラムのみ値を持つ
                TRgKeisuHoseichi row = pkRow("0000030", "9019160", "0");
                row.setExclusiveKey("rkANKEN333333333333");
                row.setExclusiveCount(0);

                // Act: テスト対象のメソッドを実行
                int actual = sut.insert(row);

                // Assert: 件数 1
                assertThat(actual).isEqualTo(1);
            }
        }

        @Nested
        @DisplayName("異常系")
        class 異常系 {

            @Test
            @DisplayName("insertメソッド_異常系_既存PKと重複したとき、PersistenceExceptionが伝搬すること（一意制約違反_握りつぶし禁止）_1C4BD")
            @DataSet(value = INITIAL_DATASET, cleanBefore = true)
            @ExpectedDataSet(value = INITIAL_DATASET)
            void testInsert_withDuplicatePk_propagatesPersistenceException() {
                // Arrange: 初期データと同じ PK で登録試行
                TRgKeisuHoseichi row = pkRow("0000010", "9019149", "0");
                row.setLoanDiscTotalCorrectionValue(99999);
                row.setExclusiveKey("rkANKEN999999999999");
                row.setExclusiveCount(0);

                // Act & Assert: PersistenceException が伝搬すること
                assertThatThrownBy(() -> sut.insert(row))
                        .isInstanceOf(PersistenceException.class);
            }

            @Test
            @DisplayName("insertメソッド_異常系_引数rowがnullのとき、NullPointerExceptionが伝搬すること（引数防衛）_1C4A")
            void testInsert_withNullRow_throwsNpe() {
                // Arrange: 引数 row を null として準備

                // Act & Assert: NPE 伝搬とメッセージを検証
                assertThatNullPointerException()
                        .isThrownBy(() -> sut.insert(null))
                        .withMessageContaining("record");
            }
        }
    }

    private static TRgKeisuHoseichi pkRow(String brNo, String cmNo, String delFlg) {
        TRgKeisuHoseichi e = new TRgKeisuHoseichi();
        e.setBrno(brNo);
        e.setCmNo(cmNo);
        e.setDelFlg(delFlg);
        return e;
    }
}
