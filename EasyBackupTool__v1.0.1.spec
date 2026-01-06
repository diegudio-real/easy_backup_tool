# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['EasyBackupTool__v1.0.1.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6.Qt6WebEngineCore', 'PyQt6.Qt6WebEngineWidgets', 'PyQt6.Qt6WebEngineQuick', 'PyQt6.Qt6Qml', 'PyQt6.Qt6Quick', 'PyQt6.Qt6Multimedia', 'PyQt6.Qt6MultimediaWidgets', 'PyQt6.Qt6Network', 'PyQt6.Qt6Sensors', 'PyQt6.Qt6Positioning', 'PyQt6.Qt6SerialPort'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EasyBackupTool__v1.0.1',
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
    icon=['assets\\icon.ico'],
)
