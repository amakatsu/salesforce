-- User Profile テーブル
CREATE TABLE IF NOT EXISTS user_profiles (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(50),
    location VARCHAR(500),
    bio TEXT,
    occupation VARCHAR(255),
    education VARCHAR(255),
    looking_for VARCHAR(100),
    age_range_min INTEGER,
    age_range_max INTEGER,
    max_distance INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Profile の趣味テーブル（多対多関係）
CREATE TABLE IF NOT EXISTS user_interests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_profile_id VARCHAR(255),
    interest VARCHAR(255),
    FOREIGN KEY (user_profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

-- User Profile の写真テーブル（1対多関係）
CREATE TABLE IF NOT EXISTS user_photos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_profile_id VARCHAR(255),
    photo_url VARCHAR(1000),
    display_order INTEGER DEFAULT 0,
    FOREIGN KEY (user_profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

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