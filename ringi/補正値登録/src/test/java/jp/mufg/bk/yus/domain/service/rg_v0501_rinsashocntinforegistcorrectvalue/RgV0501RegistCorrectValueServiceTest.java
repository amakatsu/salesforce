package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import java.sql.SQLException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.TRgKeisuHoseichiRepository;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.mapper.KeisuHoseichiEntityMapper;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;
import jp.mufg.bk.yus.lib.presentation.helper.domain.exclusive.interfaces.ExclusiveProcessHelper;

/**
 * {@link RgV0501RegistCorrectValueService} の単体テスト。
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("RgV0501RegistCorrectValueService")
class RgV0501RegistCorrectValueServiceTest {

    private static final String BR_NO = "010";
    private static final String SERVER_BR_NO = "0000010";
    private static final String CM_NO = "9019149";
    private static final String EXCLUSIVE_KEY = "rkANKEN111111111111";
    private static final int CLIENT_EXCLUSIVE_COUNT = 1;
    private static final int UPDATED_EXCLUSIVE_COUNT = 2;

    @Mock
    private TRgKeisuHoseichiRepository repository;

    @Mock
    private ExclusiveProcessHelper exclusiveProcessHelper;

    @Mock
    private KeisuHoseichiEntityMapper entityMapper;

    @InjectMocks
    private RgV0501RegistCorrectValueService sut;

    private RgV0501RegistCorrectValueServiceInput input;
    private TRgKeisuHoseichi entity;

    @BeforeEach
    void setUp() {
        input = newInput(BR_NO, CM_NO, EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT);
        entity = new TRgKeisuHoseichi();
    }

    @Nested
    @DisplayName("Step 1: インプット取得（引数防衛）")
    class Step1InputAcquisition {

        @Test
        @DisplayName("executeServiceメソッド_異常系_inputがnullの場合、NullPointerExceptionが送出され依存先がいずれも呼ばれないこと_1CE3A")
        void testExecuteService_withInputNull_throwsNpeAndCallsNoCollaborator() {
            // Arrange: テストの準備（特になし、null を直接渡す）

            // Act & Assert: テスト対象のメソッドを実行し、例外と依存未呼出を検証
            assertThatThrownBy(() -> sut.executeService(null))
                    .isInstanceOf(NullPointerException.class);

            verifyNoInteractions(repository);
            verifyNoInteractions(exclusiveProcessHelper);
            verifyNoInteractions(entityMapper);
        }

        @Test
        @DisplayName("executeServiceメソッド_異常系_input.lockInfoがnullの場合、NullPointerExceptionが送出され依存先がいずれも呼ばれないこと_1CE3A")
        void testExecuteService_withLockInfoNull_throwsNpeAndCallsNoCollaborator() {
            // Arrange: lockInfo を持たない input を準備
            final RgV0501RegistCorrectValueServiceInput bad =
                    new RgV0501RegistCorrectValueServiceInput();
            bad.setBrNo(BR_NO);
            bad.setCmNo(CM_NO);

            // Act & Assert: テスト対象のメソッドを実行し、例外と依存未呼出を検証
            assertThatThrownBy(() -> sut.executeService(bad))
                    .isInstanceOf(NullPointerException.class);

            verifyNoInteractions(repository);
            verifyNoInteractions(exclusiveProcessHelper);
            verifyNoInteractions(entityMapper);
        }
    }

    @Nested
    @DisplayName("Step 2: 排他更新回数チェック（楽観ロック）")
    class Step2ExclusiveCheck {

        @Test
        @DisplayName("executeServiceメソッド_正常系_exclusiveKeyとexclusiveCountがExclusiveProcessHelperにそのまま渡されること_1AB3A")
        void testExecuteService_passesExclusiveKeyAndCountToHelper() {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: 引数渡しと戻り値を検証
            verify(exclusiveProcessHelper).checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("executeServiceメソッド_異常系_排他チェックが例外を送出した場合、Step3以降を実行せず例外を伝搬すること_1CE3A")
        void testExecuteService_whenExclusiveCheckFails_propagatesAndSkipsLaterSteps() {
            // Arrange: 排他チェックで例外を投げるモック設定
            final RuntimeException exclusiveError =
                    new IllegalStateException("exclusive count mismatch");
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenThrow(exclusiveError);

            // Act & Assert: 同一例外が伝搬し、後続が呼ばれないことを検証
            assertThatThrownBy(() -> sut.executeService(input))
                    .isSameAs(exclusiveError);

            verifyNoInteractions(entityMapper);
            verify(repository, never()).updateByPrimaryKeyAndDelFlg(any());
            verify(repository, never()).insert(any());
        }
    }

    @Nested
    @DisplayName("Step 3: サーバー用店番取得")
    class Step3ServerBrNoConversion {

        @Test
        @DisplayName("executeServiceメソッド_正常系_入力のbrNoがサーバー用店番に変換されること_1BD3A")
        void testExecuteService_convertsInputBrNoToServerBrNo() {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: entity.brno が SERVER_BR_NO となり、戻り値が非 null であること
            assertThat(entity.getBrno()).isEqualTo(SERVER_BR_NO);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("executeServiceメソッド_正常系_serverBrNoはMapper後にentity.brnoへ後付けされRepositoryに渡る同一entityへ反映されること_1AF3A")
        void testExecuteService_appliesServerBrNoToEntityAfterMapper() {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            sut.executeService(input);

            // Assert: entity の brno と Repository への引数を検証
            assertThat(entity.getBrno()).isEqualTo(SERVER_BR_NO);
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
        }

        @Test
        @DisplayName("executeServiceメソッド_異常系_brNoがnullの場合、NullPointerExceptionが送出されMapper以降が実行されないこと_1CE3A")
        void testExecuteService_withBrNoNull_throwsNpeAndSkipsLaterSteps() {
            // Arrange: brNo=null の input を準備
            final RgV0501RegistCorrectValueServiceInput bad =
                    newInput(null, CM_NO, EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT);
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);

            // Act & Assert: 例外送出と後続未実行を検証
            assertThatThrownBy(() -> sut.executeService(bad))
                    .isInstanceOf(NullPointerException.class);

            verifyNoInteractions(entityMapper);
            verify(repository, never()).updateByPrimaryKeyAndDelFlg(any());
            verify(repository, never()).insert(any());
        }
    }

    @Nested
    @DisplayName("Step 4: 計数情報更新／新規登録")
    class Step4UpdateOrInsert {

        // ParameterizedTest: update 件数 = 1 / 2 / 100 / Integer.MAX_VALUE のとき insert は呼ばれない（境界値 UTR-021）
        @ParameterizedTest(name = "update 件数 {0} のとき、insert は呼ばれない")
        @ValueSource(ints = {1, 2, 100, Integer.MAX_VALUE})
        @DisplayName("executeServiceメソッド_正常系_updateが1件以上の場合、insertが呼ばれないこと_1BE3A")
        void testExecuteService_whenUpdateNonZero_doesNotCallInsert(final int updateCount) {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(updateCount);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: update が呼ばれ、insert は呼ばれず、戻り値が非 null
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
            verify(repository, never()).insert(any());
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("executeServiceメソッド_正常系_updateが0件の場合、同一entityでinsertにフォールバックされること_1AEF3A")
        void testExecuteService_whenUpdateZero_fallsBackToInsertWithSameEntity() {
            // Arrange: update を 0 件、insert を 1 件返すモック設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(0);
            when(repository.insert(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: update と insert の呼出順序および戻り値を検証
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
            verify(repository).insert(entity);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("executeServiceメソッド_異常系_updateが例外を送出した場合、insertが呼ばれず例外を伝搬すること_1CE3A")
        void testExecuteService_whenUpdateThrows_propagatesAndSkipsInsert() {
            // Arrange: update で SQLException 連鎖の RuntimeException を投げるモック設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            final RuntimeException sqlError =
                    new RuntimeException(new SQLException("PK violation"));
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenThrow(sqlError);

            // Act & Assert: 同一例外が伝搬し insert が呼ばれないことを検証
            assertThatThrownBy(() -> sut.executeService(input)).isSameAs(sqlError);
            verify(repository, never()).insert(any());
        }

        @Test
        @DisplayName("executeServiceメソッド_異常系_insertが例外を送出した場合、例外を伝搬すること_1C3A")
        void testExecuteService_whenInsertThrows_propagates() {
            // Arrange: insert で SQLException 連鎖の RuntimeException を投げるモック設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(0);
            final RuntimeException sqlError =
                    new RuntimeException(new SQLException("FK violation"));
            when(repository.insert(entity)).thenThrow(sqlError);

            // Act & Assert: 同一例外が伝搬することを検証
            assertThatThrownBy(() -> sut.executeService(input)).isSameAs(sqlError);
        }
    }

    @Nested
    @DisplayName("Step 5: ServiceOutput 生成")
    class Step5OutputBuild {

        @Test
        @DisplayName("executeServiceメソッド_正常系_出力のlockInfo.exclusiveKeyが入力のexclusiveKeyをそのままechoすること_1B3B")
        void testExecuteService_outputExclusiveKeyEchoesInput() {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: 出力の lockInfo.exclusiveKey が入力と一致
            assertThat(output.getLockInfo()).isNotNull();
            assertThat(output.getLockInfo().getExclusiveKey()).isEqualTo(EXCLUSIVE_KEY);
        }

        // ParameterizedTest: update 件数 と ExclusiveProcessHelper 戻り値の境界値（UTR-021）
        @ParameterizedTest(name = "update 件数={0}, ExclusiveProcessHelper 戻り値={1} → 出力 exclusiveCount={1}")
        @CsvSource({
                "1, 0",
                "1, 2",
                "1, 999",
                "0, 0",
                "0, 2",
                "0, 2147483647"
        })
        @DisplayName("executeServiceメソッド_正常系_update_insertいずれの経路でも出力exclusiveCountがExclusiveProcessHelper戻り値と一致すること_1B3B")
        void testExecuteService_outputExclusiveCountReflectsCheckExclusiveReturnValue(
                final int updateCount,
                final int returnedExclusiveCount) {
            // Arrange: 境界値をモック応答に設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(returnedExclusiveCount);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(updateCount);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: 出力 exclusiveCount が ExclusiveProcessHelper の戻り値と一致
            assertThat(output.getLockInfo()).isNotNull();
            assertThat(output.getLockInfo().getExclusiveCount()).isEqualTo(returnedExclusiveCount);
        }

        @Test
        @DisplayName("executeServiceメソッド_正常系_出力lockInfoは新しいインスタンスであり入力lockInfoの参照を共有しないこと_1BD3B")
        void testExecuteService_outputLockInfoIsNewInstance_notSharedWithInput() {
            // Arrange: モック応答を設定
            when(exclusiveProcessHelper.checkExclusiveCount(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // Act: テスト対象のメソッドを実行
            final RgV0501RegistCorrectValueServiceOutput output = sut.executeService(input);

            // Assert: 出力 lockInfo が入力 lockInfo と参照不一致で値も独立であること
            assertThat(output.getLockInfo()).isNotSameAs(input.getLockInfo());
            assertThat(output.getLockInfo().getExclusiveCount()).isEqualTo(UPDATED_EXCLUSIVE_COUNT);
            assertThat(input.getLockInfo().getExclusiveCount()).isEqualTo(CLIENT_EXCLUSIVE_COUNT);
        }
    }

    private static RgV0501RegistCorrectValueServiceInput newInput(
            final String brNo,
            final String cmNo,
            final String exclusiveKey,
            final int exclusiveCount) {
        final RgV0501RegistCorrectValueServiceInput in =
                new RgV0501RegistCorrectValueServiceInput();
        in.setBrNo(brNo);
        in.setCmNo(cmNo);
        in.setLockInfo(new LockInfo(exclusiveKey, exclusiveCount));
        return in;
    }
}
