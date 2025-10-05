# Excel単語照合ツール（LLM補助版）

業務システムの画面項目名と単語帳を照合し、lowerCamelCase形式の物理名を提案するPythonツールです。

## 🚀 主な機能

- **自動用語照合**: 画面項目定義と単語帳を自動で読み込み、類似度を計算
- **LLM判定**: OpenAI互換APIを使用して精密な一致判定と提案名生成
- **社内プロキシ対応**: プロキシ設定の自動検出とEXE対応
- **Excel出力**: 色分け・フィルター機能付きの見やすいレポート生成
- **エラー処理**: API失敗時の自動フォールバック機能

## 📋 必要なライブラリ

### 基本実行用

```bash
pip install pandas openpyxl python-dotenv requests certifi
```

### EXEビルド用（追加）

```bash
pip install pyinstaller win-inet-pton
```

## 🔧 設定

### 1. 環境設定ファイル（.env）の準備

初回実行時に自動的に`.env`ファイルが作成され、**社内プロキシ設定が自動検出**されます。

手動で設定する場合は、`.env`ファイルを作成：

```bash
# OpenAI互換API設定
OPENAI_BASE_URL=https://mufg-openai-api.azure-api.net/aoai001/openai/deployments/ptu
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_HEADERS_JSON={"api-key":"your-key","apim-user-id":"your-id"}

# プロキシ設定（自動検出されます。手動設定も可能）
HTTP_PROXY=http://proxy.company.local:8080
HTTPS_PROXY=http://proxy.company.local:8080

# 処理設定
FUZZY_THRESHOLD=0.72    # 類似度閾値
TOP_K=3                 # 候補の上位件数
MAX_WORKERS=6           # 並列処理スレッド数
MAX_CONCURRENT_API=5    # 同時API呼び出し数
```

### 2. 入力ファイルの配置

```
入力フォルダ/
├── *画面項目定義*.xlsx    ← 画面項目定義ファイル
├── *単語名一覧*.xlsx      ← 単語帳ファイル
└── ...
```

**必須列**：
- 画面項目定義: `項目名称`
- 単語帳: `論理名`, `物理名（正式名称）`, `No`

## 🎯 使い方

### 基本的な使い方

```bash
python word.py --dir ./data
```

### オプション指定

```bash
python word.py --dir ./data \
    --screen-col "項目名" \
    --vocab-col "論理名" \
    --out-dir ./output
```

### GUI起動（ダブルクリック）

引数なしで実行すると、フォルダ選択ダイアログが開きます。

### オプション一覧

- `--dir <パス>`: 入力ディレクトリ（画面項目定義・単語帳が入ったフォルダ）
- `--out-dir <パス>`: 出力ディレクトリ（デフォルト: `out`）
- `--screen-col <列名>`: 画面項目定義の列名（デフォルト: `項目名称`）
- `--vocab-col <列名>`: 単語帳の列名（デフォルト: `論理名`）
- `--no-gui`: GUIダイアログを使わない（サーバー/CI向け）

## 🔨 EXEファイルのビルド方法

### ステップ1: プロキシ設定の自動検出

まず通常のPython実行で、**社内プロキシ設定を`.env`ファイルに保存**します：

```cmd
python word.py --dir <テスト用ディレクトリ>
```

以下のようなメッセージが表示されます：
```
[INFO] 検出されたHTTPプロキシ: http://proxy.company.local:8080
[INFO] 検出されたHTTPSプロキシ: http://proxy.company.local:8080
[INFO] プロキシ設定を .env に保存しました
```

### ステップ2: 依存パッケージのインストール

```cmd
pip install pyinstaller certifi win-inet-pton
```

### ステップ3: EXEファイルのビルド

`.spec`ファイルを使ってビルドします：

```cmd
pyinstaller word.spec
```

ビルドが完了すると、`dist`フォルダに`word.exe`が生成されます。

### ステップ4: EXEファイルの配布

以下のファイルを配布します：

```
dist/
  ├── word.exe      ← 実行ファイル
  └── .env          ← 環境設定ファイル（プロキシ設定含む）
```

**重要**: `.env`ファイルを`word.exe`と同じフォルダに配置してください。

### トラブルシューティング（EXE実行時）

#### ホスト名が解決できない

**原因**: 社内DNS・プロキシ設定が正しく読み込まれていない

**解決策**:

