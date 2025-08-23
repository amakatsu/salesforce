package org.openapitools.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;
import org.openapitools.dto.UserProfileDto;
import org.openapitools.model.UserProfile;

import java.util.List;

@Mapper(componentModel = "spring")
public interface UserProfileEntityMapper {
    
    UserProfileEntityMapper INSTANCE = Mappers.getMapper(UserProfileEntityMapper.class);
    
    /**
     * EntityからDTOへの変換
     */
    @Mapping(target = "isActive", source = "isActive")
    UserProfileDto entityToDto(UserProfile userProfile);
    
    /**
     * DTOからEntityへの変換
     */
    @Mapping(target = "createdDate", ignore = true)
    @Mapping(target = "lastActive", ignore = true)
    UserProfile dtoToEntity(UserProfileDto userProfileDto);
    
    /**
     * リストの変換（EntityからDTO）
     */
    List<UserProfileDto> entitiesToDtos(List<UserProfile> userProfiles);
    
    /**
     * リストの変換（DTOからEntity）
     */
    List<UserProfile> dtosToEntities(List<UserProfileDto> userProfileDtos);
    
    /**
     * 既存Entityの更新（DTOから）
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdDate", ignore = true)
    @Mapping(target = "lastActive", ignore = true)
    void updateEntityFromDto(UserProfileDto dto, @MappingTarget UserProfile entity);
}