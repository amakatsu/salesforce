// コンポーネントデータリスト取得のモック実装

export function getComponentDataList(elements, savingBtnList) {
    // モック実装：要素からデータを取得
    const itemList = {};
    const dataList = [];

    // 要素を走査してデータを収集
    if (elements && elements.length > 0) {
        elements.forEach(element => {
            const dataId = element.dataset.id;
            if (dataId && savingBtnList.includes(dataId)) {
                if (element.tagName === 'INPUT') {
                    itemList[dataId] = element.value || '';
                } else if (element.tagName === 'SELECT') {
                    itemList[dataId] = element.value || '';
                } else {
                    itemList[dataId] = element.textContent || '';
                }
                dataList.push(element);
            }
        });
    }

    return [itemList, dataList];
}