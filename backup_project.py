#!/usr/bin/env python3
"""
Создаёт полный бекап проекта (архив ZIP) для отчёта.
Включает все файлы и папки, кроме venv, __pycache__, .env, backups и самого архива.
Файл .env не попадает в бекап, чтобы ключи не уходили наружу.
Архивы сохраняются ВНУТРИ проекта: папка backups/. Хранится не более 3 архивов; лишние удаляются (остаются самые новые).
"""
import zipfile
from pathlib import Path
from datetime import datetime

# Корень проекта = папка, где лежит этот скрипт
PROJECT_ROOT = Path(__file__).resolve().parent
BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_PREFIX = "PEm08_backup_"
MAX_BACKUPS = 3

EXCLUDE_DIRS = {"venv", "__pycache__", ".git", "backups"}
EXCLUDE_FILES = {".env"}

# ANSI-цвета для терминала (поддержка Windows 10+, PowerShell, Windows Terminal)
C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "red": "\033[91m",
    "dim": "\033[2m",
}


def msg(text: str, color: str = "reset") -> None:
    print(f"{C.get(color, '')}{text}{C['reset']}")


def ensure_backup_dir() -> None:
    """Создать папку backups/ внутри проекта, если её нет."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def get_backups() -> list[tuple[Path, float]]:
    """Список архивов PEm08_backup_*.zip в папке backups/, отсортированный по дате (новые первые)."""
    if not BACKUP_DIR.exists():
        return []
    files = []
    for p in BACKUP_DIR.glob(f"{BACKUP_PREFIX}*.zip"):
        if p.is_file():
            files.append((p, p.stat().st_mtime))
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def trim_old_backups(backups: list[tuple[Path, float]]) -> None:
    """Удаляет архивы сверх MAX_BACKUPS (оставляет только самые новые)."""
    for path, _ in backups[MAX_BACKUPS:]:
        try:
            path.unlink()
            msg(f"  Удалён старый бекап: {path.name}", "red")
        except OSError:
            pass


def backup_project() -> Path:
    """Создать архив в backups/ и вернуть путь к нему."""
    ensure_backup_dir()
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_name = BACKUP_DIR / f"{BACKUP_PREFIX}{date_str}.zip"

    msg("\n  📦 Создание архива...", "cyan")
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zf:
        count = 0
        for path in sorted(PROJECT_ROOT.rglob("*")):
            if path.is_file():
                try:
                    rel = path.relative_to(PROJECT_ROOT)
                except ValueError:
                    continue
                if rel.parts[0] in EXCLUDE_DIRS:
                    continue
                if path.name in EXCLUDE_FILES:
                    continue
                if path.suffix.lower() == ".zip" or path.name.endswith(".zip"):
                    continue
                zf.write(path, rel)
                count += 1
    msg(f"  Добавлено файлов: {count}", "dim")
    return archive_name


if __name__ == "__main__":
    msg("╔══════════════════════════════════════════╗", "cyan")
    msg("║         PEm08 — Бекап проекта            ║", "cyan")
    msg("╚══════════════════════════════════════════╝", "cyan")

    out = backup_project()
    msg(f"\n  ✅ Бекап создан: {out.name}", "green")
    msg(f"     {out}", "dim")

    backups = get_backups()
    if backups:
        msg("\n  📋 Архивы бекапов (не более 3):", "yellow")
        for i, (path, mtime) in enumerate(backups[:MAX_BACKUPS], 1):
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            size_mb = path.stat().st_size / (1024 * 1024)
            mark = " ← новый" if path == out else ""
            msg(f"     {i}. {path.name}  {dt}  ({size_mb:.2f} МБ){mark}", "magenta")

    if len(backups) > MAX_BACKUPS:
        msg("\n  🗑 Очистка старых бекапов:", "yellow")
        trim_old_backups(backups)

    msg("")
