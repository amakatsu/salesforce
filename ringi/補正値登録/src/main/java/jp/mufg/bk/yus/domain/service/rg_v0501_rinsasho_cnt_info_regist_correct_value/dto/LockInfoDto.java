package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto;

/**
 * 排他ロック情報 DTO（ドメイン層）。presentation 層の LockInfo Model とは別物。
 */
public class LockInfoDto {

    private String exclusiveKey;
    private Integer exclusiveCount;

    public LockInfoDto() {
    }

    public LockInfoDto(String exclusiveKey, Integer exclusiveCount) {
        this.exclusiveKey = exclusiveKey;
        this.exclusiveCount = exclusiveCount;
    }

    public String getExclusiveKey() {
        return exclusiveKey;
    }

    public void setExclusiveKey(String exclusiveKey) {
        this.exclusiveKey = exclusiveKey;
    }

    public Integer getExclusiveCount() {
        return exclusiveCount;
    }

    public void setExclusiveCount(Integer exclusiveCount) {
        this.exclusiveCount = exclusiveCount;
    }
}
