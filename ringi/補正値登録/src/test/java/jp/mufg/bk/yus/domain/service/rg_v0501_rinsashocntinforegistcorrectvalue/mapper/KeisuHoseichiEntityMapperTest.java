package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.mapper;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mapstruct.factory.Mappers;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;

/**
 * {@link KeisuHoseichiEntityMapper} の単体テスト。
 */
class KeisuHoseichiEntityMapperTest {

    // UTR-043: Mapper インターフェースは Mappers.getMapper でインスタンス生成
    private final KeisuHoseichiEntityMapper sut = Mappers.getMapper(KeisuHoseichiEntityMapper.class);

    @Nested
    @DisplayName("toEntity: ServiceInput から Entity への変換")
    class ToEntity {

        @Test
        @DisplayName("toEntityメソッド_正常系_全フィールド設定の場合、brnoを除く同名フィールドがそのまま転写されること_1BD3B")
        void testToEntity_withAllFieldsSet_mapsAllExceptBrno() {
            // Arrange: 全フィールドを設定した DTO を準備
            RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
            dto.setBrNo("010");
            dto.setCmNo("9019149");
            dto.setLoanDiscTotalCorrectionValue(11111);
            dto.setInternalJpyCorrectionValue(22222);
            dto.setForexCreditTotalCorrectionValue(33333);
            dto.setShiShoTotalCorrectionValue(44444);
            dto.setRegulationTanpoCorrectionValueRegulationValue(55555);
            dto.setRegulationTanpoCorrectionValueJikaBase(66666);
            dto.setCorrectionReason("正常系の補正理由");
            dto.setLockInfo(new LockInfo("rkANKEN111111111111", 1));

            // Act: テスト対象のメソッドを実行
            TRgKeisuHoseichi entity = sut.toEntity(dto);

            // Assert: brno を除く同名フィールドが転写されていること
            assertThat(entity).isNotNull();
            assertThat(entity.getCmNo()).isEqualTo("9019149");
            assertThat(entity.getLoanDiscTotalCorrectionValue()).isEqualTo(11111);
            assertThat(entity.getInternalJpyCorrectionValue()).isEqualTo(22222);
            assertThat(entity.getForexCreditTotalCorrectionValue()).isEqualTo(33333);
            assertThat(entity.getShiShoTotalCorrectionValue()).isEqualTo(44444);
            assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(55555);
            assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(66666);
            assertThat(entity.getCorrectionReason()).isEqualTo("正常系の補正理由");
        }

        @Test
        @DisplayName("toEntityメソッド_正常系_brnoは@Mapping(ignore=true)のためDTOに値があってもEntity側はnullになること_1D3B")
        void testToEntity_alwaysIgnoresBrnoAsNull() {
            // Arrange: brNo と cmNo を設定した DTO を準備
            RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
            dto.setBrNo("010");
            dto.setCmNo("9019149");

            // Act: テスト対象のメソッドを実行
            TRgKeisuHoseichi entity = sut.toEntity(dto);

            // Assert: entity.brno は null
            assertThat(entity.getBrno()).isNull();
        }

        @Test
        @DisplayName("toEntityメソッド_正常系_delFlgはDTOに存在しないためEntity側はnullになること_1D3B")
        void testToEntity_delFlgRemainsNull() {
            // Arrange: cmNo のみを設定した DTO を準備
            RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
            dto.setCmNo("9019149");

            // Act: テスト対象のメソッドを実行
            TRgKeisuHoseichi entity = sut.toEntity(dto);

            // Assert: entity.delFlg は null
            assertThat(entity.getDelFlg()).isNull();
        }

        @Nested
        @DisplayName("規定担保補正値: 規定値 と 時価ベース を独立フィールドとして個別に転写する")
        class RegulationTanpoCorrectionValue {

            @Test
            @DisplayName("toEntityメソッド_正常系_規定値のみセット時、規定値だけが転写され時価ベースはnullのままとなること_1BD3B")
            void testToEntity_withOnlyRegulationValueSet_jikaBaseRemainsNull() {
                // Arrange: 規定値のみを設定した DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setRegulationTanpoCorrectionValueRegulationValue(55555);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: 規定値は転写、時価ベースは null
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(55555);
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isNull();
            }

            @Test
            @DisplayName("toEntityメソッド_正常系_時価ベースのみセット時、時価ベースだけが転写され規定値はnullのままとなること_1BD3B")
            void testToEntity_withOnlyJikaBaseSet_regulationValueRemainsNull() {
                // Arrange: 時価ベースのみを設定した DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setRegulationTanpoCorrectionValueJikaBase(66666);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: 時価ベースは転写、規定値は null
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(66666);
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isNull();
            }

