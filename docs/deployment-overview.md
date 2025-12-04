# 📦 Обзор развертывания бота

## Текущее состояние

### Сервер:
- **IP адрес:** `81.200.146.32`
- **Путь к проекту:** `/opt/tradetherapybot`
- **Systemd service:** `tradetherapybot.service`
- **Статус:** ✅ Бот работает 24/7

### GitHub Actions:
- ✅ Workflow для автоматических тестов настроен (`.github/workflows/test.yml`)
- ✅ Workflow для автоматического деплоя создан (`.github/workflows/deploy.yml`)
- ⏳ Требуется настройка SSH ключей и GitHub Secrets для полной автоматизации

---

## Процесс обновления бота

### Вариант 1: Автоматический деплой (после настройки)

После настройки автоматического деплоя:
1. Внеси изменения в код
2. Закоммить: `git commit -m "описание"`
3. Отправить в GitHub: `git push origin main`
4. GitHub Actions автоматически:
   - Запустит тесты
   - Если тесты прошли → обновит код на сервере
   - Перезапустит бота

**Инструкция по настройке:** `docs/CICD_SETUP.md` или `QUICK_START_CICD.md`

### Вариант 2: Ручной деплой (текущий способ)

```bash
# 1. Подключиться к серверу
ssh root@81.200.146.32

# 2. Обновить код
cd /opt/tradetherapybot
git pull origin main

# 3. Установить зависимости (если requirements.txt изменился)
pip3 install --break-system-packages -r requirements.txt

# 4. Перезапустить бота
sudo systemctl restart tradetherapybot.service

# 5. Проверить статус
sudo systemctl status tradetherapybot.service
```

**Подробная инструкция:** `DEPLOYMENT_GUIDE.md` или `README_DEPLOYMENT.md`

---

## Важные файлы на сервере

- `env_vars.txt` - переменные окружения (токены) - **НЕ в Git!**
- `bot.db` - база данных SQLite - **НЕ в Git!**
- Все Python файлы - в Git
- Логи: `logs/bot.log` или через `journalctl -u tradetherapybot.service`

---

## Полезные команды

### Проверка статуса:
```bash
sudo systemctl status tradetherapybot.service
```

### Просмотр логов:
```bash
sudo journalctl -u tradetherapybot.service -f  # В реальном времени
sudo journalctl -u tradetherapybot.service -n 100  # Последние 100 строк
```

### Управление:
```bash
sudo systemctl restart tradetherapybot.service  # Перезапустить
sudo systemctl stop tradetherapybot.service     # Остановить
sudo systemctl start tradetherapybot.service    # Запустить
```

---

## Предотвращение проблем

1. **Всегда коммитьте перед деплоем** - так можно откатиться
2. **Проверяйте тесты** - они должны проходить перед деплоем
3. **Делайте бэкап БД** - команда `/backup` в боте (для админа)
4. **Проверяйте логи после деплоя** - убедитесь, что нет ошибок

---

## Документация

- **Автоматический деплой:** `docs/CICD_SETUP.md`, `QUICK_START_CICD.md`
- **Ручной деплой:** `DEPLOYMENT_GUIDE.md`, `README_DEPLOYMENT.md`
- **Git workflow:** `docs/git-workflow.md`
- **Предотвращение потери файлов:** `docs/preventing-file-loss.md`

