package org.openapitools.application.service;

import org.openapitools.repository.CreditDataRepository;
import org.openapitools.model.CreditData;
import org.openapitools.domain.entity.CreditDataEntity;
import org.openapitools.domain.service.CreditDataDomainService;
import org.openapitools.domain.valueobject.Money;
import org.openapitools.application.mapper.CreditDataDomainMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

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
        if (creditData != null) {
            CreditDataEntity entity = domainMapper.apiModelToDomain(creditData);
            return Optional.of(domainMapper.domainToApiModel(entity));
        }
        return Optional.empty();
    }
    
    // ドメインエンティティとして検索
    public Optional<CreditDataEntity> getCreditDataEntityById(String id) {
        CreditData creditData = creditDataRepository.findById(id);
        if (creditData != null) {
            return Optional.of(domainMapper.apiModelToDomain(creditData));
        }
        return Optional.empty();
    }

    // 与信データ作成
    public CreditData createCreditData(CreditData creditData) {
        if (creditData.getId() == null || creditData.getId().isEmpty()) {
            creditData.setId("credit_" + System.currentTimeMillis());
        }
        
        // ドメインエンティティで検証
        CreditDataEntity entity = domainMapper.apiModelToDomain(creditData);
        
        CreditData apiModel = domainMapper.domainToApiModel(entity);
        creditDataRepository.insert(apiModel);
        return apiModel;
    }
    
    // ドメインエンティティで作成
    public CreditDataEntity createCreditDataEntity(CreditDataEntity entity) {
        CreditData apiModel = domainMapper.domainToApiModel(entity);
        if (apiModel.getId() == null || apiModel.getId().isEmpty()) {
            apiModel.setId("credit_" + System.currentTimeMillis());
        }
        creditDataRepository.insert(apiModel);
        return domainMapper.apiModelToDomain(apiModel);
    }

    // 与信データ更新
    public CreditData updateCreditData(String id, CreditData creditData) {
        CreditDataEntity entity = domainMapper.apiModelToDomain(creditData);
        entity.getCreditId(); // ドメイン検証
        
        creditData.setId(id);
        CreditData apiModel = domainMapper.domainToApiModel(entity);
        apiModel.setId(id);
        creditDataRepository.update(apiModel);
        return apiModel;
    }
    
    // ドメインエンティティで更新
    public CreditDataEntity updateCreditDataEntity(String id, CreditDataEntity entity) {
        CreditData apiModel = domainMapper.domainToApiModel(entity);
        apiModel.setId(id);
        creditDataRepository.update(apiModel);
        return domainMapper.apiModelToDomain(apiModel);
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
        
        // ドメインエンティティで検証
        List<CreditDataEntity> entities = domainMapper.apiModelListToDomainList(creditDataList);
        List<CreditData> validatedModels = domainMapper.domainListToApiModelList(entities);
        
        for (CreditData creditData : validatedModels) {
            creditDataRepository.insert(creditData);
        }
        return creditDataRepository.findAll();
    }
    
    // ドメインサービス機能
    public Money getTotalBalance() {
        List<CreditDataEntity> entities = getAllCreditDataEntities();
        return domainService.calculateTotalBalance(entities);
    }
    
    public List<CreditDataEntity> getHighRiskCredits() {
        List<CreditDataEntity> entities = getAllCreditDataEntities();
        return domainService.findHighRiskCredits(entities);
    }
    
    public List<CreditDataEntity> getOverdueCredits() {
        List<CreditDataEntity> entities = getAllCreditDataEntities();
        return domainService.findOverdueCredits(entities);
    }
    
    public CreditDataDomainService.CreditRiskLevel evaluateRiskLevel(String id) {
        Optional<CreditDataEntity> entity = getCreditDataEntityById(id);
        return entity.map(domainService::evaluateRiskLevel)
                    .orElse(CreditDataDomainService.CreditRiskLevel.LOW);
    }
    
    public int calculateHealthScore(String id) {
        Optional<CreditDataEntity> entity = getCreditDataEntityById(id);
        return entity.map(domainService::calculateHealthScore).orElse(0);
    }

}