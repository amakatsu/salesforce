package org.openapitools.model;

import java.util.List;
import java.util.Date;
import com.fasterxml.jackson.annotation.JsonProperty;

public class UserProfile {
    
    @JsonProperty("id")
    private String id;
    
    @JsonProperty("name")
    private String name;
    
    @JsonProperty("age")
    private Integer age;
    
    @JsonProperty("gender")
    private String gender; // male, female, other
    
    @JsonProperty("location")
    private String location;
    
    @JsonProperty("bio")
    private String bio;
    
    @JsonProperty("interests")
    private List<String> interests;
    
    @JsonProperty("photos")
    private List<String> photos;
    
    @JsonProperty("occupation")
    private String occupation;
    
    @JsonProperty("education")
    private String education;
    
    @JsonProperty("lookingFor")
    private String lookingFor; // 友達, 恋人, 結婚相手
    
    @JsonProperty("ageRangeMin")
    private Integer ageRangeMin;
    
    @JsonProperty("ageRangeMax")
    private Integer ageRangeMax;
    
    @JsonProperty("maxDistance")
    private Integer maxDistance; // km
    
    @JsonProperty("isActive")
    private Boolean isActive;
    
    @JsonProperty("createdDate")
    private Date createdDate;
    
    @JsonProperty("lastActive")
    private Date lastActive;
    
    // Default constructor
    public UserProfile() {}
    
    // Constructor with all fields
    public UserProfile(String id, String name, Integer age, String gender, String location, 
                      String bio, List<String> interests, List<String> photos, String occupation,
                      String education, String lookingFor, Integer ageRangeMin, Integer ageRangeMax,
                      Integer maxDistance, Boolean isActive, Date createdDate, Date lastActive) {
        this.id = id;
        this.name = name;
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
        this.createdDate = createdDate;
        this.lastActive = lastActive;
    }
    
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
    
    public Date getCreatedDate() { return createdDate; }
    public void setCreatedDate(Date createdDate) { this.createdDate = createdDate; }
    
    public Date getLastActive() { return lastActive; }
    public void setLastActive(Date lastActive) { this.lastActive = lastActive; }
}