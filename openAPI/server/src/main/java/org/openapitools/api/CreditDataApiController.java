package org.openapitools.api;

import org.openapitools.model.CreditData;
import org.openapitools.service.CreditDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // CORS設定
public class CreditDataApiController {
    
    @Autowired
    private CreditDataService creditDataService;
    
    // 与信データ一覧取得
    @GetMapping("/credit-data")
    public ResponseEntity<List<CreditData>> getAllCreditData() {
        try {
            List<CreditData> creditDataList = creditDataService.getAllCreditData();
            return ResponseEntity.ok(creditDataList);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 与信データ取得（ID指定）
    @GetMapping("/credit-data/{id}")
    public ResponseEntity<CreditData> getCreditDataById(@PathVariable String id) {
        try {
            Optional<CreditData> creditData = creditDataService.getCreditDataById(id);
            if (creditData.isPresent()) {
                return ResponseEntity.ok(creditData.get());
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 与信データ作成
    @PostMapping("/credit-data")
    public ResponseEntity<CreditData> createCreditData(@RequestBody CreditData creditData) {
        try {
            CreditData createdData = creditDataService.createCreditData(creditData);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdData);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 与信データ更新
    @PutMapping("/credit-data/{id}")
    public ResponseEntity<CreditData> updateCreditData(@PathVariable String id, @RequestBody CreditData creditData) {
        try {
            CreditData updatedData = creditDataService.updateCreditData(id, creditData);
            return ResponseEntity.ok(updatedData);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 与信データ一括更新
    @PutMapping("/credit-data")
    public ResponseEntity<List<CreditData>> updateAllCreditData(@RequestBody List<CreditData> creditDataList) {
        try {
            List<CreditData> updatedDataList = creditDataService.updateAllCreditData(creditDataList);
            return ResponseEntity.ok(updatedDataList);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 与信データ削除
    @DeleteMapping("/credit-data/{id}")
    public ResponseEntity<Void> deleteCreditData(@PathVariable String id) {
        try {
            creditDataService.deleteCreditData(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}