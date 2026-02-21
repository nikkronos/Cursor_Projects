# Структура репозитория и проекты

## Общая информация

Этот репозиторий содержит несколько проектов с разными статусами коммита в Git.

**GitHub репозитории:**
1. `nikkronos/TradeTherapyBot` - основной репозиторий для TradeTherapyBot
2. `nikkronos/vpnservice` - отдельный репозиторий для VPN
3. `nikkronos/kopiya-iksuyemsya` - отдельный репозиторий для проекта "Копия иксуюемся"
4. `nikkronos/Cursor_Projects` - новый репозиторий для всех проектов скопом (кроме env_vars)

**Локальный путь:** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_Projects`

**Важно:** Основного репозитория нет. При создании нового проекта агент должен спросить: создать новый репозиторий или коммитить в существующий (например, Cursor_Projects)?

---

## Проекты

### 1. TradeTherapyBot

**Статус:** ⏸️ **Неактуален** (бот выключен на сервере с 2026-02-21). Репозиторий по-прежнему коммитится в Git.  
**Описание:** Telegram-бот для автоматизации управления доступом к закрытому сообществу трейдеров "Trade Therapy".

**Особенности:**
- Коммитится в Git репозиторий
- Автоматический CI/CD деплой через GitHub Actions (при включении бота)
- **Бот остановлен и отключён от автозапуска** на Timeweb (`systemctl stop` + `disable`)
- Создан с помощью AI агентов

**Расположение:**
- Локально: `Projects/TradeTherapyBot/`
- На сервере: `/opt/tradetherapybot` (предположительно)

**Документы:**
- `Projects/TradeTherapyBot/ROADMAP_TRADETHERAPYBOT.md` - планы развития
- `Projects/TradeTherapyBot/DONE_LIST_TRADETHERAPYBOT.md` - выполненные задачи
- `Projects/TradeTherapyBot/SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `Projects/TradeTherapyBot/docs/` - база знаний проекта

**Сервер:** TimeWeb

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
- Локально: `Projects/PastuhiBot/`
- На сервере: работает на TimeWeb (путь уточнить)

**Документы:**
- `Projects/PastuhiBot/ROADMAP_PASTUHIBOT.md` - планы развития
- `Projects/PastuhiBot/DONE_LIST_PASTUHIBOT.md` - выполненные задачи
- `Projects/PastuhiBot/SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `Projects/PastuhiBot/docs/` - база знаний проекта

**Сервер:** TimeWeb

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
- Локально: `Projects/ParentChildResearch/`

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
- Локально: `Projects/TestN8N/`

**Документы:**
- `README.md` - описание проекта
- `QUICK_START.md` - быстрый старт

**Технологии:**
- pyTelegramBotAPI
- N8N webhook интеграция

**Важно:** Этот проект исключён из Git через `.gitignore`

---

### 5. Копия иксуюемся

**Статус:** ✅ Отдельный репозиторий (nikkronos/kopiya-iksuyemsya)  
**Описание:** Telegram-бот для копирования информации из одного Telegram-канала в другой (бот-перелив).

**Особенности:**
- **Отдельный Git-репозиторий** — не входит в TradeTherapyBot; коммиты и пуш из папки `Projects/xxx/` идут в **nikkronos/kopiya-iksuyemsya**
- Создан по аналогии с PastuhiBot
- Работает на сервере TimeWeb (отдельная папка и systemd-сервис)
- Создан с помощью AI агентов

**Расположение:**
- Локально: папка `Projects/xxx/` (свой `.git`, свой remote)
- На сервере: например `/opt/kopiya-iksuyemsya` (отдельный клон репозитория kopiya-iksuyemsya)

**Документы:**
- `Projects/xxx/docs/ДВА_РЕПОЗИТОРИЯ_И_ДЕПЛОЙ.md` — пошаговое разделение репозиториев и деплой
- В папке `Projects/xxx/`: README, ROADMAP, DONE_LIST, TESTING_GUIDE и т.д.

**Сервер:** TimeWeb

**Технологии:**
- aiogram (бот управления)
- Pyrogram 2.x (юзербот)
- SQLite

**Важно:** Коммиты для этого проекта делаются **в папке xxx**; пуш — в репозиторий **kopiya-iksuyemsya**, не в TradeTherapyBot.

---

### 6. Damir

**Статус:** ✅ Будет отдельный репозиторий (nikkronos/damir или аналог)  
**Описание:** Виджет для отображения данных по фьючерсам (T-Invest API): таблица (название актива, цена закрытия/открытия, изменение %), настройки с фильтрами по категориям.

**Особенности:**
- **Планируется отдельный Git-репозиторий** — аналогично VPN и xxx
- Интеграция с T-Invest REST API ([developer.tbank.ru/invest](https://developer.tbank.ru/invest/intro/intro/))
- Деплой на сервер TimeWeb (24/7)
- Пользователи: ~10 человек

**Расположение:**
- Локально: `Projects/Damir/` (временно в .gitignore, потом отдельный репозиторий)
- На сервере: `/opt/damir` (планируется)

**Документы:**
- `Projects/Damir/ROADMAP_DAMIR.md` — планы
- `Projects/Damir/DONE_LIST_DAMIR.md` — выполненные задачи
- `Projects/Damir/SESSION_SUMMARY_YYYY-MM-DD.md` — последняя сессия
- `Projects/Damir/docs/` — база знаний, спеки

**Сервер:** TimeWeb

**Технологии:**
- T-Invest REST API (SDK сломан, используем requests)
- Flask (бэкенд), HTML/JS (фронт)

**Важно:** Пока в `.gitignore`; после создания репозитория — вынести в отдельную папку со своим `.git`

---

### 7. VPN

**Статус:** ✅ Отдельный репозиторий (nikkronos/vpnservice)  
**Описание:** Сервис VPN/Proxy для безопасного туннелирования трафика с упором на высокую скорость, низкий пинг и управление через Telegram-бота.

**Особенности:**
- **Отдельный Git-репозиторий** — не входит в TradeTherapyBot; коммиты и пуш из папки `Projects/VPN/` идут в **nikkronos/vpnservice**
- Коммитится в Git (без секретов, по общим правилам безопасности)
- Разворачивается на отдельных VPS-серверах (Fornex и другие провайдеры)
- Основная аудитория: владелец, друзья, коллеги; в перспективе — коммерческое использование

**Расположение:**
- Локально: папка `Projects/VPN/` (свой `.git`, свой remote: https://github.com/nikkronos/vpnservice.git)
- На сервере: отдельная папка на сервере Fornex (будет зафиксирована в `Projects/VPN/docs/deployment.md`)

**Важно:** Коммиты для этого проекта делаются **в папке Projects/VPN**; пуш — в репозиторий **vpnservice**, не в TradeTherapyBot.

**Документы:**
- `Projects/VPN/ROADMAP_VPN.md` - планы развития
- `Projects/VPN/DONE_LIST_VPN.md` - выполненные задачи
- `Projects/VPN/SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `Projects/VPN/docs/` - база знаний проекта

