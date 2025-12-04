# ⚡ Обновление бота на сервере - Пошаговая инструкция

## ✅ Что у нас есть:
- Бот уже работает на сервере `81.200.146.32`
- Код обновлен локально и в GitHub
- Все файлы восстановлены (database.py, services.py, handlers/user.py)
- Тесты проходят

## 🔄 Обновление бота:

### Шаг 1: Подключиться к серверу через PowerShell

```powershell
ssh root@81.200.146.32
```

### Шаг 2: На сервере - обновить код

```bash
# Перейти в директорию бота
cd /opt/tradetherapybot

# Обновить код из GitHub (скачать последние изменения)
git pull origin main

# Установить зависимости, если requirements.txt изменился
pip3 install --break-system-packages -r requirements.txt
```

### Шаг 3: Перезапустить бота

```bash
# Перезапустить systemd service
sudo systemctl restart tradetherapybot.service

# Проверить статус (должен быть "active (running)")
sudo systemctl status tradetherapybot.service
```

### Шаг 4: Проверить, что всё работает

```bash
# Посмотреть логи в реальном времени
sudo journalctl -u tradetherapybot.service -f
```

**Нажмите `Ctrl+C` для выхода из просмотра логов.**

Или посмотреть последние 50 строк:
```bash
sudo journalctl -u tradetherapybot.service -n 50
```

---

## ✅ Проверка работы:

1. **Проверить в Telegram** - отправить боту команду `/start`
2. **Проверить логи** - не должно быть ошибок
3. **Проверить статус** - `systemctl status` должен показывать "active (running)"

---

## 🔧 Если что-то пошло не так:

### Бот не запустился:

1. **Посмотреть ошибки в логах:**
   ```bash
   sudo journalctl -u tradetherapybot.service -n 100
   ```

2. **Проверить файл env_vars.txt:**
   ```bash
   cat /opt/tradetherapybot/env_vars.txt
   ```

3. **Проверить, что файлы на месте:**
   ```bash
   ls -la /opt/tradetherapybot/*.py
   ```

### Откатить к предыдущей версии:

```bash
cd /opt/tradetherapybot
git log --oneline -5  # Посмотреть последние коммиты
git checkout <commit-hash>  # Откатиться к нужному коммиту
sudo systemctl restart tradetherapybot.service
```

---

## 📝 Важные замечания:

- ⚠️ **env_vars.txt** не обновится через `git pull` (он в .gitignore) - токены должны быть уже на сервере
- ✅ База данных `bot.db` сохранится (она тоже в .gitignore)
- ✅ Все данные пользователей сохранятся

---

**Готово! После этих шагов бот будет обновлен и продолжит работать с новой версией кода!** 🎉

