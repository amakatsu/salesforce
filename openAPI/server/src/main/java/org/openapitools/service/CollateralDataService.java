package org.openapitools.service;

import org.openapitools.mapper.CollateralDataMapper;
import org.openapitools.model.CollateralData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class CollateralDataService {
    
    @Autowired
    private CollateralDataMapper collateralDataMapper;
    
    // 全ての担保データを取得
    public List<CollateralData> getAllCollateralData() {
        return collateralDataMapper.findAll();
    }
    
    // IDで担保データを取得
    public Optional<CollateralData> getCollateralDataById(String id) {
        CollateralData collateralData = collateralDataMapper.findById(id);
        return collateralData != null ? Optional.of(collateralData) : Optional.empty();
    }
    
    // 担保データを作成
    public CollateralData createCollateralData(CollateralData collateralData) {
        if (collateralData.getId() == null || collateralData.getId().isEmpty()) {
            collateralData.setId("collateral_" + System.currentTimeMillis());
        }
        collateralDataMapper.insert(collateralData);
        return collateralData;
    }
    
    // 担保データを更新
    public CollateralData updateCollateralData(String id, CollateralData collateralData) {
        collateralData.setId(id);
        collateralDataMapper.update(collateralData);
        return collateralData;
    }
    
    // 担保データを削除
    public void deleteCollateralData(String id) {
        collateralDataMapper.deleteById(id);
    }
    
    // 担保データを一括更新
    public List<CollateralData> updateAllCollateralData(List<CollateralData> collateralDataList) {
        collateralDataMapper.deleteAll();
        for (CollateralData collateralData : collateralDataList) {
            collateralDataMapper.insert(collateralData);
        }
        return collateralDataMapper.findAll();
    }
}