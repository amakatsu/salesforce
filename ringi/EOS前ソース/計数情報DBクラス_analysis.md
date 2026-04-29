# RLRRG004_B01_DB.java 分析レポート

## 基本情報

| 項目 | 内容 |
|------|------|
| ファイル名 | RLRRG004_B01_DB.java |
| パッケージ | jp.co.btm.irl.rlr.rg004 |
| 総行数 | 4310行（末尾欠損あり） |
| 親クラス | RLRRGCOM_DB（禀議共通DBクラス） |
| 実装インタフェース | IRingi, IRingiDB, IRingiItem, IRingiItemKeisu, IRLRCICOM_GCIFConst, IRingiMsg |

## クラスの役割・責務

**計数情報のDBアクセス処理を一手に担うデータアクセスクラス。**

融資禀議・個人ローンBPR（電子禀議）における計数情報のCRUD操作を提供する。具体的には：

- 禀議書の計数情報（一般与信状況、引当状況、経営指標、取引採算等）の全項目取得
- 計数情報の全項目更新（登録処理）
- 外部管理テーブル（顧客情報、銀取計数、取推管理、単体財務等）からのデータ取得
- 補正値の登録（UPDATE or INSERT）

## 依存関係

### import（外部依存）

| カテゴリ | クラス | 用途 |
|----------|--------|------|
| WACS基盤 | CraftsTrxFolder, CraftsDBConnector, CraftsDBParam, CraftsDBResult | DB接続・操作基盤 |
| WACS例外 | WACSSysException, WACSApplException | 例外処理 |
| WACS認証 | WACSUser | ユーザーID取得 |
| 禀議共通 | IRingi, IRingiDB, IRingiItem, IRingiMsg | インタフェース定数 |
| 計数項目 | IRingiItemKeisu | 計数情報のフィールド名定数 |
| 検討会項目 | IRingiItemKentoukai | 検討会関連定数 |
| 禀議共通DB | RLRRGCOM_DB（親クラス） | 共通DB操作メソッド |
| 代表店CIF | RLRTPCOM_DaihyoBrnoCif | 管理顧客代表店CIF取得 |
| カレンダー | RLRCMCOM_CalendarWrapper | 営業日取得 |
| 店CIF | RLRCMCOM_TenCIFWrapper | 担当情報取得 |
| 共通機能 | RLTCF001_001_R02, RLTCF001_003_R01 | 店CIF結果、日付ユーティリティ |
| GCIF | IRLRCICOM_GCIFConst, RLRCICOM_GCIFfromAttr | 顧客GCIF関連 |
| 計数共通 | RLRRG004_B01 | 配列順序変換（chgYosinDispToDb）等 |

### メソッド呼び出し先

- **RLRRG004_B01**: `chgYosinDispToDb()` — 表示順⇔DB順の配列変換
- **RLRTPCOM_DaihyoBrnoCif**: `getDaihyoBrnoCif()` — 代表店CIF取得
- **RLRCMCOM_CalendarWrapper**: `getEigyoDay()` — 当日営業日取得
- **RLRCMCOM_TenCIFWrapper**: `getTantoInfo()` — 担当情報取得
- **RLTCF001_003_R01**: `addMonthR()` — 月数加算
- **RLRCICOM_GCIFfromAttr**: GCIF情報取得（getOutsideData内で使用）
- **親クラス RLRRGCOM_DB**: `setParamKeisu()`, `setParamSonota()`, `checkAndInsert()` 等

## 主要メソッド一覧

### 1. コンストラクタ（1016行）

```
public RLRRG004_B01_DB(CraftsTrxFolder folder, CraftsDBConnector dbcon, CraftsDBParam dbparam)
```

親クラス `RLRRGCOM_DB` のコンストラクタを呼び出すのみ。

### 2. getAllData（1033〜2727行）— 全項目取得（READ）

**処理概要**: 禀議書・査定書の計数情報全項目をDBから取得し、Hashtable（hstComBasket）に格納する。

**パラメータ**: 案件番号（LC_NO）、補正区分（HOSEIKUBUN）

**SQL実行**:

| SQL ID | 操作 | 対象データ |
|--------|------|-----------|
| SQL_4101 | SELECT | 計数情報（メイン）、その他項目、経営指標、市場性与信、参考計数、自己査定、主要行取引、取引採算、引当状況 |
| SQL_4102 | SELECT | 計数情報（一般与信状況明細） |
| SQL_4103 | SELECT | 計数情報（保証人） |
| SQL_4104 | SELECT | 計数情報（限度算入与信状況） |
| SQL_4105 | SELECT | 計数情報（為替予約残高推移月別明細） |
| SQL_4121〜4138 | UPDATE | ※ getAllData内でも更新あり（新規データ挿入ロジック含む） |

