# Миграция Telegram-сервисов с Timeweb на Fornex (апрель 2026)

**Дата инцидента / работ:** 2026-04-10  
**Контекст:** блокировка/фильтрация доступа к инфраструктуре Telegram с IP Timeweb; с Fornex исходящий доступ к Telegram сохранился.

---

## Симптомы

- С **Timeweb** перестали работать боты и юзерботы, завязанные на Telegram: **Копия иксуюемся** (`kopiya-iksuyemsya`), **VPN Telegram-бот**, сторонний **PastuhiBot** на том же хосте.
- С клиента в РФ: Telegram открывается только через VPN; «прокси для клиента» перестал помогать — типичная картина ограничений на стороне оператора/РКН, **отдельно** от серверной проблемы.
- Перезагрузка VPS Timeweb не помогла.

---

## Диагностика (кратко)

На **Timeweb** (`3167915-db15242`):

- `curl -4 https://api.telegram.org/` — таймаут, `HTTP 000`.
- IPv4 и IPv6 к `api.telegram.org:443` — недоступны.
- В логах: Pyrogram `Connection timed out`, aiogram `Request timeout`, pyTelegramBotAPI `No route to host` / `ConnectionError` на `api.telegram.org`.

На **Fornex** (`284854`, IP для SSH в работе: `185.21.8.91`):

- `curl https://api.telegram.org/` — ответ за доли секунды (например `HTTP 302`).
- Вывод: **проблема не в коде**, а в **достижимости Telegram с сети Timeweb**.

---

## Что пробовали и не оставили в проде

- **SSH SOCKS-туннель** Timeweb → Fornex (`ssh -D 127.0.0.1:10805`, затем `autossh`, unit `fornex-telegram-socks.service`).
- Проверка: `curl --proxy socks5h://127.0.0.1:10805 https://api.telegram.org/` — успех.
- Решение: **не внедряли прокси в код**; выбрали **полный перенос процессов на Fornex** (проще в эксплуатации).

На Timeweb после миграции:

- `systemctl disable --now fornex-telegram-socks.service`

---

## Итоговая архитектура (после миграции)

| Сервис | Где работает | Путь / unit |
|--------|----------------|-------------|
| **Копия иксуюемся** (xxx) | **Fornex** | `/opt/kopiya-iksuyemsya`, `kopiya-iksuyemsya.service` |
| **VPN Telegram-бот** | **Fornex** | `/opt/vpnservice`, `vpn-bot.service`, `ExecStart`: `venv/bin/python -m bot.main` |
| **Pastuhi / hamster-стек** (5 процессов) | **Fornex** | `/home/hamster26/...`, `/home/hamster93_*`, unit’ы `hamster26_bot`, `hamster26_userbot`, `hamster93_bot`, `hamster93_userbot`, `hamster93_feedbackbot` — подробно: `Projects/PastuhiBot/docs/SERVER_MIGRATION_FORNEX_2026-04-10.md` |

На **Timeweb** для этих сервисов:

- `kopiya-iksuyemsya.service` — **disabled**, процесс не запускается.
- `vpn-bot.service` — **disabled**, процесс не запускается.
- Все **`hamster*.service`** — **disabled**, процесс не запускается.

Опционально: каталоги `/opt/kopiya-iksuyemsya` и `/opt/vpnservice` на Timeweb могут остаться как резервная копия; имеет смысл не путать их с «активным» продом. Аналогично каталоги `/home/hamster*` на Timeweb — только резерв.

---

## Действия на Fornex (обобщённо)

### Общие шаги

1. Установить `python3-venv` (и при необходимости `python3-pip`), если `python3 -m venv` ругается на `ensurepip`.
2. Распаковать архив с Timeweb в `/opt/...`.
3. Пересоздать venv: `rm -rf venv && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt`.
4. Проверка вручную (`./venv/bin/python main.py` или `python -m bot.main`).
5. systemd unit с `WorkingDirectory`, `ExecStart` на **venv**, `systemctl enable --now`.

### Копия иксуюемся

- Дополнительно: `pip install tgcrypto` (ускорение Pyrogram; в логе: `Using TgCrypto`).
- В логах ожидаются: Pyrogram `Connected! Production DC...`, aiogram `Run polling`.

### VPN-бот

- Зависимости из корневого `requirements.txt` (в т.ч. `pyTelegramBotAPI`).
- После переноса: стабильный `active (running)` без ошибок на `api.telegram.org`.

---

## Текущий статус после миграции (на момент фиксации)

- **xxx (пересылка):** работает на Fornex.
- **VPN-бот:** отвечает на команды на Fornex.
- **hamster / Pastuhi-стек (5 сервисов):** работает на Fornex; детали и нюансы Python/venv/session — `Projects/PastuhiBot/docs/SERVER_MIGRATION_FORNEX_2026-04-10.md`.
- **Команда `proxy rotate`:** **не работает** — отложена на отдельный разбор (вероятная причина: логика ротации завязана на хост/ Docker там, где раньше жил бот или MTProxy; после переноса только бота пути и окружение разъехались). Исправление не выполнялось в этой сессии.
- Веб-восстановление VPN: [http://81.200.146.32:5001/recovery](http://81.200.146.32:5001/recovery) — **открывается** (панель/recovery по-прежнему доступна с указанного IP).

---

## Риски и последствия

- **Нагрузка и стоимость:** два активных процесса на Fornex (xxx + vpn-bot) — учитывать лимиты VPS и биллинг.
- **Единая точка отказа:** если на Fornex появятся ограничения к Telegram, пострадают оба сервиса — иметь план B (другой регион/VPS).
- **Секреты:** в логах Timeweb ранее попадали URL с токеном бота; при работе с журналами не копировать в чаты; при компрометации — ротация через @BotFather.

---

## Что имеет смысл сделать позже (чеклист)

1. **Починить `proxy rotate`:** ✅ выполнено 2026-04-10 — MTProxy Fake TLS на Fornex, внешний порт **8444** (443 занят Xray); код: проброс `MTPROXY_*` в subprocess, диагностика порта. Подробно: `Projects/VPN/SESSION_SUMMARY_2026-04-10.md`, `Projects/VPN/DONE_LIST_VPN.md`.
2. **Задокументировать в `Projects/VPN/docs/deployment.md`:** фактическое размещение `vpn-bot` на Fornex; панель (`vpn-web`) пока Timeweb — **перенос:** `Projects/VPN/docs/vpn-web-migration-fornex-plan.md`.
3. **Решить судьбу копий на Timeweb:** оставить как бэкап или удалить/архивировать, чтобы не деплоить туда по ошибке.
4. **Остальные боты на Timeweb** (например `hamster*`, `tradetherapybot` и т.д.): если нужен Telegram — либо перенос, либо туннель/прокси; иначе будут в том же состоянии, что и до миграции xxx/vpn-bot.
5. **Обновить локальные репозитории** (`Projects/xxx`, `Projects/VPN`): при необходимости добавить в README раздел «Прод: Fornex», чтобы не расходилось с `Main_docs/PROJECTS.md`.

---

## Ссылки на смежные документы

- `Main_docs/PROJECTS.md` — обновлённые краткие сведения по xxx, VPN и PastuhiBot.
- `Main_docs/RULES_CURSOR.md` — серверы Timeweb / Fornex.
- `Projects/PastuhiBot/docs/SERVER_MIGRATION_FORNEX_2026-04-10.md` — перенос hamster-стека.
- `Projects/PastuhiBot/DEV_HANDOFF_FORNEX_2026-04-10.md` — кратко для разработчика.
