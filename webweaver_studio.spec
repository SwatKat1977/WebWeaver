# -*- mode: python ; coding: utf-8 -*-
import sys
import os

project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

from webweaver.studio.version import MAJOR, MINOR, PATCH, __version__


from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct
)

file_version_tuple = (MAJOR, MINOR, PATCH, 0)
file_version_string = f"{MAJOR}.{MINOR}.{PATCH}"

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=file_version_tuple,
        prodvers=file_version_tuple,
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904B0',
                [
                    StringStruct('CompanyName', 'WebWeaver Development Team'),
                    StringStruct('FileDescription', 'WebWeaver Studio'),
                    StringStruct('FileVersion', file_version_string),
                    StringStruct('InternalName', 'WebWeaverStudio'),
                    StringStruct('OriginalFilename', 'WebWeaverStudio.exe'),
                    StringStruct('ProductName', 'WebWeaver Studio'),
                    StringStruct('ProductVersion', __version__),
                    StringStruct('LegalCopyright', '© 2025-2026 WebWeaver Development Team'),
                ]
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

block_cipher = None


a = Analysis(
    ['webweaver/studio/studio.py'],
    pathex=['.'],
    binaries=[],
    datas=[
    ('artwork_resources/studio/app_logo.ico', 'artwork_resources/studio')],
    hiddenimports=['wx',
                   'wx.adv',
                   'wx.lib.mixins.listctrl',

                   # Selenium core
                   'selenium',
                   'selenium.webdriver',
                   'selenium.webdriver.common',

                   # Chrome / Chromium
                   'selenium.webdriver.chrome',
                   'selenium.webdriver.chrome.webdriver',
                   'selenium.webdriver.chrome.service',
                   'selenium.webdriver.chrome.options',

                   # Edge (Chromium)
                   'selenium.webdriver.edge',
                   'selenium.webdriver.edge.webdriver',
                   'selenium.webdriver.edge.service',
                   'selenium.webdriver.edge.options',

                   # webdriver-manager
                   'webdriver_manager',
                   'webdriver_manager.chrome',
                   'webdriver_manager.microsoft'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WebWeaverStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    version=version_info,
    console=False,
    icon='artwork_resources/studio/app_logo.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='WebWeaverStudio',
)
