package jp.co.btm.irl.rlr.rg004.dto;

/**
 * サービスアウトプットDTO
 * <p>計数情報マスタ再登録サービスの出力パラメータを保持する。</p>
 */
public class ServiceOutputDto {

    /** 処理成功フラグ // 旧: F_SUCCESS_FLAG */
    private boolean success;

    /** エラーID // 旧: F_ERROR_ID */
    private String errorId;

    /** エラー種別 // 旧: F_ERROR_TYPE */
    private String errorType;

    /** エラーメッセージ // 旧: F_ERROR_MSG */
    private String errorMessage;

    /** 更新後の排他回数 */
    private int updatedLockCount;

    /** 計数計算結果（画面表示用） */
    private KeisuCalcResultDto calcResult;

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean v) { this.success = v; }
    public String getErrorId() { return errorId; }
    public void setErrorId(String v) { this.errorId = v; }
    public String getErrorType() { return errorType; }
    public void setErrorType(String v) { this.errorType = v; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String v) { this.errorMessage = v; }
    public int getUpdatedLockCount() { return updatedLockCount; }
    public void setUpdatedLockCount(int v) { this.updatedLockCount = v; }
    public KeisuCalcResultDto getCalcResult() { return calcResult; }
    public void setCalcResult(KeisuCalcResultDto v) { this.calcResult = v; }
}
