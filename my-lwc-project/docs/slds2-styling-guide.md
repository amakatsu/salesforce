# SLDS2 スタイリングガイド

> **調査日**: 2026-03-15
> **対象**: Lightning Design System 2 (SLDS2) のスタイリングフック・デザイントークン
> **目的**: カスタムLWCコンポーネントのCSS設計における SLDS2 準拠の指針

---

## 1. コンポーネントスタイリングフック (`--slds-c-*`)

### SLDS2 での状況: 未サポート

公式ドキュメントの記載:

> "Component styling hooks aren't currently supported in SLDS 2.
> If your components use styling hooks that are named `--slds-c-*`
> we recommend that you stay on SLDS 1 for now."

**SLDS1 で使用可能だったフック（参考）:**

| フック名 | 用途 | SLDS2 状況 |
|---|---|---|
| `--slds-c-input-color-background` | input要素の背景色 | 未サポート |
| `--slds-c-input-shadow-focus` | input要素のフォーカスシャドウ | 未サポート |
| `--slds-c-button-brand-color-background` | brandボタンの背景色 | 未サポート |
| `--slds-c-datatable-*` | データテーブル系 | 未サポート |

### 影響範囲

CommonCss で使用中の以下のフックは SLDS2 移行時に代替が必要:

```css
/* CommonCss 内で使用中 */
.changed-cell { --slds-c-input-color-background: ...; }
.changed-cell lightning-input { --slds-c-input-shadow-focus: ...; }
```

### 対応方針

SLDS2 でコンポーネントフックがサポートされるまでは SLDS1 テーマを維持するか、
カスタム CSS 変数で同等の制御を行う。

---

## 2. グローバルスタイリングフック (`--slds-g-*`)

SLDS2 で使用可能なグローバルフック。テーマが変わっても適切な値が自動適用される。

### 命名規則

```
--slds-g-[category]-[property]-[role]-[attribute]-[state]-[range]
```

- `slds` = 名前空間（固定）
- `g` = グローバルスコープ
- `category` = color, shadow, radius, spacing, sizing, font
- `range` = 数値（1が最小/最軽量）

### 2.1 カラー: サーフェス（背景色）

| フック名 | 用途 | 適用例 |
|---|---|---|
| `--slds-g-color-surface-1` | プライマリ背景（パネル、モーダル） | データセルの白背景 |
| `--slds-g-color-surface-2` | セカンダリ背景 | ― |
| `--slds-g-color-surface-container-1` | コンテナ要素の背景（テキスト/アイコン含む） | テーブルヘッダー背景 |
| `--slds-g-color-surface-container-2` | コンテナ背景（中間トーン） | ― |
| `--slds-g-color-surface-container-3` | コンテナ背景（濃いトーン） | ― |

```css
/* 使用例: テーブルヘッダー背景 */
.data-table th {
  background: var(--slds-g-color-surface-container-1, #f2f2f2);
}

/* 使用例: データセル背景 */
.data-table td {
  background: var(--slds-g-color-surface-1, #fff);
}
```

### 2.2 カラー: ボーダー

| フック名 | 用途 | 適用例 |
|---|---|---|
| `--slds-g-color-border-1` | ニュートラルボーダー（非インタラクティブ要素） | テーブル罫線 |
| `--slds-g-color-border-2` | インタラクティブ要素のボーダー（WCAG 2.1準拠） | 入力フィールド付近 |

```css
/* 使用例: テーブルボーダー */
.data-table th,
.data-table td {
  border-top: var(--slds-g-sizing-border-1, 1px) solid var(--slds-g-color-border-1, #999);
  border-left: var(--slds-g-sizing-border-1, 1px) solid var(--slds-g-color-border-1, #999);
}
```

### 2.3 カラー: テキスト/アイコン（on-surface）

| フック名 | 用途 | 適用例 |
|---|---|---|
| `--slds-g-color-on-surface-1` | プライマリテキスト/アイコン | メイン文字色 |
| `--slds-g-color-on-surface-2` | セカンダリテキスト/アイコン | 補助テキスト、セパレータ |
| `--slds-g-color-on-surface-3` | ターシャリテキスト/アイコン | ― |

