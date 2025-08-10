public with sharing class CollateralDataService {
    
    @AuraEnabled(cacheable=true)
    public static String getCollateralData() {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/collateral-data');
            request.setMethod('GET');
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() == 200) {
                return response.getBody();
            } else {
                throw new AuraHandledException('APIコール失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled
    public static String postCollateralData(Object dataObj) {
        try {
            String jsonData;
            if (dataObj instanceof String) {
                jsonData = (String) dataObj;
            } else {
                jsonData = JSON.serialize(dataObj);
            }
            
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/collateral-data');
            request.setMethod('POST');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(jsonData);
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() >= 200 && response.getStatusCode() < 300) {
                return response.getBody();
            } else {
                throw new AuraHandledException('APIコール失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
    
    @AuraEnabled(cacheable=true)
    public static String getCreditData() {
        try {
            HttpRequest request = new HttpRequest();
            request.setEndpoint('callout:API_Server/api/credit-data');
            request.setMethod('GET');
            request.setTimeout(10000);
            
            Http http = new Http();
            HttpResponse response = http.send(request);
            
            if (response.getStatusCode() == 200) {
                return response.getBody();
            } else {
                throw new AuraHandledException('APIコール失敗: ' + response.getStatusCode() + ' - ' + response.getStatus());
            }
        } catch (Exception e) {
            throw new AuraHandledException('エラーが発生しました: ' + e.getMessage());
        }
    }
}