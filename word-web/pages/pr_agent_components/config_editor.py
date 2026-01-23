# -*- coding: utf-8 -*-
"""
PR-Agent 設定ファイルエディタ（モーダル）
"""
import streamlit as st
import toml
import io
import os
import shutil
import html
import re
import copy
import hashlib
from pathlib import Path
from datetime import datetime

from word.pr_agent.config_repository import ConfigRepository, ConfigConflictError

from .constants import CONFIG_SECTIONS, MODAL_STATE_KEY

# トラッキングをインポート（遅延インポート）
_track_usage = None
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _get_track_usage():
    """トラッキング関数を取得（遅延インポート）"""
    global _track_usage
    if _track_usage is None:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from pages.util.usage_tracker import track_usage
        _track_usage = track_usage
    return _track_usage


# =============================================================================
# バックアップ関連ヘルパー
# =============================================================================

def _list_backup_files(config_path: str) -> tuple[list | None, str | None]:
    """バックアップファイル一覧を取得"""
    try:
        config_path_obj = _resolve_config_path(config_path)
        backup_files = sorted(
            config_path_obj.parent.glob(f"{config_path_obj.name}.backup.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        entries = []
        for file_path in backup_files:
            timestamp = file_path.name.split(".backup.", 1)[1] if ".backup." in file_path.name else "unknown"
            entries.append({
                "path": file_path,
                "timestamp": timestamp,
                "label": f"{timestamp} | {file_path.stat().st_size} bytes"
            })
        return entries, None
    except Exception as e:
        return None, f"バックアップの一覧取得に失敗: {e}"


def _create_backup_if_changed(config_path: str, new_text: str, *, enable_backup: bool, label: str = "", force: bool = False) -> tuple[str | None, bool]:
    """変更がある場合にバックアップを作成"""
    config_path = str(_resolve_config_path(config_path))
    if not enable_backup or not os.path.exists(config_path):
        return None, False
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            current_text = f.read()
    except Exception:
        current_text = None

    if not force and current_text is not None and current_text == new_text:
        return None, False

    safe_label = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in label.strip())[:40]
    backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(config_path, backup_path)
    return backup_path, True


def _load_backup_file(file_path: Path) -> tuple[dict | None, str | None, str | None]:
    """バックアップファイルを読み込み"""
    try:
        text_data = file_path.read_text(encoding="utf-8")
        data = toml.load(io.StringIO(text_data))
        return data, text_data, None
    except Exception as e:
        return None, None, f"バックアップの読み込みに失敗: {e}"


# =============================================================================
# フォーム編集タブ
# =============================================================================

def _render_form_tab(edited_config: dict, config_name: str, mode_key: str, validation_errors: list):
    """フォーム編集タブをレンダリング"""
    st.info("💡 各セクションを展開して設定を編集してください。入力内容はリアルタイムで検証されます。")

    for section_key, section_info in CONFIG_SECTIONS.items():
        if section_key not in edited_config:
            continue

        with st.expander(section_info["label"], expanded=False):
            section_data = edited_config.get(section_key, {})

            for field_key, field_info in section_info["fields"].items():
                _render_field(
                    edited_config, section_key, section_data,
                    field_key, field_info, config_name, mode_key, validation_errors
                )

    if validation_errors:
        st.error("❌ 入力エラーがあります:")
        for err in validation_errors:
            st.write(f"  - {err}")


def _render_field(edited_config: dict, section_key: str, section_data: dict,
                  field_key: str, field_info: dict, config_name: str, mode_key: str, validation_errors: list):
    """個別フィールドをレンダリング"""
    previous_value = section_data.get(field_key, field_info.get("default"))
    field_type = field_info["type"]
    field_label = field_info["label"]
    field_help = field_info.get("help", "")
    current_value = section_data.get(field_key, field_info.get("default"))
    widget_key = f"modal_{config_name}_{section_key}_{field_key}"

    new_value = None

    if field_type == "textarea":
        new_value = st.text_area(
            field_label,
            value=current_value if current_value else "",
            height=200,
            help=field_help,
            key=widget_key
        )

    elif field_type == "number":
        min_val = field_info.get("min", 0)
        max_val = field_info.get("max", 100)
        default_val = field_info.get("default", min_val)

        try:
            current_int = int(current_value) if current_value is not None else default_val
        except (ValueError, TypeError):
            current_int = default_val
            validation_errors.append(f"{CONFIG_SECTIONS[section_key]['label']} > {field_label}: 数値が不正です")

        new_value = st.number_input(
            field_label,
            min_value=min_val,
            max_value=max_val,
            value=current_int,
            help=field_help,
            key=widget_key
        )

    elif field_type == "checkbox":
        default_val = field_info.get("default", False)
        current_bool = current_value if isinstance(current_value, bool) else default_val

        new_value = st.checkbox(
            field_label,
            value=current_bool,
            help=field_help,
            key=widget_key
        )

    if new_value is not None:
        if new_value != previous_value:
            st.session_state[mode_key] = "form"
        if section_key not in edited_config:
            edited_config[section_key] = {}
        edited_config[section_key][field_key] = new_value


# =============================================================================
# TOMLエディタタブ
# =============================================================================

def _render_toml_tab(edited_config: dict, session_key: str, mode_key: str, toml_editor_key: str) -> dict:
    """TOML直接編集タブをレンダリング"""
    st.warning("⚠️ TOML形式で直接編集できます。構文エラーがあると保存できません。")

    try:
        toml_text = toml.dumps(edited_config)
    except Exception as e:
        toml_text = f"# TOML変換エラー: {e}"

    edited_toml = st.text_area(
        "TOML形式で編集",
        value=toml_text,
        height=400,
        key=toml_editor_key
    )

    last_value_key = f"{toml_editor_key}_last"
    previous_value = st.session_state.get(last_value_key, toml_text)
    st.session_state[last_value_key] = edited_toml

    if edited_toml != previous_value:
        try:
            parsed = toml.load(io.StringIO(edited_toml))
            st.success("✅ TOML構文は正しいです")
            st.session_state[session_key] = parsed
            st.session_state[mode_key] = "toml"
            return parsed
        except toml.TomlDecodeError as e:
            _render_toml_error(e, edited_toml)
            return edited_config
    return edited_config


def _render_toml_error(error: toml.TomlDecodeError, edited_toml: str):
    """TOMLエラーを表示"""
    st.error("❌ TOML構文エラー")

    error_msg = str(error)
    line_match = re.search(r'line (\d+)', error_msg)
    col_match = re.search(r'col(?:umn)? (\d+)', error_msg)

    error_line = int(line_match.group(1)) if line_match else None
    error_col = int(col_match.group(1)) if col_match else None

    st.markdown(f"**エラー内容:** `{html.escape(error_msg)}`")

    if error_line:
        lines = edited_toml.split('\n')
        st.markdown(f"**エラー箇所:** 行 {error_line}" + (f", 列 {error_col}" if error_col else ""))

        start_line = max(0, error_line - 3)
        end_line = min(len(lines), error_line + 2)

        st.markdown("**エラー周辺のコード:**")

        for i in range(start_line, end_line):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            escaped_content = html.escape(line_content)

            if line_num == error_line:
                st.markdown(
                    f'<div style="background-color: #ffcccc; padding: 2px 8px; '
                    f'border-left: 4px solid #ff0000; font-family: monospace; margin: 2px 0;">'
                    f'<span style="color: #ff0000; font-weight: bold;">→ {line_num:4d}</span> | '
                    f'<code style="color: #cc0000;">{escaped_content}</code></div>',
                    unsafe_allow_html=True
                )
                if error_col and error_col <= len(line_content) + 1:
                    pointer = "&nbsp;" * (error_col + 7) + "^"
                    st.markdown(
                        f'<div style="font-family: monospace; color: #ff0000; '
                        f'padding-left: 8px;">{pointer} ここにエラー</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f'<div style="background-color: #f5f5f5; padding: 2px 8px; '
                    f'font-family: monospace; margin: 2px 0;">'
                    f'<span style="color: #888;">{line_num:4d}</span> | '
                    f'<code>{escaped_content}</code></div>',
                    unsafe_allow_html=True
                )


# =============================================================================
# バックアップ復元UI
# =============================================================================

def _render_backup_restore(config_path: str, config_name: str, session_key: str,
                           original_key: str, version_key: str, mode_key: str,
                           reset_widget_values_from_config):
    """バックアップ復元UIをレンダリング"""
    resolved_path = _resolve_config_path(config_path)
    restore_label_key = f"restore_backup_label_{config_name}"
    restore_confirm_key = f"restore_backup_confirm_{config_name}"

    restore_label = st.session_state.get(restore_label_key, "")
    restore_confirm = st.session_state.get(restore_confirm_key, True)

    if restore_confirm:
        label_text = restore_label or "自動"
        st.caption(f"復元前に現在の内容をバックアップ（ラベル: {label_text}）します")
    else:
        st.caption("復元前のバックアップ作成は無効です")

    if st.button("🔄 バックアップ一覧を更新", key=f"refresh_backups_{config_name}"):
        st.rerun()

    backup_entries, backup_error = _list_backup_files(resolved_path)

    if backup_error:
        st.error(f"❌ {backup_error}")
    elif not backup_entries:
        st.info("この設定ファイルのバックアップはまだありません")
    else:
        options = {
            f"{idx + 1:02d}. {entry['timestamp']} ({entry['path'].name})": entry
            for idx, entry in enumerate(backup_entries)
        }
        selected_label = st.selectbox(
            "復元するバックアップを選択",
            options=list(options.keys()),
            key=f"backup_select_{config_name}"
        )
        selected_entry = options[selected_label]
        backup_data, backup_text, backup_error = _load_backup_file(selected_entry['path'])

        if backup_error:
            st.error(f"❌ {backup_error}")
        elif backup_text:
            st.caption(f"バックアップ {selected_entry['path'].name} の内容")
            st.code(backup_text, language="toml")

        if backup_data and st.button(
            "このバックアップで復元",
            use_container_width=True,
            key=f"restore_backup_{config_name}"
        ):
            try:
                backup_path, _ = _create_backup_if_changed(
                    config_path, backup_text,
                    enable_backup=restore_confirm,
                    label=restore_label
                )

                with open(resolved_path, "w", encoding="utf-8") as f:
                    f.write(backup_text)

                st.session_state[session_key] = copy.deepcopy(backup_data)
                st.session_state[original_key] = copy.deepcopy(backup_data)
                restored_text = Path(resolved_path).read_text(encoding="utf-8")
                st.session_state[version_key] = hashlib.sha256(restored_text.encode("utf-8")).hexdigest()
                reset_widget_values_from_config(backup_data)
                st.session_state.pop(mode_key, None)

                st.success(f"✅ バックアップ {selected_entry['path'].name} から復元しました")
                if backup_path:
                    st.info(f"📋 現在の内容をバックアップ: {backup_path}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ バックアップからの復元に失敗: {e}")


# =============================================================================
# 保存/リセット/閉じるボタン
# =============================================================================

def _render_action_buttons(config_repo: ConfigRepository, config_path: str, config_name: str, edited_config: dict,
                           session_key: str, original_key: str, version_key: str,
                           toml_editor_key: str, mode_key: str, widget_prefix: str,
                           sync_widgets_to_config, reset_widget_values_from_config, clear_widget_state):
    """アクションボタンをレンダリング"""
    backup_label_key = f"backup_label_{config_name}"
    backup_confirm_key = f"backup_confirm_{config_name}"

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("💾 保存", type="primary", use_container_width=True):
            _handle_save(
                config_repo,
                config_path,
                config_name,
                edited_config,
                session_key,
                mode_key,
                backup_label_key,
                backup_confirm_key,
                sync_widgets_to_config,
                original_key,
                version_key,
                toml_editor_key,
            )

    with col2:
        if st.button("🔄 リセット", use_container_width=True):
            _handle_reset(config_path, session_key, original_key, version_key,
                          toml_editor_key, mode_key, reset_widget_values_from_config)

    with col3:
        if st.button("✖️ 閉じる", use_container_width=True):
            _handle_close(session_key, original_key, version_key, toml_editor_key,
                          mode_key, clear_widget_state)

    st.markdown(
        '''
        <div style="background:#f9f9f9;padding:0.75rem;border-radius:0.5rem;margin-top:0.75rem;">
            <strong>保存内容とバックアップ方法を確認してください</strong>
            <p style="margin:0.25rem 0 0;color:#4a5568;font-size:0.9rem;">
                保存作業の前後でバックアップ設定と変更内容を再確認し、安全に更新してください。
            </p>
        </div>
        ''',
        unsafe_allow_html=True
    )


def _handle_save(config_repo: ConfigRepository, config_path: str, config_name: str, edited_config: dict,
                 session_key: str, mode_key: str, backup_label_key: str,
                 backup_confirm_key: str, sync_widgets_to_config,
                 original_key: str, version_key: str, toml_editor_key: str):
    """保存処理"""
    resolved_path = _resolve_config_path(config_path)
    try:
        if st.session_state.get(mode_key) != "toml":
            edited_config = sync_widgets_to_config()
        else:
            edited_config = st.session_state.get(session_key, edited_config)

        toml_text = toml.dumps(edited_config)
        toml.load(io.StringIO(toml_text))

        backup_label = st.session_state.get(backup_label_key, "")
        backup_enabled = st.session_state.get(backup_confirm_key, True)
        save_result = config_repo.save_text(
            resolved_path,
            toml_text,
            expected_hash=st.session_state.get(version_key),
            create_backup=backup_enabled,
            backup_label=backup_label,
        )

        st.success(f"✅ 保存しました ({resolved_path})")
        if save_result.backup_path:
            st.info(f"📋 バックアップ: {save_result.backup_path}")
        elif not backup_enabled:
            st.info("ℹ️ バックアップは設定により作成されませんでした")

        track_usage = _get_track_usage()
        track_usage(action="設定ファイル編集（モーダル）", tool_name="PR-Agent", username=config_name)

        st.session_state[session_key] = copy.deepcopy(edited_config)
        st.session_state[original_key] = copy.deepcopy(edited_config)
        st.session_state[version_key] = save_result.new_hash
        st.session_state.pop(toml_editor_key, None)
        st.session_state.pop(f"{toml_editor_key}_last", None)
        st.session_state[mode_key] = "form"

    except ConfigConflictError:
        st.error("❌ 他のユーザーがこの設定を更新しました。リセットして最新内容を確認してください。")
    except toml.TomlDecodeError as e:
        st.error(f"❌ TOML構文エラー: {e}")
    except Exception as e:
        st.error(f"❌ 保存エラー: {e}")


def _handle_reset(config_path: str, session_key: str, original_key: str,
                  version_key: str, toml_editor_key: str, mode_key: str,
                  reset_widget_values_from_config):
    """リセット処理"""
    resolved_path = _resolve_config_path(config_path)
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            file_text = f.read()
            original_from_file = toml.load(io.StringIO(file_text))

        keys_to_clear = [session_key, original_key, version_key, toml_editor_key, mode_key]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        fresh_config = copy.deepcopy(original_from_file)
        st.session_state[session_key] = fresh_config
        st.session_state[original_key] = copy.deepcopy(original_from_file)
        st.session_state[version_key] = hashlib.sha256(file_text.encode("utf-8")).hexdigest()
        reset_widget_values_from_config(fresh_config)

        st.success("✅ 設定をリセットしました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ リセットに失敗: {e}")


def _handle_close(session_key: str, original_key: str, version_key: str,
                  toml_editor_key: str, mode_key: str, clear_widget_state):
    """閉じる処理"""
    keys_to_clear = [session_key, original_key, version_key, toml_editor_key, mode_key]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    clear_widget_state()
    st.session_state.pop(MODAL_STATE_KEY, None)
    st.rerun()


# =============================================================================
# メインモーダル関数
# =============================================================================

@st.dialog("⚙️ 設定ファイル編集", width="large")
def config_editor_modal(config_name: str, config_path: str, config_repo: ConfigRepository | None = None):
    """設定ファイル編集モーダル"""
    repo = config_repo or ConfigRepository()
    config_file_path = _resolve_config_path(config_path)
    st.markdown(f"### 📄 {config_name}")
    st.caption(f"ファイル: `{config_file_path}`")

    # セッションステートキー
    backup_label_key = f"backup_label_{config_name}"
    backup_confirm_key = f"backup_confirm_{config_name}"
    restore_label_key = f"restore_backup_label_{config_name}"
    restore_confirm_key = f"restore_backup_confirm_{config_name}"
    session_key = f"modal_config_{config_name}"
    original_key = f"modal_original_{config_name}"
    toml_editor_key = f"modal_toml_direct_{config_name}"
    mode_key = f"modal_mode_{config_name}"
    version_key = f"modal_version_{config_name}"
    widget_prefix = f"modal_{config_name}_"

    # セッションステート初期化
    for key, default in [
        (backup_label_key, ""), (backup_confirm_key, True),
        (restore_label_key, ""), (restore_confirm_key, True)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # 設定ファイル読み込み
    try:
        config_file_path, config_text, config_signature = repo.load_text(config_file_path)
        current_config = toml.load(io.StringIO(config_text))
    except Exception as e:
        st.error(f"❌ 設定ファイルの読み込みに失敗: {e}")
        return

    # ヘルパー関数
    def reset_widget_values_from_config(config_data):
        for section_key, section_info in CONFIG_SECTIONS.items():
            if section_key not in config_data:
                continue
            for field_key in section_info["fields"].keys():
                widget_key = f"{widget_prefix}{section_key}_{field_key}"
                st.session_state.pop(widget_key, None)
        st.session_state.pop(toml_editor_key, None)
        st.session_state.pop(f"{toml_editor_key}_last", None)
        st.session_state[mode_key] = "form"

    def clear_widget_state():
        keys_to_remove = [key for key in list(st.session_state.keys()) if str(key).startswith(widget_prefix)]
        for key in keys_to_remove:
            del st.session_state[key]
        st.session_state.pop(mode_key, None)

    def sync_widgets_to_config():
        config_data = st.session_state.get(session_key)
        if not config_data:
            return {}
        for section_key, section_info in CONFIG_SECTIONS.items():
            if section_key not in config_data:
                continue
            section = config_data.setdefault(section_key, {})
            for field_key in section_info["fields"].keys():
                widget_key = f"{widget_prefix}{section_key}_{field_key}"
                if widget_key in st.session_state:
                    section[field_key] = st.session_state[widget_key]
        st.session_state[session_key] = config_data
        return config_data

    # 設定状態の初期化/更新
    should_reset_widgets = False

    if session_key not in st.session_state:
        st.session_state[session_key] = copy.deepcopy(current_config)
        st.session_state[original_key] = copy.deepcopy(current_config)
        st.session_state[version_key] = config_signature
        should_reset_widgets = True
    elif st.session_state.get(version_key) != config_signature:
        st.session_state[session_key] = copy.deepcopy(current_config)
        st.session_state[original_key] = copy.deepcopy(current_config)
        st.session_state[version_key] = config_signature
        should_reset_widgets = True
    elif original_key not in st.session_state:
        st.session_state[original_key] = copy.deepcopy(current_config)

    edited_config = st.session_state[session_key]

    if should_reset_widgets:
        reset_widget_values_from_config(edited_config)
    elif toml_editor_key not in st.session_state:
        st.session_state[toml_editor_key] = toml.dumps(edited_config)

    validation_errors = []

    # タブ
    form_tab, toml_tab, preview_tab = st.tabs(["📝 フォーム編集", "📄 TOML直接編集", "👁️ プレビュー"])

    with form_tab:
        _render_form_tab(edited_config, config_name, mode_key, validation_errors)

    if st.session_state.get(mode_key) != "toml":
        edited_config = sync_widgets_to_config()

    with toml_tab:
        edited_config = _render_toml_tab(edited_config, session_key, mode_key, toml_editor_key)

    with preview_tab:
        st.info("💡 保存前のプレビューです")
        try:
            st.code(toml.dumps(edited_config), language="toml")
        except Exception as e:
            st.error(f"❌ プレビュー生成エラー: {e}")

    # バックアップ設定
    st.markdown("##### 📤 バックアップ設定")
    st.caption("実行前に現在の内容をどのようにバックアップするかを設定します")
    restore_label_input = st.text_input(
        "バックアップ名 (任意)",
        value=st.session_state[restore_label_key],
        key=f"modal_restore_label_{config_name}"
    )
    restore_confirm_input = st.checkbox(
        "復元前に差分があればバックアップを作成",
        value=st.session_state[restore_confirm_key],
        key=f"modal_restore_confirm_{config_name}"
    )
    st.session_state[restore_label_key] = restore_label_input
    st.session_state[restore_confirm_key] = restore_confirm_input

    # バックアップ復元
    with st.expander("📦 バックアップから復元", expanded=False):
        _render_backup_restore(
            str(config_file_path), config_name, session_key, original_key, version_key,
            mode_key, reset_widget_values_from_config
        )

    # アクションボタン
    with st.container():
        _render_action_buttons(
            repo,
            str(config_file_path), config_name, edited_config, session_key, original_key,
            version_key, toml_editor_key, mode_key, widget_prefix,
            sync_widgets_to_config, reset_widget_values_from_config, clear_widget_state
        )
def _resolve_config_path(config_path: str) -> Path:
    """設定ファイルの絶対パスを返す"""
    path_obj = Path(config_path)
    if not path_obj.is_absolute():
        path_obj = PROJECT_ROOT / path_obj
    return path_obj.resolve()