```css
/* 使用例: セパレータ文字色 */
.due-date-separator {
  color: var(--slds-g-color-on-surface-2, #444);
}
```

### 2.4 カラー: アクセント（ブランド色）

| フック名 | 用途 |
|---|---|
| `--slds-g-color-accent-1` | リンク、アクティブ状態、アイコン |
| `--slds-g-color-accent-2` | アクセント（中間） |
| `--slds-g-color-accent-3` | アクセント（濃い） |
| `--slds-g-color-accent-container-1` | ブランドボタン、選択状態の背景 |
| `--slds-g-color-accent-container-2` | アクセントコンテナ（中間） |
| `--slds-g-color-accent-container-3` | アクセントコンテナ（濃い） |
| `--slds-g-color-border-accent-1` | アクセントボーダー |
| `--slds-g-color-border-accent-2` | アクセントボーダー（中間） |
| `--slds-g-color-border-accent-3` | アクセントボーダー（濃い） |

### 2.5 カラー: フィードバック（エラー/成功/警告/情報/無効）

| カテゴリ | フック名 |
|---|---|
| **Error** | `--slds-g-color-error-1`, `-container-1`, `-container-2`, `-on-error-1`, `-border-error-1`, `-border-error-2` |
| **Success** | `--slds-g-color-success-1`, `-container-1`, `-container-2`, `-on-success-1`, `-on-success-2`, `-border-success-1` |
| **Warning** | `--slds-g-color-warning-1`, `-container-1`, `-on-warning-1`, `-border-warning-1` |
| **Info** | `--slds-g-color-info-1`, `-container-1`, `-on-info-1` |
| **Disabled** | `--slds-g-color-disabled-1`, `-2`, `-container-1`, `-container-2`, `-on-disabled-1`, `-on-disabled-2`, `-border-disabled-1`, `-border-disabled-2` |

### 2.6 シャドウ

| フック名 | 用途 |
|---|---|
| `--slds-g-shadow-1` | レベル1（最も浅い・微細なシャドウ） |
| `--slds-g-shadow-2` | レベル2 |
| `--slds-g-shadow-3` | レベル3 |
| `--slds-g-shadow-4` | レベル4（最も深い・強いシャドウ） |

**注意**: これらは UI 要素の**深度表現（ドロップシャドウ）**用。
`inset` ボーダー代替の `box-shadow` には**使用不可**（セクション4参照）。

### 2.7 ボーダー幅

| フック名 | 用途 |
|---|---|
| `--slds-g-sizing-border-1` | ボーダー幅1（最細、通常 1px 相当） |
| `--slds-g-sizing-border-2` | ボーダー幅2 |
| `--slds-g-sizing-border-3` | ボーダー幅3 |
| `--slds-g-sizing-border-4` | ボーダー幅4（最太） |

```css
/* 使用例: テーブルボーダー幅 */
border-top: var(--slds-g-sizing-border-1, 1px) solid var(--slds-g-color-border-1, #999);
```

### 2.8 ボーダー角丸

| フック名 | 用途 |
|---|---|
| `--slds-g-radius-border-1` | 角丸1（最小） |
| `--slds-g-radius-border-2` | 角丸2 |
| `--slds-g-radius-border-3` | 角丸3 |
| `--slds-g-radius-border-4` | 角丸4（大きい） |
| `--slds-g-radius-border-circle` | 円形 |
| `--slds-g-radius-border-pill` | ピル形 |

### 2.9 タイポグラフィ

| フック名 | 用途 |
|---|---|
| `--slds-g-font-size-base` | ベースフォントサイズ |
| `--slds-g-font-size-1` 〜 `14` | スケーリングされたフォントサイズ（14段階） |
| `--slds-g-font-weight-4` | 通常の太さ（normal） |
| その他 `-weight-*` | lighter / heavier バリアント |

### 2.10 スペーシング

| フック名 | 用途 |
|---|---|
| `--slds-g-spacing-*` | 4の倍数モジュラースケール（ルートフォントサイズ基準） |

---

## 3. ハードコード値 → フック 置換マッピング

C2 コンポーネントで確認されたハードコード値と推奨フックの対応表。