1. `.env`ファイルが`word.exe`と同じフォルダにあるか確認
2. `.env`に正しいプロキシ設定があるか確認：
   ```bash
   HTTP_PROXY=http://proxy.company.local:8080
   HTTPS_PROXY=http://proxy.company.local:8080
   ```
3. 通常のPython実行（`python word.py`）で動作確認してから再ビルド

## 📊 処理フロー

### 1. ファイル読み込み（pandas）

```python
# Excelファイルの自動検出
screen_files = glob("*画面項目定義*.xlsx")
vocab_files = glob("*単語帳*.xlsx")

# ヘッダー行の自動検出
df = pd.read_excel(file, header=detected_header_row)
```

### 2. 前処理・正規化

```python
def zenkaku_hankaku_norm(s: str) -> str:
    """文字列正規化"""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[\\-/・,()\\[\\]_]+", " ", s)  # 記号を空白に
    return s.strip()
```

### 3. ローカル類似度計算

```python
def local_similarity(a: str, b: str) -> float:
    """類似度計算（difflib使用）"""
    a_n, b_n = zenkaku_hankaku_norm(a), zenkaku_hankaku_norm(b)

    if a_n == b_n: return 1.0        # 完全一致
    if a_n in b_n or b_n in a_n: return 0.9  # 部分一致

    return difflib.SequenceMatcher(None, a_n, b_n).ratio()
```

### 4. 候補抽出

```python
def phrase_candidates(screen_name: str, vocab_terms: List[str]) -> List[Candidate]:
    """複合語対応の候補抽出"""
    # トークン分割
    tokens = zenkaku_hankaku_norm(screen_name).split()

    # unigram + bigram生成
    grams = set(tokens)
    for i in range(len(tokens)-1):
        grams.add(tokens[i] + " " + tokens[i+1])

    # 各gramと全用語の類似度計算
    candidates = []
    for gram in grams:
        for vocab_term in vocab_terms:
            score = local_similarity(gram, vocab_term)
            if score >= threshold:
                candidates.append(Candidate(vocab_term, score))

    return sorted(candidates, key=lambda c: c.score, reverse=True)
```

### 5. LLM判定（バッチ処理）

```python
def call_llm_batch(items: List[str], candidates: List[Candidate]) -> List[Dict]:
    """100件まとめてLLM判定"""
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "system",
            "content": "用語統一の専門家として、複数の画面項目を一括判定してください"
        }, {
            "role": "user",
            "content": f"""
            # 画面項目リスト
            {json.dumps(items, ensure_ascii=False)}

            # 単語帳候補
            {json.dumps(candidates, ensure_ascii=False)}

            # JSON応答形式
            {{
              "results": [
                {{
                  "screen_item": "項目名",
                  "match_type": "完全一致|一部一致|一致なし",
                  "matched_term": "一致用語",
                  "matched_terms": ["複数", "用語"],
                  "reason": "判定理由",
                  "proposed_name": "推奨名",
                  "optimized_physical_name": "最適化物理名",
                  "coverage_ratio": 0.8
                }}
              ]
            }}
            """
        }],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(api_url, json=payload)
    return response.json()["choices"][0]["message"]["content"]
```

### 6. 結果集約・出力（openpyxl）

```python
def save_outputs(df: pd.DataFrame):
    """Excel出力（色付け・フォーマット付き）"""
    with pd.ExcelWriter("result.xlsx", engine="openpyxl") as writer:
        # データ出力
        df.to_excel(writer, sheet_name="結果", index=False)

        # 色付け
        ws = writer.sheets["結果"]
        colors = {
            "一部一致": PatternFill(start_color="FFEB9C"),  # 黄色
            "一致なし": PatternFill(start_color="FFC7CE"),    # 赤色
        }

        # 行ごとに色付け
        for row in range(2, len(df) + 2):
            match_type = ws.cell(row, match_col_idx).value
            if match_type in colors:
                for col in range(1, len(df.columns) + 1):
                    ws.cell(row, col).fill = colors[match_type]

        # スクロール固定
        ws.freeze_panes = "D2"
```

## 📈 出力結果

### Excelファイル構成

1. **結果シート**: 全項目の詳細結果（色分け付き）
2. **サマリシート**: 完全一致/一部一致/不一致の件数集計
3. **ファイル別サマリ**: 入力ファイル別の統計
4. **エラーログ**: API失敗項目の詳細

### 色分けルール

- **完全一致**: 色なし（白背景）→ そのまま使用可能
- **一部一致**: 🟡 黄色背景 → 確認・調整が必要
- **一致なし**: 🔴 赤色背景 → 新規定義が必要

