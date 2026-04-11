@echo off
chcp 65001 >nul
cd /d "%~dp0"
python convert_xlsx_to_csv.py
pause





























