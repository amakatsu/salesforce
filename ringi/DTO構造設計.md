# DTO構造設計

> 対象: 計数情報マスタ再登録（RgV0501）で使用する全10種のDTO
> 設計原則:
> - 引数DTOはイミュータブル（読み取り専用）
> - ユーザID等はコンテキストから取得（DTOに含めない）
> - **Listの設計方針**:
>   - 横軸（列構造）が同じデータは**合計行・小計行を含めて全てListの1要素**にする
>   - 合計・小計は種別キー=「合計」「小計」の要素として持つ。個別フィールドで合計を持つのは禁止
>   - List要素には必ずキー値（業務種別名）を含めること。連番・キーなし禁止
>   - 判断基準: 画面の1行の列 = DTOのフィールド、行の繰り返し = List

---

## 明細用サブDTO定義

### IppanYoshinRow（一般与信行）

一般与信状況の1行分。貸付金明細行・外為科目行・支払承諾行・合計行・小計行すべてこの型で統一。画面の横軸（列）=フィールド。

| フィールド名 | 型 | 説明 |
|---|---|---|
| rowType | String | 行種別（"meisai"=明細行, "shototal"=小計行, "total"=合計行） |
| rowKey | String | 行キー（業務種別名。例: "kashitsuke_meisai_1", "kashitsuke_shote_total", "uchi_enka", "gaitame_total", "gaitame_shitei_gai_lc", "shisho_ippan", "shisho_total", "shibosai", "on_balance_total", "off_balance_total", "gendo_sannyu_total", "gendo_fusannyu_total", "ippan_yoshin_total" 等） |
| kyodogaku | Long | 極度額 |
| honkengoZandaka | Long | 本件後残高 |
| getsumatsuZandaka | Long | 指定月末残高 |
| jisseiZandaka | Long | 実勢現在残高 |
| tougetsZougen | Long | 当月増減額 |
| bunruiCode | String | 分類コード（明細行のみ） |
| kamokuName | String | 科目名・表示用（明細行のみ） |
| kijitsu | String | 期日（明細行のみ） |
| riritsu | String | 利率（明細行のみ） |
| hoseiValue | Long | 補正値（補正対象行のみ） |
| rinsaNo | String | 禀査番号（明細行のみ） |

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

### HikiateRow（引当状況行）

本件後引当状況の1行分。担保明細行・小計行・合計行・補正値行・裸与信行すべてこの型で統一。画面の横軸（列）=フィールド。

| フィールド名 | 型 | 説明 |
|---|---|---|
| rowType | String | 行種別（"meisai"=明細, "shototal"=小計, "total"=合計, "hosei"=補正値, "hadaka"=裸与信） |
| rowKey | String | 行キー（業務種別名。例: "kitei_yuryo_yokin", "kitei_yuryo_shototal", "kitei_tanpo_total", "kitei_tanpo_hosei", "hadaka_yoshin", "kiteigai_yuryo_yokin", "kiteigai_total" 等） |
| kiteitiValue | Long | 規定値 |
| jikaValue | Long | 時価ベース |

※ 旧TanpoItem・TanpoShototalItemを統合。合計・小計・補正値・裸与信も全てListの1要素として持つ。
※ 外為与信明細・支払承諾明細は IppanYoshinRow に統合済み（一般与信タブの行として管理）。

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

ホストから取得した計数情報。画面タブ単位でサブ構造を持つ。

### 2.1 一般与信状況（全行を統一型のListで管理）

| フィールド名 | 型 | 説明 |
|---|---|---|
| ippanYoshinRowList | List\<IppanYoshinRow\> | 一般与信状況の全行。貸付金明細12行+合計行+外為科目行+支払承諾行+その他全てをrowKeyで区別 |

ippanYoshinRowListに含まれるrowKey一覧:

