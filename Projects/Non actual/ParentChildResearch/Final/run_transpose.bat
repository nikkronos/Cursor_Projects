@echo off
chcp 65001 >nul
cd /d "%~dp0"
python transpose_csv.py
pause
