# Инструкция по автоматическому запуску бота на сервере

## Вариант 1: Использование systemd (рекомендуется для Linux)

### Шаг 1: Подготовка

1. Скопируйте бота на сервер (например, в `/opt/tradetherapybot` или `/home/user/tradetherapybot`)
2. Установите зависимости:
   ```bash
   cd /path/to/TradeTherapyBot
   pip3 install -r requirements.txt
   ```
3. Настройте `env_vars.txt` с вашими данными

### Шаг 2: Настройка systemd service

1. Скопируйте файл `tradetherapybot.service` в `/etc/systemd/system/`:
   ```bash
   sudo cp tradetherapybot.service /etc/systemd/system/
   ```

2. Откройте файл для редактирования:
   ```bash
   sudo nano /etc/systemd/system/tradetherapybot.service
   ```

3. Обновите пути в файле:
   - `WorkingDirectory` - путь к папке с ботом
   - `ExecStart` - полный путь к `main.py`
   - `User` - имя пользователя, от которого будет запускаться бот (лучше создать отдельного пользователя)

   Пример:
   ```
   WorkingDirectory=/opt/tradetherapybot
   ExecStart=/usr/bin/python3 /opt/tradetherapybot/main.py
   User=tradetherapy
   ```

4. Перезагрузите конфигурацию systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

5. Включите автозапуск:
   ```bash
   sudo systemctl enable tradetherapybot.service
   ```

6. Запустите бота:
   ```bash
   sudo systemctl start tradetherapybot.service
   ```

### Управление ботом

- **Проверить статус:**
  ```bash
  sudo systemctl status tradetherapybot.service
  ```

- **Остановить бота:**
  ```bash
  sudo systemctl stop tradetherapybot.service
  ```

- **Перезапустить бота:**
  ```bash
  sudo systemctl restart tradetherapybot.service
  ```

- **Посмотреть логи:**
  ```bash
  sudo journalctl -u tradetherapybot.service -f
  ```

- **Посмотреть последние логи:**
  ```bash
  sudo journalctl -u tradetherapybot.service -n 100
  ```

### Шаг 3: Настройка прав доступа

Убедитесь, что у бота есть права на запись в директорию:
```bash
sudo chown -R tradetherapy:tradetherapy /opt/tradetherapybot
sudo chmod -R 755 /opt/tradetherapybot
```

## Вариант 2: Использование screen (простой вариант)

Если у вас нет прав root или не хотите использовать systemd:

1. Установите screen:
   ```bash
   sudo apt-get install screen  # для Debian/Ubuntu
   ```

2. Создайте сессию screen:
   ```bash
   screen -S tradetherapybot
   ```

3. Перейдите в директорию бота и запустите:
   ```bash
   cd /path/to/TradeTherapyBot
   python3 main.py
   ```

4. Отключитесь от screen: нажмите `Ctrl+A`, затем `D`

5. Чтобы вернуться к сессии:
   ```bash
   screen -r tradetherapybot
   ```

**Недостаток:** При перезагрузке сервера бот не запустится автоматически.

## Вариант 3: Использование nohup (самый простой)

1. Запустите бота с nohup:
   ```bash
   cd /path/to/TradeTherapyBot
   nohup python3 main.py > bot_output.log 2>&1 &
   ```

2. Бот будет работать в фоне. Чтобы остановить, найдите процесс:
   ```bash
   ps aux | grep main.py
   kill <PID>
   ```

**Недостаток:** При перезагрузке сервера бот не запустится автоматически.

## Рекомендации

- **Используйте systemd** - это самый надежный способ с автоматическим перезапуском
- Регулярно делайте бэкап базы данных командой `/backup`
- Настройте мониторинг логов для отслеживания ошибок
- Создайте отдельного пользователя для бота (безопасность)

## Создание пользователя для бота

```bash
sudo useradd -r -s /bin/false tradetherapy
sudo mkdir -p /opt/tradetherapybot
sudo chown tradetherapy:tradetherapy /opt/tradetherapybot
```

## Устранение проблем

- Если бот не запускается, проверьте логи:
  ```bash
  sudo journalctl -u tradetherapybot.service -n 50
  ```

- Если есть проблемы с правами доступа, проверьте:
  ```bash
  ls -la /path/to/TradeTherapyBot
  ```

- Проверьте, что Python 3 установлен:
  ```bash
  python3 --version
  which python3
  ```











