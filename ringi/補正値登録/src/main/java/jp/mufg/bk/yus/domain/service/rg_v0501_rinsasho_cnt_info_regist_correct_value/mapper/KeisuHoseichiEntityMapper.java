package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;

/**
 * Service DTO ⇔ Table Entity 変換 Mapper（MapStruct コンパイル時自動生成）。
 */
@Mapper(componentModel = "cdi")
public interface KeisuHoseichiEntityMapper {

    /**
     * サービス入力 DTO を Table Entity に変換する。
     * brNo は Service 内で 3→7 桁変換した結果を後付けするため ignore する。
     *
     * @param dto サービス入力 DTO
     * @return Table Entity（{@code brNo} は未設定）
     */
    @Mapping(target = "brNo", ignore = true)
    RinsashoKeisuHoseichi toEntity(ServiceInputDto dto);

    /**
     * Table Entity から排他ロック情報 DTO に変換する（参照系ユースケース用の予備）。
     *
     * @param entity Table Entity
     * @return 排他ロック情報 DTO
     */
    LockInfoDto toLockInfoDto(RinsashoKeisuHoseichi entity);
}
