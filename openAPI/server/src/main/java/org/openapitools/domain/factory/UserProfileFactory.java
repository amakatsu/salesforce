package org.openapitools.domain.factory;

import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.model.UserProfile;
import org.openapitools.application.mapper.UserProfileDomainMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * ドメインエンティティの生成を担当するFactory
 * ドメインルールに従った正しいエンティティ作成とValidationを行う
 */
@Component
public class UserProfileFactory {
    
    @Autowired
    private UserProfileDomainMapper domainMapper;
    
    /**
     * APIモデルからドメインエンティティを作成
     * ドメインルールとValidationを適用
     */
    public UserProfileEntity createFromApiModel(UserProfile apiModel) {
        // 基本的なValidation
        validateApiModel(apiModel);
        
        // ドメインエンティティの作成
        UserProfileEntity entity = domainMapper.apiModelToDomain(apiModel);
        
        // ドメイン固有のValidationとビジネスルール適用
        validateDomainRules(entity);
        
        return entity;
    }
    
    /**
     * 新規ユーザープロフィール作成（IDを自動生成）
     */
    public UserProfileEntity createNewUserProfile(String name) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("名前は必須です");
        }
        
        // 新しいUserIdを生成（実際は採番ロジックが必要）
        String newId = generateNewUserId();
        UserId userId = new UserId(newId);
        
        return UserProfileEntity.create(userId, name.trim());
    }
    
    /**
     * ドメインエンティティからAPIモデルに変換
     */
    public UserProfile toApiModel(UserProfileEntity entity) {
        return domainMapper.domainToApiModel(entity);
    }
    
    /**
     * ドメインエンティティのリストをAPIモデルのリストに変換
     */
    public List<UserProfile> toApiModelList(List<UserProfileEntity> entities) {
        return domainMapper.domainListToApiModelList(entities);
    }
    
    /**
     * APIモデルの基本的なValidation
     */
    private void validateApiModel(UserProfile apiModel) {
        if (apiModel == null) {
            throw new IllegalArgumentException("UserProfileは必須です");
        }
        
        if (apiModel.getName() == null || apiModel.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("名前は必須です");
        }
        
        if (apiModel.getId() == null || apiModel.getId().trim().isEmpty()) {
            throw new IllegalArgumentException("IDは必須です");
        }
        
        // 年齢の妥当性チェック
        if (apiModel.getAge() != null && (apiModel.getAge() < 0 || apiModel.getAge() > 150)) {
            throw new IllegalArgumentException("年齢は0-150の範囲で入力してください");
        }
        
        // 年齢範囲の妥当性チェック
        if (apiModel.getAgeRangeMin() != null && apiModel.getAgeRangeMax() != null) {
            if (apiModel.getAgeRangeMin() > apiModel.getAgeRangeMax()) {
                throw new IllegalArgumentException("年齢範囲の最小値が最大値より大きくなっています");
            }
        }
    }
    
    /**
     * ドメイン固有のValidationとビジネスルール
     */
    private void validateDomainRules(UserProfileEntity entity) {
        // 年齢制限のビジネスルール
        if (entity.getAge() != null && !entity.getAge().isAdult()) {
            throw new IllegalArgumentException("18歳未満のユーザーは登録できません");
        }
        
        // プロフィール写真の制限
        if (entity.getPhotos() != null && entity.getPhotos().size() > 10) {
            throw new IllegalArgumentException("写真は10枚以下にしてください");
        }
        
        // 興味の制限
        if (entity.getInterests() != null && entity.getInterests().size() > 20) {
            throw new IllegalArgumentException("興味は20個以下にしてください");
        }
        
        // 名前の長さ制限
        if (entity.getName() != null && entity.getName().length() > 50) {
            throw new IllegalArgumentException("名前は50文字以下にしてください");
        }
        
        // 自己紹介文の長さ制限
        if (entity.getBio() != null && entity.getBio().length() > 1000) {
            throw new IllegalArgumentException("自己紹介文は1000文字以下にしてください");
        }
    }
    
    /**
     * 新しいUserIDを生成（実装例）
     */
    private String generateNewUserId() {
        // 実際はSequenceやUUIDを使用
        return "user" + System.currentTimeMillis();
    }
}