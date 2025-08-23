package org.openapitools.infrastructure.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * データベース専用のデータ転送オブジェクト
 * MyBatisとデータベースとの間でのみ使用される
 * ドメインやAPIレイヤーからは独立
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserProfileDataModel {
    
    private String id;
    private String name;
    private Integer age;
    private String gender;
    private String location;
    private String bio;
    private String occupation;
    private String education;
    private String lookingFor;
    private Integer ageRangeMin;
    private Integer ageRangeMax;
    private Integer maxDistance;
    private Boolean isActive;
    private LocalDateTime createdDate;
    private LocalDateTime lastActive;
    
    // 関連データ（別テーブル）
    private List<String> interests;
    private List<String> photos;
}