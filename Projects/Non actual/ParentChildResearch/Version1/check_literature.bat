@echo off
chcp 65001 >nul
echo ========================================
echo Проверка списка литературы
echo ========================================
cd /d "%~dp0"
python check_literature.py
pause


















