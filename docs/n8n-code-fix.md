# Исправление кода для N8N Code ноды

## Проблема

В N8N Code ноде могут быть проблемы с template literals (обратные кавычки `` ` ``). Лучше использовать конкатенацию строк через `+`.

## Правильный код (без template literals)

Скопируйте этот код в ноду Code:

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

## Что изменилось

- Заменены template literals (`` `текст ${переменная}` ``) на конкатенацию (`'текст ' + переменная`)
- Это более надёжно работает в N8N

## Как использовать

1. Удалите весь код из ноды Code
2. Скопируйте код выше
3. Вставьте в ноду Code
4. Нажмите "Save"
5. Протестируйте, отправив `/test` боту

---

**Последнее обновление:** 2025-12-24























