package jp.mufg.bk.yus.presentation.api.interfaces;

import jakarta.validation.Valid;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueRequest;
import jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model.RegistCorrectValueResponse;

/** 計数情報 補正値登録 API のエンドポイント定義。 */
@Path("/rinsasho-cnt-info/correct-value")
public interface RinsashoCntInfoCorrectValueApi {

    /** 補正値を登録する。 */
    @POST
    @Path("/regist")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    RegistCorrectValueResponse registCorrectValue(@Valid RegistCorrectValueRequest request);
}
