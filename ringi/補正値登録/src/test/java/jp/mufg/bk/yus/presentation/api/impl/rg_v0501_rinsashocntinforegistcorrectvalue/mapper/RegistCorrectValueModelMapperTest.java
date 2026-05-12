package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.mapper;

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
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueResponse;

/**
 * {@link RegistCorrectValueModelMapper} の単体テスト。
 */
class RegistCorrectValueModelMapperTest {

    // UTR-043: Mapper インターフェースは Mappers.getMapper でインスタンス生成
    private final RegistCorrectValueModelMapper sut = RegistCorrectValueModelMapper.INSTANCE;

    static Stream<Arguments> correctionValueAccessors() {
        return Stream.of(
                Arguments.of(
                        "貸付金・割引合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setLoanDiscTotalCorrectionValue,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getLoanDiscTotalCorrectionValue),
                Arguments.of(
                        "内円貨（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setInternalJpyCorrectionValue,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getInternalJpyCorrectionValue),
                Arguments.of(
                        "外為与信合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setForexCreditTotalCorrectionValue,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getForexCreditTotalCorrectionValue),
                Arguments.of(
                        "支払承諾合計（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setShiShoTotalCorrectionValue,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getShiShoTotalCorrectionValue),
                Arguments.of(
                        "規定担保（規定値）（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setRegulationTanpoCorrectionValueRegulationValue,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getRegulationTanpoCorrectionValueRegulationValue),
                Arguments.of(
                        "規定担保（時価ベース）（補正値）",
                        (BiConsumer<RegistCorrectValueRequest, Integer>)
                                RegistCorrectValueRequest::setRegulationTanpoCorrectionValueJikaBase,
                        (Function<RgV0501RegistCorrectValueServiceInput, Integer>)
                                RgV0501RegistCorrectValueServiceInput::getRegulationTanpoCorrectionValueJikaBase));
    }

    @Nested
    @DisplayName("toServiceInput: presentation Request → domain ServiceInput への変換")
    class ToServiceInput {

        @Test
        @DisplayName("toServiceInputメソッド_正常系_全項目を埋めた完全リクエストの場合、全フィールドがServiceInputに転写されること_1BD2B")
        void testToServiceInput_withFullyPopulatedRequest_mapsAllFields() {
            // Arrange: 完全リクエストを準備
            RegistCorrectValueRequest request = newFullyPopulatedRequest();

            // Act: テスト対象のメソッドを実行
            RgV0501RegistCorrectValueServiceInput actual = sut.toServiceInput(request);

            // Assert: 全フィールドが転写されていること
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

        @ParameterizedTest(name = "{0} は ServiceInput の同名フィールドへ独立に転写される")
        @MethodSource("jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.mapper.RegistCorrectValueModelMapperTest#correctionValueAccessors")
        @DisplayName("toServiceInputメソッド_正常系_補正値6項目がそれぞれの同名フィールドへ独立に転写されること_1BD2B")
        void testToServiceInput_mapsEachCorrectionValueIndependently(
                String displayName,
                BiConsumer<RegistCorrectValueRequest, Integer> setter,
                Function<RgV0501RegistCorrectValueServiceInput, Integer> getter) {
            // Arrange: ミニマルリクエストに対象フィールドのみセット
            RegistCorrectValueRequest request = newMinimalValidRequest();
            setter.accept(request, 1234567);

            // Act: テスト対象のメソッドを実行
            RgV0501RegistCorrectValueServiceInput actual = sut.toServiceInput(request);

            // Assert: 対象フィールドが転写されていること
            assertThat(getter.apply(actual)).isEqualTo(1234567);
        }

        @Test
        @DisplayName("toServiceInputメソッド_正常系_補正理由がServiceInput.correctionReasonへ転写されること_1BD2B")
        void testToServiceInput_mapsCorrectionReason() {
            // Arrange: 補正理由を設定したミニマルリクエストを準備
            RegistCorrectValueRequest request = newMinimalValidRequest();
            request.setCorrectionReason("補正理由テキスト");

            // Act: テスト対象のメソッドを実行
            RgV0501RegistCorrectValueServiceInput actual = sut.toServiceInput(request);

            // Assert: 補正理由が転写されていること
            assertThat(actual.getCorrectionReason()).isEqualTo("補正理由テキスト");
        }

        @Test
        @DisplayName("toServiceInputメソッド_正常系_required外項目がnullの場合、ServiceInput側でもnullとして伝搬されること_1D2B")
        void testToServiceInput_propagatesOptionalNullFieldsAsNull() {
            // Arrange: 必須項目のみのリクエスト（補正値 6 項目と補正理由は null のまま）
            RegistCorrectValueRequest request = newMinimalValidRequest();

            // Act: テスト対象のメソッドを実行
            RgV0501RegistCorrectValueServiceInput actual = sut.toServiceInput(request);

            // Assert: null 項目が ServiceInput でも null
            assertThat(actual.getLoanDiscTotalCorrectionValue()).isNull();
            assertThat(actual.getInternalJpyCorrectionValue()).isNull();
            assertThat(actual.getForexCreditTotalCorrectionValue()).isNull();
            assertThat(actual.getShiShoTotalCorrectionValue()).isNull();
            assertThat(actual.getRegulationTanpoCorrectionValueRegulationValue()).isNull();
            assertThat(actual.getRegulationTanpoCorrectionValueJikaBase()).isNull();
            assertThat(actual.getCorrectionReason()).isNull();
        }

        @Test
        @DisplayName("toServiceInputメソッド_正常系_LockInfoが共有LockInfoとして同型で転写されること_1BD2B")
        void testToServiceInput_mapsLockInfoToSharedLockInfo() {
            // Arrange: ミニマルリクエスト（LockInfo は newMinimalValidRequest で設定済）を準備
            RegistCorrectValueRequest request = newMinimalValidRequest();

            // Act: テスト対象のメソッドを実行
            RgV0501RegistCorrectValueServiceInput actual = sut.toServiceInput(request);

            // Assert: 共有 LockInfo として転写されていること
            assertThat(actual.getLockInfo())
                    .isNotNull()
                    .isInstanceOf(LockInfo.class)
                    .satisfies(lockInfo -> {
                        assertThat(lockInfo.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
                        assertThat(lockInfo.getExclusiveCount()).isEqualTo(1);
                    });
        }

        @Test
        @DisplayName("toServiceInputメソッド_異常系_入力リクエストがnullの場合、戻り値もnullとなること（MapStruct標準仕様）_1B2B")
        void testToServiceInput_withNullInput_returnsNull() {
            // Arrange: 入力リクエストを null として準備

            // Act & Assert: 戻り値が null
            assertThat(sut.toServiceInput(null)).isNull();
        }
    }

    @Nested
    @DisplayName("toResponse: domain ServiceOutput → presentation Response への変換")
    class ToResponse {

        @Test
        @DisplayName("toResponseメソッド_正常系_ServiceOutputのLockInfoがpresentation_Responseへ同型で転写されること_1BD2B")
        void testToResponse_mapsLockInfoToPresentationLockInfo() {
            // Arrange: LockInfo を持つ ServiceOutput を準備
            RgV0501RegistCorrectValueServiceOutput serviceOutput = new RgV0501RegistCorrectValueServiceOutput();
            LockInfo domainLockInfo = new LockInfo("rkANKEN999999999999", 2);
            serviceOutput.setLockInfo(domainLockInfo);

            // Act: テスト対象のメソッドを実行
            RegistCorrectValueResponse actual = sut.toResponse(serviceOutput);

            // Assert: presentation Response の LockInfo が同型で同値であること
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
        @DisplayName("toResponseメソッド_正常系_ServiceOutput.lockInfoがnullの場合、Response.lockInfoもnullとなること_1D2B")
        void testToResponse_propagatesNullLockInfo() {
            // Arrange: LockInfo を持たない ServiceOutput を準備
            RgV0501RegistCorrectValueServiceOutput serviceOutput = new RgV0501RegistCorrectValueServiceOutput();

            // Act: テスト対象のメソッドを実行
            RegistCorrectValueResponse actual = sut.toResponse(serviceOutput);

            // Assert: Response 非 null、lockInfo は null
            assertThat(actual).isNotNull();
            assertThat(actual.getLockInfo()).isNull();
        }

        @Test
        @DisplayName("toResponseメソッド_異常系_入力DTOがnullの場合、戻り値もnullとなること_1B2B")
        void testToResponse_withNullInput_returnsNull() {
            // Arrange: 入力 DTO を null として準備

            // Act & Assert: 戻り値が null
            assertThat(sut.toResponse(null)).isNull();
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
        request.setLockInfo(new LockInfo("rkANKEN111111111111", 1));
        return request;
    }

    /** 必須項目のみを埋めたミニマルリクエスト（補正値・補正理由は null のまま）。 */
    private static RegistCorrectValueRequest newMinimalValidRequest() {
        RegistCorrectValueRequest request = new RegistCorrectValueRequest();
        request.setBrNo("010");
        request.setCmNo("9019149");
        request.setLockInfo(new LockInfo("rkANKEN111111111111", 1));
        return request;
    }
}
