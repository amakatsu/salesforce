# Toast と Lightning Alert の使い分けガイド

| 目的                         | Toast (ShowToastEvent)                                                           | Lightning Alert (lightning-alert / lightning:alert)                                          |
| :--------------------------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| **ユーザーの操作をブロック** | しない – 画面端に数秒表示して自動で消える                                        | する – ダイアログが前面に出て「OK」等を押すまで他操作不可                                    |
| **情報の緊急度・重み**       | 軽微な通知・完了報告・一時的エラー<br>例: 「保存しました」「接続に失敗しました」 | 重要な確認・破壊的操作の警告・重大エラー<br>例: 「本当に削除しますか？」「権限がありません」 |
| **UX インパクト**            | 低 (非モーダル) – ユーザーのフローを妨げない                                     | 高 (モーダル) – 次のステップを明示的に促す                                                   |
| **アクセシビリティ**         | `role="status"` で読み上げられるが操作は続行可能                                 | `role="alertdialog"` でフォーカスが内部にトラップされ、操作完了まで外に戻らない              |
| **実装コスト**               | 1 行でイベント発火<br>`this.dispatchEvent(new ShowToastEvent({...}))`            | Promise ベースでハンドラーを書く<br>`await LightningAlert.open({message,theme});`            |
| **カスタマイズ**             | タイトル・メッセージ・variant(success/error/info)・duration                      | ボタンラベル・テーマ(warning/error/info)・アイコン・callback                                 |
| **複数同時表示**             | 可能（Stack される）                                                             | 原則 1 つずつ（次の alert は前の close 後）                                                  |

---

## 使い分けチェックリスト

- **ユーザーの手を止めずに知らせたい → Toast**
  - CRUD 完了・一時的ネットワーク失敗・軽い成功/警告
- **必ず確認・了承を取る／重大エラー → Alert**
  - 削除・データ損失・セッション切れ再ログイン etc.

---

## サンプル比較（LWC）

### Toast

```javascript
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

this.dispatchEvent(
  new ShowToastEvent({
    title: '保存完了',
    message: 'レコードが更新されました',
    variant: 'success',
    mode: 'dismissable', // sticky, pester, dismissable から選択
  }),
);
```

### Alert（LWC 公式モーダル）

```javascript
import LightningAlert from 'lightning/alert';

await LightningAlert.open({
  message: '本当に削除しますか？',
  theme: 'warning', // info / success / error / warning
  label: '確認',
});
// open() は Promise を返すので、後続処理は await 後に書く
```

> Aura では `<lightning:alert>` タグを使い、属性 `message`, `title`, `variant`, `onclick` 等で制御。

---

## ベストプラクティス

1.  **Toast を氾濫させない**
    - 同操作で 2 つ以上表示すると逆に気付かれない。
2.  **Alert は本当に必要か？**
    - モーダルは流れを断つため UX を下げやすい。設定変更・破壊的操作に限定。
3.  **テーマ/variant の一貫性**
    - 成功は green (`success`)、警告は yellow/orange (`warning`)、エラーは red (`error`)。
4.  **アクセシビリティ検証**
    - Alert 使用時は ESC キーで閉じられるか、toast はスクリーンリーダで読まれるか確認。
5.  **Error 処理の優先順位**
    - 軽微/自動復旧可 → **toast**
    - ユーザー対処必須 → **alert** + 手順リンク

---

## まとめ

- **Toast** = “チラ見せ” で OK なステータス更新や軽い失敗を伝える
- **Alert** = “必ず見てほしい” 破壊的・重大・確認系アクションを止めて伝える

この指針で設計すると、ユーザーのワークフローを邪魔せずに重要なメッセージを適切に届けられます。
