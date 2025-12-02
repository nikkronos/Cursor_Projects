# Команды для проверки развертывания бота на сервере

## Подключение к серверу

**Сервер:** Timeweb  
**IP:** 81.200.146.32  
**SSH команда:**
```bash
ssh root@81.200.146.32
```

После подключения выполните команды ниже.

---

## Шаг 1: Проверка systemd service

Выполните эти команды на сервере (через SSH):

```bash
# Проверить, существует ли service
systemctl status tradetherapybot.service

# Если service существует, проверить его статус
systemctl is-enabled tradetherapybot.service
systemctl is-active tradetherapybot.service
```

## Шаг 2: Поиск пути к проекту

**Возможные пути (из документации):**
- `/opt/tradetherapybot` (стандартный путь из service файла)
- `/home/user/tradetherapybot` (альтернативный путь)

**Команды для поиска:**

```bash
# Найти процесс Python, который запускает бота
ps aux | grep main.py

# Найти процесс по имени бота
ps aux | grep python | grep -i trade

# Проверить стандартный путь
ls -la /opt/tradetherapybot

# Найти файл main.py
find / -name "main.py" -type f 2>/dev/null | grep -i trade

# Найти файл bot.db (база данных)
find / -name "bot.db" -type f 2>/dev/null
```

## Шаг 3: Проверка логов

```bash
# Если service существует, посмотреть логи
journalctl -u tradetherapybot.service -n 50 --no-pager

# Посмотреть последние логи в реальном времени
journalctl -u tradetherapybot.service -f
```

## Шаг 4: Проверка файлов проекта

После того как найдете путь к проекту (скорее всего `/opt/tradetherapybot`):

```bash
# Перейти в директорию проекта
cd /opt/tradetherapybot  # или другой найденный путь

# Проверить наличие файлов
ls -la

# Проверить наличие env_vars.txt
cat env_vars.txt  # (не показывайте содержимое, только проверьте наличие)

# Проверить версию Python
python3 --version

# Проверить установленные зависимости
pip3 list | grep -E "pyTelegramBotAPI|python-dotenv|APScheduler"
```

## Шаг 5: Проверка конфигурации service (если существует)

```bash
# Посмотреть содержимое service файла
cat /etc/systemd/system/tradetherapybot.service

# Проверить, где находится проект согласно service
grep WorkingDirectory /etc/systemd/system/tradetherapybot.service
grep ExecStart /etc/systemd/system/tradetherapybot.service
```

---

## Что делать дальше

После выполнения команд, пришлите результаты:
1. Вывод `systemctl status tradetherapybot.service`
2. Вывод `ps aux | grep main.py` (или найденный путь)
3. Вывод `journalctl -u tradetherapybot.service -n 20` (если service существует)

На основе результатов определим:
- Работает ли бот через systemd или другим способом
- Нужно ли что-то настроить
- Где находится проект