**特記事項**:
- 取得できない場合は `RC_DATA_NOT_FOUND` を返却
- 取得データは `hstDB`（Hashtable）に `put` で格納（数百項目）
- 一般与信明細は配列形式で格納（分類コード、科目、期日、利率、面残等）
- 引当状況は規定値・時価ベースの2系統あり（各38〜39項目）
- 保全率計算結果データの取得も含む

### 3. setAllData（2729〜3013行）— 全項目更新（UPDATE）

**処理概要**: 画面で入力された計数情報をDBに登録（更新）する。

**パラメータ**: 案件番号（LC_NO）、補正区分は "1"（補正後）固定

**SQL実行**:

| SQL ID | 操作 | 対象データ |
|--------|------|-----------|
| SQL_4151 | UPDATE | 計数情報（メイン） |
| SQL_4152 | UPDATE | 計数情報（その他項目） |
| SQL_4121〜4138 | UPDATE | 一般与信状況明細（行単位、最大18行×複数項目） |
| SQL_4154 | UPDATE | 限度算入与信状況 |
| SQL_4155 | UPDATE | 保証人 |
| SQL_4156 | UPDATE | 為替予約残高推移月別明細 |
| SQL_4157 | UPDATE | 引当状況（規定値） |
| SQL_4158 | UPDATE | 引当状況（時価ベース） |
| SQL_4160 | UPDATE | 市場性与信引当状況 |
| SQL_4162 | UPDATE | 参考計数 |
| SQL_4163 | UPDATE | 保全率計算結果 |
| SQL_4164 | UPDATE | プロパーローン情報 |

**特記事項**:
- 更新失敗時（戻り値0）は `WACSApplException` をスロー
- 一般与信明細は行ごとにUPDATE実行（ループ処理）
- 配列データは `RLRRG004_B01.chgYosinDispToDb()` で表示順→DB順に変換
- `checkAndInsert()` で行数不足時に自動INSERT

### 4. getOutsideData（3015〜4231行）— 外部管理DB取得（READ）

**処理概要**: 禀議書作成に必要な外部管理テーブル（顧客系・銀取系・取推系・単体財務系）からデータを取得する。

**パラメータ**: 店番号（BRNO）、取引先番号（TRISKNO）、金額単位

**SQL実行**:

| SQL ID | 操作 | 対象データ |
|--------|------|-----------|
| SQL_0501 | SELECT | 顧客情報テーブル（GCIF番号取得） |
| SQL_4301 | SELECT | 名寄せ件数テーブル |
| SQL_4181 | SELECT | 銀取計数（総借入）※コメントアウト |
| SQL_4182 | SELECT | 銀取計数（当行）※コメントアウト |
| SQL_4183 | SELECT | 銀取計数（上位3行）月計数 |
| SQL_4056 | SELECT | データ保有最終月テーブル |
| SQL_4051 | SELECT | 取推管理顧客GCIF月次（直近・前年） |
| SQL_4053 | SELECT | 取推関係先月次（直近・前年） |
| SQL_4184 | SELECT | 計数情報引当状況テーブル |
| SQL_4185 | SELECT | 一般保証明細テーブル |
| SQL_4186 | SELECT | 自己査定テーブル |
| SQL_4194 | SELECT | 単体財務テーブル（決算期取得） |

**特記事項**:
- 代表店CIF取得失敗時は `RC_DAIHYOU_TENCIF_NG` を返却
- 取推データは直近6ヶ月+前年同期の2系統を取得
- 表示月(FROM/TO)はデータ保有最終月から動的に計算
- 銀取データの一部SQL（SQL_4181, SQL_4182）はコメントアウト済み
- 単体財務は最大3期分の決算期データを取得
- 有利子負債の算出（短期借入金、割引手形等）も含む
- 組織店番・店名の取得（10文字以内に切り詰め）

### 5. setHoseichi（4233〜4310行）— 補正値登録（UPDATE/INSERT）

**処理概要**: 一般与信の補正値（4項目）と規定担保補正値を登録する。

**パラメータ**: 店番号（BRNO）、取引先番号（TRISKNO）

**SQL実行**:

