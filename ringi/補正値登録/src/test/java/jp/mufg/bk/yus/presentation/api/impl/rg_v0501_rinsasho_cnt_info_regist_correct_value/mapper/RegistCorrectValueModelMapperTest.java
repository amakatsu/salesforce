package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.function.BiConsumer;
import java.util.function.Function;
import java.util.stream.Stream;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceOutputDto;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.LockInfo;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueResponse;

class RegistCorrectValueModelMapperTest {

    private final RegistCorrectValueModelMapper sut = RegistCorrectValueModelMapper.INSTANCE;

    static Stream<Arguments> correctionValueAccessors() {
        return Stream.of(
                Arguments.of(
                        "貸付金・割引合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setLoanDiscTotalCorrectionValue,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getLoanDiscTotalCorrectionValue),
                Arguments.of(
                        "内円貨（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setInternalJpyCorrectionValue,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getInternalJpyCorrectionValue),
                Arguments.of(
                        "外為与信合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setForexCreditTotalCorrectionValue,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getForexCreditTotalCorrectionValue),
                Arguments.of(
                        "支払承諾合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setShiShoTotalCorrectionValue,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getShiShoTotalCorrectionValue),
                Arguments.of(
                        "規定担保（規定値）（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setRegulationTanpoCorrectionValueRegulationValue,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getRegulationTanpoCorrectionValueRegulationValue),
                Arguments.of(
                        "規定担保（時価ベース）（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setRegulationTanpoCorrectionValueJikaBase,
                        (Function<ServiceInputDto, Integer>)
                                ServiceInputDto::getRegulationTanpoCorrectionValueJikaBase));
    }

    @Nested
    @DisplayName("toServiceInputDto: presentation Request → domain ServiceInputDto への変換")
    class ToServiceInputDto {

        @Test
        @DisplayName("全項目を埋めた完全リクエストは全フィールドが ServiceInputDto に転写される")
        void allFieldsAreFullyMapped() {
            // given
            RegistCorrectValueRequest request = newFullyPopulatedRequest();

            // when
            ServiceInputDto actual = sut.toServiceInputDto(request);

            // then
            assertThat(actual)
                    .isNotNull()
                    .satisfies(dto -> {
                        assertThat(dto.getBrNo()).isEqualTo("010");
                        assertThat(dto.getCmNo()).isEqualTo("9019149");
                        assertThat(dto.getLoanDiscTotalCorrectionValue()).isEqualTo(1111111);
                        assertThat(dto.getInternalJpyCorrectionValue()).isEqualTo(2222222);
                        assertThat(dto.getForexCreditTotalCorrectionValue()).isEqualTo(3333333);
                        assertThat(dto.getShiShoTotalCorrectionValue()).isEqualTo(4444444);
                        assertThat(dto.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(5555555);
                        assertThat(dto.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(6666666);
                        assertThat(dto.getCorrectionReason()).isEqualTo("テスト補正理由");
                    });
        }

        @ParameterizedTest(name = "{0} は ServiceInputDto の同名フィールドへ独立に転写される")
        @MethodSource("jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper.RegistCorrectValueModelMapperTest#correctionValueAccessors")
        @DisplayName("補正値 6 項目はそれぞれの同名フィールドへ独立に転写される")
        void eachCorrectionValueIsMappedIndependently(
                String displayName,
                BiConsumer<RegistCorrectValueRequest, Integer> setter,
                Function<ServiceInputDto, Integer> getter) {
            // given - 対象フィールドのみセットして他は null のままにする
            RegistCorrectValueRequest request = newMinimalValidRequest();
            setter.accept(request, 1234567);

            // when
            ServiceInputDto actual = sut.toServiceInputDto(request);

            // then
            assertThat(getter.apply(actual)).isEqualTo(1234567);
        }

        @Test
        @DisplayName("補正理由（String）は ServiceInputDto.correctionReason へ転写される")
        void correctionReasonIsMapped() {
            // given
            RegistCorrectValueRequest request = newMinimalValidRequest();
            request.setCorrectionReason("補正理由テキスト");

            // when
            ServiceInputDto actual = sut.toServiceInputDto(request);

            // then
            assertThat(actual.getCorrectionReason()).isEqualTo("補正理由テキスト");
        }

        @Test
        @DisplayName("required ではない補正値・補正理由が null の場合、ServiceInputDto 側でも null として伝搬される")
        void optionalNullFieldsArePropagatedAsNull() {
            // given - 必須項目のみのリクエスト（補正値 6 項目と補正理由は未設定）
            RegistCorrectValueRequest request = newMinimalValidRequest();

            // when
            ServiceInputDto actual = sut.toServiceInputDto(request);

            // then
            assertThat(actual.getLoanDiscTotalCorrectionValue()).isNull();
            assertThat(actual.getInternalJpyCorrectionValue()).isNull();
            assertThat(actual.getForexCreditTotalCorrectionValue()).isNull();
            assertThat(actual.getShiShoTotalCorrectionValue()).isNull();
            assertThat(actual.getRegulationTanpoCorrectionValueRegulationValue()).isNull();
            assertThat(actual.getRegulationTanpoCorrectionValueJikaBase()).isNull();
            assertThat(actual.getCorrectionReason()).isNull();
        }

        @Test
        @DisplayName("LockInfo は LockInfoDto（domain 層独立 DTO）に入れ子で転写される")
        void lockInfoIsMappedToLockInfoDto() {
            // given
            RegistCorrectValueRequest request = newMinimalValidRequest();

            // when
            ServiceInputDto actual = sut.toServiceInputDto(request);

            // then
            assertThat(actual.getLockInfo())
                    .isNotNull()
                    .isInstanceOf(LockInfoDto.class)
                    .satisfies(lockInfo -> {
                        assertThat(lockInfo.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
                        assertThat(lockInfo.getExclusiveCount()).isEqualTo(1);
                    });
        }

        @Test
        @DisplayName("入力リクエストが null の場合、戻り値も null となる（MapStruct のデフォルト挙動）")
        void nullInputReturnsNull() {
            // when / then
            assertThat(sut.toServiceInputDto(null)).isNull();
        }
    }

    @Nested
    @DisplayName("toResponse: domain ServiceOutputDto → presentation Response への変換")
    class ToResponse {

        @Test
        @DisplayName("ServiceOutputDto の LockInfoDto は presentation 層 LockInfo へ入れ子で転写される")
        void lockInfoIsMappedToPresentationLockInfo() {
            // given
            ServiceOutputDto serviceOutput = new ServiceOutputDto();
            LockInfoDto domainLockInfo = new LockInfoDto("rkANKEN999999999999", 2);
            serviceOutput.setLockInfo(domainLockInfo);

            // when
            RegistCorrectValueResponse actual = sut.toResponse(serviceOutput);

            // then
            assertThat(actual)
                    .isNotNull()
                    .extracting(RegistCorrectValueResponse::getLockInfo)
                    .isNotNull()
                    .isInstanceOf(LockInfo.class)
                    .satisfies(rawLockInfo -> {
                        LockInfo lockInfo = (LockInfo) rawLockInfo;
                        assertThat(lockInfo.getExclusiveKey()).isEqualTo("rkANKEN999999999999");
                        assertThat(lockInfo.getExclusiveCount()).isEqualTo(2);
                    });
        }

        @Test
        @DisplayName("ServiceOutputDto.lockInfo が null の場合、Response.lockInfo も null となる")
        void nullNestedLockInfoIsPropagated() {
            // given
            ServiceOutputDto serviceOutput = new ServiceOutputDto();

            // when
            RegistCorrectValueResponse actual = sut.toResponse(serviceOutput);

            // then
            assertThat(actual).isNotNull();
            assertThat(actual.getLockInfo()).isNull();
        }

        @Test
        @DisplayName("入力 DTO が null の場合、戻り値も null となる")
        void nullInputReturnsNull() {
            // when / then
            assertThat(sut.toResponse(null)).isNull();
        }
    }

    @Nested
    @DisplayName("ネスト変換サブメソッド: 層間 LockInfo の橋渡し")
    class LockInfoBridgeMethods {

        @Test
        @DisplayName("toServiceInputLockInfo: presentation LockInfo → domain LockInfoDto の全フィールド転写")
        void toServiceInputLockInfoMapsAllFields() {
            // given
            LockInfo source = new LockInfo();
            source.setExclusiveKey("rkANKEN111111111111");
            source.setExclusiveCount(1);

            // when
            LockInfoDto actual = sut.toServiceInputLockInfo(source);

            // then
            assertThat(actual)
                    .isNotNull()
                    .satisfies(lockInfo -> {
                        assertThat(lockInfo.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
                        assertThat(lockInfo.getExclusiveCount()).isEqualTo(1);
                    });
        }

        @Test
        @DisplayName("toResponseLockInfo: domain LockInfoDto → presentation LockInfo の全フィールド転写")
        void toResponseLockInfoMapsAllFields() {
            // given
            LockInfoDto source = new LockInfoDto("rkANKEN222222222222", 5);

            // when
            LockInfo actual = sut.toResponseLockInfo(source);

            // then
            assertThat(actual)
                    .isNotNull()
                    .satisfies(lockInfo -> {
                        assertThat(lockInfo.getExclusiveKey()).isEqualTo("rkANKEN222222222222");
                        assertThat(lockInfo.getExclusiveCount()).isEqualTo(5);
                    });
        }

        @Test
        @DisplayName("toServiceInputLockInfo に null を渡すと null が返る")
        void toServiceInputLockInfoReturnsNullForNullInput() {
            // when / then
            assertThat(sut.toServiceInputLockInfo(null)).isNull();
        }

        @Test
        @DisplayName("toResponseLockInfo に null を渡すと null が返る")
        void toResponseLockInfoReturnsNullForNullInput() {
            // when / then
            assertThat(sut.toResponseLockInfo(null)).isNull();
        }
    }

    /** 全項目を埋めた完全リクエスト（業務サンプル値ベース）。 */
    private static RegistCorrectValueRequest newFullyPopulatedRequest() {
        RegistCorrectValueRequest request = new RegistCorrectValueRequest();
        request.setBrNo("010");
        request.setCmNo("9019149");
        request.setLoanDiscTotalCorrectionValue(1111111);
        request.setInternalJpyCorrectionValue(2222222);
        request.setForexCreditTotalCorrectionValue(3333333);
        request.setShiShoTotalCorrectionValue(4444444);
        request.setRegulationTanpoCorrectionValueRegulationValue(5555555);
        request.setRegulationTanpoCorrectionValueJikaBase(6666666);
        request.setCorrectionReason("テスト補正理由");

        LockInfo lockInfo = new LockInfo();
        lockInfo.setExclusiveKey("rkANKEN111111111111");
        lockInfo.setExclusiveCount(1);
        request.setLockInfo(lockInfo);
        return request;
    }

    /** 必須項目のみを埋めたミニマルリクエスト（補正値・補正理由は null のまま）。 */
    private static RegistCorrectValueRequest newMinimalValidRequest() {
        RegistCorrectValueRequest request = new RegistCorrectValueRequest();
        request.setBrNo("010");
        request.setCmNo("9019149");

        LockInfo lockInfo = new LockInfo();
        lockInfo.setExclusiveKey("rkANKEN111111111111");
        lockInfo.setExclusiveCount(1);
        request.setLockInfo(lockInfo);
        return request;
    }
}
