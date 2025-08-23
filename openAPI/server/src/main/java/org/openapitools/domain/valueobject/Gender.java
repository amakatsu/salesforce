package org.openapitools.domain.valueobject;

import java.util.Objects;

public class Gender {
    
    public enum GenderType {
        MALE("male"),
        FEMALE("female"), 
        OTHER("other");
        
        private final String value;
        
        GenderType(String value) {
            this.value = value;
        }
        
        public String getValue() {
            return value;
        }
        
        public static GenderType fromString(String value) {
            if (value == null) return null;
            for (GenderType type : GenderType.values()) {
                if (type.value.equalsIgnoreCase(value.trim())) {
                    return type;
                }
            }
            throw new IllegalArgumentException("Invalid gender value: " + value);
        }
    }
    
    private final GenderType type;
    
    public Gender(String value) {
        this.type = GenderType.fromString(value);
    }
    
    public Gender(GenderType type) {
        this.type = type;
    }
    
    public GenderType getType() {
        return type;
    }
    
    public String getValue() {
        return type != null ? type.getValue() : null;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Gender gender = (Gender) o;
        return type == gender.type;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(type);
    }
    
    @Override
    public String toString() {
        return type != null ? type.getValue() : "null";
    }
}