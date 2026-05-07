# 03. Request / Response Schema

> **本ドキュメントの責務**: 本 API のリクエスト・レスポンスの項目定義とバリデーション仕様を整理する。
> **隣接ドキュメント**: 受信した値を内部でどう扱うかは [02_new_implementation.md](02_new_implementation.md)、入力チェックの実施場所は [../../設計ルール/設計ルール.md](../../設計ルール/設計ルール.md) を参照。

## Request Body

`Content-Type: application/json`。**required** マークが付与された項目のみ NotNull バリデーションが必須。

| 物理名 | 型 | required | バリデーション | 論理名 |
| --- | --- | --- | --- | --- |
| `brNo` | string | ✓ | NotNull、`[0-9]{3}` | 店番 |
| `cmNo` | string | ✓ | NotNull、`[0-9]{7}` | 取引先番号 |
| `loanDiscTotalCorrectionValue` | int32 | – | PositiveOrZero、整数 7 桁 | 貸付金・割引合計（補正値） |
| `internalJpyCorrectionValue` | int32 | – | PositiveOrZero、整数 7 桁 | 内円貨（補正値） |
| `forexCreditTotalCorrectionValue` | int32 | – | PositiveOrZero、整数 7 桁 | 外為与信合計（補正値） |
| `shiShoTotalCorrectionValue` | int32 | – | PositiveOrZero、整数 7 桁 | 支払承諾合計（補正値） |
| `regulationTanpoCorrectionValueRegulationValue` | int32 | – | PositiveOrZero、整数 7 桁 | 規定担保（規定値）(補正値) |
| `regulationTanpoCorrectionValueJikaBase` | int32 | – | PositiveOrZero、整数 7 桁 | 規定担保（時価ベース）(補正値) |
| `correctionReason` | string | – | ByteLength 0–100 | 補正理由 |
| `lockInfo` | object (LockInfo) | ✓ | （ネスト） | 排他ロック情報 |
| `lockInfo.exclusiveKey` | string | ✓ | `[a-zA-Z0-9]{1,70}` | 排他キー |
| `lockInfo.exclusiveCount` | int32 | ✓ | NotNull、PositiveOrZero | 排他回数 |

### サンプル値（memo.text に記載のある例）

| 物理名 | 例 |
| --- | --- |
| `brNo` | `"010"` |
| `cmNo` | `"9019149"` |
| 各補正値 (int32) | `"1234567"` |
| `correctionReason` | `"〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●〇〇〇〇●"` |
| `exclusiveKey` | `"rkANKEN111111111111"` |
| `exclusiveCount` | `"1"` |

## Response（HTTP 200 成功）

成功時は `lockInfo` のみ返却される。

| 物理名 | 型 | required | 論理名 |
| --- | --- | --- | --- |
| `lockInfo` | object (LockInfo) | ✓ | 排他ロック情報 |
| `lockInfo.exclusiveKey` | string | ✓ | 排他キー |
| `lockInfo.exclusiveCount` | int32 | ✓ | 排他回数 |

## エラー時の挙動

エラー時のレスポンスフォーマットは memo.text に記載なし。詳細は [09_open_questions.md](09_open_questions.md) を参照。

## 注意事項

- 補正値・補正理由・規定担保補正値は `required` ではない。空送信を許容するかどうかの業務要件は memo.text に記載なし → [09_open_questions.md](09_open_questions.md)。
- 更新対象項目名（[02_new_implementation.md](02_new_implementation.md) Step 5）と Request Body 項目名の表記揺れあり → [09_open_questions.md](09_open_questions.md)。
