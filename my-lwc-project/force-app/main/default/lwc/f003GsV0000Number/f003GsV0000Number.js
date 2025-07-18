import { LightningElement, api, track } from 'lwc';

export default class F003GsV0000Number extends LightningElement {
    @api numValue;
    @api numLabel = '';
    @api isTable = false;
    @api disabled = false;
    @api step = '1';
    @api setId = '';

    get inputVariant() {
        return this.isTable ? 'label-hidden' : 'standard';
    }

    get inputClass() {
        return this.isTable ? 'table-number-input' : '';
    }

    handleNumberChange(event) {
        const value = event.target.value;
        
        // 数値バリデーション
        if (value && isNaN(value)) {
            this.dispatchEvent(new CustomEvent('error', {
                detail: {
                    message: '数値を入力してください',
                    field: this.setId
                }
            }));
            return;
        }

        // 変更イベントを親コンポーネントに送信
        this.dispatchEvent(new CustomEvent('change', {
            detail: {
                value: value,
                field: this.setId,
                id: this.template.host.dataset.id
            }
        }));
    }
}