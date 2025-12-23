# Команды для коммита - выполни сейчас

## Шаг 1: Проверь, есть ли репозиторий в корне

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"
git status
```

Если выдает ошибку "not a git repository", выполни:
```powershell
git init
```

## Шаг 2: Проверь .gitignore

Убедись, что в `.gitignore` есть:
```
ParentChildResearch/
PastuhiBot/
```

## Шаг 3: Добавь файлы и сделай коммит

```powershell
# Добавить все файлы (ParentChildResearch и PastuhiBot автоматически исключатся)
git add .

# Проверить, что добавилось
git status

# Сделать коммит
git commit -m "docs: унифицирована структура документов и созданы правила работы

- Создан RULES_CURSOR.md с правилами работы с проектами
- Создан COMMIT_CURSOR.md с правилами коммитов
- Обновлен QUICK_START_AGENT.md с новой структурой
- Создан docs/AGENT_PROMPTS.md - полная инструкция для агента
- Унифицирована структура документов в TradeTherapyBot (ROADMAP, DONE_LIST, SESSION_SUMMARY)
- Обновлены README_FOR_NEXT_AGENT.md в TradeTherapyBot
- Обновлен .gitignore для исключения ParentChildResearch и PastuhiBot"

# Если репозиторий уже настроен на GitHub, отправь изменения
git push origin main
```

## Шаг 4: Если репозиторий еще не настроен на GitHub

```powershell
# Добавить remote (замени на свой URL)
git remote add origin https://github.com/твой_username/название_репозитория.git

# Установить ветку main
git branch -M main

# Отправить в репозиторий
git push -u origin main
```

---

**Выполни эти команды и сообщи результат!**

