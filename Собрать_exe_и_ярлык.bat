@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ============================================
echo   Сборка exe и ярлык на рабочем столе
echo ============================================
echo.

REM Используем venv репозитория, если нет своего
set PY=python
if exist "..\venv\Scripts\python.exe" set PY="..\venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set PY="venv\Scripts\python.exe"

echo 0. Проверка зависимостей (PyInstaller, PyQt6)...
%PY% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo     Установка requirements-desktop.txt...
    %PY% -m pip install -r requirements-desktop.txt
    if errorlevel 1 (
        echo Ошибка установки. Проверьте интернет и права.
        pause
        exit /b 1
    )
    echo     Готово.
) else (
    echo     Уже установлены.
)
echo.

echo 1. Сборка MonitorCompetitors.exe ...
%PY% build_desktop.py
if errorlevel 1 (
    echo Ошибка сборки.
    pause
    exit /b 1
)

echo.
echo 2. Создание ярлыка на рабочем столе ...
%PY% create_desktop_shortcut.py
if errorlevel 1 (
    echo Ярлык не создан. Exe уже в папке проекта — можно запускать отсюда.
)

echo.
echo Готово. Запуск с рабочего стола: двойной клик по ярлыку «Monitoring_competitors».
pause
