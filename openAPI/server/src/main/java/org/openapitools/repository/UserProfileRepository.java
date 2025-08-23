package org.openapitools.repository;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.openapitools.model.UserProfile;

import java.util.List;

@Mapper
public interface UserProfileRepository {
    
    /**
     * 全てのアクティブなユーザープロフィールを取得
     */
    List<UserProfile> selectAllActiveUserProfiles();
    
    /**
     * IDでユーザープロフィールを取得
     */
    UserProfile selectUserProfileById(@Param("id") String id);
    
    /**
     * 検索条件でユーザープロフィールを取得
     */
    List<UserProfile> selectUserProfilesBySearch(
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
    void insertUserProfile(UserProfile userProfile);
    
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
    void updateUserProfile(UserProfile userProfile);
    
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
}