#!/usr/bin/env python3
"""
Сборка exe и копирование в папку проекта. Запуск из папки PEm08: python build_desktop.py
После сборки: скопируйте всю папку PEm08 на рабочий стол и запускайте exe оттуда.
"""
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SPEC = PROJECT_ROOT / "desktop.spec"
DIST = PROJECT_ROOT / "dist"
EXE_NAME = "MonitorCompetitors.exe"


def main():
    print("Сборка exe (PyInstaller)...")
    r = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", str(SPEC)],
        cwd=str(PROJECT_ROOT),
    )
    if r.returncode != 0:
        print("Ошибка сборки.")
        sys.exit(1)

    src = DIST / EXE_NAME
    if not src.exists():
        print(f"Не найден {src}")
        sys.exit(1)

    dest = PROJECT_ROOT / EXE_NAME
    shutil.copy2(src, dest)
    print(f"Exe скопирован: {dest}")

    print()
    print("Чтобы вынести на рабочий стол:")
    print("1. Скопируйте всю папку проекта на рабочий стол:")
    print("   Лекции\\Промтинжениринг\\PEm08. Проект мультимодальное приложение  →  Рабочий стол")
    print("2. На рабочем столе откройте папку и запустите MonitorCompetitors.exe")
    print("   (рядом с exe должны быть папки backend, frontend и файл .env)")
    print()
    print("Либо: правый клик по exe → Создать ярлык → перетащите ярлык на рабочий стол.")
    print("Запускайте всегда через ярлык из папки с backend и frontend.")


if __name__ == "__main__":
    main()
