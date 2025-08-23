package org.openapitools.service;

import org.openapitools.repository.CollateralDataRepository;
import org.openapitools.model.CollateralData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class CollateralDataService {
    
    @Autowired
    private CollateralDataRepository collateralDataRepository;
    
    // 全ての担保データを取得
    public List<CollateralData> getAllCollateralData() {
        return collateralDataRepository.findAll();
    }
    
    // IDで担保データを取得
    public Optional<CollateralData> getCollateralDataById(String id) {
        CollateralData collateralData = collateralDataRepository.findById(id);
        return collateralData != null ? Optional.of(collateralData) : Optional.empty();
    }
    
    // 担保データを作成
    public CollateralData createCollateralData(CollateralData collateralData) {
        if (collateralData.getId() == null || collateralData.getId().isEmpty()) {
            collateralData.setId("collateral_" + System.currentTimeMillis());
        }
        collateralDataRepository.insert(collateralData);
        return collateralData;
    }
    
    // 担保データを更新
    public CollateralData updateCollateralData(String id, CollateralData collateralData) {
        collateralData.setId(id);
        collateralDataRepository.update(collateralData);
        return collateralData;
    }
    
    // 担保データを削除
    public void deleteCollateralData(String id) {
        collateralDataRepository.deleteById(id);
    }
    
    // 担保データを一括更新
    public List<CollateralData> updateAllCollateralData(List<CollateralData> collateralDataList) {
        collateralDataRepository.deleteAll();
        for (CollateralData collateralData : collateralDataList) {
            collateralDataRepository.insert(collateralData);
        }
        return collateralDataRepository.findAll();
    }
}