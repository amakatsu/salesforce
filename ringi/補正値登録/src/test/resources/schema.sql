-- ============================================================================
-- 計数情報(禀議計数補正値) テーブル定義（テスト用 H2 in-memory DB）
--
-- カラム物理名・型は本番テーブル（infra/mapper/tables/support/RinsashoKeisuHoseichiTable）
-- の SqlColumn 定義と完全に整合させる。差異が出ると Dynamic SQL DSL の SQL 生成と
-- スキーマがズレ、テストが見当違いの失敗を起こすため、片方を変更する場合は
-- 必ず両方同時に修正すること。
-- ============================================================================

CREATE TABLE RINSASHO_KEISU_HOSEICHI (
    BR_NO                                              VARCHAR(7)   NOT NULL,
    CM_NO                                              VARCHAR(7)   NOT NULL,
    DEL_FLG                                            VARCHAR(1)   NOT NULL,
    LOAN_DISC_TOTAL_CORRECTION_VALUE                   INTEGER,
    INTERNAL_JPY_CORRECTION_VALUE                      INTEGER,
    FOREX_CREDIT_TOTAL_CORRECTION_VALUE                INTEGER,
    SHI_SHO_TOTAL_CORRECTION_VALUE                     INTEGER,
    REGULATION_TANPO_CORRECTION_VALUE_REGULATION_VALUE INTEGER,
    REGULATION_TANPO_CORRECTION_VALUE_JIKA_BASE        INTEGER,
    CORRECTION_REASON                                  VARCHAR(100),
    EXCLUSIVE_KEY                                      VARCHAR(70)  NOT NULL,
    EXCLUSIVE_COUNT                                    INTEGER      NOT NULL,
    PRIMARY KEY (BR_NO, CM_NO)
);
