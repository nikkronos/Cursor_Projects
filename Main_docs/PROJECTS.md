# Структура репозитория и проекты

## Общая информация

Этот репозиторий содержит несколько проектов с разными статусами коммита в Git.

**GitHub репозитории:**
1. `nikkronos/TradeTherapyBot` - основной репозиторий для TradeTherapyBot
2. `nikkronos/vpnservice` - отдельный репозиторий для VPN
3. `nikkronos/kopiya-iksuyemsya` - отдельный репозиторий для проекта "Копия иксуюемся"
4. `nikkronos/Cursor_Projectcs` — репозиторий на GitHub для всех проектов скопом (кроме env_vars); имя с окончанием **`cs`**; локально папка часто `Cursor_Projects`

**Локальный путь:** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_Projects`

**Важно:** Основного репозитория нет. При создании нового проекта агент должен спросить: создать новый репозиторий или коммитить в существующий (например, `nikkronos/Cursor_Projectcs`)?

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
- **Прод с 2026-04-10:** боевые процессы (внутренние имена **`hamster26_*`**, **`hamster93_*`**) перенесены на **Fornex** из‑за недоступности Telegram API с Timeweb; см. `Projects/PastuhiBot/docs/SERVER_MIGRATION_FORNEX_2026-04-10.md` и кратко для разработчика: `Projects/PastuhiBot/DEV_HANDOFF_FORNEX_2026-04-10.md`
- Создан с разработчиком (копия с сервера)
- Изменения применяются вручную после тестирования

**Расположение:**
- Локально: `Projects/PastuhiBot/`
- На сервере (прод): **Fornex** — каталоги `/home/hamster26/`, `/home/hamster93_bot/`, `/home/hamster93_userbot/`, `/home/hamster93_feedbackbot/`; systemd `hamster*.service`

**Документы:**
- `Projects/PastuhiBot/ROADMAP_PASTUHIBOT.md` - планы развития
- `Projects/PastuhiBot/DONE_LIST_PASTUHIBOT.md` - выполненные задачи
- `Projects/PastuhiBot/SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `Projects/PastuhiBot/docs/` - база знаний проекта
- `Projects/PastuhiBot/docs/SERVER_MIGRATION_FORNEX_2026-04-10.md` — миграция на Fornex (технически)
- `Projects/PastuhiBot/DEV_HANDOFF_FORNEX_2026-04-10.md` — передача разработчику

**Сервер:** Fornex (прод с 2026-04-10); Timeweb — выключенный резерв для этого стека

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
- **Прод с 2026-04-10:** основной процесс перенесён на **Fornex** (Timeweb перестал достучаться до `api.telegram.org`; см. `Main_docs/TELEGRAM_MIGRATION_TIMWEB_FORNEX_2026-04-10.md`).
- На Timeweb копия в `/opt/kopiya-iksuyemsya` может оставаться как резерв; systemd `kopiya-iksuyemsya.service` на Timeweb **отключён**.
- Создан с помощью AI агентов

**Расположение:**
- Локально: папка `Projects/xxx/` (свой `.git`, свой remote)
- На сервере (прод): **Fornex** — `/opt/kopiya-iksuyemsya`, venv, `systemctl enable --now kopiya-iksuyemsya.service`

**Документы:**
- `Projects/xxx/docs/ДВА_РЕПОЗИТОРИЯ_И_ДЕПЛОЙ.md` — пошаговое разделение репозиториев и деплой
- `Main_docs/TELEGRAM_MIGRATION_TIMWEB_FORNEX_2026-04-10.md` — инцидент блокировки Telegram с Timeweb и миграция на Fornex
- В папке `Projects/xxx/`: README, ROADMAP, DONE_LIST, TESTING_GUIDE и т.д.

**Сервер:** Fornex (прод с 2026-04-10); Timeweb — исторически, не активный прод для этого бота

**Технологии:**
- aiogram (бот управления)
- Pyrogram 2.x (юзербот)
- SQLite

**Важно:** Коммиты для этого проекта делаются **в папке xxx**; пуш — в репозиторий **kopiya-iksuyemsya**, не в TradeTherapyBot.

---

### 6. Damir

