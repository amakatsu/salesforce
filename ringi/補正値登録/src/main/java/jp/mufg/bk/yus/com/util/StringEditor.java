package jp.mufg.bk.yus.com.util;

/**
 * 文字列編集ユーティリティ。
 */
public interface StringEditor {

    /**
     * 店番を 3 桁形式から 7 桁形式に変換する。
     *
     * @param brNo3 3 桁の店番（非 null）
     * @return 7 桁形式の店番
     * @throws NullPointerException 引数が null の場合
     */
    String toServerBrNo(String brNo3);
}
