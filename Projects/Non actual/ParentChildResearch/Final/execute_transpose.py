"""Вспомогательный скрипт для запуска транспонирования"""
import subprocess
import sys
import os

# Получаем полный путь к скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(script_dir, "run_transpose_simple.py")

# Запускаем скрипт
result = subprocess.run([sys.executable, script_path], 
                       cwd=script_dir,
                       capture_output=False,
                       text=True)

sys.exit(result.returncode)
