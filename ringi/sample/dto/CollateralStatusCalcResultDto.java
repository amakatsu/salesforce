package jp.co.btm.irl.rlr.rg004.dto;

import java.util.List;

/**
 * 本件後保全状況計算結果DTO
 * <p>担保の全行（明細+小計+合計+補正値+裸与信）を同一構造のListで保持する。
 * 合計行・小計行もListの1要素として種別キーで識別する。個別フィールドは持たない。</p>
 */
public class CollateralStatusCalcResultDto {

    /**
     * 担保の全行（明細+小計+合計+補正値+裸与信を全て含む）
     * <p>種別キー: tanpoKubun + tanpoShubetsu の複合キーで行を識別する。
     * 例: 合計行 = tanpoKubun="kitei", tanpoShubetsu="total"
     *     補正値 = tanpoKubun="kitei", tanpoShubetsu="hosei"
     *     裸与信 = tanpoKubun="hadaka", tanpoShubetsu="yoshin"</p>
     */
    private List<TanpoItem> tanpoItemList;

    public List<TanpoItem> getTanpoItemList() { return tanpoItemList; }
    public void setTanpoItemList(List<TanpoItem> v) { this.tanpoItemList = v; }
}
