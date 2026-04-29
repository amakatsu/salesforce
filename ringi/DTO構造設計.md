# DTO構造設計

> 対象: 計数情報マスタ再登録（RgV0501）で使用する全10種のDTO
> 設計原則:
> - 引数DTOはイミュータブル（読み取り専用）
> - ユーザID等はコンテキストから取得（DTOに含めない）
> - **配列の使い分け**:
>   - 禁止: 意味の異なる項目をインデックスで区別する配列（例: [0]=貸付金合計, [1]=内円貨）
>   - 許可: 業務的に同じ構造の繰り返し明細（例: 貸付金明細1〜12 → `List<KashitsukeMeisai>`）
>   - 判断基準: 各要素の意味が同じ構造か？ YES→List OK、NO→個別フィールド
>   - **List要素には必ずキー値（明細番号・種別コード等）を含めること。キーなしの配列は禁止**

---

## 明細用サブDTO定義

### KashitsukeMeisai（貸付金明細）

一般与信の貸付金明細1〜12で共通の構造。キーは科目コード（業務名）。

| フィールド名 | 型 | 説明 |
|---|---|---|
| kamokuCode | String | 科目コード（業務名。例: "tegata_kashitsuke", "shogyou_tegata", "overdraft" 等。現行の科目名F_KMK_RMTに対応） |
| kyodogaku | Long | 極度額 |
| honkengoZandaka | Long | 本件後残高 |
| getsumatsuZandaka | Long | 指定月末残高 |
| jisseiZandaka | Long | 実勢現在残高 |
| tougetsZougen | Long | 当月増減額 |
| bunruiCode | String | 分類コード |
| kamokuName | String | 科目名（表示用） |
| kijitsu | String | 期日 |
| riritsu | String | 利率 |
| hoseiValue | Long | 補正値 |
| rinsaNo | String | 禀査番号 |

### ShijoKamokuMeisai（市場性与信科目明細）

市場性与信の科目明細1〜10で共通の構造。キーは科目コード。

| フィールド名 | 型 | 説明 |
|---|---|---|
| kamokuCode | String | 科目コード（業務名。現行のF_MEND_ZAN_1〜10に対応する市場性与信の科目種別） |
| getsumatsuZandaka | Long | 指定月末残高 |
| kyodogaku | Long | 指定月末極度額 |
| honkengoZandaka | Long | 本件後与信額 |
| tougetsZougen | Long | 当月増減額（計算結果） |

### GendoSannyuMeisai（限度算入与信明細）

限度算入与信状況の明細行。キーは与信種別コード。

| フィールド名 | 型 | 説明 |
|---|---|---|
| yoshinShubetsuCode | String | 与信種別コード（業務名） |
| kyodogaku | Long | 極度額 |
| honkengoZandaka | Long | 本件後残高 |

### TosuiGetsujiData（取推月次データ）

取推管理顧客GCIF月次の1ヶ月分データ。直近6ヶ月・前年6ヶ月で共通。

| フィールド名 | 型 | 説明 |
|---|---|---|
| ym | String | 年月（yyyyMM） |
| ippanYoshinHeikin | Long | 一般与信平残 |
| yokinHeikin | Long | 預金平残 |
| el | Long | EL |
| elKanriGakuRate | String | EL管理額率 |
| elKanriRitsuRate | String | EL管理率率 |
| cmtHikiyoso | Long | CMT引当予想 |
| arariekiGaku | Long | 粗利益額 |
| keihiChokuGaku | Long | 経費直課額 |

### GintoriJouiBank（銀取上位銀行）

銀取上位3行の1行分デー���。

| フィールド名 | 型 | 説明 |
|---|---|---|
| bankName | String | 銀行名 |
| zandaka | Long | 残高 |
| yoshin1 | Long | 与信1 |
| yoshin2 | Long | 与信2 |

### TantaiZaimuKessanData（単体財務決算データ）

単体財務決算分析の1期分データ。最大3期分。

