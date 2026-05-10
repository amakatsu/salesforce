import { createElement } from 'lwc';
import { getCodeList, getCodeListWithBlank } from 'c/f003GsV0000Code';
import F003CvV0103KanrenRinsaJohoMC1 from 'c/f003CvV0103KanrenRinsaJohoMC1';
import { PATTERNS } from 'c/f003GsV0000Const';
import { C1_CHANGE_LIST, C1_CHANGE_REQ_LIST, C1_ADD_LIST, C1_ADD_REQ_LIST } from '../../f003CvV0103KanrenRinsaJohoMC1Const';
import { validateElement } from 'c/f003GsV0000DataValidation';
import { getComponentDataList } from 'c/f003GsV0000GetComponentDataList';
import * as C1Consts from '../../f003CvV0103KanrenRinsaJohoMC1Const';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

// 「与信禀査」外部コード
const MOCK_CREDIT_RINSA_OPTIONS = [
  { label: '★', value: '1', key: '0' },
  { label: '●', value: '2', key: '1' },
  { label: '', value: '', key: '' },
];

//「関連禀査」外部コード
const MOCK_RELATED_RINSA_OPTIONS = [
  { label: '●', value: '3', key: '0' },
  { label: '', value: '', key: '' },
];

//「抵触関連」外部コード
const MOCK_VIOLATION_RELATED_OPTIONS = [
  { label: '●', value: '4', key: '0' },
  { label: '', value: '', key: '' },
];

// 「区分選択」コンボ（遷移元が抵触・要管理シート以外）
const MOCK_CATEGORY_SELECT_OPTIONS = [
  { label: '--なし--', value: '' },
  { label: '与信禀査（メイン）', value: '1', key: '0' },
  { label: '与信禀査', value: '2', key: '1' },
  { label: '関連禀査', value: '3', key: '2' },
];

// 「区分選択」コンボ（遷移元が抵触・要管理シート）
const MOCK_CATEGORY_SELECT_TEISHOKU_OPTIONS = [
  { label: '--なし--', value: '' },
  { label: '抵触対応', value: '4', key: '0' },
];

// records（遷移元が抵触・要管理シート以外、かつ「hdnKanrenRinsaJohoCanUpdateFlg」がtrue）
const MOCK_RECODES_DATA_NORMAL = {
  relatedRinsaInfoList: [
    { seqNo: 11, categorySelect: '1', rsNo: '2234', rsSeqNo: '002', brNo: '020', cmNo: '2421932', cmName: '取引先名', lcNo: 2402455292, ketteiDate: '2025-05-01', creditRinsa: '2', relatedRinsa: '2', violationRelated: '2' },
  ],
  hdnExclusiveCount: 1,
  parameterList: { hdnRefNo: '012345678912', hdnSourceDispId: 'CvV0000', hdnBrNo: '223', hdnCmNo: '2234567', hdnKanrenRinsaJohoCanUpdateFlg: true },
};

// records（遷移元が抵触・要管理シート以外、かつ「hdnKanrenRinsaJohoCanUpdateFlg」がtrue）
const MOCK_RECODES_DATA = {
  relatedRinsaInfoList: [
    { seqNo: 10, categorySelect: '1', rsNo: '1234', rsSeqNo: '001', brNo: '010', cmNo: '2421931', cmName: '０１２３４', lcNo: 2402455291, ketteiDate: '2025-05-01', creditRinsa: '1', relatedRinsa: '1', violationRelated: '1' },
    { seqNo: 11, categorySelect: '1', rsNo: '2234', rsSeqNo: '002', brNo: '020', cmNo: '2421932', cmName: '取引先名', lcNo: 2402455292, ketteiDate: '2025-05-01', creditRinsa: '2', relatedRinsa: '2', violationRelated: '2' },
    { seqNo: 12, categorySelect: '1', rsNo: '3234', rsSeqNo: '003', brNo: '030', cmNo: '2421933', cmName: '取引先名', lcNo: 2402455293, ketteiDate: '2025-05-01', creditRinsa: '3', relatedRinsa: '3', violationRelated: '3' },
    { seqNo: 13, categorySelect: '1', rsNo: '4234', rsSeqNo: '004', brNo: '040', cmNo: '2421934', cmName: '取引先名', lcNo: 2402455294, ketteiDate: '2025-05-01', creditRinsa: '4', relatedRinsa: '4', violationRelated: '4' },
  ],
  hdnExclusiveCount: 1,
  parameterList: { hdnRefNo: '012345678912', hdnSourceDispId: 'CvV0000', hdnBrNo: '223', hdnCmNo: '2234567', hdnKanrenRinsaJohoCanUpdateFlg: true },
};

