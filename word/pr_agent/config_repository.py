#!/usr/bin/env python3
"""
Configuration repository utilities.

Responsible for listing, reading, and writing the canonical configuration
files that live under word/configs/custom. These files are shared assets and
must remain consistent even when multiple users edit them concurrently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union
import hashlib
import os
import shutil
import tempfile


class ConfigConflictError(RuntimeError):
    """Raised when a config file changed on disk while editing."""

    def __init__(self, path: Path, current_hash: str):
        self.path = path
        self.current_hash = current_hash
        super().__init__(f"Configuration file was updated by another user: {path}")


@dataclass
class ConfigFileInfo:
    name: str
    path: Path
    hash: str
    mtime: float


@dataclass
class BackupInfo:
    path: Path
    label: str
    size: int
    timestamp: float


@dataclass
class SaveResult:
    path: Path
    new_hash: str
    backup_path: Optional[Path]


Identifier = Union[str, Path]


class ConfigRepository:
    """Provides safe access to shared configuration files."""

    def __init__(self, custom_dir: Optional[Union[str, Path]] = None):
        if custom_dir:
            base_dir = Path(custom_dir).expanduser().resolve()
        else:
            base_dir = Path(__file__).resolve().parents[1] / "configs" / "custom"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------------- #
    # Public helpers
    # --------------------------------------------------------------------- #
    def list_configs(self) -> List[ConfigFileInfo]:
        infos: List[ConfigFileInfo] = []
        for path in sorted(self.base_dir.glob("*.toml")):
            text = path.read_text(encoding="utf-8")
            infos.append(
                ConfigFileInfo(
                    name=path.stem,
                    path=path,
                    hash=self._hash_text(text),
                    mtime=path.stat().st_mtime,
                )
            )
        return infos

    def load_text(self, identifier: Identifier) -> tuple[Path, str, str]:
        path = self._resolve(identifier)
        text = path.read_text(encoding="utf-8")
        return path, text, self._hash_text(text)

    def save_text(
        self,
        identifier: Identifier,
        content: str,
        *,
        expected_hash: Optional[str],
        create_backup: bool = True,
        backup_label: str = "",
    ) -> SaveResult:
        path = self._resolve(identifier)
        current_text = path.read_text(encoding="utf-8") if path.exists() else ""
        current_hash = self._hash_text(current_text) if current_text else ""

        if expected_hash and expected_hash != current_hash:
            raise ConfigConflictError(path, current_hash)

        backup_path: Optional[Path] = None
        if create_backup and path.exists():
            safe_label = self._normalize_label(backup_label)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_suffix = f".backup.{timestamp}"
            if safe_label:
                backup_suffix += f"_{safe_label}"
            backup_path = path.parent / f"{path.name}{backup_suffix}"
            shutil.copy(path, backup_path)

        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(content)
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return SaveResult(path=path, new_hash=self._hash_text(content), backup_path=backup_path)

    def list_backups(self, identifier: Identifier) -> List[BackupInfo]:
        path = self._resolve(identifier)
        backups: List[BackupInfo] = []
        pattern = f"{path.name}.backup.*"
        for file_path in sorted(path.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
            label = file_path.name.split(".backup.", 1)[1] if ".backup." in file_path.name else "unknown"
            stat = file_path.stat()
            backups.append(
                BackupInfo(
                    path=file_path,
                    label=label,
                    size=stat.st_size,
                    timestamp=stat.st_mtime,
                )
            )
        return backups

    def restore_backup(self, identifier: Identifier, backup_path: Identifier) -> None:
        path = self._resolve(identifier)
        backup = Path(backup_path).expanduser().resolve()
        if not backup.exists():
            raise FileNotFoundError(f"Backup file not found: {backup}")
        shutil.copy(backup, path)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _resolve(self, identifier: Identifier) -> Path:
        path = Path(identifier)
        if not path.is_absolute():
            path = self.base_dir / path
        return path.resolve()

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_label(label: str) -> str:
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in label.strip())
        return safe[:32]

