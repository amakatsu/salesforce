package org.openapitools.domain.repository;

import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.valueobject.UserId;

import java.util.List;
import java.util.Optional;

/**
 * ドメイン層のリポジトリインターフェース
 * ドメインエンティティのみを扱う
 */
public interface UserProfileDomainRepository {
    
    /**
     * 全てのアクティブなユーザープロフィールを取得
     */
    List<UserProfileEntity> findAllActive();
    
    /**
     * IDでユーザープロフィールを取得
     */
    Optional<UserProfileEntity> findById(UserId userId);
    
    /**
     * ユーザープロフィールを保存
     */
    UserProfileEntity save(UserProfileEntity entity);
    
    /**
     * ユーザープロフィールを更新
     */
    UserProfileEntity update(UserProfileEntity entity);
    
    /**
     * ユーザープロフィールを削除（論理削除）
     */
    void deleteById(UserId userId);
    
    /**
     * 検索条件でユーザープロフィールを取得
     */
    List<UserProfileEntity> findBySearchCriteria(
        Integer minAge,
        Integer maxAge,
        String gender,
        String location,
        List<String> interests
    );
    
    /**
     * ユーザーIDの存在確認
     */
    boolean existsById(UserId userId);
}