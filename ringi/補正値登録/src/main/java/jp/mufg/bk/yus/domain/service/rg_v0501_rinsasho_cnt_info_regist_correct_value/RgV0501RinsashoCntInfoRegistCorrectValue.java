package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value;

import java.util.Objects;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

import jp.mufg.bk.yus.com.util.ExclusiveControlHelper;
import jp.mufg.bk.yus.com.util.StringEditUtil;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.RinsashoKeisuHoseichiRepository;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.LockInfoDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceInputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto.ServiceOutputDto;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.mapper.KeisuHoseichiEntityMapper;

/**
 * 禀議計数情報補正値登録（RG_V0501）のドメインサービス。排他制御は楽観ロックに統一。
 */
public class RgV0501RinsashoCntInfoRegistCorrectValue {

    private final RinsashoKeisuHoseichiRepository repository;
    private final ExclusiveControlHelper exclusiveControlHelper;
    private final StringEditUtil stringEditUtil;
    private final KeisuHoseichiEntityMapper entityMapper;

    @Inject
    public RgV0501RinsashoCntInfoRegistCorrectValue(
            RinsashoKeisuHoseichiRepository repository,
            ExclusiveControlHelper exclusiveControlHelper,
            StringEditUtil stringEditUtil,
            KeisuHoseichiEntityMapper entityMapper) {
        this.repository = Objects.requireNonNull(repository, "repository");
        this.exclusiveControlHelper = Objects.requireNonNull(exclusiveControlHelper, "exclusiveControlHelper");
        this.stringEditUtil = Objects.requireNonNull(stringEditUtil, "stringEditUtil");
        this.entityMapper = Objects.requireNonNull(entityMapper, "entityMapper");
    }

    /**
     * 補正値を登録する。既存レコードがあれば更新、未登録なら新規登録する。
     *
     * @param input サービス入力 DTO（presentation 層で妥当性チェック済）
     * @return 更新後の排他ロック情報を含むサービス出力 DTO
     * @throws NullPointerException input または lockInfo が null
     * @throws RuntimeException 排他チェック NG / DB アクセス失敗時
     */
    @Transactional(rollbackFor = Exception.class)
    public ServiceOutputDto registCorrectValue(ServiceInputDto input) {
        Objects.requireNonNull(input, "input");
        Objects.requireNonNull(input.getLockInfo(), "input.lockInfo");

        Integer updatedExclusiveCount = exclusiveControlHelper.checkExclusive(
                input.getLockInfo().getExclusiveKey(),
                input.getLockInfo().getExclusiveCount());

        String serverBrNo = stringEditUtil.toServerBrNo(input.getBrNo());

        // brNo は Mapper で @Mapping(target = "brNo", ignore = true) のため、ここで後付けする
        RinsashoKeisuHoseichi entity = entityMapper.toEntity(input);
        entity.setBrNo(serverBrNo);

        int updatedCount = repository.updateByPrimaryKeyAndDelFlg(entity);
        if (updatedCount == 0) {
            repository.insert(entity);
        }

        return buildOutput(input.getLockInfo().getExclusiveKey(), updatedExclusiveCount);
    }

    private ServiceOutputDto buildOutput(String exclusiveKey, Integer updatedExclusiveCount) {
        ServiceOutputDto output = new ServiceOutputDto();
        output.setLockInfo(new LockInfoDto(exclusiveKey, updatedExclusiveCount));
        return output;
    }
}