            @Test
            @DisplayName("toEntityメソッド_正常系_規定値と時価ベースに異なる値をセットすると両者が独立に転写されること_1BD3B")
            void testToEntity_mapsRegulationAndJikaBaseIndependently() {
                // Arrange: 規定値と時価ベースに異なる値を設定した DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setRegulationTanpoCorrectionValueRegulationValue(55555);
                dto.setRegulationTanpoCorrectionValueJikaBase(66666);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: 両フィールドが独立に転写されていること
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(55555);
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(66666);
            }
        }

        @Nested
        @DisplayName("補正値の境界値: 0 / Integer.MAX_VALUE / Integer.MIN_VALUE / null を欠落なく転写する")
        class CorrectionValueBoundary {

            // UTR-021: 分岐判定のテストデータは境界値を設定
            @ParameterizedTest(name = "loanDiscTotalCorrectionValue = {0} がそのまま Entity へ転写される")
            @ValueSource(ints = {0, 1, Integer.MAX_VALUE, Integer.MIN_VALUE})
            @DisplayName("toEntityメソッド_正常系_補正値の境界値が欠落なくEntityへ転写されること_1BD3B")
            void testToEntity_mapsCorrectionValueBoundary(int boundary) {
                // Arrange: 境界値をセットした DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setLoanDiscTotalCorrectionValue(boundary);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: 境界値が転写されていること
                assertThat(entity.getLoanDiscTotalCorrectionValue()).isEqualTo(boundary);
            }

            @ParameterizedTest(name = "internalJpyCorrectionValue が null の場合、Entity 側も null になる")
            @NullSource
            @DisplayName("toEntityメソッド_正常系_補正値がnullの場合、Entity側もnullとなること_1D3B")
            void testToEntity_withNullCorrectionValue_entityRemainsNull(Integer nullValue) {
                // Arrange: 補正値を null とした DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setInternalJpyCorrectionValue(nullValue);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: Entity 側も null
                assertThat(entity.getInternalJpyCorrectionValue()).isNull();
            }
        }

        @Nested
        @DisplayName("補正理由 (correctionReason): null / 空文字 / 通常文字列 / 100 バイト境界")
        class CorrectionReasonBoundary {

            // UTR-021: 分岐判定のテストデータは境界値を設定（空文字 / 通常文字 / 100 バイト相当）
            @ParameterizedTest(name = "correctionReason = \"{0}\" がそのまま転写される")
            @ValueSource(strings = {"", "通常", "〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●"})
            @DisplayName("toEntityメソッド_正常系_補正理由（空文字_通常_境界）がそのまま転写されること_1BD3B")
            void testToEntity_mapsCorrectionReasonAsIs(String reason) {
                // Arrange: 補正理由をセットした DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setCorrectionReason(reason);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: 補正理由が転写されていること
                assertThat(entity.getCorrectionReason()).isEqualTo(reason);
            }

            @Test
            @DisplayName("toEntityメソッド_正常系_補正理由がnullの場合、Entity側もnullとなること_1D3B")
            void testToEntity_withNullCorrectionReason_entityRemainsNull() {
                // Arrange: 補正理由を null とした DTO を準備
                RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();
                dto.setCorrectionReason(null);

                // Act: テスト対象のメソッドを実行
                TRgKeisuHoseichi entity = sut.toEntity(dto);

                // Assert: Entity 側も null
                assertThat(entity.getCorrectionReason()).isNull();
            }
        }

        @Test
        @DisplayName("toEntityメソッド_正常系_DTO全フィールド未設定の場合、Entity全フィールドがnullとなること_1D3B")
        void testToEntity_withEmptyDto_allFieldsRemainNull() {
            // Arrange: 全フィールド未設定の DTO を準備
            RgV0501RegistCorrectValueServiceInput dto = new RgV0501RegistCorrectValueServiceInput();

            // Act: テスト対象のメソッドを実行
            TRgKeisuHoseichi entity = sut.toEntity(dto);

            // Assert: Entity 全フィールドが null
            assertThat(entity).isNotNull();
            assertThat(entity.getBrno()).isNull();
            assertThat(entity.getCmNo()).isNull();
            assertThat(entity.getDelFlg()).isNull();
            assertThat(entity.getLoanDiscTotalCorrectionValue()).isNull();
            assertThat(entity.getInternalJpyCorrectionValue()).isNull();
            assertThat(entity.getForexCreditTotalCorrectionValue()).isNull();
            assertThat(entity.getShiShoTotalCorrectionValue()).isNull();
            assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isNull();
            assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isNull();
            assertThat(entity.getCorrectionReason()).isNull();
        }

        @Test
        @DisplayName("toEntityメソッド_異常系_入力DTOがnullの場合、MapStruct標準仕様によりnullを返すこと_1B3B")
        void testToEntity_withNullDto_returnsNull() {
            // Arrange: 入力 DTO を null として準備

            // Act: テスト対象のメソッドを実行
            TRgKeisuHoseichi entity = sut.toEntity(null);

            // Assert: 戻り値が null
            assertThat(entity).isNull();
        }
    }
}
