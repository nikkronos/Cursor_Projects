# CLAUDE.md — Cursor_Projects (монорепо)

> Читается Claude Code автоматически при старте сессии.
> Профиль владельца: `Main_docs/PROFILE.md` — прочти первым.

---

## Старт сессии

1. `git status` + `git log --oneline -3`
2. Прочитай `Main_docs/PROFILE.md` — кто владелец, принципы работы, технический контекст
3. Если работаешь с конкретным проектом — читай `CLAUDE.md` в его папке

---

## Структура монорепо

```
Cursor_Projects/
├── Main_docs/          # PROFILE.md, PROJECTS.md, RULES_CURSOR.md, AGENT_PROMPTS.md
│   └── env_vars.txt    # Секреты (НЕ коммитить!)
├── Projects/
│   ├── VPN/            # Отдельный git-репо → nikkronos/vpnservice
│   └── Non actual/     # Архив (трекается в монорепо)
└── docs/               # Общая документация
```

## Репозитории

| Папка | Репо | Куда пушить |
|-------|------|-------------|
| Корень / Main_docs / docs | `nikkronos/Cursor_Projects` | `origin main` |
| `Projects/VPN/` | `nikkronos/vpnservice` | из папки VPN |
| `Projects/Non actual/xxx/` | `nikkronos/kopiya-iksuyemsya` | из папки xxx |

**`Projects/VPN/` и `TestN8N/` исключены из монорепо через `.gitignore`.**

---

## Git-правила

- После каждого изменения: `git add` → `git commit` → **`git push`** (push обязателен)
- Не коммитить `env_vars.txt`, `.env`, любые файлы с секретами
- Деплой на сервер: SCP напрямую, не через git pull

---

## Серверы

- **Fornex:** `ssh -i ~/.ssh/id_ed25519_fornex root@185.21.8.91` (алиас: `ssh fornex`)
- **VPN-сервис:** `/opt/vpnservice/` — бот + Flask на `:5001`

---

## Правила работы

Полные правила: `Main_docs/RULES.md`
Детали по проекту: `CLAUDE.md` в корне проекта (если есть)
