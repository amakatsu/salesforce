package org.openapitools.presentation.api;

import org.openapitools.model.CreditData;
import org.openapitools.application.service.CreditDataService;
import org.openapitools.domain.entity.CreditDataEntity;
import org.openapitools.domain.service.CreditDataDomainService;
import org.openapitools.domain.valueobject.Money;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/credit-data")
@CrossOrigin(origins = "*")
public class CreditDataController {
    
    @Autowired
    private CreditDataService creditDataService;
    
    // 全与信データ取得
    @GetMapping
    public ResponseEntity<List<CreditData>> getAllCreditData() {
        try {
            List<CreditData> creditDataList = creditDataService.getAllCreditData();
            return ResponseEntity.ok(creditDataList);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 特定与信データ取得
    @GetMapping("/{id}")
    public ResponseEntity<CreditData> getCreditDataById(@PathVariable String id) {
        try {
            return creditDataService.getCreditDataById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 新規与信データ作成
    @PostMapping
    public ResponseEntity<CreditData> createCreditData(@RequestBody CreditData creditData) {
        try {
            CreditData created = creditDataService.createCreditData(creditData);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 与信データ更新
    @PutMapping("/{id}")
    public ResponseEntity<CreditData> updateCreditData(@PathVariable String id, 
                                                      @RequestBody CreditData creditData) {
        try {
            CreditData updated = creditDataService.updateCreditData(id, creditData);
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 与信データ削除
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCreditData(@PathVariable String id) {
        try {
            creditDataService.deleteCreditData(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 一括更新
    @PutMapping
    public ResponseEntity<List<CreditData>> updateAllCreditData(@RequestBody List<CreditData> creditDataList) {
        try {
            List<CreditData> updated = creditDataService.updateAllCreditData(creditDataList);
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // ドメインサービス機能のAPI
    
    // 総額取得
    @GetMapping("/total-balance")
    public ResponseEntity<Map<String, Object>> getTotalBalance() {
        try {
            Money totalBalance = creditDataService.getTotalBalance();
            Map<String, Object> response = new HashMap<>();
            response.put("totalBalance", totalBalance.getAmount());
            response.put("currency", totalBalance.getCurrency());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 高リスク与信データ取得
    @GetMapping("/high-risk")
    public ResponseEntity<List<String>> getHighRiskCredits() {
        try {
            List<CreditDataEntity> highRiskCredits = creditDataService.getHighRiskCredits();
            List<String> ids = highRiskCredits.stream()
                .map(entity -> entity.getCreditId().getValue())
                .toList();
            return ResponseEntity.ok(ids);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 期限切れ与信データ取得
    @GetMapping("/overdue")
    public ResponseEntity<List<String>> getOverdueCredits() {
        try {
            List<CreditDataEntity> overdueCredits = creditDataService.getOverdueCredits();
            List<String> ids = overdueCredits.stream()
                .map(entity -> entity.getCreditId().getValue())
                .toList();
            return ResponseEntity.ok(ids);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // リスクレベル評価
    @GetMapping("/{id}/risk-level")
    public ResponseEntity<Map<String, Object>> evaluateRiskLevel(@PathVariable String id) {
        try {
            CreditDataDomainService.CreditRiskLevel riskLevel = creditDataService.evaluateRiskLevel(id);
            Map<String, Object> response = new HashMap<>();
            response.put("riskLevel", riskLevel.name());
            response.put("displayName", riskLevel.getDisplayName());
            response.put("colorCode", riskLevel.getColorCode());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 健全性スコア計算
    @GetMapping("/{id}/health-score")
    public ResponseEntity<Map<String, Object>> calculateHealthScore(@PathVariable String id) {
        try {
            int healthScore = creditDataService.calculateHealthScore(id);
            Map<String, Object> response = new HashMap<>();
            response.put("healthScore", healthScore);
            response.put("status", healthScore >= 80 ? "良好" : 
                                 healthScore >= 60 ? "普通" :
                                 healthScore >= 40 ? "注意" : "危険");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}