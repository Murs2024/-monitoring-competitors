# Сборка exe: pyinstaller desktop.spec
# В exe упакованы backend, frontend и зависимости (fastapi и т.д.). Рядом с exe нужен только .env.

# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH)

# Подключить frontend (статика) и подтянуть fastapi/starlette
try:
    from PyInstaller.utils.hooks import collect_all
    fapi_datas, fapi_binaries, fapi_hidden = collect_all('fastapi')
    starlette_datas, _, starlette_hidden = collect_all('starlette')
except Exception:
    fapi_datas = fapi_binaries = fapi_hidden = []
    starlette_datas = starlette_hidden = []

datas = [(str(project_root / 'frontend'), 'frontend')] + list(fapi_datas or []) + list(starlette_datas or [])

hidden = [
    'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan', 'uvicorn.lifespan.on',
    'backend', 'backend.main', 'backend.config', 'backend.models', 'backend.models.schemas',
    'backend.services', 'backend.services.openai_service', 'backend.services.parser_service', 'backend.services.history_service',
    'fastapi', 'starlette', 'starlette.routing', 'starlette.responses', 'starlette.staticfiles',
    'pydantic', 'openai', 'httpx', 'bs4', 'dotenv', 'python_dotenv',
]
if fapi_hidden:
    hidden = list(fapi_hidden) + hidden
if starlette_hidden:
    hidden = list(starlette_hidden) + hidden

a = Analysis(
    [str(project_root / 'desktop_app.py')],
    pathex=[str(project_root)],
    hiddenimports=hidden,
    datas=datas,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonitorCompetitors',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
