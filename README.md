
# 🎙️ Голосовой ассистент Oleg

[![CI](https://github.com/OneFreemans/voice-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/OneFreemans/voice-assistant/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://github.com/OneFreemans/voice-assistant/tree/main/tests)
[![Coverage](https://img.shields.io/badge/coverage-77%25-brightgreen.svg)]()

Голосовой ассистент на Python с активацией по слову «Олег». Умеет слушать команды, отвечать голосом, работать с ВК, показывать погоду, курс валют, запускать программы, ставить таймеры, вести заметки, общаться через ИИ и управлять умным домом через Яндекс.

---

## 🎤 Активация и распознавание

Активация по ключевому слову **«Олег»**. Используется нечёткое сопоставление (алгоритм Левенштейна), поэтому ассистент понимает даже с опечатками и разным произношением:

- «ОлеГ», «ОлЕг», «олег»
- «Олеже», «Олежа», «Олежка»
- «Олич», «Олиг»

Порог схожести: **78%** (меняется в `Oleg/utils/fuzzy.py`).

---

## 🚀 Возможности

| Команда | Что делает |
|---|---|
| `Олег, сколько время` | Текущее время |
| `Олег, какой сегодня день` | Дата |
| `Олег, погода` | Погода в Кемерово |
| `Олег, курс доллар` / `евро` | Курс валют |
| `Олег, таймер 5 минут` | Таймер |
| `Олег, расскажи анекдот` | Случайный анекдот |
| `Олег, запусти steam` | Запуск программы |
| `Олег, открой вк` | Открытие сайта |
| `Олег, отправь сообщение Имя Фамилия текст` | Отправка сообщения ВК |
| `Олег, последнее сообщение` | Последнее сообщение ВК |
| `Олег, ответь на сообщение текст` | Ответ на последнее сообщение ВК |
| `Олег, рассчитай стяжку` | Расчёт материалов |
| `Олег, сердце 5 красное` | Сердечки в консоли |
| `Олег, включи свет` / `выключи` | Умный дом (Яндекс) |
| `Олег, добавь заметку ...` | Заметки |
| `Олег, заметки` | Список заметок |
| `Олег, удали заметку 3` | Удаление заметки |
| `Олег, режим собеседника` | AI-собеседник (DeepSeek) |
| `Олег стоп` | Завершение работы |

---

## 🛠️ Установка

### 1. Клонируй репозиторий
```bash
git clone https://github.com/OneFreemans/voice-assistant.git
cd voice-assistant
```
---
### 2. Создай виртуальное окружение
```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```
---
### 3. Установи зависимости
```bash
pip install -r requirements.txt
```
---
### 4. Настрой переменные окружения

Создай файл `.env` в корне проекта:

```env
VK_TOKEN=ваш_токен_вк
MY_USER_ID=ваш_id_вк
DEEPSEEK_API_KEY=ваш_ключ_deepseek
YANDEX_TOKEN=ваш_токен_яндекса
```

Файл `.env` не коммитится — он в `.gitignore`.

---
### 5. Запуск
```bash
python run.py          # консольный режим
python run.py --gui    # графический интерфейс
```

---

## 📁 Структура проекта

```
voice-assistant/
├── run.py                    # точка входа (консоль / --gui)
├── requirements.txt          # основные зависимости
├── requirements-dev.txt      # зависимости для разработки
├── requirements-ci.txt       # зависимости для CI
├── .gitignore
├── .pre-commit-config.yaml
├── pytest.ini
├── README.md
│
├── Oleg/
│   ├── config.py             # настройки (без секретов)
│   ├── secrets.py            # загрузка секретов из .env
│   │
│   ├── core/                 # ядро
│   │   ├── main.py           # запуск, прослушивание команд
│   │   └── voice.py          # озвучивание
│   │
│   ├── commands/             # обработчики команд
│   │   ├── functions.py      # время, погода, курс, таймер, программы
│   │   ├── notes.py          # заметки
│   │   ├── smart_home.py     # умный дом
│   │   └── ai_chat.py        # AI-собеседник
│   │
│   ├── services/             # внешние API
│   │   ├── vk_functions.py   # VK API
│   │   ├── yandex_smart_home.py  # Яндекс.Умный дом
│   │   └── deepseek.py       # DeepSeek API
│   │
│   ├── gui/
│   │   └── tk_gui.py         # GUI на Tkinter
│   │
│   └── utils/                # утилиты
│       ├── fuzzy.py          # нечёткое сопоставление
│       ├── formatters.py     # склонение слов
│       ├── anecdote.py       # анекдоты
│       ├── logger.py         # логирование
│       └── command_parser.py # парсер команд
│
├── tests/                    # тесты
│   └── test_oleg.py
│
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions
```

---

## 🧪 Разработка

### Тесты
```bash
pytest tests/ --cov=Oleg --cov-report=term-missing
```
---
### Pre-commit
```bash
pre-commit install
pre-commit run --all-files
```
---
### CI/CD
При каждом пуше в `main` GitHub Actions запускает тесты. Статус: [![CI](https://github.com/OneFreemans/voice-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/OneFreemans/voice-assistant/actions/workflows/ci.yml)

---

## 🧠 Технологии

| Библиотека | Назначение |
|---|---|
| `pyttsx3` | Синтез речи |
| `SpeechRecognition` | Распознавание речи |
| `requests` | HTTP-запросы |
| `vk_api` | Работа с VK API |
| `python-dotenv` | Загрузка .env |
| `pytest` | Тестирование |
| `ruff` | Линтер/форматтер |
| `pre-commit` | Хуки перед коммитом |

---

## 📄 Лицензия

MIT

---

## ✍️ Автор

**OneFreemans** — [GitHub](https://github.com/OneFreemans)
