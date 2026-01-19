#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-Agent - Webインターフェース (Streamlit)
プルリクエストの自動レビューとコード品質チェック
"""
import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
# Dockerコンテナ内: /app/pages/3_pr_agent.py → /app/.env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    # デバッグ: 環境変数の読み込み確認
    import logging
    logging.info(f"✅ .env loaded from: {env_path}")
else:
    import logging
    logging.warning(f"⚠️ .env not found at: {env_path}")

# バックエンドモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from word.pr_agent import PRAgentRunner, ConfigManager, Logger, UrlValidator

# トラッキングをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from usage_tracker import track_usage

# Geminiモデルのデフォルト値
gemini_model = ""

MODAL_STATE_KEY = "config_modal_open"
INPUT_METHOD_KEY = "input_method_selector"


def _close_modal():
    """モーダル状態をクリアするコールバック関数"""
    st.session_state.pop(MODAL_STATE_KEY, None)

def render_result_summary(placeholder, result_state):
    """Render run result details that persist across reruns."""
    with placeholder.container():
        if not result_state:
            st.info("実行結果はここに表示されます")
            return

        params = result_state.get('params', {})
        warnings = result_state.get('warnings') or []
        errors = result_state.get('errors') or []
        status = result_state.get('status')

        if status == 'success':
            if warnings:
                st.warning(f"⚠️ PR-Agentコマンドが完了しましたが、{len(warnings)}件の警告がありました")
                with st.expander(f"⚠️ 警告詳細 ({len(warnings)}件)", expanded=False):
                    for warn in warnings[:10]:
                        st.code(warn, language='log')
            else:
                st.success("✅ PR-Agentコマンドが正常に完了しました！")
        else:
            st.error("❌ レビュー中にエラーが発生しました")
            if errors:
                with st.expander(f"🔍 エラー詳細 ({len(errors)}件)", expanded=True):
                    for err in errors[:20]:
                        st.code(err, language='log')

        st.markdown("### 📋 実行内容")
        if params.get('is_preview_mode'):
            st.write("- **実行モード**: 📋 プレビューのみ（投稿なし）")
        else:
            st.write("- **実行モード**: ✅ 実行して投稿")
        if params.get('pr_command'):
            st.write(f"- **コマンド**: {params['pr_command']}")
        if params.get('pr_url'):
            st.write(f"- **MR URL**: {params['pr_url']}")
        if params.get('gitlab_url'):
            st.write(f"- **GitLab URL**: {params['gitlab_url']} ✅ ユーザー指定")
        ai_provider = params.get('ai_provider')
        if ai_provider:
            if ai_provider == "Gemini":
                st.write("- **AIプロバイダー**: Google Gemini")
                if params.get('gemini_model'):
                    st.write(f"- **モデル**: {params['gemini_model']}")
            else:
                st.write("- **AIプロバイダー**: OpenAI (Azure)")
                st.write("- **モデル**: gpt-4o")
        if params.get('selected_config'):
            st.write(f"- **設定**: {params['selected_config']}")
        if params.get('pr_command') == "ask" and params.get('question'):
            st.write(f"- **質問**: {params['question']}")
        if params.get('custom_prompt'):
            st.write(f"- **カスタムプロンプト**: {params['custom_prompt']}")

        if status == 'success':
            if params.get('is_preview_mode'):
                st.info("💡 プレビューモードで実行されました。結果はGitLabに投稿されていません。")
            else:
                st.info("💡 結果はGitLabのMRページに投稿されました")
        else:
            st.warning("💡 上記のエラーログを確認して、問題を修正してください")


# =============================================================================
# 設定ファイル編集モーダル
# =============================================================================

# セクション定義（フォーム生成用）
CONFIG_SECTIONS = {
    "pr_reviewer": {
        "label": "📝 レビュー設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "レビュー時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "require_score_review": {"type": "checkbox", "label": "スコアレビューを要求", "default": True},
            "require_tests_review": {"type": "checkbox", "label": "テストレビューを要求", "default": True},
            "require_estimate_effort_to_review": {"type": "checkbox", "label": "レビュー工数見積もり", "default": True},
            "enable_review_labels_effort": {"type": "checkbox", "label": "工数ラベル有効", "default": True},
            "enable_review_labels_security": {"type": "checkbox", "label": "セキュリティラベル有効", "default": True},
        }
    },
    "pr_code_suggestions": {
        "label": "✨ コード提案設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "コード提案時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "commitable_code_suggestions": {"type": "checkbox", "label": "コミット可能な形式で提案", "default": True},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_improve": {
        "label": "🔧 コード改善設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "コード改善時のAIへの追加指示"},
            "num_code_suggestions": {"type": "number", "label": "提案数", "min": 1, "max": 20, "default": 10},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_description": {
        "label": "📋 MR説明設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "MR説明生成時のAIへの追加指示"},
            "publish_description": {"type": "checkbox", "label": "説明を公開", "default": True},
            "add_original_user_description": {"type": "checkbox", "label": "元の説明を追加", "default": True},
            "enable_pr_type": {"type": "checkbox", "label": "PR種別を有効", "default": True},
            "use_bullet_points": {"type": "checkbox", "label": "箇条書き形式", "default": True},
            "enable_semantic_files_types": {"type": "checkbox", "label": "ファイル種別分類を有効", "default": True},
            "generate_ai_title": {"type": "checkbox", "label": "AIタイトル生成", "default": False},
        }
    },
    "pr_questions": {
        "label": "❓ 質問応答設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "質問応答時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_add_docs": {
        "label": "📚 ドキュメント設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "ドキュメント生成時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_generate_labels": {
        "label": "🏷️ ラベル生成設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "ラベル生成時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_update_changelog": {
        "label": "📜 Changelog設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "Changelog更新時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
    "pr_similar_issue": {
        "label": "🔍 類似Issue設定",
        "fields": {
            "extra_instructions": {"type": "textarea", "label": "追加指示", "help": "類似Issue検索時のAIへの追加指示"},
            "enable_help_text": {"type": "checkbox", "label": "ヘルプテキスト有効", "default": True},
        }
    },
}


@st.dialog("⚙️ 設定ファイル編集", width="large")
def config_editor_modal(config_name: str, config_path: str):
    """設定ファイル編集モーダル"""
    import toml
    import io
    import shutil
    import html
    import re
    import copy
    from datetime import datetime


    st.markdown(f"### 📄 {config_name}")
    st.caption(f"ファイル: `{config_path}`")
    backup_label_key = f"backup_label_{config_name}"
    backup_confirm_key = f"backup_confirm_{config_name}"
    restore_label_key = f"restore_backup_label_{config_name}"
    restore_confirm_key = f"restore_backup_confirm_{config_name}"
    if backup_label_key not in st.session_state:
        st.session_state[backup_label_key] = ""
    if backup_confirm_key not in st.session_state:
        st.session_state[backup_confirm_key] = True
    if restore_label_key not in st.session_state:
        st.session_state[restore_label_key] = ""
    if restore_confirm_key not in st.session_state:
        st.session_state[restore_confirm_key] = True
    # 現在の設定を読み込み
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = toml.load(f)
    except Exception as e:
        st.error(f"❌ 設定ファイルの読み込みに失敗: {e}")
        return

    # 編集用の一時データをセッションステートに保存
    session_key = f"modal_config_{config_name}"
    original_key = f"modal_original_{config_name}"
    toml_editor_key = f"modal_toml_direct_{config_name}"
    mode_key = f"modal_mode_{config_name}"
    version_key = f"modal_version_{config_name}"
    widget_prefix = f"modal_{config_name}_"

    def reset_widget_values_from_config(config_data):
        """Keep widget states aligned with the loaded config."""
        for section_key, section_info in CONFIG_SECTIONS.items():
            if section_key not in config_data:
                continue
            for field_key in section_info["fields"].keys():
                widget_key = f"{widget_prefix}{section_key}_{field_key}"
                st.session_state.pop(widget_key, None)

        st.session_state.pop(toml_editor_key, None)
        st.session_state[mode_key] = "form"

    def clear_widget_state():
        """Remove modal widget entries from session state."""
        keys_to_remove = [
            key for key in list(st.session_state.keys())
            if str(key).startswith(widget_prefix)
        ]
        for key in keys_to_remove:
            del st.session_state[key]
        st.session_state.pop(mode_key, None)

    def sync_widgets_to_config():
        """Update config data from current widget states."""
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

    def list_backup_files():
        try:
            config_path_obj = Path(config_path)
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

    def create_backup_if_changed(new_text: str, *, enable_backup: bool, label: str = "", force: bool = False):
        """Create a backup only if requested and the file content will change.

        When force=True the diff check is skipped (used for manual saves that always require a backup).
        """
        if not enable_backup or not os.path.exists(config_path):
            return None, False
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                current_text = f.read()
        except Exception:
            current_text = None
        if not force and current_text is not None and current_text == new_text:
            return None, False

        safe_label = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in label.strip())
        safe_label = safe_label[:40]
        suffix = f"_{safe_label}" if safe_label else ""
        backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(config_path, backup_path)
        return backup_path, True

    def load_backup_file(file_path: Path):
        try:
            text_data = file_path.read_text(encoding="utf-8")
            data = toml.load(io.StringIO(text_data))
            return data, text_data, None
        except Exception as e:
            return None, None, f"バックアップの読み込みに失敗: {e}"

    config_mtime = os.path.getmtime(config_path)

    def load_config_into_state():
        config_copy = copy.deepcopy(current_config)
        st.session_state[session_key] = config_copy
        st.session_state[original_key] = copy.deepcopy(current_config)
        st.session_state[version_key] = config_mtime

    should_reset_widgets = False

    if session_key not in st.session_state:
        load_config_into_state()
        should_reset_widgets = True
    else:
        if st.session_state.get(version_key) != config_mtime:
            load_config_into_state()
            should_reset_widgets = True
        elif original_key not in st.session_state:
            st.session_state[original_key] = copy.deepcopy(current_config)

    edited_config = st.session_state[session_key]

    if should_reset_widgets:
        reset_widget_values_from_config(edited_config)
    else:
        if toml_editor_key not in st.session_state:
            st.session_state[toml_editor_key] = toml.dumps(edited_config)

    # バリデーションエラー表示用
    validation_errors = []

    # タブで「フォーム編集」と「TOML直接編集」を切り替え
    form_tab, toml_tab, preview_tab = st.tabs(["📝 フォーム編集", "📄 TOML直接編集", "👁️ プレビュー"])

    with form_tab:
        st.info("💡 各セクションを展開して設定を編集してください。入力内容はリアルタイムで検証されます。")

        # 各セクションをexpanderで表示
        for section_key, section_info in CONFIG_SECTIONS.items():
            # このセクションが設定ファイルに存在するかチェック
            if section_key not in edited_config:
                continue

            with st.expander(section_info["label"], expanded=False):
                section_data = edited_config.get(section_key, {})

                for field_key, field_info in section_info["fields"].items():
                    previous_value = section_data.get(field_key, field_info.get("default"))
                    field_type = field_info["type"]
                    field_label = field_info["label"]
                    field_help = field_info.get("help", "")
                    current_value = section_data.get(field_key, field_info.get("default"))

                    # フィールドタイプに応じた入力UI
                    if field_type == "textarea":
                        new_value = st.text_area(
                            field_label,
                            value=current_value if current_value else "",
                            height=200,
                            help=field_help,
                            key=f"modal_{config_name}_{section_key}_{field_key}"
                        )
                        # 空文字の場合はNoneではなく空文字として保存
                        if new_value != previous_value:
                            st.session_state[mode_key] = "form"
                        if section_key not in edited_config:
                            edited_config[section_key] = {}
                        edited_config[section_key][field_key] = new_value

                    elif field_type == "number":
                        min_val = field_info.get("min", 0)
                        max_val = field_info.get("max", 100)
                        default_val = field_info.get("default", min_val)

                        try:
                            current_int = int(current_value) if current_value is not None else default_val
                        except (ValueError, TypeError):
                            current_int = default_val
                            validation_errors.append(f"{section_info['label']} > {field_label}: 数値が不正です")

                        new_value = st.number_input(
                            field_label,
                            min_value=min_val,
                            max_value=max_val,
                            value=current_int,
                            help=field_help,
                            key=f"modal_{config_name}_{section_key}_{field_key}"
                        )
                        if new_value != previous_value:
                            st.session_state[mode_key] = "form"
                        if section_key not in edited_config:
                            edited_config[section_key] = {}
                        edited_config[section_key][field_key] = new_value

                    elif field_type == "checkbox":
                        default_val = field_info.get("default", False)
                        current_bool = current_value if isinstance(current_value, bool) else default_val

                        new_value = st.checkbox(
                            field_label,
                            value=current_bool,
                            help=field_help,
                            key=f"modal_{config_name}_{section_key}_{field_key}"
                        )
                        if new_value != previous_value:
                            st.session_state[mode_key] = "form"
                        if section_key not in edited_config:
                            edited_config[section_key] = {}
                        edited_config[section_key][field_key] = new_value

        # バリデーションエラー表示
        if validation_errors:
            st.error("❌ 入力エラーがあります:")
            for err in validation_errors:
                st.write(f"  - {err}")

    if st.session_state.get(mode_key) != "toml":
        edited_config = sync_widgets_to_config()

    with toml_tab:
        st.warning("⚠️ TOML形式で直接編集できます。構文エラーがあると保存できません。")

        # 常に最新のedited_configからTOMLテキストを生成（フォーム編集と同期）
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

        # リアルタイムバリデーション
        try:
            parsed = toml.load(io.StringIO(edited_toml))
            st.success("✅ TOML構文は正しいです")
            # パース成功時、edited_configを更新（TOML直接編集の内容を反映）
            st.session_state[session_key] = parsed
            edited_config = parsed
            st.session_state[mode_key] = "toml"
        except toml.TomlDecodeError as e:
            st.error(f"❌ TOML構文エラー")

            # エラーメッセージから行番号を抽出
            error_msg = str(e)
            import re
            line_match = re.search(r'line (\d+)', error_msg)
            col_match = re.search(r'col(?:umn)? (\d+)', error_msg)

            error_line = int(line_match.group(1)) if line_match else None
            error_col = int(col_match.group(1)) if col_match else None

            # エラー詳細を表示
            st.markdown(f"**エラー内容:** `{html.escape(error_msg)}`")

            if error_line:
                lines = edited_toml.split('\n')
                st.markdown(f"**エラー箇所:** 行 {error_line}" + (f", 列 {error_col}" if error_col else ""))

                # エラー行の前後を表示（コンテキスト付き）
                start_line = max(0, error_line - 3)
                end_line = min(len(lines), error_line + 2)

                st.markdown("**エラー周辺のコード:**")

                for i in range(start_line, end_line):
                    line_num = i + 1
                    line_content = lines[i] if i < len(lines) else ""
                    # HTML特殊文字をエスケープ
                    escaped_content = html.escape(line_content)

                    if line_num == error_line:
                        # エラー行を赤色でハイライト
                        st.markdown(
                            f'<div style="background-color: #ffcccc; padding: 2px 8px; '
                            f'border-left: 4px solid #ff0000; font-family: monospace; '
                            f'margin: 2px 0;">'
                            f'<span style="color: #ff0000; font-weight: bold;">→ {line_num:4d}</span> | '
                            f'<code style="color: #cc0000;">{escaped_content}</code></div>',
                            unsafe_allow_html=True
                        )
                        # エラー列をポイント
                        if error_col and error_col <= len(line_content) + 1:
                            pointer = "&nbsp;" * (error_col + 7) + "^"
                            st.markdown(
                                f'<div style="font-family: monospace; color: #ff0000; '
                                f'padding-left: 8px;">{pointer} ここにエラー</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        # 通常行
                        st.markdown(
                            f'<div style="background-color: #f5f5f5; padding: 2px 8px; '
                            f'font-family: monospace; margin: 2px 0;">'
                            f'<span style="color: #888;">{line_num:4d}</span> | '
                            f'<code>{escaped_content}</code></div>',
                            unsafe_allow_html=True
                        )

    with preview_tab:
        st.info("💡 保存前のプレビューです")
        try:
            preview_toml = toml.dumps(edited_config)
            st.code(preview_toml, language="toml")
        except Exception as e:
            st.error(f"❌ プレビュー生成エラー: {e}")

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

    with st.expander("📦 バックアップから復元", expanded=False):
        restore_label = st.session_state.get(restore_label_key, "")
        restore_confirm = st.session_state.get(restore_confirm_key, True)

        if restore_confirm:
            label_text = restore_label or "自動"
            st.caption(f"復元前に現在の内容をバックアップ（ラベル: {label_text}）します")
        else:
            st.caption("復元前のバックアップ作成は無効です")

        if st.button("🔄 バックアップ一覧を更新", key=f"refresh_backups_{config_name}"):
            st.rerun()

        backup_entries, backup_error = list_backup_files()
        if backup_error:
            st.error(f"❌ {backup_error}")
        elif not backup_entries:
            st.info("この設定ファイルのバックアップはまだありません")
        else:
            options = {
                f"{idx + 1:02d}. {entry['timestamp']} ({entry['path'].name})": entry
                for idx, entry in enumerate(backup_entries)
            }
            backup_select_key = f"backup_select_{config_name}"
            selected_label = st.selectbox(
                "復元するバックアップを選択",
                options=list(options.keys()),
                key=backup_select_key
            )
            selected_entry = options[selected_label]
            backup_data, backup_text, backup_error = load_backup_file(selected_entry['path'])

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
                    backup_path, _ = create_backup_if_changed(
                        backup_text,
                        enable_backup=restore_confirm,
                        label=restore_label
                    )

                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(backup_text)

                    st.session_state[session_key] = copy.deepcopy(backup_data)
                    st.session_state[original_key] = copy.deepcopy(backup_data)
                    st.session_state[version_key] = os.path.getmtime(config_path)
                    reset_widget_values_from_config(backup_data)
                    st.session_state.pop(mode_key, None)

                    st.success(f"✅ バックアップ {selected_entry['path'].name} から復元しました")
                    if backup_path:
                        st.info(f"📋 現在の内容をバックアップ: {backup_path}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ バックアップからの復元に失敗: {e}")

    # 保存ボタン
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if st.button("💾 保存", type="primary", use_container_width=True):
                try:
                    if st.session_state.get(mode_key) != "toml":
                        edited_config = sync_widgets_to_config()
                    else:
                        edited_config = st.session_state.get(session_key, edited_config)
                    # TOML構文チェック
                    toml_text = toml.dumps(edited_config)
                    toml.load(io.StringIO(toml_text))

                    backup_label = st.session_state.get(backup_label_key, "")
                    backup_enabled = st.session_state.get(backup_confirm_key, True)
                    backup_path, backup_created = create_backup_if_changed(
                        toml_text,
                        enable_backup=backup_enabled,
                        label=backup_label,
                        force=True
                    )

                    # 保存
                    with open(config_path, "w", encoding="utf-8") as f:
                        toml.dump(edited_config, f)

                    st.success(f"✅ 保存しました！")
                    if backup_created and backup_path:
                        st.info(f"📋 バックアップ: {backup_path}")
                    elif not backup_enabled:
                        st.info("ℹ️ バックアップは設定により作成されませんでした")
                    else:
                        st.info("ℹ️ バックアップファイルを作成できませんでした")

                    # トラッキング
                    track_usage(action="設定ファイル編集（モーダル）", tool_name="PR-Agent", username=config_name)

                    # セッションステートをクリア
                    if session_key in st.session_state:
                        del st.session_state[session_key]
                    st.session_state.pop(mode_key, None)

                except toml.TomlDecodeError as e:
                    st.error(f"❌ TOML構文エラー: {e}")
                except Exception as e:
                    st.error(f"❌ 保存エラー: {e}")

        with col2:
            if st.button("🔄 リセット", use_container_width=True):
                # 元の設定に戻す（ファイルから再読み込み）
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        original_from_file = toml.load(f)

                    # すべての関連セッションステートをクリア
                    keys_to_clear = [session_key, original_key, version_key, toml_editor_key, mode_key]
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]

                    # 新しい値を設定
                    fresh_config = copy.deepcopy(original_from_file)
                    st.session_state[session_key] = fresh_config
                    st.session_state[original_key] = copy.deepcopy(original_from_file)
                    st.session_state[version_key] = os.path.getmtime(config_path)
                    reset_widget_values_from_config(fresh_config)

                    st.success("✅ 設定をリセットしました")
                    st.rerun()  # 即座に反映
                except Exception as e:
                    st.error(f"❌ リセットに失敗: {e}")

        with col3:
            if st.button("✖️ 閉じる", use_container_width=True):
                # セッションステートをクリア
                keys_to_clear = [
                    session_key,
                    original_key,
                    version_key,
                    toml_editor_key,
                    mode_key
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                clear_widget_state()
                st.session_state.pop(MODAL_STATE_KEY, None)
                st.rerun()

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




# ページ設定
st.set_page_config(
    page_title="PR-Agent",
    page_icon="🤖",
    layout="wide"
)

# ページ訪問記録（初回のみ）
if 'visited_pr_agent' not in st.session_state:
    track_usage(action="ページ訪問", tool_name="PR-Agent")
    st.session_state.visited_pr_agent = True

# タイトル
st.title("🤖 PR-Agent")
st.markdown("""
<div style='background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;'>
    <h3 style='color: white; margin: 0;'>💡 マージリクエストの自動レビュー</h3>
    <p style='color: #f0fff4; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        AIがコードをレビューして改善提案・テストケース・ドキュメントを自動生成
    </p>
