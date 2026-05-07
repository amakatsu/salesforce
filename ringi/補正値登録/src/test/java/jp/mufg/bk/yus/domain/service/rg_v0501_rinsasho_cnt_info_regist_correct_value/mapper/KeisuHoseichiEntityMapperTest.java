package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mapstruct.factory.Mappers;

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;

/**
 * {@link KeisuHoseichiEntityMapper} の単体テスト。
 */
class KeisuHoseichiEntityMapperTest {

    private final KeisuHoseichiEntityMapper sut = Mappers.getMapper(KeisuHoseichiEntityMapper.class);

    @Nested
    @DisplayName("toEntity: ServiceInputDto から Entity への変換")
    class ToEntity {

        @Test
        @DisplayName("全フィールドが値を持つ場合、brNo を除く同名フィールドはそのまま転写される")
        void 全フィールド設定_brNo以外は転写される() {
            // given
            ServiceInputDto dto = new ServiceInputDto();
            dto.setBrNo("010");
            dto.setCmNo("9019149");
            dto.setLoanDiscTotalCorrectionValue(11111);
            dto.setInternalJpyCorrectionValue(22222);
            dto.setForexCreditTotalCorrectionValue(33333);
            dto.setShiShoTotalCorrectionValue(44444);
            dto.setRegulationTanpoCorrectionValueRegulationValue(55555);
            dto.setRegulationTanpoCorrectionValueJikaBase(66666);
            dto.setCorrectionReason("正常系の補正理由");
            dto.setLockInfo(new LockInfoDto("rkANKEN111111111111", 1));

            // when
            RinsashoKeisuHoseichi entity = sut.toEntity(dto);

            // then
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
        @DisplayName("brNo は @Mapping(ignore = true) のため、DTO に値があっても Entity 側は null になる")
        void brNoは常にignoreされnullになる() {
            // given
            ServiceInputDto dto = new ServiceInputDto();
            dto.setBrNo("010");
            dto.setCmNo("9019149");

            // when
            RinsashoKeisuHoseichi entity = sut.toEntity(dto);

            // then
            assertThat(entity.getBrNo()).isNull();
        }

        @Test
        @DisplayName("delFlg は DTO に存在しないため、Entity 側は null になる")
        void delFlgはDTOに存在しないためnullになる() {
            // given
            ServiceInputDto dto = new ServiceInputDto();
            dto.setCmNo("9019149");

            // when
            RinsashoKeisuHoseichi entity = sut.toEntity(dto);

            // then
            assertThat(entity.getDelFlg()).isNull();
        }

        @Nested
        @DisplayName("規定担保補正値: 規定値 と 時価ベース を独立フィールドとして個別に転写する")
        class RegulationTanpoCorrectionValue {

            @Test
            @DisplayName("規定値のみセット時、規定値だけ転写され時価ベースは null のまま")
            void 規定値のみセット_時価ベースはnull() {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setRegulationTanpoCorrectionValueRegulationValue(55555);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(55555);
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isNull();
            }

            @Test
            @DisplayName("時価ベースのみセット時、時価ベースだけ転写され規定値は null のまま")
            void 時価ベースのみセット_規定値はnull() {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setRegulationTanpoCorrectionValueJikaBase(66666);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(66666);
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isNull();
            }

            @Test
            @DisplayName("規定値と時価ベースに異なる値をセットすると、両者がそれぞれ独立に転写される")
            void 規定値と時価ベースは独立フィールドとして転写される() {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setRegulationTanpoCorrectionValueRegulationValue(55555);
                dto.setRegulationTanpoCorrectionValueJikaBase(66666);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getRegulationTanpoCorrectionValueRegulationValue()).isEqualTo(55555);
                assertThat(entity.getRegulationTanpoCorrectionValueJikaBase()).isEqualTo(66666);
            }
        }

        @Nested
        @DisplayName("補正値の境界値: 0 / Integer.MAX_VALUE / Integer.MIN_VALUE / null を欠落なく転写する")
        class CorrectionValueBoundary {

            @ParameterizedTest(name = "loanDiscTotalCorrectionValue = {0} がそのまま Entity へ転写される")
            @ValueSource(ints = {0, 1, Integer.MAX_VALUE, Integer.MIN_VALUE})
            void 補正値の境界値が転写される(int boundary) {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setLoanDiscTotalCorrectionValue(boundary);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getLoanDiscTotalCorrectionValue()).isEqualTo(boundary);
            }

