# Конфигурация проекта

## Важные переменные окружения

### GROUP_CHAT_ID

**Критически важно:** `GROUP_CHAT_ID` должен быть актуальным и указывать на группу, в которой бот является администратором.

#### Формат
- Для групп ID начинается с `-100` (например, `-1002346216181`)
- Это числовое значение, которое можно получить через бота @userinfobot или через API

#### Где обновить
1. **Локально:** `env_vars.txt` в корне проекта
2. **На сервере:** `/opt/tradetherapybot/env_vars.txt` (или путь, указанный в `DEPLOY_PATH`)
3. **GitHub Secrets:** Settings → Secrets and variables → Actions → `GROUP_CHAT_ID` (для CI/CD)

#### Когда обновлять
- При смене группы
- Если бот был исключен из группы
- Если получаете ошибку 403: "bot was kicked from the supergroup chat"

#### Как проверить актуальность
1. Убедитесь, что бот является администратором группы
2. Используйте команду `/test_get_member` в боте (если доступна)
3. Проверьте логи на наличие ошибок 403 Forbidden

#### После обновления
1. Обновить `GROUP_CHAT_ID` в `env_vars.txt` на сервере
2. Перезапустить бота: `sudo systemctl restart tradetherapybot.service`
3. Проверить логи: `sudo journalctl -u tradetherapybot.service -f`

### BOT_TOKEN

Токен бота, полученный от @BotFather в Telegram.

**Важно:**
- Токен должен быть одинаковым на сервере и локально (если используете скрипты)
- Токен должен соответствовать боту, который является администратором группы

### ADMIN_ID

Telegram ID администратора (ваш ID).

**Как получить:**
- Написать боту @userinfobot
- Или использовать команду `/start` в боте и посмотреть логи

## Типичные проблемы

### Ошибка 403: "bot was kicked from the supergroup chat"
**Причина:** `GROUP_CHAT_ID` указывает на старую группу, из которой бот был исключен.

**Решение:**
1. Получить актуальный ID группы
2. Обновить `GROUP_CHAT_ID` в `env_vars.txt` на сервере
3. Перезапустить бота

### Ошибка 401: Unauthorized при get_chat_member()
**Причина:** Бот не является администратором группы или `GROUP_CHAT_ID` неверный.

**Решение:**
1. Проверить, что бот является администратором группы
2. Проверить правильность `GROUP_CHAT_ID`
3. Убедиться, что токен соответствует боту-администратору

### Не получаются данные пользователей
**Причина:** Пользователи не в группе или не писали боту.

**Решение:**
- `get_chat_member()` работает только для пользователей в группе
- `get_chat()` работает только если пользователь писал боту
- Если пользователь не доступен через API, данные останутся "Unknown" (это нормально)

## Проверка конфигурации

### Локально
```bash
cd TradeTherapyBot
python -c "from config import load_config; print(load_config())"
```

### На сервере
```bash
cd /opt/tradetherapybot
cat env_vars.txt
sudo systemctl status tradetherapybot.service
```

## Обновление конфигурации на сервере

### Через SSH
```bash
ssh root@81.200.146.32
cd /opt/tradetherapybot
nano env_vars.txt
# Обновить GROUP_CHAT_ID
sudo systemctl restart tradetherapybot.service
```

### Через GitHub Secrets (для CI/CD)
1. Перейти в репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. Найти `GROUP_CHAT_ID` и обновить значение
4. Следующий деплой применит новое значение

