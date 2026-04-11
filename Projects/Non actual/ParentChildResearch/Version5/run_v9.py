# -*- coding: utf-8 -*-
"""Простая обертка для запуска fix_v8_to_v9.py"""
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    script_path = Path(__file__).parent / "fix_v8_to_v9.py"
    subprocess.run([sys.executable, str(script_path)])




