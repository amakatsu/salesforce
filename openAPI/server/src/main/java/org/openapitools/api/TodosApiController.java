package org.openapitools.api;

import org.openapitools.model.Todo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.context.request.NativeWebRequest;

import jakarta.validation.constraints.*;
import jakarta.validation.Valid;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import jakarta.annotation.Generated;

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2025-07-13T02:19:13.358908009Z[Etc/UTC]", comments = "Generator version: 7.5.0")
@Controller
@RequestMapping("${openapi.todo.base-path:}")
/**
 * Todos APIのコントローラークラス。
 * このクラスは、Todoアイテムに関連するHTTPリクエストを処理します。
 * OpenAPI定義に基づいて自動生成されています。
 */
public class TodosApiController implements TodosApi {

    private final NativeWebRequest request;

    /**
     * コンストラクタ。
     * SpringフレームワークによってNativeWebRequestがインジェクト（注入）されます。
     * これにより、リクエスト固有のデータへのアクセスが可能になります。
     * 
     * @param request ネイティブなWebリクエストのコンテキスト
     */
    @Autowired
    public TodosApiController(NativeWebRequest request) {
        this.request = request;
    }

    /**
     * 現在のNativeWebRequestを取得します。
     * これにより、API実装がリクエストの詳細にアクセスできるようになります。
     * 
     * @return 現在のNativeWebRequestを含むOptional
     */
    @Override
    public Optional<NativeWebRequest> getRequest() {
        return Optional.ofNullable(request);
    }

}