| フィールド名 | 型 | 説明 |
|---|---|---|
| kessanki | String | 決算期 |
| jikocapital | Long | ��己資本 |
| ryudoShisanKei | Long | 流動資産計 |
| cashYokin | Long | 現金預金 |
| uketeTegata | Long | 受取手形 |
| urikakekin | Long | 売掛金 |
| zaikoKei | Long | 棚卸資産計 |
| koteiShisanKei | Long | 固定資産計 |
| koteiShisanYukeiKei | Long | 有形固定資産計 |
| kurinobeshisanKei | Long | 繰延資産計 |
| shisanKei | Long | 資産計 |
| ryudoFusaiKei | Long | 流動負債計 |
| shiharaiteGata | Long | 支払手形 |
| kaikakekin | Long | 買掛金 |
| wariteTegata | Long | 割引手形 |
| tanki | Long | 短期借入金 |
| koteFusaiKei | Long | 固定負債計 |
| shaBond | Long | 社債 |
| chokiKariirekin | Long | 長期借入金 |
| fusaiJunshisanKei | Long | 負債・純資産計 |
| chokiKariire1nen | Long | 長期借入金(1年以内) |
| shaBond1nen | Long | 社債(1年以内) |
| cpZandaka | Long | CP残高 |
| junshisanKei | Long | 純資産計 |
| uriage | Long | 売上高 |
| uriageSoeki | Long | 売上総利益 |
| eigyoEki | Long | 営業利益 |
| keijoeEki | Long | 経常利益 |
| tokiEki | Long | 当期利益 |
| uriageSoekiRitsu | String | 売上総利益率 |
| uriageKeijoeRitsu | String | 売上経常利益率 |
| uriageTokiRitsu | String | 売上当期利益率 |
| uriageGetsuShoheikin | Long | 平均月商 |
| kariireKaitenritsu | String | 借入回転率 |
| jikocapitalHiritsu | String | 自己資本比率 |
| uriageJuInterestFutanRitsu | String | 売上純金利負担率 |
| idoKeijyoShushi | Long | 移動経常収支 |
| idoKeijyoShushiHiritsu | String | 移動���常収支比率 |
| shuekiYoriShifusaiCf | Long | 収益より資金繰CF |
| tokiGensyoJisseiGaku | Long | 当期減少実績額 |

### TanpoShototalItem（担保小計項目）

担保区分ごとの小計。規定・優良小計/規定・一般小計/規定・その他小計/規定外・優良小計/規定外・一般小計で共通の構造。

| フィールド名 | 型 | 説明 |
|---|---|---|
| shubetsu | String | 小計種別（"kitei_yuryo_shototal", "kitei_ippan_shototal", "kitei_sonota_shototal", "kiteigai_yuryo_shototal", "kiteigai_ippan_shototal"） |
| kiteitiValue | Long | 規定値 |
| jikaValue | Long | 時価ベース |

### TanpoItem（担保項目）

引当状況の各担保項目。規定・優良/規定・一般/規定・その他/規定外・優良/規定外・一般の各区分で共通の構造。

| フィールド名 | 型 | 説明 |
|---|---|---|
| tanpoKubun | String | 担保区分（"kitei_yuryo", "kitei_ippan", "kitei_sonota", "kiteigai_yuryo", "kiteigai_ippan"） |
| tanpoShubetsu | String | 担保種別（"yokin", "shote", "tante", "yusho", "kyokai_hosho", "hosho", "ippan_lc", "tegata_hoken", "ikkatsu_shiharai", "fudosan_tei", "fudosan_tei_hloan", "fudosan_ne", "df_hosho", "dhcdc_hosho", "nyukyo_hoshokin", "saiken", "sonota"） |
| kiteitiValue | Long | 規定値 |
| jikaValue | Long | 時価ベース |

### ShiharaiShodakuItem（支払承諾項目）

支払承諾の各種別で共通の構造。4指標+当月増減額。

| フィールド名 | 型 | 説明 |
|---|---|---|
| shubetsu | String | 種別（"ippan", "ippan_gaita", "dairi_kasitsuki"） |
| kyodogaku | Long | 極度額 |
| honkengoZandaka | Long | 本件後残高 |
| getsumatsuZandaka | Long | 指定月末残高 |
| jisseiZandaka | Long | 実勢現在残高 |
| tougetsZougen | Long | 当月増減額 |

### GaitameMeisai（外為与信明細）

外為与信の各科目で共通の構造。

