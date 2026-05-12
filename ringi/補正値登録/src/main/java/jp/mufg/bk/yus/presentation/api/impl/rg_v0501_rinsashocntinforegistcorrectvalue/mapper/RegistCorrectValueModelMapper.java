package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.NullValuePropertyMappingStrategy;
import org.mapstruct.factory.Mappers;

import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueResponse;

/**
 * presentation 層 Model と domain 層 ServiceInput / ServiceOutput の双方向変換 Mapper。
 *
 * <p>SET_TO_NULL は補正値系 7 項目と補正理由が required ではないため、空送信時の null を
 * そのまま domain 層へ伝搬させる目的（業務的な「未指定」セマンティクス維持）。
 *
 * <p>LockInfo は presentation / domain の双方で共有 LockInfo を直接使用するため変換不要。
 * MapStruct は同型フィールドを自動コピーする。
 */
@Mapper(componentModel = "cdi",
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.SET_TO_NULL)
public interface RegistCorrectValueModelMapper {

    RegistCorrectValueModelMapper INSTANCE = Mappers.getMapper(RegistCorrectValueModelMapper.class);

    RgV0501RegistCorrectValueServiceInput toServiceInput(RegistCorrectValueRequest request);

    RegistCorrectValueResponse toResponse(RgV0501RegistCorrectValueServiceOutput output);
}
