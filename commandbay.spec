# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['start_server.py'],
    pathex=[],
    binaries=[],
    datas=[('start_server.py', '.'), ('alembic.ini', '.'), ('alembic', 'alembic'), ('frontend/out', 'frontend'), ('static', 'static')],
    hiddenimports=['commandbay.version', 'commandbay.models'],
    hookspath=['.'],
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
    name='commandbay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['frontend\\src\\app\\favicon.ico'],
)
