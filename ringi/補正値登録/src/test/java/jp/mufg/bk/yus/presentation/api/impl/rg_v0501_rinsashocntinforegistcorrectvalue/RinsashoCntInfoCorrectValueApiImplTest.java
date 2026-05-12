package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatNullPointerException;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import java.lang.reflect.Method;
import java.util.Set;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.ValidatorFactory;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import jakarta.validation.executable.ExecutableValidator;
import org.hibernate.validator.messageinterpolation.ParameterMessageInterpolator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.RgV0501RegistCorrectValueService;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.mapper.RegistCorrectValueModelMapper;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueResponse;

/**
 * {@link RinsashoCntInfoCorrectValueApiImpl} の単体テスト。
 *
 * <p>UTR-007: Request バリデーションは `executableValidator.validateParameters` で確認する。
 * UTR-008: Response データモデルの中身は検証対象外（Mapper 委譲の呼出検証のみ）。
 * UTR-009: ApiImpl はテスト対象。
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("RinsashoCntInfoCorrectValueApiImpl")
class RinsashoCntInfoCorrectValueApiImplTest {

    private static final String VALID_BR_NO = "010";
    private static final String VALID_CM_NO = "9019149";
    private static final String VALID_EXCLUSIVE_KEY = "rkANKEN111111111111";
    private static final int VALID_EXCLUSIVE_COUNT = 1;

    @Mock
    private RgV0501RegistCorrectValueService service;

    @Mock
    private RegistCorrectValueModelMapper modelMapper;

    @InjectMocks
    private RinsashoCntInfoCorrectValueApiImpl sut;

    @Nested
    @DisplayName("registCorrectValue: 正常委譲（Service / ModelMapper への委譲検証）")
    class NormalDelegation {

        @Test
        @DisplayName("registCorrectValueメソッド_正常系_有効リクエストの場合、ModelMapperでServiceInputへ変換しServiceへ委譲、戻りをModelMapperでResponse化すること_1AEF2AB")
        void testRegistCorrectValue_withValidRequest_delegatesToMapperAndService() {
            // Arrange: 有効リクエスト + Service / ModelMapper のモック応答を設定
            RegistCorrectValueRequest request = newValidRequest();
            RgV0501RegistCorrectValueServiceInput serviceInput = new RgV0501RegistCorrectValueServiceInput();
            RgV0501RegistCorrectValueServiceOutput serviceOutput = new RgV0501RegistCorrectValueServiceOutput();
            RegistCorrectValueResponse expectedResponse = new RegistCorrectValueResponse();

            when(modelMapper.toServiceInput(request)).thenReturn(serviceInput);
            when(service.executeService(serviceInput)).thenReturn(serviceOutput);
            when(modelMapper.toResponse(serviceOutput)).thenReturn(expectedResponse);

            // Act: テスト対象のメソッドを実行
            RegistCorrectValueResponse actual = sut.registCorrectValue(request);

            // Assert: UTR-008 により Response 中身は検証せず、参照同一性（Mapper 返却の素通り）のみ検証
            assertThat(actual).isSameAs(expectedResponse);
            verify(modelMapper).toServiceInput(request);
            verify(service).executeService(serviceInput);
            verify(modelMapper).toResponse(serviceOutput);
        }
    }

    @Nested
    @DisplayName("registCorrectValue: 実装側引数防衛（Objects.requireNonNull）")
    class ImplementationNullDefense {

        @Test
        @DisplayName("registCorrectValueメソッド_異常系_requestがnullの場合、NullPointerExceptionを送出し依存先が呼ばれないこと_1CE")
        void testRegistCorrectValue_withNullRequest_throwsNpeAndCallsNoCollaborator() {
            // Arrange: 引数 null（実装側 Objects.requireNonNull で防衛される想定）

            // Act & Assert: NPE 送出と依存未呼出を検証
            assertThatNullPointerException()
                    .isThrownBy(() -> sut.registCorrectValue(null))
                    .withMessageContaining("request");

            verifyNoInteractions(modelMapper);
            verifyNoInteractions(service);
        }
    }

    @Nested
    @DisplayName("registCorrectValue: 引数バリデーション（UTR-007 / UTR-045 executableValidator.validateParameters）")
    class ArgumentValidation {

        private ExecutableValidator executableValidator;
        private Method registCorrectValueMethod;

        @BeforeEach
        void setUpValidator() throws NoSuchMethodException {
            // UTR-037: ValidatorFactory から ExecutableValidator を取得
            ValidatorFactory factory = Validation.byDefaultProvider()
                    .configure()
                    .messageInterpolator(new ParameterMessageInterpolator())
                    .buildValidatorFactory();
            executableValidator = factory.getValidator().forExecutables();
            registCorrectValueMethod = RinsashoCntInfoCorrectValueApiImpl.class
                    .getMethod("registCorrectValue", RegistCorrectValueRequest.class);
        }

        @Nested
        @DisplayName("正常系")
        class 正常系 {

            @Test
            @DisplayName("registCorrectValueメソッド_正常系_全フィールド有効値の場合、バリデーション違反0件となること_2C")
            void testRegistCorrectValue_withAllFieldsValid_yieldsNoViolations() {
                // Arrange: 全フィールド有効なリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();

                // Act: テスト対象メソッドのバリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: 違反 0 件
                assertThat(violations).isEmpty();
            }
        }

        @Nested
        @DisplayName("異常系: @NotNull 違反")
        class NotNullViolations {

            @Test
            @DisplayName("registCorrectValueメソッド_異常系_brNoがnullの場合、@NotNullバリデーション違反となること_2C")
            void testRegistCorrectValue_withBrNoNull_yieldsNotNullViolation() {
                // Arrange: brNo を null としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setBrNo(null);

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: brNo に対する @NotNull 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".brNo");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(NotNull.class);
                        });
            }

            @Test
            @DisplayName("registCorrectValueメソッド_異常系_cmNoがnullの場合、@NotNullバリデーション違反となること_2C")
            void testRegistCorrectValue_withCmNoNull_yieldsNotNullViolation() {
                // Arrange: cmNo を null としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setCmNo(null);

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: cmNo に対する @NotNull 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".cmNo");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(NotNull.class);
                        });
            }

            @Test
            @DisplayName("registCorrectValueメソッド_異常系_lockInfoがnullの場合、@NotNullバリデーション違反となること_2C")
            void testRegistCorrectValue_withLockInfoNull_yieldsNotNullViolation() {
                // Arrange: lockInfo を null としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setLockInfo(null);

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: lockInfo に対する @NotNull 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".lockInfo");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(NotNull.class);
                        });
            }
        }

        @Nested
        @DisplayName("異常系: @Pattern 違反（PK 系フィールドの形式違反）")
        class PatternViolations {

            // UTR-021: 境界値（フォーマット境界 ─ 数字以外の混入が代表ケース）
            @Test
            @DisplayName("registCorrectValueメソッド_異常系_brNoが数字以外を含む場合、@Patternバリデーション違反となること_2C")
            void testRegistCorrectValue_withBrNoNonDigit_yieldsPatternViolation() {
                // Arrange: brNo にアルファベット混入のリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setBrNo("01a");

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: brNo に対する @Pattern 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".brNo");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(Pattern.class);
                        });
            }

            // UTR-021: 境界値（桁数境界 ─ 規定 7 桁から 1 桁少ない 6 桁が代表ケース）
            @Test
            @DisplayName("registCorrectValueメソッド_異常系_cmNoが規定桁数未満の場合、@Patternバリデーション違反となること_2C")
            void testRegistCorrectValue_withCmNoTooShort_yieldsPatternViolation() {
                // Arrange: cmNo が 6 桁（規定 7 桁未満）のリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setCmNo("901914");

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: cmNo に対する @Pattern 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".cmNo");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(Pattern.class);
                        });
            }
        }

        @Nested
        @DisplayName("異常系: 補正値の境界違反（@PositiveOrZero / @Digits）")
        class CorrectionValueViolations {

            // UTR-021: 境界値（0 以上を要求する @PositiveOrZero の負側境界 -1）
            @Test
            @DisplayName("registCorrectValueメソッド_異常系_補正値が負数の場合、@PositiveOrZeroバリデーション違反となること_2C")
            void testRegistCorrectValue_withNegativeCorrectionValue_yieldsPositiveOrZeroViolation() {
                // Arrange: loanDiscTotalCorrectionValue を負数 (-1) としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setLoanDiscTotalCorrectionValue(-1);

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: loanDiscTotalCorrectionValue に対する @PositiveOrZero 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".loanDiscTotalCorrectionValue");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(PositiveOrZero.class);
                        });
            }

            // UTR-021: 境界値（@Digits(integer=7) の桁数上限を 1 つ超える 10000000 = 8 桁）
            @Test
            @DisplayName("registCorrectValueメソッド_異常系_補正値が整数8桁の場合、@Digitsバリデーション違反となること_2C")
            void testRegistCorrectValue_withCorrectionValueExceedingDigits_yieldsDigitsViolation() {
                // Arrange: loanDiscTotalCorrectionValue を 8 桁 (10000000) としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setLoanDiscTotalCorrectionValue(10_000_000);

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: loanDiscTotalCorrectionValue に対する @Digits 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".loanDiscTotalCorrectionValue");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(Digits.class);
                        });
            }
        }

        @Nested
        @DisplayName("異常系: 補正理由の文字数境界違反（@Size）")
        class CorrectionReasonSizeViolation {

            // UTR-021: 境界値（@Size(max=100) の上限を 1 つ超える 101 文字）
            @Test
            @DisplayName("registCorrectValueメソッド_異常系_補正理由が101文字の場合、@Sizeバリデーション違反となること_2C")
            void testRegistCorrectValue_withCorrectionReasonExceedingMaxLength_yieldsSizeViolation() {
                // Arrange: correctionReason を 101 文字としたリクエストを準備
                RegistCorrectValueRequest request = newValidRequest();
                request.setCorrectionReason("a".repeat(101));

                // Act: バリデーションを実行
                Set<ConstraintViolation<RinsashoCntInfoCorrectValueApiImpl>> violations =
                        executableValidator.validateParameters(
                                sut, registCorrectValueMethod, new Object[] {request});

                // Assert: correctionReason に対する @Size 違反が含まれること
                assertThat(violations)
                        .hasSize(1)
                        .anySatisfy(v -> {
                            assertThat(v.getPropertyPath().toString()).endsWith(".correctionReason");
                            assertThat(v.getConstraintDescriptor().getAnnotation().annotationType())
                                    .isEqualTo(Size.class);
                        });
            }
        }
    }

    /** 全フィールドが妥当な値を持つリクエスト。各テストで必要に応じて 1 フィールドだけ書き換える。 */
    private static RegistCorrectValueRequest newValidRequest() {
        RegistCorrectValueRequest request = new RegistCorrectValueRequest();
        request.setBrNo(VALID_BR_NO);
        request.setCmNo(VALID_CM_NO);
        request.setLoanDiscTotalCorrectionValue(1000);
        request.setInternalJpyCorrectionValue(2000);
        request.setForexCreditTotalCorrectionValue(3000);
        request.setShiShoTotalCorrectionValue(4000);
        request.setRegulationTanpoCorrectionValueRegulationValue(5000);
        request.setRegulationTanpoCorrectionValueJikaBase(6000);
        request.setCorrectionReason("正常系の補正理由");
        request.setLockInfo(new LockInfo(VALID_EXCLUSIVE_KEY, VALID_EXCLUSIVE_COUNT));
        return request;
    }
}