| ハードコード値 | 推奨フック | 記法 | 確度 |
|---|---|---|---|
| `#f2f2f2`（ヘッダー背景） | `--slds-g-color-surface-container-1` | `var(--slds-g-color-surface-container-1, #f2f2f2)` | 高 |
| `#fff`（セル背景） | `--slds-g-color-surface-1` | `var(--slds-g-color-surface-1, #fff)` | 高 |
| `#444`（セパレータ文字色） | `--slds-g-color-on-surface-2` | `var(--slds-g-color-on-surface-2, #444)` | 高 |
| `#999`（ボーダー色） | `--slds-g-color-border-1` | `var(--slds-g-color-border-1, #999)` | 中 |
| `1px`（ボーダー幅） | `--slds-g-sizing-border-1` | `var(--slds-g-sizing-border-1, 1px)` | 中 |

### 置換コード例（Before / After）

```css
/* ══ Before ══ */
.data-table th {
  background: #f2f2f2;
  box-shadow: inset 0 1px 0 #999;
}
.data-table td {
  background: #fff;
  border-top: 1px solid #999;
  border-left: 1px solid #999;
}
.due-date-separator {
  color: #444;
}

/* ══ After ══ */
.data-table th {
  background: var(--slds-g-color-surface-container-1, #f2f2f2);
  box-shadow: inset 0 var(--slds-g-sizing-border-1, 1px) 0 var(--slds-g-color-border-1, #999);
}
.data-table td {
  background: var(--slds-g-color-surface-1, #fff);
  border-top: var(--slds-g-sizing-border-1, 1px) solid var(--slds-g-color-border-1, #999);
  border-left: var(--slds-g-sizing-border-1, 1px) solid var(--slds-g-color-border-1, #999);
}
.due-date-separator {
  color: var(--slds-g-color-on-surface-2, #444);
}
```

---

## 4. カスタム CSS で書くしかないもの

SLDS2 のフック/トークンでは代替できず、カスタム CSS が必要なもの。

### 4.1 `box-shadow: inset` によるボーダー代替

```css
box-shadow: inset 0 1px 0 #999, inset 0 -1px 0 #999;
```

**理由**: `--slds-g-shadow-1`〜`4` はドロップシャドウ（UI要素の深度表現）用に設計されており、
`inset` を使った sticky ヘッダーのボーダー代替という用途に合致しない。
ボーダー色部分のみフック化可能（`var(--slds-g-color-border-1, #999)`）だが、
`inset 0 1px 0` という構造自体は SLDS2 のフックでは表現できない。

### 4.2 Sticky ポジショニング関連

```css
position: sticky;
top: var(--c2-thead-height);
z-index: 9;
```

**理由**: Sticky テーブルヘッダー/行のポジショニングはレイアウト固有のロジック。
SLDS2 にはスティッキー制御用のフックは存在しない。
コンポーネント固有の CSS 変数（`--c2-thead-height` 等）で管理するのが適切。

### 4.3 テーブル列幅・セルレイアウト

```css
.column-icon { width: 1.25rem; }
.column-label { width: 10rem; }
.due-date-cell lightning-input { flex: 0 1 3.4375em; }
```

**理由**: コンポーネント固有のレイアウト寸法。SLDS2 のスペーシングフックはマージン/
パディング用であり、テーブル列幅のような具体的レイアウト寸法には対応していない。

### 4.4 `nth-child` セレクタによる行単位スタイリング

```css
.table-container-credit tbody tr:nth-child(1) td { background-color: #f2f2f2; }
.table-container-collateral tbody tr:nth-child(-n+3) td { background-color: #f2f2f2; }
```

**理由**: 特定行の固定表示は業務ロジックに依存する構造的スタイリング。
SLDS2 はこのような行単位の条件付きスタイリングのフックを提供していない。
色のみフック化可能（`var(--slds-g-color-surface-container-1, #f2f2f2)`）。

### 4.5 `!important` によるスタイル上書き

```css
padding-left: 0.25rem !important;
padding-right: 0 !important;
```

**理由**: LWC の Shadow DOM 境界を超えたスタイル適用のため `!important` が必要な場合、
SLDS2 フックでは解決できない。構造的な設計判断の領域。

---

## 5. SLDS2 移行時の注意点

### 5.1 フォールバック値は必須

SLDS Linter ルール `no-slds-var-without-fallback`（Error レベル）:

