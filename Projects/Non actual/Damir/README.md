# Виджет «Таблица инструментов» — Т-Инвестиции

Веб-виджет для отображения данных по фьючерсам и спот-инструментам Т-Инвестиции с поддержкой режимов «Свечи» и «Стакан», автообновлением и настройками выбора инструментов.

**Статус:** ⏸️ Прод на Timeweb **выключен** с 2026-04-04 (`futures_auction.service`: `stop` + `disable`; порт `5000` свободен). Код и файлы на сервере не удалялись.  
**URL (был):** http://81.200.146.32:5000 — сейчас снаружи ожидаемо `ERR_CONNECTION_REFUSED`, пока сервис снова не включат.  
**Репозиторий:** https://github.com/nikkronos/Futures_auction  
**Передача проекта:** см. `Projects/Non actual/Damir/TRANSFER_OTHER_PERSON.md` (и `.pdf`).

---

## 📋 Содержание

- [Описание](#описание)
- [Архитектура](#архитектура)
- [Функциональность](#функциональность)
- [Технические детали](#технические-детали)
- [Исправления (2026-02-12)](#исправления-2026-02-12)
- [Деплой](#деплой)
- [Разработка](#разработка)

---

## Описание

Виджет отображает таблицу выбранных инструментов (фьючерсы, спот) с данными:
- **Режим «Свечи»**: Актив, Цена закрытия, Цена аукциона, Отклонение %, Лоты
- **Режим «Стакан»**: Bid, Ask, Цена аукциона, Отклонение %, Лоты

**Особенности:**
- Автообновление каждые 30 минут (во время аукциона — каждые 5 секунд)
- Настройки: выбор инструментов, поиск, фильтры по категориям
- Сохранение выбора в localStorage
- Определение времени аукциона по московскому времени (МСК)

---

## Архитектура

### Структура проекта

```
Damir/
├── server.py              # Flask-бэкенд (REST API)
├── static/
│   └── index.html        # Фронтенд (HTML + CSS + JS)
├── README.md             # Эта документация
├── ROADMAP_DAMIR.md      # Планы развития
└── DONE_LIST_DAMIR.md    # История изменений
```

### Технологии

**Бэкенд:**
- Python 3.8+
- Flask (веб-сервер)
- requests (HTTP-клиент для T-Invest API)
- threading (потокобезопасный кэш)

**Фронтенд:**
- Vanilla JavaScript (без фреймворков)
- HTML5 + CSS3
- localStorage (сохранение настроек)

**API:**
- T-Invest REST API (https://invest-public-api.tbank.ru/rest/)
- Endpoints: `/instruments/futures`, `/market/candles`, `/market/orderbook`

---

## Функциональность

### 1. Таблица инструментов

**Режим «Свечи»:**
- Актив (название инструмента)
- Цена закрытия (вчерашняя дневная свеча)
- Цена аукциона (текущая цена открытия/закрытия)
- Отклонение % (от вчерашней цены закрытия до цены аукциона)
- Лоты (объём)

**Режим «Стакан»:**
- Bid (лучшая цена покупки)
- Ask (лучшая цена продажи)
- Цена аукциона
- Отклонение % (от вчерашней цены закрытия до цены аукциона)
- Лоты (суммарный объём по уровням)

### 2. Настройки

- **Выбор инструментов**: список с чекбоксами (до 20 инструментов одновременно)
- **Поиск**: фильтрация по названию/тикеру
- **Категории**: Металлы, Крипта, Индексы, Валюты, Товары, Акции
- **Действия**: Выбрать все / Снять все / Выбрать найденные

### 3. Автообновление

- **Обычное время**: каждые 30 минут
- **Время аукциона**: каждые 5 секунд
  - Открытие: Пн-Пт 8:45-9:05 МСК, Сб-Вс 9:45-10:05 МСК
  - Закрытие: 18:35-18:55 МСК (каждый день)
- Кнопка «Авто: ВКЛ/ВЫКЛ» для переключения
- Отображение статуса: «обновление каждые X мин/сек»

### 4. Сортировка

- По всем колонкам (клик по заголовку)
- Индикаторы направления сортировки (↑↓)

---

## Технические детали

### Обработка событий

**Проблема (исправлена 2026-02-12):**
- Кнопки «Настройки», «Режим: Свечи», «Авто: ВКЛ» имели **двойные обработчики**:
  - Inline `onclick` в HTML
  - `addEventListener` в JavaScript
- При клике срабатывали оба обработчика → панель открывалась и сразу закрывалась, режим переключался дважды

**Решение:**
- Удалены `addEventListener` для этих трёх кнопок
- Оставлены только inline `onclick` с вызовом функций через `try/catch`
- Все функции (`toggleSettings`, `toggleMode`, `toggleAutoRefresh`) обёрнуты в `try/catch` для предотвращения блокировки интерфейса при ошибках

**Код обработчиков:**

```html
<!-- Inline onclick с защитой от ошибок -->
<button onclick="try{if(typeof toggleSettings==='function')toggleSettings();}catch(e){console.error('Settings',e);}">
  Настройки
</button>
<button onclick="try{if(typeof toggleMode==='function')toggleMode();}catch(e){console.error('Mode',e);}">
  Режим: Свечи
</button>
<button onclick="try{if(typeof toggleAutoRefresh==='function')toggleAutoRefresh();}catch(e){console.error('Auto',e);}">
  Авто: ВКЛ
</button>
```

**Функции с защитой:**

```javascript
function toggleSettings() {
  try {
    const panel = document.getElementById('settingsPanel');
    if (!panel) return;
    // Сначала переключаем видимость (синхронно)
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    if (panel.style.display === 'none') return;
    // Потом подгружаем список (асинхронно)
    // ...
  } catch (e) { console.error('toggleSettings', e); }
}
```

### Кэширование

**Бэкенд (`server.py`):**
- Список фьючерсов: TTL 5 минут
- Свечи: TTL 10 секунд
- Стакан: TTL 5 секунд
- Потокобезопасный in-memory кэш с `threading.Lock`

**Логирование:**
- Показывает, сколько запросов из кэша, сколько свежих
- Пример: `[INFO] Cache hit: futures_list` или `[INFO] Cache miss: candles_SI-3.26`

### Определение времени аукциона

**Московское время (МСК = UTC+3):**
- Считается из UTC, а не из локального времени браузера
- Функция `getRefreshInterval()` пересчитывает интервал при каждом обновлении
- Watcher каждые 30 секунд проверяет, не наступило ли время аукциона

**Код:**

```javascript
function getRefreshInterval() {
  const now = new Date();
  const utcHour = now.getUTCHours();
  const utcMinute = now.getUTCMinutes();
  const mskTotalMin = (utcHour + 3) * 60 + utcMinute;
  const mskMinOfDay = mskTotalMin % (24 * 60);
  const mskHour = Math.floor(mskMinOfDay / 60);
  const mskMinute = mskMinOfDay % 60;
  const timeMinutes = mskHour * 60 + mskMinute;
  
  // Проверка времени аукциона
  // ...
}
```

### Форматирование цен

- **≥1000**: 2 знака после запятой
- **≥1**: 4 знака после запятой
- **<1**: 6 знаков после запятой
- Автоматическое удаление лишних нулей (17070.0000 → 17070)

### Отклонение в %

**Унифицировано для обоих режимов:**
- Считается от **вчерашней цены закрытия** (из дневных свечей) до **цены аукциона**
- Формула: `((auctionPrice - yesterdayClose) / yesterdayClose) * 100`

---

## Исправления (2026-02-12)

### Проблема: Кнопки перестают работать после клика

**Симптомы:**
1. После нажатия «Настройки» панель не открывается, остальные кнопки перестают работать
2. После нажатия «Режим: Свечи» экран не переключается, остальные кнопки перестают работать
3. После нажатия «Авто: ВКЛ» кнопка загорается, но ничего не происходит, остальные кнопки перестают работать
4. Кнопка «Обновить» работает и сбрасывает состояние

**Причина:**
- Двойные обработчики событий (inline `onclick` + `addEventListener`)
- При клике срабатывали оба → панель открывалась и сразу закрывалась
- Ошибки внутри функций не обрабатывались → ломался весь интерфейс

**Решение:**

1. **Удалены дублирующие `addEventListener`:**
   ```javascript
   // УДАЛЕНО:
   // document.getElementById('btnSettings').addEventListener('click', toggleSettings);
   // document.getElementById('btnMode').addEventListener('click', toggleMode);
   // document.getElementById('btnAutoRefresh').addEventListener('click', toggleAutoRefresh);
   ```

2. **Упрощены inline `onclick`:**
   - Вызов функций через `try/catch`
   - Проверка существования функции перед вызовом

3. **Добавлены `try/catch` в функции:**
   - `toggleSettings()` — панель открывается синхронно, список подгружается асинхронно
   - `toggleMode()` — переключение режима с защитой от ошибок
   - `toggleAutoRefresh()` — переключение автообновления с защитой от ошибок

4. **Проверки элементов DOM:**
   - Все `getElementById` проверяются на `null` перед использованием

**Результат:**
- ✅ Панель настроек открывается один раз
- ✅ Режим переключается один раз
- ✅ Автообновление переключается один раз
- ✅ Ошибки логируются в консоль, но не ломают интерфейс
- ✅ Остальные кнопки продолжают работать

**Коммит:** `58d1de9` — "fix: Настройки/Режим/Авто — один обработчик, try/catch, панель открывается сразу"

---

## Деплой

### Сервер

- **Хостинг:** Timeweb
- **IP:** 81.200.146.32
- **Порт:** 5000
- **Путь:** `/opt/futures_auction`
- **Сервис:** `futures_auction.service` (systemd)

### Процесс деплоя

1. **Локально (Windows):**
   ```bash
   cd Damir
   git add static/index.html
   git commit -m "описание изменений"
   git push
   ```

2. **На сервере (Linux):**
   ```bash
   cd ~/Futures_auction
   git pull
   cp -r . /opt/futures_auction/
   # Или перезапуск сервиса, если нужно:
   # systemctl restart futures_auction
   ```

### Переменные окружения

**Файл:** `env_vars.txt` (в корне проекта)

```
TINKOFF_INVEST_TOKEN=your_token_here
SANDBOX=0  # 0 = боевой контур, 1 = sandbox
```

**На сервере:** файл должен быть в `/opt/futures_auction/env_vars.txt`

### systemd сервис

**Файл:** `/etc/systemd/system/futures_auction.service`

```ini
[Unit]
Description=Futures Auction Widget
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/futures_auction
Environment="PATH=/opt/futures_auction/.venv/bin:/usr/bin"
ExecStart=/opt/futures_auction/.venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Команды:**
```bash
sudo systemctl enable futures_auction
sudo systemctl start futures_auction
sudo systemctl status futures_auction
```

---

## Разработка

### Локальный запуск

1. **Установка зависимостей:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # или
   source .venv/bin/activate  # Linux/Mac
   pip install flask requests
   ```

2. **Настройка токена:**
   - Создать файл `env_vars.txt` в корне проекта
   - Добавить: `TINKOFF_INVEST_TOKEN=your_token`

3. **Запуск сервера:**
   ```bash
   python server.py
   ```
   Сервер запустится на http://127.0.0.1:5000

### Структура API

**Бэкенд endpoints:**

- `GET /` — главная страница (отдаёт `static/index.html`)
- `GET /api/futures` — список всех фьючерсов
- `GET /api/table?ids=...` — данные по выбранным инструментам (режим «Свечи»)
- `GET /api/orderbook?ids=...` — данные стакана по выбранным инструментам (режим «Стакан»)

**Пример запроса:**
```bash
curl "http://127.0.0.1:5000/api/table?ids=BBG004730N88,BBG004730RP0"
```

### Отладка

**Консоль браузера (F12):**
- Ошибки JavaScript логируются с префиксами: `Settings`, `Mode`, `Auto`
- Пример: `console.error('Settings', e)`

**Логи сервера:**
- Показывают кэш-хиты/миссы
- Показывают ошибки API
- Формат: `[INFO] Cache hit: futures_list`

---

## Ссылки

- [T-Invest API — документация](https://developer.tbank.ru/invest/api)
- [T-Invest API — начало работы](https://developer.tbank.ru/invest/intro/intro/)
- [Репозиторий на GitHub](https://github.com/nikkronos/Futures_auction)

---

**Обновлено:** 2026-02-12  
**Версия:** 3.0
