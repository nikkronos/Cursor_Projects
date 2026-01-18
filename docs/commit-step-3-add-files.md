# Шаг 3: Добавление файлов в Git

## Ситуация

Файлы скопированы в `TradeTherapyBot/`. Теперь нужно добавить их в Git для коммита.

## Команды для добавления

Выполните в PowerShell **из папки TradeTherapyBot**:

```powershell
# Убедитесь, что вы в папке TradeTherapyBot
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"

# Добавить всю документацию N8N
git add docs/n8n-*.md
git add docs/commit-*.md
git add docs/cursor-agent-controls.md
git add docs/env-vars-location.md
git add docs/extensions-recommendations.md
git add docs/project-structure-analysis.md
git add docs/server-timeweb.md
git add docs/work-plan-n8n-testing.md

# Добавить обновлённые файлы в корне
git add PROJECTS.md
git add RULES_CURSOR.md
git add ROAD_MAP_AI.md
git add .gitignore
git add env_vars.example.txt

# Добавить папку n8n
git add n8n/

# Добавить другие изменённые файлы (если нужно)
git add DONE_LIST_TRADETHERAPYBOT.md
git add ROADMAP_TRADETHERAPYBOT.md
```

## Проверка перед коммитом

После добавления проверьте статус:

```powershell
git status
```

Должны быть видны файлы в разделе **"Changes to be committed"** (зелёным цветом).

## Если есть файлы с `../` (в родительской директории)

Если Git всё ещё видит файлы в родительской директории (`../`), это нормально - они могут быть отслеживаемыми, но изменёнными. Их можно игнорировать для этого коммита, так как мы работаем с файлами внутри `TradeTherapyBot/`.

---

**Последнее обновление:** 2025-12-24























