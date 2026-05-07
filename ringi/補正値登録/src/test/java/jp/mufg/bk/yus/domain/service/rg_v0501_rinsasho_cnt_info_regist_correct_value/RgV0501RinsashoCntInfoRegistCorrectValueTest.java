package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value;

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
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import jp.mufg.bk.yus.com.util.ExclusiveControlHelper;
import jp.mufg.bk.yus.com.util.StringEditUtil;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.RinsashoKeisuHoseichiRepository;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceOutputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper.KeisuHoseichiEntityMapper;

/**
 * {@link RgV0501RinsashoCntInfoRegistCorrectValue} の単体テスト。
 * Service の 5 ステップ（インプット取得 / 排他チェック / 店番取得 / 更新or新規 / Output 生成）の境界に沿って @Nested で構造化する。
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("RgV0501RinsashoCntInfoRegistCorrectValue")
class RgV0501RinsashoCntInfoRegistCorrectValueTest {

    private static final String BR_NO = "010";
    private static final String SERVER_BR_NO = "0000010";
    private static final String CM_NO = "9019149";
    private static final String EXCLUSIVE_KEY = "rkANKEN111111111111";
    private static final int CLIENT_EXCLUSIVE_COUNT = 1;
    private static final int UPDATED_EXCLUSIVE_COUNT = 2;

    @Mock
    private RinsashoKeisuHoseichiRepository repository;

    @Mock
    private ExclusiveControlHelper exclusiveControlHelper;

    @Mock
    private StringEditUtil stringEditUtil;

    @Mock
    private KeisuHoseichiEntityMapper entityMapper;

    @InjectMocks
    private RgV0501RinsashoCntInfoRegistCorrectValue sut;

    private ServiceInputDto input;
    private RinsashoKeisuHoseichi entity;

    @BeforeEach
    void setUp() {
        input = newInput(BR_NO, CM_NO, EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT);
        entity = new RinsashoKeisuHoseichi();
    }

    // ========================================================================
    // Step 1: インプット取得（引数防衛）
    // ========================================================================

    @Nested
    @DisplayName("Step 1: インプット取得（引数防衛）")
    class Step1_InputAcquisition {

        @Test
        @DisplayName("input が null のとき、NullPointerException を送出し、依存はいずれも呼ばれない")
        void inputNull_throwsNpeAndCallsNoCollaborator() {
            // given - 引数 null

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(null))
                    .isInstanceOf(NullPointerException.class);

            verifyNoInteractions(repository);
            verifyNoInteractions(exclusiveControlHelper);
            verifyNoInteractions(stringEditUtil);
            verifyNoInteractions(entityMapper);
        }

        @Test
        @DisplayName("input.lockInfo が null のとき、NullPointerException を送出し、依存はいずれも呼ばれない")
        void lockInfoNull_throwsNpeAndCallsNoCollaborator() {
            // given - lockInfo を持たない input
            ServiceInputDto bad = new ServiceInputDto();
            bad.setBrNo(BR_NO);
            bad.setCmNo(CM_NO);

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(bad))
                    .isInstanceOf(NullPointerException.class);

            verifyNoInteractions(repository);
            verifyNoInteractions(exclusiveControlHelper);
            verifyNoInteractions(stringEditUtil);
            verifyNoInteractions(entityMapper);
        }
    }

    // ========================================================================
    // Step 2: 排他更新回数チェック（楽観ロック）
    // ========================================================================

    @Nested
    @DisplayName("Step 2: 排他更新回数チェック（楽観ロック）")
    class Step2_ExclusiveCheck {

        @Test
        @DisplayName("入力の exclusiveKey と exclusiveCount が ExclusiveControlHelper にそのまま渡される")
        void exclusiveCheck_isCalledWithInputKeyAndCount() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            verify(exclusiveControlHelper).checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("排他チェックが例外を送出した場合、Step 3 以降は実行されず例外を伝搬する")
        void exclusiveCheckFails_propagatesAndSkipsLaterSteps() {
            // given
            RuntimeException exclusiveError = new IllegalStateException("exclusive count mismatch");
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenThrow(exclusiveError);

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(input))
                    .isSameAs(exclusiveError);

            verifyNoInteractions(stringEditUtil);
            verifyNoInteractions(entityMapper);
            verify(repository, never()).updateByPrimaryKeyAndDelFlg(any());
            verify(repository, never()).insert(any());
        }
    }

    // ========================================================================
    // Step 3: サーバー用店番取得（3→7 桁変換）
    // ========================================================================

    @Nested
    @DisplayName("Step 3: サーバー用店番取得（3→7 桁変換）")
    class Step3_ServerBrNoConversion {

        @Test
        @DisplayName("入力の brNo が StringEditUtil#toServerBrNo にそのまま渡される")
        void toServerBrNo_isCalledWithInputBrNo() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            verify(stringEditUtil).toServerBrNo(BR_NO);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("変換結果の serverBrNo は Mapper#toEntity 後に entity.brNo へ後付けされ、Repository に渡る Entity に反映される")
        void serverBrNo_isAppliedToEntityAfterMapper() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // when
            sut.registCorrectValue(input);

            // then
            assertThat(entity.getBrNo()).isEqualTo(SERVER_BR_NO);
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
        }

        @Test
        @DisplayName("店番変換が例外を送出した場合、Step 4 以降は実行されず例外を伝搬する")
        void stringEditFails_propagatesAndSkipsLaterSteps() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            RuntimeException stringEditError = new IllegalArgumentException("invalid brNo length");
            when(stringEditUtil.toServerBrNo(BR_NO)).thenThrow(stringEditError);

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(input))
                    .isSameAs(stringEditError);

            verifyNoInteractions(entityMapper);
            verify(repository, never()).updateByPrimaryKeyAndDelFlg(any());
            verify(repository, never()).insert(any());
        }
    }

    // ========================================================================
    // Step 4: 計数情報更新／新規登録
    // ========================================================================

    @Nested
    @DisplayName("Step 4: 計数情報更新／新規登録")
    class Step4_UpdateOrInsert {

        @ParameterizedTest(name = "update 件数 {0} のとき、insert は呼ばれない")
        @ValueSource(ints = {1, 2, 100, Integer.MAX_VALUE})
        @DisplayName("update が 1 件以上の場合、insert は呼ばれない")
        void updateNonZero_doesNotCallInsert(int updateCount) {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(updateCount);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
            verify(repository, never()).insert(any());
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("update が 0 件の場合、同一 entity で insert にフォールバックされる")
        void updateZero_fallsBackToInsertWithSameEntity() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(0);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            verify(repository).updateByPrimaryKeyAndDelFlg(entity);
            verify(repository).insert(entity);
            assertThat(output).isNotNull();
        }

        @Test
        @DisplayName("update が例外を送出した場合、insert は呼ばれず例外を伝搬する")
        void updateThrows_propagatesAndSkipsInsert() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            RuntimeException sqlError = new RuntimeException(new SQLException("PK violation"));
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenThrow(sqlError);

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(input)).isSameAs(sqlError);
            verify(repository, never()).insert(any());
        }

        @Test
        @DisplayName("insert が例外を送出した場合、例外を伝搬する")
        void insertThrows_propagates() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(0);
            RuntimeException sqlError = new RuntimeException(new SQLException("FK violation"));
            Mockito.doThrow(sqlError).when(repository).insert(entity);

            // when / then
            assertThatThrownBy(() -> sut.registCorrectValue(input)).isSameAs(sqlError);
        }
    }

    // ========================================================================
    // Step 5: ServiceOutputDto 生成
    // ========================================================================

    @Nested
    @DisplayName("Step 5: ServiceOutputDto 生成")
    class Step5_OutputBuild {

        @Test
        @DisplayName("出力の lockInfo.exclusiveKey は入力の exclusiveKey をそのまま echo する")
        void outputExclusiveKey_echoesInput() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            assertThat(output.getLockInfo()).isNotNull();
            assertThat(output.getLockInfo().getExclusiveKey()).isEqualTo(EXCLUSIVE_KEY);
        }

        @ParameterizedTest(name = "update 件数={0}, ExclusiveControlHelper 戻り値={1} → 出力 exclusiveCount={1}")
        @CsvSource({
                "1, 0",
                "1, 2",
                "1, 999",
                "0, 0",
                "0, 2",
                "0, 2147483647"
        })
        @DisplayName("update / insert いずれの経路でも、出力 exclusiveCount は ExclusiveControlHelper の戻り値（更新後排他回数）と一致する")
        void outputExclusiveCount_reflectsCheckExclusiveReturnValue(int updateCount, int returnedExclusiveCount) {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(returnedExclusiveCount);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(updateCount);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            assertThat(output.getLockInfo()).isNotNull();
            assertThat(output.getLockInfo().getExclusiveCount()).isEqualTo(returnedExclusiveCount);
        }

        @Test
        @DisplayName("出力 lockInfo は Service が確定値から組み立てた新しいインスタンスであり、入力 lockInfo の参照を共有しない")
        void outputLockInfo_isNewInstance_notSharedWithInputLockInfo() {
            // given
            when(exclusiveControlHelper.checkExclusive(EXCLUSIVE_KEY, CLIENT_EXCLUSIVE_COUNT))
                    .thenReturn(UPDATED_EXCLUSIVE_COUNT);
            when(stringEditUtil.toServerBrNo(BR_NO)).thenReturn(SERVER_BR_NO);
            when(entityMapper.toEntity(input)).thenReturn(entity);
            when(repository.updateByPrimaryKeyAndDelFlg(entity)).thenReturn(1);

            // when
            ServiceOutputDto output = sut.registCorrectValue(input);

            // then
            assertThat(output.getLockInfo()).isNotSameAs(input.getLockInfo());
            assertThat(output.getLockInfo().getExclusiveCount()).isEqualTo(UPDATED_EXCLUSIVE_COUNT);
            assertThat(input.getLockInfo().getExclusiveCount()).isEqualTo(CLIENT_EXCLUSIVE_COUNT);
        }
    }

    private static ServiceInputDto newInput(
            String brNo, String cmNo, String exclusiveKey, int exclusiveCount) {
        ServiceInputDto in = new ServiceInputDto();
        in.setBrNo(brNo);
        in.setCmNo(cmNo);
        in.setLockInfo(new LockInfoDto(exclusiveKey, exclusiveCount));
        return in;
    }
}
