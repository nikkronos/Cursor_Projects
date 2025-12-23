# Инструкция для следующего агента

## Быстрый старт

1. **Прочитай правила работы:**
   - `../RULES_CURSOR.md` - общие правила работы с проектами

2. **Изучи проект:**
   - `ROADMAP_TRADETHERAPYBOT.md` - что в планах
   - `DONE_LIST_TRADETHERAPYBOT.md` - что уже сделано
   - `SESSION_SUMMARY_2025-12-09.md` - последняя сессия

3. **Прочитай базу знаний:**
   - `docs/agent-onboarding.md` - начни отсюда
   - `docs/architecture.md` - архитектура
   - `docs/business-rules.md` - бизнес-правила
   - `docs/database.md` - структура БД
   - `docs/patterns.md` - правила кода
   - `docs/security.md` - безопасность

## Важные правила

### ⚠️ КРИТИЧЕСКИ ВАЖНО:

1. **Проект коммитится в Git** - все изменения через Git
2. **Перед изменением функции проверяй все связанные обработчики**
3. **Все кнопки в меню должны иметь обработчики**
4. **Проверяй навигацию между меню**
5. **Не коммить код, который ломает существующие функции**

### Работа с кодом:

- Используй `validators.py` для валидации входных данных
- Логируй все важные операции через `logger`
- Обрабатывай все ошибки через `try-except`
- Используй параметризованные SQL-запросы (никогда f-строки!)

### Работа с Git:

- **Автоматический деплой:** при `git push origin main` код автоматически обновляется на сервере
- **Тесты:** автоматически запускаются перед деплоем
- **Бэкап БД:** автоматически создается перед деплоем

**Подробнее:** `docs/CICD_SETUP.md`, `docs/git-workflow.md`

## Что уже сделано

**См. подробности в:** `DONE_LIST_TRADETHERAPYBOT.md`

## Что в планах

**См. планы в:** `ROADMAP_TRADETHERAPYBOT.md`

## Полезные команды

### Проверка статуса бота:
```bash
systemctl status tradetherapybot.service
journalctl -u tradetherapybot.service -f
```

### Обновление на сервере:
```bash
# Автоматически через Git push
git push origin main
```

### Ручное обновление (если нужно):
```bash
# На сервере
cd /home/tradetherapybot
git pull origin main
systemctl restart tradetherapybot.service
```

## Если что-то непонятно

1. Читай `../RULES_CURSOR.md` - общие правила
2. Изучи `ROADMAP_TRADETHERAPYBOT.md` - планы
3. Изучи `DONE_LIST_TRADETHERAPYBOT.md` - выполненные задачи
4. Изучи `SESSION_SUMMARY_2025-12-09.md` - последняя сессия
5. Читай документацию в `docs/`

---

**Удачи!** 🚀
