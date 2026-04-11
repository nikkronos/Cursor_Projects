@echo off
chcp 65001 >nul
cd /d "%~dp0"
python fix_v8_to_v9.py
pause




