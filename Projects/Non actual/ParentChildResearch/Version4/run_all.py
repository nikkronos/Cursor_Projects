# -*- coding: utf-8 -*-
"""Главный скрипт для выполнения всех задач"""
import subprocess
import sys
from pathlib import Path

def run_script(script_name):
    """Запускает Python скрипт"""
    script_path = Path(__file__).parent / script_name
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

if __name__ == '__main__':
    print("Запуск извлечения текста...")
    if run_script('quick_extract.py'):
        print("\n✓ Извлечение завершено успешно!")
    else:
        print("\n✗ Ошибка при извлечении")





