package jp.mufg.bk.yus.presentation.api.impl.rg_v0501_rinsasho_cnt_info_regist_correct_value.model;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.PositiveOrZero;

/** 排他制御（楽観ロック）に用いる共通 Model。Request / Response の双方で再利用する。 */
public class LockInfo {

    @NotNull(message = "排他キーは必須です")
    @Pattern(regexp = "[a-zA-Z0-9]{1,70}", message = "排他キーは半角英数字 1〜70 桁で入力してください")
    private String exclusiveKey;

    @NotNull(message = "排他回数は必須です")
    @PositiveOrZero(message = "排他回数は 0 以上の整数で入力してください")
    private Integer exclusiveCount;

    public String getExclusiveKey() {
        return exclusiveKey;
    }

    public void setExclusiveKey(String exclusiveKey) {
        this.exclusiveKey = exclusiveKey;
    }

    public Integer getExclusiveCount() {
        return exclusiveCount;
    }

    public void setExclusiveCount(Integer exclusiveCount) {
        this.exclusiveCount = exclusiveCount;
    }
}
