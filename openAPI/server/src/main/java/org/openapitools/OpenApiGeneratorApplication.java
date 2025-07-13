package org.openapitools;

import com.fasterxml.jackson.databind.Module;

import org.mybatis.spring.annotation.MapperScan;
import org.openapitools.jackson.nullable.JsonNullableModule;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.context.annotation.FullyQualifiedAnnotationBeanNameGenerator;

/**
 * Spring Bootアプリケーションのメインクラス。
 * このクラスは、アプリケーションを起動し、基本的な設定を構成する役割を担います。
 *
 * 主な機能：
 * - `@SpringBootApplication`: Spring Bootアプリケーションであることを示し、自動設定、コンポーネントスキャン、
 * およびBean定義を有効にします。
 * - `mainメソッド`: アプリケーションのエントリーポイントであり、`SpringApplication.run()`を呼び出して
 * アプリケーションを起動します。
 * - `jsonNullableModule` Bean: `JsonNullable`型をサポートするためのJacksonモジュールを登録します。
 * これにより、APIのフィールドが明示的にnullに設定された場合と、存在しない場合を区別できます。
 *
 * このクラスは、アプリケーション全体の起動と設定の中心的な役割を果たします。
 */
@SpringBootApplication(nameGenerator = FullyQualifiedAnnotationBeanNameGenerator.class)
@ComponentScan(basePackages = { "org.openapitools", "org.openapitools.api",
        "org.openapitools.configuration", "org.openapitools.service",
        "org.openapitools.repository" }, nameGenerator = FullyQualifiedAnnotationBeanNameGenerator.class)
@EntityScan(basePackages = { "org.openapitools.model" })
@MapperScan("org.openapitools.mapper")
public class OpenApiGeneratorApplication {

    public static void main(String[] args) {
        SpringApplication.run(OpenApiGeneratorApplication.class, args);
    }

    @Bean(name = "org.openapitools.OpenApiGeneratorApplication.jsonNullableModule")
    public Module jsonNullableModule() {
        return new JsonNullableModule();
    }

}
