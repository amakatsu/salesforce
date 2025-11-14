# SearchTool Documentation Hub

Single stop for explaining the product, running demos, and pointing teammates to deeper docs.

---

## 1. One-minute overview
- **Problem:** engineers hop between local folders, Redmine, SharePoint, Teams, and internal wikis when troubleshooting.
- **Solution:** Electron desktop app that issues one query to every source, shows an AI (Mastra) summary on the left and sortable hits on the right, and logs metrics for follow-up.
- **Stack:** Electron 30 + React 18, Mastra agent, MCP servers (rg/rga + Playwright), TypeScript everywhere.

> **Takeaway:** “One search box, all sources, instant summary.” Use this line when opening a briefing.

---

## 2. Architecture snapshot
- **Renderer (React/Vite)** – Search tab = keyword input + source pills + hit-cap control + Mastra summary/results columns. Metrics & Settings tabs hang off the same shell.
- **Main process (Electron/Node)** – IPC handlers for settings, search, and metrics. Logger writes JSONL.
- **Search pipeline** – Renderer → `searchService` → Mastra agent (or fallback MCPs) → deduped hits + metrics → Renderer.
- **MCP servers** – Local FS, Redmine UI, SharePoint, Teams, Internal Docs. Each can be toggled per query.

Key files: `app/src/renderer/App.tsx`, `app/src/renderer/components/SearchPane.tsx`, `app/src/main/services/searchService.ts`, `app/src/main/mastra/agent.ts`.

---

## 3. Setup checklist
1. `cd searchtool/app && npm install`
2. `npx playwright install chromium` (only if SharePoint/Redmine/Teams searches are needed)
3. Install ripgrep (`sudo apt install ripgrep` or `brew install ripgrep`)
4. Launch once with `npm run dev`, open **設定** tab, and fill:
   - AI key + model (default `openai/gpt-4o-mini`)
   - Local search roots, exclusion globs
   - Redmine / SharePoint / Teams / Internal Docs URLs
   - Optional browser user data dir to reuse logins
5. Click **保存**, switch to **検索** tab, and you are ready.

---

## 4. Demo flow (≈3 minutes)
1. **Settings tab** – show AI section, multiple source URLs, and limits section.
2. **Search tab** – highlight keyword box, source pills, and “取り込む最大件数”.
3. Run `API 認証 エラー`:
   - Spinner → Mastra summary (left column)
   - Click `統合結果 → Local → Redmine → SharePoint → Teams → 社内Docs` on the right
4. Toggle one pill (e.g., disable SharePoint) and re-run to show backend filtering.
5. **Metrics tab** – show totals + recent history.

Narration: “Per query we decide which sources to hit, cap the number of hits, and still get an AI brief before reading raw lines.”

---

## 5. Screenshot & collateral workflow
All PNGs live under `app/screenshots/`:
- `01-settings-full.png` … `06-info-box.png` for general UI
- `linux/*.png` for the current Linux Electron run (search, metrics, settings, home)

### 5.1 Environment variables
| 変数 | 役割 |
| --- | --- |
| `SCREENSHOT_PATH` | 出力する PNG ファイルの絶対パス（必須） |
| `SCREENSHOT_VIEW` | 初期表示タブ (`search` `metrics` `settings`) |
| `SCREENSHOT_SEARCH_TAB` | 検索タブ内で開くサブタブ (`combined` `local` `redmine` `sharepoint` `teams` `internalDocs`) |
| `SCREENSHOT_KEYWORD` | 検索キーワード欄に事前入力する文字列 |
| `SCREENSHOT_SAMPLE_FILE` | `SearchResponse` 形式の JSON。読み込むと検索結果 UI にサンプルが描画される |
| `SCREENSHOT_METRICS_FILE` | `SearchRecord[]` 形式の JSON。読み込むと統計タブにダミーデータが表示される |
| `SCREENSHOT_DELAY_MS` | 画面描画後にキャプチャするまでの待機時間 (ms)。デフォルト 400 |

サンプル JSON は `app/screenshots/samples/` にあります。

### 5.2 コマンド例
**検索タブ（Mastra要約 + 統合タブ）**
```bash
cd searchtool/app
SCREENSHOT_PATH="./screenshots/linux/linux-search.png" SCREENSHOT_VIEW=search SCREENSHOT_KEYWORD="API 認証 エラー" SCREENSHOT_SEARCH_TAB=combined SCREENSHOT_SAMPLE_FILE="./screenshots/samples/search-response.json" ELECTRON_DISABLE_GPU=1 xvfb-run -s "-screen 0 1400x900x24" npm exec electron dist-electron/main.js
```

**統計タブ**
```bash
cd searchtool/app
SCREENSHOT_PATH="./screenshots/linux/linux-metrics.png" SCREENSHOT_VIEW=metrics SCREENSHOT_METRICS_FILE="./screenshots/samples/metrics-history.json" ELECTRON_DISABLE_GPU=1 xvfb-run -s "-screen 0 1400x900x24" npm exec electron dist-electron/main.js
```

**設定タブ**
```bash
cd searchtool/app
SCREENSHOT_PATH="./screenshots/linux/linux-settings.png" SCREENSHOT_VIEW=settings ELECTRON_DISABLE_GPU=1 xvfb-run -s "-screen 0 1400x900x24" npm exec electron dist-electron/main.js
```

### 5.3 画面説明ポイント
1. **検索タブ**: キーワード → ソースピル/最大件数 → 検索 → 左でAI要約・右でタブ切替
2. **統計タブ**: 総検索回数、平均処理時間、ソース別ヒット、履歴、`更新/クリア` ボタン
3. **設定タブ**: AIキー、ローカルルート、各WebソースURL、除外パターン、ブラウザ設定

---

## 6. Status soundbite
- **完成度:** ~95%。Linux AppImage (156 MB) ビルド済み。Windows NSIS パッケージは未着手。
- **テスト:** `npm run typecheck` と `npm exec vite build` はグリーン。MCPごとのE2Eは手動検証のみ。
- **次のステップ:** 依存サービスごとの自動テスト拡充、Windows 配布、検索フィルター（期間/ファイル種別）の検討。

---

## 7. Reference map
| トピック | ファイル |
| --- | --- |
| プロダクト概要 / デモ台本 | `docs/external/README.md`（このファイル） |
| クイックスタート | `docs/external/QUICKSTART.md` |
| プレゼン資料 | `docs/external/PRESENTATION.md` |
| UI レイアウト（ASCII） | `docs/external/VISUAL_GUIDE.md` |
| 実装状況・未完了タスク | `docs/internal/STATUS.md` |
| 変更履歴 / リリースノート | `docs/internal/CHANGELOG.md`, `docs/internal/RELEASE_NOTES_v1.0.0.md` |
| Windows ビルド手順 | `docs/internal/WINDOWS_BUILD.md` |
| バックログ / 課題リスト | `docs/internal/issues.md` |

Use the hub as the canonical entry point; other files dive deeper when needed.
