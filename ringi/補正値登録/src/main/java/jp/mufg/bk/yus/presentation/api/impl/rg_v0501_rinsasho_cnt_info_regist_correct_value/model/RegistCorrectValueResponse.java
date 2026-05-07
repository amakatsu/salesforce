package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model;

/** 計数情報 補正値登録 API のレスポンス Body。 */
public class RegistCorrectValueResponse {

    private LockInfo lockInfo;

    public LockInfo getLockInfo() {
        return lockInfo;
    }

    public void setLockInfo(LockInfo lockInfo) {
        this.lockInfo = lockInfo;
    }
}
