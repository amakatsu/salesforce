
-- Credit Data 初期データ
INSERT INTO credit_data (id, label, due_date, rate, balance99, principal, change_amount, post_balance, actual_balance, correction, parent_id) VALUES
('root1', '信用取引関連', '2024-12-31', '2.5%', 10000000, 9500000, -500000, 1100000, 1050000, 50000, NULL),
('root2', '設備資金', '2025-03-31', '1.8%', 15000000, 14500000, -300000, 800000, 750000, 50000, NULL),
('child1', '短期借入金', '2024-06-30', '3.2%', 5000000, 4800000, -200000, 500000, 480000, 20000, 'root1');

-- Collateral Data 初期データ
INSERT INTO collateral_data (id, collateral_type, reg_value, market_value, parent_id) VALUES
('collGeneral', '規定担保合計', 8000000, 9600000, NULL),
('collGeneral2', '裸与信', 8000000, 9600000, NULL),
('cg4_1', '規定・優良小計 子1', 4000000, 4800000, 'collGeneral4');
