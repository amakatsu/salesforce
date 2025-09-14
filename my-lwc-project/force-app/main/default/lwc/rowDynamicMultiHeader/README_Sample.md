# rowDynamicMultiHeader サンプル実装ガイド

## 概要

このディレクトリには、Sample1から移植したメソッドで使用される外部依存コンポーネントのサンプル実装が含まれています。

## ファイル構成

### メインファイル
- **`rowDynamicMultiHeader.js`** - メインコンポーネント
- **`rowDynamicMultiHeaderMockData.js`** - モックデータ生成

### サンプル実装
- **`sampleAlertError.js`** - AlertErrorコンポーネントのサンプル
- **`sampleMessageConstants.js`** - メッセージ定数のサンプル

## Sample1からの移植状況

### ✅ 完全移植（動作確認済み）
- `handleRowSelection` - 行選択処理（効率化修正版）
- `handleSelectFullCheck` - 全選択/全解除処理
- `updateRecord` - レコード更新処理
- `getSavingDatas` - 保存データ取得（変数名修正版）

### 🔄 移植済み（外部依存あり）
- `checkSelectedRows` - 行選択バリデーション
- `handleRecordEditClick` - レコード編集モーダル

## サンプル実装の使用方法

### 1. AlertError サンプルを使用する場合

```javascript
// rowDynamicMultiHeader.js に追加
import SampleAlertError from './sampleAlertError';
import { YUSGS5015C_E, YUSGS5016C_E } from './sampleMessageConstants';

// checkSelectedRows メソッドで使用
async checkSelectedRows() {
  if (this.selectedRows.length > 1) {
    const result = await SampleAlertError.open({
      size: "small",
      message: YUSGS5016C_E,
      code: "YUSGS5016C-E"
    });
    return result;
  } else if (this.selectedRows.length === 0) {
    const result = await SampleAlertError.open({
      size: "small",
      message: YUSGS5015C_E,
      code: "YUSGS5015C-E"
    });
    return result;
  }
  return "";
}
```

### 2. 実際のプロジェクトで使用する場合

```javascript
// 既存のコンポーネントとメッセージ定数をインポート
import { YUSGS5015C_E, YUSGS5016C_E } from "c/f003GsV0000MsgConst";
import AlertError from "c/f003GsV0000AlertError";

// Sample1と同じ実装で動作
async checkSelectedRows() {
  if (this.selectedRows.length > 1) {
    const result = await AlertError.open({
      size: "small",
      message: YUSGS5016C_E,
      code: "YUSGS5016C-E"
    });
    return result;
  } else if (this.selectedRows.length === 0) {
    const result = await AlertError.open({
      size: "small",
      message: YUSGS5015C_E,
      code: "YUSGS5015C-E"
    });
    return result;
  }
  return "";
}
```

## メッセージ内容

### YUSGS5015C_E（0件選択エラー）
「操作対象の行が選択されていません。1行選択してから操作してください。」

### YUSGS5016C_E（複数選択エラー）
「複数の行が選択されています。操作は1行のみ選択して実行してください。」

## 注意事項

1. **サンプル実装は開発・テスト用**です
2. **本番環境では既存のコンポーネントを使用**してください
3. **メッセージ定数も実際のプロジェクトの定数**を使用してください
4. **ModalViewコンポーネントも同様に実装が必要**です

## 次のステップ

1. 実際のプロジェクトでAlertError・ModalViewコンポーネントを確認
2. 適切なインポート文に変更
3. メッセージ定数の実際のパスを確認・修正
4. テスト実行して動作確認