# Excel用語照合ツール（LLM補助版）

業務システムの画面項目名と単語帳を照合し、用語統一を支援するPythonツールです。

## 🚀 主な機能

- **自動用語照合**: 画面項目定義と単語帳を自動で読み込み、類似度を計算
- **LLM判定**: OpenAI互換APIを使用して精密な一致判定と提案名生成
- **バッチ処理**: 100件ずつまとめて処理し、API呼び出しを効率化
- **Excel出力**: 色分け・フィルター機能付きの見やすいレポート生成
- **エラー処理**: API失敗時の自動フォールバック機能

## 📋 必要なライブラリ

```bash
pip install pandas openpyxl python-dotenv requests
```

## 🔧 設定

### 1. APIキー設定（.env ファイル）

```bash
# OpenAI互換API設定
OPENAI_BASE_URL=https://your-api-endpoint.com
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# 処理設定
BATCH_SIZE=100          # バッチ処理サイズ
FUZZY_THRESHOLD=0.72    # 類似度閾値
MAX_WORKERS=6           # 並列処理数
```

### 2. ファイル配置

```
入力フォルダ/
├── 画面項目定義_システムA.xlsx
├── 単語帳_2024.xlsx
└── ...
```

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

### 1. API失敗時

```
❌ バッチAPI失敗: Connection timeout...
→ 個別処理にフォールバック中...
→ 個別処理でも3件失敗（フォールバック適用）
```

→ エラーログシートで詳細確認可能

### 2. Excel保存エラー

```
❌ ファイルが開かれています: match_result.xlsx
   ファイルを閉じてから Enter を押してください... (試行 1/3)
```

→ ファイルを閉じて Enter キーで再試行

### 3. ヘッダー検出失敗

```
KeyError: 必須列 ['項目名称'] を含むヘッダー行が見つかりませんでした。
```

→ `--screen-col` オプションで正しい列名を指定

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