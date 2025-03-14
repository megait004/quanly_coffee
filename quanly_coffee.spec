# -*- mode: python ; coding: utf-8 -*-
import os

# Lấy đường dẫn tuyệt đối của thư mục dự án
project_root = os.path.abspath(SPECPATH)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'static'), 'static'),
        (os.path.join(project_root, 'config'), 'config'),
        (os.path.join(project_root, 'sample_data'), 'sample_data'),
        (os.path.join(project_root, 'utils'), 'utils'),
        (os.path.join(project_root, 'views'), 'views'),
        (os.path.join(project_root, 'models'), 'models'),
        (os.path.join(project_root, 'controllers'), 'controllers')
    ],
    hiddenimports=[
        'sqlite3',
        'sqlite3.dbapi2',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'utils.styles',
        'utils.validators',
        'utils.csv_importer',
        'views.dialogs.login_dialog',
        'views.dialogs.register_dialog',
        'views.windows.admin_window',
        'views.windows.staff_window',
        'views.windows.customer_window',
        'views.managers.employee_manager',
        'views.managers.inventory_manager',
        'views.managers.menu_manager',
        'views.managers.order_manager',
        'views.managers.report_manager',
        'views.managers.table_manager'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    collect_submodules=['sqlite3']
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuanLyCoffee',
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
    icon=os.path.join(project_root, 'static', 'images', 'logo.png')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QuanLyCoffee',
)