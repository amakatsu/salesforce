package jp.mufg.bk.yus.com.util;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

/**
 * {@link StringEditUtils} の単体テスト。
 */
@DisplayName("StringEditUtils")
class StringEditUtilsTest {

    @Nested
    @DisplayName("Step1: toServerBrNo 正常系")
    class Step1_NormalCase {

        @Test
        @DisplayName("toServerBrNoメソッド_正常系_3桁文字列の場合、先頭0000付与の7桁文字列が返ること_1A")
        void testToServerBrNo_with3DigitInput_returns7DigitZeroPadded() {
            // Arrange:
            final String input = "010";

            // Act:
            final String actual = StringEditUtils.toServerBrNo(input);

            // Assert:
            assertThat(actual).isEqualTo("0000010");
        }
    }

    @Nested
    @DisplayName("Step2: toServerBrNo 境界値")
    class Step2_BoundaryValue {

        // UTR-021: 境界値
        @ParameterizedTest(name = "[{index}] 入力={0} → 期待={1}")
        @CsvSource({
                "'000', '0000000'",
                "'999', '0000999'",
                "'001', '0000001'"
        })
        @DisplayName("toServerBrNoメソッド_正常系_3桁境界値の場合、先頭0000付与の7桁文字列が返ること_1A")
        void testToServerBrNo_with3DigitBoundaryInput_returns7DigitZeroPadded(String input, String expected) {
            // Arrange: @CsvSource で注入

            // Act:
            final String actual = StringEditUtils.toServerBrNo(input);

            // Assert:
            assertThat(actual).isEqualTo(expected);
        }
    }

    @Nested
    @DisplayName("Step3: toServerBrNo 異常系・エッジケース")
    class Step3_NullAndEdgeCase {

        @Test
        @DisplayName("toServerBrNoメソッド_異常系_null入力の場合、NullPointerExceptionが送出されること_1C")
        void testToServerBrNo_withNullInput_throwsNullPointerException() {
            // Arrange:
            final String input = null;

            // Act & Assert:
            assertThatThrownBy(() -> StringEditUtils.toServerBrNo(input))
                    .isInstanceOf(NullPointerException.class)
                    .hasMessageContaining("brNo3");
        }

        @ParameterizedTest(name = "[{index}] 入力={0} → 期待={1}")
        @CsvSource({
                "'',     '0000'",
                "' ',    '0000 '",
                "'01',   '000001'",
                "'0100', '00000100'"
        })
        @DisplayName("toServerBrNoメソッド_異常系_3桁以外の入力の場合、入力依存の文字列が返ること_1A")
        void testToServerBrNo_withNon3DigitInput_returnsInputDependentString(String input, String expected) {
            // Arrange: @CsvSource で注入。桁数バリデーションは行わない実装ゆえ現状の挙動を固定化（Q-A3-05 殿承認済）

            // Act:
            final String actual = StringEditUtils.toServerBrNo(input);

            // Assert:
            assertThat(actual).isEqualTo(expected);
        }
    }

    @Nested
    @DisplayName("Step4: utility class インスタンス化禁止")
    class Step4_UtilityClassConstraint {

        @Test
        @DisplayName("StringEditUtilsクラス_異常系_リフレクションでprivate_ctorを呼び出した場合、AssertionErrorが送出されること_1F")
        void testPrivateConstructor_whenInvokedViaReflection_throwsAssertionError() throws NoSuchMethodException {
            // Arrange: private ctor をリフレクションで可視化
            final Constructor<StringEditUtils> ctor = StringEditUtils.class.getDeclaredConstructor();
            ctor.setAccessible(true);

            // Act & Assert: InvocationTargetException でラップされ、cause が AssertionError であること
            assertThatThrownBy(ctor::newInstance)
                    .isInstanceOf(InvocationTargetException.class)
                    .hasCauseInstanceOf(AssertionError.class)
                    .cause()
                    .hasMessageContaining("utility class");
        }
    }
}
