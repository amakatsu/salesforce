# RLRRG004_B01_U04 分析レポート

> 計数情報画面 — 計数再取得処理（704行）

## クラスの役割・責務

ホスト（メインフレーム）から計数情報を再取得し、DBに登録する処理。画面上の「計数再取得」ボタン押下時に呼ばれる。

## 継承・インタフェース

- 継承: `RLRRGCOM_HOST_BASE`（ホスト連携基底クラス — 他のU系と異なりホスト通信機能を持つ）
- 実装: `IRingiMsg`, `IRingiWF`

## 他クラスへの依存関係

| 依存先 | 変数名 | 用途 |
|--------|--------|------|
| `RLRRG004_B01` | keisuCom | 計数業務共通（ハッシュ間データコピー、科目データ取得、外部管理DBとの結合計算、出力設定） |
| `RLRRG004_B01_DB` | keisuDB | 計数情報のDB操作（全項目取得、新規データ登録） |
| `RLRRGCOM_RINGI` | ringiCom | 禀議業務共通（共有情報初期化、補正区分取得、取引日取得、ホストエラーメッセージID取得、null変換、出力ビーン制御情報設定） |
| `RLRRGCOM_WF` | wfCom | ワークフロー共通（操作者情報取得、案件基本情報取得） |
| `RLRRGCOM_DB` | dbCom | 禀議共通DB（禀議共通2取得、計数要否登録） |
| `RLRRGCOM_PROP_BASE` / `_FACT` / `_RES` | strProp / hsRes | 項目属性管理（ボタン制御・プロテクト・色変リセット） |
| `RLRCMCOM_CalendarWrapper` | Cal | カレンダー（営業日取得、和暦変換） |

## クラスフィールド（39〜101行）

| フィールド | 型 | 値/用途 |
|-----------|-----|---------|
| `dbparam` | `CraftsDBParam` | DBパラメータ |
| `hstComBasket` | `Hashtable` | 共有情報（全Hashtableの親コンテナ） |
| `hstKey` | `Hashtable` | KEY共通領域（案件番号、店CIF、ユーザーID等） |
| `hstWF` | `Hashtable` | ワークフロー領域（操作者情報、案件情報） |
| `hstDB` | `Hashtable` | DB共通領域（計数情報のデータ） |
| `hstHOST` | `Hashtable` | ホスト領域（メインフレームから取得したデータ） |
| `F_PROP_CHANGE_EXECUTE` | `String` | `"rlrPropChangeExecute"` — 属性変更実行フラグ |
| `strReqId` | `String` | `"rlrrg004_b01_u04"` — リクエストID |
| `intBtnCnt` | `int` | `6` — ボタン制御用配列サイズ |
| `strHidukeErrMsg` | `String` | `"入力された日付"` — 日付エラーメッセージ |
| `strMessageID` | `String` | エラーメッセージID格納用 |
| `strMessageText` | `String` | エラーメッセージテキスト格納用 |

## 主要メソッド一覧

| メソッド | 行範囲 | 処理概要 |
|----------|--------|----------|
| `RLRRG004_B01_U04()` | 108〜110 | コンストラクタ（親クラスのsuper()呼出のみ） |
| `checkInput()` | 120〜122 | 入力チェック（常にtrue） |
| `doProcess()` | 135〜695 | メイン処理: ホストから計数取得 → バリデーション → DB登録 → ボタン制御 → 出力設定 |
| `ns(Object)` | 697〜703 | null安全変換ユーティリティ（null→空文字） |

---

## doProcess() 処理フロー詳細

