package org.openapitools.api;

import org.openapitools.model.CollateralData;
import org.openapitools.service.CollateralDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // CORS設定
public class CollateralDataApiController {
    
    @Autowired
    private CollateralDataService collateralDataService;
    
    // 担保データ一覧取得
    @GetMapping("/collateral-data")
    public ResponseEntity<List<CollateralData>> getAllCollateralData() {
        try {
            List<CollateralData> collateralDataList = collateralDataService.getAllCollateralData();
            return ResponseEntity.ok(collateralDataList);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 担保データ取得（ID指定）
    @GetMapping("/collateral-data/{id}")
    public ResponseEntity<CollateralData> getCollateralDataById(@PathVariable String id) {
        try {
            Optional<CollateralData> collateralData = collateralDataService.getCollateralDataById(id);
            if (collateralData.isPresent()) {
                return ResponseEntity.ok(collateralData.get());
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    // 担保データ作成
    @PostMapping("/collateral-data")
    public ResponseEntity<CollateralData> createCollateralData(@RequestBody CollateralData collateralData) {
        try {
            CollateralData createdData = collateralDataService.createCollateralData(collateralData);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdData);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 担保データ更新
    @PutMapping("/collateral-data/{id}")
    public ResponseEntity<CollateralData> updateCollateralData(@PathVariable String id, @RequestBody CollateralData collateralData) {
        try {
            CollateralData updatedData = collateralDataService.updateCollateralData(id, collateralData);
            return ResponseEntity.ok(updatedData);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 担保データ一括更新
    @PutMapping("/collateral-data")
    public ResponseEntity<List<CollateralData>> updateAllCollateralData(@RequestBody List<CollateralData> collateralDataList) {
        try {
            List<CollateralData> updatedDataList = collateralDataService.updateAllCollateralData(collateralDataList);
            return ResponseEntity.ok(updatedDataList);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }
    
    // 担保データ削除
    @DeleteMapping("/collateral-data/{id}")
    public ResponseEntity<Void> deleteCollateralData(@PathVariable String id) {
        try {
            collateralDataService.deleteCollateralData(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}