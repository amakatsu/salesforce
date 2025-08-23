public class MemberSearchConstants {
    
    // 性別マッピング
    public static final Map<String, String> GENDER_MAPPING = new Map<String, String>{
        'male' => '男性',
        'female' => '女性',
        'other' => 'その他'
    };
    
    // 性別の逆マッピング（UIからAPIへ）
    public static final Map<String, String> GENDER_REVERSE_MAPPING = new Map<String, String>{
        '男性' => 'male',
        '女性' => 'female',
        'その他' => 'other'
    };
    
    // 趣味・興味のマッピング（UIからAPIへ）
    public static final Map<String, String> INTEREST_MAPPING = new Map<String, String>{
        'reading' => '読書',
        'movies' => '映画',
        'music' => '音楽',
        'travel' => '旅行',
        'sports' => 'スポーツ',
        'cooking' => '料理',
        'gaming' => 'ゲーム',
        'art' => 'アート',
        'technology' => 'テクノロジー',
        'photography' => '写真',
        'gardening' => 'ガーデニング',
        'dancing' => 'ダンス',
        'anime' => 'アニメ',
        'cafe' => 'カフェ巡り',
        'sweets' => 'お菓子作り',
        'outdoor' => 'アウトドア',
        'diy' => 'DIY',
        'camp' => 'キャンプ',
        'yoga' => 'ヨガ',
        'fitness' => 'フィットネス',
        'live' => 'ライブ'
    };
    
    // 趣味・興味の逆マッピング（APIからUIへ）
    public static final Map<String, String> INTEREST_REVERSE_MAPPING = new Map<String, String>{
        '読書' => 'reading',
        '映画' => 'movies',
        '音楽' => 'music',
        '旅行' => 'travel',
        'スポーツ' => 'sports',
        '料理' => 'cooking',
        'ゲーム' => 'gaming',
        'アート' => 'art',
        'テクノロジー' => 'technology',
        '写真' => 'photography',
        'ガーデニング' => 'gardening',
        'ダンス' => 'dancing',
        'アニメ' => 'anime',
        'カフェ巡り' => 'cafe',
        'お菓子作り' => 'sweets',
        'アウトドア' => 'outdoor',
        'DIY' => 'diy',
        'キャンプ' => 'camp',
        'ヨガ' => 'yoga',
        'フィットネス' => 'fitness',
        'ライブ' => 'live'
    };
    
    // 探しているもののマッピング
    public static final Map<String, String> LOOKING_FOR_MAPPING = new Map<String, String>{
        '友達' => 'friends',
        '恋人' => 'relationship',
        '結婚相手' => 'marriage',
        'その他' => 'other'
    };
    
    // 探しているものの逆マッピング
    public static final Map<String, String> LOOKING_FOR_REVERSE_MAPPING = new Map<String, String>{
        'friends' => '友達',
        'relationship' => '恋人',
        'marriage' => '結婚相手',
        'other' => 'その他'
    };
    
    // 教育レベルのマッピング
    public static final Map<String, String> EDUCATION_MAPPING = new Map<String, String>{
        '高校卒業' => 'high_school',
        '専門学校卒業' => 'vocational_school',
        '短大卒業' => 'junior_college',
        '大学卒業' => 'university',
        '大学院卒業' => 'graduate_school',
        '音楽大学卒業' => 'music_university'
    };
    
    // 教育レベルの逆マッピング
    public static final Map<String, String> EDUCATION_REVERSE_MAPPING = new Map<String, String>{
        'high_school' => '高校卒業',
        'vocational_school' => '専門学校卒業',
        'junior_college' => '短大卒業',
        'university' => '大学卒業',
        'graduate_school' => '大学院卒業',
        'music_university' => '音楽大学卒業'
    };
    
    // 職業のマッピング（一般的な職業）
    public static final Set<String> COMMON_OCCUPATIONS = new Set<String>{
        'エンジニア',
        'デザイナー',
        '営業',
        'プログラマー',
        '音楽講師',
        'パティシエ',
        'IT企業経営',
        'インストラクター',
        'コンサルタント',
        '教師',
        '看護師',
        '医師',
        '公務員',
        '会計士',
        '弁護士'
    };
    
    // 都道府県のマッピング
    public static final Set<String> PREFECTURES = new Set<String>{
        '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
        '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
        '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
        '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
        '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
        '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
        '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
    };
    
    // ユーティリティメソッド
    
    /**
     * 性別を日本語に変換
     */
    public static String getGenderLabel(String genderValue) {
        return GENDER_MAPPING.containsKey(genderValue) ? GENDER_MAPPING.get(genderValue) : genderValue;
    }
    
    /**
     * 性別を英語に変換
     */
    public static String getGenderValue(String genderLabel) {
        return GENDER_REVERSE_MAPPING.containsKey(genderLabel) ? GENDER_REVERSE_MAPPING.get(genderLabel) : genderLabel;
    }
    
    /**
     * 趣味リストを日本語に変換
     */
    public static List<String> getInterestLabels(List<String> interestValues) {
        List<String> labels = new List<String>();
        if (interestValues != null) {
            for (String value : interestValues) {
                labels.add(INTEREST_MAPPING.containsKey(value) ? INTEREST_MAPPING.get(value) : value);
            }
        }
        return labels;
    }
    
    /**
     * 趣味リストを英語に変換
     */
    public static List<String> getInterestValues(List<String> interestLabels) {
        List<String> values = new List<String>();
        if (interestLabels != null) {
            for (String label : interestLabels) {
                values.add(INTEREST_REVERSE_MAPPING.containsKey(label) ? INTEREST_REVERSE_MAPPING.get(label) : label);
            }
        }
        return values;
    }
    
    /**
     * 探しているものを日本語に変換
     */
    public static String getLookingForLabel(String lookingForValue) {
        return LOOKING_FOR_REVERSE_MAPPING.containsKey(lookingForValue) ? LOOKING_FOR_REVERSE_MAPPING.get(lookingForValue) : lookingForValue;
    }
    
    /**
     * 探しているものを英語に変換
     */
    public static String getLookingForValue(String lookingForLabel) {
        return LOOKING_FOR_MAPPING.containsKey(lookingForLabel) ? LOOKING_FOR_MAPPING.get(lookingForLabel) : lookingForLabel;
    }
    
    /**
     * 教育レベルを日本語に変換
     */
    public static String getEducationLabel(String educationValue) {
        return EDUCATION_REVERSE_MAPPING.containsKey(educationValue) ? EDUCATION_REVERSE_MAPPING.get(educationValue) : educationValue;
    }
    
    /**
     * 教育レベルを英語に変換
     */
    public static String getEducationValue(String educationLabel) {
        return EDUCATION_MAPPING.containsKey(educationLabel) ? EDUCATION_MAPPING.get(educationLabel) : educationLabel;
    }
}