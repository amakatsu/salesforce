package org.openapitools.domain.entity;

import lombok.Builder;
import lombok.Getter;
import org.openapitools.domain.valueobject.CreditId;
import org.openapitools.domain.valueobject.Money;
import org.openapitools.domain.valueobject.InterestRate;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;

@Getter
@Builder(toBuilder = true)
@lombok.Setter(lombok.AccessLevel.PACKAGE)
public class CreditDataEntity {
    
    private final CreditId creditId;
    private String label;
    private LocalDate dueDate;
    private InterestRate rate;
    private Money balance99;
    private Money principal;
    private Money changeAmount;
    private Money postBalance;
    private Money actualBalance;
    private Money correction;
    private String parentId;
    
    // Factory method
    public static CreditDataEntity create(CreditId creditId, String label) {
        Objects.requireNonNull(creditId, "CreditId cannot be null");
        Objects.requireNonNull(label, "Label cannot be null");
        
        return CreditDataEntity.builder()
                .creditId(creditId)
                .label(label)
                .build();
    }
    
    // Business methods that return new instances
    public CreditDataEntity updateBalance(Money newBalance) {
        if (newBalance != null) {
            Money change = newBalance.subtract(this.actualBalance != null ? this.actualBalance : new Money(null));
            return this.toBuilder()
                    .changeAmount(change)
                    .postBalance(newBalance)
                    .actualBalance(newBalance)
                    .build();
        }
        return this;
    }
    
    public CreditDataEntity applyCorrection(Money correctionAmount) {
        if (correctionAmount != null && this.actualBalance != null) {
            return this.toBuilder()
                    .correction(correctionAmount)
                    .actualBalance(this.actualBalance.add(correctionAmount))
                    .build();
        }
        return this.toBuilder().correction(correctionAmount).build();
    }
    
    public Money calculateInterestAmount() {
        if (rate != null && principal != null) {
            return rate.calculateInterest(principal);
        }
        return new Money(null);
    }
    
    public boolean isOverdue() {
        return dueDate != null && dueDate.isBefore(LocalDate.now());
    }
    
    public boolean isHighRisk() {
        return (rate != null && rate.isHighRate()) || 
               (actualBalance != null && actualBalance.isNegative());
    }
    
    public String formatDueDate() {
        if (dueDate == null) return null;
        return dueDate.format(DateTimeFormatter.ofPattern("MM/dd"));
    }
    
    public static LocalDate parseDueDate(String dueDateString) {
        if (dueDateString == null || dueDateString.trim().isEmpty()) {
            return null;
        }
        
        try {
            // Assuming format is "MM/dd"
            String[] parts = dueDateString.split("/");
            if (parts.length == 2) {
                int month = Integer.parseInt(parts[0]);
                int day = Integer.parseInt(parts[1]);
                int year = LocalDate.now().getYear(); // Use current year
                return LocalDate.of(year, month, day);
            }
        } catch (Exception e) {
            // Log error or handle invalid date format
        }
        
        return null;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CreditDataEntity that = (CreditDataEntity) o;
        return Objects.equals(creditId, that.creditId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(creditId);
    }
}