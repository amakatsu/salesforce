# 01. 機能概要と案件背景

## 機能概要

| 項目 | 値 |
| --- | --- |
| 機能 ID | `RgV0501_RinsashoCntInfoRegistCorrectValue` |
| サービスクラス物理名 | `RgV0501RinsashoCntInfoRegistCorrectValue` |
| サービスクラス論理名 | 計数情報 補正値登録 |
| 機能の目的 | リクエスト情報（補正値）を DB へ登録する |

## 処理分類

| 区分 | 値 |
| --- | --- |
| DB 接続 | 更新 |
| 他システム連携 | × |
| ホスト連携 | × |
| 帳票出力 | × |
| API 冪等性（リトライ可否） | 〇 |

## エラーチェック

| 種別 | 値 |
| --- | --- |
| 入力相関チェック | なし |
| DB 相関チェック | なし |

## 案件背景（旧 → 新更改の位置づけ）

本機能は **既存 Java 資産（IBM WACS / Crafts! 基盤、2002〜2010 年実装）から新 MUFG 基盤（`jp.mufg.bk.yus`）への更改** として位置づけられる。

| 観点 | 現行 | 新方式 |
|---|---|---|
| 配置パッケージ | `jp.co.btm.irl.rlr.rg004` | `jp.mufg.bk.yus`（参照: [../../設計ルール/アーキテクチャ.md](../../設計ルール/アーキテクチャ.md)） |
| 既存資産ファイル | `RLRRG004_B01_U06.java` | （新規実装）|
| 詳細解析 | [04_legacy_analysis.md](04_legacy_analysis.md) を参照 | [02_new_implementation.md](02_new_implementation.md) を参照 |

## スコープ

- **スコープ内**: 新サービスクラスおよび周辺資産の新規実装（参照: [02_new_implementation.md](02_new_implementation.md)）。
- **対象外（明示）**: 他システム連携、ホスト連携、帳票出力。
- **対象外（推定）**: 画面 (UI) 実装の有無は memo.text に記載なし。詳細は [09_open_questions.md](09_open_questions.md) を参照。
