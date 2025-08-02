package org.openapitools.mapper;

import org.apache.ibatis.annotations.*;
import org.openapitools.model.CreditData;
import java.util.List;

@Mapper
public interface CreditDataMapper {
    
    @Select("SELECT * FROM credit_data")
    List<CreditData> findAll();
    
    @Select("SELECT * FROM credit_data WHERE id = #{id}")
    CreditData findById(@Param("id") String id);
    
    @Insert("INSERT INTO credit_data (id, label, due_date, rate, balance99, principal, change_amount, post_balance, actual_balance, correction, parent_id) " +
            "VALUES (#{id}, #{label}, #{dueDate}, #{rate}, #{balance99}, #{principal}, #{change}, #{postBalance}, #{actualBalance}, #{correction}, #{parentId})")
    void insert(CreditData creditData);
    
    @Update("UPDATE credit_data SET label = #{label}, due_date = #{dueDate}, rate = #{rate}, " +
            "balance99 = #{balance99}, principal = #{principal}, change_amount = #{change}, " +
            "post_balance = #{postBalance}, actual_balance = #{actualBalance}, correction = #{correction}, " +
            "parent_id = #{parentId} WHERE id = #{id}")
    void update(CreditData creditData);
    
    @Delete("DELETE FROM credit_data WHERE id = #{id}")
    void deleteById(@Param("id") String id);
    
    @Delete("DELETE FROM credit_data")
    void deleteAll();
}