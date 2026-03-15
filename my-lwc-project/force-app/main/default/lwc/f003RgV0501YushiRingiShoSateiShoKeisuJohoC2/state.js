/**
 * 与信・保全テーブルの状態管理サービス
 *
 * ■ 3世代のツリーデータを保持:
 *   current - ユーザー編集中のツリー(handleEditで更新される)
 *   initial - 初回ロード時の状態(reset時にここへ戻す)
 *   saved   - 最後の保存時の状態(変更ハイライトの比較基準)
 *
 * ■ ライフサイクル:
 *   initialize() → 3世代全てにdata.jsの初期ツリーをコピー
 *   (ユーザー操作) → currentが編集される
 *   saveSnapshot() → currentをsavedにコピー(ハイライト基準更新)
 *   reset()        → current/savedをinitialに戻す
 */
import {
  creditTreeData,
  collateralTreeData,
  applyEditableFlags,
  deepCopy
} from "./data";

export class StateService {

  // --- プロパティ ---

  _initialized = false;
  _currentCredit = [];
  _initialCredit = [];
  _savedCredit = [];
  _currentCollateral = [];
  _initialCollateral = [];
  _savedCollateral = [];
  _expanded = new Set();

  // --- 初期化・リセット ---

  /** data.jsのツリーに編集可否フラグを付与し、3世代分をコピーして初期化 */
  initialize() {
    if (this._initialized) return;
    const creditWithFlags = applyEditableFlags(creditTreeData);
    const collateralWithFlags = applyEditableFlags(collateralTreeData);

    this._currentCredit = deepCopy(creditWithFlags);
    this._initialCredit = deepCopy(creditWithFlags);
    this._savedCredit = deepCopy(creditWithFlags);
    this._currentCollateral = deepCopy(collateralWithFlags);
    this._initialCollateral = deepCopy(collateralWithFlags);
    this._savedCollateral = deepCopy(collateralWithFlags);
    this._initialized = true;
  }

  /** current/savedをinitialに戻す(リセット操作) */
  reset() {
    this._currentCredit = deepCopy(this._initialCredit);
    this._savedCredit = deepCopy(this._initialCredit);
    this._currentCollateral = deepCopy(this._initialCollateral);
    this._savedCollateral = deepCopy(this._initialCollateral);
  }

  // --- 状態取得・更新 ---

  /** 現在の全状態を返す(表示行構築・ハイライト計算で使用) */
  getState() {
    return {
      creditSource: this._currentCredit,
      collateralSource: this._currentCollateral,
      savedCreditSource: this._savedCredit,
      savedCollateralSource: this._savedCollateral,
      expanded: this._expanded
    };
  }

  /** currentの状態をsavedにコピーする(変更ハイライトの基準が更新される) */
  saveSnapshot() {
    this._savedCredit = deepCopy(this._currentCredit);
    this._savedCollateral = deepCopy(this._currentCollateral);
  }
}
