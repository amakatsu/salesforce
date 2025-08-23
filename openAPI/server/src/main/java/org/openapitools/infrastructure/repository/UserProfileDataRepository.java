package org.openapitools.infrastructure.repository;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.openapitools.infrastructure.dto.UserProfileDataModel;

import java.util.List;

/**
 * MyBatis専用のデータアクセスリポジトリ
 * UserProfileDataModel（DB DTO）のみを扱う
 * ドメインやAPIレイヤーから完全に独立
 */
@Mapper
public interface UserProfileDataRepository {
    
    /**
     * 全てのアクティブなユーザープロフィールを取得
     */
    List<UserProfileDataModel> selectAllActiveUserProfiles();
    
    /**
     * IDでユーザープロフィールを取得
     */
    UserProfileDataModel selectUserProfileById(@Param("id") String id);
    
    /**
     * 検索条件でユーザープロフィールを取得
     */
    List<UserProfileDataModel> selectUserProfilesBySearch(
        @Param("minAge") Integer minAge,
        @Param("maxAge") Integer maxAge,
        @Param("gender") String gender,
        @Param("location") String location,
        @Param("interests") List<String> interests
    );
    
    /**
     * ユーザーIDで趣味リストを取得
     */
    List<String> selectInterestsByUserId(@Param("userId") String userId);
    
    /**
     * ユーザーIDで写真リストを取得
     */
    List<String> selectPhotosByUserId(@Param("userId") String userId);
    
    /**
     * ユーザープロフィールを挿入
     */
    void insertUserProfile(UserProfileDataModel dataModel);
    
    /**
     * ユーザーの趣味を挿入
     */
    void insertUserInterests(@Param("userId") String userId, @Param("interests") List<String> interests);
    
    /**
     * ユーザーの写真を挿入
     */
    void insertUserPhotos(@Param("userId") String userId, @Param("photos") List<String> photos);
    
    /**
     * ユーザープロフィールを更新
     */
    void updateUserProfile(UserProfileDataModel dataModel);
    
    /**
     * ユーザーの趣味を削除
     */
    void deleteUserInterests(@Param("userId") String userId);
    
    /**
     * ユーザーの写真を削除
     */
    void deleteUserPhotos(@Param("userId") String userId);
    
    /**
     * ユーザープロフィールを論理削除
     */
    void deleteUserProfile(@Param("id") String id);
    
    /**
     * ユーザーIDの存在確認
     */
    boolean existsUserProfileById(@Param("id") String id);
}