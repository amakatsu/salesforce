package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue;

import java.util.Objects;
import jakarta.inject.Inject;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.RgV0501RegistCorrectValueService;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.mapper.RegistCorrectValueModelMapper;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model.RegistCorrectValueResponse;
import jp.mufg.bk.yus.presentation.api.interfaces.RinsashoCntInfoCorrectValueApi;

/** 計数情報 補正値登録 API の実装。 */
public class RinsashoCntInfoCorrectValueApiImpl implements RinsashoCntInfoCorrectValueApi {

    private final RgV0501RegistCorrectValueService service;
    private final RegistCorrectValueModelMapper modelMapper;

    @Inject
    public RinsashoCntInfoCorrectValueApiImpl(
            RgV0501RegistCorrectValueService service,
            RegistCorrectValueModelMapper modelMapper) {
        this.service = Objects.requireNonNull(service, "service");
        this.modelMapper = Objects.requireNonNull(modelMapper, "modelMapper");
    }

    @Override
    public RegistCorrectValueResponse registCorrectValue(RegistCorrectValueRequest request) {
        Objects.requireNonNull(request, "request");
        RgV0501RegistCorrectValueServiceInput serviceInput = modelMapper.toServiceInput(request);
        RgV0501RegistCorrectValueServiceOutput serviceOutput = service.executeService(serviceInput);
        return modelMapper.toResponse(serviceOutput);
    }
}
