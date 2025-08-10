
-- User Profile 初期データ
INSERT INTO user_profiles (id, name, age, gender, location, bio, occupation, education, looking_for, age_range_min, age_range_max, max_distance, is_active) VALUES
('user001', '田中太郎', 28, 'male', '東京都渋谷区', '映画と料理が好きです。一緒に楽しい時間を過ごせる方と出会いたいです。', 'エンジニア', '大学卒業', '恋人', 25, 35, 10, TRUE),
('user002', '佐藤花子', 26, 'female', '東京都新宿区', '読書と音楽鑑賞が趣味です。カフェでゆっくり過ごすのが好きです。', 'デザイナー', '専門学校卒業', '友達', 24, 32, 15, TRUE),
('user003', '山田次郎', 32, 'male', '神奈川県横浜市', 'スポーツとアウトドアが大好きです。一緒にアクティブに過ごしましょう！', '営業', '大学卒業', '結婚相手', 28, 36, 20, TRUE),
('user004', '鈴木美香', 24, 'female', '東京都品川区', 'ゲームとアニメが大好きです！同じ趣味の人と話したいです。', 'プログラマー', '大学卒業', '友達', 22, 30, 25, TRUE),
('user005', '高橋健一', 30, 'male', '千葉県船橋市', '音楽制作が趣味です。ライブにもよく行きます。音楽好きな方とお話したいです。', '音楽講師', '音楽大学卒業', '恋人', 26, 34, 30, TRUE),
('user006', '渡辺麻衣', 29, 'female', '埼玉県大宮区', '料理とお菓子作りが得意です。一緒に美味しいものを食べに行ける方を探しています。', 'パティシエ', '専門学校卒業', '恋人', 27, 35, 20, TRUE),
('user007', '中村広志', 35, 'male', '東京都中野区', 'アウトドア活動とDIYが趣味です。週末はキャンプによく行きます。', 'IT企業経営', '大学院卒業', '結婚相手', 30, 38, 15, TRUE),
('user008', '小林聡子', 23, 'female', '神奈川県川崎市', 'ダンスとヨガをしています。健康的なライフスタイルを大切にしています。', 'インストラクター', '専門学校卒業', '友達', 21, 28, 18, TRUE);

-- User Interests 初期データ
INSERT INTO user_interests (user_profile_id, interest) VALUES
('user001', '映画'), ('user001', '料理'), ('user001', '旅行'),
('user002', '読書'), ('user002', '音楽'), ('user002', 'カフェ巡り'),
('user003', 'スポーツ'), ('user003', 'アウトドア'), ('user003', '写真'),
('user004', 'ゲーム'), ('user004', 'アニメ'), ('user004', '読書'),
('user005', '音楽'), ('user005', 'アート'), ('user005', 'ライブ'),
('user006', '料理'), ('user006', 'お菓子作り'), ('user006', '旅行'),
('user007', 'アウトドア'), ('user007', 'DIY'), ('user007', 'キャンプ'),
('user008', 'ダンス'), ('user008', 'ヨガ'), ('user008', 'フィットネス');

-- User Photos 初期データ
INSERT INTO user_photos (user_profile_id, photo_url, display_order) VALUES
('user001', 'https://example.com/photo1.jpg', 0),
('user002', 'https://example.com/photo2.jpg', 0),
('user003', 'https://example.com/photo3.jpg', 0),
('user004', 'https://example.com/photo4.jpg', 0),
('user005', 'https://example.com/photo5.jpg', 0),
('user006', 'https://example.com/photo6.jpg', 0),
('user007', 'https://example.com/photo7.jpg', 0),
('user008', 'https://example.com/photo8.jpg', 0);

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
