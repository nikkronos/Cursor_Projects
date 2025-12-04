# 🔄 Ручное обновление бота на сервере

## Текущая ситуация:
- ✅ Бот уже развернут и работает на сервере
- ✅ Нужно обновить код с новыми изменениями

## Обновление через PowerShell:

### Шаг 1: Подключиться к серверу

```powershell
ssh root@81.200.146.32
```

### Шаг 2: На сервере - обновить код

```bash
# Перейти в директорию бота
cd /opt/tradetherapybot

# Обновить код из GitHub
git pull origin main

# Установить зависимости (если requirements.txt изменился)
pip3 install --break-system-packages -r requirements.txt
```

### Шаг 3: Перезапустить бота

```bash
# Перезапустить systemd service
sudo systemctl restart tradetherapybot.service

# Проверить статус
sudo systemctl status tradetherapybot.service
```

### Шаг 4: Проверить логи

```bash
# Посмотреть логи в реальном времени
sudo journalctl -u tradetherapybot.service -f
```

Или последние 50 строк:
```bash
sudo journalctl -u tradetherapybot.service -n 50
```

---

## Если возникли проблемы:

### Бот не запускается:
1. Проверить логи: `sudo journalctl -u tradetherapybot.service -n 50`
2. Проверить файл `env_vars.txt`: `cat /opt/tradetherapybot/env_vars.txt`
3. Проверить права доступа: `ls -la /opt/tradetherapybot`

### Откатить к предыдущей версии:
```bash
cd /opt/tradetherapybot
git log --oneline -5  # Посмотреть последние коммиты
git checkout <commit-hash>  # Откатиться к нужному коммиту
sudo systemctl restart tradetherapybot.service
```

---

## ✅ Готово!

После обновления бот будет работать с новой версией кода!

