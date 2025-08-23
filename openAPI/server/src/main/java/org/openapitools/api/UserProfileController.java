package org.openapitools.api;

import org.openapitools.model.UserProfile;
import org.openapitools.repository.UserProfileRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user-profiles")
@CrossOrigin(origins = "*") // SalesforceのCSP対応
public class UserProfileController {

    @Autowired
    private UserProfileRepository userProfileRepository;

    private int idCounter = 1;

    // 全ユーザープロフィール取得
    @GetMapping
    public ResponseEntity<List<UserProfile>> getAllUserProfiles() {
        try {
            List<UserProfile> activeProfiles = userProfileRepository.selectAllActiveUserProfiles();
            return ResponseEntity.ok(activeProfiles);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // 特定ユーザープロフィール取得
    @GetMapping("/{id}")
    public ResponseEntity<UserProfile> getUserProfile(@PathVariable String id) {
        try {
            UserProfile profile = userProfileRepository.selectUserProfileById(id);
            if (profile != null) {
                return ResponseEntity.ok(profile);
            }
            return ResponseEntity.notFound().build();
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

            // プロフィール基本情報を挿入
            userProfileRepository.insertUserProfile(userProfile);

            // 趣味を挿入
            if (userProfile.getInterests() != null && !userProfile.getInterests().isEmpty()) {
                userProfileRepository.insertUserInterests(newId, userProfile.getInterests());
            }

            // 写真を挿入
            if (userProfile.getPhotos() != null && !userProfile.getPhotos().isEmpty()) {
                userProfileRepository.insertUserPhotos(newId, userProfile.getPhotos());
            }

            return ResponseEntity.status(HttpStatus.CREATED).body(userProfile);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    // ユーザープロフィール更新
    @PutMapping("/{id}")
    public ResponseEntity<UserProfile> updateUserProfile(@PathVariable String id,
            @RequestBody UserProfile userProfile) {
        try {
            UserProfile existingProfile = userProfileRepository.selectUserProfileById(id);
            if (existingProfile == null) {
                return ResponseEntity.notFound().build();
            }

            // IDと作成日は保持
            userProfile.setId(id);
            userProfile.setCreatedDate(existingProfile.getCreatedDate());
            userProfile.setLastActive(new Date());

            // プロフィール基本情報を更新
            userProfileRepository.updateUserProfile(userProfile);

            // 趣味を更新（削除してから挿入）
            userProfileRepository.deleteUserInterests(id);
            if (userProfile.getInterests() != null && !userProfile.getInterests().isEmpty()) {
                userProfileRepository.insertUserInterests(id, userProfile.getInterests());
            }

            // 写真を更新（削除してから挿入）
            userProfileRepository.deleteUserPhotos(id);
            if (userProfile.getPhotos() != null && !userProfile.getPhotos().isEmpty()) {
                userProfileRepository.insertUserPhotos(id, userProfile.getPhotos());
            }

            return ResponseEntity.ok(userProfile);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    // ユーザープロフィール削除（論理削除）
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUserProfile(@PathVariable String id) {
        try {
            UserProfile profile = userProfileRepository.selectUserProfileById(id);
            if (profile != null) {
                userProfileRepository.deleteUserProfile(id);
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

            List<UserProfile> results = userProfileRepository.selectUserProfilesBySearch(
                    minAge, maxAge, gender, location, interests);

            return ResponseEntity.ok(results);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}