### Step 1: 初期化（138〜202行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 140 | `rc = 0` | 戻り値変数初期化 |
| 143 | `ibean = getInDataBean()` | 画面からの入力データビーン取得（親クラスメソッド） |
| 146 | `obean = getOutDataBean()` | 画面への出力データビーン取得（親クラスメソッド） |
| 149 | `dbcon = connect(false)` | DB接続取得（オートコミットOFF） |
| 150 | `dbparam = getDBParam()` | DBパラメータ取得 |
| 153 | `ringiCom = new RLRRGCOM_RINGI(folder, dbcon, dbparam)` | 禀議業務共通インスタンス生成 |
| 156 | `hstComBasket = ringiCom.initialComBasket(ibean)` | 共有情報（hstComBasket）の生成と初期化。ibeanの内容をK_KEY_DATAに展開 |
| 159 | `strBtn = new String[6]` | ボタン制御用配列（最大6ボタン分） |
| 163 | `strTribi = null` | 基準日（取引日）変数 |
| 167-169 | `hstClnComBasket, hstClnDB, hstClnKey = null` | clone用Hashtable変数（STEP2で追加） |
| 173-178 | ユーザーID取得 → hstKeyに設定 | `folder.getUser().getUserID()` → `hstKey.put(F_USER_ID, strUserId)` |
| 181 | `keisuCom = new RLRRG004_B01(folder, dbcon, dbparam)` | 計数業務共通インスタンス生成 |
| 184 | `keisuDB = new RLRRG004_B01_DB(folder, dbcon, dbparam)` | 計数情報DBインスタンス生成 |
| 190 | `wfCom = new RLRRGCOM_WF(folder, dbcon, dbparam)` | WFインスタンス生成 |
| 193 | `strProp = RLRRGCOM_PROP_FACT.getPropInstance(strReqId)` | 項目属性管理インスタンス取得（リクエストID="rlrrg004_b01_u04"） |
| 197 | `Cal = new RLRCMCOM_CalendarWrapper(folder, dbcon, getDBParam())` | カレンダーインスタンス生成 |
| 202 | `dbCom = new RLRRGCOM_DB(folder, dbcon, dbparam)` | 禀議共通DBインスタンス生成 |

### Step 2: 操作者情報・案件基本情報の取得（210〜240行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 211-214 | `wfCom.getOperatorInfo(hstComBasket)` | ユーザーIDをキーにWFから操作者情報を取得。結果はK_WF_DATAに格納 |
| 218-223 | WFデータからユーザー情報をhstKeyにコピー | `F_USER_ID`, `F_BUTEN_AREA_CD`（部店エリアコード）, `F_KA_GRP_CD`（課・グループコード）, `F_SHOK_JUN`（役職順コード）をhstWF→hstKeyに転写 |
| 229-233 | `wfCom.getAnkenInfo(hstComBasket)` | 案件番号(`F_LC_NO`)と採番(`F_CP_NO`=デフォルト値)をキーに案件基本情報を取得。結果はK_WF_DATAに格納 |
| 237-240 | 移管後の店CIFを取得・保持 | `hstWF.get(F_BRNO)` → `strIkangoBrno`, `hstWF.get(F_TRISKNO)` → `strIkangoTriskno` を変数に保持。hstKeyにも設定 |

**データフロー**:
```
ibean(F_LC_NO) → hstKey → wfCom.getAnkenInfo() → hstWF(F_BRNO, F_TRISKNO) → strIkangoBrno, strIkangoTriskno
```

### Step 3: 取引日（基準日）の決定（247〜295行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 250 | `ibean.containsData(F_LC_NO)` 判定 | 案件番号がibeanに存在するか |
| 254 | `ringiDB = new RLRRGCOM_DB(...)` | 禀議共通DBインスタンス（ローカル変数） |
| 257 | `ringiCom.getHoseiKbn(hstComBasket)` | 補正区分を取得 → K_COM_DATAに格納 |
| 262-263 | `hstKey.put(F_HOSEIKUBUN, hstCom.get(F_HOSEIKUBUN))` | 取得した補正区分をhstKeyに設定 |
| 266 | `ringiDB.getRingishoKgn(hstComBasket)` | 禀議書期限情報から取引日を取得 |
| 278 | `strTribi = ringiCom.cnvNullData(ibean.getString(F_TRIBI))` | ibeanから取引日を取得（null→空文字変換） |
| 279-282 | 取引日が空の場合、営業日を取得 | `strTribi = Cal.getEigyoDay()` |
| 284 | `hstKey.put(F_TRIBI, strTribi)` | 取引日をhstKeyに設定 |
| 288-293 | else分岐: 案件番号なしの場合 | 当日営業日を設定: `strTribi = Cal.getEigyoDay()` |

**取引日の決定ロジック**:
```
if 案件番号あり:
    補正区分を取得 → 禀議書から取引日取得
    if ibeanの取引日が空:
        取引日 = 当日営業日
    else:
        取引日 = ibeanの取引日
else:
    取引日 = 当日営業日
```

### Step 4: ホスト連携 — 計数・利率外照会（299〜324行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 300 | `super.rqstKeisuRiritugaiSyokai(hstComBasket)` | **ホストへの計数・利率外照会リクエスト**。親クラス`RLRRGCOM_HOST_BASE`のメソッド呼出 |
| 302 | `intRc = hstComBasket.get(K_RETURN)` | ホスト呼出の戻り値を取得 |
| 304-324 | エラー判定 | `intRc != IRingiHOST.RC_OK` の場合、エラー処理して return |