| rowType | rowKey | 説明 | 現行定数 |
|---|---|---|---|
| meisai | kashitsuke_meisai_1〜12 | 貸付金明細1〜12 | V_KEISU_KASHISHO_MEISAI1_BAP〜12_BAP |
| total | kashitsuke_shote_total | 貸付金・商手合計 | V_KEISU_KASHISHO_TOT_BAP |
| meisai | uchi_enka | 内円貨 | V_KEISU_UCHIENKA_BAP |
| meisai | gaitame_shitei_gai_lc | 指定外L/C | V_KEISU_GAITAME_SHITEIGAILC_BAP |
| meisai | gaitame_dp_da | D/P・D/A | V_KEISU_GAITAME_DPDA_BAP |
| meisai | gaitame_gaika_kitte | 外貨小切手 | V_KEISU_GAITAME_GAIKAKITTE_BAP |
| shototal | gaitame_yusyu_shototal | 輸出(小計) | V_KEISU_GAITAME_YUSYU_STOT_BAP |
| meisai | gaitame_kasidashi_yusyu | 貸出(輸出) | V_KEISU_GAITAME_KSDS_YUSYU_BAP |
| meisai | gaitame_yunyu_lc | 輸入L/C | V_KEISU_GAITAME_YUNYULC_BAP |
| meisai | gaitame_usance | ユーザンス | V_KEISU_GAITAME_USANCE_BAP |
| meisai | gaitame_lg | L/G | V_KEISU_GAITAME_LG_BAP |
| shototal | gaitame_yunyu_shototal | 輸入(小計) | V_KEISU_GAITAME_YUNYU_STOT_BAP |
| meisai | gaitame_kasidashi_yunyu | 貸出(輸入) | V_KEISU_GAITAME_KSDS_YUNYU_BAP |
| meisai | gaitame_kosho_lc | 故障指定L/C | V_KEISU_GAITAME_KOSHOLC_BAP |
| meisai | gaitame_usan_shift | ユーザンスシフト外貨 | V_KEISU_GAITAME_USANSHIFT_BAP |
| total | gaitame_total | 外為与信合計 | V_KEISU_GAITAME_TOT_BAP |
| meisai | shisho_ippan | 支承・一般 | V_KEISU_SHISHO_IPAN_BAP |
| meisai | shisho_ippan_gaita | 支承・一般外為 | V_KEISU_SHISHO_IPANGAITA_BAP |
| meisai | shisho_dairi_kasitsuki | 代理貸付 | V_KEISU_SHISHO_DAIRIKSTK_BAP |
| total | shisho_total | 支払承諾合計 | V_KEISU_SHISHO_TOT_BAP |
| meisai | shibosai | 私募債 | V_KEISU_SHIBOSAI_BAP |
| meisai | kyohogashi | 協保貸 | V_KEISU_KYOHOGASHI_BAP |
| meisai | ippan_yoshin_sonota | その他一般与信 | V_KEISU_IPNYSSNT_BAP |
| meisai | gendo_loan_total | 限度算入ローン合計 | V_KEISU_GENDOLOAN_TOT_BAP |
| total | on_balance_total | オンバランス合計 | V_KEISU_ONBALANCE_TOT_BAP |
| total | off_balance_total | オフバランス合計 | V_KEISU_OFFBALANCE_TOT_BAP |
| total | gendo_sannyu_total | 限度算入与信合計 | F_LMT_TOT[V_KEISU_GENDOSAN_TOT_BAP] |
| total | gendo_fusannyu_total | 限度不算入与信合計 | V_KEISU_GNDFUSAN_TOT_BAP |
| meisai | gendo_fusannyu_nenkin | 年金転貸 | V_KEISU_GNDFUSAN_NENKIN_BAP |
| meisai | gendo_fusannyu_sitei_lc | 指定L/C小切手 | V_KEISU_GNDFUSAN_SITEILC_BAP |
| meisai | gendo_fusannyu_lg | L/G | V_KEISU_GNDFUSAN_LG_BAP |
| total | ippan_yoshin_total | 一般与信合計 | V_KEISU_IPPANYSN_TOT_BAP |
| meisai | sonota_yoshin_1 | 特定与信1 | V_KEISU_SONOTA_YSN1_BAP |
| meisai | sonota_yoshin_2 | 特定与信2 | V_KEISU_SONOTA_YSN2_BAP |
| total | sonota_yoshin_total | 特定与信合計 | V_KEISU_SONOTA_TOT_BAP |
| meisai | hl_shinyo_fusannyu | 内HL信用不算入 | V_KEISU_HLSHINYOFUSANNYU_BAP |

**補正値（4項目、個別フィールド → 各行のhoseiValueフィールドで管理）**

補正値はippanYoshinRowListの該当行（rowKey=kashitsuke_shote_total/uchi_enka/gaitame_total/shisho_total）のhoseiValueフィールドに格納する。

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
※ 上記ippanYoshinRowListに合計行・小計行・補正値を含めて全て統一管理。個別フィールドなし。

### 2.2 本件後引当状況（全行をHikiateRowのListで管理）

| フィールド名 | 型 | 説明 |
|---|---|---|
| hikiateRowList | List\<HikiateRow\> | 引当状況の全行。担保明細+小計+合計+補正値+裸与信をrowKeyで区別 |

hikiateRowListに含まれるrowKey一覧:

