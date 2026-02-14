 
No.	ドメイン名	ドメイン説明	データ型	カラム定義	参考定義（類推）	問題	サンプル値	文字列長	SJISバイト長	数値	書式（正規表現）	参照外部コードID
 	 	最小文字数	最大文字数	最小バイト数	最大バイト数	小数部バイト数	最小値	最大値	整数部桁数	小数部桁数
-4	Agent（補足）	コベナンツ案件のAgentの補足	全半角混合文字	VARCHAR2(200)	VARCHAR2(200)	OK	Agent（補足）	0	200	0	200	 	 	 	 	 	 	 
-3	Agentコード	コベナンツ案件のAgentの区分	コード	CHAR(2)	CHAR(2)	OK	01	2	2	2	2	 	 	 	 	 	 	cv_code00006
（旧：rlrcv_code00006）
-2	Agent名称	コベナンツ案件のAgentの名称
旧シス：cv_code00006の名称1、または手入力した名称	全半角混合文字	VARCHAR2(22)	VARCHAR2(22)	OK	Agent（その他）	0	22	0	22	 	 	 	 	 	 	cv_code00006
（旧：rlrcv_code00006）
-1	ＣＤＤ取得区分	 	コード	CHAR(1)	CHAR(1)	OK	 	1	1	1	1	 	 	 	 	 	 	gs_code00053
0	D-Vision会社コード	株式会社ダイヤモンド社の保有する企業役員情報の会社コード	半角数字	CHAR(8)	CHAR(8)	OK	 	8	8	8	8	 	 	 	 	 	 	 
1	D-Vision個人コード	株式会社ダイヤモンド社の保有する企業役員情報の個人コード	半角数字	CHAR(8)	CHAR(8)	OK	 	8	8	8	8	 	 	 	 	 	 	 
2	GCIF番号	新情報のGCIF	半角数字	CHAR(10)	CHAR(10)	OK	1234567891	10	10	10	10	 	 	 	 	 	 	 
3	HTTPリクエストメソッド	 	半角英字	VARCHAR2(10)	VARCHAR2(10)	OK	GET	1	10	1	10	 	 	 	 	 	[A-Z]{1,10}	 
4	MIME-Type	ファイルのデータ形式を表す	半角英数字記号	VARCHAR2(128)	VARCHAR2(128)	OK	text/plain	0	128	0	128	 	 	 	 	 	 	 
5	ON未実施店	 	半角数字	 	VARCHAR2(1)	4.charとvarcharのカラム定義の揺れ	 	0	1	0	1	 	 	 	 	 	 	 
6	S3オブジェクトキー	S3上のオブジェクトを識別するキー文字列	半角英数字記号	VARCHAR2(1024)	VARCHAR2(1024)	OK	 	0	1024	0	1024	 	 	 	 	 	 	 
7	SHA-1チェックサム	ハッシュ関数の一つ。16進数表記。	半角英数字	CHAR(40)	CHAR(40)	OK	f6f8c9dd1e8efebb02a95f2575135a1574d7148f	40	40	40	40	 	 	 	 	 	 	 
8	SMTPアドレス	外部I/F(共通認証)	半角英数字記号	VARCHAR2(60)	VARCHAR2(60)	OK	 	0	60	0	60	 	 	 	 	 	 	 
9	URI	 	半角英数字	VARCHAR2(1000)	VARCHAR2(1000)	OK	bkyus0/kessai_shohin/KsV0502_KessaiShohinKanriDetail/shonin	1	1000	1	1000	 	 	 	 	 	 	 
10	WFステータスコード	汎用WFのワークフローのステータスコード	コード	 	CHAR(5)	 	001	5	5	5	5	 	 	 	 	 	 	gs_code00004
（旧：rlgco_code01016）
11	WFステータス名称	汎用WFのワークフローのステータスコードに対応する名称	コード	VARCHAR2(50)	VARCHAR2(50)	OK	 	0	50	0	50	 	 	 	 	 	 	gs_code00004
（旧：rlgco_code01016）
12	アラーム	債務者格付　アラーム分析	半角数字	 	VARCHAR2(3)	5.同一ドメインだがカラム定義が異なる	 	0	3	0	3	 	 	 	 	 	 	 
13	案件番号	案件を識別するキー情報。	半角英数字	CHAR(12)	CHAR(12)	OK	123465789012	12	12	12	12	 	 	 	 	 	[0-9A-Z](12)	 
14	案件枝番	案件を識別するキー情報（枝番）。	数値（整数）	NUMBER(3)	NUMBER(3)	OK	123	1	3	1	3	 	1	999	 	 	 	 
15	エリアポストコード	外部I/F(共通認証)	半角数字	 	VARCHAR2(3)	4.charとvarcharのカラム定義の揺れ	 	0	3	0	3	 	 	 	 	 	 	 
16	エリア店番	外部I/F(共通認証)	半角数字	VARCHAR2(5)	VARCHAR2(5)	OK	 	4	5	4	5	 	 	 	 	 	 	 
17	オペレーションセンター	 	半角数字	 	VARCHAR2(1)	4.charとvarcharのカラム定義の揺れ	 	0	1	0	1	 	 	 	 	 	 	 
18	改定内容	履歴の改定内容／備考	全半角混合文字	 	VARCHAR2(80)	 	 	0	80	0	80	 	 	 	 	 	 	 
19	開店日	外部I/F(共通認証), 部店情報ファイル「開店日」	半角数字	 	VARCHAR2(7)	4.charとvarcharのカラム定義の揺れ	 	0	7	0	7	 	 	 	 	 	 	 
20	合併区分	外部I/F(共通認証)	半角数字	VARCHAR2(2)	VARCHAR2(2)	OK	 	0	2	0	2	 	 	 	 	 	 	 
21	ｔ	人事データ上のカナ氏名	半角英数字記号	 	VARCHAR2(20)	 	 	0	20	0	20	 	 	 	 	 	 	 
22	勘定店区分	外部I/F(共通認証)	半角数字	 	VARCHAR2(1)	4.charとvarcharのカラム定義の揺れ	 	0	1	0	1	 	 	 	 	 	 	 
23	完了日区分	未完・期日管理において、完了日を表すコード	コード	 	CHAR(1)	 	 	1	1	1	1	 	 	 	 	 	 	gs_code00066
24	期中・申請区分	 	半角数字	CHAR(1)	CHAR(1)	OK	 	1	1	1	1	 	 	 	 	 	 	cv_code00079
 
 
 
