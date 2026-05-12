package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue;

import java.util.Objects;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jp.mufg.bk.yus.com.util.StringEditUtils;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.TRgKeisuHoseichiRepository;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceInput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto.RgV0501RegistCorrectValueServiceOutput;
import jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.mapper.KeisuHoseichiEntityMapper;
import jp.mufg.bk.yus.domain.service.shared.LockInfo;
import jp.mufg.bk.yus.lib.presentation.helper.domain.exclusive.interfaces.ExclusiveProcessHelper;

/**
 * 禀議計数情報補正値登録（RG_V0501）のドメインサービス。排他制御は楽観ロックに統一。
 */
public class RgV0501RegistCorrectValueService {

    private final TRgKeisuHoseichiRepository repository;
    private final ExclusiveProcessHelper exclusiveProcessHelper;
    private final KeisuHoseichiEntityMapper entityMapper;

    @Inject
    public RgV0501RegistCorrectValueService(
            TRgKeisuHoseichiRepository repository,
            ExclusiveProcessHelper exclusiveProcessHelper,
            KeisuHoseichiEntityMapper entityMapper) {
        this.repository = Objects.requireNonNull(repository, "repository");
        this.exclusiveProcessHelper = Objects.requireNonNull(exclusiveProcessHelper, "exclusiveProcessHelper");
        this.entityMapper = Objects.requireNonNull(entityMapper, "entityMapper");
    }

    /**
     * 補正値を登録する。既存レコードがあれば更新、未登録なら新規登録する。
     *
     * @param input サービス入力 DTO（presentation 層で妥当性チェック済）
     * @return 更新後の排他ロック情報を含むサービス出力 DTO
     * @throws NullPointerException input または lockInfo / brNo が null
     * @throws RuntimeException 排他チェック NG / DB アクセス失敗時
     */
    @Transactional(rollbackFor = Exception.class)
    public RgV0501RegistCorrectValueServiceOutput executeService(RgV0501RegistCorrectValueServiceInput input) {
        // Step 1: インプット取得（引数防衛）
        Objects.requireNonNull(input, "input");
        Objects.requireNonNull(input.getLockInfo(), "input.lockInfo");

        // Step 2: 排他更新回数チェック（楽観ロック）
        int updatedExclusiveCount = exclusiveProcessHelper.checkExclusiveCount(
                input.getLockInfo().getExclusiveKey(),
                input.getLockInfo().getExclusiveCount());

        // Step 3: サーバー用店番取得（3 桁 → 7 桁変換）
        String serverBrNo = StringEditUtils.toServerBrNo(input.getBrNo());

        // brno は Mapper で ignore されるため、ここで後付けする
        TRgKeisuHoseichi entity = entityMapper.toEntity(input);
        entity.setBrno(serverBrNo);

        // Step 4: 計数情報更新（0 件なら新規登録にフォールバック）
        int updatedCount = repository.updateByPrimaryKeyAndDelFlg(entity);
        if (updatedCount == 0) {
            repository.insert(entity);
        }

        // Step 5: ServiceOutput 生成（新しい LockInfo インスタンス、入力と参照非共有）
        return buildOutput(input.getLockInfo().getExclusiveKey(), updatedExclusiveCount);
    }

    private RgV0501RegistCorrectValueServiceOutput buildOutput(String exclusiveKey, int exclusiveCount) {
        RgV0501RegistCorrectValueServiceOutput output = new RgV0501RegistCorrectValueServiceOutput();
        output.setLockInfo(new LockInfo(exclusiveKey, exclusiveCount));
        return output;
    }
}
