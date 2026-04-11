@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo ОТПРАВКА ДАННЫХ В GOOGLE FORM
echo ========================================
echo.
python scripts\submit_to_google_form.py
pause



