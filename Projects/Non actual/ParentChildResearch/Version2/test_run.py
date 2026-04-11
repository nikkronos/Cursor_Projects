"""Тестовый запуск генерации графиков"""
import sys
import os

# Добавляем путь к скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Запускаем скрипт
try:
    exec(open(os.path.join(script_dir, 'generate_charts.py'), encoding='utf-8').read())
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()














