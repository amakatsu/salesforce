package jp.mufg.bk.yus.domain.service.rg_v0501_rinsashocntinforegistcorrectvalue.constant;

/**
 * 補正値登録機能で使用する定数の集約。
 */
public final class RegistCorrectValueConst {

    /** 削除フラグ（未削除）。Repository の WHERE 条件で使用する。 */
    public static final String DEL_FLG_ACTIVE = "0";

    private RegistCorrectValueConst() {
        // 誤って new されたら検知できるよう例外を投げる
        throw new AssertionError("RegistCorrectValueConst is a constants holder; do not instantiate.");
    }
}
