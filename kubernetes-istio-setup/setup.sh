#!/bin/bash

# Kubernetes + Istio + Kiali + Prometheus セットアップスクリプト
set -e

echo "🚀 Kubernetes + Istio + Kiali + Prometheus セットアップを開始します"

# 1. Kindクラスターの作成
echo "📦 Kindクラスターを作成しています..."
if ! kind get clusters | grep -q "istio-openai-cluster"; then
    kind create cluster --config kind-config.yaml --name istio-openai-cluster
    echo "✅ Kindクラスター作成完了"
else
    echo "ℹ️  Kindクラスターは既に存在します"
fi

# 2. Istioのダウンロードとインストール
echo "🔧 Istioをインストールしています..."
if [ ! -d "istio-1.26.3" ]; then
    curl -L https://istio.io/downloadIstio | sh-
    echo "✅ Istioダウンロード完了"
else
    echo "ℹ️  Istioは既にダウンロードされています"
fi

# istoctlのパスを設定
export PATH=$PWD/istio-1.26.3/bin:$PATH

# Istioのインストール
echo "⚙️  Istioコントロールプレーンをインストールしています..."
istioctl install --set values.defaultRevision=default -y
echo "✅ Istioインストール完了"

# 3. Kiali & Prometheusのインストール
echo "📊 Kiali & Prometheusをインストールしています..."
kubectl apply -f istio-1.26.3/samples/addons/kiali.yaml
kubectl apply -f istio-1.26.3/samples/addons/prometheus.yaml

# ポッドが起動するまで待機
echo "⏳ ポッドの起動を待機しています..."
kubectl wait --for=condition=ready pod -l app=kiali -n istio-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=prometheus -n istio-system --timeout=300s
echo "✅ Kiali & Prometheus起動完了"

# 4. Gateway設定の適用
echo "🌐 Gatewayを設定しています..."
kubectl apply -f monitoring-gateway.yaml
echo "✅ Gateway設定完了"

# 5. 動作確認
echo "🔍 セットアップ状況を確認しています..."
echo ""
echo "=== Istio System Pods ==="
kubectl get pods -n istio-system

echo ""
echo "=== Services ==="
kubectl get svc -n istio-system

echo ""
echo "🎉 セットアップ完了！"
echo ""
echo "📱 アクセス方法:"
echo "- Kiali:      http://サーバーのIP:8080/kiali"
echo "- Prometheus: http://サーバーのIP:8080/prometheus"
echo ""
echo "例: http://$(curl -s ifconfig.me):8080/kiali"