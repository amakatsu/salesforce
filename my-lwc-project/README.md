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

## 動的テーブルコンポーネント仕様

### Validation機能について

#### 現行仕様（既存の固定テーブルに準拠）
- **直接編集方式**: ユーザーがテーブル内で直接データを編集可能
- **リアルタイムvalidation**: データ変更時に`validateElement`を呼び出してvalidation実行
- **結果処理**: validationの結果（エラー件数）は取得せず、エラー表示のみ行う
- **保存時validation**: 保存ボタン押下時に選択されたデータのみ再度validation実行

#### 実装詳細
```javascript
// 入力変更時（リアルタイムvalidation）
handleInputChange(event) {
  // データ更新
  this.editableTableData = this.editableTableData.map(record =>
    record.Id === id ? { ...record, [field]: value } : record
  );

  // validation実行（結果は画面表示のみ）
  validateElement([event.target], [], []);
}

// 保存時（選択データのみvalidation）
validateAllInputs(targetComponent) {
  selectedIds.forEach(recordId => {
    const elements = targetComponent.getElementsById(recordId);
    elements.forEach(element => {
      const errorCount = validateElement([element], [], []);
      // エラー件数を集計して保存処理の可否を判定
    });
  });
}
```

#### 対象コンポーネント
- `rowDynamicMultiHeader` - マルチヘッダーテーブル
- `rowDynamicOPC` - OPCテーブル

#### 実装における設計判断とコメント

**データフローについて**
- 親コンポーネントから子コンポーネントに`@api`でデータを渡す方式を採用
- 子コンポーネント内で`editableTableData`として管理し、UI操作と同期

**validation処理について**
- 既存の固定テーブルの方式に倣い、子コンポーネント内で`validateElement`を呼び出し
- 入力時validation：エラー表示のみ（結果の戻り値は使用せず）
- 保存時validation：親コンポーネントで実装し、エラー件数を集計して保存可否を判定

**保存メソッドの設計**
- 既存の固定テーブルでは子コンポーネントに保存メソッドが不要だったため、今回も子には実装せず
- 親コンポーネントに保存ボタンを配置し、選択されたデータのvalidationを自前で実装
- **この設計は既存処理に取って代わる認識のため、サンプル的な実装**

**validation例外処理について**
- `validateElement`内でエラーを投げる例外が存在する可能性
- 親コンポーネントでのキャッチ方法については要検討
- 現状は`try-catch`で基本的なエラーハンドリングを実装

**既存システムとの整合性**
- 固定テーブルの動作を踏襲することで、ユーザー体験の一貫性を保持
- 将来的な機能拡張時も既存パターンに沿った開発が可能

#### 仕様変更が必要な場合
現行の仕様に不足がある場合は以下をご相談ください：
- validation結果の詳細な処理方法
- エラー表示の形式・タイミング
- 保存条件の変更
- validation例外の適切なハンドリング方法
- その他の要件

## 開発メモ

- CSP問題を回避するためApex経由でAPI呼び出し
- LWCからApexメソッドを呼び出す構成
- Named Credentialで外部接続を管理
- 動的テーブルは既存固定テーブルのvalidation方式に準拠