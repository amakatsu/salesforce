package jp.co.btm.irl.rlr.rg004.dto;

import java.util.Date;

/**
 * サービスインプットDTO
 * <p>計数情報マスタ再登録サービスの入力パラメータを保持する。イミュータブル。</p>
 */
public class ServiceInputDto {

    /** 案件番号 // 旧: F_LC_NO */
    private final String ankenNo;

    /** 店番 // 旧: F_BRNO */
    private final String branchNo;

    /** 取引先番号 // 旧: F_TRISKNO */
    private final String customerNo;

    /** 取引先貸外店番 */
    private final String lendingBranchNo;

    /** 取引日 // 旧: F_TRIBI */
    private final Date tradingDate;

    /** 禀査番号 // 旧: F_RSNO */
    private final String assessmentNo;

    /** 排他ロック情報 - 排他キー */
    private final String lockKey;

    /** 排他ロック情報 - 更新回数 */
    private final int updateCount;

    public ServiceInputDto(String ankenNo, String branchNo, String customerNo,
                           String lendingBranchNo, Date tradingDate,
                           String assessmentNo, String lockKey, int updateCount) {
        this.ankenNo = ankenNo;
        this.branchNo = branchNo;
        this.customerNo = customerNo;
        this.lendingBranchNo = lendingBranchNo;
        this.tradingDate = tradingDate;
        this.assessmentNo = assessmentNo;
        this.lockKey = lockKey;
        this.updateCount = updateCount;
    }

    public String getAnkenNo() { return ankenNo; }
    public String getBranchNo() { return branchNo; }
    public String getCustomerNo() { return customerNo; }
    public String getLendingBranchNo() { return lendingBranchNo; }
    public Date getTradingDate() { return tradingDate; }
    public String getAssessmentNo() { return assessmentNo; }
    public String getLockKey() { return lockKey; }
    public int getUpdateCount() { return updateCount; }
}
