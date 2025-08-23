package org.openapitools.infrastructure.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.openapitools.domain.entity.UserProfileEntity;
import org.openapitools.domain.valueobject.UserId;
import org.openapitools.domain.valueobject.Age;
import org.openapitools.domain.valueobject.Gender;
import org.openapitools.infrastructure.dto.UserProfileDataModel;

import java.util.List;

/**
 * インフラストラクチャ層専用のMapper
 * ドメインエンティティ ↔ データベースDTO間の変換
 * APIモデルに依存しない
 */
@Mapper(componentModel = "spring")
public interface UserProfileInfrastructureMapper {
    
    /**
     * Domain Entity → Database DTO
     */
    @Mapping(target = "id", source = "userId", qualifiedByName = "userIdToString")
    @Mapping(target = "age", source = "age", qualifiedByName = "ageToInteger")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "genderToString")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "ageToInteger")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "ageToInteger")
    @Mapping(target = "isActive", source = "active")
    @Mapping(target = "createdDate", source = "createdAt")
    @Mapping(target = "lastActive", source = "lastActiveAt")
    UserProfileDataModel domainToDataModel(UserProfileEntity entity);
    
    /**
     * Database DTO → Domain Entity
     */
    @Mapping(target = "userId", source = "id", qualifiedByName = "stringToUserId")
    @Mapping(target = "age", source = "age", qualifiedByName = "integerToAge")
    @Mapping(target = "gender", source = "gender", qualifiedByName = "stringToGender")
    @Mapping(target = "ageRangeMin", source = "ageRangeMin", qualifiedByName = "integerToAge")
    @Mapping(target = "ageRangeMax", source = "ageRangeMax", qualifiedByName = "integerToAge")
    @Mapping(target = "isActive", source = "isActive")
    @Mapping(target = "createdAt", source = "createdDate")
    @Mapping(target = "lastActiveAt", source = "lastActive")
    UserProfileEntity dataModelToDomain(UserProfileDataModel dataModel);
    
    /**
     * リスト変換
     */
    List<UserProfileDataModel> domainListToDataModelList(List<UserProfileEntity> entities);
    List<UserProfileEntity> dataModelListToDomainList(List<UserProfileDataModel> dataModels);
    
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
}