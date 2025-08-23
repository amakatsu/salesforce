package org.openapitools.domain.entity;

import org.openapitools.domain.valueobject.CreditId;
import org.openapitools.domain.valueobject.Money;
import org.openapitools.domain.valueobject.InterestRate;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;

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
    
    public CreditDataEntity(CreditId creditId, String label) {
        this.creditId = Objects.requireNonNull(creditId, "CreditId cannot be null");
        this.label = Objects.requireNonNull(label, "Label cannot be null");
    }
    
    public CreditDataEntity(CreditId creditId, String label, String dueDateString, 
                           String rateString, Money balance99, Money principal,
                           Money changeAmount, Money postBalance, Money actualBalance,
                           Money correction, String parentId) {
        this.creditId = Objects.requireNonNull(creditId, "CreditId cannot be null");
        this.label = label;
        this.dueDate = parseDueDate(dueDateString);
        this.rate = new InterestRate(rateString);
        this.balance99 = balance99;
        this.principal = principal;
        this.changeAmount = changeAmount;
        this.postBalance = postBalance;
        this.actualBalance = actualBalance;
        this.correction = correction;
        this.parentId = parentId;
    }
    
    // Business methods
    public void updateBalance(Money newBalance) {
        if (newBalance != null) {
            this.changeAmount = newBalance.subtract(this.actualBalance != null ? this.actualBalance : new Money(null));
            this.postBalance = newBalance;
            this.actualBalance = newBalance;
        }
    }
    
    public void applyCorrection(Money correctionAmount) {
        this.correction = correctionAmount;
        if (this.actualBalance != null && correctionAmount != null) {
            this.actualBalance = this.actualBalance.add(correctionAmount);
        }
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
    
    private LocalDate parseDueDate(String dueDateString) {
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
    
    // Getters
    public CreditId getCreditId() { return creditId; }
    public String getLabel() { return label; }
    public LocalDate getDueDate() { return dueDate; }
    public InterestRate getRate() { return rate; }
    public Money getBalance99() { return balance99; }
    public Money getPrincipal() { return principal; }
    public Money getChangeAmount() { return changeAmount; }
    public Money getPostBalance() { return postBalance; }
    public Money getActualBalance() { return actualBalance; }
    public Money getCorrection() { return correction; }
    public String getParentId() { return parentId; }
    
    // Setters for updates
    public void setLabel(String label) { 
        this.label = label; 
    }
    
    public void setDueDate(String dueDateString) { 
        this.dueDate = parseDueDate(dueDateString); 
    }
    
    public void setRate(String rateString) { 
        this.rate = new InterestRate(rateString); 
    }
    
    public void setBalance99(Money balance99) { 
        this.balance99 = balance99; 
    }
    
    public void setPrincipal(Money principal) { 
        this.principal = principal; 
    }
    
    public void setParentId(String parentId) { 
        this.parentId = parentId; 
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