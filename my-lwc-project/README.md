# Salesforce LWC プロジェクト

Lightning Web Components（LWC）を使用した担保・与信データ管理システム

## プロジェクト構成

### Apexクラス
- `CollateralDataService.cls` - 外部API呼び出し用サービス
  - 担保データ取得・投稿
  - 与信データ取得・投稿
  - Named Credentialを使用した安全な接続

### LWCコンポーネント
- `collateralDataManager` - 担保データ管理
- `creditDataManager` - 与信データ管理
- その他のテーブル関連コンポーネント

### API接続設定
- Named Credential: `API_Server`
- エンドポイント: `http://35.79.251.78:8080`
- 認証: なし（NoAuthentication）

## デプロイコマンド

```bash
# 全体デプロイ
sf project deploy start --source-dir force-app

# 特定のコンポーネントのみ
sf project deploy start --source-dir force-app/main/default/classes
sf project deploy start --source-dir force-app/main/default/lwc
```

## ファイル構成

```
force-app/main/default/
├── classes/           # Apexクラス（.cls）
├── lwc/              # Lightning Web Components
├── namedCredentials/ # 外部接続設定
└── customMetadata/   # カスタムメタデータ

scripts/
├── apex/            # 実行用Apexスクリプト（.apex）
└── soql/            # SOQL クエリ
```

## 開発メモ

- CSP問題を回避するためApex経由でAPI呼び出し
- LWCからApexメソッドを呼び出す構成
- Named Credentialで外部接続を管理