**Статус:** ✅ Код в отдельном репозитории [nikkronos/Futures_auction](https://github.com/nikkronos/Futures_auction); **прод на Timeweb выключен** с 2026-04-04 (`futures_auction.service`: `stop` + `disable`).  
**Описание:** Виджет для отображения данных по фьючерсам (T-Invest API): таблица (название актива, цена закрытия/открытия, изменение %), настройки с фильтрами по категориям.

**Особенности:**
- **Отдельный Git-репозиторий:** https://github.com/nikkronos/Futures_auction
- Интеграция с T-Invest REST API ([developer.tbank.ru/invest](https://developer.tbank.ru/invest/intro/intro/))
- Деплой на TimeWeb: `/opt/futures_auction`, systemd `futures_auction.service` (при необходимости снова: `enable` + `start`)
- Пользователи: ~10 человек (исторически)

**Расположение:**
- Локально: `Projects/Damir/` (в Cursor_Projects; по правилам репозитория может не коммититься в корень монорепо)
- На сервере: `/opt/futures_auction`

**Документы:**
- `Projects/Damir/TRANSFER_OTHER_PERSON.md` — инструкция для передачи человеку / агенту (есть также `.html`, `.pdf`)
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
- Локально: папка `Projects/VPN/` (свой `.git`, отдельный remote от корня `Cursor_Projects`)
- **Полный путь (Windows, этот ПК):** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_Projects\Projects\VPN`
- **Репозиторий GitHub:** https://github.com/nikkronos/vpnservice
- На сервере: **Fornex** — прод для **VPN Telegram-бота**: `/opt/vpnservice`, `venv`, `systemctl enable --now vpn-bot.service` (с 2026-04-10; на Timeweb `vpn-bot.service` отключён). Подробности: `Main_docs/TELEGRAM_MIGRATION_TIMWEB_FORNEX_2026-04-10.md`.
- Веб-панель и recovery: **прод на Fornex** — `http://185.21.8.91:5001/` и `http://185.21.8.91:5001/recovery` (`VPN_RECOVERY_URL` в `env_vars.txt`); на Timeweb панель **выключена** (2026-04-11). См. `Projects/VPN/docs/deployment.md`, `Projects/VPN/docs/vpn-web-migration-fornex-plan.md`.
- **`/proxy_rotate`:** починено (MTProxy на Fornex, порт **8444**, проброс `MTPROXY_*` в subprocess) — см. `Projects/VPN/SESSION_SUMMARY_2026-04-10.md`.

**Важно:** Коммиты для этого проекта делаются **в папке Projects/VPN**; пуш — в репозиторий **vpnservice**, не в TradeTherapyBot.

**Документы:**
- `Projects/VPN/ROADMAP_VPN.md` - планы развития
- `Projects/VPN/DONE_LIST_VPN.md` - выполненные задачи
- `Projects/VPN/SESSION_SUMMARY_YYYY-MM-DD.md` - последняя сессия
- `Projects/VPN/docs/` - база знаний проекта
- `Main_docs/TELEGRAM_MIGRATION_TIMWEB_FORNEX_2026-04-10.md` — миграция бота на Fornex и блокировка Timeweb

**Сервер:** Fornex — прод **бот** и **веб-панель** с 2026-04-11 (`185.21.8.91:5001`); main (WireGuard) остаётся на Timeweb.

---

### 8. Limits

**Статус:** ⚙️ В разработке, локально и на Timeweb  
**Описание:** Виджет для выставления пачки лимитных заявок через API Т‑Инвестиции: выбор инструмента (акции и фьючерсы), ввод суммы в рублях для акций или количества контрактов для фьючерсов, шаг в процентах и кнопки «Покупка ниже / Продажа выше».

**Особенности:**
- Блок «Акции» — работает по сумме в рублях (как в десктоп‑версии).
- Блок «Фьючерсы» — работает по количеству контрактов (с оценкой только по контрактам, без пересчёта в ₽).
- Интеграция с T‑Invest REST API, один счёт, простая панель для личного использования.

**Расположение:**
- Локально: `Projects/Limits/`
- На сервере Timeweb: `/opt/Limits`, systemd‑сервис `limits.service`

**URL:**
- **Damir (таблица инструментов):** `http://81.200.146.32:5000/` — **с 2026-04-04 недоступен** (сервис остановлен; снаружи ожидаемо `ERR_CONNECTION_REFUSED`), пока снова не включат `futures_auction`
- **VPN мониторинг (панель vpnservice):** `http://185.21.8.91:5001/` (Fornex; Timeweb-панель отключена 2026-04-11)
- **Limits (лимитные заявки):** `http://81.200.146.32:<PORT>/` — порт задаётся переменной `PORT` в `/opt/Limits/env_vars.txt` (рекомендуется свободный, например `5002`).

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

**Важно:** При создании нового проекта агент должен спросить пользователя: создать новый репозиторий или коммитить в `nikkronos/Cursor_Projectcs`?

Подробные правила: `Main_docs/RULES_CURSOR.md`

---

## Серверы

У пользователя есть **два сервера**:

### Сервер TimeWeb
- Оплаченный сервер на TimeWeb
- На сервере работают / развёрнуто:
  - TradeTherapyBot — **выключен** с 2026-02-21 (см. `Main_docs/RULES_CURSOR.md`)
  - PastuhiBot (24/7)
  - Damir (Futures_auction) — **выключен** с 2026-04-04 (не 24/7)
  - Копия иксуюемся (xxx) (24/7)

### Сервер Fornex
- Дополнительный сервер на Fornex
- На сервере работают:
  - VPN (и другие проекты при необходимости)

Подробная документация: `docs/server-timeweb.md`

---

**Последнее обновление:** 2026-04-04

