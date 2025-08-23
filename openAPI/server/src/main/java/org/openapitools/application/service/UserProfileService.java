package org.openapitools.application.service;

import org.openapitools.model.UserProfile;
import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.service.UserProfileDomainService;
import org.openapitools.domain.factory.UserProfileFactory;
import org.openapitools.domain.valueobject.UserId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserProfileService {
    
    @Autowired
    private UserProfileFactory userProfileFactory;
    
    @Autowired
    private UserProfileDomainService domainService;
    
    // 全アクティブユーザー取得
    public List<UserProfile> getAllActiveUserProfiles() {
        List<UserProfileEntity> entities = domainService.getAllActiveUserProfiles();
        return userProfileFactory.toApiModelList(entities);
    }
    
    // ドメインエンティティとして取得
    public List<UserProfileEntity> getAllActiveUserProfileEntities() {
        return domainService.getAllActiveUserProfiles();
    }
    
    // ID による検索
    public Optional<UserProfile> getUserProfileById(String id) {
        return domainService.getUserProfileById(id)
            .map(userProfileFactory::toApiModel);
    }
    
    // ドメインエンティティとして検索
    public Optional<UserProfileEntity> getUserProfileEntityById(String id) {
        return domainService.getUserProfileById(id);
    }
    
    // ユーザープロフィール作成
    public UserProfile createUserProfile(UserProfile userProfile) {
        UserProfileEntity entity = userProfileFactory.createFromApiModel(userProfile);
        UserProfileEntity created = domainService.createUserProfile(entity);
        return userProfileFactory.toApiModel(created);
    }
    
    // ドメインエンティティで作成
    public UserProfileEntity createUserProfileEntity(UserProfileEntity entity) {
        return domainService.createUserProfile(entity);
    }
    
    // ユーザープロフィール更新
    public UserProfile updateUserProfile(String id, UserProfile userProfile) {
        UserProfileEntity entity = userProfileFactory.createFromApiModel(userProfile);
        UserProfileEntity updated = domainService.updateUserProfile(new UserId(id), entity);
        return userProfileFactory.toApiModel(updated);
    }
    
    // 削除
    public void deleteUserProfile(String id) {
        domainService.deleteUserProfile(new UserId(id));
    }
    
    // 検索
    public List<UserProfile> searchUserProfiles(Integer minAge, Integer maxAge, 
                                               String gender, String location, 
                                               List<String> interests) {
        List<UserProfileEntity> entities = domainService.searchUserProfiles(
            minAge, maxAge, gender, location, interests);
        return userProfileFactory.toApiModelList(entities);
    }
    
    // ドメインサービス機能の委譲
    public List<UserProfileEntity> findMatchingProfiles(String requesterId) {
        Optional<UserProfileEntity> requester = domainService.getUserProfileById(requesterId);
        if (requester.isEmpty()) {
            return List.of();
        }
        
        List<UserProfileEntity> allProfiles = domainService.getAllActiveUserProfiles();
        return domainService.findMatchingProfiles(requester.get(), allProfiles);
    }
    
    public int calculateProfileCompleteness(String userId) {
        Optional<UserProfileEntity> entity = domainService.getUserProfileById(userId);
        return entity.map(domainService::calculateProfileCompleteness).orElse(0);
    }
    
    public UserProfileDomainService.ProfileValidationResult validateProfile(String userId) {
        Optional<UserProfileEntity> entity = domainService.getUserProfileById(userId);
        return entity.map(domainService::validateProfile)
                    .orElse(new UserProfileDomainService.ProfileValidationResult());
    }
    
    public UserProfileDomainService.UserActivityRank calculateActivityRank(String userId) {
        Optional<UserProfileEntity> entity = domainService.getUserProfileById(userId);
        return entity.map(domainService::calculateActivityRank)
                    .orElse(UserProfileDomainService.UserActivityRank.INACTIVE);
    }
}