**ホスト連携の詳細**:

- **呼出メソッド**: `RLRRGCOM_HOST_BASE.rqstKeisuRiritugaiSyokai(hstComBasket)`
- **リクエストデータ**: hstComBasketのK_KEY_DATAに格納された以下の項目
  - `F_BRNO`（店番号）— 移管後の値
  - `F_TRISKNO`（取引先番号）— 移管後の値
  - `F_TRIBI`（取引日/基準日）
  - `F_USER_ID`, `F_BUTEN_AREA_CD`, `F_KA_GRP_CD`, `F_SHOK_JUN`（操作者情報）
- **レスポンスデータ**: hstComBasketに格納
  - `K_RETURN` — 戻り値コード（`IRingiHOST.RC_OK` = 正常）
  - `K_HOST_DATA` — ホストから取得した計数データ（Hashtable）
  - `K_DETAIL` — エラー詳細コード

**エラーハンドリング（304〜324行）**:
```
if intRc != RC_OK:
    1. DBロールバック
    2. hstHOST から KY_ERROR_MESSAGE を取得
    3. ringiCom.getHostErrorMsgId(K_DETAIL, K_RETURN, true) でメッセージID決定
    4. obean に F_SUCCESS_FLAG=FALSE, F_ERROR_ID, F_ERROR_TYPE=WARNING, F_ERROR_MSG を設定
    5. return（処理終了）
```

### Step 5: ホストデータ → DB用パラメータへの転写（329〜368行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 332-333 | hstKey, hstHOSTを再取得 | `hstComBasket.get(K_KEY_DATA)`, `hstComBasket.get(K_HOST_DATA)` |
| 360 | `keisuCom.setHashToHash(hstHOST, hstKey)` | **ホストデータの全項目をhstKeyにコピー**。hstHOSTの全キーをenumerateし、hstKeyに`put` |
| 366-367 | 移管後の店CIFを再設定 | `hstKey.put(F_BRNO, strIkangoBrno)`, `hstKey.put(F_TRISKNO, strIkangoTriskno)` |
| 368 | `hstComBasket.put(K_KEY_DATA, hstKey)` | 更新したhstKeyを共有情報に書き戻し |

**データフロー**:
```
K_HOST_DATA（ホスト計数データ）→ setHashToHash → K_KEY_DATA（DBパラメータとしてマージ）
                                                   ↑ 店CIFは移管後の値で上書き
```

### Step 6: 外部管理DBとの結合計算 — setHostAndDbData（371〜397行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 375 | `keisuCom.setHostAndDbData(hstComBasket)` | **外部管理DBデータ取得 + 計算の一括実行** |
| 378 | `intRc2 = hstComBasket.get(K_RETURN)` | 戻り値チェック |
| 379-397 | 代表店CIF取得NGの場合エラー | `RC_DAIHYOU_TENCIF_NG` → エラーメッセージ設定 → ロールバック → return |

**setHostAndDbData の内部処理フロー**（RLRRG004_B01クラス、4320行〜）:
```
setHostAndDbData(hstComBasket)
  │
  ├── 1. RLRRG004_B01_DB.getOutsideData(hstComBasket)
  │      ├── 顧客情報テーブル取得（SQL_0501）→ GCIF番号
  │      ├── 代表店CIF取得（RLRTPCOM_DaihyoBrnoCif）
  │      ├── 名寄せ件数取得（SQL_4301）
  │      ├── 銀取計数取得（SQL_4183等）
  │      ├── 取推管理GCIF月次取得（SQL_4051）— 直近+前年
  │      ├── 取推関係先月次取得（SQL_4053）— 直近+前年
  │      ├── 計数情報引当状況取得（SQL_4184）
  │      ├── 一般保証明細取得（SQL_4185）
  │      ├── 自己査定取得（SQL_4186）
  │      ├── 単体財務取得（SQL_4194）— 最大3期分
  │      └── 結果をK_DB_DATAに格納
  │
  ├── 2. ホスト引当データでDB引当データの一部を上書き
  │
  ├── 3. keisuCom.setHashToHash(hstHOST, hstDB)
  │      ホストデータをDBハッシュにコピー
  │
  ├── 4. computeYosin(hstComBasket)
  │      一般与信の補正値適用・合計計算
  │
  ├── 5. computeKokyakuShutoku(hstComBasket)
  │      保全状況の初期計算（商手・裸与信初期値）
  │
  ├── 6. computeKokyaku(hstComBasket)
  │      保全状況の詳細計算（小計・合計・裸与信）
  │
  ├── 7. computeKokyaku2(hstComBasket)
  │      市場性与信の科目明細当月増減額計算
  │
  └── 8. computeHozen(hstComBasket)
         保全率・総合与信・総合信用の計算
```

