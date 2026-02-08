# Мониторинг конкурентов — мультимодальное приложение

Веб-приложение для мониторинга конкурентов: анализ текста (DeepSeek), изображений (OpenAI), парсинг сайтов (в т.ч. КонсультантПлюс). Результаты сохраняются в `history.json`. Доступны веб-интерфейс и десктоп-версия (exe для Windows).

---

## Запуск

1. Откройте терминал в папке проекта.
2. Установите зависимости (один раз): `pip install -r requirements.txt`
3. Создайте `.env` из `.env.example` и укажите **DEEPSEEK_API_KEY** и **OPENAI_API_KEY**.
4. Запустите сервер: `python run.py`
5. Откройте в браузере: **http://127.0.0.1:8000** или **http://localhost:8000**

Доступны блоки «Анализ текста», «Анализ изображения», «Парсинг сайта», вкладка «История».

### Ошибка `ModuleNotFoundError: No module named 'fastapi'`

Установите зависимости в том окружении, из которого запускаете:
```bash
pip install -r requirements.txt
```

---

## Переменные окружения (.env)

Создайте файл `.env` на основе `.env.example`. **Не загружайте `.env` в репозиторий** — в нём хранятся ключи API.

| Переменная | Назначение |
|------------|------------|
| `OPENAI_API_KEY` | Ключ OpenAI (анализ изображений) |
| `OPENAI_VISION_MODEL` | Модель для анализа изображений (по умолчанию gpt-4o-mini) |
| `DEEPSEEK_API_KEY` | Ключ DeepSeek (анализ текста и парсинга) |
| `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` | Опционально (по умолчанию api.deepseek.com, deepseek-chat) |
| `API_HOST`, `API_PORT` | Хост и порт сервера (по умолчанию 0.0.0.0, 8000) |
| `HISTORY_FILE`, `MAX_HISTORY_ITEMS` | Файл истории и лимит записей |
| `USE_SELENIUM` | `true` — парсинг через Selenium (для JS-страниц) |
| `PARSER_SELENIUM_WAIT` | Секунды ожидания после загрузки страницы |

---

## Модели и функции

- **DeepSeek** — анализ текста и распарсенных страниц (вкладки «Текст», «Парсинг»).
- **OpenAI** — анализ изображений (вкладка «Изображение»).

**API:**  
`POST /analyze_text`, `POST /analyze_image`, `POST /parse_demo`, `GET /history`, `DELETE /history`, `GET /health`.

**Парсинг:** по умолчанию используется HTTP + BeautifulSoup. Для страниц с JavaScript (например, КонсультантПлюс) в `.env` укажите `USE_SELENIUM=true`. Требуется Chrome; драйвер устанавливается через `webdriver-manager`.

**Тип страницы:** модель определяет автоматически — новости/законодательство (поля «Что нового», «На что обратить внимание», «Ключевые темы») или лендинг/конкуренты (сильные и слабые стороны, рекомендации). Краткое резюме формируется в обоих случаях.

---

## Структура проекта

```
проект/
├── backend/
│   ├── config.py           # Настройки из .env
│   ├── main.py             # FastAPI: эндпоинты, раздача frontend
│   ├── models/schemas.py   # Pydantic-модели
│   └── services/
│       ├── openai_service.py   # Анализ текста/изображений/парсинга (DeepSeek + OpenAI)
│       ├── parser_service.py   # Парсинг URL (HTTP или Selenium)
│       └── history_service.py  # История в history.json
├── frontend/
│   ├── index.html, styles.css, app.js, favicon.svg
├── data/                   # Папка для данных (PDF, скриншоты)
├── run.py                  # Запуск сервера: uvicorn backend.main:app
├── desktop_app.py          # Десктоп: PyQt6 + встроенный браузер, сервер в потоке
├── desktop.spec            # Спека PyInstaller
├── build_desktop.py        # Сборка exe и копирование в папку проекта
├── create_desktop_shortcut.py  # Ярлык на рабочем столе (на exe)
├── Собрать_exe_и_ярлык.bat    # Установка зависимостей + сборка exe + ярлык
├── backup_project.py       # Бекап в backups/ (ZIP, не более 3, без .env)
├── requirements.txt
├── requirements-desktop.txt   # PyQt6, PyInstaller
├── .env.example
└── README.md
```

---

## Бекап

```bash
python backup_project.py
```

Скрипт создаёт ZIP-архив в папке **backups/** (хранятся не более 3 последних; старые удаляются автоматически). В архив не включаются: venv, __pycache__, .env, папка backups.

---

## Десктоп и exe (запуск с рабочего стола)

**Вариант 1 — только окно (без exe):**  
`pip install -r requirements-desktop.txt`, затем `python desktop_app.py`. Откроется окно с тем же интерфейсом.

**Вариант 2 — exe и ярлык на рабочем столе:**

1. В папке проекта запустите **Собрать_exe_и_ярлык.bat**. Скрипт установит зависимости (при необходимости), соберёт **MonitorCompetitors.exe** и создаст ярлык на рабочем столе.
2. Запуск: двойной щелчок по ярлыку. Файл **.env** должен находиться рядом с exe (backend и frontend упакованы в exe).

Сборка вручную:
```bash
pip install -r requirements-desktop.txt
python build_desktop.py
python create_desktop_shortcut.py
```

---

## Документация API

После запуска сервера документация доступна по адресам:  
**http://127.0.0.1:8000/docs** (Swagger), **http://127.0.0.1:8000/redoc** (ReDoc).

---

## Репозиторий

[https://github.com/Murs2024/-monitoring-competitors](https://github.com/Murs2024/-monitoring-competitors)

Файлы с секретами и артефакты сборки исключены из репозитория (см. `.gitignore`): `.env`, `venv/`, `history.json`, `dist/`, `build/`, `*.exe`.
