#!/bin/bash

# OpenAPI サーバーのビルドとデプロイスクリプト
set -e

echo "🚀 OpenAPI サーバーのビルドとデプロイを開始します"

# 1. Dockerイメージのビルド
echo "🔧 Dockerイメージをビルドしています..."
docker build -t openapi-server:latest .
echo "✅ Dockerイメージビルド完了"

# 2. KindクラスターにDockerイメージをロード
echo "📦 KindクラスターにDockerイメージをロードしています..."
kind load docker-image openapi-server:latest --name istio-openai-cluster
echo "✅ Dockerイメージロード完了"

# 3. Kubernetesにデプロイ
echo "🚀 Kubernetesにデプロイしています..."
kubectl apply -f openapi-deployment.yaml
echo "✅ デプロイ完了"

# 4. ポッドの起動を待機
echo "⏳ ポッドの起動を待機しています..."
kubectl wait --for=condition=ready pod -l app=openapi-server --timeout=300s
echo "✅ ポッド起動完了"

# 5. 動作確認
echo "🔍 デプロイメント状況を確認しています..."
echo ""
echo "=== OpenAPI Server Pods ==="
kubectl get pods -l app=openapi-server

echo ""
echo "=== OpenAPI Service ==="
kubectl get svc openapi-service

echo ""
echo "🎉 OpenAPI サーバーのデプロイ完了！"
echo ""
echo "📱 アクセス方法:"
echo "- OpenAPI Docs: http://サーバーのIP:8080/api/swagger-ui.html"
echo "- API Endpoint: http://サーバーのIP:8080/api/"
echo ""