@echo off
chcp 65001 >nul
cd /d "%~dp0"
python analyze_v20_structure.py
pause
