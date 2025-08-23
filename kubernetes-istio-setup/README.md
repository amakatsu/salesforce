# 🚀 Kiali と Prometheus の簡単セットアップガイド

このガイドでは、Kubernetesクラスター上にKiali（サービスメッシュの可視化）とPrometheus（メトリクス監視）を簡単にインストールする方法を説明します。

## 📋 事前準備

以下が必要です：
- 動作するKubernetesクラスター
- `kubectl` コマンドが使える環境

## 🏃‍♂️ ステップ1: Istioをインストール

Istioは、KialiとPrometheusを動かすために必要なサービスメッシュプラットフォームです。

```bash
# 1. Istioをダウンロード
curl -L https://istio.io/downloadIstio | sh-

# 2. ダウンロードしたフォルダに移動（バージョン番号は変わる可能性があります）
cd istio-1.*

# 3. istioctl コマンドを使えるようにする
export PATH=$PWD/bin:$PATH

# 4. Istioをインストール（デモ用設定）
istioctl install --set values.defaultRevision=default -y

# ✅ この時点でIstioのインストールは完了です
```

## 📊 ステップ2: Kiali（可視化ツール）をインストール

Kialiを使うと、サービス間の通信を図で見ることができます。

```bash
# 1. Kialiをインストール
kubectl apply -f samples/addons/kiali.yaml

# 2. Kialiが起動するまで待つ（最大5分）
kubectl wait --for=condition=ready pod -l app=kiali -n istio-system --timeout=300s

# ✅ Kialiのインストールは完了です
```

## 📈 ステップ3: Prometheus（監視ツール）をインストール

Prometheusでシステムのメトリクスを収集・監視できます。

```bash
# 1. Prometheusをインストール
kubectl apply -f samples/addons/prometheus.yaml

# 2. Prometheusが起動するまで待つ（最大5分）
kubectl wait --for=condition=ready pod -l app=prometheus -n istio-system --timeout=300s

# ✅ Prometheusのインストールは完了です
```

## 🌐 ステップ4: Istio Gatewayで外部アクセスを設定

### Kiali用Gateway設定

```bash
# Kiali用のGatewayとVirtualServiceを作成
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: kiali-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: kiali-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - kiali-gateway
  http:
  - match:
    - uri:
        prefix: /kiali
    route:
    - destination:
        host: kiali
        port:
          number: 20001
EOF
```

### Prometheus用Gateway設定

```bash
# Prometheus用のGatewayとVirtualServiceを作成
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: prometheus-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http-prometheus
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: prometheus-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - prometheus-gateway
  http:
  - match:
    - uri:
        prefix: /prometheus
    route:
    - destination:
        host: prometheus
        port:
          number: 9090
EOF
```

### Istio IngressGatewayのポート確認

```bash
# IngressGatewayのポート番号を確認
kubectl get svc istio-ingressgateway -n istio-system

# 出力例：
# istio-ingressgateway   LoadBalancer   10.96.172.12   <pending>   15021:30203/TCP,80:31508/TCP,443:31468/TCP
```

### ブラウザでアクセス

**Kindクラスター**を使用している場合は、kind-config.yamlで設定されたポートマッピングを使用：

- **Kiali**: `http://サーバーのIP:8080/kiali`
- **Prometheus**: `http://サーバーのIP:8080/prometheus`

例：`http://35.79.251.78:8080/kiali`

**通常のKubernetesクラスター**の場合は、IngressGatewayのNodePortを確認：

```bash
kubectl get svc istio-ingressgateway -n istio-system
# 80番ポートのNodePortを確認（例：31508）
# http://サーバーのIP:31508/kiali
```

## ✅ ステップ5: 正しくインストールされたか確認

```bash
# インストールされたポッドを確認
kubectl get pods -n istio-system

# 以下のようなポッドが表示されればOK：
# kiali-xxxxxxxxx-xxxxx        1/1     Running
# prometheus-xxxxxxxxx-xxxxx   2/2     Running
# istiod-xxxxxxxxx-xxxxx       1/1     Running
```

## 🔧 トラブルシューティング

### 外部からアクセスできない場合

**問題**: `http://サーバーのIP:20001/kiali/` にアクセスできない

**解決方法**:
1. AWSの場合：セキュリティグループでポート20001を開放
2. ファイアウォールの場合：ポート20001を許可

### ポートフォワードが停止した場合

```bash
# 停止したプロセスを確認
ps aux | grep port-forward

# 必要に応じてプロセスを停止
kill [プロセスID]

# 再度ポートフォワードを開始
kubectl port-forward svc/kiali 20001:20001 -n istio-system --address 0.0.0.0 &
```

## 💡 補足情報

- **Kiali**: サービス間の通信を視覚的に確認できるツール
- **Prometheus**: システムメトリクスの収集と監視ができるツール
- **ポートフォワード**: 一時的にローカルから Kubernetes サービスにアクセスする方法
- **本番環境**: Ingressコントローラーを使用した適切な公開設定を推奨