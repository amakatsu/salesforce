package org.openapitools.application.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;
import org.openapitools.presentation.dto.CreditDataDto;
import org.openapitools.model.CreditData;
import org.openapitools.domain.entity.CreditDataEntity;
import org.openapitools.domain.valueobject.CreditId;
import org.openapitools.domain.valueobject.Money;
import org.openapitools.domain.valueobject.InterestRate;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Mapper(componentModel = "spring")
public interface CreditDataDomainMapper {
    
    CreditDataDomainMapper INSTANCE = Mappers.getMapper(CreditDataDomainMapper.class);
    
    /**
     * Domain Entity → API Model
     */
    @Mapping(target = "id", source = "creditId", qualifiedByName = "creditIdToString")
    @Mapping(target = "dueDate", source = "dueDate", qualifiedByName = "localDateToString")
    @Mapping(target = "rate", source = "rate", qualifiedByName = "interestRateToString")
    @Mapping(target = "balance99", source = "balance99", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "principal", source = "principal", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "change", source = "changeAmount", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "postBalance", source = "postBalance", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "actualBalance", source = "actualBalance", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "correction", source = "correction", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "editableFields", ignore = true)
    CreditData domainToApiModel(CreditDataEntity entity);
    
    /**
     * API Model → Domain Entity
     */
    @Mapping(target = "creditId", source = "id", qualifiedByName = "stringToCreditId")
    @Mapping(target = "dueDate", source = "dueDate", qualifiedByName = "stringToLocalDate")
    @Mapping(target = "rate", source = "rate", qualifiedByName = "stringToInterestRate")
    @Mapping(target = "balance99", source = "balance99", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "principal", source = "principal", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "changeAmount", source = "change", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "postBalance", source = "postBalance", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "actualBalance", source = "actualBalance", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "correction", source = "correction", qualifiedByName = "bigDecimalToMoney")
    CreditDataEntity apiModelToDomain(CreditData model);
    
    /**
     * Domain Entity → DTO
     */
    @Mapping(target = "id", source = "creditId", qualifiedByName = "creditIdToString")
    @Mapping(target = "dueDate", source = "dueDate", qualifiedByName = "localDateToString")
    @Mapping(target = "rate", source = "rate", qualifiedByName = "interestRateToString")
    @Mapping(target = "balance99", source = "balance99", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "principal", source = "principal", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "change", source = "changeAmount", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "postBalance", source = "postBalance", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "actualBalance", source = "actualBalance", qualifiedByName = "moneyToBigDecimal")
    @Mapping(target = "correction", source = "correction", qualifiedByName = "moneyToBigDecimal")
    CreditDataDto domainToDto(CreditDataEntity entity);
    
    /**
     * DTO → Domain Entity
     */
    @Mapping(target = "creditId", source = "id", qualifiedByName = "stringToCreditId")
    @Mapping(target = "dueDate", source = "dueDate", qualifiedByName = "stringToLocalDate")
    @Mapping(target = "rate", source = "rate", qualifiedByName = "stringToInterestRate")
    @Mapping(target = "balance99", source = "balance99", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "principal", source = "principal", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "changeAmount", source = "change", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "postBalance", source = "postBalance", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "actualBalance", source = "actualBalance", qualifiedByName = "bigDecimalToMoney")
    @Mapping(target = "correction", source = "correction", qualifiedByName = "bigDecimalToMoney")
    CreditDataEntity dtoToDomain(CreditDataDto dto);
    
    /**
     * リスト変換
     */
    List<CreditData> domainListToApiModelList(List<CreditDataEntity> entities);
    List<CreditDataEntity> apiModelListToDomainList(List<CreditData> models);
    List<CreditDataDto> domainListToDtoList(List<CreditDataEntity> entities);
    List<CreditDataEntity> dtoListToDomainList(List<CreditDataDto> dtos);
    
    // Custom conversion methods
    @Named("creditIdToString")
    default String creditIdToString(CreditId creditId) {
        return creditId != null ? creditId.getValue() : null;
    }
    
    @Named("stringToCreditId")
    default CreditId stringToCreditId(String id) {
        return id != null ? new CreditId(id) : null;
    }
    
    @Named("localDateToString")
    default String localDateToString(LocalDate date) {
        return date != null ? date.format(DateTimeFormatter.ofPattern("MM/dd")) : null;
    }
    
    @Named("stringToLocalDate")
    default LocalDate stringToLocalDate(String dateStr) {
        if (dateStr == null || dateStr.trim().isEmpty()) return null;
        try {
            String[] parts = dateStr.split("/");
            if (parts.length == 2) {
                int month = Integer.parseInt(parts[0]);
                int day = Integer.parseInt(parts[1]);
                int year = LocalDate.now().getYear();
                return LocalDate.of(year, month, day);
            }
        } catch (Exception e) {
            // Log error
        }
        return null;
    }
    
    @Named("interestRateToString")
    default String interestRateToString(InterestRate rate) {
        return rate != null ? rate.getRateAsString() : null;
    }
    
    @Named("stringToInterestRate")
    default InterestRate stringToInterestRate(String rateStr) {
        return rateStr != null ? new InterestRate(rateStr) : null;
    }
    
    @Named("moneyToBigDecimal")
    default BigDecimal moneyToBigDecimal(Money money) {
        return money != null ? money.getAmount() : null;
    }
    
    @Named("bigDecimalToMoney")
    default Money bigDecimalToMoney(BigDecimal amount) {
        return new Money(amount);
    }
}