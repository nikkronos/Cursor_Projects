# Шаг 2: Копирование файлов в TradeTherapyBot

## Ситуация

Git видит файлы в родительской директории (`../`), но репозиторий находится в `TradeTherapyBot/`. Нужно скопировать файлы в репозиторий.

## Команды для копирования

Выполните в PowerShell **из корня проекта** (`Cursor_test`):

```powershell
# Перейти в корень проекта
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"

# Скопировать документацию N8N в TradeTherapyBot/docs/
Copy-Item -Path "docs\n8n-*.md" -Destination "TradeTherapyBot\docs\" -Force

# Скопировать другие файлы документации
Copy-Item -Path "docs\commit-instructions-n8n.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\commit-strategy.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\cursor-agent-controls.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\env-vars-location.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\extensions-recommendations.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\project-structure-analysis.md" -Destination "TradeTherapyBot\docs\" -Force
Copy-Item -Path "docs\server-timeweb.md" -Destination "TradeTherapyBot\docs\" -Force

# Скопировать обновлённые файлы в TradeTherapyBot/
Copy-Item -Path "RULES_CURSOR.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "PROJECTS.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "ROAD_MAP_AI.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path ".gitignore" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "env_vars.example.txt" -Destination "TradeTherapyBot\" -Force

# Скопировать папку n8n в TradeTherapyBot/
Copy-Item -Path "n8n" -Destination "TradeTherapyBot\" -Recurse -Force
```

## После копирования

Перейдите в `TradeTherapyBot` и проверьте статус:

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
git status
```

Теперь файлы должны быть видны как новые или изменённые **внутри** репозитория.

---

**Последнее обновление:** 2025-12-24























