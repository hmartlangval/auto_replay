# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files for packages that might need them
datas = []

# Add the runtime folders that users can modify
datas += [('prompts', 'prompts')]
datas += [('sequences', 'sequences')]  
datas += [('images', 'images')]

# Add automation modules and their data
datas += [('automation', 'automation')]

# Add utils modules
datas += [('utils', 'utils')]

# Add examples (optional, can be removed if not needed)
datas += [('examples', 'examples')]

# Collect any additional data files from packages
try:
    datas += collect_data_files('cv2')
except:
    pass

try:
    datas += collect_data_files('numpy')
except:
    pass

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'pynput.mouse._win32',
    'pynput.keyboard._win32', 
    'cv2',
    'numpy',
    'win32gui',
    'win32api', 
    'win32con',
    'dotenv',
    'tkinter',
    'PIL._tkinter_finder',
    'openai',
    'langchain_openai',
    'langchain_core'
]

# Try to collect all submodules for critical packages
try:
    hiddenimports += collect_submodules('pynput')
except:
    pass

try:
    hiddenimports += collect_submodules('cv2')
except:
    pass

block_cipher = None

a = Analysis(
    ['hello_world_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FiservAutomationTaskbar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have one
) 