package org.openapitools.presentation.api;

import org.openapitools.model.UserProfile;
import org.openapitools.application.service.UserProfileService;
import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.service.UserProfileDomainService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

import java.util.*;

@RestController
@RequestMapping("/api/user-profiles")
@CrossOrigin(origins = "*") // SalesforceのCSP対応
public class UserProfileController {

    @Autowired
    private UserProfileService userProfileService;

    private int idCounter = 1;

    // 全ユーザープロフィール取得
    @GetMapping
    public ResponseEntity<List<UserProfile>> getAllUserProfiles() {
        try {
            List<UserProfile> activeProfiles = userProfileService.getAllActiveUserProfiles();
            return ResponseEntity.ok(activeProfiles);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // 特定ユーザープロフィール取得
    @GetMapping("/{id}")
    public ResponseEntity<UserProfile> getUserProfile(@PathVariable String id) {
        try {
            return userProfileService.getUserProfileById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // 新規ユーザープロフィール作成
    @PostMapping
    public ResponseEntity<UserProfile> createUserProfile(@RequestBody UserProfile userProfile) {
        try {
            String newId = "user" + String.format("%03d", idCounter++);
            userProfile.setId(newId);
            userProfile.setCreatedDate(new Date());
            userProfile.setLastActive(new Date());
            userProfile.setIsActive(true);

            UserProfile created = userProfileService.createUserProfile(userProfile);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // ユーザープロフィール更新
    @PutMapping("/{id}")
    public ResponseEntity<UserProfile> updateUserProfile(@PathVariable String id,
            @RequestBody UserProfile userProfile) {
        try {
            Optional<UserProfile> existingProfileOpt = userProfileService.getUserProfileById(id);
            if (existingProfileOpt.isEmpty()) {
                return ResponseEntity.notFound().build();
            }

            UserProfile existingProfile = existingProfileOpt.get();
            
            // IDと作成日は保持
            userProfile.setId(id);
            userProfile.setCreatedDate(existingProfile.getCreatedDate());
            userProfile.setLastActive(new Date());

            UserProfile updated = userProfileService.updateUserProfile(id, userProfile);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // ユーザープロフィール削除（論理削除）
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUserProfile(@PathVariable String id) {
        try {
            Optional<UserProfile> profile = userProfileService.getUserProfileById(id);
            if (profile.isPresent()) {
                userProfileService.deleteUserProfile(id);
                return ResponseEntity.noContent().build();
            }
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // プロフィール検索
    @PostMapping("/search")
    public ResponseEntity<List<UserProfile>> searchUserProfiles(@RequestBody Map<String, Object> searchCriteria) {
        try {
            Integer minAge = (Integer) searchCriteria.get("minAge");
            Integer maxAge = (Integer) searchCriteria.get("maxAge");
            String gender = (String) searchCriteria.get("gender");
            String location = (String) searchCriteria.get("location");
            @SuppressWarnings("unchecked")
            List<String> interests = (List<String>) searchCriteria.get("interests");

            List<UserProfile> results = userProfileService.searchUserProfiles(
                    minAge, maxAge, gender, location, interests);

            return ResponseEntity.ok(results);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // ドメインサービス機能のAPI
    
    // マッチング候補取得
    @GetMapping("/{id}/matches")
    public ResponseEntity<List<String>> getMatchingProfiles(@PathVariable String id) {
        try {
            List<UserProfileEntity> matches = userProfileService.findMatchingProfiles(id);
            List<String> matchIds = matches.stream()
                .map(entity -> entity.getUserId().getValue())
                .toList();
            return ResponseEntity.ok(matchIds);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // プロフィール完成度取得
    @GetMapping("/{id}/completeness")
    public ResponseEntity<Map<String, Object>> getProfileCompleteness(@PathVariable String id) {
        try {
            int completeness = userProfileService.calculateProfileCompleteness(id);
            Map<String, Object> response = new HashMap<>();
            response.put("completeness", completeness);
            response.put("status", completeness >= 80 ? "完璧" : 
                                  completeness >= 60 ? "良好" :
                                  completeness >= 40 ? "普通" : "要改善");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // プロフィール検証
    @GetMapping("/{id}/validation")
    public ResponseEntity<Map<String, Object>> validateProfile(@PathVariable String id) {
        try {
            UserProfileDomainService.ProfileValidationResult validation = 
                userProfileService.validateProfile(id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("isValid", validation.isValid());
            response.put("errors", validation.getErrors());
            response.put("warnings", validation.getWarnings());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 活動ランク取得
    @GetMapping("/{id}/activity-rank")
    public ResponseEntity<Map<String, Object>> getActivityRank(@PathVariable String id) {
        try {
            UserProfileDomainService.UserActivityRank rank = 
                userProfileService.calculateActivityRank(id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("rank", rank.name());
            response.put("displayName", rank.getDisplayName());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}