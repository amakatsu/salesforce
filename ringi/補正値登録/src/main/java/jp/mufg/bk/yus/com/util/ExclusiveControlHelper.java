package jp.mufg.bk.yus.com.util;

/**
 * 排他制御ヘルパー。
 */
public interface ExclusiveControlHelper {

    /**
     * 排他キーに紐づく現行回数とクライアント保持回数を照合し、一致時のみ更新後の排他回数を返す。
     *
     * @param exclusiveKey   排他キー（非 null・非空）
     * @param exclusiveCount クライアントが保持する排他回数（非 null・0 以上）
     * @return 更新後の排他回数
     * @throws NullPointerException 引数が null の場合
     */
    Integer checkExclusive(String exclusiveKey, Integer exclusiveCount);
}
