# Быстрый старт для автоматического запуска на сервере

## Шаги для настройки systemd (Linux)

### 1. Подготовка на сервере

```bash
# Создайте директорию для бота
sudo mkdir -p /opt/tradetherapybot
sudo chown $USER:$USER /opt/tradetherapybot

# Скопируйте файлы бота в эту директорию
# (используйте scp, git clone или другой способ)
```

### 2. Установка зависимостей

```bash
cd /opt/tradetherapybot
python3 -m venv venv  # опционально, создание виртуального окружения
source venv/bin/activate  # если используете venv
pip3 install -r requirements.txt
```

### 3. Настройка конфигурации

Убедитесь, что файл `env_vars.txt` заполнен:
```bash
nano env_vars.txt
```

### 4. Настройка systemd

```bash
# Скопируйте service файл
sudo cp tradetherapybot.service /etc/systemd/system/

# Отредактируйте пути
sudo nano /etc/systemd/system/tradetherapybot.service

# Важно изменить:
# - WorkingDirectory=/opt/tradetherapybot  (ваш путь)
# - ExecStart=/usr/bin/python3 /opt/tradetherapybot/main.py  (ваш путь)
# - User=your_username  (ваше имя пользователя)
```

### 5. Активация и запуск

```bash
# Перезагрузите конфигурацию
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable tradetherapybot.service

# Запустите бота
sudo systemctl start tradetherapybot.service

# Проверьте статус
sudo systemctl status tradetherapybot.service
```

### 6. Просмотр логов

```bash
# В реальном времени
sudo journalctl -u tradetherapybot.service -f

# Последние 100 строк
sudo journalctl -u tradetherapybot.service -n 100
```

## Управление ботом

```bash
# Запустить
sudo systemctl start tradetherapybot.service

# Остановить
sudo systemctl stop tradetherapybot.service

# Перезапустить
sudo systemctl restart tradetherapybot.service

# Статус
sudo systemctl status tradetherapybot.service

# Отключить автозапуск
sudo systemctl disable tradetherapybot.service
```

## Готово!

Теперь бот будет:
- ✅ Автоматически запускаться при загрузке сервера
- ✅ Автоматически перезапускаться при падении
- ✅ Работать в фоновом режиме

Подробная инструкция в файле `README_DEPLOYMENT.md`