| フィールド名 | 型 | 説明 |
|---|---|---|
| kamokuCode | String | 科目コード（"shitei_gai_lc", "dp_da", "gaika_kitte", "yusyu_shototal", "kasidashi_yusyu", "yunyu_lc", "usance", "lg", "yunyu_shototal", "kasidashi_yunyu", "kosho_lc", "usan_shift"） |
| kyodogaku | Long | 極度額 |
| honkengoZandaka | Long | 本件後残高 |
| getsumatsuZandaka | Long | 指定月末残高 |
| jisseiZandaka | Long | 実勢現在残高 |
| tougetsZougen | Long | 当月増減額 |

### Hosyonin（保証人）

保証人名。最大5人。

| フィールド名 | 型 | 説明 |
|---|---|---|
| junban | int | 順番（1〜5） |
| name | String | 保証人名 |

---

## 1. サービスインプットDTO

画面からの入力。内部サービスはこのDTOに直接依存しない。

| フィールド名 | 型 | 説明 |
|---|---|---|
| ankenNo | String | 案件番号 |
| torihikibi | Date | 取引日（未設定時は内部で営業日を採用） |
| tenban | String | 店番 |
| torihikisakiNo | String | 取引先番号 |
| torihikisakiKasogaiTenban | String | 取引先貸外店番 |
| rinsaNo | String | 禀査番号 |
| haitaKey | String | 排他キー（楽観ロック用） |
| haitaKaisu | Integer | 排他回数（楽観ロック用） |

---

## 2. ホスト計数情報DTO

ホストから取得した計数情報。

### 2.1 一般与信状況

**繰り返し明細（List）**

| フィールド名 | 型 | 説明 | 現行対応 |
|---|---|---|---|
| kashitsukeMeisaiList | List\<KashitsukeMeisai\> | 貸付金明細1〜12（12要素） | F_LMT[V_KEISU_KASHISHO_MEISAI1_BAP〜12_BAP]等 |

**合計・小計・個別科目（意味が異なるため個別フィールド）**