| SQL ID | 操作 | 対象データ |
|--------|------|-----------|
| SQL_4173 | SELECT FOR UPDATE | 排他ロック取得 |
| SQL_4171 | UPDATE | 補正値の更新 |
| SQL_4172 | INSERT | 補正値の新規挿入（UPDATE対象なしの場合） |

**特記事項**:
- SELECT FOR UPDATE による排他制御あり
- UPSERT パターン（UPDATE → 0件なら INSERT）
- 補正値は4種類: 一般与信合計、内円貨、貿易合計、支承合計
- 規定担保補正値（規定値・時価ベース）も登録（GEC20-C-059で追加）

## DB操作サマリ

### 使用SQL ID一覧（49個）

| 操作 | SQL ID |
|------|--------|
| SELECT | SQL_0501, SQL_4051, SQL_4053, SQL_4056, SQL_4101〜4105, SQL_4181〜4186, SQL_4194, SQL_4301 |
| UPDATE | SQL_4121〜4138, SQL_4151〜4158, SQL_4160, SQL_4162〜4164, SQL_4171 |
| INSERT | SQL_4172 |
| SELECT FOR UPDATE | SQL_4173 |

### CRUD種別分布

| 操作 | 件数 | 主な用途 |
|------|------|----------|
| Read (SELECT) | 17 | 計数情報取得、外部管理テーブル参照 |
| Update (UPDATE) | 30 | 計数情報更新、一般与信明細更新 |
| Create (INSERT) | 1 | 補正値新規登録 |
| 排他 (SELECT FOR UPDATE) | 1 | 補正値更新時の排他制御 |

## ビジネスロジック概要

1. **計数情報管理**: 融資禀議書に付随する計数情報（一般与信状況、引当状況、取引採算等）の取得・更新を行う
2. **補正値管理**: ユーザーが入力した補正値（一般与信の修正値）を登録する。UPSERT方式で排他制御あり
3. **外部データ連携**: 顧客情報、銀取計数、取推管理、単体財務決算分析等の外部管理テーブルから関連データを収集
4. **引当状況**: 規定値ベースと時価ベースの2系統で管理。各38〜39項目
5. **取推管理**: 直近6ヶ月+前年同期データの2系統を取得。データ保有最終月から表示期間を動的算出
6. **金額単位変換**: ホストから取得した金額単位文言をコードに変換
7. **配列データの順序変換**: 表示順とDB順の相互変換（RLRRG004_B01.chgYosinDispToDb）

## クラス定数（主要なもの）

| 定数 | 値 | 用途 |
|------|----|------|
| intHikiateTotNum | 3 | 引当状況合計数（GEC20-C-059で2→3に変更） |
| intHikiateNum | 39 | 引当状況項目数（YC20218-02で38→39に変更） |
| SQL_CODE_2023 | "rlskk_o2023" | 金額単位取得用SQL |

## 末尾欠損について

ファイルは4310行の `setHoseichi` メソッドの最後で終了している。`setHoseichi` メソッド自体は正常に閉じているが、**クラスの閉じ括弧 `}` が存在しない**。

推定される欠損内容：
- クラスの閉じ括弧 `}`
- 可能性として、追加のprivateヘルパーメソッド（`ns()`, `nsa()`, `no()` 等のnullセーフユーティリティ）が存在していた可能性あり（ただしこれらは親クラス `RLRRGCOM_DB` で定義されている可能性が高い）

## 改修履歴（主要なもの）

| 年月 | 担当者 | 改修内容 | 管理番号 |
|------|--------|----------|----------|
| 2002/12 | M.Nitami | 新規作成 | - |
| 2003/03 | S.Seimura | 代表店CIF例外処理追加 | - |
| 2004/02 | S.Seimura | 銀取レベルアップ | GEC15-C-080-215 |
| 2005/02 | M.Kudo | 引当項目追加（KYKHSHO等） | GEC16-C-143-005 |
| 2007/02 | M.Kawano | にゅーとん対応（資金調達運用表追加） | GEC18-C-014 |
| 2009/06 | R.Matsumura | Day2.1対応（規定担保補正値追加） | GEC20-C-059 |
| 2011/11 | M.Hayashi | 保全率表示機能追加 | GEC23-C-051 |
| 2012/03 | Y.Sato | 総合与信・総合正味追加 | GEC23-C-078 |
| 不明 | - | プロパーローン情報追加 | YC20218-02 |
| 不明 | - | 禀査番号対応 | GEC294-C-004 |
