package org.openapitools.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;
import org.openapitools.dto.UserProfileDto;
import org.openapitools.model.UserProfile;
import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.domain.valueobject.Age;
import org.openapitools.domain.valueobject.Gender;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;

@Mapper(componentModel = "spring")
public interface UserProfileDomainMapper {
    
    UserProfileDomainMapper INSTANCE = Mappers.getMapper(UserProfileDomainMapper.class);
    
    /**
     * Domain Entity → API Model
     */
    @Mapping(target = "id", source = "userId", qualifiedByName = "userIdToString")
    @Mapping(target = "age", source = "age", qualifiedByName = "ageToInteger")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "genderToString")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "ageToInteger")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "ageToInteger")
    @Mapping(target = "isActive", source = "active")
    @Mapping(target = "createdDate", source = "createdAt", qualifiedByName = "localDateTimeToDate")
    @Mapping(target = "lastActive", source = "lastActiveAt", qualifiedByName = "localDateTimeToDate")
    UserProfile domainToApiModel(UserProfileEntity entity);
    
    /**
     * API Model → Domain Entity
     */
    @Mapping(target = "userId", source = "id", qualifiedByName = "stringToUserId")
    @Mapping(target = "age", source = "age", qualifiedByName = "integerToAge")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "stringToGender")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "integerToAge")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "integerToAge")
    @Mapping(target = "active", source = "isActive")
    @Mapping(target = "createdAt", source = "createdDate", qualifiedByName = "dateToLocalDateTime")
    @Mapping(target = "lastActiveAt", source = "lastActive", qualifiedByName = "dateToLocalDateTime")
    UserProfileEntity apiModelToDomain(UserProfile model);
    
    /**
     * Domain Entity → DTO
     */
    @Mapping(target = "id", source = "userId", qualifiedByName = "userIdToString")
    @Mapping(target = "age", source = "age", qualifiedByName = "ageToInteger")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "genderToString")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "ageToInteger")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "ageToInteger")
    @Mapping(target = "isActive", source = "active")
    UserProfileDto domainToDto(UserProfileEntity entity);
    
    /**
     * DTO → Domain Entity
     */
    @Mapping(target = "userId", source = "id", qualifiedByName = "stringToUserId")
    @Mapping(target = "age", source = "age", qualifiedByName = "integerToAge")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "stringToGender")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "integerToAge")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "integerToAge")
    @Mapping(target = "active", source = "isActive")
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "lastActiveAt", ignore = true)
    UserProfileEntity dtoToDomain(UserProfileDto dto);
    
    /**
     * リスト変換
     */
    List<UserProfile> domainListToApiModelList(List<UserProfileEntity> entities);
    List<UserProfileEntity> apiModelListToDomainList(List<UserProfile> models);
    List<UserProfileDto> domainListToDtoList(List<UserProfileEntity> entities);
    List<UserProfileEntity> dtoListToDomainList(List<UserProfileDto> dtos);
    
    // Custom conversion methods
    @Named("userIdToString")
    default String userIdToString(UserId userId) {
        return userId != null ? userId.getValue() : null;
    }
    
    @Named("stringToUserId")
    default UserId stringToUserId(String id) {
        return id != null ? new UserId(id) : null;
    }
    
    @Named("ageToInteger")
    default Integer ageToInteger(Age age) {
        return age != null ? age.getValue() : null;
    }
    
    @Named("integerToAge")
    default Age integerToAge(Integer age) {
        return age != null ? new Age(age) : null;
    }
    
    @Named("genderToString")
    default String genderToString(Gender gender) {
        return gender != null ? gender.getValue() : null;
    }
    
    @Named("stringToGender")
    default Gender stringToGender(String genderStr) {
        return genderStr != null ? new Gender(genderStr) : null;
    }
    
    @Named("localDateTimeToDate")
    default Date localDateTimeToDate(LocalDateTime localDateTime) {
        return localDateTime != null ? Date.from(localDateTime.atZone(ZoneId.systemDefault()).toInstant()) : null;
    }
    
    @Named("dateToLocalDateTime")
    default LocalDateTime dateToLocalDateTime(Date date) {
        return date != null ? LocalDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault()) : null;
    }
}