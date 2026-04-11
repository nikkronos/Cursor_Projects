@echo off
chcp 65001 >nul
echo ========================================
echo HeadHunter API Server
echo ========================================
echo.
cd /d %~dp0
echo Текущая директория: %CD%
echo.
echo Запуск Flask API сервера...
echo Сервер будет доступен на http://127.0.0.1:5000
echo.
echo Для остановки нажмите Ctrl+C
echo.
python scripts\hh_api_server.py
pause





















