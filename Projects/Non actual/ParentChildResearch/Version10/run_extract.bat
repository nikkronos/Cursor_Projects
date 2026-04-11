@echo off
chcp 65001 >nul
cd /d "%~dp0"
python extract_literature_v20.py
pause
