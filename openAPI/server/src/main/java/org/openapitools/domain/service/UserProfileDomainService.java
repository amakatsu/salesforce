package org.openapitools.domain.service;

import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.domain.repository.UserProfileDomainRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserProfileDomainService {
    
    @Autowired
    private UserProfileDomainRepository domainRepository;
    
    /**
     * ユーザープロフィールのマッチング候補を取得
     */
    public List<UserProfileEntity> findMatchingProfiles(UserProfileEntity requester, 
                                                        List<UserProfileEntity> allProfiles) {
        return allProfiles.stream()
            .filter(profile -> !profile.getUserId().equals(requester.getUserId()))
            .filter(profile -> requester.isMatchingPreferences(profile))
            .collect(Collectors.toList());
    }
    
    /**
     * プロフィールの完成度を計算（0-100%）
     */
    public int calculateProfileCompleteness(UserProfileEntity profile) {
        int totalFields = 10;
        int completedFields = 0;
        
        if (profile.getName() != null && !profile.getName().trim().isEmpty()) completedFields++;
        if (profile.getAge() != null) completedFields++;
        if (profile.getGender() != null) completedFields++;
        if (profile.getLocation() != null && !profile.getLocation().trim().isEmpty()) completedFields++;
        if (profile.getBio() != null && !profile.getBio().trim().isEmpty()) completedFields++;
        if (profile.getOccupation() != null && !profile.getOccupation().trim().isEmpty()) completedFields++;
        if (profile.getEducation() != null && !profile.getEducation().trim().isEmpty()) completedFields++;
        if (profile.getInterests() != null && !profile.getInterests().isEmpty()) completedFields++;
        if (profile.getPhotos() != null && !profile.getPhotos().isEmpty()) completedFields++;
        if (profile.getLookingFor() != null && !profile.getLookingFor().trim().isEmpty()) completedFields++;
        
        return (completedFields * 100) / totalFields;
    }
    
    /**
     * プロフィールの妥当性を検証
     */
    public ProfileValidationResult validateProfile(UserProfileEntity profile) {
        ProfileValidationResult result = new ProfileValidationResult();
        
        // 必須フィールドの検証
        if (profile.getName() == null || profile.getName().trim().isEmpty()) {
            result.addError("名前は必須です");
        }
        
        if (profile.getAge() != null && !profile.getAge().isAdult()) {
            result.addWarning("18歳未満のユーザーには制限があります");
        }
        
        // 年齢範囲の妥当性チェック
        if (profile.getAgeRangeMin() != null && profile.getAgeRangeMax() != null) {
            if (profile.getAgeRangeMin().getValue() > profile.getAgeRangeMax().getValue()) {
                result.addError("年齢範囲の最小値が最大値より大きくなっています");
            }
        }
        
        // プロフィール写真の妥当性
        if (profile.getPhotos() != null && profile.getPhotos().size() > 10) {
            result.addWarning("写真は10枚以下にすることをお勧めします");
        }
        
        // 興味の妥当性
        if (profile.getInterests() != null && profile.getInterests().size() > 20) {
            result.addWarning("興味は20個以下にすることをお勧めします");
        }
        
        return result;
    }
    
    /**
     * ユーザーの活動ランクを計算
     */
    public UserActivityRank calculateActivityRank(UserProfileEntity profile) {
        int completeness = calculateProfileCompleteness(profile);
        
        if (!profile.isActive()) {
            return UserActivityRank.INACTIVE;
        }
        
        if (completeness >= 80) {
            return UserActivityRank.PREMIUM;
        } else if (completeness >= 60) {
            return UserActivityRank.ACTIVE;
        } else if (completeness >= 40) {
            return UserActivityRank.CASUAL;
        } else {
            return UserActivityRank.BEGINNER;
        }
    }
    
    // ドメインサービスの主要メソッド（純粋なドメインロジック）
    
    /**
     * 全アクティブユーザー取得
     */
    public List<UserProfileEntity> getAllActiveUserProfiles() {
        return domainRepository.findAllActive();
    }
    
    /**
     * ID による検索
     */
    public Optional<UserProfileEntity> getUserProfileById(String id) {
        return domainRepository.findById(new UserId(id));
    }
    
    /**
     * ユーザープロフィール作成
     */
    public UserProfileEntity createUserProfile(UserProfileEntity entity) {
        // ドメイン検証
        ProfileValidationResult validation = validateProfile(entity);
        
        if (!validation.isValid()) {
            throw new IllegalArgumentException("プロフィール検証エラー: " + 
                String.join(", ", validation.getErrors()));
        }
        
        // ドメインリポジトリで永続化
        return domainRepository.save(entity);
    }
    
    /**
     * ユーザープロフィール更新
     */
    public UserProfileEntity updateUserProfile(UserId userId, UserProfileEntity entity) {
        // 存在確認
        if (!domainRepository.existsById(userId)) {
            throw new IllegalArgumentException("指定されたユーザーは存在しません: " + userId.getValue());
        }
        
        // ドメイン検証
        ProfileValidationResult validation = validateProfile(entity);
        
        if (!validation.isValid()) {
            throw new IllegalArgumentException("プロフィール検証エラー: " + 
                String.join(", ", validation.getErrors()));
        }
        
        return domainRepository.update(entity);
    }
    
    /**
     * 削除
     */
    public void deleteUserProfile(UserId userId) {
        if (!domainRepository.existsById(userId)) {
            throw new IllegalArgumentException("指定されたユーザーは存在しません: " + userId.getValue());
        }
        
        domainRepository.deleteById(userId);
    }
    
    /**
     * 検索
     */
    public List<UserProfileEntity> searchUserProfiles(Integer minAge, Integer maxAge, 
                                                     String gender, String location, 
                                                     List<String> interests) {
        return domainRepository.findBySearchCriteria(minAge, maxAge, gender, location, interests);
    }
    
    public static class ProfileValidationResult {
        private final List<String> errors = new java.util.ArrayList<>();
        private final List<String> warnings = new java.util.ArrayList<>();
        
        public void addError(String error) {
            errors.add(error);
        }
        
        public void addWarning(String warning) {
            warnings.add(warning);
        }
        
        public boolean isValid() {
            return errors.isEmpty();
        }
        
        public List<String> getErrors() {
            return errors;
        }
        
        public List<String> getWarnings() {
            return warnings;
        }
    }
    
    public enum UserActivityRank {
        INACTIVE("非アクティブ"),
        BEGINNER("初心者"),
        CASUAL("カジュアル"),
        ACTIVE("アクティブ"),
        PREMIUM("プレミアム");
        
        private final String displayName;
        
        UserActivityRank(String displayName) {
            this.displayName = displayName;
        }
        
        public String getDisplayName() {
            return displayName;
        }
    }
}