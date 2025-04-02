# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# A function to locate data files
def get_data_files():
    import os
    
    data_files = []
    
    # Add assets directory
    if os.path.exists('app/assets'):
        data_files.append(('app/assets', 'app/assets'))
    
    # Add any other required data files
    additional_files = [
        'README.md',
        'HOW_TO_RUN.txt',
        'autostart.py'
    ]
    
    for file in additional_files:
        if os.path.exists(file):
            data_files.append((file, '.'))
    
    return data_files

# Check if standard icon files exist, otherwise use the jpeg
icon_file = None
for icon_path in ['app/assets/icon.ico', 'app/assets/icon.icns', 'app/assets/icon.jpeg', 'app/assets/icon.jpg', 'app/assets/icon.png']:
    if os.path.exists(icon_path):
        icon_file = icon_path
        break

# Get all data files
added_files = get_data_files()

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'matplotlib',
        'numpy',
        'pandas',
        'requests',
        'mplfinance',
        'pywin32' if sys.platform == 'win32' else None,
        'winreg' if sys.platform == 'win32' else None,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Windows executable
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WallStonks',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file,
        version='file_version_info.txt' if os.path.exists('file_version_info.txt') else None,
    )

# macOS application bundle
elif sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='WallStonks',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='WallStonks',
    )
    
    app = BUNDLE(
        coll,
        name='WallStonks.app',
        icon=icon_file,
        bundle_identifier='com.wallstonks.app',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleGetInfoString': 'WallStonks Real-time Stock Wallpaper Application',
            'NSHighResolutionCapable': 'True',
            'NSRequiresAquaSystemAppearance': 'False',
            'LSUIElement': '1',  # Makes it a background application
        },
    )

# Linux executable
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WallStonks',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
