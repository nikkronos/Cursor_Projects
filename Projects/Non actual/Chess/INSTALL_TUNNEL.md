# Установка localtunnel (решение проблемы с PowerShell)

## Проблема
PowerShell блокирует выполнение скриптов npm из-за политики безопасности Windows.

## Решение 1: Использовать npm.cmd (самый простой способ)

Вместо `npm` используйте `npm.cmd`:

```powershell
npm.cmd install -g localtunnel
```

Затем для запуска туннеля тоже используйте полный путь или `npx`:

```powershell
npx.cmd localtunnel --port 8000
```

## Решение 2: Изменить политику выполнения PowerShell (требует прав администратора)

1. Закройте текущее окно PowerShell
2. Откройте **новое** окно PowerShell **от имени администратора**:
   - Нажмите Win + X
   - Выберите "Windows PowerShell (Администратор)" или "Терминал (Администратор)"
3. Выполните команду:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. Нажмите `Y` для подтверждения
5. Закройте окно администратора
6. В обычном PowerShell выполните:

```powershell
npm install -g localtunnel
```

## Решение 3: Использовать cmd вместо PowerShell

1. Откройте обычную командную строку (cmd):
   - Нажмите Win + R
   - Введите `cmd` и нажмите Enter
2. Выполните:

```cmd
npm install -g localtunnel
```

## Проверка установки

После установки проверьте:

```powershell
npm.cmd list -g localtunnel
```

или

```cmd
npm list -g localtunnel
```

## Запуск туннеля

После установки запустите туннель:

```powershell
npx.cmd localtunnel --port 8000
```

или

```cmd
npx localtunnel --port 8000
```
