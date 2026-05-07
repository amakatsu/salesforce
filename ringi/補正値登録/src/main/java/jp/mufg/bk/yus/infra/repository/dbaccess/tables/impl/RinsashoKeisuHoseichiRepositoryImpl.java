package jp.mufg.bk.yus.infra.repository.dbaccess.tables.impl;

import java.util.Objects;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import jp.mufg.bk.yus.domain.entity.dbaccess.tables.RinsashoKeisuHoseichi;
import jp.mufg.bk.yus.domain.repository.dbaccess.tables.interfaces.RinsashoKeisuHoseichiRepository;
import jp.mufg.bk.yus.infra.mapper.tables.RinsashoKeisuHoseichiMapper;

/** {@link RinsashoKeisuHoseichiRepository} の MyBatis 実装（Mapper への薄い委譲）。 */
@ApplicationScoped
public class RinsashoKeisuHoseichiRepositoryImpl implements RinsashoKeisuHoseichiRepository {

    private final RinsashoKeisuHoseichiMapper mapper;

    @Inject
    public RinsashoKeisuHoseichiRepositoryImpl(RinsashoKeisuHoseichiMapper mapper) {
        this.mapper = Objects.requireNonNull(mapper, "mapper");
    }

    @Override
    public int updateByPrimaryKeyAndDelFlg(RinsashoKeisuHoseichi record) {
        Objects.requireNonNull(record, "record");
        return mapper.updateByPrimaryKeyAndDelFlg(record);
    }

    @Override
    public int insert(RinsashoKeisuHoseichi record) {
        Objects.requireNonNull(record, "record");
        return mapper.insert(record);
    }
}
