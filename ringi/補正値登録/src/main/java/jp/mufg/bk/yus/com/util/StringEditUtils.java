package jp.mufg.bk.yus.com.util;

import java.util.Objects;

/**
 * 文字列編集ユーティリティ。
 */
public final class StringEditUtils {

    private static final String SERVER_BR_NO_PREFIX = "0000";

    private StringEditUtils() {
        throw new AssertionError("（なぜ）utility class のため new 禁止");
    }

    /**
     * 店番を 3 桁形式から 7 桁形式（サーバー用店番）に変換する。
     *
     * @param brNo3 3 桁の店番（非 null）
     * @return 7 桁形式の店番（先頭 4 文字を "0000" でパディング）
     * @throws NullPointerException 引数が null の場合
     */
    public static String toServerBrNo(String brNo3) {
        Objects.requireNonNull(brNo3, "brNo3");
        return SERVER_BR_NO_PREFIX + brNo3;
    }
}
