"""
Создание ярлыка приложения на рабочем столе.
Ярлык запускает Мониторинг_конкурентов.exe (рабочая папка — папка проекта).
Сначала соберите exe: python build_desktop.py
"""
import os
import sys

EXE_NAME = "MonitorCompetitors.exe"


def create_shortcut():
    """Создаёт ярлык на exe на рабочем столе."""
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        exe_file = os.path.join(project_dir, EXE_NAME)
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        # Имя ярлыка в латинице — меньше проблем с кодировкой при сохранении
        shortcut_name = "Monitoring_competitors.lnk"
        shortcut_path = os.path.join(desktop, shortcut_name)

        if not os.path.exists(exe_file):
            print(f"Сначала соберите exe: в папке проекта выполните")
            print(f"  python build_desktop.py")
            print(f"Ожидаемый файл: {exe_file}")
            return False

        def do_create(path):
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(path)
                shortcut.TargetPath = exe_file
                shortcut.WorkingDirectory = project_dir
                shortcut.Description = "Мониторинг конкурентов — AI-ассистент"
                shortcut.save()
                return True
            except ImportError:
                pass
            # Fallback: PowerShell
            import subprocess
            esc = lambda s: s.replace("\\", "\\\\")
            ps = f'$s = New-Object -ComObject WScript.Shell; $l = $s.CreateShortcut("{esc(path)}"); $l.TargetPath = "{esc(exe_file)}"; $l.WorkingDirectory = "{esc(project_dir)}"; $l.Save()'
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=10)
            return r.returncode == 0

        if do_create(shortcut_path):
            print(f"Ярлык на рабочем столе: {shortcut_path}")
            return True
        # Запасной вариант: ярлык в папке проекта
        fallback = os.path.join(project_dir, shortcut_name)
        if do_create(fallback):
            print(f"Ярлык создан в папке проекта: {fallback}")
            print("Скопируйте его на рабочий стол при необходимости.")
            return True
        print("Не удалось создать ярлык. Создайте вручную: ПКМ по exe → Создать ярлык → перетащить на рабочий стол.")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


if __name__ == "__main__":
    ok = create_shortcut()
    if sys.stdin.isatty():
        input("\nНажмите Enter для выхода...")
    sys.exit(0 if ok else 1)
