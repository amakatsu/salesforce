import { LightningElement, api, track } from 'lwc';

export default class RirituKeisuPage extends LightningElement {
    @api activeTab = 'riritu';
    @api rirituData;
    @api keisuData;

    /* データ管理（Single Source of Truth） */
    @track multiHeaderData = [];
    @track debugInfo = '';

    /* ライフサイクル・データ初期化 */
    connectedCallback() {
        this.initializeMultiHeaderData();
    }

    initializeMultiHeaderData() {
        // 本番時削除：モックデータは子コンポーネントで生成
        // 親では空配列のまま（子が自動でモックデータを生成）
        this.multiHeaderData = [];
    }

    /* フィールド変更通知 */
    handleFieldChange(event) {
        const { recordId, fieldName, newValue } = event.detail;
        console.log(`フィールド変更通知: ${recordId}.${fieldName} = ${newValue}`);
    }

    /* バリデーション検証用メソッド */
    handleValidationTest() {
        const multiHeaderComponent = this.template.querySelector('c-row-dynamic-multi-header');

        if (!multiHeaderComponent) {
            alert('コンポーネントが見つかりません。');
            return;
        }

        try {
            console.log('=== バリデーション検証開始 ===');
            console.log('multiHeaderComponent:', multiHeaderComponent);
            console.log('multiHeaderComponent.template:', multiHeaderComponent.template);

            // getSavingDatas()の呼び出しを安全にラップ
            let itemList, validationResult;
            try {
                const result = multiHeaderComponent.getSavingDatas();
                console.log('getSavingDatas() 戻り値:', result);

                if (Array.isArray(result) && result.length >= 2) {
                    [itemList, validationResult] = result;
                } else {
                    throw new Error(`getSavingDatas()の戻り値が不正です: ${JSON.stringify(result)}`);
                }
            } catch (innerError) {
                console.error('getSavingDatas()エラー:', innerError);
                this.debugInfo = `❌ getSavingDatas()でエラーが発生しました:
${innerError.message}

スタックトレース:
${innerError.stack}`;
                return;
            }

            console.log('バリデーション結果:', validationResult);
            console.log('取得データ:', itemList);

            // デバッグ情報を画面に表示（コンソールログから取得）
            this.debugInfo = `【バリデーション検証結果】
実行日時: ${new Date().toLocaleString()}
結果コード: ${validationResult}

【バリデーション状況】
・全data-id要素数: 34個
・validationElements数: 34個
・バリデーション結果: ${validationResult}

【問題の確認】
数値フィールドに文字列を入力してもvalidationResult=0となっています。
原因を調査中...

【考えられる原因】
1. validateElement関数が数値フィールドを正しく検出していない
2. SAVING_FIELD_LISTとdata-id属性が一致していない
3. バリデーション対象の要素が期待通りに取得されていない

コンソールログで詳細を確認してください。
`;

            if (validationResult !== 0) {
                this.debugInfo += `⚠️ バリデーションエラーが発生しました
エラーコード: ${validationResult}`;

                console.error('❌ バリデーションエラー詳細:', {
                    resultCode: validationResult,
                    itemList: itemList,
                    timestamp: new Date().toISOString()
                });
            } else {
                const tableData = itemList.tableData || [];
                const fixedDataKeys = Object.keys(itemList).filter(key => key !== 'tableData');

                this.debugInfo += `✅ バリデーション成功！

📊 データ概要:
・テーブルデータ: ${tableData.length}件
・固定要素: ${fixedDataKeys.length}項目`;

                if (fixedDataKeys.length > 0) {
                    this.debugInfo += `
・固定要素キー: ${fixedDataKeys.join(', ')}`;
                }

                console.log('✅ バリデーション成功詳細:', {
                    tableDataCount: tableData.length,
                    fixedDataKeys: fixedDataKeys,
                    fullData: itemList,
                    timestamp: new Date().toISOString()
                });
            }

        } catch (error) {
            console.error('バリデーション検証エラー:', error);
            alert(`❌ バリデーション検証に失敗しました\n\nエラー: ${error.message}\n\n詳細はコンソールを確認してください`);
        }
    }

    /* 保存処理 */
    handleSave() {
        const multiHeaderComponent = this.template.querySelector('c-row-dynamic-multi-header');

        if (!multiHeaderComponent) {
            alert('コンポーネントが見つかりません。');
            return;
        }

        try {
            const [itemList, validationResult] = multiHeaderComponent.getSavingDatas();

            if (validationResult !== 0) {
                return;
            }

            console.log('=== 保存処理開始 ===');
            console.log('保存データ:', itemList);
            this.performSave(itemList);

        } catch (error) {
            console.error('保存処理エラー:', error);
            alert(`保存に失敗しました: ${error.message}`);
        }
    }

    async performSave(itemList) {
        console.log('保存処理実行中...');
        await new Promise(resolve => setTimeout(resolve, 500));

        const tableData = itemList.tableData || [];
        const selectedCount = tableData.length;

        alert(`${selectedCount}件のデータを保存しました。`);
        console.log('保存完了');
    }
}