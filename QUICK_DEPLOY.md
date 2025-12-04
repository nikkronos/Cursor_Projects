# ⚡ Быстрое развертывание бота в продакшн

## Что уже готово ✅

- ✅ GitHub Actions workflows созданы (автоматические тесты + деплой)
- ✅ Systemd service файл готов (`tradetherapybot.service`)
- ✅ Скрипты для настройки SSH ключей готовы
- ✅ Документация по развертыванию готова

## Что нужно сделать сейчас

### Вариант 1: Автоматический деплой (рекомендуется) 🚀

**За 3 шага:**

1. **Инициализируйте Git и загрузите код в GitHub:**
   ```powershell
   cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
   git init
   git add .
   git commit -m "Initial commit"
   # Создайте репозиторий на GitHub и выполните:
   git remote add origin https://github.com/ВАШ_НИК/TradeTherapyBot.git
   git branch -M main
   git push -u origin main
   ```

2. **Настройте сервер (один раз):**
   - Подключитесь к серверу: `ssh root@81.200.146.32`
   - Выполните шаги из `DEPLOYMENT_GUIDE.md` (раздел "Подготовка на сервере")

3. **Настройте автоматический деплой:**
   - Следуйте инструкции в `QUICK_START_CICD.md` (5 минут)

**После этого:** Каждый `git push` автоматически обновит бота на сервере! 🎉

---

### Вариант 2: Ручной деплой (быстро, но без автоматизации)

1. **Подготовьте файл `env_vars.txt`** (если еще нет):
   ```
   BOT_TOKEN=ваш_токен
   ADMIN_ID=ваш_id
   GROUP_CHAT_ID=id_группы
   ```

2. **Загрузите файлы на сервер:**
   ```powershell
   # Используйте scp или загрузите через FTP/SFTP клиент
   scp -r * root@81.200.146.32:/opt/tradetherapybot/
   ```

3. **На сервере:**
   ```bash
   ssh root@81.200.146.32
   cd /opt/tradetherapybot
   pip3 install --break-system-packages -r requirements.txt
   sudo cp tradetherapybot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable tradetherapybot.service
   sudo systemctl start tradetherapybot.service
   ```

---

## Подробные инструкции

- **Полная инструкция:** `DEPLOYMENT_GUIDE.md`
- **Автоматический деплой:** `QUICK_START_CICD.md`
- **Ручной деплой:** `README_DEPLOYMENT.md`

---

## Проверка работы

После развертывания проверьте:

```bash
# На сервере
sudo systemctl status tradetherapybot.service
sudo journalctl -u tradetherapybot.service -f
```

Бот должен отвечать в Telegram! 🤖

