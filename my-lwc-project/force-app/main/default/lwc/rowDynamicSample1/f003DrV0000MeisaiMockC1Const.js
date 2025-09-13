// コンポーネント定数定義

export const COMPONENT_KEY = {
    MODAL_VIEW: 'modalView',
    TABLE_DATA: 'tableData',
    SELECTED_ROWS: 'selectedRows'
};

export const SAVING_BTN_LIST = [
    'input1',
    'input2', 
    'select1',
    'checkbox1'
];

export const API_DATA = {
    id: 'mock-record-001',
    dtoList: [
        {
            id: '001',
            name: 'サンプルレコード1',
            description: 'テスト用のサンプルデータ1',
            status: 'アクティブ',
            createdDate: '2024-01-01',
            checked: false,
            possibility: true
        },
        {
            id: '002', 
            name: 'サンプルレコード2',
            description: 'テスト用のサンプルデータ2',
            status: '処理中',
            createdDate: '2024-01-02',
            checked: false,
            possibility: false
        },
        {
            id: '003',
            name: 'サンプルレコード3', 
            description: 'テスト用のサンプルデータ3',
            status: '完了',
            createdDate: '2024-01-03',
            checked: false,
            possibility: true
        },
        {
            id: '004',
            name: 'サンプルレコード4',
            description: 'テスト用のサンプルデータ4', 
            status: 'アクティブ',
            createdDate: '2024-01-04',
            checked: false,
            possibility: false
        },
        {
            id: '005',
            name: 'サンプルレコード5',
            description: 'テスト用のサンプルデータ5',
            status: '処理中', 
            createdDate: '2024-01-05',
            checked: false,
            possibility: true
        }
    ]
};