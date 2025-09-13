// データバリデーションのモック実装

export function validateElement(elements) {
    // モック実装：基本的なバリデーション
    let isValid = true;
    const errors = [];

    if (elements && elements.length > 0) {
        elements.forEach(element => {
            const value = element.value || element.textContent || '';
            const required = element.hasAttribute('required');
            
            // 必須チェック
            if (required && !value.trim()) {
                isValid = false;
                errors.push({
                    element: element,
                    message: '必須項目です',
                    type: 'required'
                });
                element.classList.add('slds-has-error');
            } else {
                element.classList.remove('slds-has-error');
            }

            // メールアドレス形式チェック（email type の場合）
            if (element.type === 'email' && value && !isValidEmail(value)) {
                isValid = false;
                errors.push({
                    element: element,
                    message: '正しいメールアドレス形式で入力してください',
                    type: 'email'
                });
                element.classList.add('slds-has-error');
            }

            // 数値チェック（number type の場合）
            if (element.type === 'number' && value && isNaN(value)) {
                isValid = false;
                errors.push({
                    element: element,
                    message: '数値で入力してください',
                    type: 'number'
                });
                element.classList.add('slds-has-error');
            }
        });
    }

    return {
        isValid: isValid,
        errors: errors
    };
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}