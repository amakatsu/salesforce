# keisuコンポーネント テストリスト

## 1. 初期化テスト
- [x] コンポーネントが正常にレンダリングされる
- [x] connectedCallback()でデータが初期化される
- [x] creditRowsとcollateralRowsが空でない配列として初期化される
- [x] guarantorDataが5つの保証人で初期化される
- [x] activeSectionsが["d", "e"]で初期化される

## 2. ラベル・定数テスト
- [x] TABLE_HEADERSが正しい日本語ラベルを返す
- [x] ACCORDION_LABELSが正しいアコーディオンラベルを返す
- [x] BUTTON_LABELSが「保存」「リセット」ラベルを返す
- [x] MESSAGE_LABELSが正しいメッセージを返す
- [x] labels getterが全てのラベルオブジェクトを返す

## 3. 状態管理テスト
- [x] draft getterがstateServiceから正しい下書き状態を取得する
- [x] hasDraftが下書きの存在を正しく判定する
- [x] draftJsonが下書きデータをJSON文字列に変換する

## 4. 保存・リセット機能テスト
- [x] handleSave()で下書きがクリアされる
- [x] handleSave()でhighlightOnがtrueになる
- [x] handleSave()後にデータが更新される
- [x] handleReset()でstateServiceがリセットされる
- [x] handleReset()でhighlightOnがfalseになる

## 5. 展開/折りたたみテスト
- [x] handleToggle()で展開状態が正しく切り替わる
- [x] 展開されていないノードをクリックすると展開される
- [x] 展開されているノードをクリックすると折りたたまれる
- [x] データが正しく更新される

## 6. 編集機能テスト
- [x] handleEdit()で数値入力が正しく処理される
- [x] handleEdit()でテキスト入力が正しく処理される
- [x] handleEdit()でチェックボックス入力が正しく処理される
- [x] 無効化されたフィールドの編集が拒否される
- [x] 下書きデータが正しく更新される

## 7. 保証人入力テスト
- [x] handleInputChange()で保証人データが更新される
- [x] 正しいIDの保証人のみが更新される
- [x] 他の保証人データが変更されない

## 8. ツリー構造テスト
- [x] _flattenTree()が正しくツリーをフラット化する
- [x] ネストレベルが正しく計算される
- [x] 展開/折りたたみ状態に応じて子ノードが表示される
- [x] アイコンが展開状態に応じて変わる

## 9. フィールド状態テスト
- [x] _isFieldDisabled()が正しくフィールドの無効化を判定する
- [x] _hasFieldChanged()が変更を正しく検出する
- [x] フィールドのCSSクラスが変更状態に応じて適用される

## 10. エラーハンドリングテスト
- [x] numberErrorHandler()が数値入力エラーを処理する
- [x] 不正なnodeIdでの操作が安全に処理される
- [x] 存在しないフィールドの更新が安全に処理される