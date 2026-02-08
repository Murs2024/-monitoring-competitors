# PEm08. Проект: мультимодальное приложение

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

## Как выложить проект в репозиторий (по шагам)

### Вариант А: через Cursor (проще всего)

| Шаг | Действие |
|-----|----------|
| 1 | Убедиться, что **.env** не попадёт в репозиторий: откройте `.gitignore` — там должна быть строка `.env`. |
| 2 | В Cursor откройте **папку проекта** «PEm08. Проект мультимодальное приложение» (File → Open Folder). |
| 3 | Слева на панели нажмите иконку **Source Control** (ветка) или нажмите **Ctrl+Shift+G**. |
| 4 | Вверху нажмите **Publish to GitHub** (или «Опубликовать на GitHub»). |
| 5 | Введите **название репозитория** латиницей, например: `monitoring-competitors` или `PEm08-app`. |
| 6 | Выберите **Private** (приватный) или **Public** (публичный; для сдачи ДЗ обычно просят публичный). |
| 7 | Подтвердите. Cursor создаст репозиторий на вашем GitHub и загрузит туда файлы. Готово. |

После этого откройте в браузере `https://github.com/ВАШ_ЛОГИН/ИМЯ_РЕПОЗИТОРИЯ` — там будет код и README.

---

### Вариант Б: через терминал (Git)

**Шаг 1.** Откройте терминал в папке проекта и инициализируйте репозиторий:

```bash
cd "Лекции\Промтинжениринг\PEm08. Проект мультимодальное приложение"
git init
```

**Шаг 2.** Добавьте все файлы и проверьте список (в списке не должно быть `.env`, `venv/`, `*.exe`):

```bash
git add .
git status
```

Если видите `.env` или `venv` — добавьте их в `.gitignore` и снова `git add .`.

**Шаг 3.** Сделайте первый коммит:

```bash
git commit -m "PEm08: мониторинг конкурентов — мультимодальное приложение"
```

**Шаг 4.** Создайте пустой репозиторий на GitHub:
- Зайдите на **https://github.com** и войдите в аккаунт.
- Нажмите **«+»** → **New repository**.
- **Repository name:** например `monitoring-competitors`.
- **Public** или **Private** — по желанию.
- **Не** ставьте галочки «Add a README» и «Add .gitignore» — у вас уже есть свои.
- Нажмите **Create repository**.

**Шаг 5.** Подключите локальный репозиторий к GitHub и отправьте код (подставьте свой логин и имя репозитория):

```bash
git remote add origin https://github.com/ВАШ_ЛОГИН/monitoring-competitors.git
git branch -M main
git push -u origin main
```

При запросе авторизации: введите логин GitHub и вместо пароля — **Personal Access Token** (GitHub → Settings → Developer settings → Personal access tokens → Generate new token). Или войдите через браузер, если система предложит.

**Готово.** Страница репозитория на GitHub покажет все файлы и README.

---

### Что не должно попасть в репозиторий

Уже добавлено в `.gitignore`: `.env`, `venv/`, `history.json`, `*.exe`, `dist/`, `build/`. Перед `git add .` проверьте: `git status` не должен показывать эти файлы и папки.

---

*ДЗ PEm08: окружение → адаптация моделей → Selenium-парсинг → сборка desktop (PyQt6 + PyInstaller) → публикация на GitHub с README.*
