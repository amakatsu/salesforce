package org.openapitools.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;
import org.openapitools.dto.CreditDataDto;
import org.openapitools.model.CreditData;

import java.util.List;

@Mapper(componentModel = "spring")
public interface CreditDataEntityMapper {
    
    CreditDataEntityMapper INSTANCE = Mappers.getMapper(CreditDataEntityMapper.class);
    
    /**
     * EntityからDTOへの変換
     */
    CreditDataDto entityToDto(CreditData creditData);
    
    /**
     * DTOからEntityへの変換
     */
    CreditData dtoToEntity(CreditDataDto creditDataDto);
    
    /**
     * リストの変換（EntityからDTO）
     */
    List<CreditDataDto> entitiesToDtos(List<CreditData> creditDataList);
    
    /**
     * リストの変換（DTOからEntity）
     */
    List<CreditData> dtosToEntities(List<CreditDataDto> creditDataDtos);
    
    /**
     * 既存Entityの更新（DTOから）
     */
    @Mapping(target = "id", ignore = true)
    void updateEntityFromDto(CreditDataDto dto, @MappingTarget CreditData entity);
}