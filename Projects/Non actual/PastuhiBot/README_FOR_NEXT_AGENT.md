# Инструкция для следующего агента

## Быстрый старт

1. **Прочитай правила работы:**
   - `../RULES_CURSOR.md` - общие правила работы с проектами

2. **Изучи проект:**
   - `ROADMAP_PASTUHIBOT.md` - что в планах
   - `DONE_LIST_PASTUHIBOT.md` - что уже сделано
   - `SESSION_SUMMARY_2025-12-23.md` - последняя сессия

3. **Прочитай базу знаний:**
   - `docs/agent-onboarding.md` - начни отсюда
   - `docs/architecture.md` - архитектура
   - `docs/business-rules.md` - бизнес-правила
   - `docs/database.md` - структура БД
   - `docs/patterns.md` - правила кода
   - `docs/security.md` - безопасность

## Важные правила

### ⚠️ КРИТИЧЕСКИ ВАЖНО:

1. **Проект НЕ коммитится в Git** - все изменения хранятся локально
2. **Перед изменением функции проверяй все связанные обработчики**
3. **Все кнопки в меню должны иметь обработчики**
4. **Проверяй навигацию между меню**
5. **Не применяй изменения на боевом сервере без тестирования**

### Работа с кодом:

- Используй `validators.py` для валидации входных данных
- Логируй все важные операции через `logger`
- Обрабатывай все ошибки через `try-except`
- Используй параметризованные SQL-запросы (никогда f-строки!)

### Работа с сервером:

- **IP:** 81.200.146.32
- **Пользователь:** root
- **Путь:** `/home/hamster93_bot/`
- **Сервис:** `hamster93_bot.service`

**Обновление на сервере:**
- Скопировать файлы через SCP
- Перезапустить: `systemctl restart hamster93_bot.service`
- Проверить логи: `journalctl -u hamster93_bot.service -f`

Подробнее: `docs/deployment.md`

## Что уже сделано

**См. подробности в:** `DONE_LIST_PASTUHIBOT.md`

## Что в планах

**См. планы в:** `ROADMAP_PASTUHIBOT.md`

## Полезные команды

### Экспорт пользователей:
```bash
cd /home/hamster93_bot
source venv/bin/activate
python export_users_simple.py
```

### Проверка статуса бота:
```bash
systemctl status hamster93_bot.service
journalctl -u hamster93_bot.service -f
```

### Обновление на сервере:
```powershell
# Скопировать файлы
scp -r "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\PastuhiBot\handlers" root@81.200.146.32:/home/hamster93_bot/
# На сервере
systemctl restart hamster93_bot.service
```

## Если что-то непонятно

1. Читай `../RULES_CURSOR.md` - общие правила
2. Изучи `ROADMAP_PASTUHIBOT.md` - планы
3. Изучи `DONE_LIST_PASTUHIBOT.md` - выполненные задачи
4. Изучи `SESSION_SUMMARY_2025-12-23.md` - последняя сессия
5. Читай документацию в `docs/`

---

**Удачи!** 🚀

