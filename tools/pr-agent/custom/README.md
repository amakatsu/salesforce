# カスタムLLMハンドラー

このディレクトリには、PR-Agentのデフォルト動作をカスタマイズするためのファイルを配置します。

## 📁 ディレクトリ構成

```
custom/
├── README.md                    # このファイル
└── litellm_ai_handler.py       # カスタムLLMハンドラー（オプション）
```

## 🔧 カスタマイズ方法

### LLMハンドラーのカスタマイズ

PR-AgentのLLMハンドラーをカスタマイズする場合、以下の手順で実施します：

1. **カスタムハンドラーファイルを作成**
   ```bash
   # カスタムハンドラーを作成
   cp <元のファイル> tools/pr-agent/custom/litellm_ai_handler.py
   # または新規作成
   touch tools/pr-agent/custom/litellm_ai_handler.py
   ```

2. **カスタマイズ内容を実装**
   - Gemini API固有の設定
   - リトライロジックの調整
   - レスポンス処理のカスタマイズ
   - など

3. **Dockerビルド時に自動適用**

   Dockerfileに以下の処理が含まれています：
   ```dockerfile
   # カスタムLLMハンドラーが存在する場合は上書き
   RUN if [ -f /app/pr-agent/custom/litellm_ai_handler.py ]; then \
       cp /app/pr-agent/custom/litellm_ai_handler.py \
          /usr/local/lib/python3.11/site-packages/pr_agent/algo/ai_handlers/litellm_ai_handler.py; \
       echo "✅ カスタムLLMハンドラーを適用しました"; \
   fi
   ```

## 📝 使用例

### Gemini API用カスタマイズ例

```python
# custom/litellm_ai_handler.py
from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler

class LiteLLMAIHandler(BaseAiHandler):
    def __init__(self):
        super().__init__()
        # Gemini固有の設定
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"

    async def chat_completion(self, model, messages, **kwargs):
        # カスタムロジックを実装
        # ...
        pass
```

## 🚀 適用確認

カスタムハンドラーが適用されているか確認：

```bash
# Dockerコンテナ内で確認
docker exec dev-tools-web ls -la /usr/local/lib/python3.11/site-packages/pr_agent/algo/ai_handlers/litellm_ai_handler.py

# ログで確認
docker logs dev-tools-web | grep "カスタムLLMハンドラー"
```

## ⚠️ 注意事項

- カスタムハンドラーファイルは `.gitignore` に追加することを推奨（API固有の設定が含まれる可能性があるため）
- PR-Agentのバージョンアップ時は、互換性を確認してください
- カスタマイズによる動作保証はありません

## 🔗 関連リンク

- [PR-Agent公式ドキュメント](https://github.com/Codium-ai/pr-agent)
- [LiteLLM公式ドキュメント](https://docs.litellm.ai/)
