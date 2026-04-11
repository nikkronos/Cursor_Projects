@echo off
chcp 65001 >nul
cd /d "%~dp0"
python fix_v6_to_v7_complete.py
pause





