# 📝 Закоммитить изменения и обновить бота

## Шаг 1: Закоммитить изменения документации

В терминале Cursor выполните:

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"

# Посмотреть, что изменилось
git status

# Добавить все изменения
git add .

# Создать коммит
git commit -m "docs: обновление документации (предотвращение потери файлов)"

# Отправить в GitHub
git push origin main
```

---

## Шаг 2: Обновить бота на сервере

### Подключиться к серверу:

```powershell
ssh root@81.200.146.32
```

### На сервере выполнить:

```bash
# Перейти в директорию бота
cd /opt/tradetherapybot

# Обновить код из GitHub
git pull origin main

# Установить зависимости (если requirements.txt изменился)
pip3 install --break-system-packages -r requirements.txt

# Перезапустить бота
sudo systemctl restart tradetherapybot.service

# Проверить статус
sudo systemctl status tradetherapybot.service
```

### Проверить логи:

```bash
sudo journalctl -u tradetherapybot.service -n 50
```

---

**После этого бот будет обновлен!** ✅

