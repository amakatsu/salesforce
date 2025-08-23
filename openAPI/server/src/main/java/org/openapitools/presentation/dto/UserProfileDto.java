package org.openapitools.presentation.dto;

import java.util.List;

public class UserProfileDto {
    
    private String id;
    private String name;
    private Integer age;
    private String gender;
    private String location;
    private String bio;
    private List<String> interests;
    private List<String> photos;
    private String occupation;
    private String education;
    private String lookingFor;
    private Integer ageRangeMin;
    private Integer ageRangeMax;
    private Integer maxDistance;
    private Boolean isActive;
    
    // デフォルトコンストラクタ
    public UserProfileDto() {}
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
    
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
    
    public List<String> getInterests() { return interests; }
    public void setInterests(List<String> interests) { this.interests = interests; }
    
    public List<String> getPhotos() { return photos; }
    public void setPhotos(List<String> photos) { this.photos = photos; }
    
    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }
    
    public String getEducation() { return education; }
    public void setEducation(String education) { this.education = education; }
    
    public String getLookingFor() { return lookingFor; }
    public void setLookingFor(String lookingFor) { this.lookingFor = lookingFor; }
    
    public Integer getAgeRangeMin() { return ageRangeMin; }
    public void setAgeRangeMin(Integer ageRangeMin) { this.ageRangeMin = ageRangeMin; }
    
    public Integer getAgeRangeMax() { return ageRangeMax; }
    public void setAgeRangeMax(Integer ageRangeMax) { this.ageRangeMax = ageRangeMax; }
    
    public Integer getMaxDistance() { return maxDistance; }
    public void setMaxDistance(Integer maxDistance) { this.maxDistance = maxDistance; }
    
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }
}