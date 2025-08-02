-- Credit Data テーブル
CREATE TABLE IF NOT EXISTS credit_data (
    id VARCHAR(255) PRIMARY KEY,
    label VARCHAR(255),
    due_date VARCHAR(50),
    rate VARCHAR(50),
    balance99 DECIMAL(19,2),
    principal DECIMAL(19,2),
    change_amount DECIMAL(19,2),
    post_balance DECIMAL(19,2),
    actual_balance DECIMAL(19,2),
    correction DECIMAL(19,2),
    parent_id VARCHAR(255)
);

-- Collateral Data テーブル
CREATE TABLE IF NOT EXISTS collateral_data (
    id VARCHAR(255) PRIMARY KEY,
    collateral_type VARCHAR(255),
    reg_value DECIMAL(19,2),
    market_value DECIMAL(19,2),
    parent_id VARCHAR(255)
);