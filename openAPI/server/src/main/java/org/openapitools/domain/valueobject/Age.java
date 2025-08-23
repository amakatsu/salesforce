package org.openapitools.domain.valueobject;

import java.util.Objects;

public class Age {
    
    private final Integer value;
    
    public Age(Integer value) {
        if (value != null && (value < 0 || value > 150)) {
            throw new IllegalArgumentException("Age must be between 0 and 150");
        }
        this.value = value;
    }
    
    public Integer getValue() {
        return value;
    }
    
    public boolean isAdult() {
        return value != null && value >= 18;
    }
    
    public boolean isInRange(Age min, Age max) {
        if (value == null) return false;
        if (min != null && min.value != null && value < min.value) return false;
        if (max != null && max.value != null && value > max.value) return false;
        return true;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Age age = (Age) o;
        return Objects.equals(value, age.value);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
    
    @Override
    public String toString() {
        return value != null ? value.toString() : "null";
    }
}