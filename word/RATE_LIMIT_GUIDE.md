# APIレート制限ガイド

## 概要

大量の画面項目を処理する際、APIサーバーへの負荷を軽減するため、同時に実行するAPI呼び出し数を制限できます。

## 基本設定

### API同時実行数の制限

```bash
# 同時実行するAPIリクエストの最大数（デフォルト: 5）
export MAX_CONCURRENT_API=5

# 例：より高速に処理（高負荷）
export MAX_CONCURRENT_API=8

# 例：より負荷を抑える（低負荷）
export MAX_CONCURRENT_API=3

# 例：最も負荷を抑える
export MAX_CONCURRENT_API=1
```

### 並列ワーカー数の調整

```bash
# 並列ワーカー数（デフォルト: 6）
# ※ローカル処理も並列実行されるため、MAX_CONCURRENT_APIより大きい値を推奨
export MAX_WORKERS=6

# 例：高速処理（ローカル処理も多く並列実行）
export MAX_WORKERS=10

# 例：低リソース環境
export MAX_WORKERS=3
```

## 処理速度の目安

| 設定 | 100件の処理時間 | サーバー負荷 | 推奨用途 |
|------|----------------|-------------|----------|
| `API=8`, `WORKERS=10` | 約1分 | 高 | 開発・テスト環境 |
| `API=5`, `WORKERS=6` | 約1-2分 | 中高 | **推奨設定（デフォルト）** |
| `API=3`, `WORKERS=6` | 約2-3分 | 中 | 本番環境 |
| `API=1`, `WORKERS=3` | 約8-10分 | 低 | 共有環境・ピーク時 |

## 推奨設定パターン

### パターン1: 開発・テスト（高速）

```bash
export MAX_CONCURRENT_API=5
export MAX_WORKERS=10
export RETRY=1
```

### パターン2: 本番環境（バランス型・デフォルト）

```bash
export MAX_CONCURRENT_API=3
export MAX_WORKERS=6
export RETRY=2
```

### パターン3: サーバー負荷軽減（低負荷）

```bash
export MAX_CONCURRENT_API=2
export MAX_WORKERS=4
export RETRY=3
```

### パターン4: 共有環境（最低負荷）

```bash
export MAX_CONCURRENT_API=1
export MAX_WORKERS=2
export RETRY=3
```

## エラー時の自動リトライ

APIエラー時は自動的にリトライします：

```bash
# リトライ回数（デフォルト: 2回）
export RETRY=3

# タイムアウト時間（秒）
export TIMEOUT_SEC=30
```

リトライ時の待機時間は自動的に増加します：
- 1回目: 1.2秒
- 2回目: 2.4秒
- 3回目: 3.6秒

## 実行例

### 例1: 標準設定で実行

```bash
python3 word.py --dir /path/to/excel
```

### 例2: カスタム設定で実行

```bash
export RATE_LIMIT_DELAY=1.5
export MAX_WORKERS=4
python3 word.py --dir /path/to/excel
```

### 例3: 低負荷モードで実行

```bash
export RATE_LIMIT_DELAY=2.0
export MAX_WORKERS=2
export RETRY=3
python3 word.py --dir /path/to/excel
```

## モニタリング

処理中は以下の情報が表示されます：

```
[INFO] 合計読み込み: 画面項目定義 100件, 単語帳 50件
[INFO] 処理中... (MAX_CONCURRENT_API=3, MAX_WORKERS=6)
処理進捗: 100%|████████████| 100/100 [02:45<00:00, 1.65s/it]
保存: out/match_result.xlsx
```

**仕組みの説明:**
- `MAX_WORKERS=6`: 最大6つのワーカースレッドが並列動作
- `MAX_CONCURRENT_API=3`: そのうち同時にAPI呼び出しできるのは3つまで
- 残りのワーカーはローカル処理（完全一致判定など）を実行
- API待機中のワーカーは自動的に待機し、処理中のAPI呼び出しが完了次第実行される

## トラブルシューティング

### 問題: APIエラーが多発する

**原因**: サーバー負荷が高い

**対策**:
```bash
export MAX_CONCURRENT_API=1  # API同時実行数を減らす
export MAX_WORKERS=3         # 並列数を減らす
```

### 問題: 処理が遅すぎる

**原因**: API同時実行数が少なすぎる

**対策**:
```bash
export MAX_CONCURRENT_API=5  # API同時実行数を増やす
export MAX_WORKERS=10        # 並列数を増やす
```

### 問題: タイムアウトエラー

**原因**: ネットワーク遅延

**対策**:
```bash
export TIMEOUT_SEC=60  # タイムアウトを延長
export RETRY=5         # リトライ回数を増やす
```

## ベストプラクティス

1. **最初は標準設定で実行**
   - `MAX_CONCURRENT_API=3`, `MAX_WORKERS=6`（デフォルト）

2. **エラーが出たら設定を調整**
   - エラー多発 → API同時実行数を減らす
   - 処理が遅い → API同時実行数を増やす

3. **本番環境では余裕を持った設定**
   - `MAX_CONCURRENT_API=2~3`
   - `MAX_WORKERS=4~6`

4. **大量データは分割処理を検討**
   - 1000件以上のデータは複数回に分けて処理

## 設定の保存

`.env`ファイルに保存して再利用：

```bash
# .env ファイルを作成
cat > .env << 'EOF'
# レート制限設定
MAX_CONCURRENT_API=3
MAX_WORKERS=6
RETRY=2
TIMEOUT_SEC=30

# API設定
OPENAI_BASE_URL=https://your-api-endpoint
OPENAI_API_KEY=your-api-key
EOF

# 実行
python3 word.py --dir /path/to/excel
```

## まとめ

| 設定項目 | デフォルト | 説明 |
|---------|-----------|------|
| `MAX_CONCURRENT_API` | 3 | 同時実行するAPI呼び出しの最大数 |
| `MAX_WORKERS` | 6 | 並列ワーカー数（ローカル処理含む） |
| `RETRY` | 2回 | エラー時のリトライ回数 |
| `TIMEOUT_SEC` | 30秒 | API応答のタイムアウト |

**重要:** `MAX_CONCURRENT_API` < `MAX_WORKERS` とすることで、API負荷を抑制しながらローカル処理は並列実行できます。

サーバーの状況に応じて適切な値に調整してください。