```css
/* NG: フォールバックなし */
background: var(--slds-g-color-surface-container-1);

/* OK: フォールバックあり */
background: var(--slds-g-color-surface-container-1, #f2f2f2);
```

フォールバック値があることで、SLDS1 テーマ環境でもSLDS2 テーマ環境でも正しく表示される。

### 5.2 グローバルフックの再代入は禁止

`--slds-g-*` の値をコンポーネント内で上書きしてはならない。消費（`var()` で読む）のみ。

```css
/* NG: グローバルフックの再代入 */
:host {
  --slds-g-color-surface-container-1: #e0e0e0;
}

/* OK: 消費のみ */
.my-header {
  background: var(--slds-g-color-surface-container-1, #f2f2f2);
}
```

### 5.3 デザイントークン (`--lwc-*`) は SLDS2 で非サポート

SLDS1 で使用していた `--lwc-*` トークンは SLDS2 テーマでは動作しない。

```css
/* NG: SLDS2テーマで動作しない */
background: var(--lwc-cardBodyPadding);

/* OK: SLDS2対応 */
padding: var(--slds-g-spacing-4, 1rem);
```

### 5.4 `--slds-c-*` フックは SLDS2 で未サポート

コンポーネントレベルフックは SLDS2 テーマでは動作しない（開発中）。
使用している場合は SLDS1 テーマを維持すること。

**当プロジェクトへの影響**: CommonCss で使用中の以下フックは要監視:
- `--slds-c-input-color-background`（changed-cell のハイライト）
- `--slds-c-input-shadow-focus`（changed-cell のフォーカスシャドウ）

### 5.5 SLDS Linter の活用

移行時は SLDS Linter の以下ルールを活用:

| ルール | レベル | 内容 |
|---|---|---|
| `no-hardcoded-values-slds2` | Warning | ハードコード値を `--slds-g-*` フックに置換 |
| `lwc-token-to-slds-hook` | Error | `--lwc-*` トークンを `--slds-g-*` フックに置換 |
| `enforce-sds-to-slds-hooks` | Warning | `--sds-g-*` を `--slds-g-*` に変換 |
| `no-slds-var-without-fallback` | Error | `var()` にフォールバック値を必須化 |

### 5.6 デフォルト値は非公開・変更可能

`--slds-g-*` フックのデフォルト Hex 値は Salesforce が非公開としている。
リリースごとに変更される可能性があるため、フォールバック値で現在の見た目を保証すること。

### 5.7 SLDS1 デザイントークンとの対応（参考）

| SLDS1 トークン | 値 | 対応する SLDS2 フック |
|---|---|---|
| `$color-gray-3` | `#f3f2f2` | `--slds-g-color-surface-container-1` |
| `$color-gray-8` | `#969492` | `--slds-g-color-border-1`（近似） |
| `$color-background` | `#f3f3f3` | `--slds-g-color-surface-1` or `surface-container-1` |
| `$color-background-alt` | `#ffffff` | `--slds-g-color-surface-1` |
| `$color-border` | `#e5e5e5` | `--slds-g-color-border-1` |
| `$shadow-drag` | `0 2px 4px rgba(0,0,0,.4)` | `--slds-g-shadow-3` or `shadow-4`（近似） |
| `$shadow-drop-down` | `0 2px 3px rgba(0,0,0,.16)` | `--slds-g-shadow-1` or `shadow-2`（近似） |

---

## 参考資料

- [SLDS Styling Hooks (LWC Developer Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties.html)
- [Global Styling Hooks Guidance (SLDS v1)](https://v1.lightningdesignsystem.com/platforms/lightning/new-global-styling-hooks-guidance/)
- [Compare SLDS Versions (LWC Developer Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds1-slds2.html)
- [SLDS Linter Rules Reference](https://developer.salesforce.com/docs/platform/slds-linter/guide/reference-rules.html)
- [SLDS v1 Design Tokens](https://v1.lightningdesignsystem.com/design-tokens/)
- [Global Styling Hooks (SLDS2)](https://www.lightningdesignsystem.com/2e1ef8501/p/591960-global-styling-hooks)
- [Styling Hooks Overview (SLDS2)](https://www.lightningdesignsystem.com/2e1ef8501/p/319e5f-styling-hooks)
