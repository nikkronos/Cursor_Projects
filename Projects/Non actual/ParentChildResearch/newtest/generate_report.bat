@echo off
chcp 65001 >nul
cd /d "%~dp0"
python generate_word_report.py
pause





























