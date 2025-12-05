#!/bin/bash
# Скрипт запуска Trade Therapy Bot

# Получаем директорию, где находится скрипт
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Проверяем наличие виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запускаем бота
python3 main.py