| フィールド名 | 型 | 説明 | 現行定数 |
|---|---|---|---|
| kashitsukeShoteTotalKyodogaku | Long | 貸付金・商手合計 極度額 | V_KEISU_KASHISHO_TOT_BAP |
| kashitsukeShoteTotalHonkengoZandaka | Long | 貸付金・商手合計 本件後残高 | 同 |
| kashitsukeShoteTotalGetsumatsuZandaka | Long | 貸付金・商手合計 月末残高 | 同 |
| kashitsukeShoteTotalJisseiZandaka | Long | 貸付金・商手合計 実勢現在残高 | 同 |
| kashitsukeShoteTotalTougetsZougen | Long | 貸付金・商手合計 当月増減額 | 同 |
| uchiEnkaKyodogaku | Long | 内円貨 極度額 | V_KEISU_UCHIENKA_BAP |
| uchiEnkaHonkengoZandaka | Long | 内円貨 本件後残高 | 同 |
| gaitameTotalKyodogaku | Long | 外為与信合計 極度額 | V_KEISU_GAITAME_TOT_BAP |
| gaitameTotalHonkengoZandaka | Long | 外為与信合計 本件後残高 | 同 |
| gaitameTotalGetsumatsuZandaka | Long | 外為与信合計 月末残高 | 同 |
| gaitameTotalJisseiZandaka | Long | 外為与信合計 実勢現在残高 | 同 |
| gaitameTotalTougetsZougen | Long | 外為与信合計 当月増減額 | 同 |
| gaitameMeisaiList | List\<GaitameMeisai\> | 外為与信明細（kamokuCodeキー: shitei_gai_lc, dp_da, gaika_kitte, yusyu_shototal, kasidashi_yusyu, yunyu_lc, usance, lg, yunyu_shototal, kasidashi_yunyu, kosho_lc, usan_shift） | V_KEISU_GAITAME_*_BAP |
| shishoTotalKyodogaku | Long | 支払承諾合計 極度額 | V_KEISU_SHISHO_TOT_BAP |
| shishoTotalHonkengoZandaka | Long | 支払承諾合計 本件後残高 | 同 |
| shishoTotalGetsumatsuZandaka | Long | 支払承諾合計 月末残高 | 同 |
| shishoTotalJisseiZandaka | Long | 支払承諾合計 実勢現在残高 | 同 |
| shishoTotalTougetsZougen | Long | 支払承諾合計 当月増減額 | 同 |
| shiharaiShodakuItemList | List\<ShiharaiShodakuItem\> | 支払承諾明細（shubetsuキー: ippan, ippan_gaita, dairi_kasitsuki） | V_KEISU_SHISHO_*_BAP |
| shibosaiKyodogaku | Long | 私募債 極度額 | V_KEISU_SHIBOSAI_BAP |
| shibosaiHonkengoZandaka | Long | 私募債 本件後残高 | 同 |
| shibosaiTougetsZougen | Long | 私募債 当月増減額 | 同 |
| kyohogashiHonkengoZandaka | Long | 協保貸 本件後残高 | V_KEISU_KYOHOGASHI_BAP |
| ippanYoshinSonotaHonkengoZandaka | Long | その他一般与信 本件後残高 | V_KEISU_IPNYSSNT_BAP |
| gendoLoanTotalKyodogaku | Long | 限度算入ローン合計 極度額 | V_KEISU_GENDOLOAN_TOT_BAP |
| gendoLoanTotalHonkengoZandaka | Long | 限度算入ローン合計 本件後残高 | 同 |
| gendoLoanTotalTougetsZougen | Long | 限度算入ローン合計 当月増減額 | 同 |
| onBalanceTotalKyodogaku | Long | オンバランス合計 極度額 | V_KEISU_ONBALANCE_TOT_BAP |
| onBalanceTotalHonkengoZandaka | Long | オンバランス合計 本件後残高 | 同 |
| onBalanceTotalTougetsZougen | Long | オンバランス合計 当月増減額 | 同 |
| offBalanceTotalKyodogaku | Long | オフバランス合計 極度額 | V_KEISU_OFFBALANCE_TOT_BAP |
| offBalanceTotalHonkengoZandaka | Long | オフバランス合計 本件後残高 | 同 |
| offBalanceTotalTougetsZougen | Long | オフバランス合計 当月増減額 | 同 |
| gendoSannyuTotalKyodogaku | Long | 限度算入与信合計 極度額 | F_LMT_TOT[V_KEISU_GENDOSAN_TOT_BAP] |
| gendoSannyuTotalHonkengoZandaka | Long | 限度算入与信合計 本件後残高 | F_HONAF_ZAN_TOT[同] |
| gendoSannyuTotalTougetsZougen | Long | 限度算入与信合計 当月増減額 | F_IPNYSNDLTZGG_TOT[同] |
| gendoFusannyuTotalKyodogaku | Long | 限度不算入与信合計 極度額 | V_KEISU_GNDFUSAN_TOT_BAP |
| gendoFusannyuTotalHonkengoZandaka | Long | 限度不算入与信合計 本件後残高 | 同 |
| ippanYoshinTotalKyodogaku | Long | 一般与信合計 極度額 | V_KEISU_IPPANYSN_TOT_BAP |
| ippanYoshinTotalHonkengoZandaka | Long | 一般与信合計 本件後残高 | 同 |
| ippanYoshinTotalTougetsZougen | Long | 一般与信合計 当月増減額 | 同 |
| sonotaYoshinTotalHonkengoZandaka | Long | 特定与信合計 本件後残高 | V_KEISU_SONOTA_TOT_BAP |
| sonotaYoshin1HonkengoZandaka | Long | 特定与信1 本件後残高 | V_KEISU_SONOTA_YSN1_BAP |
| sonotaYoshin2HonkengoZandaka | Long | 特定与信2 本件後残高 | V_KEISU_SONOTA_YSN2_BAP |
| hlShinyoFusannyuHonkengoZandaka | Long | 内HL信用不算入 本件後残高 | V_KEISU_HLSHINYOFUSANNYU_BAP |

**補正値（意味が異なる4項目→個別フィールド）**

| フィールド名 | 型 | 説明 | 現行定数 |
|---|---|---|---|
| hoseiKashitsukeShokeTotal | Long | 貸付金・商手合計 補正値 | F_HOSCH[V_KEISU_KASHISHO_TOT_BAP] |
| hoseiUchiEnka | Long | 内円貨 補正値 | F_HOSCH[V_KEISU_UCHIENKA_BAP] |
| hoseiGaitameTotal | Long | 外為与信合計 補正値 | F_HOSCH[V_KEISU_GAITAME_TOT_BAP] |
| hoseiShishoTotal | Long | 支払承諾合計 補正値 | F_HOSCH[V_KEISU_SHISHO_TOT_BAP] |

