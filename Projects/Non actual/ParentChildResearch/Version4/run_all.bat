@echo off
chcp 65001 >nul
cd /d "%~dp0"
python execute_all_tasks.py
pause





