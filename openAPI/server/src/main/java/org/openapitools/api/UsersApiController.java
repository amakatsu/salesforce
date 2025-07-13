package org.openapitools.api;

import org.openapitools.model.User;
import org.openapitools.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.context.request.NativeWebRequest;

import java.util.List;
import java.util.Optional;

/**
 * Users APIのコントローラークラス。
 * このクラスは、ユーザーに関連するHTTPリクエストを処理します。
 * OpenAPI定義に基づいて自動生成されています。
 */
@Controller
@RequestMapping("${openapi.todo.base-path:}")
public class UsersApiController implements UsersApi {

    private final NativeWebRequest request;

    private final UserService userService;

    @Autowired
    public UsersApiController(NativeWebRequest request, UserService userService) {
        this.request = request;
        this.userService = userService;
    }

    @Override
    public Optional<NativeWebRequest> getRequest() {
        return Optional.ofNullable(request);
    }

    @Override
    public ResponseEntity<List<User>> usersGet() {
        return ResponseEntity.ok(userService.findAllUsers());
    }

}
