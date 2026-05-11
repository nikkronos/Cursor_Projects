# Документация о сервере Fornex

## Общая информация

- **Провайдер:** Fornex
- **IP:** `185.21.8.91`
- **ОС:** Ubuntu 24.04
- **Локация:** Германия (eu1)
- **Статус:** Основной боевой сервер с 2026-04-10

## Проекты на сервере

| Проект | Путь | Сервис |
|--------|------|--------|
| VPN-бот | `/opt/vpnservice/` | `vpn-bot.service` |
| Веб-панель VPN | `/opt/vpnservice/web/` | `vpn-web.service` (порт 5001) |
| AmneziaWG | Docker-контейнер `amnezia-awg2` | порт `39580/UDP` |
| MTProxy Fake TLS | Docker-контейнер `mtproxy-faketls` | порт `8444→443/TCP` |
| Kopiya-iksuyemsya (xxx) | `/opt/kopiya-iksuyemsya/` | запускается при старте |
| PastuhiBot | `/home/hamster*/` | несколько процессов (`hamster26`, `hamster93_*`) |
| kb-market | `/opt/kb-market/` | запускается при старте |

## SSH-доступ

**Вход по паролю отключён** — только по ключу (настроено 2026-05-11).

```powershell
# Короткий способ (рекомендуется)
ssh fornex

# Полный способ
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_fornex" root@185.21.8.91
```

Алиас `fornex` прописан в `C:\Users\krono\.ssh\config`:
```
Host fornex
    HostName 185.21.8.91
    User root
    IdentityFile ~/.ssh/id_ed25519_fornex
```

**Ключ:** `C:\Users\krono\.ssh\id_ed25519_fornex`

### Важная ловушка — sshd_config

На Ubuntu 24.04 с cloud-init есть два файла конфига SSH:
- `/etc/ssh/sshd_config` — основной
- `/etc/ssh/sshd_config.d/50-cloud-init.conf` — **перекрывает основной**

При изменении SSH-настроек (например PasswordAuthentication) нужно менять **оба файла**, иначе `50-cloud-init.conf` отменит изменения.

## Безопасность (настроено 2026-05-11)

### fail2ban
Установлен и активен. Автоматически банит IP после нескольких неудачных попыток входа по SSH.
```bash
systemctl status fail2ban   # проверить статус
fail2ban-client status sshd # список забаненных IP
```

### Rate-limit на VPN-порт
Iptables-правила ограничивают UDP-флуд на порт 39580 (AmneziaWG):
- Лимит: 1000 пакетов/сек, burst 2000
- Всё сверх лимита — DROP
- Правила сохранены через `iptables-persistent` (переживают ребут)

```bash
iptables -L INPUT -n | grep 39580   # проверить правила
```

### Хранение секретов
- **На сервере:** `/opt/vpnservice/env_vars.txt`
- **Никогда не коммитить** в Git

## Мониторинг

### Веб-панель
- Главная: `http://185.21.8.91:5001/`
- Recovery: `http://185.21.8.91:5001/recovery`

### История CPU/сети на сервере
Установлен `sysstat` (2026-05-11):
```bash
sar -u 1 10      # CPU: 10 замеров по 1 сек
sar -n DEV 1 10  # сеть: 10 замеров по 1 сек
sar -u -f /var/log/sysstat/saXX  # история за день XX
```

## Полезные команды

```bash
# Статус сервисов
systemctl is-active vpn-bot vpn-web

# Docker-контейнеры
docker ps

# Логи VPN-бота
journalctl -u vpn-bot.service -f

# Логи веб-панели
journalctl -u vpn-web.service -f

# Перезапуск бота
systemctl restart vpn-bot.service

# Список клиентов AmneziaWG
docker exec amnezia-awg2 awg show awg0

# Логи контейнера AmneziaWG
docker logs amnezia-awg2
```

## История изменений

| Дата | Событие |
|------|---------|
| 2026-04-10 | Перенос VPN-бота, xxx, PastuhiBot с Timeweb на Fornex |
| 2026-04-11 | Перенос vpn-web на Fornex, Timeweb vpn-web отключён |
| 2026-05-08 | Редизайн панели мониторинга |
| 2026-05-11 | Установка fail2ban, отключение SSH-пароля, rate-limit UDP 39580, sysstat |
