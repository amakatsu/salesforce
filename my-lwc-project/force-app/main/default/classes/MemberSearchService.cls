public with sharing class MemberSearchService {
    
    @AuraEnabled
    public static List<MemberData> searchMembers(String searchParams) {
        try {
            System.debug('Search Params: ' + searchParams);
            
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles/search');
            request.setMethod('POST');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(searchParams);
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            System.debug('Request Body: ' + searchParams);
            System.debug('Response Status Code: ' + response.getStatusCode());
            System.debug('Response Body: ' + response.getBody());
            
            if (response.getStatusCode() == 200) {
                return parseUserProfileResponse(response.getBody());
            } else {
                System.debug('API Error Response: ' + response.getBody());
                throw new AuraHandledException('メンバー検索失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            System.debug('Exception: ' + e.getMessage());
            System.debug('Stack Trace: ' + e.getStackTraceString());
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    private static List<MemberData> parseUserProfileResponse(String responseBody) {
        List<MemberData> members = new List<MemberData>();
        
        try {
            // レスポンスは直接UserProfileの配列
            List<Object> userProfileList = (List<Object>) JSON.deserializeUntyped(responseBody);
            
            for (Object userProfileObj : userProfileList) {
                Map<String, Object> userProfileMap = (Map<String, Object>) userProfileObj;
                
                MemberData member = new MemberData();
                member.id = String.valueOf(userProfileMap.get('id'));
                member.name = String.valueOf(userProfileMap.get('name'));
                
                // 年齢の処理
                Object ageObj = userProfileMap.get('age');
                if (ageObj != null) {
                    member.age = ageObj instanceof Integer ? (Integer) ageObj : Integer.valueOf(String.valueOf(ageObj));
                }
                
                // 性別の処理（APIの値を日本語ラベルに変換）
                String genderValue = String.valueOf(userProfileMap.get('gender'));
                member.gender = genderValue;
                member.genderLabel = MemberSearchConstants.getGenderLabel(genderValue);
                
                member.location = String.valueOf(userProfileMap.get('location'));
                member.occupation = String.valueOf(userProfileMap.get('occupation'));
                member.bio = String.valueOf(userProfileMap.get('bio'));
                
                // 教育レベルの処理（APIの値はすでに日本語）
                String educationValue = String.valueOf(userProfileMap.get('education'));
                member.education = educationValue;
                member.educationLabel = educationValue;
                
                // 探しているものの処理（APIの値はすでに日本語）
                String lookingForValue = String.valueOf(userProfileMap.get('lookingFor'));
                member.lookingFor = lookingForValue;
                member.lookingForLabel = lookingForValue;
                
                // 趣味リストの処理（APIの値をそのまま保持し、表示用ラベルも生成）
                Object interestsObj = userProfileMap.get('interests');
                if (interestsObj instanceof List<Object>) {
                    List<Object> interestsList = (List<Object>) interestsObj;
                    member.interests = new List<String>();
                    member.interestLabels = new List<String>();
                    for (Object interest : interestsList) {
                        String interestValue = String.valueOf(interest);
                        member.interests.add(interestValue);
                        // APIの値はすでに日本語なのでそのまま使用
                        member.interestLabels.add(interestValue);
                    }
                }
                
                // 写真リストの処理
                Object photosObj = userProfileMap.get('photos');
                if (photosObj instanceof List<Object>) {
                    List<Object> photosList = (List<Object>) photosObj;
                    member.photos = new List<String>();
                    for (Object photo : photosList) {
                        member.photos.add(String.valueOf(photo));
                    }
                }
                
                // 年齢範囲の処理
                Object ageRangeMinObj = userProfileMap.get('ageRangeMin');
                if (ageRangeMinObj != null) {
                    member.ageRangeMin = ageRangeMinObj instanceof Integer ? (Integer) ageRangeMinObj : Integer.valueOf(String.valueOf(ageRangeMinObj));
                }
                
                Object ageRangeMaxObj = userProfileMap.get('ageRangeMax');
                if (ageRangeMaxObj != null) {
                    member.ageRangeMax = ageRangeMaxObj instanceof Integer ? (Integer) ageRangeMaxObj : Integer.valueOf(String.valueOf(ageRangeMaxObj));
                }
                
                // Boolean値の処理
                Object isActiveObj = userProfileMap.get('isActive');
                if (isActiveObj != null) {
                    member.isActive = isActiveObj instanceof Boolean ? (Boolean) isActiveObj : Boolean.valueOf(String.valueOf(isActiveObj));
                }
                
                members.add(member);
            }
        } catch (Exception e) {
            System.debug('レスポンス解析エラー: ' + e.getMessage());
            System.debug('レスポンス内容: ' + responseBody);
            throw new AuraHandledException('APIレスポンスの解析でエラーが発生しました: ' + e.getMessage());
        }
        
        return members;
    }
    
    // UserProfile用のメンバーデータラッパークラス
    public class MemberData {
        @AuraEnabled public String id { get; set; }
        @AuraEnabled public String name { get; set; }
        @AuraEnabled public Integer age { get; set; }
        @AuraEnabled public String gender { get; set; }
        @AuraEnabled public String genderLabel { get; set; }
        @AuraEnabled public String location { get; set; }
        @AuraEnabled public String bio { get; set; }
        @AuraEnabled public List<String> interests { get; set; }
        @AuraEnabled public List<String> interestLabels { get; set; }
        @AuraEnabled public List<String> photos { get; set; }
        @AuraEnabled public String occupation { get; set; }
        @AuraEnabled public String education { get; set; }
        @AuraEnabled public String educationLabel { get; set; }
        @AuraEnabled public String lookingFor { get; set; }
        @AuraEnabled public String lookingForLabel { get; set; }
        @AuraEnabled public Integer ageRangeMin { get; set; }
        @AuraEnabled public Integer ageRangeMax { get; set; }
        @AuraEnabled public Boolean isActive { get; set; }
    }
}