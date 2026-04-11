# Быстрый старт: игра через интернет БЕЗ проброса порта

## Самый простой способ — Localtunnel

### Шаг 1: Установите Node.js (если ещё не установлен)
- Скачайте с https://nodejs.org/
- Установите (можно оставить все настройки по умолчанию)

### Шаг 2: Установите localtunnel
Откройте PowerShell и выполните:
```powershell
npm install -g localtunnel
```

### Шаг 3: Запустите туннель
В первом окне PowerShell:
```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\Chess"
npx localtunnel --port 8000
```

или если установили глобально:

```powershell
lt --port 8000
```

Вы увидите что-то вроде:
```
your url is: https://random-name-123.loca.lt
```

**Скопируйте этот URL!** Это адрес, по которому друзья будут подключаться.

### Шаг 4: Запустите сервер
Во втором окне PowerShell:
```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\Chess"
python server.py
```

### Шаг 5: Играйте!
- Вы: откройте `http://localhost:8000/` в браузере
- Друзья: откройте URL из шага 3 (например, `https://random-name-123.loca.lt`)

⚠️ **Важно:** 
- Оба окна (туннель и сервер) должны быть открыты всё время игры
- URL туннеля меняется при каждом запуске
- Туннель работает только пока запущен процесс `lt`

---

## Альтернатива: Ngrok (если localtunnel не работает)

### Шаг 1: Скачайте и установите ngrok
- https://ngrok.com/download
- Распакуйте в удобную папку

### Шаг 2: Зарегистрируйтесь и получите токен
- https://dashboard.ngrok.com/
- Скопируйте токен

### Шаг 3: Настройте токен
В PowerShell:
```powershell
cd путь\к\папке\ngrok
.\ngrok config add-authtoken ВАШ_ТОКЕН
```

### Шаг 4: Запустите ngrok
В первом окне:
```powershell
.\ngrok http 8000
```

### Шаг 5: Запустите сервер
Во втором окне:
```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\Chess"
python server.py
```

### Шаг 6: Узнайте публичный URL
- Откройте http://127.0.0.1:4040 в браузере
- Скопируйте URL из строки "Forwarding" (например, `https://xxxx-xx-xx-xx-xx.ngrok-free.app`)

### Шаг 7: Играйте!
- Вы: `http://localhost:8000/`
- Друзья: URL из шага 6

---

## Что выбрать?

- **Localtunnel** — проще, не требует регистрации, но URL меняется каждый раз
- **Ngrok** — стабильнее, можно зафиксировать URL (в платной версии), требует регистрацию

Для разовой игры с друзьями рекомендую **Localtunnel** — быстрее настроить.
