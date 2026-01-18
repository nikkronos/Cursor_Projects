# Инструкция: Коммит изменений N8N интеграции

## Важно: Расположение репозитория

**Репозиторий находится в папке `TradeTherapyBot/`, а НЕ в корне проекта!**

- **Корень проекта:** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_test`
- **Репозиторий:** `C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot`

## Что нужно закоммитить

### Файлы в корне (нужно скопировать в TradeTherapyBot или добавить из корня):

1. **Документация N8N:**
   - `docs/n8n-*.md` (все файлы документации N8N)

2. **Обновлённые файлы:**
   - `RULES_CURSOR.md`
   - `PROJECTS.md`
   - `ROAD_MAP_AI.md`
   - `.gitignore`
   - `env_vars.example.txt`

3. **Структура N8N:**
   - `n8n/` (папка с утилитами и примерами)

### Что НЕ коммитить (уже в .gitignore):

- ❌ `TestN8N/` (тестовый бот, не коммитится)
- ❌ `env_vars.txt` (секреты)
- ❌ `PastuhiBot/` (не коммитится)
- ❌ `ParentChildResearch/` (не коммитится)

## Пошаговые команды

### Шаг 1: Перейти в папку с репозиторием

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
```

### Шаг 2: Проверить статус

```powershell
git status
```

### Шаг 3: Добавить файлы

**Вариант А: Если файлы уже в TradeTherapyBot/**

```powershell
git add docs/n8n-*.md
git add n8n/
git add RULES_CURSOR.md
git add PROJECTS.md
git add ROAD_MAP_AI.md
git add .gitignore
git add env_vars.example.txt
```

**Вариант Б: Если файлы в корне, нужно скопировать их в TradeTherapyBot/**

Сначала скопируйте файлы из корня в TradeTherapyBot:

```powershell
# Из корня проекта
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"

# Скопировать документацию N8N
Copy-Item -Path "docs\n8n-*.md" -Destination "TradeTherapyBot\docs\" -Force

# Скопировать обновлённые файлы
Copy-Item -Path "RULES_CURSOR.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "PROJECTS.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "ROAD_MAP_AI.md" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path ".gitignore" -Destination "TradeTherapyBot\" -Force
Copy-Item -Path "env_vars.example.txt" -Destination "TradeTherapyBot\" -Force

# Скопировать папку n8n (если её нет в TradeTherapyBot)
Copy-Item -Path "n8n" -Destination "TradeTherapyBot\" -Recurse -Force
```

Затем перейти в TradeTherapyBot и добавить:

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
git add docs/n8n-*.md
git add n8n/
git add RULES_CURSOR.md
git add PROJECTS.md
git add ROAD_MAP_AI.md
git add .gitignore
git add env_vars.example.txt
```

### Шаг 4: Проверить, что будет закоммичено

```powershell
git status
```

Убедитесь, что:
- ✅ Добавлены файлы документации N8N
- ✅ Добавлены обновлённые файлы
- ❌ НЕ добавлены `TestN8N/`, `env_vars.txt`, `PastuhiBot/`, `ParentChildResearch/`

### Шаг 5: Сделать коммит

```powershell
git commit -m "feat: интеграция N8N и создание TestN8N бота

- Настроена интеграция с N8N Cloud
- Создан workflow 'Telegram Event Webhook Receiver'
- Создан тестовый бот TestN8N для проверки интеграции
- Добавлена документация по N8N (n8n-integration.md, n8n-setup-instructions.md, и т.д.)
- Обновлены RULES_CURSOR.md, PROJECTS.md, ROAD_MAP_AI.md
- Добавлена задача про автоматизм по резюме для HeadHunter
- Обновлён .gitignore для защиты секретов N8N"
```

### Шаг 6: Отправить в GitHub

```powershell
git push origin main
```

После `git push` автоматически:
1. Запускаются тесты (GitHub Actions)
2. При успешных тестах → автоматический деплой на сервер (для TradeTherapyBot)

## Проверка после коммита

1. Проверьте в GitHub, что коммит появился
2. Проверьте в GitHub Actions, что тесты прошли
3. Убедитесь, что все файлы на месте

---

**Последнее обновление:** 2025-12-24























