# -*- coding: utf-8 -*-
"""Прямой запуск исправлений"""
import sys
import os

# Устанавливаем рабочую директорию
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Импортируем и запускаем
from fix_v8_to_v9 import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")




