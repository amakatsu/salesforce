/**
  * レコード値変更共通処理
  * 
  * @param {Event} event イベント
  */
handleRecordValueChange(event) {
// データレコードの更新
this.record[event.target.dataset.id] = event.target.value;
console.log('record:'+ JSON.stringify(this.record));
 
// バリデーションチェック実施
const inputElement = event.target;
const childDataList = [inputElement];
validateElement(childDataList);
 }
 
/**
  * チェックボックス値変更共通処理
  * 
  * @param {Event} event イベント
  */
handleRecordCheckedChange(event) {
// データレコードの更新
this.record[event.target.dataset.id] = event.detail.checked === true ? true : false;
console.log('record:'+ JSON.stringify(this.record));
// バリデーションチェック実施
const inputElement = event.target;
const childDataList = [inputElement];
validateElement(childDataList);
 }