### 2.2 本件後引当状況（同構造の担保明細→List\<TanpoItem\> + 合計は個別フィールド）

**担保明細（同構造の繰り返し→List\<TanpoItem\>）**

| フィールド名 | 型 | 説明 |
|---|---|---|
| tanpoItemList | List\<TanpoItem\> | 全担保明細。tanpoKubun+tanpoShubetsuが複合キー |

tanpoKubun × tanpoShubetsu の組み合わせ:

| tanpoKubun | tanpoShubetsu 一覧 | 現行定数 |
|---|---|---|
| kitei_yuryo | yokin, shote, tante, yusho, kyokai_hosho, hosho, ippan_lc, tegata_hoken, ikkatsu_shiharai, sonota | V_KEISU_KTI_YUTNP_*_BAP |
| kitei_ippan | yusho, hosho, fudosan_tei, fudosan_tei_hloan, fudosan_ne, df_hosho, sonota | V_KEISU_KTI_IPNTNP_*_BAP |
| kitei_sonota | yusho, hosho, dhcdc_hosho, sonota | V_KEISU_KTI_SNTTNP_*_BAP |
| kiteigai_yuryo | yokin, yusho, hosho, sonota | V_KEISU_KTIG_YUTNP_*_BAP |
| kiteigai_ippan | yusho, hosho, fudosan_tei, fudosan_ne, nyukyo_hoshokin, saiken, sonota | V_KEISU_KTIG_IPNTNP_*_BAP |

**小計（同構造の繰り返し→List\<TanpoShototalItem\>）**

| フィールド名 | 型 | 説明 |
|---|---|---|
| tanpoShototalItemList | List\<TanpoShototalItem\> | 担保区分ごとの小計（shubetsuキー: kitei_yuryo_shototal, kitei_ippan_shototal, kitei_sonota_shototal, kiteigai_yuryo_shototal, kiteigai_ippan_shototal） |

**合計・補正値・裸与信（意味が異なるため個別フィールド）**

| フィールド名 | 型 | 説明 | 現行定数 |
|---|---|---|---|
| kiteiTanpoTotalKiteiti | Long | 規定担保合計（規定値） | V_KEISU_KTITNP_TOT_BAP |
| kiteiTanpoTotalJika | Long | 規定担保合計（時価ベース） | 同 |
| kiteiTanpoHoseiKiteiti | Long | 規定担保補正値（規定値） | V_KEISU_KTITNP_HOSCH_BAP |
| kiteiTanpoHoseiJika | Long | 規定担保補正値（時価ベース） | 同 |
| hadakaYoshinKiteiti | Long | 裸与信（規定値） | V_KEISU_STRCRE_BAP |
| kiteigaiSonotaKiteiti | Long | 規定外・その他（規定値） | V_KEISU_KTIG_SONOTA_BAP |
| kiteigaiSonotaJika | Long | 規定外・その他（時価ベース） | 同 |
| kiteigaiTotalKiteiti | Long | 規定外担保合計（規定値） | V_KEISU_KTIG_TOT_BAP |
| kiteigaiTotalJika | Long | 規定外担保合計（時価ベース） | 同 |

### 2.3 その他主要項目

| フィールド名 | 型 | 説明 | 現行Hashtableキー |
|---|---|---|---|
| kiteiYuryoTanpoShote | Long | 規定・優良担保・商手（規定値） | F_SUTNTE |
| shijoGendoSannyuHonkengoZandaka | Long | 市場性与信_限度算入与信合計(本件後与信額) | F_LMTINTL_RN_HONAF_ZAN |
| hadakaYoshinTaishoTotal | Long | 裸与信対象与信合計 | F_STRCRE_TSHO_TOT |
| ippanYoshinTaniMsg | String | 一般与信1タブの金額単位 | F_TANI_MSG_1 |
| shijoYoshinTaniMsg | String | 市場性与信1タブの金額単位 | F_SJOSEIINF_TANI_MSG_1 |

