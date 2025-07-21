import { LightningElement, track } from "lwc";
import { stateService } from './rirituState';

const GUARANTOR_COLUMNS = [
  { label: "保証人", fieldName: "name", type: "text" }
];

export default class f003RgV0501YushiRingiShoSateiShoKeisuJohoC2 extends LightningElement {
  activeSections = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r"
  ];

  @track guarantorData = generateGuarantorData();

  guarantorColumns = GUARANTOR_COLUMNS;

  handleInputChange(event) {
    const { id, field } = event.currentTarget.dataset;
    const value = event.target.value;
    this.updateData(this.creditRows, id, field, value);
    this.updateData(this.collateralRows, id, field, value);
  }

  updateData(data, id, field, value) {
    const item = data.find((row) => row.id === id);
    if (item) {
      item[field] = value;
    }
  }

  @track creditRows = [];
  @track collateralRows = [];
  highlightOn = false;

  get draft() {
    return stateService.getState().draft;
  }
  get hasDraft() {
    return this.draft.size > 0;
  }
  get draftJson() {
    return JSON.stringify(Object.fromEntries(this.draft), null, 2);
  }

  connectedCallback() {
    stateService.initializeState();
    this.creditRows = this.flatten(stateService.getState().creditSource, false);
    this.collateralRows = this.flatten(
      stateService.getState().collateralSource,
      false
    );
  }

  /* ---------- SAVE / RESET ---------- */
  handleSave() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this.creditRows = this.flatten(stateService.getState().creditSource, true);
    this.collateralRows = this.flatten(
      stateService.getState().collateralSource,
      true
    );
  }
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this.creditRows = this.flatten(stateService.getState().creditSource, false);
    this.collateralRows = this.flatten(
      stateService.getState().collateralSource,
      false
    );
  }

  /* ---------- TOGGLE / EDIT ---------- */
  handleToggle(e) {
    const { creditSource, collateralSource, expanded } =
      stateService.getState();
    const id = e.currentTarget.dataset.id;
    expanded.has(id) ? expanded.delete(id) : expanded.add(id);
    this.creditRows = this.flatten(creditSource, this.highlightOn);
    this.collateralRows = this.flatten(collateralSource, this.highlightOn);
  }

  handleEdit(e) {
    const id = e.target.dataset.id;
    const field = e.target.dataset.field;
    const value = field === "active" ? e.target.checked : e.target.value;

    const creditRow = this.creditRows.find((r) => r.id === id);
    const collateralRow = this.collateralRows.find((r) => r.id === id);
    if (creditRow && creditRow[`${field}Disabled`]) return; // 編集不可なら無視
    if (collateralRow && collateralRow[`${field}Disabled`]) return; // 編集不可なら無視

    const { creditSource, collateralSource, draft } = stateService.getState();
    this.updateNode(creditSource, id, field, value); // ソース更新
    this.updateNode(collateralSource, id, field, value); // ソース更新

    const prev = draft.get(id) || {};
    draft.set(id, { ...prev, [field]: value }); // draft へ

    this.creditRows = this.flatten(creditSource, this.highlightOn);
    this.collateralRows = this.flatten(collateralSource, this.highlightOn);
  }

  /* ---------- tree -> flat ---------- */
  flatten(tree, highlight, level = 0, out = []) {
    const { expanded, originalCreditSource, originalCollateralSource, draft } =
      stateService.getState();

    tree.forEach((node) => {
      const open = expanded.has(node.id);
      const base =
        this.findNode(originalCreditSource, node.id) ||
        this.findNode(originalCollateralSource, node.id);

      const diff = (k) =>
        highlight && !draft.has(node.id) && base && base[k] !== node[k]
          ? "changed-cell"
          : "";

      const indent = level === 0 ? 'indent-0' : 
                    level === 1 ? 'indent-1' :
                    level === 2 ? 'indent-2' : 'indent-3';
      const ed = node.editable; // shorthand

      out.push({
        ...node,
        level,
        hasChildren: node.children?.length,
        icon: node.children
          ? open
            ? "utility:chevrondown"
            : "utility:chevronright"
          : "",

        labelClass: `${indent} ${diff("label")}`.trim(),
        dueDateClass: `${indent} ${diff("dueDate")}`.trim(),
        rateClass: `${indent} ${diff("rate")}`.trim(),
        balance99Class: `${indent} ${diff("balance99")}`.trim(),
        markClass: `${indent} ${diff("mark")}`.trim(),
        principalClass: `${indent} ${diff("principal")}`.trim(),
        changeClass: `${indent} ${diff("change")}`.trim(),
        postBalanceClass: `${indent} ${diff("postBalance")}`.trim(),
        actualBalanceClass: `${indent} ${diff("actualBalance")}`.trim(),
        correctionClass: `${indent} ${diff("correction")}`.trim(),
        collateralTypeClass: `${indent} ${diff("collateralType")}`.trim(),
        regValueClass: `${indent} ${diff("regValue")}`.trim(),
        marketValueClass: `${indent} ${diff("marketValue")}`.trim(),

        /* disabled フラグを生成 */
        labelDisabled: !ed.label,
        dueDateDisabled: !ed.dueDate,
        rateDisabled: !ed.rate,
        balance99Disabled: !ed.balance99,
        markDisabled: !ed.mark,
        principalDisabled: !ed.principal,
        changeDisabled: !ed.change,
        postBalanceDisabled: !ed.postBalance,
        actualBalanceDisabled: !ed.actualBalance,
        correctionDisabled: !ed.correction,
        collateralTypeDisabled: !ed.collateralType,
        regValueDisabled: !ed.regValue,
        marketValueDisabled: !ed.marketValue
      });

      if (open && node.children)
        this.flatten(node.children, highlight, level + 1, out);
    });
    return out;
  }

  /* ---------- helpers ---------- */
  updateNode(tree, id, field, value) {
    for (const n of tree) {
      if (n.id === id) {
        n[field] = value;
        return;
      }
      if (n.children) this.updateNode(n.children, id, field, value);
    }
  }

  findNode(tree, id) {
    for (const n of tree) {
      if (n.id === id) return n;
      if (n.children) {
        const f = this.findNode(n.children, id);
        if (f) return f;
      }
    }
    return null;
  }
}

function generateGuarantorData() {
  return Array.from({ length: 5 }, (_, i) => ({
    id: `g${i + 1}`,
    name: `保証人${i + 1}`
  }));
}