FROM openjdk:21-jre-slim

WORKDIR /app

# JARファイルをコピー
COPY openapi-spring-0.1.0.jar app.jar

# ポート8080を公開
EXPOSE 8080

# アプリケーションを起動
ENTRYPOINT ["java", "-jar", "app.jar"]