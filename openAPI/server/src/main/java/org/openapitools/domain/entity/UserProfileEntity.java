package org.openapitools.domain.entity;

import lombok.Builder;
import lombok.Getter;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.domain.valueobject.Age;
import org.openapitools.domain.valueobject.Gender;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;

@Getter
@Builder(toBuilder = true)
@lombok.Setter(lombok.AccessLevel.PACKAGE)
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
    @Builder.Default
    private boolean isActive = true;
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
    @Builder.Default
    private LocalDateTime lastActiveAt = LocalDateTime.now();
    
    
    // Factory method to create new instances
    public static UserProfileEntity create(UserId userId, String name) {
        Objects.requireNonNull(userId, "UserId cannot be null");
        Objects.requireNonNull(name, "Name cannot be null");
        
        return UserProfileEntity.builder()
                .userId(userId)
                .name(name.trim())
                .build();
    }
    
    // Business methods that return new instances
    public UserProfileEntity updateProfile(String name, Age age, Gender gender, String location, String bio,
                            String occupation, String education) {
        return this.toBuilder()
                .name(name != null && !name.trim().isEmpty() ? name.trim() : this.name)
                .age(age)
                .gender(gender)
                .location(location)
                .bio(bio)
                .occupation(occupation)
                .education(education)
                .lastActiveAt(LocalDateTime.now())
                .build();
    }
    
    public UserProfileEntity updatePreferences(String lookingFor, Age ageRangeMin, Age ageRangeMax, Integer maxDistance) {
        return this.toBuilder()
                .lookingFor(lookingFor)
                .ageRangeMin(ageRangeMin)
                .ageRangeMax(ageRangeMax)
                .maxDistance(maxDistance)
                .lastActiveAt(LocalDateTime.now())
                .build();
    }
    
    public UserProfileEntity activate() {
        return this.toBuilder()
                .isActive(true)
                .lastActiveAt(LocalDateTime.now())
                .build();
    }
    
    public UserProfileEntity deactivate() {
        return this.toBuilder()
                .isActive(false)
                .build();
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