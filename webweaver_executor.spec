# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# Ensure PyInstaller knows where to look for your packages
# PyInstaller doesn't define __file__, so use current working directory
project_dir = os.path.abspath(os.getcwd())
sys.path.insert(0, project_dir)

block_cipher = None

# Automatically collect all aiohttp submodules
aiohttp_modules = collect_submodules('aiohttp')
yarl_modules = collect_submodules('yarl')
multidict_modules = collect_submodules('multidict')
async_timeout_modules = collect_submodules('async_timeout')

a = Analysis(
    ['webweaver/executor/main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'webweaver.executor',
        'webweaver.executor.test_decorators',
        'webweaver.executor.executor_exceptions',
        'webweaver.executor.test_listener',
        'webweaver.executor.test_status',
        'webweaver.web',
        'webweaver.web.api_client',
        'webweaver.web.web_driver',
        'webweaver.web.web_driver_option',
        'webweaver.web.browser_type',
        'webweaver.web.button_control',
        'webweaver.web.autocomplete_textbox_control',
        'webweaver.web.dropdown_control',
        'webweaver.web.radio_button_control',
        'webweaver.web.tickbox_control',
        'webweaver.web.text_element_control',
        'webweaver.web.textbox_control',
        'webweaver.web.text_element_control',
        'webweaver.web.exceptions',
        'webweaver.web.webweaver_page',

        # Auto include aiohttp and dependencies
        *aiohttp_modules,
        *yarl_modules,
        *multidict_modules,
        *async_timeout_modules,
    ],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='webweaver_executor',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    onefile=True,
)