// records（遷移元が抵触・要管理シート、かつ「hdnKanrenRinsaJohoCanUpdateFlg」がfalse）
const MOCK_RECODES_TEISHOKU_DATA = {
  relatedRinsaInfoList: [
    { seqNo: 10, categorySelect: '1', rsNo: '1234', rsSeqNo: '001', brNo: '010', cmNo: '2421931', cmName: '０１２３４', lcNo: 2402455291, ketteiDate: '2025-05-01', creditRinsa: '1', relatedRinsa: '1', violationRelated: '1' },
    { seqNo: 11, categorySelect: '1', rsNo: '2234', rsSeqNo: '002', brNo: '020', cmNo: '2421932', cmName: '取引先名', lcNo: 2402455292, ketteiDate: '2025-05-01', creditRinsa: '2', relatedRinsa: '2', violationRelated: '2' },
    { seqNo: 12, categorySelect: '1', rsNo: '3234', rsSeqNo: '003', brNo: '030', cmNo: '2421933', cmName: '取引先名', lcNo: 2402455293, ketteiDate: '2025-05-01', creditRinsa: '3', relatedRinsa: '3', violationRelated: '3' },
    { seqNo: 13, categorySelect: '1', rsNo: '4234', rsSeqNo: '004', brNo: '040', cmNo: '2421934', cmName: '取引先名', lcNo: 2402455294, ketteiDate: '2025-05-01', creditRinsa: '4', relatedRinsa: '4', violationRelated: '4' },
  ],
  hdnExclusiveCount: 1,
  parameterList: { hdnRefNo: '012345678912', hdnSourceDispId: 'CvV0501', hdnBrNo: '223', hdnCmNo: '2234567', hdnKanrenRinsaJohoCanUpdateFlg: false },
};

// validateElementのモック
jest.mock(
  'c/f003GsV0000DataValidation',
  () => ({ validateElement: jest.fn() }),
  { virtual: true }
);

global.structuredClone = jest.fn((obj) => JSON.parse(JSON.stringify(obj)));

// getComponentDataListのモック
jest.mock(
  'c/f003GsV0000GetComponentDataList',
  () => ({ getComponentDataList: jest.fn() }),
  { virtual: true }
);

jest.mock(
  'c/f003GsV0000Code',
  () => ({ getCodeList: jest.fn(), getCodeListWithBlank: jest.fn() }),
  { virtual: true }
);

jest.mock('lightning/platformShowToastEvent', () => ({ ShowToastEvent: jest.fn() }));

// Helper function to wait until the microtask queue is empty. This is needed for promise
// timing when calling imperative Apex.
async function flushPromises() {
  return Promise.resolve();
}