**エラーハンドリング（379〜397行）**:
```
if intRc2 == RC_DAIHYOU_TENCIF_NG:
    1. K_DETAILからメッセージIDを取得
    2. obean に F_SUCCESS_FLAG=FALSE, エラー情報を設定
    3. DBロールバック
    4. return（処理終了）
```

### Step 7: バリデーション — オーバーフロー・日付チェック（399〜438行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 402 | `rc = keisuCom.checkOverFlow(hstComBasket)` | オーバーフロー・日付整合性チェック |
| 404-418 | `rc == -1` の場合: 日付入力エラー | `MSG_RRGS1041` を設定、`dbcon.commit()`, return |
| 420-438 | `rc == -2` の場合: コメントアウト済み | 計数再取得時はオーバーフローチェックを行わない（2003/04/21削除） |

**checkOverFlow の検証内容**（RLRRG004_B01クラス、3936〜4318行）:
- **日付チェック（rc=-1）**: 経営指標のYYMM形式の妥当性検証。決算期の年月が不正な場合にエラー
- **金額オーバーフロー（rc=-2）**: 金額が9桁超のチェック。ただし計数再取得時はこのチェックをスキップ（コメントアウト）

### Step 8: 計数情報のDB登録（441〜500行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 445-449 | DB登録用パラメータの設定 | `hstKey.put(F_LC_NO, ibean.getString(F_LC_NO))`, `hstKey.put(F_BRNO, ibean.getString(F_BRNO))`, `hstKey.put(F_TRISKNO, ibean.getString(F_TRISKNO))` ※ここでは移管前の店CIFを使用（DB登録キーとして） |
| 452-453 | `keisuCom.setHashToHash(K_DB_DATA, hstKey)` | K_DB_DATA（計算済みデータ）の全項目をhstKeyにコピー。DB登録パラメータとしてマージ |
| 458-468 | **計数案件番号の取得（1回目のgetRingiKyotsu2）** | hstComBasketのcloneを作成 → `F_LC_NO`（入力の案件番号）+ `F_HOSEIKUBUN`=補正前 でRingiKyotsu2を検索 → `F_KEISU_LC_NO`（計数案件番号）を取得 |
| 472-480 | **取引日の取得（2回目のgetRingiKyotsu2）** | 取得した計数案件番号 + 補正前 で再度RingiKyotsu2を検索 → `F_TRIBI`（取引日）を取得 |
| 483-492 | 基準日(F_MKBI)の決定 | 取引日が空の場合 → 当日営業日 `Cal.getEigyoDay()` |
| 493 | `hstKey.put(F_MKBI, strTribi)` | 基準日をhstKeyに設定 |
| 496 | `hstKey.put(F_RSNO, ibean.getString(F_RSNO))` | 禀査番号をhstKeyに設定 |
| 499-500 | `keisuDB.setNewData(hstComBasket)` | **計数情報をDBに新規登録**。hstKeyに設定された全パラメータを使ってINSERT/UPDATE実行 |

**getRingiKyotsu2 の2回呼び出しの理由**:
```
1回目: 入力の案件番号 → 計数案件番号を取得（F_KEISU_LC_NO）
2回目: 計数案件番号 → その案件の取引日を取得（F_TRIBI）
       → 取引日があればそれを基準日に、なければ営業日を基準日に
```

### Step 9: 計数取得要否フラグの更新（503〜512行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 505-509 | パラメータ設定 | `hstKey.put(F_LC_NO, ibean.getString(F_LC_NO))`, `hstKey.put(F_KESR, V_KESR_YO)` — 計数取得要否="要" |
| 511 | `dbCom.setKeisuYohi(hstComBasket)` | **計数取得要否フラグを"要"に更新**。この更新により、計数が取得済みであることをシステムが認識する |

