package org.openapitools.repository;

import org.openapitools.model.CreditData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CreditDataRepository extends JpaRepository<CreditData, String> {
    
    // 親IDが指定された子要素を取得
    List<CreditData> findByParentId(String parentId);
    
    // ルート要素（親IDがnull）を取得
    @Query("SELECT c FROM CreditData c WHERE c.parentId IS NULL")
    List<CreditData> findRootElements();
    
    // ラベルで検索
    List<CreditData> findByLabelContaining(String label);
}