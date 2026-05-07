# DB アクセス（MyBatis）

> **本ドキュメントの位置付け**: ringi 配下の各機能で共通に従う DB アクセス手段（MyBatis Table Mapper / Query Mapper）と、Table Data Gateway パターン、トランザクション境界、排他制御の方針を規定する汎用設計ルール。
> **隣接ドキュメント**: 配置レイヤは [アーキテクチャ.md](アーキテクチャ.md)、リポジトリパターンは [設計ルール.md](設計ルール.md) を参照。

## ORM 採用方針

| 観点 | 採用 |
|---|---|
| ORM | **MyBatis** |
| パターン | Table Data Gateway |
| 単一テーブル CRUD | **Table Mapper**（MyBatis インターフェース、Dynamic SQL DSL を default method で記述） |
| 結合 SQL / 複雑な参照 | **Query Mapper（XML）** + Query Mapper インターフェース（Dynamic SQL で書けないものに限る） |
| トランザクション境界 | `Service` クラスに宣言 |
| SQL 記述方式 | **MyBatis Dynamic SQL 1.5.x（Java DSL）を第 1 選択**。詳細は次節 |

> **責務分離（SEPARATION）**: MyBatis Mapper は **SQL 実行のみ** を担う。POJO 間の変換（Bean Mapping）を MyBatis Mapper で記述してはならない。Bean Mapping 用途には [設計ルール.md](設計ルール.md) の「層間データ受け渡し」節で規定する **MapStruct** を使用する。

## SQL 記述方式

### 採用方針

| 順位 | 記述方式 | 採用基準 |
|---|---|---|
| **第 1 選択** | **MyBatis Dynamic SQL（Java DSL）** | 単一テーブル CRUD・結合・条件分岐のほとんどをカバー。型安全・コンパイル時検証・IDE リファクタ追従 |
| 第 2 選択（補助） | **XML Mapper** | Dynamic SQL DSL で表現できない高度なクエリのみ（例: ベンダ固有のヒント句、複雑なリカーシブ CTE 等） |
| **禁止** | アノテーション SQL（`@Select` / `@Update` / `@Insert` / `@Delete` / `@SelectProvider` 等で文字列 SQL を直書き） | 静的検査が効かず、テーブル名・カラム名のリネームに追従できない |
| **禁止** | 文字列リテラル SQL（`String sql = "SELECT ..."`、StringBuilder 連結等） | SQL インジェクション・タイプセーフ性喪失 |
| **禁止** | `org.apache.ibatis.session.SqlSession` の直接利用（`session.selectOne(statementId, ...)` 等） | 静的型付けの恩恵が失われる |

### Dynamic SQL を第 1 選択にする理由

1. **型安全**: テーブル・カラムを Java の `SqlTable` / `SqlColumn` で定義するため、リネームはコンパイラが追跡。
2. **静的検査**: 構文エラー・カラム名タイポ・型不整合がコンパイル時に検出される。
3. **IDE リファクタ追従**: フィールド名変更が SQL 側にも自動反映。
4. **可読性**: `where(id, isEqualTo(x))` のような流暢な DSL で SQL の意図が読み取れる。
5. **再利用**: フラグメント（条件節・カラムリスト）を `BasicColumn[]` 等で共有可能。
6. **SEPARATION 強化**: SQL 文字列がコードから消えるため、Mapper で POJO 変換ロジックを混在させる誘惑が減る。

### 実装パターン

- Mapper interface は `org.mybatis.dynamic.sql.util.mybatis3.CommonInsertMapper` / `CommonUpdateMapper` / `CommonSelectMapper` 等の **共通 Mapper をベースとし**、業務メソッドは **`default` メソッド** で Dynamic SQL DSL を組み立てて呼び出す。
- テーブル定義は `org.mybatis.dynamic.sql.SqlTable` を継承した **Table support クラス** に集約する（[コーディング規約.md](コーディング規約.md) の「SQL リテラル禁止」節参照）。
- カラム定数は Table support クラスの `public final SqlColumn<T>` フィールドとして公開し、Mapper / RepositoryImpl からは Table support クラス経由で参照する。

### XML Mapper を採用する場合の判断基準

XML はあくまで **Dynamic SQL で表現できないもの専用** とする。採用前に以下を確認する。

- [ ] 当該クエリは `SelectDSL` / `UpdateDSL` / `InsertDSL` / `DeleteDSL` で書けないか？（複雑な CASE / JOIN / サブクエリも DSL でほぼ書ける）
- [ ] 書けない場合、ベンダ固有機能の使用が真に必要か？
- [ ] 真に必要な場合、当該機能の `design/09_open_questions.md` に「XML 採用根拠」を記載したか？

上記すべて Yes なら XML 採用可。それ以外は Dynamic SQL で書く。

## DB アクセスパターン

| パターン | 内容 |
| --- | --- |
| Table Data Gateway | 1 テーブルにつき DAO + DTO を 1 つずつ作成。本システムでは Table Mapper（DAO）+ Table Entity（DTO）が該当 |
| 単一テーブル CRUD | Table Mapper インターフェース（MyBatis Generator 自動生成）を介して実行 |
| 結合 SQL | Query Mapper インターフェース + Query Mapper（XML）で対応。XML は手動作成 |
| トランザクション境界 | `Service` クラスに宣言（参照系でも業務要件次第で宣言する場合あり） |