| rowType | rowKey | 説明 | 現行定数 |
|---|---|---|---|
| meisai | kitei_yuryo_yokin | 規定・優良・預金 | V_KEISU_KTI_YUTNP_YOKIN_BAP |
| meisai | kitei_yuryo_shote | 規定・優良・商手 | V_KEISU_KTI_YUTNP_SYOTE_BAP |
| meisai | kitei_yuryo_tante | 規定・優良・担手 | V_KEISU_KTI_YUTNP_TANTE_BAP |
| meisai | kitei_yuryo_yusho | 規定・優良・有証 | V_KEISU_KTI_YUTNP_YUSYO_BAP |
| meisai | kitei_yuryo_kyokai_hosho | 規定・優良・協会保証 | V_KEISU_KTI_YUTNP_KYOHO_BAP |
| meisai | kitei_yuryo_hosho | 規定・優良・保証（除協会） | V_KEISU_KTI_YUTNP_HOSYO_BAP |
| meisai | kitei_yuryo_ippan_lc | 規定・優良・一般L/C | V_KEISU_KTI_YUTNP_IPANLC_BAP |
| meisai | kitei_yuryo_tegata_hoken | 規定・優良・手形保険 | V_KEISU_KTI_YUTNP_TEGATAHO_BAP |
| meisai | kitei_yuryo_ikkatsu_shiharai | 規定・優良・一括支払 | V_KEISU_KTI_YUTNP_IKKATU_BAP |
| meisai | kitei_yuryo_sonota | 規定・優良・その他 | V_KEISU_KTI_YUTNP_SONOTA_BAP |
| shototal | kitei_yuryo_shototal | 規定・優良小計 | V_KEISU_KTI_YUTNP_STOT_BAP |
| meisai | kitei_ippan_yusho | 規定・一般・有証 | V_KEISU_KTI_IPNTNP_YUSYO_BAP |
| meisai | kitei_ippan_hosho | 規定・一般・保証 | V_KEISU_KTI_IPNTNP_HOSYO_BAP |
| meisai | kitei_ippan_fudosan_tei | 規定・一般・不動産(抵) | V_KEISU_KTI_IPNTNP_FUDO_TEI_BAP |
| meisai | kitei_ippan_fudosan_tei_hloan | 規定・一般・内HL(抵) | V_KEISU_KTI_IPNTNP_FUDOTE_HLOAN_BAP |
| meisai | kitei_ippan_fudosan_ne | 規定・一般・不動産(根) | V_KEISU_KTI_IPNTNP_FUDO_NE_BAP |
| meisai | kitei_ippan_df_hosho | 規定・一般・D/F保証 | V_KEISU_KTI_IPNTNP_DFHOSYO_BAP |
| meisai | kitei_ippan_sonota | 規定・一般・その他 | V_KEISU_KTI_IPNTNP_SONOTA_BAP |
| shototal | kitei_ippan_shototal | 規定・一般小計 | V_KEISU_KTI_IPNTNP_STOT_BAP |
| meisai | kitei_sonota_yusho | 規定・その他・有証 | V_KEISU_KTI_SNTTNP_YUSYO_BAP |
| meisai | kitei_sonota_hosho | 規定・その他・保証 | V_KEISU_KTI_SNTTNP_HOSYO_BAP |
| meisai | kitei_sonota_dhcdc_hosho | 規定・その他・DHC・DC保証 | V_KEISU_KTI_SNTTNP_DHCDC_BAP |
| meisai | kitei_sonota_sonota | 規定・その他・その他 | V_KEISU_KTI_SNTTNP_SONOTA_BAP |
| shototal | kitei_sonota_shototal | 規定・その他小計 | V_KEISU_KTI_SNTTNP_STOT_BAP |
| total | kitei_tanpo_total | 規定担保合計 | V_KEISU_KTITNP_TOT_BAP |
| hosei | kitei_tanpo_hosei | 規定担保補正値 | V_KEISU_KTITNP_HOSCH_BAP |
| hadaka | hadaka_yoshin | 裸与信 | V_KEISU_STRCRE_BAP |
| meisai | kiteigai_yuryo_yokin | 規定外・優良・預金 | V_KEISU_KTIG_YUTNP_YOKIN_BAP |
| meisai | kiteigai_yuryo_yusho | 規定外・優良・有証 | V_KEISU_KTIG_YUTNP_YUSYO_BAP |
| meisai | kiteigai_yuryo_hosho | 規定外・優良・保証 | V_KEISU_KTIG_YUTNP_HOSYO_BAP |
| meisai | kiteigai_yuryo_sonota | 規定外・優良・その他 | V_KEISU_KTIG_YUTNP_SONOTA_BAP |
| shototal | kiteigai_yuryo_shototal | 規定外・優良小計 | V_KEISU_KTIG_YUTNP_STOT_BAP |
| meisai | kiteigai_ippan_yusho | 規定外・一般・有証 | V_KEISU_KTIG_IPNTNP_YUSYO_BAP |
| meisai | kiteigai_ippan_hosho | 規定外・一般・保証 | V_KEISU_KTIG_IPNTNP_HOSYO_BAP |
| meisai | kiteigai_ippan_fudosan_tei | 規定外・一般・不動産(抵) | V_KEISU_KTIG_IPNTNP_FUDO_TEI_BAP |
| meisai | kiteigai_ippan_fudosan_ne | 規定外・一般・不動産(根) | V_KEISU_KTIG_IPNTNP_FUDO_NE_BAP |
| meisai | kiteigai_ippan_nyukyo_hoshokin | 規定外・一般・入居保証金 | V_KEISU_KTIG_IPNTNP_NYUKYO_BAP |
| meisai | kiteigai_ippan_saiken | 規定外・一般・債券 | V_KEISU_KTIG_IPNTNP_SAIKEN_BAP |
| meisai | kiteigai_ippan_sonota | 規定外・一般・その他 | V_KEISU_KTIG_IPNTNP_SONOTA_BAP |
| shototal | kiteigai_ippan_shototal | 規定外・一般小計 | V_KEISU_KTIG_IPNTNP_STOT_BAP |
| meisai | kiteigai_sonota | 規定外・その他 | V_KEISU_KTIG_SONOTA_BAP |
| total | kiteigai_total | 規定外担保合計 | V_KEISU_KTIG_TOT_BAP |

