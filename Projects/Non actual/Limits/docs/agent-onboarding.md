# Онбординг агента — Лимиты

## Назначение проекта
Виджет для массового выставления лимитных заявок через API Т-Инвестиции (T-Bank Invest). Пользователь выбирает инструмент, вводит сумму в рублях, количество заявок и шаг в %, нажимает кнопку — выставляется пачка заявок ниже (покупка) или выше (продажа) текущей цены.

## Стек
- Backend: Python, Flask, requests. Токен TINKOFF_INVEST_TOKEN, SANDBOX=1 — песочница.
- Frontend: статика (HTML/CSS/JS), без фреймворков. Избранное — localStorage.
- Деплой: Timeweb 24/7 (как Damir).

## Важные файлы
- `server.py` — Flask, прокси к T-Invest API, эндпоинты: accounts, instruments, orderbook, place_orders.
- `static/` — index.html, style.css, app.js.
- Документация API: https://developer.tbank.ru/invest/

## Репозиторий
Коммиты из папки `Projects/Non actual/Limits/` в репозиторий **nikkronos/Limits**. Секреты не коммитить (env_vars.txt, .env в .gitignore).
