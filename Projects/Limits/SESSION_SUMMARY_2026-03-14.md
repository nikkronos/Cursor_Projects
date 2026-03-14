# Резюме сессии 2026-03-14 — Лимиты

## Контекст работы
- Новый проект «Лимиты»: виджет для выставления пачек лимитных заявок через API Т-Инвестиции (по образцу Damir).
- Репозиторий: nikkronos/Limits (уже создан пользователем).
- Решения: один счёт (первый из API), ввод в рублях с авто-переводом в лоты, без подтверждения, избранное в localStorage.

## Выполненные задачи в этой сессии
- Созданы ROADMAP, DONE_LIST, SESSION_SUMMARY, docs (agent-onboarding, architecture, spec 01-limit-orders-widget).
- Реализован backend (server.py): GetAccounts (первый счёт), инструменты (Shares + Futures), стакан (кэш 10 сек), POST /api/orders/limit-batch (рубли → лоты, пачка лимитных заявок с паузой 0.5 сек).
- Реализован frontend: поиск инструмента, фильтр «Только избранные» (localStorage), текущая цена (обновление 10 сек), поля сумма/кол-во/шаг %, кнопки «Покупка ниже» / «Продажа выше», лог результатов. Избранное: двойной клик по инструменту в списке.
- Добавлены README, requirements.txt, env_vars.example.txt, .gitignore, README_FOR_NEXT_AGENT.

## Важные замечания для следующего агента
- Токен и SANDBOX — в env (TINKOFF_INVEST_TOKEN, SANDBOX=1 — песочница).
- Документация API: developer.tbank.ru/invest
