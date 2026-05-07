# 04. 現行 Java 資産の解析（レガシー）

> **本ドキュメントの責務**: 旧 IBM WACS / Crafts! 基盤に存在する現行 Java クラス `RLRRG004_B01_U06.java` の構造・改訂履歴・処理フローを整理し、新方式（[02_new_implementation.md](02_new_implementation.md)）との差分を明らかにする。
> **隣接ドキュメント**: 案件背景は [01_overview.md](01_overview.md)、新方式アーキテクチャは [../../設計ルール/アーキテクチャ.md](../../設計ルール/アーキテクチャ.md) を参照。

## 既存資産（レガシー Java クラス）

現行実装として以下の Java ソースが存在する。

| 項目 | 値 |
| --- | --- |
| ファイル名 | `RLRRG004_B01_U06.java` |
| パッケージ | `jp.co.btm.irl.rlr.rg004` |
| 親クラス | `com.ibm.jp.wacs.CraftsTransaction` |
| 役割 | 計数画面−補正値登録処理（計数情報画面の補正値登録） |

## 改訂履歴

| 日付 | 担当 | 変更理由 |
|---|---|---|
| 2002/12/06 | M.Nitami | 新規作成 |
| 2009/06/23 | R.Matsumura | 【Day2.1】融資管理システム・Crafts! 対応（GEC20-C-059）— **規定担保補正値の設定追加**（`F_HIKIATE_KITEITI_TOT` / `F_HIKIATE_JIKA_TOT`） |
| 2010/02/04 | R.Matsumura | 貸外逆集約対応（変更管理）（GEC21-C-025）— **店 CIF の取得元を移管後データに変更**（`getSeverTenban()` を介した 3 桁 → 7 桁変換、`F_BRNO_IKNATO` / `F_TRISKNO_IKNATO` を使用） |

## 現行処理フロー

1. 入力データビーン (`ibean`) と出力データビーン (`obean`) を取得。
2. DB 接続インスタンスをオートコミット OFF で取得（`connect(false)`）。
3. 禀議業務共通クラス `RLRRGCOM_RINGI` で共有情報（`hstComBasket`）を初期化。
4. 操作者ユーザ ID を `WACSUser` 経由で取得し共有情報に格納。
5. 移管後の取引先貸外店番を `RLTCF001_004_R01.getSeverTenban()` で 3 桁 → 7 桁変換。
6. 補正値 4 つを `ibean.getStringArray(F_HOSCH)` で配列受け取り、補正理由を `F_HOSRSN` で取得し共有情報に設定。
7. 規定担保補正値（規定値 / 時価ベース）を `F_HIKIATE_KITEITI_TOT` / `F_HIKIATE_JIKA_TOT` で配列受け取り共有情報に設定。
8. 計数共通 DB クラス `RLRRG004_B01_DB.setHoseichi(hstComBasket)` で永続化。
9. 出力データに成功フラグ `V_TRUE` を設定。
10. `dbcon.commit()` でコミット。
11. 例外発生時（`WACSApplException` / `WACSDBException` / `WACSSysException`）は `dbcon.rollback()` 後に再送出。
12. `finally` で `dbcon.close()`。

## 現行と新方式の差分

現行 Java と新方式アーキ説明の対比から差分が読み取れる。

| 観点 | 現行 | 新方式 |
|---|---|---|
| プラットフォーム | IBM WACS / Crafts! | Java + MyBatis + JAX-RS（`jp/mufg/bk/yus`） |
| DB アクセス | `CraftsDBConnector` 直接操作（接続・コミット・ロールバックをサービス内で記述） | MyBatis + Repository パターン（`Service` で宣言的トランザクション境界） |
| データ受け渡し | `Hashtable`（`hstComBasket` / `hstKey` 等、型安全性なし） | POJO / DTO / Entity（Bean Validation 併用） |
| 層分離 | サービスクラス内で DB 接続・ビジネス・例外処理を全部実施 | プレゼンテーション / ドメイン / インフラの 3 層分離 |
| トランザクション境界 | サービス内で `commit/rollback` を都度記述 | `Service` クラスで宣言的に設定 |
| 補正値の受け渡し | 配列（`ibean.getStringArray(F_HOSCH)`） | フラットフィールド（Request Body、項目仕様は [03_request_response.md](03_request_response.md) 参照）— ただし整合は [09_open_questions.md](09_open_questions.md) 参照 |
| 自動生成 | なし（手書き） | OpenAPI Generator（`Api` / `Model`）、MyBatis Generator（Table Mapper） |
| 例外処理 | 例外 3 種で同じロールバック処理が重複 | 共通化を方針とする（[../../設計ルール/設計ルール.md](../../設計ルール/設計ルール.md) コーディング品質ルール参照） |
