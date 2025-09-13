import { LightningElement, api } from 'lwc';

export default class F003GsV0000AlertError extends LightningElement {
    @api size;
    @api message;
    @api code;

    // アラートエラー表示のモック実装
    static async open(config) {
        return new Promise((resolve) => {
            // モック実装：コンソールにメッセージを出力し、空文字を返す
            console.error(`Error Code: ${config.code}`);
            console.error(`Error Message: ${config.message}`);
            
            // 実際の実装では、ユーザーがOKボタンを押すまで待つ
            // ここでは簡単なモックとして即座に解決
            setTimeout(() => {
                resolve("");
            }, 100);
        });
    }

    handleClose() {
        this.dispatchEvent(new CustomEvent('close'));
    }
}