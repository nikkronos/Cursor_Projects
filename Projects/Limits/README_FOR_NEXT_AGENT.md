# Инструкция для следующего агента — Лимиты

- Проект: виджет для пачки лимитных заявок Т-Инвестиции (акции/фьючерсы).
- Backend: `server.py` (Flask), эндпоинты: `/api/accounts`, `/api/instruments`, `/api/orderbook`, `POST /api/orders/limit-batch`.
- Frontend: `static/index.html`, `static/style.css`, `static/app.js`. Избранное — localStorage ключ `limits_favorites`.
- Документация: `docs/agent-onboarding.md`, `docs/architecture.md`, `docs/specs/01-limit-orders-widget.md`.
- Репозиторий: **nikkronos/Limits**. Секреты не коммитить (env_vars.txt, .env в .gitignore).
