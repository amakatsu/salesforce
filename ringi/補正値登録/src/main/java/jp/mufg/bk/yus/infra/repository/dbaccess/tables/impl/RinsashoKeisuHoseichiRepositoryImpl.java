package jp.mufg.bk.yus.infra.repository.dbaccess.tables.impl;

import java.util.Objects;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jp.mufg.bk.yus.domain.entity.dbaccess.tables.TRgKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.base.TRgKeisuHoseichiBaseRepository;
import jp.mufg.bk.yus.infra.mapper.tables.RinsashoKeisuHoseichiMapper;

/** {@link TRgKeisuHoseichiBaseRepository} の MyBatis 実装（Mapper への薄い委譲）。 */
@ApplicationScoped
public class RinsashoKeisuHoseichiRepositoryImpl implements TRgKeisuHoseichiBaseRepository {

    private final RinsashoKeisuHoseichiMapper mapper;

    @Inject
    public RinsashoKeisuHoseichiRepositoryImpl(RinsashoKeisuHoseichiMapper mapper) {
        this.mapper = Objects.requireNonNull(mapper, "mapper");
    }

    @Override
    public int updateByPrimaryKeyAndDelFlg(TRgKeisuHoseichi record) {
        Objects.requireNonNull(record, "record");
        return mapper.updateByPrimaryKeyAndDelFlg(record);
    }

    @Override
    public int insert(TRgKeisuHoseichi record) {
        Objects.requireNonNull(record, "record");
        return mapper.insert(record);
    }
}
