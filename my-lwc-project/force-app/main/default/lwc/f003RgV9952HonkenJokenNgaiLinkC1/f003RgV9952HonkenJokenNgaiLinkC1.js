import { LightningElement } from 'lwc';
 
export default class f003RgV9952HonkenJokenNgaiLinkC1 extends LightningElement {
    activeSections = ['b'];
    conditions = [
        { id: 1, transactionCondition: 'wwwwwwwwwwwwwwwwwwwwwwwwwww', selectedCondition: '' },
        { id: 2, transactionCondition: 'wwwwwwwwwwwwwwwwwwwwwwwwwww', selectedCondition: '' },
        { id: 3, transactionCondition: 'wwwwwwwwwwwwwwwwwwwwwwwwwww', selectedCondition: '' },
        { id: 4, transactionCondition: '', selectedCondition: '' },
        { id: 5, transactionCondition: '', selectedCondition: '' }
    ];
 
    honkenJokenComment = 'w'.repeat(366);
 
    conditionOptions = [
        { label: '荷受入に当行以外を指定', value: 'option1' },
        { label: '荷受入に当行以外を指定', value: 'option2' },
        { label: '荷受入に当行以外を指定', value: 'option3' },
        { label: '荷受入に当行以外を指定', value: 'option4' },
        { label: '荷受入に当行以外を指定', value: 'option5' }
    ];
 
    handleConditionChange(event) {
        const conditionId = event.target.dataset.id;
        const selectedCondition = event.target.value;
        this.conditions = this.conditions.map(condition => {
            if (condition.id === parseInt(conditionId, 10)) {
                return { ...condition, selectedCondition };
            }
            return condition;
        });
    }

    handleCommentChange(event) {
        this.honkenJokenComment = event.detail.value;
    }
}