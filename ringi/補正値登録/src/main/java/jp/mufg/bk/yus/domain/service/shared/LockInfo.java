package jp.mufg.bk.yus.domain.service.shared;

/**
 * 楽観排他制御情報の不変値オブジェクト。
 * presentation / domain / infra 間で受け渡すための共有 POJO であり、
 * バリデーションは presentation 層（Request クラス）で実施する責務分担とする。
 */
public final class LockInfo {

    private final String exclusiveKey;
    private final int exclusiveCount;

    public LockInfo(String exclusiveKey, int exclusiveCount) {
        this.exclusiveKey = exclusiveKey;
        this.exclusiveCount = exclusiveCount;
    }

    public String getExclusiveKey() {
        return exclusiveKey;
    }

    public int getExclusiveCount() {
        return exclusiveCount;
    }
}
