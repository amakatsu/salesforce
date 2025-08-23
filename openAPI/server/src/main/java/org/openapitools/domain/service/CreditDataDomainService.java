package org.openapitools.domain.service;

import org.openapitools.domain.entity.CreditDataEntity;
import org.openapitools.domain.valueobject.Money;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

public class CreditDataDomainService {
    
    /**
     * 与信データの総額を計算
     */
    public Money calculateTotalBalance(List<CreditDataEntity> creditDataList) {
        BigDecimal total = creditDataList.stream()
            .map(CreditDataEntity::getActualBalance)
            .filter(balance -> balance != null && balance.getAmount() != null)
            .map(Money::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        return new Money(total);
    }
    
    /**
     * リスクレベルを評価
     */
    public CreditRiskLevel evaluateRiskLevel(CreditDataEntity creditData) {
        if (!creditData.isHighRisk()) {
            return CreditRiskLevel.LOW;
        }
        
        boolean isOverdue = creditData.isOverdue();
        boolean hasNegativeBalance = creditData.getActualBalance() != null && 
                                   creditData.getActualBalance().isNegative();
        boolean isHighRate = creditData.getRate() != null && 
                           creditData.getRate().isHighRate();
        
        int riskFactors = 0;
        if (isOverdue) riskFactors++;
        if (hasNegativeBalance) riskFactors++;
        if (isHighRate) riskFactors++;
        
        switch (riskFactors) {
            case 0:
                return CreditRiskLevel.LOW;
            case 1:
                return CreditRiskLevel.MEDIUM;
            case 2:
                return CreditRiskLevel.HIGH;
            default:
                return CreditRiskLevel.CRITICAL;
        }
    }
    
    /**
     * 期限切れの与信データを取得
     */
    public List<CreditDataEntity> findOverdueCredits(List<CreditDataEntity> creditDataList) {
        return creditDataList.stream()
            .filter(CreditDataEntity::isOverdue)
            .collect(Collectors.toList());
    }
    
    /**
     * 高リスクの与信データを取得
     */
    public List<CreditDataEntity> findHighRiskCredits(List<CreditDataEntity> creditDataList) {
        return creditDataList.stream()
            .filter(CreditDataEntity::isHighRisk)
            .collect(Collectors.toList());
    }
    
    /**
     * 与信データの健全性スコアを計算（0-100）
     */
    public int calculateHealthScore(CreditDataEntity creditData) {
        int score = 100;
        
        // 期限切れによる減点
        if (creditData.isOverdue()) {
            long daysOverdue = java.time.temporal.ChronoUnit.DAYS.between(
                creditData.getDueDate(), LocalDate.now());
            score -= Math.min(30, (int)(daysOverdue * 2));
        }
        
        // 負の残高による減点
        if (creditData.getActualBalance() != null && creditData.getActualBalance().isNegative()) {
            score -= 25;
        }
        
        // 高金利による減点
        if (creditData.getRate() != null && creditData.getRate().isHighRate()) {
            score -= 15;
        }
        
        // 修正額が大きい場合の減点
        if (creditData.getCorrection() != null && 
            creditData.getCorrection().getAmount() != null &&
            creditData.getPrincipal() != null &&
            creditData.getPrincipal().getAmount() != null) {
            
            BigDecimal correctionRatio = creditData.getCorrection().getAmount()
                .abs()
                .divide(creditData.getPrincipal().getAmount(), 2, java.math.RoundingMode.HALF_UP);
            
            if (correctionRatio.compareTo(new BigDecimal("0.1")) > 0) {
                score -= 20;
            }
        }
        
        return Math.max(0, score);
    }
    
    /**
     * 親子関係のある与信データをグループ化
     */
    public List<CreditDataGroup> groupByParent(List<CreditDataEntity> creditDataList) {
        return creditDataList.stream()
            .filter(credit -> credit.getParentId() == null)
            .map(parent -> {
                List<CreditDataEntity> children = creditDataList.stream()
                    .filter(credit -> parent.getCreditId().getValue().equals(credit.getParentId()))
                    .collect(Collectors.toList());
                
                return new CreditDataGroup(parent, children);
            })
            .collect(Collectors.toList());
    }
    
    public enum CreditRiskLevel {
        LOW("低リスク", "#4CAF50"),
        MEDIUM("中リスク", "#FF9800"),
        HIGH("高リスク", "#FF5722"),
        CRITICAL("危険", "#F44336");
        
        private final String displayName;
        private final String colorCode;
        
        CreditRiskLevel(String displayName, String colorCode) {
            this.displayName = displayName;
            this.colorCode = colorCode;
        }
        
        public String getDisplayName() {
            return displayName;
        }
        
        public String getColorCode() {
            return colorCode;
        }
    }
    
    public static class CreditDataGroup {
        private final CreditDataEntity parent;
        private final List<CreditDataEntity> children;
        
        public CreditDataGroup(CreditDataEntity parent, List<CreditDataEntity> children) {
            this.parent = parent;
            this.children = children;
        }
        
        public CreditDataEntity getParent() {
            return parent;
        }
        
        public List<CreditDataEntity> getChildren() {
            return children;
        }
        
        public Money getTotalBalance() {
            BigDecimal parentBalance = parent.getActualBalance() != null ? 
                parent.getActualBalance().getAmount() : BigDecimal.ZERO;
            
            BigDecimal childrenTotal = children.stream()
                .map(CreditDataEntity::getActualBalance)
                .filter(balance -> balance != null && balance.getAmount() != null)
                .map(Money::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            
            return new Money(parentBalance.add(childrenTotal));
        }
    }
}