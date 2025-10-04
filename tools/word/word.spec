# -*- mode: python ; coding: utf-8 -*-
import certifi
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# certifi証明書のパスを取得
cert_datas = [(certifi.where(), 'certifi')]

# .envファイルをバンドル（存在する場合）
env_file = '.env'
if os.path.exists(env_file):
    cert_datas.append((env_file, '.'))

a = Analysis(
    ['word.py'],
    pathex=[],
    binaries=[],
    datas=cert_datas,
    hiddenimports=[
        'certifi',
        'win_inet_pton',  # Windows DNS解決用
        'openpyxl.cell._writer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='word',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # コンソールウィンドウを表示（デバッグ用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
