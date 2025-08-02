package org.openapitools.service;

import org.openapitools.mapper.CreditDataMapper;
import org.openapitools.model.CreditData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class CreditDataService {
    
    @Autowired
    private CreditDataMapper creditDataMapper;
    
    // 全ての与信データを取得
    public List<CreditData> getAllCreditData() {
        return creditDataMapper.findAll();
    }

    // ID による検索
    public Optional<CreditData> getCreditDataById(String id) {
        CreditData creditData = creditDataMapper.findById(id);
        return creditData != null ? Optional.of(creditData) : Optional.empty();
    }

    // 与信データ作成
    public CreditData createCreditData(CreditData creditData) {
        if (creditData.getId() == null || creditData.getId().isEmpty()) {
            creditData.setId("credit_" + System.currentTimeMillis());
        }
        creditDataMapper.insert(creditData);
        return creditData;
    }

    // 与信データ更新
    public CreditData updateCreditData(String id, CreditData creditData) {
        creditData.setId(id);
        creditDataMapper.update(creditData);
        return creditData;
    }

    // 与信データ削除
    public void deleteCreditData(String id) {
        creditDataMapper.deleteById(id);
    }

    // 全削除とバッチ更新
    public void deleteAllCreditData() {
        creditDataMapper.deleteAll();
    }
    
    public List<CreditData> updateAllCreditData(List<CreditData> creditDataList) {
        creditDataMapper.deleteAll();
        for (CreditData creditData : creditDataList) {
            creditDataMapper.insert(creditData);
        }
        return creditDataMapper.findAll();
    }

}