No.	PK	論理項目名	物理項目名(小文字)	データ型	Length	数値
全体数桁	数値
小数桁	デフォルト値
-5	1	案件番号	lc_no	char	12	 	 	 
-4	 	条件･指示番号	j_no	number	 	10	0	 
-3	 	組織店番	sskbrno	char	5	 	 	 
-2	 	組織店名	sskbrnm	varchar2	20	 	 	 
-1	 	部門コード	dep_cd	char	1	 	 	 
0	 	部門コード細区分	dep_cd_saiid	char	1	 	 	 
1	 	店番	brno	char	7	 	 	 
2	 	取引先番号	triskno	char	7	 	 	 
3	 	取引先名	trinm	varchar2	50	 	 	 
4	 	業種名称	gyoshu_nm	varchar2	50	 	 	 
5	 	当行親密度	mbksinmt	varchar2	20	 	 	 
6	 	主力行	mainbank	varchar2	20	 	 	 
7	 	コア企業	crkgy	varchar2	24	 	 	 
8	 	部店･エリア名称(与信)	buten_area_nm_ysb	varchar2	50	 	 	 
9	 	課･グループ名称(与信)	ka_grp_nm_ysb	varchar2	20	 	 	 
10	 	部店エリア(与信)	buten_area_cd_ysb	char	6	 	 	 
11	 	課･グループ(与信)	ka_grp_cd_ysb	char	5	 	 	 
12	 	部店エリア(決定)	buten_area_cd_ksb	char	6	 	 	 
13	 	課･グループ(決定)	ka_grp_cd_ksb	char	5	 	 	 
14	 	決裁権限	keskengen	varchar2	16	 	 	 
15	 	役職順コード	shok_jun	number	 	4	0	 
16	 	案件決定日	lc_ketbi	date	 	 	 	 
17	 	報告期限	houkigen	date	 	 	 	 
18	 	要報告内容	yohhoukoku	varchar2	1200	 	 	 
19	 	回答書･報告書内容	ans_naiyo	varchar2	1200	 	 	 
20	 	親案件番号	oya_lc_no	char	12	 	 	 
21	 	与信区分	ysid	char	1	 	 	 
22	 	債務者格付	saimush_kakzk	char	2	 	 	 
23	 	債務者格付細区分	saimush_kakzk_skb	char	1	 	 	 
24	 	禀議査定番号	ring_sat_no	char	4	 	 	 
25	 	禀議査定枝番	ring_sat_edano	char	3	 	 	 
 
 
 
