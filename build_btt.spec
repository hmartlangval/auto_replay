# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files for packages that might need them
datas = []

# Add the runtime folders that BTT needs
datas += [('prompts', 'prompts')]
datas += [('images', 'images')]

# Add the BTT-specific modules and their dependencies
datas += [('automation/btt/forms', 'automation/btt/forms')]
datas += [('automation/btt/helpers.py', 'automation/btt')]
datas += [('automation/btt/questionnaire_filler.py', 'automation/btt')]

# Add utils modules that BTT depends on
datas += [('utils', 'utils')]

# Collect any additional data files from packages
try:
    datas += collect_data_files('cv2')
except:
    pass

try:
    datas += collect_data_files('numpy')
except:
    pass

try:
    datas += collect_data_files('mss')
except:
    pass

try:
    datas += collect_data_files('PIL')
except:
    pass

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'pynput.mouse._win32',
    'pynput.keyboard._win32', 
    'cv2',
    'numpy',
    'mss',  # CRITICAL: Required by utils.image_scanner for screen capture
    'mss.base',
    'mss.darwin',
    'mss.linux',
    'mss.windows',
    'win32gui',
    'win32api', 
    'win32con',
    'dotenv',
    'tkinter',
    'tkinter.ttk',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'openai',
    'langchain_openai',
    'langchain_openai.chat_models',
    'langchain_core',
    'langchain_core.messages',
    'langchain_core.prompts',
    # BTT-specific imports
    'automation.btt.forms',
    'automation.btt.forms.base_forms',
    'automation.btt.forms.custom_forms',
    'automation.btt.forms.default_forms',
    'automation.btt.forms.emvco_l1_forms',
    'automation.btt.forms.emvco_l2_forms',
    'automation.btt.helpers',
    'automation.btt.questionnaire_filler',
    'utils.common',
    'utils.windows_automation',
    'utils.image_scanner',
    'utils.graphics',
    'utils.sequence_player',
    'utils.treeview.treeview_navigator',
    'utils.treeview.treeview_path_computer',
    'utils.ai_service',
    'utils.file_utils',
    'utils.navigation_parser',
    'utils.text_reader',
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

try:
    hiddenimports += collect_submodules('mss')
except:
    pass

try:
    hiddenimports += collect_submodules('PIL')
except:
    pass

try:
    hiddenimports += collect_submodules('langchain_openai')
except:
    pass

try:
    hiddenimports += collect_submodules('langchain_core')
except:
    pass

block_cipher = None

a = Analysis(
    ['automation/btt/btt.py'],  # Full path from project root for integrated builds
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
    name='btt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for BTT debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have one
) 