describe('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', () => {
  afterEach(() => {
    getComponentDataList.mockClear();
    validateElement.mockClear();
  });

  afterEach(() => {
    // The jsdom instance is shared across test cases in a single file so reset the DOM
    while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
  });

  it('コンポーネント_f003CvV0103KanrenRinsaJohoMC1_正常系_brNoの定義チェック_2A', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    const input = element.shadowRoot.querySelector('lightning-input[data-id="brNo"]');

    expect(input).not.toBeNull();
    expect(input.label).toBe('店番');
    expect(input.type).toBe('text');
    expect(input.pattern).toBe(PATTERNS.HANKAKU_NUMBER.regex);
    expect(input.minLength).toBe('3');
    expect(input.maxLength).toBe('3');
  });

  it('コンポーネント_f003CvV0103KanrenRinsaJohoMC1_正常系_cmNoの定義チェック_2A', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    const input = element.shadowRoot.querySelector('lightning-input[data-id="cmNo"]');

    expect(input).not.toBeNull();
    expect(input.label).toBe('取引先番号');
    expect(input.type).toBe('text');
    expect(input.pattern).toBe(PATTERNS.HANKAKU_NUMBER.regex);
    expect(input.minLength).toBe('7');
    expect(input.maxLength).toBe('7');
  });

  it('コンポーネント_f003CvV0103KanrenRinsaJohoMC1_正常系_rsNoの定義チェック_2A', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    const input = element.shadowRoot.querySelector('lightning-input[data-id="rsNo"]');

    expect(input).not.toBeNull();
    expect(input.label).toBe('禀査番号');
    expect(input.type).toBe('text');
    expect(input.pattern).toBe(PATTERNS.HANKAKU_NUMBER.regex);
    expect(input.minLength).toBe('4');
    expect(input.maxLength).toBe('4');
  });

  it('コンポーネント_f003CvV0103KanrenRinsaJohoMC1_正常系_rsSeqNoの定義チェック_2A', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    const input = element.shadowRoot.querySelector('lightning-input[data-id="rsSeqNo"]');

    expect(input).not.toBeNull();
    expect(input.label).toBe('禀査番号(枝番)');
    expect(input.type).toBe('text');
    expect(input.pattern).toBe(PATTERNS.HANKAKU_NUMBER.regex);
    expect(input.minLength).toBe('3');
    expect(input.maxLength).toBe('3');
  });

  it('コンポーネント_f003CvV0103KanrenRinsaJohoMC1_正常系_lcNoの定義チェック_2A', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    const input = element.shadowRoot.querySelector('lightning-input[data-id="lcNo"]');

    expect(input).not.toBeNull();
    expect(input.label).toBe('案件番号');
    expect(input.type).toBe('text');
    expect(input.pattern).toBe(PATTERNS.HANKAKU_NUMBER.regex);
    expect(input.minLength).toBe('10');
    expect(input.maxLength).toBe('10');
  });

  it('メソッド_getChangeList_正常系_バリデーションチェックでエラーなし_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [{ dataset: { id: 'categorySelect' }, value: '1', name: '区分選択' }];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);
    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList, valid] = element.getChangeList();

    // Assert
    expect(itemList).toEqual(mockItemList);
    expect(valid).toEqual(0);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_CHANGE_LIST);
    expect(validateElement).toHaveBeenCalledTimes(1);
    expect(validateElement).toHaveBeenCalledWith(mockDataList, C1_CHANGE_REQ_LIST, expectedData);
  });

  it('メソッド_getChangeList_準正常系_バリデーションチェックで1件エラー（必須入力）_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [{ dataset: { id: 'categorySelect' }, value: '', name: '区分選択' }];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);
    validateElement.mockImplementation(() => 1);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList, valid] = element.getChangeList();

    // Assert
    expect(itemList).toEqual(mockItemList);
    expect(valid).toEqual(1);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_CHANGE_LIST);
    expect(validateElement).toHaveBeenCalledTimes(1);
    expect(validateElement).toHaveBeenCalledWith(mockDataList, C1_CHANGE_REQ_LIST, expectedData);
  });

  it('メソッド_getChangeList_異常系_呼び出し先メソッドでException発生時、エスカレーションする事_1C', async () => {
    // Arrange
    getComponentDataList.mockImplementation(() => {
      throw new Error('TestException');
    });

    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    try {
      element.getChangeList();
      fail('TestException did not occur');
    } catch (e) {
      expect(e.message).toEqual('TestException');
    }
  });

  it('メソッド_getChangeNoCheckList_正常系_エラーなし_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [{ dataset: { id: 'categorySelect' }, value: '1', name: '区分選択' }];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList] = element.getChangeNoCheckList();

    // Assert
    expect(itemList).toEqual(mockItemList);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_CHANGE_LIST);
    expect(validateElement).toHaveBeenCalledTimes(0);
  });

  it('メソッド_getChangeNoCheckList_異常系_呼び出し先メソッドでException発生時、エスカレーションする事_1C', async () => {
    // Arrange
    getComponentDataList.mockImplementation(() => {
      throw new Error('TestException');
    });

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    try {
      element.getChangeNoCheckList();
      fail('TestException did not occur');
    } catch (e) {
      expect(e.message).toEqual('TestException');
    }
  });

  it('メソッド_getAddList_正常系_バリデーションチェックでエラーなし_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [
      { dataset: { id: 'brNo' }, value: '111', name: '店番' },
      { dataset: { id: 'cmNo' }, value: '2222222', name: '取引先番号' },
      { dataset: { id: 'rsNo' }, value: '3333', name: '禀査番号' },
      { dataset: { id: 'rsSeqNo' }, value: '444', name: '枝番' },
      { dataset: { id: 'categorySelect' }, value: '1', name: '区分選択' },
    ];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);
    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList, valid] = element.getAddList();

    // Assert
    expect(itemList).toEqual(mockItemList);
    expect(valid).toEqual(0);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_ADD_LIST);
    expect(validateElement).toHaveBeenCalledTimes(1);
    expect(validateElement).toHaveBeenCalledWith(mockDataList, C1_ADD_REQ_LIST, expectedData);
  });

  it('メソッド_getAddList_準正常系_バリデーションチェックで1件エラー（必須入力）_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [
      { dataset: { id: 'brNo' }, value: '', name: '店番' },
      { dataset: { id: 'cmNo' }, value: '2222222', name: '取引先番号' },
      { dataset: { id: 'rsNo' }, value: '3333', name: '禀査番号' },
      { dataset: { id: 'rsSeqNo' }, value: '444', name: '枝番' },
      { dataset: { id: 'categorySelect' }, value: '1', name: '区分選択' },
    ];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);
    validateElement.mockImplementation(() => 1);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList, valid] = element.getAddList();

    // Assert
    expect(itemList).toEqual(mockItemList);
    expect(valid).toEqual(1);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_ADD_LIST);
    expect(validateElement).toHaveBeenCalledTimes(1);
    expect(validateElement).toHaveBeenCalledWith(mockDataList, C1_ADD_REQ_LIST, expectedData);
  });

  it('メソッド_getAddList_異常系_呼び出し先メソッドでException発生時、エスカレーションする事_1C', async () => {
    // Arrange
    getComponentDataList.mockImplementation(() => {
      throw new Error('TestException');
    });

    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    try {
      element.getAddList();
      fail('TestException did not occur');
    } catch (e) {
      expect(e.message).toEqual('TestException');
    }
  });

  it('メソッド_getAddNoCheckList_エラーなし_1ABDEF', async () => {
    // Arrange
    const mockItemList = ['item1', 'item2'];
    const mockDataList = [
      { dataset: { id: 'brNo' }, value: '111', name: '店番' },
      { dataset: { id: 'cmNo' }, value: '2222222', name: '取引先番号' },
      { dataset: { id: 'rsNo' }, value: '3333', name: '禀査番号' },
      { dataset: { id: 'rsSeqNo' }, value: '444', name: '枝番' },
      { dataset: { id: 'categorySelect' }, value: '1', name: '区分選択' },
    ];

    getComponentDataList.mockImplementation(() => [mockItemList, mockDataList]);
    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    const [itemList] = element.getAddNoCheckList();

    // Assert
    expect(itemList).toEqual(mockItemList);

    const expectedData = element.shadowRoot.querySelectorAll('[data-id]');

    expect(getComponentDataList).toHaveBeenCalledTimes(1);
    expect(getComponentDataList).toHaveBeenCalledWith(expectedData, C1_ADD_LIST);
    expect(validateElement).toHaveBeenCalledTimes(0);
  });

  it('メソッド_getAddNoCheckList_異常系_呼び出し先メソッドでException発生時、エスカレーションする事_1C', async () => {
    // Arrange
    getComponentDataList.mockImplementation(() => {
      throw new Error('TestException');
    });

    validateElement.mockImplementation(() => 0);

    const element = createElement('c-f003-cv-v0103-kanren-rinsa-joho-m-c1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    // Act
    element.records = {};
    document.body.appendChild(element);
    await flushPromises();

    try {
      element.getAddNoCheckList();
      fail('TestException did not occur');
    } catch (e) {
      expect(e.message).toEqual('TestException');
    }
  });

  it('メソッド_getSelectRecordList_正常系_行選択なしの場合、空の配列を返す_1B', () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    expect(element.getSelectRecordList()).toEqual([]);
  });

  it('メソッド_getSelectRecordList_正常系_行選択ありの場合、選択された行を返す_1B', () => {
    // Arrange
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    document.body.appendChild(element);

    function getSelectRecordList() {
      return this.row;
    }

    const Parent = { row: [1, 2, 3] };
    const result = getSelectRecordList.call(Parent);

    expect(result).toEqual([1, 2, 3]);
  });

  it('メソッド_dataSetting_準正常系_recordsがundefinedの場合メソッドが早期にリターン_1BE', async () => {
    getCodeList.mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = undefined;
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(0);

    getCodeList.mockReset();
  });

  it('メソッド_dataSetting_準正常系_recordsが空の場合メソッドが早期にリターン_1BE', async () => {
    getCodeList.mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = {};
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(0);

    getCodeList.mockReset();
  });

  it('メソッド_dataSetting_準正常系_recordsのタイプがオブジェクトでない場合メソッドが早期にリターン_1BE', async () => {
    getCodeList.mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = 'string';
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(0);

    getCodeList.mockReset();
  });

  it('メソッド_dataSetting_準正常系_recordsが空オブジェクトの場合メソッドが早期にリターン_1BE', async () => {
    getCodeList.mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = {};
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(0);

    getCodeList.mockReset();
  });

  it('メソッド_dataSetting_準正常系_COMPONENT_KEYに定義されているキーがrecordsにない場合_1B', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    const MOCK_RECODES_DATA2 = { sample: 'sample' };
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    document.body.appendChild(element);
    element.dispatchEvent = jest.fn();
    element.records = MOCK_RECODES_DATA2;

    await flushPromises();
    await flushPromises();

    expect(element.dispatchEvent).toHaveBeenCalledTimes(1);

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSettings_正常系_2回目呼び出し時に外部コード取得が行われないことを確認_1E', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    document.body.appendChild(element);

    element.records = MOCK_RECODES_DATA;

    await flushPromises();
    await flushPromises();

    expect(getCodeList).toHaveBeenCalledTimes(3);
    expect(getCodeListWithBlank).toHaveBeenCalledTimes(1);

    element.records = MOCK_RECODES_DATA;

    await flushPromises();
    await flushPromises();

    expect(getCodeList).toHaveBeenCalledTimes(3);
    expect(getCodeListWithBlank).toHaveBeenCalledTimes(1);

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSettings_正常系_処理の正常終了時(名称変換の対象項目がブランクの場合)_1A', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    const MOCK_RECODES_DATA2 = { ...MOCK_RECODES_DATA_NORMAL, relatedRinsaInfoList: MOCK_RECODES_DATA_NORMAL.relatedRinsaInfoList.map((item) => ({ ...item, creditRinsa: '', relatedRinsa: '', violationRelated: '' })) };

    element.records = MOCK_RECODES_DATA2;
    document.body.appendChild(element);

    await flushPromises();
    await flushPromises();

    const tableEle = element.shadowRoot.querySelector('lightning-datatable');

    expect(tableEle.data).toEqual([
      {
        seqNo: 11,
        categorySelect: '1',
        rsNo: '2234',
        rsSeqNo: '002',
        brNo: '020',
        cmNo: '2421932',
        cmName: '取引先名',
        lcNo: 2402455292,
        ketteiDate: '2025-05-01',
        creditRinsa: '',
        relatedRinsa: '',
        violationRelated: '',
        creditRinsaValue: '',
      },
    ]);

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSettings_正常系_処理の正常終了時(名称変換の対象項目の値が外部コードにない場合)_1A', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });
    const MOCK_RECODES_DATA2 = { ...MOCK_RECODES_DATA_NORMAL, relatedRinsaInfoList: MOCK_RECODES_DATA_NORMAL.relatedRinsaInfoList.map((item) => ({ ...item, creditRinsa: '99', relatedRinsa: '99', violationRelated: '99' })) };

    element.records = MOCK_RECODES_DATA2;
    document.body.appendChild(element);

    await flushPromises();
    await flushPromises();

    const tableEle = element.shadowRoot.querySelector('lightning-datatable');

    expect(tableEle.data).toEqual([
      {
        seqNo: 11,
        categorySelect: '1',
        rsNo: '2234',
        rsSeqNo: '002',
        brNo: '020',
        cmNo: '2421932',
        cmName: '取引先名',
        lcNo: 2402455292,
        ketteiDate: '2025-05-01',
        creditRinsa: '',
        relatedRinsa: '',
        violationRelated: '',
        creditRinsaValue: '99',
      },
    ]);

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSetting_正常系_処理正常（遷移元が抵触・要管理シート以外の場合）_1ABE', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = MOCK_RECODES_DATA;
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(3);
    expect(getCodeListWithBlank).toHaveBeenCalledTimes(1);
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '4');
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '5');
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '6');
    expect(getCodeListWithBlank).toHaveBeenCalledWith('cv_code00034', '1', '2');

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSetting_正常系_処理正常（遷移元が抵触・要管理シートの場合）_1ABE', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_TEISHOKU_OPTIONS);

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.records = MOCK_RECODES_TEISHOKU_DATA;
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(3);
    expect(getCodeListWithBlank).toHaveBeenCalledTimes(1);
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '4');
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '5');
    expect(getCodeList).toHaveBeenCalledWith('cv_code00034', '2', '6');
    expect(getCodeListWithBlank).toHaveBeenCalledWith('cv_code00034', '1', '3');

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();
  });

  it('メソッド_dataSetting_異常系_不明な例外発生の場合例外がキャッチする_1CE', async () => {
    getCodeList
      .mockImplementation(() => MOCK_CREDIT_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_RELATED_RINSA_OPTIONS)
      .mockImplementation(() => MOCK_VIOLATION_RELATED_OPTIONS);

    getCodeListWithBlank.mockImplementation(() => MOCK_CATEGORY_SELECT_OPTIONS);

    Object.defineProperty(C1Consts, 'COMPONENT_KEY', { value: undefined, configurable: true });

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.dispatchEvent = jest.fn();
    element.records = MOCK_RECODES_DATA;
    document.body.appendChild(element);

    expect(getCodeList).toHaveBeenCalledTimes(0);
    expect(element.dispatchEvent).toHaveBeenCalledTimes(1);

    getCodeList.mockReset();
    getCodeListWithBlank.mockReset();

    Object.defineProperty(C1Consts, 'COMPONENT_KEY', { value: ['relatedRinsaInfoList'], configurable: true });
  });

  it('メソッド_dataSetting_異常系_外部コード取得時に不明な例外発生の場合外部コード取得処理で例外がキャッチ_1CE', async () => {
    getCodeList.mockImplementation(() => {
      throw new Error('不明な例外が発生しました！');
    });

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.dispatchEvent = jest.fn();
    element.records = MOCK_RECODES_DATA;

    await flushPromises();

    expect(element.dispatchEvent).toHaveBeenCalledTimes(1);

    getCodeList.mockReset();
  });

  it('メソッド_clearSelectedRows_正常系_選択されている行のデータをクリア_1D', async () => {
    const datatableElement = document.createElement('lightning-datatable');

    datatableElement.dataset.id = 'relatedRinsaInfoList';
    datatableElement.selectedRows = [{ seqNo: '10' }];

    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.appendChild(datatableElement);

    expect(datatableElement.selectedRows).toEqual([{ seqNo: '10' }]);

    element.clearSelectedRows();

    expect(datatableElement.selectedRows).toEqual([]);
  });

  it('メソッド_checkSelectedRows_準正常系_行選択されていない場合_1B', async () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.dispatchEvent = jest.fn();
    document.body.appendChild(element);

    const mockEvent = new CustomEvent('rowselection', { detail: { selectedRows: [] } });
    const datatable = element.shadowRoot.querySelector('lightning-datatable');

    datatable.dispatchEvent(mockEvent);

    const result = await element.checkSelectedRows();

    expect(element.dispatchEvent).toHaveBeenCalledWith(expect.any(ShowToastEvent));
    expect(result).toBeUndefined();
  });

  it('メソッド_checkSelectedRows_正常系_行選択されている場合_1B', async () => {
    const element = createElement('c-f003-cv-v-0103-kanren-rinsa-joho-m-c-1', { is: F003CvV0103KanrenRinsaJohoMC1 });

    element.dispatchEvent = jest.fn();
    document.body.appendChild(element);

    const mockEvent = new CustomEvent('rowselection', { detail: { selectedRows: [{ id: '1', sample: 'sample' }] } });
    const datatable = element.shadowRoot.querySelector('lightning-datatable');

    datatable.dispatchEvent(mockEvent);

    const result = await element.checkSelectedRows();

    expect(element.dispatchEvent).not.toHaveBeenCalled();
    expect(result).toBe('');
  });
});