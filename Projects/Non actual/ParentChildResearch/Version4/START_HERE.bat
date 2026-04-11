@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Извлечение текста из документов v6
echo ========================================
python execute_extraction.py
pause





