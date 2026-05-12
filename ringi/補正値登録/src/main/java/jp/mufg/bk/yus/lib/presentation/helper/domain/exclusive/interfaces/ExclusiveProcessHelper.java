package jp.mufg.bk.yus.lib.presentation.helper.domain.exclusive.interfaces;

/**
 * 楽観排他制御の更新回数チェック契約。
 * 実装は別所（lib モジュール側）で提供する想定で、本モジュールは API のみを公開する。
 */
public interface ExclusiveProcessHelper {

    /**
     * 排他キーに紐づく現行回数とクライアント保持回数を照合し、更新後の排他回数を返す。
     *
     * @param exclusiveKey   排他キー
     * @param exclusiveCount クライアントが保持する排他回数
     * @return 更新後の排他回数
     */
    int checkExclusiveCount(String exclusiveKey, int exclusiveCount);
}
