package org.openapitools.presentation.dto;

import java.math.BigDecimal;

public class CreditDataDto {
    
    private String id;
    private String label;
    private String dueDate;
    private String rate;
    private BigDecimal balance99;
    private BigDecimal principal;
    private BigDecimal change;
    private BigDecimal postBalance;
    private BigDecimal actualBalance;
    private BigDecimal correction;
    private String parentId;
    
    // デフォルトコンストラクタ
    public CreditDataDto() {}
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }
    
    public String getDueDate() { return dueDate; }
    public void setDueDate(String dueDate) { this.dueDate = dueDate; }
    
    public String getRate() { return rate; }
    public void setRate(String rate) { this.rate = rate; }
    
    public BigDecimal getBalance99() { return balance99; }
    public void setBalance99(BigDecimal balance99) { this.balance99 = balance99; }
    
    public BigDecimal getPrincipal() { return principal; }
    public void setPrincipal(BigDecimal principal) { this.principal = principal; }
    
    public BigDecimal getChange() { return change; }
    public void setChange(BigDecimal change) { this.change = change; }
    
    public BigDecimal getPostBalance() { return postBalance; }
    public void setPostBalance(BigDecimal postBalance) { this.postBalance = postBalance; }
    
    public BigDecimal getActualBalance() { return actualBalance; }
    public void setActualBalance(BigDecimal actualBalance) { this.actualBalance = actualBalance; }
    
    public BigDecimal getCorrection() { return correction; }
    public void setCorrection(BigDecimal correction) { this.correction = correction; }
    
    public String getParentId() { return parentId; }
    public void setParentId(String parentId) { this.parentId = parentId; }
}