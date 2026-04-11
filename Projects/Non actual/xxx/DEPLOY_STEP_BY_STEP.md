# Деплой «Копия иксуюемся» на сервер — пошагово

Бот должен работать на сервере 24/7. Ниже — действия по порядку.

---

## Что нужно до начала

- Доступ по SSH к серверу (логин/пароль или ключ).
- На сервере: Linux (Ubuntu/Debian или аналог), установлены `git` и `python3` (3.8+).
- Локально: заполненный `env_vars.txt` из папки `xxx` (токен бота, API_ID, API_HASH, номер телефона, ID каналов). Эти же значения понадобятся на сервере.

---

## Шаг 1. Подключиться к серверу

На своём компьютере откройте терминал и выполните (подставьте свой хост и пользователя):

```bash
ssh root@IP_ВАШЕГО_СЕРВЕРА
```

Или, если логин не root:

```bash
ssh user@IP_ВАШЕГО_СЕРВЕРА
```

Дальше все команды выполняются **на сервере**, если не сказано иное.

---

## Шаг 2. Установить зависимости (если ещё нет)

Проверка Python:

```bash
python3 --version
```

Должно быть 3.8 или выше. Если Python нет — установите (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install -y python3 python3-pip git
```

---

## Шаг 3. Клонировать репозиторий

Выберите одну папку для бота, например `/opt/kopiya-iksuyemsya`:

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/nikkronos/xxxsuemsya.git kopiya-iksuyemsya
cd kopiya-iksuyemsya
```

Если репозиторий **приватный** (как xxxsuemsya), клонировать по SSH: на сервере сгенерировать ключ (`ssh-keygen -t ed25519 -C "server"`), добавить содержимое `~/.ssh/id_ed25519.pub` в GitHub → репозиторий xxxsuemsya → **Settings** → **Deploy keys** → **Add deploy key**. Затем:

```bash
sudo git clone git@github.com:nikkronos/xxxsuemsya.git kopiya-iksuyemsya
```

Проверка:

```bash
ls -la
```

Должны быть файлы: `main.py`, `requirements.txt`, `config.py`, `userbot.py`, `copy_handler.py` и др.

---

## Шаг 4. Создать `env_vars.txt` на сервере

Секреты в репозиторий не попадают — файл нужно создать вручную на сервере.

```bash
nano /opt/kopiya-iksuyemsya/env_vars.txt
```

Вставьте те же переменные, что и локально (скопируйте из своего `env_vars.txt`), и сохраните:

- `BOT_TOKEN=...`
- `ADMIN_ID=...`
- `API_ID=...`
- `API_HASH=...`
- `PHONE_NUMBER=...` (в формате +79...)
- `SOURCE_CHANNEL_ID=...`
- `TARGET_CHANNEL_ID=...`

Сохранить: `Ctrl+O`, Enter. Выход: `Ctrl+X`.

Проверка:

```bash
cat /opt/kopiya-iksuyemsya/env_vars.txt
```

Убедитесь, что нет лишних пробелов и кавычек вокруг значений.

---

## Шаг 5. Установить зависимости Python

```bash
cd /opt/kopiya-iksuyemsya
pip3 install -r requirements.txt --break-system-packages
```

Или, если используете виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(Если используете venv, потом в systemd в `ExecStart` нужно будет указать полный путь к `venv/bin/python3` и к `main.py`.)

---

## Шаг 6. Первый запуск — авторизация Pyrogram (один раз)

При первом запуске Pyrogram попросит код из Telegram. Запустите бота вручную:

```bash
cd /opt/kopiya-iksuyemsya
python3 main.py
```

В Telegram придёт код. Введите его в терминале. После успешного входа появится сессия (файл `userbot.session` в папке бота). Остановите бота: `Ctrl+C`.

Дальше этот шаг повторять не нужно — systemd будет использовать уже созданную сессию.

---

## Шаг 7. Настроить systemd (автозапуск и перезапуск при падении)

Скопировать unit-файл:

```bash
sudo cp /opt/kopiya-iksuyemsya/kopiya-iksuyemsya.service /etc/systemd/system/
```

Проверить пути в unit-файле (если клонировали в другую папку — поправьте):

```bash
sudo nano /etc/systemd/system/kopiya-iksuyemsya.service
```

Должно быть:

- `WorkingDirectory=/opt/kopiya-iksuyemsya`
- `ExecStart=/usr/bin/python3 /opt/kopiya-iksuyemsya/main.py`

Если бот в другой папке (например `/opt/xxxsuemsya`) — замените `/opt/kopiya-iksuyemsya` на неё в обоих местах. Сохраните и выйдите.

Перезагрузить конфигурацию systemd и включить сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kopiya-iksuyemsya.service
sudo systemctl start kopiya-iksuyemsya.service
```

Проверить статус:

```bash
sudo systemctl status kopiya-iksuyemsya.service
```

Должно быть `active (running)`. Логи в реальном времени:

```bash
sudo journalctl -u kopiya-iksuyemsya.service -f
```

Выход из логов: `Ctrl+C`.

---

## Шаг 8. (По желанию) Автодеплой при push в GitHub

Чтобы при каждом `git push origin main` в репозиторий **xxxsuemsya** на сервере автоматически подтягивался код и перезапускался бот:

1. В GitHub откройте репозиторий **nikkronos/xxxsuemsya**.
2. **Settings** → **Secrets and variables** → **Actions**.
3. Создайте секреты (те же, что для TradeTherapyBot, если сервер один):
   - `SSH_HOST` — IP или домен сервера
   - `SSH_USER` — пользователь (например `root`)
   - `SSH_PRIVATE_KEY` — приватный SSH-ключ (содержимое файла без публичной части)
   - `SSH_PORT` — порт SSH (обычно `22`)
   - `DEPLOY_PATH` — каталог с ботом на сервере: `/opt/kopiya-iksuyemsya`

После сохранения секретов при каждом пуше в `main` workflow «Deploy Kopiya Iksuyemsya» будет выполнять на сервере: `cd $DEPLOY_PATH`, `git pull`, `pip3 install -r requirements.txt`, `systemctl restart kopiya-iksuyemsya.service`.

---

## Полезные команды на сервере

| Действие        | Команда |
|-----------------|--------|
| Статус бота     | `sudo systemctl status kopiya-iksuyemsya.service` |
| Перезапуск      | `sudo systemctl restart kopiya-iksuyemsya.service` |
| Остановка       | `sudo systemctl stop kopiya-iksuyemsya.service` |
| Запуск          | `sudo systemctl start kopiya-iksuyemsya.service` |
| Логи в реальном времени | `sudo journalctl -u kopiya-iksuyemsya.service -f` |
| Последние 100 строк логов | `sudo journalctl -u kopiya-iksuyemsya.service -n 100` |

---

## Если что-то пошло не так

- **Бот не стартует** — смотрите логи: `sudo journalctl -u kopiya-iksuyemsya.service -n 100`. Часто причина: ошибка в `env_vars.txt` (опечатка, лишний пробел) или не пройдена авторизация Pyrogram (шаг 6).
- **«Peer id invalid» / ошибки канала** — проверьте, что в канале есть юзербот (номер из `PHONE_NUMBER`) и бот (BOT_TOKEN), и что ID каналов указаны верно (числа, можно с минусом).
- **Нет прав на папку** — при необходимости: `sudo chown -R root:root /opt/kopiya-iksuyemsya`.

После выполнения шагов 1–7 бот уже работает на сервере; шаг 8 нужен только для автоматического обновления при пуше в **xxxsuemsya**.
