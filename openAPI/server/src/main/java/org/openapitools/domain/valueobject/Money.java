package org.openapitools.domain.valueobject;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

public class Money {
    
    private final BigDecimal amount;
    private final String currency;
    
    public Money(BigDecimal amount, String currency) {
        if (amount == null) {
            this.amount = null;
        } else {
            this.amount = amount.setScale(2, RoundingMode.HALF_UP);
        }
        this.currency = currency != null ? currency : "JPY";
    }
    
    public Money(BigDecimal amount) {
        this(amount, "JPY");
    }
    
    public BigDecimal getAmount() {
        return amount;
    }
    
    public String getCurrency() {
        return currency;
    }
    
    public Money add(Money other) {
        if (amount == null || other.amount == null) return new Money(null, currency);
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(amount.add(other.amount), currency);
    }
    
    public Money subtract(Money other) {
        if (amount == null || other.amount == null) return new Money(null, currency);
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot subtract different currencies");
        }
        return new Money(amount.subtract(other.amount), currency);
    }
    
    public Money multiply(BigDecimal multiplier) {
        if (amount == null || multiplier == null) return new Money(null, currency);
        return new Money(amount.multiply(multiplier), currency);
    }
    
    public boolean isPositive() {
        return amount != null && amount.compareTo(BigDecimal.ZERO) > 0;
    }
    
    public boolean isNegative() {
        return amount != null && amount.compareTo(BigDecimal.ZERO) < 0;
    }
    
    public boolean isZero() {
        return amount != null && amount.compareTo(BigDecimal.ZERO) == 0;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Money money = (Money) o;
        return Objects.equals(amount, money.amount) && Objects.equals(currency, money.currency);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
    
    @Override
    public String toString() {
        return amount != null ? amount.toString() + " " + currency : "null " + currency;
    }
}