### Step 10: 色変情報リセット・再取得（514〜543行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 519 | `hstKey.put(F_LC_NO, ibean.getString(F_LC_NO))` | 案件番号を再設定（前ステップで変更されている可能性があるため） |
| 527 | `hstComBasket.put(K_KEY_DATA, hstKey)` | 更新したhstKeyを共有情報に書き戻し |
| 530 | `keisuDB.getAllData(hstComBasket)` | **計数情報の全項目を再取得**。DB登録後の最新データを取得して画面表示用とする |
| 535-542 | 基準日の和暦変換 | `hstDB.get(F_MKBI)` → `Cal.getYearMonthDayWareki(strTribi, "", GGG_GENGO)` で和暦形式に変換 → `hstDB.put(F_MKBI, strTribi)` |
| 546 | `strProp.setAllDefaultColor()` | 全項目の色をデフォルトにリセット |

**getAllDataの目的**: setNewDataでDB登録した直後に再取得するのは、DB上の正規化された値（トリガー等で変換された値含む）を画面に反映するため。

### Step 11: 出力データ設定（549〜553行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 552 | `keisuCom.getKamokuData(hstComBasket)` | 科目名称の固定ラベル設定（貸付金・割引合計、外為与信等のラベル配列をDBの科目名称とマージ） |
| 553 | `keisuCom.setOutData(ibean, obean, hstComBasket)` | 出力データ設定。ibeanの全キーをobeanにコピーし、K_DB_DATAの計算結果で上書き。店番7桁→3桁変換、保全率金額単位の全角トリム含む |

### Step 12: ボタン制御（589〜650行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 595-599 | 直近計数照会ボタンの制御 | `hstDB.get(F_CKKKNKEISU_LC_NO)` が null or 空 → `strBtn[intNo++] = B_CKKEISUINQ` でプロテクト対象に追加 |
| 643 | `strProp.setProtect(strBtn)` | 指定ボタンをプロテクト（使用不可に） |
| 647-650 | 制御情報の出力設定 | `strProp.getPropTables()` → `ringiCom.getOutDataBeanPropRes(obean, hsRes, strFlg)` で出力ビーンにボタン制御情報を設定 |

### Step 13: コミット・モード設定（652〜655行）

| 行 | 処理 | 詳細 |
|----|------|------|
| 653 | `obean.setString(F_UPDATE_MODE_FLG, V_UPDATE_KOUSIN_MODE)` | 更新モードを"更新"に設定（画面に更新可能状態を通知） |
| 655 | `dbcon.commit()` | トランザクションをコミット |

### Step 14: 例外処理（657〜693行）

| 例外 | 行範囲 | ログメッセージ | 処理 |
|------|--------|---------------|------|
| `WACSApplException` | 657〜665 | `MSG_SKKS0105` | ロールバック → rethrow |
| `WACSDBException` | 667〜676 | `MSG_SKKS0104` | ロールバック → rethrow |
| `WACSSysException` | 678〜687 | `MSG_SKKS0104` | ロールバック → rethrow |
| finally | 689〜693 | — | `dbcon.close()` |

---

## DB操作の詳細フロー

### 全体のDB操作シーケンス

```
1. ringiCom.initialComBasket(ibean)          … 共有情報初期化
2. wfCom.getOperatorInfo(hstComBasket)       … 操作者情報取得（WF系DB READ）
3. wfCom.getAnkenInfo(hstComBasket)          … 案件基本情報取得（WF系DB READ）
4. ringiCom.getHoseiKbn(hstComBasket)        … 補正区分取得（禀議DB READ）
5. ringiDB.getRingishoKgn(hstComBasket)      … 禀議書期限取得（禀議DB READ）
6. [ホスト連携]                                … メインフレーム照会
7. keisuCom.setHostAndDbData(hstComBasket)   … 外部管理DB READ + 計算
8. keisuCom.checkOverFlow(hstComBasket)      … バリデーション
9. keisuDB.setNewData(hstComBasket)          … 計数情報 INSERT/UPDATE
10. dbCom.getRingiKyotsu2(hstClnComBasket)   … 計数案件番号取得（READ×2回）
11. dbCom.setKeisuYohi(hstComBasket)         … 計数要否フラグ UPDATE
12. keisuDB.getAllData(hstComBasket)          … 計数情報 全項目 READ（出力用）
13. dbcon.commit()                            … コミット
```

### getRingiKyotsu2 の2段階取得

**1回目（465行）**: 入力の案件番号で禀議共通2を検索
- キー: `F_LC_NO` = ibeanの案件番号, `F_HOSEIKUBUN` = 補正前(V_HOSEI_MAE)
- 取得値: `F_KEISU_LC_NO`（計数案件番号）

