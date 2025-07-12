import { LightningElement, track } from "lwc";
import { stateService } from "./editableTreeGridState";

export default class EditableTreeGrid extends LightningElement {
  @track rows = [];
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
    this.rows = this.flatten(stateService.getState().source, false);
  }

  /* ---------- SAVE / RESET ---------- */
  handleSave() {
    stateService.getState().draft.clear();
    this.highlightOn = true;
    this.rows = this.flatten(stateService.getState().source, true);
  }
  handleReset() {
    stateService.resetState();
    this.highlightOn = false;
    this.rows = this.flatten(stateService.getState().source, false);
  }

  /* ---------- TOGGLE / EDIT ---------- */
  handleToggle(e) {
    const { source, expanded } = stateService.getState();
    const id = e.currentTarget.dataset.id;
    expanded.has(id) ? expanded.delete(id) : expanded.add(id);
    this.rows = this.flatten(source, this.highlightOn);
  }

  handleEdit(e) {
    const id = e.target.dataset.id;
    const field = e.target.dataset.field;
    const value = field === "active" ? e.target.checked : e.target.value;

    const row = this.rows.find((r) => r.id === id);
    if (row && row[`${field}Disabled`]) return; // 編集不可なら無視

    const { source, draft } = stateService.getState();
    this.updateNode(source, id, field, value); // ソース更新

    const prev = draft.get(id) || {};
    draft.set(id, { ...prev, [field]: value }); // draft へ

    this.rows = this.flatten(source, this.highlightOn);
  }

  /* ---------- tree -> flat ---------- */
  flatten(tree, highlight, level = 0, out = []) {
    const { expanded, originalSource, draft } = stateService.getState();

    tree.forEach((node) => {
      const open = expanded.has(node.id);
      const base = this.findNode(originalSource, node.id);

      const diff = (k) =>
        highlight && !draft.has(node.id) && base && base[k] !== node[k]
          ? "changed-cell"
          : "";

      const indent = `indent-${level}`;
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

        nameClass: `${indent} ${diff("name")}`.trim(),
        statusClass: `${indent} ${diff("status")}`.trim(),
        joinDateClass: `${indent} ${diff("joinDate")}`.trim(),
        activeClass: `${indent} ${diff("active")}`.trim(),
        roleClass: `${indent} ${diff("role")}`.trim(),

        /* disabled フラグを生成 */
        nameDisabled: !ed.name,
        statusDisabled: !ed.status,
        joinDateDisabled: !ed.joinDate,
        activeDisabled: !ed.active,
        roleDisabled: !ed.role
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