### 2.4 市場性与信科目明細（同構造の繰り��し→List）

| フィールド名 | 型 | 説明 |
|---|---|---|
| shijoKamokuMeisaiList | List\<ShijoKamokuMeisai\> | 市場性与信科目明細1〜10（10要素） |

### 2.5 簡易CF

| フィールド名 | 型 | 説明 | 現行Hashtableキー |
|---|---|---|---|
| kanICf1 | Long | 簡易CF1 | F_KSKBTDLCF1 |
| kanICf2 | Long | 簡易CF2 | F_KSKBTDLCF2 |
| kanICf3 | Long | 簡易CF3 | F_KSKBTDLCF3 |

---

## 3. 顧客財務関連データDTO

DBから取得した顧客財務関連データ。同構造の繰り返しはList、意味が異な���項目は個別。

| フィールド名 | 型 | 説明 |
|---|---|---|
| soshikiTenban | String | 組織店番 |
| soshikiTenmeiRyakusho | String | 組織店名略称（10文字以内） |
| sakuseibi | String | 作成日（当日営業日） |
| gcifNo | String | GCIF番号 |
| nayoseDatanum | Integer | 名寄件数 |
| nayoseFlg60num | Integer | flg60件数 |
| nayoseFlg59num | Integer | flg59件数 |
| nayoseFlg58num | Integer | flg58件数 |
| gintoriSokairiZandaka | Long | 銀取・総借入 残高 |
| gintoriSokairiYoshin1 | Long | 銀取・総借入 与信1 |
| gintoriSokairiYoshin2 | Long | 銀取・総借入 与信2 |
| gintoriTokouZandaka | Long | 銀取・当行 残高 |
| gintoriTokouYoshin1 | Long | 銀取・当行 与信1 |
| gintoriTokouYoshin2 | Long | 銀取・当行 与信2 |
| gintoriJouiBankList | List\<GintoriJouiBank\> | 銀取・上位3行（最大3要素） |
| tosuiChokkinList | List\<TosuiGetsujiData\> | 取推・直近6ヶ月 |
| tosuiZennenList | List\<TosuiGetsujiData\> | 取推・前年6ヶ月 |
| tosuiKankeisakiChokkinList | List\<TosuiGetsujiData\> | 取推関係先・直近6ヶ月 |
| tosuiKankeisakiZennenList | List\<TosuiGetsujiData\> | 取推関係先・前年6ヶ月 |
| hoshoninList | List\<Hosyonin\> | 保証人（最大5要素） |
| jikoSatei1BunruiGaku | Long | 自己査定 1分類額 |
| jikoSatei2BunruiGaku | Long | 自己査定 2分類額 |
| jikoSatei3BunruiGaku | Long | 自己査定 3分類額 |
| jikoSatei4BunruiGaku | Long | 自己査定 4分類額 |
| jikoSateiTotal | Long | 自己査定 合計 |
| jikoSateiUyokinRisuku | Long | 自己査定 預金リスク |
| jikoSateiCreditCost | Long | 自己査定 クレジットコスト |
| tantaiZaimuList | List\<TantaiZaimuKessanData\> | 単体財務（最大3期分） |
| hoseiIppanYoshinTotal | Long | 補正値・一般与信合計 |
| hoseiUchiEnka | Long | 補正値・内円貨 |
| hoseiBouekiTotal | Long | 補正値・貿易合計 |
| hoseiShishoTotal | Long | 補正値・支承合計 |
| hoseiReason | String | 補正理由 |
| hoseiKiteiTanpoKiteiti | Long | 規定担保補正値（規定値） |
| hoseiKiteiTanpoJika | Long | 規定担保補正値（時価ベース） |
| jikaToriGaku | Long | プロパーローン 時価取分額 |
| onLoanKasidashiZandaka | Long | プロパーローン ���ンローン残高 |
| chokkinKeisuAnkenNo | String | 直近計数案件番号 |
| hyoujiFrom | String | 表示月FROM（yyyyMM） |
| hyoujiTo | String | 表示月TO（yyyyMM） |
| hyoujiZennenFrom | String | 表示月前年FROM（yyyyMM） |
| hyoujiZennenTo | String | 表示月前年TO（yyyyMM） |

---