**2回目（477行）**: 計数案件番号で禀議共通2を再検索
- キー: `F_LC_NO` = 1回目で取得した計数案件番号, `F_HOSEIKUBUN` = 補正前
- 取得値: `F_TRIBI`（取引日）→ 基準日(F_MKBI)として使用

### setKeisuYohi の更新内容

- キー: `F_LC_NO` = ibeanの案件番号
- 更新値: `F_KESR` = `V_KESR_YO`（"要"）
- 目的: 計数取得済みフラグを"要"に更新し、システムが計数情報が取得済みであることを認識できるようにする

---

## 変数のデータフロー

### Hashtable間のデータの流れ

```
ibean（画面入力）
  │
  ├──→ ringiCom.initialComBasket(ibean)
  │       └──→ hstComBasket 生成
  │               ├── K_KEY_DATA  (hstKey)   … 案件番号、店CIF、ユーザーID等
  │               ├── K_WF_DATA   (hstWF)    … WF操作者情報、案件情報
  │               ├── K_HOST_DATA (hstHOST)  … ホストから取得した計数データ
  │               ├── K_DB_DATA   (hstDB)    … DB計数情報（計算結果含む）
  │               ├── K_COM_DATA  (hstCom)   … 補正区分等
  │               ├── K_RETURN               … 戻り値コード
  │               └── K_DETAIL               … エラー詳細コード
  │
  ├──→ wfCom.getOperatorInfo() → K_WF_DATA にユーザー情報格納
  │       └──→ hstWF → hstKey にコピー（F_BUTEN_AREA_CD等）
  │
  ├──→ wfCom.getAnkenInfo() → K_WF_DATA に案件情報格納
  │       └──→ hstWF(F_BRNO, F_TRISKNO) → strIkangoBrno, strIkangoTriskno（移管後店CIF）
  │
  ├──→ rqstKeisuRiritugaiSyokai() → K_HOST_DATA にホスト計数データ格納
  │
  ├──→ setHashToHash(hstHOST, hstKey)  … ホストデータ → hstKey に全コピー
  │
  ├──→ setHostAndDbData()
  │       ├── getOutsideData() → K_DB_DATA に外部管理DBデータ格納
  │       ├── ホストデータで引当項目を上書き
  │       ├── computeYosin()         → K_DB_DATA 更新（一般与信計算結果）
  │       ├── computeKokyakuShutoku() → K_DB_DATA 更新（保全状況初期値）
  │       ├── computeKokyaku()       → K_DB_DATA 更新（保全状況合計）
  │       ├── computeKokyaku2()      → K_DB_DATA 更新（市場性与信増減額）
  │       └── computeHozen()         → K_DB_DATA 更新（保全率）
  │
  ├──→ setHashToHash(K_DB_DATA, hstKey) … 計算済みデータ → hstKey に全コピー
  │
  ├──→ keisuDB.setNewData() … hstKey のデータでDB INSERT/UPDATE
  │
  ├──→ keisuDB.getAllData() → K_DB_DATA に最新DBデータ再取得
  │
  └──→ setOutData(ibean, obean, hstComBasket) → obean に出力データ設定
```

### 店CIFの使い分け

| 場面 | 使用する店CIF | 理由 |
|------|-------------|------|
| ホスト連携（Step 4） | 移管後（strIkangoBrno） | ホストは移管後のCIFを使用 |
| 外部管理DB取得（Step 6） | 移管後（strIkangoBrno） | Step 5で再設定済み |
| DB登録（Step 8） | 移管前（ibean.getString） | DB登録キーは移管前のCIF |
| 計数案件番号取得（Step 8） | 移管前（ibean.getString） | 案件管理は移管前のCIF |

---

## 設計上の特徴

- 5ファイル中唯一 `RLRRGCOM_HOST_BASE` を継承しており、ホスト連携（メインフレーム通信）機能を持つ
- 依存クラスが最も多く、処理フローも最長（ホスト通信→外部DB結合→計算→DB登録→再取得→ボタン制御→出力）
- 移管対応（2003年）で店CIFの使い分けが必要（ホスト向け=移管後、DB向け=移管前）
- getRingiKyotsu2の2段階呼び出し: 「入力案件番号→計数案件番号→取引日」の間接参照パターン
- setNewData後にgetAllDataで再取得するのは、DB正規化後の値を画面に反映するため
- 計数再取得時はオーバーフローチェック（rc=-2）をスキップ（2003/04/21で削除）
- STEP2修正は後にGEC15-C-080-214で打ち消されており、ボタン制御はシンプル化されている（直近計数照会ボタンのみ制御）
