package org.openapitools.configuration;

import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * ルートURL ("/")へのアクセスをOpenAPIのAPIドキュメント（Swagger UI）にリダイレクトするためのコントローラー。
 *
 * このコントローラーは、アプリケーションのルートにアクセスした際に、ユーザーを自動的に
 * `swagger-ui.html`に転送します。これにより、開発者やAPI利用者は、
 * アプリケーションのベースURLにアクセスするだけで簡単にAPIドキュメントを閲覧できます。
 */
@Controller
public class HomeController {

    @RequestMapping("/")
    public String index() {
        return "redirect:swagger-ui.html";
    }

}
