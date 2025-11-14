# SearchTool - Windows ビルドガイド

このガイドでは、Windows 環境で SearchTool をビルドする方法を説明します。

---

## 📋 前提条件

### 必須ソフトウェア

1. **Node.js 18 以上**
   - https://nodejs.org/
   - LTS版を推奨

2. **Git**
   - https://git-scm.com/download/win
   - Git Bash を含めてインストール

3. **Visual Studio Build Tools** または **Visual Studio**
   - https://visualstudio.microsoft.com/downloads/
   - 「C++ によるデスクトップ開発」ワークロードを選択

### オプション

- **ripgrep** (ローカル検索機能用)
  - https://github.com/BurntSushi/ripgrep/releases
  - `rg.exe` を PATH に追加

---

## 🚀 ビルド手順

### 1. プロジェクトの取得

```powershell
# リポジトリをクローン
git clone https://github.com/your-repo/searchtool.git
cd searchtool\app

# または既存のプロジェクトに移動
cd C:\path\to\searchtool\app
```

### 2. 依存関係のインストール

```powershell
# npm パッケージのインストール
npm install

# Playwright ブラウザのインストール（Web検索を使う場合）
npx playwright install chromium
```

### 3. TypeScript 型チェック

```powershell
npm run typecheck
```

エラーが出なければ OK です。

### 4. Windows ビルドの実行

```powershell
npm run build:win
```

ビルドには数分かかります。完了すると以下のファイルが生成されます：

```
release\1.0.0\SearchTool-Windows-1.0.0-Setup.exe
```

### 5. ビルド成果物の確認

```powershell
dir release\1.0.0
```

以下のファイルが表示されればビルド成功です：

- `SearchTool-Windows-1.0.0-Setup.exe` - インストーラー
- `win-unpacked\` - アンパック版（開発用）

---

## 🧪 ビルドしたアプリのテスト

### インストーラーのテスト

```powershell
# インストーラーを実行
.\release\1.0.0\SearchTool-Windows-1.0.0-Setup.exe
```

インストール後、スタートメニューから「SearchTool」を起動します。

### アンパック版の実行（開発用）

```powershell
# アンパック版を直接実行
.\release\1.0.0\win-unpacked\SearchTool.exe
```

---

## 🔧 トラブルシューティング

### エラー: `node-gyp` のビルドエラー

**原因**: Visual Studio Build Tools がインストールされていない

**解決方法**:

1. Visual Studio Installer を起動
2. 「C++ によるデスクトップ開発」をインストール
3. npm のキャッシュをクリアして再実行

```powershell
npm cache clean --force
npm install
```

### エラー: `electron-builder` のエラー

**原因**: 署名証明書の設定エラー

**解決方法**: 開発用には署名不要なので、無視して OK です。
商用リリースの場合は、証明書を取得して `electron-builder.json5` で設定してください。

### エラー: メモリ不足

**原因**: Node.js のメモリ制限

**解決方法**:

```powershell
# メモリ制限を増やす
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build:win
```

### 警告: アイコンが設定されていない

```
default Electron icon is used  reason=application icon is not set
```

**解決方法**: アイコンファイルを追加（オプション）

1. `public/icon.ico` を作成（256x256 推奨）
2. `electron-builder.json5` に以下を追加：

```json5
"win": {
  "icon": "public/icon.ico"
}
```

---

## 📦 配布準備

### インストーラーの配布

生成されたインストーラーをそのまま配布できます：

```
release\1.0.0\SearchTool-Windows-1.0.0-Setup.exe
```

### 署名（商用リリース時）

Windows Defender SmartScreen の警告を回避するには、コード署名証明書が必要です。

1. **証明書の取得**
   - DigiCert, Sectigo 等から購入
   - 年間 $100〜$500

2. **electron-builder.json5 の設定**

```json5
"win": {
  "certificateFile": "path/to/certificate.pfx",
  "certificatePassword": "your-password"
}
```

3. **ビルド**

```powershell
npm run build:win
```

---

## 🔄 継続的インテグレーション（CI）

GitHub Actions で Windows ビルドを自動化する例：

```yaml
name: Build Windows

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install
        working-directory: app

      - name: Build Windows
        run: npm run build:win
        working-directory: app

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: SearchTool-Windows
          path: app/release/1.0.0/*.exe
```

---

## 📊 ビルド成果物のサイズ

| ファイル | サイズ |
|---------|--------|
| Setup.exe | 約 160 MB |
| win-unpacked/ | 約 250 MB |

サイズを小さくするには：

1. `asar: true` を維持（デフォルト）
2. 不要な依存関係を削除
3. `electron-builder` の圧縮オプションを調整

---

## 🔗 関連ドキュメント

- [README.md](./README.md) - メインドキュメント
- [QUICKSTART.md](./QUICKSTART.md) - クイックスタート
- [CHANGELOG.md](./CHANGELOG.md) - 変更履歴
- [Electron Builder ドキュメント](https://www.electron.build/)

---

## ❓ よくある質問

### Q: Linuxでビルドした後、Windowsでビルドできますか？

A: はい、可能です。各プラットフォームで独立してビルドできます。

### Q: ビルド時間はどのくらいですか？

A: 初回は 5〜10 分、2回目以降はキャッシュにより 2〜3 分程度です。

### Q: インストーラーのUIをカスタマイズできますか？

A: はい、NSIS のカスタムスクリプトを使用できます。詳細は electron-builder のドキュメントを参照してください。

### Q: Windows 7 に対応していますか？

A: Electron 30 は Windows 10 以降のみサポートしています。

---
