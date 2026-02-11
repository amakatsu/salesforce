@startuml
title as-is: 一枚岩（ゴッドクラス）で画面差分/登録差分を抱え、差分は Factory 注入

legend top
【構造（現状）】

- 中心: ゴッドクラス（全画面分の項目/分岐/検証/変換/永続化）
- 差分: 各画面で準備（画面項目差分・登録差分）を Factory 経由で注入
  endlegend

actor "画面" as 画面
database "DB" as DB

box "アプリケーション（現状）"
participant "ゴッドクラス\n（全画面の項目/分岐/登録を内包）" as ゴッド
participant "差分生成ファクトリ" as 差分Factory

box "各画面で準備（差分）" #FFE6CC
participant "画面項目差分ロジック\n（項目有無/必須/入力可否/変換）" as 画面差分
participant "登録差分ロジック\n（登録列/更新方式/SQL 方針）" as 登録差分
end box

participant "DB アクセス\n（DAO/ゲートウェイ）" as DBアクセス
end box

画面 -> ゴッド : 登録(画面 ID, 入力 DTO)

note right of ゴッド

- 全画面分の項目と分岐が集中
- 画面差分/登録差分もサービス中心で制御
- 検証/変換/永続化まで一枚岩
  end note

ゴッド -> 差分Factory : 差分取得(画面 ID, 入力 DTO)
差分Factory --> ゴッド : 画面差分 / 登録差分

ゴッド -> 画面差分 : 検証・正規化(入力 DTO)
画面差分 --> ゴッド : 正規化データ

ゴッド -> 登録差分 : 永続化モデル変換(正規化データ)
登録差分 --> ゴッド : 永続化モデル

ゴッド -> DBアクセス : 保存(永続化モデル)
DBアクセス -> DB : INSERT/UPDATE
DB --> DBアクセス : 結果
DBアクセス --> ゴッド : 結果

ゴッド --> 画面 : 応答
@enduml

@startuml
title to-be: API は操作ごと（登録 API）／サービス入力 DTO は「XX 稟議固有」に寄せる

legend top

- リクエスト本文 -> XX 稟議 Request DTO へバインド -> Bean Validation
- XX 稟議 Mapper（稟議単位で 1 つ）で入力変換（Request DTO -> XX 稟議入力 DTO）
- サービスは共通 IF で受け、差分（ふるまい/永続化）は稟議単位で吸収
  ※ 色付き box は「各稟議で準備(差分)」
  endlegend

actor "画面" as 画面

box "API 層"
box "各稟議で準備(差分)" #FFE6CC
participant "XX 稟議 登録 API コントローラ" as api
participant "XX 稟議 Request DTO\n(バインド + Bean Validation 対象)" as reqDto
participant "XX 稟議 Mapper\n(入力変換を集約)" as xxMapper
end box
end box

box "サービス層"
participant "稟議入力 IF\n(サービス境界の共通型)" as inIf
participant "登録アプリケーションサービス\n(共通: 手順/Tx 境界)" as appSvc
participant "差分サービスファクトリ\n(稟議 ID -> 差分サービス)" as svcFactory

box "各稟議で準備(差分)" #FFE6CC
participant "XX 稟議 入力 DTO\n(稟議入力 IF を実装)" as inXX
participant "業務差分サービス\n(ふるまい差分がある場合のみ)" as diffSvc
end box
end box

box "リポジトリ層"
participant "リポジトリ実装\n(共通: RepoIF implement)" as repoImpl
participant "稟議別永続化ファクトリ\n(共通: 稟議 ID -> 永続化一式)" as pFactory

box "各稟議で準備(差分)" #FFE6CC
participant "XX 稟議 永続化マッパー\n(XX 稟議入力 DTO -> DB エンティティ詰め替え)" as pMapper
participant "XX 稟議 DB エンティティ" as dbEntity
participant "XX 稟議 MyBatisMapper\n(insert 実行)" as mybatis
participant "XX 稟議 MapperXML\n(SQL 定義)" as xml
end box
end box

box "DB"
database "DB" as DB
end box

' ===== シーケンス =====

画面 -> api : POST 登録(稟議 ID=XX, リクエスト本文)
activate api

create reqDto
api -> reqDto : バインド(リクエスト本文)\n+ Bean Validation
activate reqDto
reqDto --> api : XX 稟議 Request DTO(値が詰まった状態)
deactivate reqDto

api -> xxMapper : to 入力(XX 稟議 Request DTO) -> XX 稟議入力 DTO
activate xxMapper

create inXX
xxMapper -> inXX : new() / 値セット(正規化・詰め替え)
inXX --> xxMapper : XX 稟議入力 DTO
deactivate inXX

xxMapper --> api : 返却(入力: 稟議入力 IF)\n※実体=XX 稟議入力 DTO
deactivate xxMapper

api -> appSvc : 実行(入力: 稟議入力 IF, 稟議 ID=XX)
deactivate api
activate appSvc

appSvc -> svcFactory : 差分サービス取得(稟議 ID=XX)
activate svcFactory
svcFactory --> appSvc : 差分サービス
deactivate svcFactory

opt ふるまい差分がある場合のみ
appSvc -> diffSvc : 固有処理(入力: 稟議入力 IF)
activate diffSvc
diffSvc -> inXX : 固有項目参照()\n(必要時のみ)
inXX --> diffSvc : 固有項目
diffSvc --> appSvc : 補助情報/更新済み入力(必要時)
deactivate diffSvc
end opt

appSvc -> repoImpl : 保存(入力: 稟議入力 IF, 稟議 ID=XX)
deactivate appSvc
activate repoImpl

repoImpl -> pFactory : 永続化一式取得(稟議 ID=XX)
activate pFactory
pFactory --> repoImpl : XX 稟議 永続化マッパー, XX 稟議 MyBatisMapper, XX 稟議 MapperXML
deactivate pFactory

repoImpl -> pMapper : 詰め替え(入力: 稟議入力 IF)\n-> XX 稟議 DB エンティティ
activate pMapper

create dbEntity
pMapper -> dbEntity : new() / 値セット(DB 列に詰め替え)
activate dbEntity
dbEntity --> pMapper : XX 稟議 DB エンティティ
deactivate dbEntity

pMapper --> repoImpl : XX 稟議 DB エンティティ
deactivate pMapper

repoImpl -> mybatis : insert(XX 稟議 DB エンティティ)
activate mybatis
mybatis -> xml : SQL 解決(insert)
activate xml
xml --> mybatis : SQL
deactivate xml

mybatis -> DB : INSERT
activate DB
DB --> mybatis : 結果
deactivate DB
mybatis --> repoImpl : 結果
deactivate mybatis

repoImpl --> appSvc : 結果
deactivate repoImpl
activate appSvc

appSvc --> api : 応答
deactivate appSvc
activate api
api --> 画面 : 応答
deactivate api

@enduml
