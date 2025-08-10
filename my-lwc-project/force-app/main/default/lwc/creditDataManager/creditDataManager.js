import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getCreditData from '@salesforce/apex/CollateralDataService.getCreditData';
import postCollateralData from '@salesforce/apex/CollateralDataService.postCollateralData';

export default class CreditDataManager extends LightningElement {
    @track creditData = [];
    @track showModal = false;
    @track modalTitle = '';
    @track selectedRecord = null;


    // テーブルのカラム定義
    columns = [
        { label: 'ID', fieldName: 'id', type: 'text' },
        { label: 'ラベル', fieldName: 'label', type: 'text', editable: true },
        { label: '期日', fieldName: 'dueDate', type: 'text', editable: true },
        { label: '率', fieldName: 'rate', type: 'text', editable: true },
        { label: '残高99', fieldName: 'balance99', type: 'currency', editable: true },
        { label: '元本', fieldName: 'principal', type: 'currency', editable: true },
        { label: '変更', fieldName: 'change', type: 'currency', editable: true },
        { label: '変更後残高', fieldName: 'postBalance', type: 'currency', editable: true },
        { label: '実残高', fieldName: 'actualBalance', type: 'currency', editable: true },
        { label: '修正', fieldName: 'correction', type: 'currency', editable: true },
        {
            type: 'action',
            typeAttributes: {
                rowActions: [
                    { label: '編集', name: 'edit' },
                    { label: '削除', name: 'delete' }
                ]
            }
        }
    ];

    // フォームのフィールド定義
    formFields = ['label', 'dueDate', 'rate', 'balance99', 'principal', 'change', 'postBalance', 'actualBalance', 'correction'];

    connectedCallback() {
        this.loadCreditData();
    }

    // 与信データを取得
    async loadCreditData() {
        try {
            const result = await getCreditData();
            this.creditData = JSON.parse(result);
        } catch (error) {
            this.showToast('エラー', 'データの取得に失敗しました: ' + error.body.message, 'error');
        }
    }

    // 新規作成ボタンクリック
    handleCreate() {
        this.modalTitle = '新規与信データ作成';
        this.selectedRecord = null;
        this.showModal = true;
    }

    // 更新ボタンクリック
    handleRefresh() {
        this.loadCreditData();
        this.showToast('成功', 'データを更新しました', 'success');
    }

    // 行アクション処理
    handleRowAction(event) {
        const actionName = event.detail.action.name;
        const row = event.detail.row;
        
        switch (actionName) {
            case 'edit':
                this.handleEdit(row);
                break;
            case 'delete':
                this.handleDelete(row);
                break;
        }
    }

    // 編集処理
    handleEdit(row) {
        this.modalTitle = '与信データ編集';
        this.selectedRecord = { ...row };
        this.showModal = true;
    }

    // 削除処理（DELETE APIが必要な場合はApexに追加）
    async handleDelete(row) {
        this.showToast('情報', '削除機能は現在準備中です', 'info');
    }

    // インライン保存処理
    async handleSave(event) {
        const recordInputs = event.detail.draftValues;
        
        try {
            for (const record of recordInputs) {
                await postCollateralData({ dataObj: record });
            }
            
            this.showToast('成功', 'データを更新しました', 'success');
            this.loadCreditData();
        } catch (error) {
            this.showToast('エラー', '更新に失敗しました: ' + error.body.message, 'error');
        }
    }

    // モーダルを閉じる
    closeModal() {
        this.showModal = false;
    }

    // フォーム送信成功処理
    async handleFormSuccess(event) {
        const formData = event.detail.fields;
        
        try {
            await postCollateralData({ dataObj: formData });
            
            this.showToast('成功', 
                this.selectedRecord ? 'データを更新しました' : 'データを作成しました', 
                'success');
            this.closeModal();
            this.loadCreditData();
        } catch (error) {
            this.showToast('エラー', '操作に失敗しました: ' + error.body.message, 'error');
        }
    }

    // トースト表示
    showToast(title, message, variant) {
        const evt = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(evt);
    }
}