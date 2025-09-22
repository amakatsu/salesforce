import { LightningElement, api, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { validateElement } from 'c/f003GsV0000DataValidation';

export default class RirituKeisuPage extends LightningElement {
    @api activeTab = 'riritu';
    @api rirituData;
    @api keisuData;

    /* データ管理（Single Source of Truth） */
    @track multiHeaderData = [];

    /* ライフサイクル・データ初期化 */
    connectedCallback() {
        this.initializeMultiHeaderData();
    }

    initializeMultiHeaderData() {
        // 本番時削除：モックデータは子コンポーネントで生成
        // 親では空配列のまま（子が自動でモックデータを生成）
        this.multiHeaderData = [];
    }

    disconnectedCallback() {
        // クリーンアップ処理（現在は不要）
    }

    /* エラーハンドリング */
    /* 子コンポーネントからのエラー通知処理 */
    handleValidationError(event) {
        const { message, field, value, recordId } = event.detail;
        
        // より具体的なエラーメッセージを構築
        let errorMessage = '';
        if (field && value !== undefined) {
            errorMessage = `「${field}」フィールドの入力値「${value}」が無効です。`;
        } else {
            errorMessage = message || '入力値に問題があります。';
        }
        
        // コンソールに詳細ログを出力
        console.error('Validation Error:', {
            field,
            value,
            recordId,
            message,
            timestamp: new Date().toISOString()
        });

        // トーストでエラー表示
        this.showValidationErrorToast('入力エラー', errorMessage);
    }

    

    showValidationErrorToast(title, message) {
        this.dispatchEvent(
            new ShowToastEvent({
                title: title,
                message: message,
                variant: 'error'
            })
        );
    }

    /* フィールド変更通知 */
    handleFieldChange() {
        // フィールド変更の通知を受け取る（必要に応じて処理を追加）
    }

    /* バリデーション検証用メソッド */
    /**
     * 対象コンポーネントの選択データをvalidation
     * @param {HTMLElement} targetComponent 対象の子コンポーネント
     * @returns {Object} {errorCount: number, errorDetails: Array}
     */
    validateAllInputs(targetComponent) {
        // 選択されたレコードのIDを取得
        const allData = targetComponent.tableData || [];
        const selectedIds = allData
            .filter(item => item.checked)
            .map(item => item.Id);

        if (selectedIds.length === 0) {
            return { errorCount: 0, errorDetails: [] };
        }

        // validation実行
        let totalErrorCount = 0;
        const errorDetails = [];

        selectedIds.forEach(recordId => {
            const elements = targetComponent.getElementsById(recordId);
            elements.forEach(element => {
                const errorCount = validateElement([element], [], []);
                if (errorCount > 0) {
                    totalErrorCount += errorCount;
                    errorDetails.push({
                        field: element.dataset.field || '不明',
                        value: element.type === 'checkbox' ? element.checked : element.value,
                        recordId: element.dataset.id
                    });
                }
            });
        });

        return { errorCount: totalErrorCount, errorDetails };
    }

    /* 保存処理 */
    handleSave(event) {
        // クリックされたボタンのdata-component属性を取得
        const componentType = event.target.dataset.component;

        // 対応するコンポーネントを選択
        let targetComponent;
        if (componentType === 'opc') {
            targetComponent = this.template.querySelector('c-row-dynamic-o-p-c');
        } else if (componentType === 'multi') {
            targetComponent = this.template.querySelector('c-row-dynamic-multi-header');
        } else {
            // フォールバック: 両方のコンポーネントを確認
            const multiHeaderComponent = this.template.querySelector('c-row-dynamic-multi-header');
            const opcComponent = this.template.querySelector('c-row-dynamic-o-p-c');
            targetComponent = multiHeaderComponent || opcComponent;
        }

        if (!targetComponent) {
            alert('コンポーネントが見つかりません。');
            return;
        }

        try {
            // tableDataプロパティから直接データを取得
            const allData = targetComponent.tableData || [];
            const selectedData = allData.filter(item => item.checked);

            if (selectedData.length === 0) {
                alert(`保存するデータが選択されていません。\n\n詳細:\n・全データ数: ${allData.length}件\n・選択データ数: ${selectedData.length}件\n\nテーブルで行を選択してから保存してください。`);
                return;
            }

            // 保存前に子コンポーネントの全入力要素でvalidation実行
            const validationResult = this.validateAllInputs(targetComponent);

            if (validationResult.errorCount > 0) {
                // 具体的なエラー詳細を含むメッセージを構築
                let errorMessage = `入力データに${validationResult.errorCount}件のエラーがあります：\n\n`;

                validationResult.errorDetails.forEach((error, index) => {
                    errorMessage += `${index + 1}. フィールド「${error.field}」`;
                    if (error.value !== undefined && error.value !== '') {
                        errorMessage += `の値「${error.value}」`;
                    }
                    errorMessage += 'が無効です\n';
                });

                errorMessage += '\nエラーを修正してから保存してください。';

                this.showValidationErrorToast('保存エラー', errorMessage);
                return;
            }

            // 保存処理実行
            this.performSave({ tableData: selectedData });

        } catch (error) {
            console.error('保存処理エラー:', error);
            this.showValidationErrorToast('保存エラー', `保存に失敗しました: ${error.message}`);
        }
    }

    async performSave(itemList) {
        await new Promise(resolve => setTimeout(resolve, 500));

        const tableData = itemList.tableData || [];
        const selectedCount = tableData.length;

        alert(`${selectedCount}件のデータを保存しました。`);
    }
}