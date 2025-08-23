package org.openapitools.domain.entity;

import org.openapitools.domain.valueobject.UserId;
import org.openapitools.domain.valueobject.Age;
import org.openapitools.domain.valueobject.Gender;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;

public class UserProfileEntity {
    
    private final UserId userId;
    private String name;
    private Age age;
    private Gender gender;
    private String location;
    private String bio;
    private List<String> interests;
    private List<String> photos;
    private String occupation;
    private String education;
    private String lookingFor;
    private Age ageRangeMin;
    private Age ageRangeMax;
    private Integer maxDistance;
    private boolean isActive;
    private final LocalDateTime createdAt;
    private LocalDateTime lastActiveAt;
    
    public UserProfileEntity(UserId userId, String name) {
        this.userId = Objects.requireNonNull(userId, "UserId cannot be null");
        this.name = Objects.requireNonNull(name, "Name cannot be null");
        this.createdAt = LocalDateTime.now();
        this.lastActiveAt = LocalDateTime.now();
        this.isActive = true;
    }
    
    public UserProfileEntity(UserId userId, String name, Age age, Gender gender, 
                           String location, String bio, List<String> interests, 
                           List<String> photos, String occupation, String education,
                           String lookingFor, Age ageRangeMin, Age ageRangeMax,
                           Integer maxDistance, boolean isActive, 
                           LocalDateTime createdAt, LocalDateTime lastActiveAt) {
        this.userId = Objects.requireNonNull(userId, "UserId cannot be null");
        this.name = Objects.requireNonNull(name, "Name cannot be null");
        this.age = age;
        this.gender = gender;
        this.location = location;
        this.bio = bio;
        this.interests = interests;
        this.photos = photos;
        this.occupation = occupation;
        this.education = education;
        this.lookingFor = lookingFor;
        this.ageRangeMin = ageRangeMin;
        this.ageRangeMax = ageRangeMax;
        this.maxDistance = maxDistance;
        this.isActive = isActive;
        this.createdAt = createdAt != null ? createdAt : LocalDateTime.now();
        this.lastActiveAt = lastActiveAt != null ? lastActiveAt : LocalDateTime.now();
    }
    
    // Business methods
    public void updateProfile(String name, Age age, Gender gender, String location, String bio,
                            String occupation, String education) {
        if (name != null && !name.trim().isEmpty()) {
            this.name = name.trim();
        }
        this.age = age;
        this.gender = gender;
        this.location = location;
        this.bio = bio;
        this.occupation = occupation;
        this.education = education;
        this.lastActiveAt = LocalDateTime.now();
    }
    
    public void updatePreferences(String lookingFor, Age ageRangeMin, Age ageRangeMax, Integer maxDistance) {
        this.lookingFor = lookingFor;
        this.ageRangeMin = ageRangeMin;
        this.ageRangeMax = ageRangeMax;
        this.maxDistance = maxDistance;
        this.lastActiveAt = LocalDateTime.now();
    }
    
    public void addInterest(String interest) {
        if (interest != null && !interest.trim().isEmpty() && 
            (interests == null || !interests.contains(interest.trim()))) {
            interests.add(interest.trim());
            this.lastActiveAt = LocalDateTime.now();
        }
    }
    
    public void removeInterest(String interest) {
        if (interests != null) {
            interests.remove(interest);
            this.lastActiveAt = LocalDateTime.now();
        }
    }
    
    public void addPhoto(String photoUrl) {
        if (photoUrl != null && !photoUrl.trim().isEmpty() &&
            (photos == null || !photos.contains(photoUrl.trim()))) {
            photos.add(photoUrl.trim());
            this.lastActiveAt = LocalDateTime.now();
        }
    }
    
    public void removePhoto(String photoUrl) {
        if (photos != null) {
            photos.remove(photoUrl);
            this.lastActiveAt = LocalDateTime.now();
        }
    }
    
    public void activate() {
        this.isActive = true;
        this.lastActiveAt = LocalDateTime.now();
    }
    
    public void deactivate() {
        this.isActive = false;
    }
    
    public boolean isMatchingPreferences(UserProfileEntity other) {
        if (!this.isActive || !other.isActive) return false;
        
        // Age range check
        if (this.ageRangeMin != null && other.age != null) {
            if (!other.age.isInRange(this.ageRangeMin, this.ageRangeMax)) {
                return false;
            }
        }
        
        // Reverse age range check
        if (other.ageRangeMin != null && this.age != null) {
            if (!this.age.isInRange(other.ageRangeMin, other.ageRangeMax)) {
                return false;
            }
        }
        
        return true;
    }
    
    // Getters
    public UserId getUserId() { return userId; }
    public String getName() { return name; }
    public Age getAge() { return age; }
    public Gender getGender() { return gender; }
    public String getLocation() { return location; }
    public String getBio() { return bio; }
    public List<String> getInterests() { return interests; }
    public List<String> getPhotos() { return photos; }
    public String getOccupation() { return occupation; }
    public String getEducation() { return education; }
    public String getLookingFor() { return lookingFor; }
    public Age getAgeRangeMin() { return ageRangeMin; }
    public Age getAgeRangeMax() { return ageRangeMax; }
    public Integer getMaxDistance() { return maxDistance; }
    public boolean isActive() { return isActive; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getLastActiveAt() { return lastActiveAt; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UserProfileEntity that = (UserProfileEntity) o;
        return Objects.equals(userId, that.userId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(userId);
    }
}