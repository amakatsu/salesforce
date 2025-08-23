package org.openapitools.domain.valueobject;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

public class InterestRate {
    
    private final BigDecimal rate;
    
    public InterestRate(String rateString) {
        if (rateString == null || rateString.trim().isEmpty()) {
            this.rate = null;
        } else {
            try {
                BigDecimal parsedRate = new BigDecimal(rateString.trim());
                if (parsedRate.compareTo(BigDecimal.ZERO) < 0) {
                    throw new IllegalArgumentException("Interest rate cannot be negative");
                }
                if (parsedRate.compareTo(new BigDecimal("100")) > 0) {
                    throw new IllegalArgumentException("Interest rate cannot exceed 100%");
                }
                this.rate = parsedRate.setScale(2, RoundingMode.HALF_UP);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid interest rate format: " + rateString);
            }
        }
    }
    
    public InterestRate(BigDecimal rate) {
        if (rate == null) {
            this.rate = null;
        } else {
            if (rate.compareTo(BigDecimal.ZERO) < 0) {
                throw new IllegalArgumentException("Interest rate cannot be negative");
            }
            if (rate.compareTo(new BigDecimal("100")) > 0) {
                throw new IllegalArgumentException("Interest rate cannot exceed 100%");
            }
            this.rate = rate.setScale(2, RoundingMode.HALF_UP);
        }
    }
    
    public BigDecimal getRate() {
        return rate;
    }
    
    public String getRateAsString() {
        return rate != null ? rate.toString() : null;
    }
    
    public Money calculateInterest(Money principal) {
        if (rate == null || principal == null || principal.getAmount() == null) {
            return new Money(null);
        }
        
        BigDecimal interestAmount = principal.getAmount()
            .multiply(rate)
            .divide(new BigDecimal("100"), RoundingMode.HALF_UP);
        
        return new Money(interestAmount, principal.getCurrency());
    }
    
    public boolean isHighRate() {
        return rate != null && rate.compareTo(new BigDecimal("10")) > 0;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        InterestRate that = (InterestRate) o;
        return Objects.equals(rate, that.rate);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(rate);
    }
    
    @Override
    public String toString() {
        return rate != null ? rate.toString() + "%" : "null";
    }
}