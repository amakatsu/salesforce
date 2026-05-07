# 02. 新規実装内容（処理フローと周辺資産）

> **本ドキュメントの責務**: サービスクラスの処理ステップと、それを実現するために揃える Java 資源を整理する。
> **隣接ドキュメント**: Request / Response の項目仕様は [03_request_response.md](03_request_response.md)、配置レイヤと責務は [../../設計ルール/アーキテクチャ.md](../../設計ルール/アーキテクチャ.md) を参照。

## 処理フロー（全 5 ステップ）

排他制御は **楽観ロックに統一** （[../../設計ルール/DBアクセス.md](../../設計ルール/DBアクセス.md) の「排他制御（楽観ロック原則）」参照）。旧仕様の「対象行の排他ロック取得（`FOR UPDATE WAIT 30`）」ステップは廃止し、5 ステップ構成とする。

### Step 1. インプット取得

引数を取得し、サービスインプット DTO へマッピングする。マッピング仕様は別資料「【map 仕様】サービスインプット」を参照する旨が記載されている。

### Step 2. 排他更新回数チェック（楽観ロック）

共通ライブラリ「排他制御ヘルパー」の「排他チェック」を呼出す。

| 入力 | 値 |
| --- | --- |
| 排他キー | サービスインプット DTO.排他ロック情報.排他キー |
| 更新回数 | サービスインプット DTO.排他ロック情報.排他回数 |
| 戻り値 | 更新後の排他回数 |

- **エラー時**: 共通ライブラリの例外をそのままクライアントへ返却し処理終了。
- **正常時**: 戻り値（更新後排他回数）をサービスアウトプット DTO へ設定し後続処理で使用。

### Step 3. サーバー用店番取得

取引先貸外店番を 3 桁 → 7 桁へ変換する。共通ライブラリ「文字列編集クラス」の「サーバー用店番取得」を呼出す。

| 入力 | 値 |
| --- | --- |
| 店番 | サービスインプット DTO.店番 |
| 戻り値 | サーバー用店番 |

### Step 4. 計数情報(禀議計数補正値) 更新

| 項目 | 値 |
| --- | --- |
| リポジトリ | 計数情報(禀議計数補正値)リポジトリ |
| メソッド | `updateByPrimaryKeyAndDelFlg` |
| 条件 | 店番 / 取引先番号 / 削除フラグ = `"0"`（未削除） |

**更新対象項目**:

| カラム種別 | 項目 |
|---|---|
| 補正値 | 一般与信合計(補正値) |
| 補正値 | 内円貨(補正値) |
| 補正値 | 貿易与信合計(補正値) |
| 補正値 | 支払承諾合計(補正値) |
| 補正理由 | 補正理由 |
| 規定担保補正値 | 規定担保補正値(規定値) |
| 規定担保補正値 | 規定担保補正値(時価ベース) |

- **正常更新時**: 後続処理へ。
- **更新件数 0 件時**: 新規登録 `insertToKeisuHoseichi` を実行（DB 行ロックは取らない。一意制約違反は楽観ロック失敗または並行登録の検出として扱う想定）。

> **整合性の留意**: 本ステップの更新対象項目名と Request Body 項目名（[03_request_response.md](03_request_response.md)）には不整合がある。詳細は [09_open_questions.md](09_open_questions.md) を参照。

### Step 5. サービスアウトプット DTO 生成

- 正常終了時: 「【マップ】サービスアウトプット DTO」に従い生成・返却。
- 例外終了時: アウトプット DTO は生成せず、例外を上位送出。

## 周辺資産（揃える Java 資源）

memo.text のアーキ説明およびディレクトリ構成に基づく、本機能で揃える資源一覧。配置レイヤの詳細は [../../設計ルール/アーキテクチャ.md](../../設計ルール/アーキテクチャ.md) を参照。

| 層 | 資源 | 役割 | 生成方法 |
| --- | --- | --- | --- |
| presentation | `Api` インターフェース | Web API エンドポイント定義（JAX-RS アノテーション付） | OpenAPI Generator 自動生成 |
| presentation | `ApiImpl` | `Api` の実装。HTTP 受付・入力チェック・`ServiceDto` 詰替・レスポンス変換 | 手動実装 |
| presentation | `Model`（Request / Response） | リクエスト/レスポンスを表す POJO。Bean Validation アノテーション付与 | OpenAPI Generator 自動生成 |
| presentation | Bean マッパ | `Model` ↔ `ServiceDto` の変換 | Bean マッピング機能を推奨 |
| domain | `Service` クラス | ビジネスロジック実装、トランザクション境界宣言 | 手動実装 |
| domain | `ServiceInputDto` / `ServiceOutputDto` | プレゼンテーション ↔ ドメイン間のデータ受け渡し POJO（Input / Output 各 1） | 手動実装 |
| domain | `Repository(DB)` インターフェース | DB アクセス抽象化 I/F（依存性逆転） | 手動実装 |
| domain | Table Mapper インターフェース | MyBatis 単一テーブル CRUD I/F | MyBatis Generator 自動生成 |
| domain | Query Mapper インターフェース | MyBatis 結合 SQL 用 I/F | 手動実装（実装クラスは MyBatis-CDI が動的生成） |
| domain | `Entity`（Table / Query） | DB アクセスや API 連携で授受する POJO | MyBatis Generator 自動生成（Table）/ 手動（Query） |
| infra | `RepositoryImpl(DB)` | `Repository(DB)` の実装。MyBatis を介して DB アクセス | 手動実装 |
| infra | Query Mapper (XML) | MyBatis 結合 SQL マップファイル | 手動作成または自作ツール生成 |

> **備考**: 本機能は他システム連携・ホスト連携が無いため、`Repository(API)` / `RepositoryImpl(API)` は本機能スコープ外。