</div>
""", unsafe_allow_html=True)

# 使い方ガイド
with st.expander("💡 使い方を見る", expanded=False):
    st.markdown("""
    ## 📚 このツールでできること

    - ✅ コードレビューの自動化
    - ✅ コード品質の分析
    - ✅ 改善提案の生成
    - ✅ テストケースの提案
    - ✅ ドキュメントの自動生成

    ---

    ## 🚀 使用手順

    ### ステップ1️⃣: MR URLを入力

    GitLabのマージリクエストURLを入力

    ### ステップ2️⃣: API設定

    - GitLab Token（リポジトリアクセス用）
    - OpenAI API キーとユーザID（レビュー生成用）

    ### ステップ3️⃣: 設定を選択

    - プリセット設定（セキュリティ特化、パフォーマンス特化など）
    - コマンド選択（review, improve, describe等）

    ### ステップ4️⃣: レビュー実行

    「🚀 レビュー実行」ボタンをクリック
    """)

st.markdown("---")

# ConfigManagerを初期化
config_manager = ConfigManager()
available_configs = config_manager.get_available_configs()

# サイドバーで設定
with st.sidebar:
    # サイドバーの間隔を狭くするカスタムCSS
    st.markdown("""
    <style>
    /* サイドバーの要素間のマージンを削減 */
    .stSidebar [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    .stSidebar [data-testid="stBlock"]:not(:last-child) {
        margin-bottom: 0.25rem;
    }
    /* セレクトボックス、テキスト入力の下マージンを削減 */
    .stSidebar .stSelectbox, .stSidebar .stTextInput, .stSidebar .stNumberInput {
        margin-bottom: 0.5rem;
    }
    /* マークダウンの上下マージンを削減 */
    .stSidebar .stMarkdown {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }
    /* 区切り線の上下マージンを削減 */
    .stSidebar hr {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("⚙️ 1.設定")

    # AIプロバイダー選択
    ai_provider = st.selectbox(
        "🤖 AIプロバイダー",
        ["OpenAI (Azure)", "Gemini"],
        help="使用するAIモデルのプロバイダーを選択",
        on_change=_close_modal
    )

    # API認証情報
    st.markdown("---")

    # GitLab Token
    default_token = os.getenv("GITLAB_TOKEN", "")
    gitlab_token = st.text_input(
        "🔑 GitLab Token",
        value=default_token,
        type="password",
        help="GitLabアクセストークン（api scope必須）"
    )

    # プロバイダーに応じた認証情報入力
    import json

    gemini_model = ''

    if ai_provider == "OpenAI (Azure)":
        # OPENAI_HEADERS_JSONから値を抽出
        headers_json = os.getenv("OPENAI_HEADERS_JSON", "{}")
        try:
            headers_dict = json.loads(headers_json)
            default_api_key = headers_dict.get("api-key", "")
            default_user_id = headers_dict.get("apim-user-id", "")
        except:
            default_api_key = ""
            default_user_id = ""

        # OpenAI API設定
        api_key = st.text_input(
            "OpenAI APIキー",
            value=default_api_key,
            type="password",
            help="OpenAI APIのキーを入力してください（.envのOPENAI_HEADERS_JSONから自動取得）"
        )

        user_id = st.text_input(
            "ユーザID",
            value=default_user_id,
            help="APIユーザIDを入力してください（.envのOPENAI_HEADERS_JSONから自動取得）"
        )

    else:  # Gemini
        # Gemini API設定
        default_gemini_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini APIキー",
            value=default_gemini_key,
            help="Google Gemini APIのキーを入力してください（.envのGEMINI_API_KEYから自動取得）"
        )

        # Geminiモデル選択
        gemini_model = st.selectbox(
            "Geminiモデル",
            [
                "gemini/gemini-2.0-flash-exp",
                "gemini/gemini-1.5-pro-latest",
                "gemini/gemini-1.5-flash-latest",
                "gemini/gemini-1.5-flash-002"
            ],
            help="使用するGeminiモデルを選択"
        )

        user_id = None  # GeminiではユーザーID不要

    st.markdown("---")

    st.subheader("🎯 2.PR-Agentコマンド")

    # コマンドの説明
    command_descriptions = {
        "review": "📝 コードレビュー - コードの問題点、改善提案、ベストプラクティスを分析",
        "improve": "✨ コード改善 - 具体的なコード改善案を提示（リファクタリング、最適化など）",
        "describe": "📋 MR説明生成 - MRの内容を分析して説明文を自動生成",
        "ask": "❓ 質問応答 - MRに関する質問に回答（例: セキュリティリスクは？）",
        "generate_labels": "🏷️ ラベル生成 - MRの内容に基づいて適切なラベルを提案",
        "add_docs": "📚 ドキュメント追加 - コードのドキュメントを自動生成"
    }

    cmd_col, cmd_desc_col = st.columns([2, 1])
    with cmd_col:
        pr_command = st.selectbox(
            "実行コマンド",
            options=list(command_descriptions.keys()),
            help="実行するPR-Agentコマンドを選択",
            on_change=_close_modal
        )
    with cmd_desc_col:
        st.caption("説明")
        st.caption(command_descriptions[pr_command])

    # askコマンドの場合は質問入力欄を表示
    question = ""
    if pr_command == "ask":
        question = st.text_area(
            "質問内容",
            placeholder="例: このMRのセキュリティリスクは？",
            help="MRに関する質問を入力してください"
        )

    st.markdown("---")

    st.subheader("⚙️ 3.コンテキスト設定")

    # 設定選択
    config_options = {"デフォルト": None}
    config_descriptions = {"デフォルト": "標準的なコードレビュー設定（common.tomlのみ使用）"}

    def extract_description(path):
        """設定ファイルから説明を抽出"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # コメント行で、=や空行でないものを探す
                    if line.startswith('#') and line not in ['#', '# =============================================================================']:
                        desc = line.lstrip('# ').strip()
                        if desc and not desc.startswith('='):
                            return desc
                return Path(path).stem
        except:
            return Path(path).stem

    # カスタム設定（すべての設定はcustomディレクトリに統合）
    for name, path in available_configs["custom"].items():
        config_options[name] = path
        config_descriptions[name] = extract_description(path)


    config_col, config_desc_col = st.columns([2, 1])
    with config_col:
        selected_config = st.selectbox(
            "設定ファイル",
            options=list(config_options.keys()),
            help="PR-Agentの動作を制御する設定ファイルを選択",
            on_change=_close_modal
        )

    config_path = config_options[selected_config]

    with config_desc_col:
        st.caption("説明")
        st.caption(config_descriptions.get(selected_config, "標準設定を使用"))

    # 設定ファイルの確認・編集（モーダルで一括）
    modal_state_key = MODAL_STATE_KEY
    if selected_config != "デフォルト":
        if st.button("⚙️ 設定を確認・編集", use_container_width=True, key="open_config_modal"):
            st.session_state[modal_state_key] = selected_config
        if st.session_state.get(modal_state_key) == selected_config:
            config_editor_modal(selected_config, config_path)
    else:
        st.session_state.pop(modal_state_key, None)

    st.markdown("---")

    with st.expander("🔧 詳細設定", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # デバッグレベル設定
            st.markdown("#### 🔍 ログレベル")
            debug_level = st.selectbox(
                "ログ出力レベル",
                options=[0, 1, 2],
                index=1,
                format_func=lambda x: {
                    0: "エラーのみ",
                    1: "標準（推奨）",
                    2: "詳細"
                }[x],
                help="0:エラーのみ / 1:進捗情報 / 2:デバッグ詳細"
            )
            # verbosity_levelを自動計算
            verbosity_level = min(debug_level, 2)

        with col2:
            # GitLab URL設定
            st.markdown("#### 🌐 GitLab URL")
            default_gitlab_url = os.getenv("GITLAB_URL", "")
            gitlab_url = st.text_input(
                "GitLab URL（任意）",
                value=default_gitlab_url,
                placeholder="例: https://gitlab.example.com",
                help="通常はMR URLから自動抽出されます"
            )

        # GitLab URLのバリデーション
        if gitlab_url:
            normalized_url = UrlValidator.normalize_gitlab_url(gitlab_url)
            if UrlValidator.validate_gitlab_url(normalized_url):
                gitlab_url = normalized_url
            else:
                st.error("❌ 無効なGitLab URL")
                gitlab_url = None

        st.markdown("---")

        # カスタムプロンプト
        custom_prompt = st.text_area(
            "📝 カスタムプロンプト（任意）",
            placeholder="例: セキュリティ脆弱性を重点的にチェック",
            height=80,
            help="レビューに適用する追加の指示"
        )

        # コマンド別の設定
        if pr_command == "improve":
            num_suggestions = st.slider(
                "提案数",
                min_value=1,
                max_value=20,
                value=10,
                help="コード改善提案の数"
            )
        elif pr_command == "review":
            inline_limit = st.slider(
                "インラインコメント上限",
                min_value=10,
                max_value=100,
                value=30,
                help="レビューコメントの最大数"
            )

    st.markdown("---")

# メインエリア
st.subheader("📍 マージリクエスト情報")

# 入力方法選択
input_method = st.radio(
    "入力方法",
    ["URLを直接入力", "プロジェクトから選択"],
    horizontal=True,
    key=INPUT_METHOD_KEY,
    on_change=_close_modal
)

pr_url = ""

if input_method == "URLを直接入力":
    pr_url = st.text_input(
        "MR URL",
        placeholder="https://gitlab.com/group/project/-/merge_requests/1",
        help="レビュー対象のマージリクエストURL"
    )

    # MR URLのバリデーション
    if pr_url:
        if UrlValidator.validate_pr_url(pr_url):
            st.success("✅ 有効なMR/PR URL")
        else:
            st.error("❌ 無効なMR/PR URLです。/merge_requests/ または /pull/ を含むURLを入力してください")
else:
    # プロジェクトから選択
    project_url = st.text_input(
        "プロジェクトURL",
        placeholder="https://gitlab.rp.dss.itmufg/PIT03077/word",
        help="GitLabプロジェクトのURL（例: https://gitlab.rp.dss.itmufg/グループ名/プロジェクト名）"
    )

    if project_url and gitlab_token:
        try:
            import requests
            import re
            import urllib.parse

            # GitLab MR一覧を取得
            # 独自ホスティングにも対応
            match = re.match(r'(https?://[^/]+)/(.+)', project_url.rstrip('/'))
            if match:
                gitlab_base_url = match.group(1)
                project_path = match.group(2)
                # URLエンコード
                encoded_project = urllib.parse.quote(project_path, safe='')

                # GitLab API でMR一覧を取得
                headers = {
                    "PRIVATE-TOKEN": gitlab_token
                }
                api_url = f"{gitlab_base_url}/api/v4/projects/{encoded_project}/merge_requests"

                with st.spinner("MR一覧を取得中..."):
                    response = requests.get(
                        api_url,
                        headers=headers,
                        params={"state": "opened", "order_by": "updated_at", "sort": "desc"}
                    )

                if response.status_code == 200:
                    mrs = response.json()

                    if mrs:
                        # MR選択ボックス
                        mr_options = {
                            f"!{mr['iid']} - {mr['title']} (by {mr['author']['name']})": mr['web_url']
                            for mr in mrs
                        }

                        selected_label = st.selectbox(
                            "マージリクエストを選択",
                            options=list(mr_options.keys()),
                            help="レビューしたいMRを選択してください"
                        )

                        pr_url = mr_options[selected_label]

                        # 選択されたMRの詳細を表示
                        selected_mr = next(mr for mr in mrs if mr['web_url'] == pr_url)

                        with st.expander("📋 MR詳細", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**タイトル**: {selected_mr['title']}")
                                st.write(f"**作成者**: {selected_mr['author']['name']}")
                                st.write(f"**ターゲットブランチ**: {selected_mr['target_branch']}")
                            with col2:
                                st.write(f"**ソースブランチ**: {selected_mr['source_branch']}")
                                st.write(f"**作成日**: {selected_mr['created_at'][:10]}")
                                st.write(f"**更新日**: {selected_mr['updated_at'][:10]}")
                    else:
                        st.info("このプロジェクトにはオープンなMRがありません")
                else:
                    st.error(f"❌ MR一覧の取得に失敗しました: {response.status_code}")
                    if response.status_code == 401:
                        st.error("GitLab Tokenが無効です")
                    elif response.status_code == 404:
                        st.error("プロジェクトが見つかりません")
            else:
                st.warning("⚠️ プロジェクトURLにはプロジェクトパスが必要です")
                st.info("""
**正しい形式:**
- ✅ `https://gitlab.rp.dss.itmufg/グループ名/プロジェクト名`
- ✅ `https://gitlab.rp.dss.itmufg/PIT03077/word`

**間違った形式:**
- ❌ `https://gitlab.rp.dss.itmufg` （プロジェクトパスが無い）
                """)

        except Exception as e:
            st.error(f"エラー: {str(e)}")
    elif project_url and not gitlab_token:
        st.warning("⚠️ GitLab Tokenを入力してください")

st.markdown("---")

# 実行状態の管理
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'execute_params' not in st.session_state:
    st.session_state.execute_params = None
if 'log_text' not in st.session_state:
    st.session_state.log_text = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# 実行ボタン
# Geminiの場合はuser_id不要
if ai_provider == "Gemini":
    button_disabled = not (gitlab_token and api_key and pr_url)
else:
    button_disabled = not (gitlab_token and api_key and user_id and pr_url)

if pr_command == "ask":
    button_disabled = button_disabled or not question

# 実行中は無効化
button_disabled = button_disabled or st.session_state.is_running

if st.session_state.is_running and not st.session_state.execute_params:
    # 実行が完了した状態（paramsはクリアされている）
    st.session_state.is_running = False  # 状態をクリア

# 実行ボタンを2つに分割
col_execute1, col_execute2 = st.columns(2)

with col_execute1:
    preview_button = st.button("📋 プレビュー実行（投稿しない）", use_container_width=True, disabled=button_disabled)

with col_execute2:
    execute_button = st.button("🚀 実行して投稿", type="primary", use_container_width=True, disabled=button_disabled)

# プレビューボタンまたは実行ボタンが押された場合
if preview_button or execute_button:
    is_preview_mode = preview_button  # プレビューボタンが押された場合はTrue

    # モーダル状態をクリア（ボタン押下時にモーダルが表示されないように）
    st.session_state.pop(MODAL_STATE_KEY, None)

    # バリデーション
    if not gitlab_token or not api_key:
        st.error("❌ GitLab TokenとAPIキーを入力してください")
    elif ai_provider == "OpenAI (Azure)" and not user_id:
        st.error("❌ OpenAI (Azure)にはユーザIDが必要です")
    elif not pr_url:
        st.error("❌ MR URLを入力してください")
    elif pr_command == "ask" and not question:
        st.error("❌ askコマンドには質問内容が必要です")
    else:
        # 実行ボタン押下を記録
        mode_label = "プレビュー実行" if is_preview_mode else "実行して投稿"
        track_usage(action=f"{mode_label}ボタン押下", tool_name="PR-Agent", username=f"{pr_command}コマンド")

        st.session_state.log_text = ""
        st.session_state.last_result = None

        # 実行パラメータを保存
        st.session_state.execute_params = {
            'gitlab_token': gitlab_token,
            'gitlab_url': gitlab_url if gitlab_url else None,
            'ai_provider': ai_provider,
            'api_key': api_key,
            'user_id': user_id,
            'pr_url': pr_url,
            'pr_command': pr_command,
            'question': question,
            'gemini_model': gemini_model,
            'config_path': config_path,
            'custom_prompt': custom_prompt,
            'selected_config': selected_config,
            'debug_level': debug_level,
            'verbosity_level': verbosity_level,
            'is_preview_mode': is_preview_mode  # プレビューモードフラグ
        }
        # 実行状態を設定して再レンダリング（二重クリック防止）
        st.session_state.is_running = True
        st.rerun()

# 前回の実行結果を表示（実行ボタンの下）
if st.session_state.get('last_result') and not st.session_state.is_running:
    st.markdown("---")
    st.subheader("📊 前回の実行結果")

    # タブで実行ログと結果を分ける
    log_tab_prev, result_tab_prev = st.tabs(["📋 実行ログ", "✅ 実行結果"])

    with log_tab_prev:
        if st.session_state.get('last_log'):
            st.text(st.session_state.last_log)
        else:
            st.info("実行ログはありません")

    with result_tab_prev:
        result_placeholder_prev = st.empty()
        render_result_summary(result_placeholder_prev, st.session_state.last_result)

# 実行パラメータがある場合は実行
if st.session_state.is_running and st.session_state.execute_params:
    params = st.session_state.execute_params
    st.session_state.execute_params = None  # パラメータをクリア

    try:
        # API認証情報を環境変数に設定（GitLab用）
        os.environ['GITLAB_TOKEN'] = params['gitlab_token']
        # GitプロバイダーをGitLabに固定（PR-AgentのURL自動判定をオーバーライド）
        os.environ['GIT_PROVIDER'] = 'gitlab'

        # API設定を準備（PR-Agent設定ファイルに注入）
        import json

        if params['ai_provider'] == "Gemini":
            # Gemini用の設定
            api_config = {
                'provider': 'gemini',
                'api_key': params['api_key'],
                'model': params['gemini_model']
            }
            # Geminiの場合は環境変数でプロバイダーとモデルを明示
            os.environ['AI_PROVIDER'] = 'google'
            os.environ['GEMINI_API_KEY'] = params['api_key']
            os.environ['GEMINI_MODEL'] = params['gemini_model']
        else:
            # OpenAI (Azure)用の設定
            base_url = os.getenv("OPENAI_BASE_URL", "")
            api_path = os.getenv("OPENAI_PATH", "/chat/completions")
            api_config = {
                'provider': 'openai',
                'api_key': params['api_key'],
                'base_url': base_url,
                'api_path': api_path,
                'user_id': params['user_id'],
                'custom_headers': {
                    'api-key': params['api_key'],
                    'apim-user-id': params['user_id']
                }
            }
            # OpenAI利用時はGemini用の環境変数をリセット
            os.environ.pop('AI_PROVIDER', None)
            os.environ.pop('GEMINI_API_KEY', None)
            os.environ.pop('GEMINI_MODEL', None)
            os.environ['AI_PROVIDER'] = 'openai'

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 設定ファイルを適用
        status_text.text("⚙️ 設定ファイルを適用中...")
        progress_bar.progress(10)

        config_applied = False
        gitlab_url_param = params.get('gitlab_url')

        if params['config_path']:
            # 選択された設定ファイルを適用
            config_applied = config_manager.apply_config(
                params['config_path'],
                params['custom_prompt'],
                api_config,
                gitlab_url=gitlab_url_param,
                verbosity=params.get('verbosity_level', 1),
                preview_mode=params.get('is_preview_mode', False),
                pr_command=params['pr_command']
            )
        else:
            # デフォルト設定を作成
            config_manager.create_default_config(
                params['custom_prompt'],
                api_config,
                gitlab_url=gitlab_url_param,
                verbosity=params.get('verbosity_level', 1),
                preview_mode=params.get('is_preview_mode', False),
                pr_command=params['pr_command']
            )
            config_applied = True

        if config_applied:
            config_file_path = config_manager.config_file
            params['resolved_config_file'] = str(config_file_path)
            status_text.text(f"✅ 設定ファイルを適用しました ({config_file_path})")
            try:
                import toml
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    applied_config = toml.load(f)

                # コマンドに応じてフィルタリング
                command_section_map = {
                    "review": ["pr_reviewer"],
                    "improve": ["pr_improve", "pr_code_suggestions"],
                    "describe": ["pr_description"],
                    "ask": ["pr_questions"],
                    "generate_labels": ["pr_generate_labels"],
                    "add_docs": ["pr_add_docs"]
                }

                relevant_sections = command_section_map.get(params['pr_command'], [])
                filtered_config = {}
                for section in relevant_sections:
                    if section in applied_config:
                        filtered_config[section] = applied_config[section]

                # プレビューモードの場合、設定を確認
                if params.get('is_preview_mode'):
                    st.info("💡 プレビューモードで実行されました（GitLabに投稿されていません）")
                    with st.expander("📄 適用された設定（全体）を確認", expanded=False):
                        config_text = Path(config_file_path).read_text(encoding="utf-8")
                        st.code(config_text, language="toml")

                        # publish_output の確認
                        if 'publish_output = false' in config_text.lower():
                            st.success("✅ publish_output = false が設定されています")
                        else:
                            st.error("❌ publish_output = false が設定されていません！")

                # フィルタリングされた設定を表示
                filtered_toml = toml.dumps(filtered_config)

                with st.expander(f"📄 適用された設定 ({params['pr_command']}コマンド用)", expanded=False):
                    if relevant_sections:
                        st.info(f"💡 {params['pr_command']}コマンドに関連する設定のみ表示: {', '.join(relevant_sections)}")
                        st.code(filtered_toml, language="toml")

                    # 全設定を見るオプション
                    with st.expander("🔍 全設定を表示", expanded=False):
                        config_text = Path(config_file_path).read_text(encoding="utf-8")
                        preview = config_text if len(config_text) <= 4000 else config_text[:4000] + "\n... (truncated)"
                        st.code(preview, language="toml")

            except Exception as config_error:
                st.warning(f".pr_agent.toml の読み込みに失敗しました: {config_error}")
        else:
            st.error("❌ 設定ファイルの適用に失敗しました")
            st.session_state.is_running = False
            raise RuntimeError("Failed to apply PR-Agent configuration")

        status_text.text(f"🔄 PR-Agent {params['pr_command']} コマンドを実行中...（2～3分程度かかります）")
        progress_bar.progress(30)

        # 実行中の操作ガイド
        st.info("💡 **実行中の操作:** 途中で中断したい場合は、ブラウザをリロード（F5キー）してください。失敗した場合は、実行結果タブでエラーログを確認できます。")

        # タブで実行ログと結果を分ける
        log_tab, result_tab = st.tabs(["📋 実行ログ", "✅ 実行結果"])

        with log_tab:
            log_placeholder = st.empty()

        with result_tab:
            result_placeholder = st.empty()

        # PR-Agentを実行
        extra_args = []
        if params['pr_command'] == "ask" and params['question']:
            extra_args.append(params['question'])

        # ログ収集用（標準出力/エラー出力をキャプチャ）
        import sys
        import io
        import time
        import concurrent.futures

        log_lines = []
        capture_running = True

        def update_log_display(text):
            st.session_state.log_text = text
            if text:
                log_placeholder.text(text)
            else:
                log_placeholder.info("実行ログはここに表示されます")

        # 標準出力/エラー出力をキャプチャするクラス
        class OutputCapture:
            def __init__(self, original_stream):
                self.original_stream = original_stream
                self.buffer = io.StringIO()

            def write(self, text):
                self.original_stream.write(text)
                self.original_stream.flush()
                if text.strip():
                    log_lines.append(text.rstrip())
                    # 最新100行のみ保持
                    if len(log_lines) > 100:
                        log_lines.pop(0)

            def flush(self):
                self.original_stream.flush()

        # 標準出力/エラー出力をキャプチャ
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = OutputCapture(old_stdout)
        sys.stderr = OutputCapture(old_stderr)

        try:
            # Streamlitセッションステートからセッション IDを取得
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            session_id = ctx.session_id if ctx else None

            # セッションログをクリア（前回実行のログが残らないように）
            if session_id:
                Logger.clear_session_logs(session_id)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # PR-Agentを非同期で実行
                future = executor.submit(
                    PRAgentRunner.run_sync,
                    params['pr_url'],
                    params['pr_command'],
                    extra_args,
                    params.get('resolved_config_file'),
                    params.get('gitlab_url'),
                    params.get('debug_level', 1),
                    session_id  # セッションIDを渡す
                )

                # 完了するまでログを更新
                while not future.done():
                    # セッションログを取得して表示
                    if session_id:
                        session_logs = Logger.get_session_logs(session_id)
                        if session_logs:
                            log_text = '\n'.join([log['message'] for log in session_logs])
                            update_log_display(log_text)
                    elif log_lines:
                        # フォールバック: 標準出力キャプチャ
                        log_text = '\n'.join(log_lines)
                        update_log_display(log_text)
                    time.sleep(0.5)  # 0.5秒ごとに更新

                # 最終結果を取得
                result = future.result()

            # 最終ログを表示
            if session_id:
                session_logs = Logger.get_session_logs(session_id)
                if session_logs:
                    log_text = '\n'.join([log['message'] for log in session_logs])
                    update_log_display(log_text)
            elif log_lines:
                # フォールバック: 標準出力キャプチャ
                log_text = '\n'.join(log_lines)
                update_log_display(log_text)
        finally:
            # 標準出力/エラー出力を元に戻す
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        progress_bar.progress(100)

        # ログからエラー/警告を検出
        errors = [line for line in log_lines if 'ERROR' in line or 'Exception' in line or 'Traceback' in line]
        warnings = [line for line in log_lines if 'WARNING' in line or 'warning' in line or 'Failed to generate prediction' in line]

        result_state = {
            'status': 'success' if result else 'error',
            'warnings': warnings,
            'errors': [] if result else errors,
            'params': {
                'pr_command': params['pr_command'],
                'pr_url': params['pr_url'],
                'gitlab_url': params.get('gitlab_url'),
                'ai_provider': params['ai_provider'],
                'gemini_model': params.get('gemini_model'),
                'selected_config': params.get('selected_config', 'デフォルト'),
                'question': params.get('question'),
                'custom_prompt': params.get('custom_prompt'),
                'is_preview_mode': params.get('is_preview_mode')
            }
        }

        status_text.text("✅ 実行完了！" if result else "❌ レビュー失敗")
        st.session_state.last_result = result_state
        render_result_summary(result_placeholder, result_state)
        st.session_state.execute_params = None

        # 最終ログを session_state に保存（ページ更新後も表示できるように）
        if session_id:
            session_logs = Logger.get_session_logs(session_id)
            if session_logs:
                st.session_state.last_log = '\n'.join([log['message'] for log in session_logs])
        elif log_lines:
            st.session_state.last_log = '\n'.join(log_lines)

        # 実行状態を解除（最後に設定）
        st.session_state.is_running = False

        # 実行完了後、ボタンを有効化するためにページを更新（結果はlast_resultから表示される）
        st.rerun()

    except Exception as e:
        st.session_state.is_running = False
        st.session_state.execute_params = None  # エラー時もクリア
        st.session_state.last_result = None
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.exception(e)

        # ページを再読み込みしてボタンを有効化
        st.info("🔄 ページを更新してください（F5キーを押すか、ブラウザの更新ボタンをクリック）")

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        PR-Agent v2.0 | Powered by Streamlit & tool-branch backend
    </div>
    """,
    unsafe_allow_html=True
)
