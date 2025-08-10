public with sharing class UserProfileService {
    
    @AuraEnabled(cacheable=true)
    public static String getAllUserProfiles() {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles');
            request.setMethod('GET');
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() == 200) {
                return response.getBody();
            } else {
                throw new AuraHandledException('ユーザープロフィール取得失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled(cacheable=true)
    public static String getUserProfile(String userId) {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles/' + userId);
            request.setMethod('GET');
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() == 200) {
                return response.getBody();
            } else {
                throw new AuraHandledException('ユーザープロフィール取得失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled
    public static String saveUserProfile(Object profileData) {
        try {
            String jsonData;
            if (profileData instanceof String) {
                jsonData = (String) profileData;
            } else {
                jsonData = JSON.serialize(profileData);
            }
            
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles');
            request.setMethod('POST');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(jsonData);
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() >= 200 && response.getStatusCode() < 300) {
                return response.getBody();
            } else {
                throw new AuraHandledException('プロフィール保存失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled
    public static String updateUserProfile(String userId, Object profileData) {
        try {
            String jsonData;
            if (profileData instanceof String) {
                jsonData = (String) profileData;
            } else {
                jsonData = JSON.serialize(profileData);
            }
            
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles/' + userId);
            request.setMethod('PUT');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(jsonData);
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() >= 200 && response.getStatusCode() < 300) {
                return response.getBody();
            } else {
                throw new AuraHandledException('プロフィール更新失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled
    public static String deleteUserProfile(String userId) {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles/' + userId);
            request.setMethod('DELETE');
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() >= 200 && response.getStatusCode() < 300) {
                return response.getBody();
            } else {
                throw new AuraHandledException('プロフィール削除失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled(cacheable=true)
    public static String searchUserProfiles(String searchCriteria) {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/user-profiles/search');
            request.setMethod('POST');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(searchCriteria);
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() == 200) {
                return response.getBody();
            } else {
                throw new AuraHandledException('プロフィール検索失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
}