package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;

/**
 * Service Input ⇔ Table Entity 変換 Mapper（MapStruct コンパイル時自動生成）。
 */
@Mapper(componentModel = "cdi")
public interface KeisuHoseichiEntityMapper {

    /**
     * サービス入力 DTO を Table Entity に変換する。
     * brno は Service 内で 3→7 桁変換した結果を後付けするため ignore する。
     * lockInfo はネスト構造のため明示マッピングで entity のフラット列へフラット化する。
     *
     * @param dto サービス入力 DTO
     * @return Table Entity（{@code brno} は未設定）
     */
    @Mapping(target = "brno", ignore = true)
    @Mapping(source = "lockInfo.exclusiveKey", target = "exclusiveKey")
    @Mapping(source = "lockInfo.exclusiveCount", target = "exclusiveCount")
    TRgKeisuHoseichi toEntity(RgV0501RegistCorrectValueServiceInput dto);
}
