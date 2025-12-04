# 🚀 Инструкция по развертыванию бота в продакшн

## Что нужно для развертывания

### 1. Подготовка на сервере

**Требования:**
- Сервер с Linux (Ubuntu/Debian)
- Python 3.7+
- Git установлен
- Доступ по SSH (root или пользователь с sudo)

**Шаги:**

1. **Подключитесь к серверу:**
   ```bash
   ssh root@81.200.146.32
   ```

2. **Создайте директорию для бота:**
   ```bash
   mkdir -p /opt/tradetherapybot
   cd /opt/tradetherapybot
   ```

3. **Инициализируйте Git репозиторий (если еще не сделано):**
   ```bash
   git init
   git remote add origin https://github.com/ВАШ_НИК/TradeTherapyBot.git
   git pull origin main
   ```

4. **Установите зависимости:**
   ```bash
   pip3 install --break-system-packages -r requirements.txt
   ```

5. **Создайте файл с переменными окружения:**
   ```bash
   nano env_vars.txt
   ```
   
   Добавьте:
   ```
   BOT_TOKEN=ваш_токен_бота
   ADMIN_ID=ваш_telegram_id
   GROUP_CHAT_ID=id_закрытой_группы
   ```

6. **Настройте systemd service:**
   ```bash
   sudo cp tradetherapybot.service /etc/systemd/system/
   sudo nano /etc/systemd/system/tradetherapybot.service
   ```
   
   Проверьте пути в файле (они должны быть правильными).

7. **Активируйте и запустите сервис:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable tradetherapybot.service
   sudo systemctl start tradetherapybot.service
   ```

8. **Проверьте статус:**
   ```bash
   sudo systemctl status tradetherapybot.service
   ```

---

### 2. Настройка автоматического деплоя (CI/CD)

**Преимущества:** После настройки каждый `git push` автоматически обновит бота на сервере.

#### Шаг 1: Создание SSH ключа

**На вашем компьютере (Windows):**

1. Откройте PowerShell в папке проекта:
   ```powershell
   cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
   ```

2. Запустите скрипт создания ключа:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup-ssh-key.ps1
   ```

3. Скопируйте **публичный ключ** (будет показан в консоли)

#### Шаг 2: Добавление ключа на сервер

**На сервере:**

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ_ЗДЕСЬ" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### Шаг 3: Настройка GitHub Secrets

1. Откройте ваш репозиторий на GitHub
2. Перейдите: **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret** и добавьте:

   - **SSH_PRIVATE_KEY** - приватный ключ (весь текст от `-----BEGIN` до `-----END`)
   - **SSH_HOST** - `81.200.146.32`
   - **SSH_PORT** - `22`
   - **SSH_USER** - `root`
   - **DEPLOY_PATH** - `/opt/tradetherapybot`
   - **SERVICE_NAME** - `tradetherapybot`

#### Шаг 4: Проверка

Сделайте тестовый коммит:
```powershell
git add .
git commit -m "test: проверка CI/CD"
git push origin main
```

Проверьте в GitHub: **Actions** → должны запуститься тесты, затем деплой.

---

### 3. Ручной деплой (если CI/CD не настроен)

Если автоматический деплой не работает, можно обновить бота вручную:

```bash
# 1. Подключиться к серверу
ssh root@81.200.146.32

# 2. Перейти в директорию проекта
cd /opt/tradetherapybot

# 3. Обновить код
git pull origin main

# 4. Установить зависимости (если requirements.txt изменился)
pip3 install --break-system-packages -r requirements.txt

# 5. Перезапустить бота
systemctl restart tradetherapybot.service

# 6. Проверить статус
systemctl status tradetherapybot.service
```

---

## Управление ботом на сервере

### Полезные команды:

```bash
# Проверить статус
sudo systemctl status tradetherapybot.service

# Остановить бота
sudo systemctl stop tradetherapybot.service

# Запустить бота
sudo systemctl start tradetherapybot.service

# Перезапустить бота
sudo systemctl restart tradetherapybot.service

# Посмотреть логи
sudo journalctl -u tradetherapybot.service -f

# Посмотреть последние 100 строк логов
sudo journalctl -u tradetherapybot.service -n 100
```

---

## Что делать, если что-то пошло не так?

### Бот не запускается

1. Проверьте логи:
   ```bash
   sudo journalctl -u tradetherapybot.service -n 50
   ```

2. Проверьте файл `env_vars.txt`:
   ```bash
   cat /opt/tradetherapybot/env_vars.txt
   ```

3. Проверьте права доступа:
   ```bash
   ls -la /opt/tradetherapybot
   ```

### CI/CD не работает

1. Проверьте GitHub Secrets (все ли добавлены)
2. Проверьте SSH подключение:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\test-ssh-connection.ps1
   ```
3. Проверьте логи в GitHub: **Actions** → выберите последний workflow

---

## Резервное копирование

**Важно:** Регулярно делайте бэкап базы данных!

### Через бота (рекомендуется):
Используйте команду `/backup` в Telegram (только для администратора)

### Вручную на сервере:
```bash
cd /opt/tradetherapybot
cp bot.db backups/bot_$(date +%Y%m%d_%H%M%S).db
```

---

## Безопасность

⚠️ **Важно:**
- Никогда не коммитьте файл `env_vars.txt` в Git (он в .gitignore)
- Храните SSH ключи в безопасном месте
- Регулярно обновляйте зависимости: `pip3 install --upgrade -r requirements.txt`
- Делайте бэкапы базы данных перед обновлениями

---

## Подробные инструкции

- **Автоматический деплой:** `QUICK_START_CICD.md` или `docs/CICD_SETUP.md`
- **Ручной деплой:** `README_DEPLOYMENT.md`
- **Git workflow:** `docs/git-workflow.md`