**Сервер:** Fornex (и другие VPS)

---

## Структура репозитория

```
Cursor_Projects/
├── Main_docs/                 # Основные документы
│   ├── RULES_CURSOR.md        # Правила работы с проектами
│   ├── QUICK_START_AGENT.md   # Быстрый старт для агента
│   ├── COMMIT_CURSOR.md       # Правила коммитов
│   ├── PROJECTS.md            # Этот файл
│   ├── ROAD_MAP_AI.md         # Roadmap AI проектов
│   ├── AGENT_PROMPTS.md       # Полная инструкция для агента
│   └── env_vars.txt           # Секреты (НЕ коммитится!)
├── Projects/                  # Все проекты
│   ├── TradeTherapyBot/       # ✅ Коммитится в nikkronos/TradeTherapyBot
│   │   ├── ROADMAP_TRADETHERAPYBOT.md
│   │   ├── DONE_LIST_TRADETHERAPYBOT.md
│   │   ├── SESSION_SUMMARY_YYYY-MM-DD.md
│   │   └── docs/
│   ├── PastuhiBot/            # ❌ НЕ коммитится
│   ├── Damir/                 # ❌ НЕ коммитится (виджет Т-Инвестиции)
│   ├── xxx/                   # ✅ Коммитится в nikkronos/kopiya-iksuyemsya
│   ├── VPN/                   # ✅ Коммитится в nikkronos/vpnservice
│   ├── HH/                    # ❌ НЕ коммитится (HeadHunter)
│   ├── Chess/                 # ❌ НЕ коммитится
│   ├── n8n/                   # ❌ НЕ коммитится
│   ├── TestN8N/               # ❌ НЕ коммитится
│   └── ParentChildResearch/   # ❌ НЕ коммитится
├── docs/                      # Общая документация
│   └── server-timeweb.md      # Документация о серверах
└── .gitignore                 # Игнорируемые файлы
```

---

## Правила работы с проектами

1. **TradeTherapyBot** - коммитится в `nikkronos/TradeTherapyBot`, есть CI/CD
2. **Копия иксуюемся (Projects/xxx/)** - коммитится в `nikkronos/kopiya-iksuyemsya`
3. **VPN (Projects/VPN/)** - коммитится в `nikkronos/vpnservice`
4. **PastuhiBot** - НЕ коммитить, только локально
5. **Damir** - будет отдельный репозиторий (как VPN/xxx)
6. **HH, Chess, n8n, TestN8N** - НЕ коммитить, только локально
7. **ParentChildResearch** - НЕ коммитить, временный проект

**Важно:** При создании нового проекта агент должен спросить пользователя: создать новый репозиторий или коммитить в `nikkronos/Cursor_Projects`?

Подробные правила: `Main_docs/RULES_CURSOR.md`

---

## Серверы

У пользователя есть **два сервера**:

### Сервер TimeWeb
- Оплаченный сервер на TimeWeb
- На сервере работают:
  - TradeTherapyBot (24/7)
  - PastuhiBot (24/7)
  - Damir (24/7)
  - Копия иксуюемся (xxx) (24/7)

### Сервер Fornex
- Дополнительный сервер на Fornex
- На сервере работают:
  - VPN (и другие проекты при необходимости)

Подробная документация: `docs/server-timeweb.md`

---

**Последнее обновление:** 2026-02-17

