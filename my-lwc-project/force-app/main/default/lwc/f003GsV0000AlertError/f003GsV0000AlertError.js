import { LightningElement, api } from 'lwc';

export default class F003GsV0000AlertError extends LightningElement {
    @api size;
    @api message;
    @api code;

    /**
     * Sample1互換のアラートダイアログ表示
     * @param {Object} config - 設定オブジェクト
     * @param {string} config.size - ダイアログサイズ
     * @param {string} config.message - 表示メッセージ
     * @param {string} config.code - エラーコード
     * @returns {Promise<string>} ユーザーの応答（Sample1仕様に合わせて空文字を返す）
     */
    static async open(config) {
        return new Promise((resolve) => {
            const { size, message, code } = config;

            // confirm()ダイアログでSample1の挙動を再現
            const userResponse = confirm(
                `【AlertError】\n\n` +
                `エラーコード: ${code}\n` +
                `メッセージ: ${message}\n\n` +
                `OK をクリックして続行します。`
            );

            // Sample1の仕様に合わせて空文字を返す
            resolve("");
        });
    }

    handleClose() {
        this.dispatchEvent(new CustomEvent('close'));
    }
}