package org.openapitools.repository;

import org.apache.ibatis.annotations.*;
import org.openapitools.model.CollateralData;
import java.util.List;

@Mapper
public interface CollateralDataRepository {
    
    @Select("SELECT * FROM collateral_data")
    List<CollateralData> findAll();
    
    @Select("SELECT * FROM collateral_data WHERE id = #{id}")
    CollateralData findById(@Param("id") String id);
    
    @Insert("INSERT INTO collateral_data (id, collateral_type, reg_value, market_value, parent_id) " +
            "VALUES (#{id}, #{collateralType}, #{regValue}, #{marketValue}, #{parentId})")
    void insert(CollateralData collateralData);
    
    @Update("UPDATE collateral_data SET collateral_type = #{collateralType}, reg_value = #{regValue}, " +
            "market_value = #{marketValue}, parent_id = #{parentId} WHERE id = #{id}")
    void update(CollateralData collateralData);
    
    @Delete("DELETE FROM collateral_data WHERE id = #{id}")
    void deleteById(@Param("id") String id);
    
    @Delete("DELETE FROM collateral_data")
    void deleteAll();
}