#!/usr/bin/env python3
"""
Десктоп-приложение: окно с веб-интерфейсом, сервер запускается в фоне.
Запуск из папки PEm08: python desktop_app.py
"""
import os
import sys
import threading
import time
from pathlib import Path

# Корень проекта: при сборке exe — папка с exe, иначе — папка с desktop_app.py
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
    # Не добавляем папку exe в sys.path — backend и fastapi грузятся из упакованного exe
else:
    PROJECT_ROOT = Path(__file__).resolve().parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)  # чтобы load_dotenv() и history находили .env и history.json рядом с exe

# Порты и хост для десктопа — только localhost
DESKTOP_HOST = "127.0.0.1"
DESKTOP_PORT = 8000


def run_server(port: int):
    """Запуск FastAPI в потоке (без reload)."""
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=DESKTOP_HOST,
        port=port,
        reload=False,
    )


def wait_for_server(port: int, timeout: float = 15.0) -> bool:
    """Ждём, пока сервер ответит на /health."""
    try:
        import urllib.request
        url = f"http://{DESKTOP_HOST}:{port}/health"
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            try:
                with urllib.request.urlopen(url, timeout=1) as r:
                    if r.status == 200:
                        return True
            except Exception:
                time.sleep(0.3)
        return False
    except Exception:
        return False


def main():
    from backend.config import settings
    port = getattr(settings, "api_port", DESKTOP_PORT)

    # Запуск сервера в фоновом потоке
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(port):
        print("Сервер не запустился за 15 сек. Проверьте порт и .env")
        sys.exit(1)

    # PyQt6: окно с WebEngine
    try:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        print("Установите зависимости десктопа: pip install -r requirements-desktop.txt")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Мониторинг конкурентов")

    window = QMainWindow()
    window.setWindowTitle("Мониторинг конкурентов | AI Ассистент")
    window.setMinimumSize(900, 700)
    window.resize(1000, 750)

    browser = QWebEngineView()
    browser.setUrl(QUrl(f"http://{DESKTOP_HOST}:{port}/"))
    window.setCentralWidget(browser)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