※ 合計・小計・補正値・裸与信もListの1要素。個別フィールドなし。

### 2.3 その他（個別フィールド）

計算入力に使われるが一般与信行・引当状況行のどちらにも属さない項目。

| フィールド名 | 型 | 説明 | 現行Hashtableキー |
|---|---|---|---|
| kiteiYuryoTanpoShote | Long | 規定・優良担保・商手（規定値）— 初期計算入力 | F_SUTNTE |
| shijoGendoSannyuHonkengoZandaka | Long | 市場性与信・限度算入与信合計（本件後与信額） | F_LMTINTL_RN_HONAF_ZAN |
| hadakaYoshinTaishoTotal | Long | 裸与信対象与信合計 | F_STRCRE_TSHO_TOT |
| ippanYoshinTaniMsg | String | 一般与信1タブの金額単位 | F_TANI_MSG_1 |
| shijoYoshinTaniMsg | String | 市場性与信1タブの金額単位 | F_SJOSEIINF_TANI_MSG_1 |

### 2.4 市場性与信科目明細

| フィールド名 | 型 | 説明 |
|---|---|---|
| shijoKamokuMeisaiList | List\<ShijoKamokuMeisai\> | 市場性与信科目明細1〜10（10要素、科目コードキー） |

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

computeYosin()の出力。DTO#2セクション2.1と同一構造。

| フィールド名 | 型 | 説明 |
|---|---|---|
| ippanYoshinRowList | List\<IppanYoshinRow\> | 一般与信状況の全行（補正適用・合計再計算・当月増減額再計算後の値）。rowKeyでDTO#2と同一キー体系 |

---

## 6. 本件後保全状況計算結果DTO

computeKokyakuShutoku()+computeKokyaku()の出力。DTO#2セクション2.2と同一構造。

| フィールド名 | 型 | 説明 |
|---|---|---|
| hikiateRowList | List\<HikiateRow\> | 引当状況の全行（各小計・合計・裸与信が再計算後の値）。rowKeyでDTO#2と同一キー体系 |

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
| 横軸（列構造）が同じ → 合計行含めて全てList | 一般与信全行→List\<IppanYoshinRow\>、引当状況全行→List\<HikiateRow\> |
| 合計・小計はListの1要素 | rowKey=「合計」「小計」の要素として持つ。個別フィールドで合計を持つのは禁止 |
| 横軸が異なる → 個別フィールド | 保全率計算結果7項目、その他の計算入力項目 |
| 引数DTOはイミュータブル | DTO#1〜4は読み取り専用 |
| サービスインプットDTO非依存 | 各インナーは必要な値を個別引数で受け取る |
| ユーザID等はコンテキスト | リクエストスコープから取得 |
| Compositionは許可 | DTO#9がDTO#5〜8を内包 |
