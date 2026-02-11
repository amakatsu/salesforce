# サービス層 Specification パターン

## 概要

複数の稟議で共有するビジネスルール（承認条件、金額判定、稟議種別判定等）を **Specification（仕様）** として部品化し、各稟議の業務差分サービスで再利用する。

## サービス層の構造

@startuml
title サービス層: Specification パターンによる共有ルールの部品化

box "サービス層" #E6F7FF
participant "登録アプリケーション\nサービス（共通）" as appSvc

box "XX 稟議（差分）" #FFE6CC
participant "XX 稟議\n入力 DTO" as xxInput
participant "XX 稟議\n業務差分サービス" as xxDiffSvc
end box

box "YY 稟議（差分）" #FFE6CC
participant "YY 稟議\n入力 DTO" as yyInput
participant "YY 稟議\n業務差分サービス" as yyDiffSvc
end box

box "共有 Specification（部品）" #E6FFE6
participant "金額判定\nSpecification" as amountSpec
participant "稟議種別判定\nSpecification" as typeSpec
participant "承認条件\nSpecification" as approvalSpec
end box

end box

' ===== シーケンス =====

appSvc -> xxDiffSvc : 固有処理実行(XX 稟議入力 DTO)
activate xxDiffSvc

xxDiffSvc -> xxInput : 稟議データ取得()
xxInput --> xxDiffSvc : 金額、種別等

xxDiffSvc -> amountSpec : isSatisfiedBy(金額)
activate amountSpec
amountSpec --> xxDiffSvc : true/false
deactivate amountSpec

xxDiffSvc -> typeSpec : isSatisfiedBy(種別)
activate typeSpec
typeSpec --> xxDiffSvc : true/false
deactivate typeSpec

xxDiffSvc -> approvalSpec : isSatisfiedBy(金額, 種別)
activate approvalSpec
approvalSpec --> xxDiffSvc : 承認要否
deactivate approvalSpec

xxDiffSvc --> appSvc : 処理結果
deactivate xxDiffSvc

note right of xxDiffSvc
  **XX 稟議の業務差分サービス**
  共有 Specification を組み合わせて
  XX 稟議固有の判定を実現
end note

appSvc -> yyDiffSvc : 固有処理実行(YY 稟議入力 DTO)
activate yyDiffSvc

yyDiffSvc -> yyInput : 稟議データ取得()
yyInput --> yyDiffSvc : 金額、種別等

yyDiffSvc -> amountSpec : isSatisfiedBy(金額)
activate amountSpec
note right of amountSpec
  **同じ Specification を再利用**
end note
amountSpec --> yyDiffSvc : true/false
deactivate amountSpec

yyDiffSvc -> approvalSpec : isSatisfiedBy(金額, 種別)
activate approvalSpec
approvalSpec --> yyDiffSvc : 承認要否
deactivate approvalSpec

yyDiffSvc --> appSvc : 処理結果
deactivate yyDiffSvc

note right of yyDiffSvc
  **YY 稟議の業務差分サービス**
  共有 Specification を組み合わせて
  YY 稟議固有の判定を実現
end note

legend bottom
  **凡例:**
  - <back:#E6F7FF>青背景</back>: サービス層全体
  - <back:#E6FFE6>緑背景</back>: 共有 Specification（部品）
  - <back:#FFE6CC>橙背景</back>: 各稟議で準備する差分
end legend

@enduml

## Specification パターンの利点

### 1. **ルールの再利用**
- 金額判定、稟議種別判定などの共通ルールを複数の稟議で再利用
- ルールの重複実装を防ぐ

### 2. **ルールの一元管理**
- ビジネスルールの変更時、Specification を修正するだけで全稟議に反映
- メンテナンス性の向上

### 3. **複雑なルールの組み合わせ**
- Composite パターンで複数の Specification を組み合わせ可能
- `AndSpecification`, `OrSpecification`, `NotSpecification` 等

### 4. **テスタビリティの向上**
- Specification を単体でテスト可能
- 業務差分サービスは Specification をモック化してテスト可能

## 実装例

### 金額判定 Specification

```java
public class AmountSpecification implements Specification<稟議入力DTO> {
    private final BigDecimal threshold;

    public AmountSpecification(BigDecimal threshold) {
        this.threshold = threshold;
    }

    @Override
    public boolean isSatisfiedBy(稟議入力DTO input) {
        return input.get金額().compareTo(threshold) > 0;
    }
}
```

### 承認条件 Specification

```java
public class ApprovalSpecification implements Specification<稟議入力DTO> {
    private final AmountSpecification amountSpec;
    private final TypeSpecification typeSpec;

    @Override
    public boolean isSatisfiedBy(稟議入力DTO input) {
        // 金額が閾値を超え、かつ特定種別の場合、承認必要
        return amountSpec.isSatisfiedBy(input)
            && typeSpec.isSatisfiedBy(input);
    }
}
```

### XX 稟議 業務差分サービス

```java
public class XX稟議DiffService {
    private final ApprovalSpecification approvalSpec;

    public ProcessResult execute(XX稟議入力DTO input) {
        // 共有 Specification を使用
        if (approvalSpec.isSatisfiedBy(input)) {
            // 承認フローへ
            return ProcessResult.needsApproval();
        }
        // 自動承認
        return ProcessResult.autoApproved();
    }
}
```

## 新規稟議追加時の作業

1. **稟議固有の入力 DTO を作成** （既存の稟議入力 IF を実装）
2. **業務差分サービスを作成** （共有 Specification を組み合わせる）
3. **稟議固有の Specification が必要なら追加** （他稟議で再利用可能なら共有化）

既存の共有 Specification を使うだけなら、新規実装は最小限で済む。
