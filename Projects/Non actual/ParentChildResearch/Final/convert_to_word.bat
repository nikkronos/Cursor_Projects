@echo off
chcp 65001 >nul
cd /d "%~dp0"
python convert_md_to_word.py
pause
