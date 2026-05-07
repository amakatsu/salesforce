package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.NullValuePropertyMappingStrategy;
import org.mapstruct.factory.Mappers;

import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceOutputDto;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.LockInfo;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueResponse;

/**
 * presentation 層 Model と domain 層 ServiceDto の双方向変換 Mapper。
 *
 * <p>SET_TO_NULL は補正値系 7 項目と補正理由が required ではないため、空送信時の null を
 * そのまま domain 層へ伝搬させる目的（業務的な「未指定」セマンティクス維持）。
 *
 * <p>componentModel = "cdi" は暫定（escalations ESC-012-01）。{@link #INSTANCE} は
 * DI コンテナ未配備のテスト・スタンドアロン用フォールバック。
 */
@Mapper(componentModel = "cdi",
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.SET_TO_NULL)
public interface RegistCorrectValueModelMapper {

    RegistCorrectValueModelMapper INSTANCE = Mappers.getMapper(RegistCorrectValueModelMapper.class);

    ServiceInputDto toServiceInputDto(RegistCorrectValueRequest request);

    RegistCorrectValueResponse toResponse(ServiceOutputDto dto);

    LockInfoDto toServiceInputLockInfo(LockInfo source);

    LockInfo toResponseLockInfo(LockInfoDto source);
}