## Mapper（MyBatis 固有のインターフェース）

- Mapper は MyBatis 固有の Java インターフェースであり、Mapper インターフェースを介して SQL を実行する。Mapper インターフェースに定義した 1 つ 1 つのメソッドがそれぞれ SQL に対応する。

### Table Mapper

- 単一テーブルへのアクセスを定義する MyBatis のインターフェース。
- 単一テーブルに対する CRUD を表現するメソッドが定義されており、**MyBatis Generator** という資源自動生成ツールによって生成される。
- Table Mapper インターフェースの実装クラスは、**MyBatis-CDI ライブラリによってアプリケーションの起動時に自動生成** されるため、開発者が作成する必要はない。

### Query Mapper

- DB のデータを取得する際、単一テーブル単位では対応しきれない複雑なデータ取得（複数テーブルを結合・加工）に対応する。
- 結合 SQL に対応するデータを取得するためのもの。厳密には結合 SQL のみではないが、大部分が結合 SQL になるためその前提で記載されている。
- 対応する実装クラスは、MyBatis-CDI により動的に作成されるので個別に開発する必要がない。

### Query Mapper（XML、SQL マップファイル）

- MyBatis でデータベースへのアクセスを定義するための XML ファイル。
- ドメイン層の Query Mapper インターフェースに対応している。結合 SQL が記述されている。
- **MyBatis Generator では自動生成できない** ため、手動作成または自作ツールでの生成が必要。

## Table Data Gateway パターン

- 1 つのテーブルに対して DAO と DTO を 1 つずつ作成し、対象テーブルへのアクセスを抽象化するデザインパターン。
- DAO は対象テーブルの CRUD 操作に対応した振る舞い（メソッド）を持つ。DTO は対象テーブルの 1 レコードに対応する。
- MyBatis は Table Data Gateway パターンを効率的に実現するためのライブラリ。
- 本システムにおいては DAO が **Table Mapper インターフェース**、DTO が **Table Entity** にあたる。
- トランザクションスクリプトパターン（[設計ルール.md](設計ルール.md) 参照）には Table Data Gateway パターンをあわせて利用することが多い。

## トランザクション境界

- トランザクション境界は **原則 `Service` クラスに設ける**。
- データの一貫性を保障する必要がある処理（主にデータの更新処理）を行う業務ロジックの場合、トランザクション境界を宣言する。
- データの参照処理の場合でも業務要件によってはトランザクション管理が必要になる場合があり、その場合も宣言する。

## 排他制御（楽観ロック原則）

### 原則

| 観点 | 方針 |
|---|---|
| 採用方式 | **楽観ロック** に統一 |
| 悲観ロック | **禁止**（`FOR UPDATE` / `FOR UPDATE WAIT n` / `SELECT ... LOCK IN SHARE MODE` 等を含む DB 行ロックは新方式では行わない） |
| 集約点 | 共通ライブラリ「**排他制御ヘルパー**」の「排他チェック」に集約。各機能は同ヘルパーを呼出すのみ |
| DB 行ロック独立ステップ | **禁止**。サービスのフローに「排他ロック取得」のみを目的とした独立ステップを置いてはならない |
| 例外的な悲観ロックの採用 | 業務要件として真にやむを得ない場合のみ。**設計レビュー承認** を経たうえで個別判断とし、本ドキュメントの原則を上書きする旨を当該機能の `design/09_open_questions.md`（または相当文書）に明記する |

### 採用根拠

- **インフラ製品依存の排除**: `FOR UPDATE WAIT n` 等は Oracle 固有構文。RDBMS 変更の影響を上位層に漏らさない設計（[アーキテクチャ.md](アーキテクチャ.md) infra 層責務）と整合させるため、DB 製品依存の悲観ロックは採用しない。
- **責務の分離**: 排他制御はビジネスルールの一部であり、DB 製品ではなく **domain 層** で表現する（[アーキテクチャ.md](アーキテクチャ.md) 参照）。
- **共通化と再利用**: 排他制御ヘルパーに集約することで、各機能の Service は排他キー・更新回数を渡すだけで済む。実装重複を排除する（[設計ルール.md](設計ルール.md) コーディング品質ルール参照）。

### 楽観ロックの実装フロー

`Service` クラスで以下を実施する。詳細な実装パターンは [設計ルール.md](設計ルール.md) の「楽観ロック実装パターン」節を参照。

1. リクエストから「排他キー」「排他回数」を取り出す。
2. 共通ライブラリ「排他制御ヘルパー」の「排他チェック」を呼出す。
3. 戻り値（更新後の排他回数）をサービスアウトプット DTO に設定し、後続の更新処理に進む。
4. ヘルパーが投げる例外はそのままクライアントへ返却（握りつぶさない）。

### Mapper 設計への影響

- Table Mapper / Query Mapper のメソッドに `lock` / `lockBy...` / `selectForUpdate` 等の **悲観ロック専用メソッドを定義してはならない**。
- 単純な PK 検索 → 更新 の流れは、`updateByPrimaryKey...`（UPDATE 件数 0 のとき INSERT へフォールバック）で実現する。
