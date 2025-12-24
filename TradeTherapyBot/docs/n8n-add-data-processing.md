# Добавление обработки данных в N8N Workflow

## Текущий workflow

Сейчас workflow состоит из двух нод:
1. **Telegram Webhook** - принимает данные
2. **Respond to Telegram** - отвечает "OK"

## Шаг 1: Добавить ноду Code для обработки

### 1.1. Добавить ноду

**Вариант А: Через "+" на стрелке (самый простой)**

1. В N8N откройте workflow "Telegram Event Webhook Receiver"
2. Найдите **стрелку** между нодами "Telegram Webhook" и "Respond to Telegram"
3. На **стрелке** должен быть маленький **"+"** (плюсик)
4. **Кликните на этот "+"** (или кликните прямо на стрелку)
5. Откроется панель поиска нод
6. В поиске введите: **"code"** или **"function"**
7. Выберите ноду **"Code"** или **"Function"**
8. Нода автоматически добавится между существующими нодами

**Вариант Б: Через правую панель**

1. Посмотрите на **правую панель** (вертикальная панель с иконками справа)
2. Нажмите на **"+"** (плюсик вверху правой панели)
3. В поиске введите: **"code"**
4. Выберите ноду **"Code"**
5. **Перетащите** ноду на canvas между "Telegram Webhook" и "Respond to Telegram"
6. Нода должна автоматически подключиться

**Важно:** После добавления ноды должны быть видны **три ноды**, соединённые стрелками!

### 1.2. Настроить код

Кликните на ноду Code и вставьте следующий код:

```javascript
// Получаем данные из webhook
const eventData = $input.all()[0].json;

// Логируем для отладки
console.log('Received event:', JSON.stringify(eventData, null, 2));

// Обрабатываем разные типы событий
let processedData = {
  ...eventData,
  processed: true,
  processed_at: new Date().toISOString()
};

// Обработка по типу события
if (eventData.event_type === 'user_started') {
  processedData.message = 'Пользователь ' + eventData.data.user_id + ' начал работу с ботом';
  processedData.priority = 'info';
} else if (eventData.event_type === 'test_event') {
  processedData.message = 'Тестовое событие от пользователя ' + eventData.data.user_id;
  processedData.priority = 'info';
} else if (eventData.event_type === 'message_received') {
  processedData.message = 'Получено сообщение: ' + eventData.data.message_text;
  processedData.priority = 'info';
} else {
  processedData.message = 'Событие типа: ' + eventData.event_type;
  processedData.priority = 'info';
}

// Возвращаем обработанные данные
return { json: processedData };
```

**Важно:** В N8N иногда возникают проблемы с template literals (обратные кавычки). Используйте конкатенацию строк через `+` для надёжности.

### 1.3. Сохранить workflow

Нажмите **"Save"** (Ctrl+S)

## Шаг 2: Протестировать обработку

1. Отправьте команду `/test` боту TestN8N
2. Проверьте в N8N:
   - Перейдите на вкладку **"Executions"**
   - Кликните на последнее выполнение
   - Проверьте данные в ноде Code
   - Должны быть видны обработанные данные с полем `message`

## Шаг 3: Добавить логирование (опционально)

Можно добавить ноду для сохранения данных:

1. Добавьте ноду **"Set"** после Code
2. Настройте для сохранения важных полей
3. Или добавьте ноду **"Google Sheets"** для сохранения в таблицу

## Примеры обработки

### Обработка события user_started:

```javascript
if (eventData.event_type === 'user_started') {
  return {
    json: {
      event_type: 'user_started',
      user_id: eventData.data.user_id,
      username: eventData.data.username,
      message: `Новый пользователь: ${eventData.data.username || eventData.data.user_id}`,
      timestamp: eventData.timestamp
    }
  };
}
```

### Обработка события test_event:

```javascript
if (eventData.event_type === 'test_event') {
  return {
    json: {
      event_type: 'test_event',
      user_id: eventData.data.user_id,
      message: 'Тестовое событие успешно обработано',
      original_data: eventData.data
    }
  };
}
```

## Проверка работы

После добавления обработки:

1. Отправьте `/test` боту
2. Проверьте в N8N:
   - Данные должны пройти через ноду Code
   - В ноде Code должны быть видны обработанные данные
   - Поле `message` должно содержать обработанное сообщение

---

**Последнее обновление:** 2025-12-24

