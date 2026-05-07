package jp.mufg.bk.yus.domain.service.rg_v0501_rinsasho_cnt_info_regist_correct_value.dto;

/**
 * 補正値登録機能のサービス出力 DTO。本機能では更新後の排他ロック情報のみを返却する。
 */
public class ServiceOutputDto {

    private LockInfoDto lockInfo;

    public LockInfoDto getLockInfo() {
        return lockInfo;
    }

    public void setLockInfo(LockInfoDto lockInfo) {
        this.lockInfo = lockInfo;
    }
}
