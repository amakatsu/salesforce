import { LightningElement, track } from "lwc";
import { stateService } from "./editableTreeGridState";

/* =========================================
 * EditableTreeGrid
 * ========================================= */
export default class EditableTreeGrid extends LightningElement {
  /* ---------- reactive rows ---------- */
  @track rows = [];

  /* ---------- local flag ---------- */
  highlightOn = false; // 保存直後のみ true

  /* ---------- getters ---------- */
  get draft() {
    return stateService.getState().draft;
  }
  get hasDraft() {
    return this.draft.size > 0;
  }
  get draftJson() {
    return JSON.stringify(Object.fromEntries(this.draft), null, 2);
  }

  /* ---------- lifecycle ---------- */
  connectedCallback() {
    stateService.initializeState();
    this.rows = this.flatten(stateService.getState().source, false);
  }

  /* ---------- button handlers ---------- */
  handleSave() {
    /* ★ Apex で一括保存する処理をここで呼ぶ */

    stateService.getState().draft.clear(); // draft クリア
    this.highlightOn = true; // ハイライト許可
    this.rows = this.flatten(stateService.getState().source, true);
  }

  handleReset() {
    stateService.resetState();
    this.highlightOn = false; // ハイライト解除
    this.rows = this.flatten(stateService.getState().source, false);
  }

  /* ---------- table interaction ---------- */
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

    const { source, draft } = stateService.getState();

    /* 1) ソース更新 */
    this.updateNode(source, id, field, value);

    /* 2) draft へ保持 */
    const prev = draft.get(id) || {};
    draft.set(id, { ...prev, [field]: value });

    /* 3) 旧ハイライトは残したまま再描画 */
    this.rows = this.flatten(source, this.highlightOn);
  }

  /* ---------- util: tree -> flat ---------- */
  flatten(tree, highlight, level = 0, out = []) {
    const { expanded, originalSource, draft } = stateService.getState();

    tree.forEach((node) => {
      const open = expanded.has(node.id);
      const base = this.findNode(originalSource, node.id); // 前回保存時点

      /* draft に含まれる（編集中）行はハイライトしない */
      const diff = (key) =>
        highlight && !draft.has(node.id) && base && base[key] !== node[key]
          ? "changed-cell"
          : "";

      const indent = `indent-${level}`;

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
        roleClass: `${indent} ${diff("role")}`.trim()
      });

      if (open && node.children)
        this.flatten(node.children, highlight, level + 1, out);
    });
    return out;
  }

  /* ---------- util: update node ---------- */
  updateNode(tree, id, field, value) {
    for (const n of tree) {
      if (n.id === id) {
        n[field] = value;
        return;
      }
      if (n.children) this.updateNode(n.children, id, field, value);
    }
  }

  /* ---------- util: find node ---------- */
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