## 4. 計数ベースデータDTO

ホスト+DB値をマージした計算用データ。構造はDTO#2と同一（同じフィールド名・型）。採用ルールのみが異なる。

| 採用ルール | 対象 |
|---|---|
| ホスト値をそのまま採用 | 極度額、当月増減額、限度算入合計、引当状況合計、商手規定値、裸与信対象等 |
| DB値で上書き | 指定月末残高、本件後残高、実勢現在残高 |
| DBベース＋一部ホスト上書き | 引当状況・規定値（電債割引/電債担保/協会保証/一般L/C/手形保険/D/F保証はホスト値） |
| DB値を採用 | ���定担保補正値（規定値/時価ベ���ス） |

---

## 5. 一般与信状況計算結果DTO

computeYosin()の出力。DTO#2の一般与信部分と同一フィールド構造（補正適用・合計再計算後の値）。

---

## 6. 本件後保全状況計算結果DTO

computeKokyakuShutoku()+computeKokyaku()の出力。DTO#2の引当状況部分と同一フィールド構造（各小計・合計・裸与信の再計算後の値）。

---

## 7. 科目明細当月増減額計算結果DTO

computeKokyaku2()の出力。

| フィールド名 | 型 | 説明 |
|---|---|---|
| shijoKamokuMeisaiResultList | List\<ShijoKamokuMeisai\> | 市場性与信科目明細1〜10（当月増減額が計算済み） |
| kanICf1 | Long | 簡易CF1（未設定時は空文字） |
| kanICf2 | Long | 簡易CF2（未設定時は空文字） |
| kanICf3 | Long | 簡易CF3（未設定時は空文字） |

---

## 8. 保全率計算結果DTO

computeHozen()��出力。各項目の意味が異なるため全て個別フィールド。

| フィールド名 | 型 | 説明 | 現行Hashtableキー |
|---|---|---|---|
| hozenTaniMsg | String | 保全率・金額単位 | F_HOZEN_TANI_MSG |
| hozenIppanYoshin | String | 保全率・限度算入一般与信 | F_HOZEN_IPNYSN |
| hozenShijoYoshin | String | 保全率・限度算入市場性与信 | F_HOZEN_SJOSEIYSN |
| hozenKiteiTanpo | String | 保全率・規定担保合計 | F_HOZEN_KITEITANPO |
| hozenHozenritsu | String | 保全率・保全率（小数点第2位） | F_HOZEN_HOZENRT |
| hozenSogoYoshin | String | 保全率・総合与信 | F_HOZEN_SOGOYSN |
| hozenSogoShinyo | String | 保全率・総合信用 | F_HOZEN_SOGOSNYO |

---

## 9. 計数計算結果DTO

計数計算サービスの戻り値。4つのサブDTOをCompositionで内包（配列ではない）。

| フィールド名 | 型 | 説明 |
|---|---|---|
| ippanYoshinResult | 一般与信状況計算結果DTO | DTO#5 |
| hozenJokyoResult | 本件後保全状況計算結果DTO | DTO#6 |
| kamokuMeisaiResult | 科目明細当月増減額計算結果DTO | DTO#7 |
| hozenritsuResult | 保全率計算結果DTO | DTO#8 |

---

## 10. サービスアウトプットDTO

画面への返却。

| フィールド名 | 型 | 説明 |
|---|---|---|
| haitaKaisu | Integer | 更新後の排他回数 |
| resultFlag | String | 処理結果フラグ |
| errorId | String | エラーID |
| errorType | String | エラー種別 |
| errorMessage | String | エラーメッセージ |

---

## 設計原則

| 原則 | 適用 |
|---|---|
| 意味の異なる項目 → 個別フィールド | 合計・小計項目、各担保区分、補正値4項目、保全率7項目 |
| 同構造の繰り返し → List | 貸付金明細12行、市場性与信科目明細10行、取推月次6ヶ月、単体財務3期、銀取上位3行、保証人5人 |
| 引数DTOはイミュータブル | DTO#1〜4は読み取り専用 |
| サービスインプットDTO非依存 | 各インナーは必要な値を個別引数で受け取る |
| ユーザID等はコンテキスト | リクエストスコープから取得 |
| Compositionは許可 | DTO#9がDTO#5〜8を内包 |
