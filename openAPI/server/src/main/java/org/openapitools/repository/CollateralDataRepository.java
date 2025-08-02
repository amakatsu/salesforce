package org.openapitools.repository;

import org.openapitools.model.CollateralData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CollateralDataRepository extends JpaRepository<CollateralData, String> {
    
    // 親IDが指定された子要素を取得
    List<CollateralData> findByParentId(String parentId);
    
    // ルート要素（親IDがnull）を取得
    @Query("SELECT c FROM CollateralData c WHERE c.parentId IS NULL")
    List<CollateralData> findRootElements();
    
    // 担保種類で検索
    List<CollateralData> findByCollateralTypeContaining(String collateralType);
}