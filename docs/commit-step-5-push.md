# Шаг 5: Отправка коммита в GitHub

## Ситуация

Коммит успешно создан. Теперь нужно отправить изменения в GitHub.

## Команда для push

Выполните в PowerShell **из папки TradeTherapyBot**:

```powershell
# Убедитесь, что вы в папке TradeTherapyBot
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"

# Отправить в GitHub
git push origin main
```

## Что произойдёт после push

1. **GitHub Actions запустит тесты** (если настроены)
2. **При успешных тестах** → автоматический деплой на сервер (для TradeTherapyBot)
3. **Изменения появятся в GitHub** репозитории `nikkronos/TradeTherapyBot`

## Проверка после push

1. Проверьте в GitHub, что коммит появился
2. Проверьте в GitHub Actions, что тесты прошли (если настроены)
3. Убедитесь, что все файлы на месте

---

**Последнее обновление:** 2025-12-24























