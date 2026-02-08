# Проект: мультимодальное приложение

AI-ассистент для мониторинга конкурентов: анализ текста (DeepSeek), изображений (OpenAI), парсинг сайтов (в т.ч. КонсультантПлюс). История в `history.json`. Веб-интерфейс и десктоп (exe для Windows).

---

## Запуск (как в лекции)

1. Терминал в папке проекта:
   ```bash
   cd "Лекции\Промтинжениринг\PEm08. Проект мультимодальное приложение"
   ```
2. Зависимости (один раз): `pip install -r requirements.txt`
3. Ключи: скопируйте `.env.example` в `.env`, укажите **DEEPSEEK_API_KEY** и **OPENAI_API_KEY**.
4. Запуск сервера: `python run.py`
5. В браузере: **http://127.0.0.1:8000** или **http://localhost:8000**

Доступны блоки «Анализ текста», «Анализ изображения», «Парсинг сайта», вкладка «История».

### Ошибка `ModuleNotFoundError: No module named 'fastapi'`

Установите зависимости в том окружении, из которого запускаете:
```bash
pip install -r requirements.txt
```

---

## Переменные окружения (.env)

Создайте `.env` из `.env.example`. **Не загружайте `.env` в репозиторий** — в нём ключи API.

| Переменная | Назначение |
|------------|------------|
| `OPENAI_API_KEY` | Ключ OpenAI (анализ изображений) |
| `OPENAI_VISION_MODEL` | Модель для картинок (по умолчанию gpt-4o-mini) |
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

**Парсинг:** по умолчанию HTTP + BeautifulSoup. Для страниц с JavaScript (например КонсультантПлюс) в `.env` задайте `USE_SELENIUM=true`. Нужен Chrome; драйвер подтягивается через `webdriver-manager`.

**Тип страницы:** модель определяет сама — новости/законодательство (поля «Что нового», «На что обратить внимание», «Ключевые темы») или лендинг/конкуренты (сильные/слабые стороны, рекомендации). Резюме всегда.

---

## Структура проекта

```
PEm08. Проект мультимодальное приложение/
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
├── data/                   # Папка для PDF/скриншотов конкурентов (ДЗ)
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

Создаётся ZIP в папке **backups/** (не более 3 архивов; старые удаляются). В архив не попадают: venv, __pycache__, .env, папка backups.

---

## Десктоп и exe (запуск с рабочего стола)

**Вариант 1 — только окно (без exe):**  
`pip install -r requirements-desktop.txt`, затем `python desktop_app.py`. Откроется окно с тем же интерфейсом.

**Вариант 2 — exe и ярлык на рабочем столе:**

1. В папке проекта дважды щёлкните **Собрать_exe_и_ярлык.bat**.  
   Скрипт при необходимости установит зависимости, соберёт **MonitorCompetitors.exe** и создаст на рабочем столе ярлык **Monitoring_competitors**.
2. Запуск: двойной клик по ярлыку. Рядом с exe должен лежать только **.env** (папки backend/frontend упакованы в exe).

Вручную:
```bash
pip install -r requirements-desktop.txt
python build_desktop.py
python create_desktop_shortcut.py
```


---

## Документация API

После запуска сервера:  
**http://127.0.0.1:8000/docs** (Swagger), **http://127.0.0.1:8000/redoc** (ReDoc).

---

## Репозиторий

[https://github.com/Murs2024/-monitoring-competitors](https://github.com/Murs2024/-monitoring-competitors)

Секреты и артефакты сборки не попадают в репозиторий: в `.gitignore` указаны `.env`, `venv/`, `history.json`, `dist/`, `build/`, `*.exe`.
