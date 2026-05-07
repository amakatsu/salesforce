# 09. 殿への確認事項（Open Questions）

> **本ドキュメントの責務**: memo.text に記載がない事項、および記述上の不整合・揺れを集約し、実装着手前に殿の判断を仰ぐ。
> **位置付け**: 推測による補完は行わず、確認すべき項目をすべて挙げる。

## 確認事項一覧

| ID | 観点 | 内容 | 判断根拠が必要な場所 |
|---|---|---|---|
| E-02 | 項目名の不整合 | 更新項目名と Request Body 項目名の不整合（**一般与信合計** vs **貸付金・割引合計**） | [02_new_implementation.md](02_new_implementation.md) Step 5 / [03_request_response.md](03_request_response.md) |
| E-03 | テーブル名表記揺れ | テーブル名表記『**禀議**』vs『**稟議**』が混在 | memo.text 全般 |
| E-04 | データ格納方式 | 規定担保補正値の格納方式（2 行 vs 配列）。新方式 Request Body はフラット 2 フィールド、現行 Java は `getStringArray` で配列受け取り | [03_request_response.md](03_request_response.md) / [04_legacy_analysis.md](04_legacy_analysis.md) |
| E-05 | 必須性 | `correctionReason`（補正理由）の必須性。Request では `required` ではないが業務上の必須性は不明 | [03_request_response.md](03_request_response.md) |
| E-06 | 排他キーの生成主体 | `lockInfo.exclusiveKey` の生成主体（クライアント / サーバー / 共通ライブラリのいずれか） | [02_new_implementation.md](02_new_implementation.md) Step 2 / [03_request_response.md](03_request_response.md) |
| ~~E-07~~ | ~~DB 製品依存~~ | ✅ **解決済（cmd_ringi_013）**: 楽観ロック採用により悲観ロック (`FOR UPDATE WAIT 30`) は廃止。Oracle 固有構文の問題は不要化。詳細は [../../設計ルール/DBアクセス.md](../../設計ルール/DBアクセス.md) の「排他制御（楽観ロック原則）」を参照。 | — |
| E-08 | UI 実装の要否 | 画面（UI）実装の要否。memo.text に記載なし | [01_overview.md](01_overview.md) スコープ |
| E-09 | 別資料の所在不明 | 「【map 仕様】サービスインプット」、「【マップ】サービスアウトプット DTO」の **別資料の所在が不明** | [02_new_implementation.md](02_new_implementation.md) Step 1, Step 6 |

## memo.text に記載なき事項（明示）

- **エラー時のレスポンスフォーマット**: 異常系のレスポンス Schema が memo.text に記載なし（[03_request_response.md](03_request_response.md) 参照）。
- **補正値の空送信許容**: 補正値・補正理由・規定担保補正値は `required` ではないが、空送信時の業務上の扱いは memo.text に記載なし（[03_request_response.md](03_request_response.md) 参照）。
- **入力相関チェック / DB 相関チェック**: 本機能では「なし」と明記されている。これは記載なきものではなく明示的に「なし」である点に留意。