### 主要な出力列

| 列名 | 説明 | 例 |
|------|------|------|
| 画面項目名 | 元の項目名 | "顧客コード" |
| 単語帳との一致結果 | 判定結果 | "一部一致" |
| 一致した単語 | 単一語での一致 | "顧客" |
| 複数単語での一致 | 複合語での一致 | "顧客, コード" |
| 類似度（0-1） | ローカル類似度 | 0.85 |
| 項目名のカバー率 | LLMが算出したカバー率 | 0.9 |
| 推奨する新しい項目名 | LLMによる提案 | "顧客識別コード" |

## 🔧 カスタマイズ

### 1. 閾値調整

```python
# 類似度閾値（0.0-1.0）
FUZZY_THRESHOLD = 0.72  # デフォルト

# より厳密： 0.8-0.9
# より緩い： 0.5-0.7
```

### 2. バッチサイズ調整

```python
# API制限に応じて調整
BATCH_SIZE = 100   # デフォルト
BATCH_SIZE = 50    # APIが不安定な場合
BATCH_SIZE = 200   # 高速化したい場合
```

### 3. 列名カスタマイズ

```bash
python word.py --dir ./data \
    --screen-col "項目名称" \
    --vocab-col "用語名"
```

## ⚠️ トラブルシューティング

### 1. ヘッダー検出失敗

```
KeyError: 必須列 ['項目名称'] を含むヘッダー行が見つかりませんでした。
```

**解決策**:
- `--screen-col` オプションで正しい列名を指定
- または環境変数で指定：
  ```bash
  SCREEN_COL=項目名称
  VOCAB_TERM_COL=論理名
  SCREEN_HEADER_ROW=3  # ヘッダー行を手動指定（3行目の場合）
  ```

### 2. API接続エラー

```
❌ DNS解決失敗: [Errno 11001] getaddrinfo failed
```

**解決策**:
1. プロキシ設定を確認：
   ```bash
   # .envファイルに追加
   HTTP_PROXY=http://proxy.company.local:8080
   HTTPS_PROXY=http://proxy.company.local:8080
   ```
2. 通常のPython実行で自動検出：
   ```cmd
   python word.py --dir <ディレクトリ>
   ```

### 3. Excel保存エラー

```
❌ ファイルが開かれています: match_result.xlsx
```

**解決策**: 出力先のExcelファイルを閉じてから再実行

## 📁 プロジェクト構成

```
word/
├── word.py                    # メインプログラム
├── word.spec                  # PyInstallerビルド設定
├── domain_check.py            # ドメイン固有の検証ツール
├── README.md                  # このファイル
├── RATE_LIMIT_GUIDE.md       # API制限対応ガイド
├── .env                       # 環境設定（プロキシ、APIキーなど）
├── tests/                     # テストファイル
│   ├── __init__.py
│   ├── mock_api.py           # モックAPI応答
│   ├── run_tests.py          # テスト実行スクリプト
│   ├── test_word_matching.py
│   ├── test_functions.py
│   ├── test_partial_matching.py
│   └── test_sheet_matching.py
└── dev/                       # 開発中・実験的機能（現在は空）
    └── README.md
```

## 📚 技術詳細

### 使用ライブラリ

- **pandas**: Excelファイル読み書き、データ処理
- **openpyxl**: Excel書式設定、色付け
- **difflib**: 文字列類似度計算
- **requests**: HTTP API通信
- **unicodedata**: 文字正規化
- **concurrent.futures**: 並列処理（予約、現在は順次処理）

### アーキテクチャ

```
入力Excel → 前処理 → 候補抽出 → LLM判定 → 結果集約 → Excel出力
     ↓         ↓         ↓         ↓         ↓         ↓
   pandas   正規化    difflib   OpenAI    pandas   openpyxl
```

### パフォーマンス

- **1000件の場合**: 約10分（100件×10バッチ）
- **API呼び出し回数**: 1/100に削減（バッチ処理）
- **メモリ使用量**: 中程度（全データをメモリ上で処理）

## 📞 サポート

問題が発生した場合は、以下の情報をお知らせください：

1. エラーメッセージ全文
2. 入力ファイルの形式・サンプル
3. 実行コマンド
4. 出力されたエラーログシートの内容

---

**開発**: Claude Code Assistant
**バージョン**: 2.0
**最終更新**: 2025年1月