# Пошаговая инструкция: Добавление ноды Code в N8N

## Проблема

Нода Code не видна в workflow. Нужно добавить её между "Telegram Webhook" и "Respond to Telegram".

## Пошаговая инструкция

### Шаг 1: Убедиться, что вы в Editor

1. В N8N перейдите на вкладку **"Editor"** (не "Executions")
2. Должны быть видны две ноды: "Telegram Webhook" и "Respond to Telegram"

### Шаг 2: Добавить ноду Code

**Вариант А: Через "+" между нодами**

1. Найдите **стрелку** между нодами "Telegram Webhook" и "Respond to Telegram"
2. На **стрелке** должен быть маленький **"+"** (плюсик)
3. **Кликните на этот "+"**
4. Откроется панель поиска нод
5. В поиске введите: **"code"** (или **"function"**)
6. Выберите ноду **"Code"** или **"Function"**
7. Нода должна появиться между двумя существующими нодами

**Вариант Б: Через правую панель**

1. Посмотрите на **правую панель** (вертикальная панель с иконками)
2. Нажмите на **"+"** (плюсик вверху правой панели)
3. В поиске введите: **"code"**
4. Выберите ноду **"Code"**
5. **Перетащите** ноду на canvas между "Telegram Webhook" и "Respond to Telegram"
6. Нода должна автоматически подключиться

### Шаг 3: Удалить старое соединение (если нужно)

Если нода Code добавлена, но соединения неправильные:

1. **Удалите стрелку** между "Telegram Webhook" и "Respond to Telegram"
   - Кликните на стрелку
   - Нажмите Delete или правой кнопкой → Delete
2. **Соедините ноды правильно:**
   - От "Telegram Webhook" → к "Code"
   - От "Code" → к "Respond to Telegram"

### Шаг 4: Настроить код в ноде Code

1. **Кликните на ноду Code**
2. В правой панели откроются настройки
3. Убедитесь, что выбрана вкладка **"Parameters"**
4. **Удалите весь код** из окна редактора
5. **Вставьте этот код:**

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

6. **Нажмите "Save"** (Ctrl+S)

### Шаг 5: Проверить соединения

Убедитесь, что ноды соединены правильно:

```
Telegram Webhook → Code → Respond to Telegram
```

Все стрелки должны быть зелёными (если workflow выполнен успешно).

### Шаг 6: Сохранить и активировать

1. Нажмите **"Save"** в правом верхнем углу (Ctrl+S)
2. Убедитесь, что workflow **активирован** (кнопка "Deactivate" видна)

### Шаг 7: Протестировать

1. Отправьте команду `/test` боту TestN8N
2. Перейдите на вкладку **"Executions"**
3. Кликните на последнее выполнение
4. Должны быть видны **три ноды**:
   - Telegram Webhook ✅
   - **Code** ✅ ← должна быть видна!
   - Respond to Telegram ✅

## Если не получается

### Проблема: Не вижу "+" на стрелке

**Решение:**
- Попробуйте кликнуть **прямо на стрелку** между нодами
- Или используйте правую панель (иконка "+" вверху)

### Проблема: Нода добавилась, но не соединена

**Решение:**
1. Удалите старую стрелку между webhook и response
2. Перетащите выходной порт "Telegram Webhook" к входному порту "Code"
3. Перетащите выходной порт "Code" к входному порту "Respond to Telegram"

### Проблема: Код не работает

**Решение:**
- Убедитесь, что используете код **без template literals** (обратных кавычек)
- Используйте конкатенацию строк через `+`
- См. `docs/n8n-code-fix.md`

---

**Последнее обновление:** 2025-12-24