親コンポーネント	f003RgV0201RinsaLst	 	 	 	 	 	 	 	 	 	 	 	 	 	 
No.	配置コンポーネント	項目名称	ドメイン名	データID/フィールド名	型	lightningパーツ	アクセス種別	バリデーション
テキストタイプ	最小桁	最大桁	最大
バイト数	最小値	最大値	必須項目	日付前後関係
（YYYY/MM/DDに限定）	外部コード
 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	 
1	f003RgV0201RinsaLstB1	回収新規	 	btnRecoveryNew	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
2	f003RgV0201RinsaLstB1	継続	 	btnKezk	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
3	f003RgV0201RinsaLstB1	条件変更	 	btnJokenChange	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
4	f003RgV0201RinsaLstB1	増減額	 	btnFluctuationAmt	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
5	f003RgV0201RinsaLstB1	利率変更	 	btnRtChange	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
6	f003RgV0201RinsaLstB1	極度超過	 	btnMaximumOver	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
7	f003RgV0201RinsaLstB1	削除	 	btnDelete	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
8	f003RgV0201RinsaLstB1	ファイル作成	 	btnCreateFile	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
9	f003RgV0201RinsaLstC1	検索条件	 	acSearchJoken	アコーディオン	lightning-accordion-section	 	 	 	 	 	 	 	 	 	 
10	f003RgV0201RinsaLstC1	検索	 	btnSearch	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
11	f003RgV0201RinsaLstC1	クリア	 	btnClear	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
12	f003RgV0201RinsaLstC1	登録	 	btnRegist	ボタン	lightning-button	 	 	 	 	 	 	 	 	 	 
13	f003RgV0201RinsaLstC1	基本条件	フラグ(true/false)	basicJoken	ラジオボタン	lightning-radio-group	入力可能	 	 	 	 	 	 	 	 	rg_code00034_1_1
14	f003RgV0201RinsaLstC1	期間	フラグ(true/false)	period	チェックボックス	lightning-checkbox-group	入力可能	 	 	 	 	 	 	 	 	rg_code01006_1_1
15	f003RgV0201RinsaLstC1	絞込条件	フラグ(true/false)	shiborikomiJoken	チェックボックス	lightning-checkbox-group	入力可能	 	 	 	 	 	 	 	 	rg_code01007_1_2
16	f003RgV0201RinsaLstC1	並び替え条件	フラグ(true/false)	sortJoken	ラジオボタン	lightning-radio-group	入力可能	 	 	 	 	 	 	 	 	rg_code00082_1_1
17	f003RgV0201RinsaLstC1	組織店番１	部店コード	orgBrNo1	テキスト	lightning-input(text)	入力可能	半角英数字	4	5	 	 	 	 	 	 
18	f003RgV0201RinsaLstC1	組織店番２	部店コード	orgBrNo2	テキスト	lightning-input(text)	入力可能	半角英数字	4	5	 	 	 	 	 	 
 
 