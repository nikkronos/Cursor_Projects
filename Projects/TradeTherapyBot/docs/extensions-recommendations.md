# Рекомендации по расширениям Cursor

## Текущие установленные расширения

Судя по скриншоту, у вас установлены:
- ✅ **GitHub Actions** - для работы с CI/CD
- ✅ **PowerShell** - для работы с PowerShell скриптами
- ✅ **Python (Static Type Checking)** - Anysphere
- ✅ **Python (Language Support)** - ms-python
- ✅ **Python Debugger** - ms-python

## Рекомендуемые к установке

### Обязательные для работы

1. **GitLens — Git Supercharged** (GitKraken)
   - Расширенная работа с Git
   - Просмотр истории коммитов, blame, сравнение версий
   - **ID:** `eamodio.gitlens`

2. **Git History** (donjayamanne)
   - Просмотр истории Git файлов
   - Полезно для отслеживания изменений
   - **ID:** `donjayamanne.githistory`

3. **markdownlint** (DavidAnson)
   - Проверка Markdown файлов
   - Полезно для документации
   - **ID:** `DavidAnson.vscode-markdownlint`

### Полезные для разработки

4. **Python** (ms-python) - уже установлен ✅
5. **Python Debugger** (ms-python) - уже установлен ✅
6. **GitHub Actions** - уже установлен ✅

## Расширения, которые можно удалить (если не используются)

- Если есть дублирующие расширения Python - оставить только ms-python
- Если есть неиспользуемые расширения для других языков (если не планируете их использовать)

## Как установить/удалить расширения

### Через UI Cursor:

1. **Откройте Extensions:**
   - Нажмите `Ctrl+Shift+X`
   - Или через меню: View → Extensions

2. **Установка:**
   - Введите название расширения в поиск
   - Нажмите "Install"

3. **Удаление:**
   - Найдите расширение в списке "INSTALLED"
   - Нажмите на иконку настроек (⚙️) рядом с расширением
   - Выберите "Uninstall"

### Через Command Palette:

1. Нажмите `Ctrl+Shift+P`
2. Введите "Extensions: Install Extensions" или "Extensions: Uninstall Extensions"
3. Выберите нужное расширение

## Рекомендуемый набор для ваших проектов

**Минимальный набор:**
- ✅ Python (ms-python) - уже есть
- ✅ Python Debugger (ms-python) - уже есть
- ✅ GitHub Actions - уже есть
- ✅ PowerShell - уже есть
- ⬜ GitLens - **рекомендуется установить**
- ⬜ Git History - **рекомендуется установить**
- ⬜ markdownlint - **рекомендуется установить**

---

**Последнее обновление:** 2025-12-23

