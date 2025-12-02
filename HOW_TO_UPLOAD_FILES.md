# Как загрузить файлы на сервер (простая инструкция)

## Когда нужно это делать?
Когда вы изменили код на компьютере и нужно обновить бота на сервере.

---

## ШАГ 1: Открыть PowerShell на компьютере

1. Нажмите `Win + R`
2. Введите `powershell`
3. Нажмите Enter

---

## ШАГ 2: Перейти в папку проекта

Скопируйте и вставьте эту команду, нажмите Enter:

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
```

---

## ШАГ 3: Скопировать файлы на сервер

Выполните эти команды по очереди (каждую отдельно, нажимая Enter после каждой):

**Файл 1:**
```powershell
scp handlers/user.py root@81.200.146.32:/opt/tradetherapybot/handlers/user.py
```
(Введите пароль, когда попросит)

**Файл 2:**
```powershell
scp handlers/callbacks.py root@81.200.146.32:/opt/tradetherapybot/handlers/callbacks.py
```
(Введите пароль)

**Файл 3:**
```powershell
scp utils.py root@81.200.146.32:/opt/tradetherapybot/utils.py
```
(Введите пароль)

---

## ШАГ 4: Подключиться к серверу и перезапустить бота

1. Откройте **НОВОЕ** окно PowerShell (не закрывая предыдущее)
2. Выполните:
```powershell
ssh root@81.200.146.32
```
3. Введите пароль
4. Выполните:
```bash
systemctl restart tradetherapybot.service
```

---

## Готово! ✅

Бот перезапущен с новым кодом.

---

## Если scp не работает

Если команда `scp` не найдена, используйте WinSCP или FileZilla для копирования файлов.





