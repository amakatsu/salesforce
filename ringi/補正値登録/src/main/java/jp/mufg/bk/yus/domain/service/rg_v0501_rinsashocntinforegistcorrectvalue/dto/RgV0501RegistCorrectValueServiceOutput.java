package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.dto;

import jp.mufg.bk.yus.domain.service.shared.LockInfo;

/**
 * 補正値登録機能のサービス出力 DTO。本機能では更新後の排他ロック情報のみを返却する。
 */
public class RgV0501RegistCorrectValueServiceOutput {

    private LockInfo lockInfo;

    public LockInfo getLockInfo() {
        return lockInfo;
    }

    public void setLockInfo(LockInfo lockInfo) {
        this.lockInfo = lockInfo;
    }
}
