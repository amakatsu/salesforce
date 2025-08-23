package org.openapitools.service;

import org.openapitools.repository.CreditDataRepository;
import org.openapitools.model.CreditData;
import org.openapitools.domain.entity.CreditDataEntity;
import org.openapitools.domain.service.CreditDataDomainService;
import org.openapitools.mapper.CreditDataDomainMapper;
import org.openapitools.domain.valueobject.CreditId;
import org.openapitools.domain.valueobject.Money;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CreditDataService {
    
    @Autowired
    private CreditDataRepository creditDataRepository;
    
    @Autowired
    private CreditDataDomainMapper domainMapper;
    
    @Autowired
    private CreditDataDomainService domainService;
    
    // 全ての与信データを取得
    public List<CreditData> getAllCreditData() {
        List<CreditData> apiModels = creditDataRepository.findAll();
        List<CreditDataEntity> entities = domainMapper.apiModelListToDomainList(apiModels);
        return domainMapper.domainListToApiModelList(entities);
    }
    
    // ドメインエンティティとして取得
    public List<CreditDataEntity> getAllCreditDataEntities() {
        List<CreditData> apiModels = creditDataRepository.findAll();
        return domainMapper.apiModelListToDomainList(apiModels);
    }

    // ID による検索
    public Optional<CreditData> getCreditDataById(String id) {
        CreditData creditData = creditDataRepository.findById(id);
        return creditData != null ? Optional.of(creditData) : Optional.empty();
    }

    // 与信データ作成
    public CreditData createCreditData(CreditData creditData) {
        if (creditData.getId() == null || creditData.getId().isEmpty()) {
            creditData.setId("credit_" + System.currentTimeMillis());
        }
        creditDataRepository.insert(creditData);
        return creditData;
    }

    // 与信データ更新
    public CreditData updateCreditData(String id, CreditData creditData) {
        creditData.setId(id);
        creditDataRepository.update(creditData);
        return creditData;
    }

    // 与信データ削除
    public void deleteCreditData(String id) {
        creditDataRepository.deleteById(id);
    }

    // 全削除とバッチ更新
    public void deleteAllCreditData() {
        creditDataRepository.deleteAll();
    }
    
    public List<CreditData> updateAllCreditData(List<CreditData> creditDataList) {
        creditDataRepository.deleteAll();
        for (CreditData creditData : creditDataList) {
            creditDataRepository.insert(creditData);
        }
        return creditDataRepository.findAll();
    }

}