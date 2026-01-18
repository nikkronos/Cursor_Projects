# Структура репозитория и проекты

## Общая информация

Этот репозиторий содержит несколько проектов с разными статусами коммита в Git.

**GitHub репозиторий:** `nikkronos/TradeTherapyBot`  
**Локальный путь:** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_test`

---

## Проекты

### 1. TradeTherapyBot

**Статус:** ✅ Коммитится в Git  
**Описание:** Telegram-бот для автоматизации управления доступом к закрытому сообществу трейдеров "Trade Therapy".

**Особенности:**
- Коммитится в Git репозиторий
- Автоматический CI/CD деплой через GitHub Actions
- Работает на сервере Timeweb 24/7
- Создан с помощью AI агентов

**Расположение:**
- Локально: `TradeTherapyBot/`
- На сервере: `/opt/tradetherapybot` (предположительно)

**Документы:**
- `ROADMAP_TRADETHERAPYBOT.md` - планы развития
- `DONE_LIST_TRADETHERAPYBOT.md` - выполненные задачи
- `SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `docs/` - база знаний проекта

**Технологии:**
- aiogram / python-telegram-bot
- SQLite
- APScheduler
- GitHub Actions для CI/CD

---

### 2. PastuhiBot

**Статус:** ❌ НЕ коммитится в Git (хранится только локально)  
**Описание:** Telegram-бот для копирования содержимого определенных Telegram каналов (бот-перелив).

**Особенности:**
- **НЕ коммитится в Git** - все изменения хранятся локально
- Боевой бот работает на сервере Timeweb
- Создан с разработчиком (копия с сервера)
- Изменения применяются вручную после тестирования

**Расположение:**
- Локально: `PastuhiBot/`
- На сервере: работает на Timeweb (путь уточнить)

**Документы:**
- `ROADMAP_PASTUHIBOT.md` - планы развития
- `DONE_LIST_PASTUHIBOT.md` - выполненные задачи
- `SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `docs/` - база знаний проекта

**Технологии:**
- aiogram 2.25.1
- Pyrogram 2.0.106 (для юзербота)
- APScheduler
- SQLite

**Важно:** Этот проект исключён из Git через `.gitignore`

---

### 3. ParentChildResearch

**Статус:** ❌ НЕ коммитится в Git (временный исследовательский проект)  
**Описание:** Исследовательский проект для диплома.

**Особенности:**
- **НЕ коммитится в Git** - временный проект
- Исследовательская работа
- Может быть удалён после завершения

**Расположение:**
- Локально: `ParentChildResearch/`

**Документы:**
- `PROJECT_SUMMARY.md` - описание проекта
- `docs/` - документация исследования

**Важно:** Этот проект исключён из Git через `.gitignore`

---

### 4. TestN8N

**Статус:** ❌ НЕ коммитится в Git (тестовый проект)  
**Описание:** Тестовый Telegram-бот для проверки интеграции с N8N.

**Особенности:**
- **НЕ коммитится в Git** - тестовый проект
- Используется для быстрого тестирования N8N интеграции
- Простой бот с базовыми командами
- Отправляет события в N8N webhook

**Расположение:**
- Локально: `TestN8N/`

**Документы:**
- `README.md` - описание проекта
- `QUICK_START.md` - быстрый старт

**Технологии:**
- pyTelegramBotAPI
- N8N webhook интеграция

**Важно:** Этот проект исключён из Git через `.gitignore`

---

## Структура репозитория

```
CURSOR_TEST/
├── .gitignore                  # Исключает ParentChildResearch и PastuhiBot
├── RULES_CURSOR.md            # Правила работы с проектами
├── QUICK_START_AGENT.md       # Быстрый старт для агента
├── COMMIT_CURSOR.md           # Правила коммитов
├── PROJECTS.md                # Этот файл
├── ROAD_MAP_AI.md            # Roadmap AI проектов
├── docs/                      # Общая документация
│   ├── AGENT_PROMPTS.md       # Полная инструкция для агента
│   └── server-timeweb.md      # Документация о сервере
├── TradeTherapyBot/           # ✅ Коммитится
│   ├── ROADMAP_TRADETHERAPYBOT.md
│   ├── DONE_LIST_TRADETHERAPYBOT.md
│   ├── SESSION_SUMMARY_YYYY-MM-DD.md
│   └── docs/
├── PastuhiBot/                # ❌ НЕ коммитится
│   ├── ROADMAP_PASTUHIBOT.md
│   ├── DONE_LIST_PASTUHIBOT.md
│   ├── SESSION_SUMMARY_YYYY-MM-DD.md
│   └── docs/
└── ParentChildResearch/       # ❌ НЕ коммитится
    └── docs/
```

---

## Правила работы с проектами

1. **TradeTherapyBot** - можно коммитить, есть CI/CD
2. **PastuhiBot** - НЕ коммитить, только локально
3. **ParentChildResearch** - НЕ коммитить, временный проект

Подробные правила: `RULES_CURSOR.md`

---

## Сервер Timeweb

- У пользователя есть оплаченный сервер на Timeweb
- На сервере работают: TradeTherapyBot и PastuhiBot
- Подробная документация: `docs/server-timeweb.md`

---

**Последнее обновление:** 2025-12-23

