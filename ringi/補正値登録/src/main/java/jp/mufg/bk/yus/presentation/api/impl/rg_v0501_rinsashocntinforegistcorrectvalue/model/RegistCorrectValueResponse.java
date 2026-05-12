package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsashocntinforegistcorrectvalue.model;

import jp.mufg.bk.yus.domain.service.shared.LockInfo;

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
