#!/usr/bin/env python3
"""
Запуск сервера разработки. Выполнять из корня проекта: python run.py
переход к проекту: cd "Лекции\Промтинжениринг\PEm08. Проект мультимодальное приложение"

"""
import uvicorn

from backend.config import settings

if __name__ == "__main__":
    print(f"Сервер слушает на {settings.api_host}:{settings.api_port}")
    print("В браузере откройте: http://127.0.0.1:8000 или http://localhost:8000")
    print("(0.0.0.0 в адресную строку не вводите — это только для сервера)\n")
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
