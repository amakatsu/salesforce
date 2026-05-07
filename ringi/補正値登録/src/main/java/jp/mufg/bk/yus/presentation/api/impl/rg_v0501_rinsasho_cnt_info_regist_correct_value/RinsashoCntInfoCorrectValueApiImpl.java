package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value;

import java.util.Objects;

import jakarta.inject.Inject;

import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.RgV0501RinsashoCntInfoRegistCorrectValue;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceOutputDto;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper.RegistCorrectValueModelMapper;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueResponse;
import jp.mufg.bk.yus.presentation.api.interfaces.RinsashoCntInfoCorrectValueApi;

/** 計数情報 補正値登録 API の実装。 */
public class RinsashoCntInfoCorrectValueApiImpl implements RinsashoCntInfoCorrectValueApi {

    private final RgV0501RinsashoCntInfoRegistCorrectValue service;
    private final RegistCorrectValueModelMapper modelMapper;

    @Inject
    public RinsashoCntInfoCorrectValueApiImpl(
            RgV0501RinsashoCntInfoRegistCorrectValue service,
            RegistCorrectValueModelMapper modelMapper) {
        this.service = Objects.requireNonNull(service, "service");
        this.modelMapper = Objects.requireNonNull(modelMapper, "modelMapper");
    }

    @Override
    public RegistCorrectValueResponse registCorrectValue(RegistCorrectValueRequest request) {
        Objects.requireNonNull(request, "request");
        ServiceInputDto serviceInput = modelMapper.toServiceInputDto(request);
        ServiceOutputDto serviceOutput = service.registCorrectValue(serviceInput);
        return modelMapper.toResponse(serviceOutput);
    }
}