            @ParameterizedTest(name = "internalJpyCorrectionValue が null の場合、Entity 側も null になる")
            @NullSource
            void 補正値がnullの場合Entityもnull(Integer nullValue) {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setInternalJpyCorrectionValue(nullValue);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getInternalJpyCorrectionValue()).isNull();
            }
        }

        @Nested
        @DisplayName("補正理由 (correctionReason): null / 空文字 / 通常文字列 / 100 バイト境界")
        class CorrectionReasonBoundary {

            @ParameterizedTest(name = "correctionReason = \"{0}\" がそのまま転写される")
            @ValueSource(strings = {"", "通常", "〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●"})
            void 補正理由はそのまま転写される(String reason) {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setCorrectionReason(reason);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getCorrectionReason()).isEqualTo(reason);
            }

            @Test
            @DisplayName("correctionReason が null の場合、Entity 側も null になる")
            void 補正理由がnullの場合Entityもnull() {
                // given
                ServiceInputDto dto = new ServiceInputDto();
                dto.setCorrectionReason(null);

                // when
                RinsashoKeisuHoseichi entity = sut.toEntity(dto);

                // then
                assertThat(entity.getCorrectionReason()).isNull();
            }
        }

        @Test
        @DisplayName("DTO 全フィールド未設定の場合、Entity の全フィールドが null になる")
        void 空DTO_Entity全フィールドがnull() {
            // given
            ServiceInputDto dto = new ServiceInputDto();

            // when
            RinsashoKeisuHoseichi entity = sut.toEntity(dto);

            // then
            assertThat(entity).isNotNull();
            assertThat(entity.getBrNo()).isNull();
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
        @DisplayName("入力 DTO が null の場合、MapStruct 標準仕様により null を返す")
        void DTOがnullの場合_nullを返す() {
            // when
            RinsashoKeisuHoseichi entity = sut.toEntity(null);

            // then
            assertThat(entity).isNull();
        }
    }

    @Nested
    @DisplayName("toLockInfoDto: Entity から LockInfoDto への変換")
    class ToLockInfoDto {

        @Test
        @DisplayName("Entity の排他キー・排他回数が DTO に転写される")
        void 排他キーと排他回数が転写される() {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();
            entity.setExclusiveKey("rkANKEN111111111111");
            entity.setExclusiveCount(2);

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto).isNotNull();
            assertThat(dto.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
            assertThat(dto.getExclusiveCount()).isEqualTo(2);
        }

        @ParameterizedTest(name = "exclusiveKey = \"{0}\" / exclusiveCount = {1} がそのまま転写される")
        @CsvSource({
            "'rkANKEN_minimal', 0",
            "'a', 1",
            "'1234567890123456789012345678901234567890123456789012345678901234567890', 2147483647"
        })
        void 排他キーと排他回数の境界値が転写される(String key, int count) {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();
            entity.setExclusiveKey(key);
            entity.setExclusiveCount(count);

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto.getExclusiveKey()).isEqualTo(key);
            assertThat(dto.getExclusiveCount()).isEqualTo(count);
        }

        @Test
        @DisplayName("Entity の補正値カラムは LockInfoDto に影響しない")
        void Entityの補正値カラムはLockInfoDtoに影響しない() {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();
            entity.setExclusiveKey("rkANKEN111111111111");
            entity.setExclusiveCount(1);
            entity.setLoanDiscTotalCorrectionValue(99999);
            entity.setCorrectionReason("DTO 側に漏れてはならない");

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
            assertThat(dto.getExclusiveCount()).isEqualTo(1);
            // LockInfoDto には補正値・補正理由のフィールドが存在しないこと自体がコンパイル時保証
        }

        @Test
        @DisplayName("exclusiveKey が null の場合、DTO の exclusiveKey も null")
        void 排他キーがnullの場合DTOの排他キーもnull() {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();
            entity.setExclusiveKey(null);
            entity.setExclusiveCount(1);

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto.getExclusiveKey()).isNull();
            assertThat(dto.getExclusiveCount()).isEqualTo(1);
        }

        @Test
        @DisplayName("exclusiveCount が null の場合、DTO の exclusiveCount も null")
        void 排他回数がnullの場合DTOの排他回数もnull() {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();
            entity.setExclusiveKey("rkANKEN111111111111");
            entity.setExclusiveCount(null);

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto.getExclusiveKey()).isEqualTo("rkANKEN111111111111");
            assertThat(dto.getExclusiveCount()).isNull();
        }

        @Test
        @DisplayName("Entity 全フィールド未設定の場合、DTO は両フィールドが null の空インスタンス")
        void 空Entity_DTO両フィールドnull() {
            // given
            RinsashoKeisuHoseichi entity = new RinsashoKeisuHoseichi();

            // when
            LockInfoDto dto = sut.toLockInfoDto(entity);

            // then
            assertThat(dto).isNotNull();
            assertThat(dto.getExclusiveKey()).isNull();
            assertThat(dto.getExclusiveCount()).isNull();
        }

        @Test
        @DisplayName("入力 Entity が null の場合、MapStruct 標準仕様により null を返す")
        void Entityがnullの場合_nullを返す() {
            // when
            LockInfoDto dto = sut.toLockInfoDto(null);

            // then
            assertThat(dto).isNull();
        }
    }
}
